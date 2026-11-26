#!/usr/bin/env python3
"""Moonlight nightly flagger (spec A8). Reads the live site, writes a list of suspect cards.

It never touches the site, moonlight/*.py, moonlight/*.json or web/. Output goes to
flags/<date>.csv, flags/<date>.md, flags/<date>-no-label.csv and checked.json
in the repo root (branch `flagger` only).

  python3 tools/flagger/flagger.py plan   [--budget 0.90]   # walk live site, read labels, write requests; no money spent
  python3 tools/flagger/flagger.py submit --yes             # send the batch, poll, download (needs ANTHROPIC_API_KEY)
  python3 tools/flagger/flagger.py report                   # results -> flags/<date>.csv, -no-label.csv, .md, checked.json
  python3 tools/flagger/flagger.py combos                   # list tonight's combo sources that would switch (no model call)

Work files (labels, cards, requests, results) live in --work (default /workspace/flagger/work), outside git.
Key: ANTHROPIC_API_KEY from the environment only. It is never printed, logged or written.
Reuses docs/benchmarks/2026-11-24/: prompt (build_requests.SYSTEM), submit_batch (batch calls, prices), score (parse, norm).
"""
import argparse, concurrent.futures as cf, csv, hashlib, importlib.util, json, os, re, subprocess, sys, time
import threading, unicodedata
import xml.etree.ElementTree as ET
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
BENCH = os.path.join(REPO, "docs", "benchmarks", "2026-11-24")
LIVE = "https://moonlightclues.com"
UA = {"User-Agent": "MoonlightFlagger/0.1 (+https://github.com/Moonlight-Clues/moonlight)"}
TAB_LISTS = ("approved", "narrower", "wider_group")   # the Approved tab: main list and both folded boxes
MAX_LABEL_CHARS = 15000
OUT_ALLOWANCE = 250        # output tokens per card used in the estimate (JSON answer is ~100)
MAX_TOKENS = 700           # per request ceiling (benchmark used 1500)
HARD_CAP = 1.00
# Flags are NO, UNCLEAR, and any card whose verdict changed since its last check.
# NO_LABEL is written to its own file and is not a flag (MAIN 5, 26 Nov 2026).
FLAG_VERDICTS = ("NO", "UNCLEAR")
# Order used to sort flags/<date>-no-label.csv and the counts in the md file.
SOURCE_KIND_ORDER = (
    "WHO ATC",
    "TTD",
    "PMDA general list",
    "trial page",
    "missing link",
    "DailyMed, no indications section",
    "DailyMed, unreadable",
    "USAN name page",
    "FDA label, unreadable",
    "EMA page, unreadable",
    "combination only",
    "other",
)
PENDING_RELABEL = "combo-relabel"   # checked.json mark: no date, treated as never checked
COMBO_ONLY = "combination only"
COMBO_ONLY_NOTE = "combination only: no single-ingredient label found; source kept"
NL_COLS = ["disease_id", "disease", "medicine_id", "medicine", "source_kind", "label_url", "note"]
SALT_WORDS = {
    "hydrochloride", "hydrobromide", "sodium", "potassium", "calcium", "magnesium",
    "acetate", "maleate", "fumarate", "succinate", "tartrate", "sulfate", "sulphate",
    "phosphate", "citrate", "mesylate", "besylate", "tosylate", "pamoate",
    "anhydrous", "monohydrate", "dihydrate", "trihydrate", "hydrate",
    "free", "base", "acid",
}


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, os.path.join(BENCH, filename))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def bench():
    return _load("bench_build", "build_requests.py"), _load("bench_submit", "submit_batch.py"), _load("bench_score", "score.py")


# ---------------------------------------------------------------- live site
def get_json(path, params=None, tries=4):
    last = None
    for i in range(tries):
        try:
            r = requests.get(LIVE + path, params=params, headers=UA, timeout=180)
            if r.status_code == 200:
                return r.json()
            last = f"HTTP {r.status_code}"
        except requests.RequestException as e:
            last = type(e).__name__
        time.sleep(2 * (i + 1))
    raise RuntimeError(f"{path} {params}: {last}")


def fingerprint():
    v = get_json("/api/version")
    return v.get("fingerprint", ""), v.get("revision", "")


def walk_cards(disease_ids, workers=4):
    """Every card on the Approved tab of every page. Returns (cards, failed_disease_ids)."""
    cards, failed = [], []

    def one(d):
        return d, get_json("/api/clues", {"disease_id": d})

    with cf.ThreadPoolExecutor(workers) as ex:
        futs = [ex.submit(one, d) for d in disease_ids]
        for fu in futs:
            try:
                d, page = fu.result()
            except Exception as e:  # keep going; report the page
                failed.append(str(e)[:120]); continue
            red = set(page.get("wrong_approvals_box") or [])
            seen = set()
            for lst in TAB_LISTS:
                for m in page.get(lst) or []:
                    if m["id"] in seen:
                        continue
                    seen.add(m["id"])
                    cards.append({
                        "disease_id": page["disease"]["id"], "disease": page["disease"]["name"],
                        "medicine_id": m["id"], "medicine": m["medicine"], "forms": m.get("forms") or [],
                        "source": m.get("source") or "", "list": lst,
                        "red": bool(m.get("warning")) or m["id"] in red,
                        "also_called": ((page.get("about_disease") or {}).get("also_called") or [])[:12],
                    })
    return cards, failed


def card_key(c):
    return f"{c['disease_id']}|{c['medicine_id']}"


# ---------------------------------------------------------------- labels
_ema_lock = threading.Lock()


def _get(url, tries=6, spaced=False):
    """GET with a back-off on 429 and 5xx. spaced=True: one at a time, 1.5 s apart (EMA rate-limits)."""
    r = None
    for i in range(tries):
        if spaced:
            with _ema_lock:
                r = requests.get(url, headers=UA, timeout=120)
                time.sleep(1.5)
        else:
            r = requests.get(url, headers=UA, timeout=180)
        if r.status_code not in (429, 500, 502, 503, 504):
            return r
        wait = r.headers.get("Retry-After", "")
        time.sleep(min(60, int(wait)) if wait.isdigit() else 5 * (i + 1))
    return r


def _squash(s):
    return re.sub(r"[ \t\r\f\v]+", " ", re.sub(r"\n\s*\n+", "\n", s)).strip()


def _dailymed_setid(url):
    m = re.search(r"setid=([0-9a-fA-F-]{36})", url or "")
    return m.group(1) if m else ""


def _ingredients_from_spl(xml_bytes):
    """Unique active moieties (ACTIB) from a DailyMed SPL. Order preserved."""
    ns = "{urn:hl7-org:v3}"
    root = ET.fromstring(xml_bytes)
    seen, out = set(), []
    for ing in root.iter(ns + "ingredient"):
        if (ing.get("classCode") or "") != "ACTIB":
            continue
        moiety = ing.find(f".//{ns}activeMoiety/{ns}activeMoiety/{ns}name")
        subst = ing.find(f"{ns}ingredientSubstance/{ns}name")
        node = moiety if moiety is not None else subst
        if node is None:
            continue
        name = _squash("".join(node.itertext()))
        key = name.lower()
        if name and key not in seen:
            seen.add(key); out.append(name)
    return out


def _ingredients_from_dailymed_html(html_bytes):
    """Active Ingredient/Active Moiety table on the DailyMed web page (used when the XML copy is missing)."""
    import lxml.html
    doc = lxml.html.fromstring(html_bytes)
    seen, out = set(), []
    for table in doc.xpath("//table"):
        rows = table.xpath(".//tr")
        heads = [_squash(c.text_content()).lower() for c in (rows[0].xpath("./th|./td") if rows else [])]
        if not any("ingredient name" in h for h in heads):
            continue
        if not any("basis of strength" in h or "strength" in h for h in heads):
            continue
        for row in rows[1:]:
            cells = [_squash(c.text_content()) for c in row.xpath("./th|./td")]
            if not cells:
                continue
            # "IRBESARTAN (UNII: ...) (IRBESARTAN - UNII:...)" — take the name before the first (
            raw = cells[1] if len(cells) > 1 and "unii" not in cells[1].lower() else cells[0]
            name = re.sub(r"\s*\(.*", "", raw).strip()
            if not name or "ingredient" in name.lower() or "product information" in name.lower():
                continue
            key = name.lower()
            if key not in seen:
                seen.add(key); out.append(name)
        if out:
            return out
    # Fall back to the document title: "IRBESARTAN AND HYDROCHLOROTHIAZIDE - irbesartan and hydrochlorothiazide tablet"
    titles = doc.xpath("//*[contains(@class,'DocumentTitle') or contains(@class,'contentTableTitle')]")
    if titles:
        return ingredients_from_title(_squash(titles[0].text_content()))
    return []


def _dailymed(url):
    sid = _dailymed_setid(url)
    if not sid:
        return None, "no setid", []
    r = _get(f"https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/{sid}.xml")
    if r.status_code == 404:        # not in the v2 services copy: read the label's own web page instead
        return _dailymed_page(url)
    if r.status_code != 200:
        return None, f"dailymed HTTP {r.status_code}", []
    ings = _ingredients_from_spl(r.content)
    ns = "{urn:hl7-org:v3}"
    root = ET.fromstring(r.content)
    best = ""
    for s in root.iter(ns + "section"):
        c = s.find(ns + "code")
        if c is not None and c.get("code") == "34067-9":      # LOINC: indications and usage
            t = _squash("".join(s.itertext()))
            if len(t) > len(best):
                best = t
    return (best, "", ings) if len(best) >= 40 else (None, "no indications section", ings)


def _dailymed_page(url):
    import lxml.html
    r = _get(url)
    if r.status_code != 200:
        return None, f"dailymed HTTP {r.status_code}", []
    ings = _ingredients_from_dailymed_html(r.content)
    doc = lxml.html.fromstring(r.content)
    best = ""
    for el in doc.xpath('//*[@data-sectioncode="34067-9"]'):
        t = _squash(el.text_content())
        if len(t) > len(best):
            best = t
    return (best, "", ings) if len(best) >= 40 else (None, "no indications section", ings)


def _fda_pdf(url):
    r = _get(url)
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        return None, f"fda HTTP {r.status_code}", []
    p = subprocess.run(["pdftotext", "-layout", "-", "-"], input=r.content, capture_output=True, timeout=120)
    t = p.stdout.decode("utf-8", "ignore")
    starts = [m.start() for m in re.finditer(r"INDICATIONS\s*(?:AND|&)\s*USAGE", t, re.I)]
    # the highlights page names the heading first; the full section comes later and is the longest stretch
    best = ""
    for s in starts:
        seg = t[s:s + 40000]
        e = re.search(r"\n\s*(?:2\s+)?DOSAGE\s*(?:AND|&)\s*ADMINISTRATION", seg[30:], re.I)
        seg = seg[: e.start() + 30] if e else seg[:MAX_LABEL_CHARS]
        seg = _squash(seg)
        if len(seg) > len(best):
            best = seg
    ings = ingredients_from_title(t[:2500])
    return (best, "", ings) if len(best) >= 60 else (None, "no indications section", ings)


def _ema_active_substances(page_text):
    t = re.sub(r"<[^>]+>", " ", page_text)
    import html as _h
    t = re.sub(r"\s+", " ", _h.unescape(t))
    m = re.search(r"Active substances?\s+(.{1,300})", t, re.I)
    if not m:
        return []
    # Older EPAR summaries follow the name with a description sentence.
    # Stop at the first period, or at the usual heading that follows a short list.
    raw = m.group(1)
    raw = re.sub(r"^in [A-Za-z][A-Za-z0-9-]+,\s*", "", raw.strip())  # "in Tegsedi, inotersen, is an..."
    raw = re.sub(r"\([^)]*\)", " ", raw)   # drop strengths such as (0.1% and 0.03%) before any split
    raw = re.split(
        r",\s+is\b|\.\s+(?:This|How|It|What|Expand|International)|Expand section|International non-proprietary|Therapeutic area|\s+INN\b",
        raw, maxsplit=1, flags=re.I)[0]
    return tidy_ingredients(split_ingredient_list(raw))


def _ema(url):
    r = _get(url, spaced=True)
    if r.status_code != 200:
        return None, f"ema HTTP {r.status_code}", []
    ings = _ema_active_substances(r.text)
    t = re.sub(r"<[^>]+>", "\n", r.text)
    import html as _h
    t = _h.unescape(t)
    m = re.search(r"Therapeutic indication(.*?)(?:Authorisation details|Pharmacotherapeutic group)", t, re.S | re.I)
    txt = _squash(m.group(1)) if m else ""
    return (txt, "", ings) if len(txt) >= 40 else (None, "no indication text", ings)


def read_label(url, labels_dir):
    """-> {status: 'label'|'no_label', text, reason, ingredients}. Cached by URL."""
    os.makedirs(labels_dir, exist_ok=True)
    f = os.path.join(labels_dir, hashlib.sha1((url or "").encode()).hexdigest()[:16] + ".json")
    if os.path.exists(f):
        out = json.load(open(f))
        out.setdefault("ingredients", [])
        return out
    host = re.match(r"https?://([^/]+)", url or "")
    host = host.group(1) if host else ""
    text, why, ings = None, "source is not a readable label page", []
    try:
        if host == "dailymed.nlm.nih.gov":
            text, why, ings = _dailymed(url)
        elif host == "www.accessdata.fda.gov" and url.lower().endswith(".pdf"):
            text, why, ings = _fda_pdf(url)
        elif host == "www.ema.europa.eu":
            text, why, ings = _ema(url)
    except Exception as e:
        text, why, ings = None, f"fetch error {type(e).__name__}", []
    out = {"url": url, "status": "label" if text else "no_label",
           "text": (text or "")[:MAX_LABEL_CHARS], "reason": why, "ingredients": ings or []}
    if not text and re.search(r"fetch error|HTTP (429|5\d\d)", why or ""):
        return out                      # transient: not cached
    json.dump(out, open(f, "w"))
    return out


# ---------------------------------------------------------------- combination products (Kashish's rule Q22)
def split_ingredient_list(text):
    """Split 'ivacaftor, tezacaftor and elexacaftor' or 'ezetimibe/simvastatin' into names."""
    s = _squash(text or "")
    s = re.sub(r"[.]\s*$", "", s)
    parts = re.split(r"\s*,\s*|\s+and\s+|\s*/\s*", s, flags=re.I)
    return tidy_ingredients([p.strip() for p in parts if len(p.strip()) >= 3])


def tidy_ingredients(ings):
    """Drop prose, section numbers and leftover description phrases."""
    seen, out = set(), []
    for raw in ings or []:
        piece = re.split(r"\.\s+", raw)[0]
        piece = re.sub(r"\([^)]*\)", " ", piece)
        piece = _squash(piece).strip(" -;,")
        piece = re.sub(r"^(and|or|of)\s+", "", piece, flags=re.I)
        if not _valid_ingredient(piece):
            continue
        key = piece.lower()
        if key not in seen:
            seen.add(key); out.append(piece)
    return out


def _valid_ingredient(name):
    if not name or len(name) > 80 or re.fullmatch(r"[\d.]+", name):
        return False
    if re.match(r"in\s+[A-Za-z]", name, re.I):          # leftover "in Tegsedi"
        return False
    if re.search(r"\b(this|that|which|used|available|given|how|what|is|are|the|a|an|for|with|from|including|copy|human|hormone|section|see|www|http|fda|isolate|isolates|strain|strains|susceptible|resistant|medwatch|includes|include)\b", name, re.I):
        return False
    toks = name_tokens(name)
    if not toks or len(toks) > 6:
        return False
    if len(toks) == 1 and len(toks[0]) <= 2:            # "S" from "S. aureus"
        return False
    return True


def ingredients_from_title(title):
    """Read active ingredients out of a product title, or [] if the title is not a product name."""
    t = re.sub(r"\[[^\]]*\]", " ", title or "")
    t = _squash(t)
    # "VYTORIN (ezetimibe/simvastatin) Tablets" or "VYTORIN (ezetimibe and simvastatin)"
    for par in re.findall(r"\(([^)]{3,120})\)", t):
        if re.search(r"including|includes|isolate|strain|susceptible|resistant|www\.|http|see |highlight|section", par, re.I):
            continue
        if re.search(r"\s+and\s+|/|,", par, re.I) and not re.search(
                r"tablet|capsule|injection|for oral", par, re.I):
            parts = split_ingredient_list(par)
            if len(parts) >= 2:
                return parts
        # single generic in parens: "(simvastatin)" — not used as a combo signal
    # "IRBESARTAN and HYDROCHLOROTHIAZIDE Tablets" / "Oxycodone and Acetaminophen Tablets"
    m = re.search(
        r"\b([A-Z][A-Za-z0-9-]+(?:\s+[A-Z][A-Za-z0-9-]+){0,3})\s+and\s+"
        r"([A-Z][A-Za-z0-9-]+(?:\s+[A-Z][A-Za-z0-9-]+){0,3})\s+"
        r"(?:and\s+([A-Z][A-Za-z0-9-]+(?:\s+[A-Z][A-Za-z0-9-]+){0,3})\s+)?"
        r"(?:tablets?|capsules?|film|oral|for oral)",
        t, re.I)
    if m:
        return [p for p in m.groups() if p]
    return []


def title_looks_combo(title):
    """True when a DailyMed search title names two or more active ingredients."""
    t = re.sub(r"\[[^\]]*\]", " ", title or "")
    t = _squash(t)
    # Generic name in parentheses, or the leading generic itself.
    parens = re.findall(r"\(([^)]+)\)", t)
    body = " ".join(parens) if parens else t
    return bool(re.search(r"\s+and\s+|/", body, re.I))


def name_tokens(name):
    s = unicodedata.normalize("NFKC", name or "").lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return [t for t in s.split() if t and t not in SALT_WORDS and not t.isdigit()]


def names_match(a, b):
    """Same medicine, ignoring salt/ester words: 'Simvastatin' matches 'simvastatin calcium'."""
    ta, tb = name_tokens(a), name_tokens(b)
    if not ta or not tb:
        return False
    if ta == tb:
        return True
    # one is a prefix of the other ("tenofovir" vs "tenofovir disoproxil") once salts are gone
    return ta == tb[:len(ta)] or tb == ta[:len(tb)]


def card_names(c):
    names = [c.get("medicine") or ""]
    for x in c.get("forms") or []:
        if x and x not in names:
            names.append(x)
    return names


def is_combination(ingredients):
    """A label is a combination when it has two or more distinct active ingredients."""
    return len(ingredients or []) >= 2


def card_is_the_combination(c, ingredients):
    """True when the card itself is the combination product (every ingredient is a name of the card)."""
    if not is_combination(ingredients):
        return False
    names = card_names(c)
    return all(any(names_match(ing, n) for n in names) for ing in ingredients)


def needs_own_label(c, ingredients):
    """Q22: a combination pill's label does not count for one of its parts."""
    return is_combination(ingredients) and not card_is_the_combination(c, ingredients)


def dailymed_url(setid):
    return f"https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={setid}"


def dailymed_search(name, get=_get, pages=2, pagesize=40):
    """Search DailyMed for SPLs whose drug_name is this medicine. No network in tests: pass get=..."""
    hits, url = [], (
        "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json"
        f"?drug_name={requests.utils.quote(name)}&pagesize={pagesize}"
    )
    for _ in range(pages):
        r = get(url)
        if r.status_code != 200:
            break
        data = r.json()
        hits.extend(data.get("data") or [])
        url = (data.get("metadata") or {}).get("next_page_url")
        if not url or url == "null":
            break
    return hits


def _published_key(hit):
    raw = hit.get("published_date") or ""
    try:
        return time.strptime(raw, "%b %d, %Y")
    except ValueError:
        return time.strptime("Jan 01, 1900", "%b %d, %Y")


def pick_single_ingredient_hit(hits, c, ingredients_of):
    """Newest search hit that is not a combination and whose only ingredient is this card's medicine."""
    ranked = sorted(hits, key=_published_key, reverse=True)
    for h in ranked:
        if title_looks_combo(h.get("title") or ""):
            continue
        ings = ingredients_of(h["setid"])
        if not ings or is_combination(ings):
            continue
        if any(names_match(ings[0], n) for n in card_names(c)):
            return h, ings
    return None, []


def ingredients_of_url(url, labels_dir, get=_get):
    """Active ingredients of a source label. Uses the label cache when it already has them; otherwise fetches."""
    lab = read_label(url, labels_dir) if url else {"ingredients": []}
    if lab.get("ingredients"):
        return tidy_ingredients(lab["ingredients"])
    host = re.match(r"https?://([^/]+)", url or "")
    host = host.group(1) if host else ""
    ings = []
    try:
        if host == "dailymed.nlm.nih.gov":
            sid = _dailymed_setid(url)
            r = get(f"https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/{sid}.xml")
            if r.status_code == 200 and b"<" in r.content[:40]:
                ings = _ingredients_from_spl(r.content)
            else:
                r2 = get(url)
                if r2.status_code == 200:
                    ings = _ingredients_from_dailymed_html(r2.content)
        elif host == "www.ema.europa.eu":
            r = get(url, spaced=True) if get is _get else get(url)
            if r.status_code == 200:
                ings = _ema_active_substances(r.text)
        elif host == "www.accessdata.fda.gov":
            # Only a short product line counts (e.g. "Oxycodone and Acetaminophen Tablets").
            # The indications section lists species and warnings and is not a product title.
            header = (lab.get("text") or "").split("INDICATIONS")[0][:400]
            ings = ingredients_from_title(header) if header.strip() else []
    except Exception:
        ings = []
    ings = tidy_ingredients(ings)
    if ings:
        lab["ingredients"] = ings
        # refresh the cache file when we have a path
        f = os.path.join(labels_dir, hashlib.sha1((url or "").encode()).hexdigest()[:16] + ".json")
        if os.path.exists(f):
            json.dump(lab, open(f, "w"))
    return ings


def find_single_ingredient_label(c, labels_dir, get=_get, ingredients_of=None):
    """DailyMed search for this medicine's own single-ingredient SPL. None if none can be confirmed."""
    def ings_of(setid):
        if ingredients_of:
            return ingredients_of(setid)
        return ingredients_of_url(dailymed_url(setid), labels_dir, get=get)

    hits = dailymed_search(c["medicine"], get=get)
    hit, _ = pick_single_ingredient_hit(hits, c, ings_of)
    if not hit:
        # "Carbidopa Anhydrous" -> search "Carbidopa" as well
        base = " ".join(name_tokens(c["medicine"]))
        if base and base.lower() != (c["medicine"] or "").lower():
            hits = dailymed_search(base, get=get)
            hit, _ = pick_single_ingredient_hit(hits, c, ings_of)
    if hit:
        return dailymed_url(hit["setid"])
    return None


def resolve_source_label(c, labels_dir, get=_get, ingredients_of=None, finder=None):
    """Read the card's source; if it is a combination for another product, use the medicine's own label (Q22).

    Returns (lab, url_used, note). note is empty when the source was kept.
    """
    source = c.get("source") or ""
    if not source:
        return {"status": "no_label", "text": "", "reason": "no source link", "ingredients": [], "url": ""}, source, ""
    lab = read_label(source, labels_dir)
    if lab["status"] != "label":
        return lab, source, ""
    ings = lab.get("ingredients") or ingredients_of_url(source, labels_dir, get=get)
    lab["ingredients"] = ings
    if not needs_own_label(c, ings):
        return lab, source, ""
    found = (finder or find_single_ingredient_label)(c, labels_dir, get=get, ingredients_of=ingredients_of)
    if not found or found == source:
        return lab, source, "combo source, no single-ingredient label found"
    new_lab = read_label(found, labels_dir)
    if new_lab["status"] != "label":
        return lab, source, "combo source, single-ingredient lookup had no readable label"
    return new_lab, found, f"replaced combo source ({', '.join(ings)}) with the medicine's own label"


# ---------------------------------------------------------------- no-label source kinds
def source_kind(url, reason=""):
    """A short source type for the no-label file. Unknown hosts fall under 'other'."""
    if (reason or "").startswith("combination only") or "no single-ingredient label" in (reason or ""):
        return COMBO_ONLY
    if not (url or "").strip():
        return "missing link"
    host = (re.match(r"https?://([^/]+)", url) or [None, ""])[1]
    if "whocc.no" in host:
        return "WHO ATC"
    if "idrblab" in host:
        return "TTD"
    if "pmda.go.jp" in host:
        return "PMDA general list"
    if "clinicaltrials.gov" in host:
        return "trial page"
    if "dailymed.nlm.nih.gov" in host:
        return "DailyMed, no indications section" if "no indications" in (reason or "") else "DailyMed, unreadable"
    if "ama-assn.org" in host:
        return "USAN name page"
    if "fda.gov" in host:
        return "FDA label, unreadable"
    if "ema.europa.eu" in host:
        return "EMA page, unreadable"
    return "other"


def kind_sort_key(kind):
    try:
        return SOURCE_KIND_ORDER.index(kind)
    except ValueError:
        return len(SOURCE_KIND_ORDER)


# ---------------------------------------------------------------- order, estimate, plan
def is_never_checked(rec):
    """True when there is no completed check: missing, no date, or pending a combination relabel."""
    if not rec:
        return True
    if rec.get("pending") == PENDING_RELABEL:
        return True
    return not rec.get("date")


def last_checked_date(c, checked):
    rec = checked.get(card_key(c)) or {}
    return "" if is_never_checked(rec) else rec["date"]


def mark_not_yet_checked(checked, keys):
    """Mark these cards as never checked so the next run picks them first (no date)."""
    for key in keys:
        checked[key] = {"pending": PENDING_RELABEL}
    return checked


def order_cards(cards, checked):
    """Oldest-checked first; never checked first. Ties: a fixed hash, so the slice is spread over the diseases.

    A card is never checked if it is absent from checked.json, has no date, or is
    marked pending=combo-relabel (a combination source that will be replaced).
    """
    def k(c):
        return (last_checked_date(c, checked), hashlib.sha1(card_key(c).encode()).hexdigest())
    return sorted(cards, key=k)


def combo_only_row(r):
    """A no-label-file row for a card whose source is a combination with no single-ingredient label."""
    return {
        "disease_id": r["disease_id"], "disease": r["disease"],
        "medicine_id": r["medicine_id"], "medicine": r["medicine"],
        "source_kind": COMBO_ONLY,
        "label_url": r.get("source_url") or r.get("label_url") or "",
        "note": r.get("note") if (r.get("note") or "").startswith("combination only") else COMBO_ONLY_NOTE,
    }


def merge_combo_only(no_label, combo_only_cards):
    """Append combination-only cards to the no-label list. They keep their source. Does not touch flags."""
    seen = {(r["disease_id"], r["medicine_id"]) for r in no_label}
    out = list(no_label)
    for r in combo_only_cards:
        key = (r["disease_id"], r["medicine_id"])
        if key in seen:
            continue
        out.append(combo_only_row(r))
        seen.add(key)
    out.sort(key=lambda r: (kind_sort_key(r["source_kind"]), r["label_url"] or "", r["disease"], r["medicine"]))
    return out


def write_no_label_csv(date, no_label):
    path = os.path.join(REPO, "flags", f"{date}-no-label.csv")
    os.makedirs(os.path.join(REPO, "flags"), exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=NL_COLS, extrasaction="ignore")
        w.writeheader()
        w.writerows(no_label)
    kind_counts = {}
    for r in no_label:
        kind_counts[r["source_kind"]] = kind_counts.get(r["source_kind"], 0) + 1
    return path, kind_counts


def combo_only_sentence(n, flag_count=None):
    extra = (" of %s" % flag_count) if flag_count is not None else ""
    return (
        'The %s "combination only" cards have a combination product\'s label and no '
        "single-ingredient label of their own; they keep that source. They are listed here in addition to "
        "any flag their model verdict already earned. This does not change the flag count%s."
        % (n, extra)
    )


def update_md_no_label_counts(date, no_label, kind_counts, flag_count=None):
    """Refresh the no-label table in flags/<date>.md. Leaves the flag count as it is."""
    md_path = os.path.join(REPO, "flags", f"{date}.md")
    if not os.path.exists(md_path):
        return
    lines = [
        f"## No readable label: {len(no_label)}",
        "",
        "| Source | Cards |",
        "|---|---|",
    ]
    for kind in SOURCE_KIND_ORDER:
        if kind in kind_counts:
            lines.append(f"| {kind} | {kind_counts[kind]} |")
    for kind in kind_counts:
        if kind not in SOURCE_KIND_ORDER:
            lines.append(f"| {kind} | {kind_counts[kind]} |")
    lines += ["", f"Sorted list: `flags/{date}-no-label.csv`."]
    if kind_counts.get(COMBO_ONLY):
        lines += ["", combo_only_sentence(kind_counts[COMBO_ONLY], flag_count)]
    lines.append("")
    text = open(md_path).read()
    text = re.sub(
        r"## No readable label:.*?(?=\n## |\Z)",
        "\n".join(lines),
        text,
        count=1,
        flags=re.S,
    )
    open(md_path, "w").write(text)


def _md_after_no_label(md, date, kind_counts, flag_count):
    md += ["", f"Sorted list: `flags/{date}-no-label.csv`."]
    n = kind_counts.get(COMBO_ONLY)
    if n:
        md += ["", combo_only_sentence(n, flag_count), ""]
    else:
        md.append("")
    return md


def user_message(c, label_url, text):
    names = (c["medicine"],) + tuple(x for x in c["forms"] if x and x != c["medicine"])
    syn = "; ".join(c["also_called"])
    return (f"MEDICINE: {c['medicine']}\nFORMS: {', '.join(names)}\n"
            f"DISEASE: {c['disease']} ({c['disease_id']})\nDISEASE ALSO CALLED: {syn or 'none listed'}\n"
            f"LABEL SOURCE: {label_url}\n\nLABEL TEXT:\n{text}")


def est_cost(user, system, prices):
    tin = (len(user) + len(system)) // 3 + 20          # ~3 chars per token: the benchmark's conservative rule
    return tin, tin / 1e6 * prices[0] + OUT_ALLOWANCE / 1e6 * prices[1]


def cmd_plan(a):
    if not os.environ.get("ANTHROPIC_API_KEY", "").strip():
        sys.exit("ANTHROPIC_API_KEY is not set. Nothing was written.")
    B, S, _ = bench()
    model = B.MODEL
    prices = S.PRICES[model]
    W = a.work; os.makedirs(W, exist_ok=True)
    fp0, rev0 = fingerprint()
    ids = [l.strip() for l in open(os.path.join(HERE, "diseases.txt")) if l.strip()]
    cards, failed = walk_cards(ids)
    fp1, rev1 = fingerprint()
    json.dump(cards, open(os.path.join(W, "cards.json"), "w"))
    checked = json.load(open(a.checked)) if os.path.exists(a.checked) else {}
    live_red = [c for c in cards if c["red"]]
    pool = [c for c in cards if not c["red"]]
    ordered = order_cards(pool, checked)
    labels_dir = os.path.join(W, "labels")

    chosen, reqs, est_total, tin_total = [], [], 0.0, 0
    n_label = n_nolabel = n_combo = 0
    i = 0
    stop = False
    while i < len(ordered) and not stop:
        chunk = ordered[i:i + 48]; i += 48
        with cf.ThreadPoolExecutor(4) as ex:
            labs = list(ex.map(lambda c: resolve_source_label(c, labels_dir), chunk))
        for c, (lab, used_url, combo_note) in zip(chunk, labs):
            if lab["status"] != "label":
                chosen.append({**c, "custom_id": "", "label_status": "no_label",
                               "label_url": c["source"], "reason": lab["reason"], "combo_note": combo_note})
                n_nolabel += 1
                continue
            user = user_message(c, used_url, lab["text"])
            tin, cost = est_cost(user, B.SYSTEM, prices)
            if est_total + cost > a.budget:
                stop = True; break
            cid = f"fl-{len(reqs) + 1:05d}"
            reqs.append({"custom_id": cid, "params": {"model": model, "max_tokens": MAX_TOKENS,
                         "output_config": {"effort": "low"}, "system": B.SYSTEM,
                         "messages": [{"role": "user", "content": user}]}})
            chosen.append({**c, "custom_id": cid, "label_status": "label", "label_url": used_url,
                           "reason": "", "combo_note": combo_note, "source_was": c["source"]})
            if combo_note.startswith("replaced"):
                n_combo += 1
            est_total += cost; tin_total += tin; n_label += 1
        print(f"  planned {len(chosen)} cards ({n_label} to the model, {n_nolabel} no label), est ${est_total:.3f}", flush=True)

    S.load_requests  # (validated below)
    with open(os.path.join(W, "requests.jsonl"), "w") as f:
        for r in reqs:
            f.write(json.dumps(r) + "\n")
    for r in reqs:
        S.validate_request(r)
    plan = {"date": a.date, "model": model, "fingerprint_start": fp0, "fingerprint_end": fp1, "revision_start": rev0,
            "revision_end": rev1, "diseases_listed": len(ids), "diseases_failed": failed, "cards_on_pages": len(cards),
            "cards_red_skipped": len(live_red), "cards_planned": len(chosen), "requests": len(reqs), "no_label": n_nolabel,
            "combo_replaced": n_combo, "input_tokens_est": tin_total, "output_allowance_per_card": OUT_ALLOWANCE,
            "estimate_usd": round(est_total, 4), "budget_usd": a.budget, "hard_cap_usd": HARD_CAP,
            "max_tokens": MAX_TOKENS}
    json.dump(plan, open(os.path.join(W, "plan.json"), "w"), indent=1)
    json.dump(chosen, open(os.path.join(W, "chosen.json"), "w"))
    print(json.dumps(plan, indent=1))


# ---------------------------------------------------------------- submit
def cmd_submit(a):
    B, S, _ = bench()
    W = a.work
    plan = json.load(open(os.path.join(W, "plan.json")))
    if plan["estimate_usd"] > HARD_CAP:
        sys.exit("Estimate is over the hard cap. Nothing sent.")
    if not a.yes:
        sys.exit("Add --yes to submit (this spends API credit).")
    reqs = S.load_requests(os.path.join(W, "requests.jsonl"))
    os.chdir(W)                                    # submit_batch writes its state file in the cwd
    state = "batch_state.json"
    if os.path.exists(state):
        bid = json.load(open(state))["id"]
        print(f"Resuming batch {bid}")
    else:
        bid = S.submit(reqs)
    deadline = time.time() + a.max_wait
    while True:
        b = S.http("GET", f"{S.BASE}/v1/messages/batches/{bid}")
        print(f"{time.strftime('%H:%M')} {b['processing_status']} {b.get('request_counts')}", flush=True)
        if b["processing_status"] == "ended":
            break
        if time.time() > deadline:
            print(f"NOT FINISHED within the wait. Batch id: {bid}. Resume: submit --yes (same work dir).")
            return 3
        time.sleep(a.every)
    S.download(b, "results.jsonl")
    return 0


# ---------------------------------------------------------------- report
def usage_cost(result, prices):
    if result.get("type") != "succeeded":
        return 0.0, 0, 0
    u = result["message"]["usage"]
    i = u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0)
    o = u.get("output_tokens", 0)
    return i / 1e6 * prices[0] + o / 1e6 * prices[1], i, o


def flag_reason(verdict, previous):
    """Why a card is a flag, or '' if it is not. NO_LABEL is never a flag."""
    parts = []
    if verdict in FLAG_VERDICTS:
        parts.append(verdict)
    if previous and previous != verdict:
        parts.append("changed since last check")
    return "; ".join(parts)


def decide(chosen, results, labels_dir, B, S, SC, prices):
    rows = []
    for c in chosen:
        r = {"disease_id": c["disease_id"], "disease": c["disease"], "medicine_id": c["medicine_id"], "medicine": c["medicine"],
             "verdict": "", "quote": "", "label_url": c["label_url"], "model": "", "cost": 0.0, "note": "", "list": c["list"]}
        if not c["custom_id"]:
            r.update(verdict="NO_LABEL", note=c["reason"])
        else:
            res = results.get(c["custom_id"])
            if res is None:
                r.update(verdict="UNCLEAR", note="no result in batch")
            else:
                r["cost"], _, _ = usage_cost(res, prices)
                if res.get("type") == "succeeded":
                    r["model"] = res["message"].get("model", "")
                d, why = SC.parse(res)
                if d is None:
                    r.update(verdict="UNCLEAR", note=why)
                else:
                    r.update(verdict=d["verdict"], quote=d.get("quote", ""), note=d.get("note", ""))
                    if d["verdict"] in ("YES", "PARTIAL"):
                        lab = read_label(c["label_url"], labels_dir)
                        q = SC.norm(d.get("quote", ""))
                        if not (q and q.strip('".') in SC.norm(lab["text"])):
                            r.update(verdict="UNCLEAR", note=f"quote not in label (model said {d['verdict']})")
        rows.append(r)
    return rows


def cmd_report(a):
    B, S, SC = bench()
    prices = S.PRICES[B.MODEL]
    W = a.work
    plan = json.load(open(os.path.join(W, "plan.json")))
    chosen = json.load(open(os.path.join(W, "chosen.json")))
    results = {}
    for line in open(os.path.join(W, "results.jsonl")):
        if line.strip():
            r = json.loads(line); results[r["custom_id"]] = r["result"]
    rows = decide(chosen, results, os.path.join(W, "labels"), B, S, SC, prices)
    actual = sum(r["cost"] for r in rows)
    tin = sum(usage_cost(v, prices)[1] for v in results.values())
    tout = sum(usage_cost(v, prices)[2] for v in results.values())
    checked = json.load(open(a.checked)) if os.path.exists(a.checked) else {}
    for r in rows:
        prev = (checked.get(f"{r['disease_id']}|{r['medicine_id']}") or {}).get("verdict")
        r["previous"] = prev or ""
        r["changed"] = bool(prev and prev != r["verdict"])
        r["flag"] = flag_reason(r["verdict"], prev)
        r["source_kind"] = source_kind(r["label_url"], r["note"]) if r["verdict"] == "NO_LABEL" else ""
    date = a.date
    os.makedirs(os.path.join(REPO, "flags"), exist_ok=True)
    cols = ["disease_id", "disease", "medicine_id", "medicine", "verdict", "quote", "label_url", "model", "cost", "flag", "note"]
    flags = [r for r in rows if r["flag"]]
    with open(os.path.join(REPO, "flags", f"{date}.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader()
        for r in flags:
            w.writerow({**r, "cost": f"{r['cost']:.6f}"})
    no_label = [r for r in rows if r["verdict"] == "NO_LABEL"]
    combo_only = []
    for c in chosen:
        note = c.get("combo_note") or ""
        if "no single-ingredient label found" in note:
            combo_only.append({**c, "label_url": c.get("source") or c.get("label_url") or "", "note": note})
    combo_path = os.path.join(REPO, "flags", f"{date}-combo-would-switch.csv")
    if os.path.exists(combo_path):
        for r in csv.DictReader(open(combo_path)):
            if not r.get("replacement_url"):
                combo_only.append(r)
    no_label = merge_combo_only(no_label, combo_only)
    _, kind_counts = write_no_label_csv(date, no_label)
    for r in rows:
        checked[f"{r['disease_id']}|{r['medicine_id']}"] = {"date": date, "verdict": r["verdict"]}
    json.dump(checked, open(a.checked, "w"), indent=0, sort_keys=True)
    cnt = {v: sum(1 for r in rows if r["verdict"] == v) for v in ("YES", "PARTIAL", "NO", "UNCLEAR", "NO_LABEL")}
    over = actual > HARD_CAP
    md = [f"# Flagger run {date}", "",
          f"- Build checked: `{plan['fingerprint_start']}` (revision {plan['revision_start']}); at the end of the card walk: `{plan['fingerprint_end']}`",
          f"- Model: `{plan['model']}`, low effort, Message Batches API (batch price)",
          f"- Cards on the {plan['diseases_listed']} listed pages' Approved tabs: {plan['cards_on_pages']} ({plan['cards_red_skipped']} already red, skipped)",
          f"- **Cards checked: {len(rows)}** ({plan['requests']} sent to the model, {plan['no_label']} with no readable label)",
          f"- Estimated cost: USD {plan['estimate_usd']:.4f} (budget {plan['budget_usd']:.2f}, hard cap {HARD_CAP:.2f})",
          f"- **Actual cost: USD {actual:.4f}** ({tin} input + {tout} output tokens)" + (" **OVER THE CAP: halve tomorrow's slice**" if over else ""),
          "", "## Verdicts", "", "| Verdict | Cards |", "|---|---|"]
    md += [f"| {k} | {v} |" for k, v in cnt.items()]
    md += ["", f"## Flags: {len(flags)}", "",
           "NO, UNCLEAR, and any card whose verdict changed since its last check. "
           f"Full list with the quoted sentences: `flags/{date}.csv`. "
           "A flag is evidence for a person to read, never a change to a card. "
           "Cards with no readable label are not flags; they are listed separately below.",
           "", f"## No readable label: {len(no_label)}", "",
           "| Source | Cards |", "|---|---|"]
    for kind in SOURCE_KIND_ORDER:
        if kind in kind_counts:
            md.append(f"| {kind} | {kind_counts[kind]} |")
    extra = [k for k in kind_counts if k not in SOURCE_KIND_ORDER]
    for kind in extra:
        md.append(f"| {kind} | {kind_counts[kind]} |")
    md = _md_after_no_label(md, date, kind_counts, len(flags))
    if plan["diseases_failed"]:
        md += ["## Pages that could not be read", ""] + [f"- {x}" for x in plan["diseases_failed"]] + [""]
    open(os.path.join(REPO, "flags", f"{date}.md"), "w").write("\n".join(md) + "\n")
    json.dump(rows, open(os.path.join(W, "decided.json"), "w"))
    print(json.dumps({"checked": len(rows), "counts": cnt, "flags": len(flags),
                      "no_label": len(no_label), "no_label_by_source": kind_counts,
                      "estimate": plan["estimate_usd"], "actual": round(actual, 4), "tokens": [tin, tout]}))
    return 0


def cmd_combos(a):
    """List tonight's labeled cards whose source is a combination that Q22 would replace. No model call."""
    W = a.work
    chosen = json.load(open(os.path.join(W, "chosen.json")))
    labels_dir = os.path.join(W, "labels")
    labeled = [c for c in chosen if c.get("custom_id")]
    # Unique sources first, so each label is inspected once.
    by_url = {}
    for c in labeled:
        by_url.setdefault(c["label_url"] or c.get("source") or "", []).append(c)

    def inspect(url):
        ings = ingredients_of_url(url, labels_dir)
        return url, ings

    with cf.ThreadPoolExecutor(4) as ex:
        inspected = dict(ex.map(lambda u: inspect(u), by_url))

    rows = []
    # Look up a replacement once per medicine name.
    found_for = {}
    for c in labeled:
        url = c["label_url"] or c.get("source") or ""
        ings = inspected.get(url) or []
        if not needs_own_label(c, ings):
            continue
        med = c["medicine"]
        if med not in found_for:
            found_for[med] = find_single_ingredient_label(c, labels_dir)
        replacement = found_for[med]
        rows.append({
            "disease_id": c["disease_id"], "disease": c["disease"],
            "medicine_id": c["medicine_id"], "medicine": c["medicine"],
            "source_url": url, "ingredients": ", ".join(ings),
            "replacement_url": replacement or "",
            "note": ("would switch to the medicine's own single-ingredient label"
                     if replacement and replacement != url
                     else "combo source, no single-ingredient label found"),
        })
    date = a.date
    os.makedirs(os.path.join(REPO, "flags"), exist_ok=True)
    path = os.path.join(REPO, "flags", f"{date}-combo-would-switch.csv")
    cols = ["disease_id", "disease", "medicine_id", "medicine", "source_url", "ingredients", "replacement_url", "note"]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    switched = [r for r in rows if r["replacement_url"] and r["replacement_url"] != r["source_url"]]
    none = [r for r in rows if not r["replacement_url"] or r["replacement_url"] == r["source_url"]]
    # Next run should read the cards that would switch first, against the single-medicine label.
    checked_path = a.checked
    checked = json.load(open(checked_path)) if os.path.exists(checked_path) else {}
    mark_not_yet_checked(checked, [f"{r['disease_id']}|{r['medicine_id']}" for r in switched])
    json.dump(checked, open(checked_path, "w"), indent=0, sort_keys=True)
    # Combination-only cards go on the no-label list; they keep their source and are not flags for that reason.
    nl_path = os.path.join(REPO, "flags", f"{date}-no-label.csv")
    existing = list(csv.DictReader(open(nl_path))) if os.path.exists(nl_path) else []
    no_label = merge_combo_only(existing, none)
    _, kind_counts = write_no_label_csv(date, no_label)
    flags_path = os.path.join(REPO, "flags", f"{date}.csv")
    flag_count = sum(1 for _ in csv.DictReader(open(flags_path))) if os.path.exists(flags_path) else None
    update_md_no_label_counts(date, no_label, kind_counts, flag_count)
    md_path = os.path.join(REPO, "flags", f"{date}.md")
    section = [
        f"## Combination sources that Q22 would replace: {len(rows)}",
        "",
        "A combination pill's label does not count for one of its parts (Kashish, Q22). "
        "From the next run, the flagger looks up that medicine's own single-ingredient DailyMed SPL instead. "
        f"{len(switched)} would switch and have been marked not-yet-checked so they are read first with that label; "
        f"{len(none)} have no single-ingredient label, keep their source, and are listed as "
        f'"combination only" in `flags/{date}-no-label.csv`. '
        "That listing does not change the flag count"
        + (f" of {flag_count}" if flag_count is not None else "") + ". "
        f"List: `flags/{date}-combo-would-switch.csv`.",
        "",
    ]
    if os.path.exists(md_path):
        text = open(md_path).read()
        text = re.sub(r"\n## Combination sources that Q22 would replace:.*", "", text, flags=re.S)
        open(md_path, "w").write(text.rstrip() + "\n\n" + "\n".join(section))
    print(json.dumps({"combo_cards": len(rows), "would_switch": len(switched),
                      "no_single_found": len(none), "no_label": len(no_label),
                      "flags": flag_count, "file": path}))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["plan", "submit", "report", "combos"])
    ap.add_argument("--work", default="/workspace/flagger/work")
    ap.add_argument("--checked", default=os.path.join(REPO, "checked.json"))
    ap.add_argument("--date", default=time.strftime("%Y-%m-%d"))
    ap.add_argument("--budget", type=float, default=0.90)
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--every", type=int, default=120)
    ap.add_argument("--max-wait", type=int, default=2 * 3600)
    a = ap.parse_args(argv)
    if a.budget > HARD_CAP:
        sys.exit("budget is over the USD 1.00 hard cap")
    return {"plan": cmd_plan, "submit": cmd_submit, "report": cmd_report, "combos": cmd_combos}[a.cmd](a) or 0


if __name__ == "__main__":
    sys.exit(main())
