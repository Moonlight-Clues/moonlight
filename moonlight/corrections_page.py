"""Ticket 2.66 (sheet W3). The public corrections page, served at /corrections.

One row per entry of the hand-written lists, so anyone can check our work:
the date, the disease's name, the medicine's name, what the card now shows
(in the card's own words) and the link to what we read. Newest first.

Built once from the lists when the app starts (api.py), never at request
time and never over the network. Names come from moonlight/names.json
(ID -> Open Targets name, written by a script from Open Targets 26.09).
No ID is ever shown: an entry whose medicine or disease has no name there,
or that has no https link, stops the build with ValueError, and with it the
app, like the other hand-written lists (Kashish, 27 Nov, decisions A and B).

What each list's row says it shows (Kashish, 27 Nov, decision C):
    corrections     the card's red sentence, exactly as shown (engine.RED_WORDS)
    approvals       engine.ADDED_LINE, and engine.LIMITED_LINE under it when the
                    entry says "limited": both lines, as the card shows them
    limits          engine.LIMITED_LINE
    confirmed       CONFIRMED_LINE (new words, for Kashish's sheet)
    withdrawals     the card's withdrawal line (W4): REGION_LINES or HAND_WITHDRAWAL_LINE;
                    an entry with a region shows on every page, so ALL_PAGES
    pmda_summaries  the Japan line, engine.pmda_line
    salt_parents    "Forms: ..." with the forms, and ALL_PAGES as the disease
    discontinued    engine.DISCONTINUED_LINE, and ALL_PAGES (read only if present)
"""

import datetime
import html
import json
import pathlib
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from moonlight import engine, explain

HERE = pathlib.Path(__file__).resolve().parent

# The lists, in the ticket's order. A row's place among rows of the same date
# follows this order, then the entry's place in its file.
LISTS = ("corrections", "approvals", "limits", "confirmed", "withdrawals",
         "salt_parents", "discontinued", "pmda_summaries")
LINK_FIELD = {"corrections": "label", "approvals": "label", "limits": "label",
              "confirmed": "label", "withdrawals": "source", "salt_parents": "source",
              "discontinued": "source", "pmda_summaries": "link"}

# Kashish's signed words (ticket 2.66). Changing them needs her approval.
HEADING = ("Every change we made by hand to the database's list, with the label we "
           "read. If you find a mistake, tell us.")
# Kashish, 27 Nov (decision C). New words, for Kashish's sheet.
CONFIRMED_LINE = "Source record opens the label we read."
# Kashish, 27 Nov (decision C). The disease column of a row for every page.
ALL_PAGES = "All pages"
# Words already on the site, reused here (listed in the PR for Kashish's sheet).
SAFETY_LINE = ("For learning and research exploration, not medical advice. Never start, "
               "stop or change any medicine without a doctor.")
SOURCE_LINK = "Source record"
COLUMNS = ("Date", "Disease", "Medicine", "Card", "Source")


@dataclass(frozen=True)
class Row:
    date: str  # "2026-11-26", for sorting
    disease: str
    medicine: str
    lines: Tuple[str, ...]  # what the card shows, one item per line
    source: str

    @property
    def shows(self) -> str:
        """The card's lines, one per text line."""
        return "\n".join(self.lines)

    @property
    def shown_date(self) -> str:
        """"2026-11-26" -> "26 Nov 2026"."""
        day = datetime.date.fromisoformat(self.date)
        return f"{day.day} {day.strftime('%b')} {day.year}"


def _read(name: str):
    """The one place a list (or names.json) is read. Tests replace this.
    A file that is not there gives None."""
    path = HERE / f"{name}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def entries_of(lists: Dict[str, object]) -> List[Tuple[str, dict, int]]:
    """Every entry of the lists as (list name, entry, place in its file).
    A salt_parents row becomes an entry whose medicine_id is the salt."""
    found = []
    for name in LISTS:
        held = lists.get(name)
        if not held:
            continue
        if name == "salt_parents":
            for place, (salt, row) in enumerate(held.items()):
                found.append((name, dict(row, medicine_id=salt), place))
        else:
            for place, entry in enumerate(held):
                found.append((name, entry, place))
    return found


def link_of(name: str, entry: dict) -> Optional[str]:
    """The entry's https link, or None."""
    link = entry.get(LINK_FIELD[name])
    if isinstance(link, str) and link.startswith("https://"):
        return link
    return None


def ids_needing_names(lists: Dict[str, object]) -> Set[str]:
    """Every medicine and disease ID the rows name."""
    needed: Set[str] = set()
    for name, entry, _ in entries_of(lists):
        needed.add(entry["medicine_id"])
        if name == "salt_parents":
            needed.add(entry["parent"])
        elif name != "discontinued":
            needed.add(entry["disease_id"])
    return needed


def _shows(name: str, entry: dict, medicine: str, names: Dict[str, str]) -> Tuple[str, ...]:
    """The lines the card shows, in its order (Kashish, 27 Nov, decision C)."""
    if name == "approvals" and entry.get("limited") is True:
        return (engine.ADDED_LINE, engine.LIMITED_LINE)  # both, as the card shows them
    return (_one_line(name, entry, medicine, names),)


def _one_line(name: str, entry: dict, medicine: str, names: Dict[str, str]) -> str:
    if name == "corrections":
        return engine.RED_WORDS[entry["note"]]
    if name == "approvals":
        return engine.ADDED_LINE
    if name == "limits":
        return engine.LIMITED_LINE
    if name == "confirmed":
        return CONFIRMED_LINE
    if name == "withdrawals":
        region = entry.get("region")
        return engine.REGION_LINES[region] if region else engine.HAND_WITHDRAWAL_LINE
    if name == "pmda_summaries":
        return engine.pmda_line(entry["summary_date"][:4])
    if name == "salt_parents":
        return "Forms: " + ", ".join([medicine, explain._display(names[entry["medicine_id"]])])
    if name == "discontinued":
        return engine.DISCONTINUED_LINE
    raise ValueError(f"Unknown list: {name}")


def rows() -> List[Row]:
    """Every row of the page, newest first. ValueError if an ID has no name
    or an entry has no link: no ID and no empty link is ever shown."""
    lists = {name: _read(name) for name in LISTS}
    names = _read("names") or {}
    missing = sorted(i for i in ids_needing_names(lists)
                     if not isinstance(names.get(i), str) or not names[i].strip())
    if missing:
        raise ValueError(f"No name in moonlight/names.json for: {', '.join(missing)}")
    no_link = [f"{name}: {entry['medicine_id']} {entry.get('disease_id', '')}".strip()
               for name, entry, _ in entries_of(lists) if not link_of(name, entry)]
    if no_link:
        raise ValueError(f"An entry has no https link: {'; '.join(no_link)}")

    found = []
    for order, (name, entry, place) in enumerate(entries_of(lists)):
        if name == "salt_parents":
            medicine = explain._display(names[entry["parent"]])
            disease = ALL_PAGES
        else:
            medicine = explain._display(names[entry["medicine_id"]])
            # Kashish, 27 Nov: a withdrawal with a region shows on every page
            # (2.65, W4), so its row says "All pages" too.
            on_every_page = name == "discontinued" or (name == "withdrawals" and entry.get("region"))
            disease = ALL_PAGES if on_every_page else names[entry["disease_id"]]
        datetime.date.fromisoformat(entry["date"])  # ValueError if not a real date
        found.append((entry["date"], order, Row(entry["date"], disease, medicine,
                                                _shows(name, entry, medicine, names),
                                                link_of(name, entry))))
    found.sort(key=lambda item: item[1])
    found.sort(key=lambda item: item[0], reverse=True)  # stable: newest first
    return [row for _, _, row in found]


_STYLE = """
:root{--cream:#F5F0E8;--navy:#101F31;--teal:#429D9A;--paper:#FFFFFF;--line:#D5E0E2;--muted:#566877}
*{box-sizing:border-box}
body{margin:0;background:var(--cream);color:var(--navy);font:400 15px/1.55 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
a{color:var(--teal);text-underline-offset:3px}
a:focus-visible{outline:3px solid var(--teal);outline-offset:3px}
.wrap{width:min(100% - 32px,1060px);margin-inline:auto}
.site-header{background:var(--navy);padding:20px 0}
.wordmark{font-family:"Space Grotesk",system-ui,sans-serif;letter-spacing:-.035em;font-size:clamp(27px,5.5vw,35px);font-weight:700;color:#F5F0E8;text-decoration:none}
.safety{position:sticky;top:0;z-index:10;background:#203448;border-bottom:1px solid #5F9E9B}
.safety-inner{padding:11px 0;font-size:12px;line-height:1.45;color:#F4F0E9}
.main{padding:28px 0 58px}
h1{font-family:"Space Grotesk",system-ui,sans-serif;letter-spacing:-.02em;font-size:clamp(20px,4.5vw,28px);line-height:1.25;font-weight:650;margin:0 0 20px}
table{width:100%;border-collapse:collapse;background:var(--paper);border:1px solid var(--line);border-radius:14px}
th,td{text-align:left;vertical-align:top;padding:10px 12px;border-bottom:1px solid var(--line);font-size:14px;overflow-wrap:anywhere}
th{font-size:12px;color:var(--muted);font-weight:700}
td.date{white-space:nowrap}
.site-footer{border-top:1px solid var(--line);padding:24px 0 36px;font-size:12px;color:var(--muted)}
@media(max-width:700px){
  thead{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
  table,tbody,tr,td{display:block;width:100%}
  table{background:none;border:0}
  tr.row{background:var(--paper);border:1px solid var(--line);border-radius:14px;margin:0 0 12px;padding:6px 0}
  td{border:0;padding:4px 14px}
  td::before{content:attr(data-label);display:block;font-size:11px;font-weight:700;color:var(--muted)}
}
"""


def page_html() -> str:
    """The whole page, as one string. Built at start-up by api.py."""
    e = html.escape
    body = []
    for row in rows():
        cells = (("date", e(row.shown_date)), ("disease", e(row.disease)),
                 ("medicine", e(row.medicine)), ("shows", "<br>".join(e(l) for l in row.lines)))
        tds = "".join(f'<td class="{cls}" data-label="{e(label)}">{text}</td>'
                      for (cls, text), label in zip(cells, COLUMNS))
        tds += (f'<td class="source" data-label="{e(COLUMNS[4])}"><a href="{e(row.source)}" '
                f'rel="noopener" target="_blank">{e(SOURCE_LINK)}</a></td>')
        body.append(f'<tr class="row">{tds}</tr>')
    heads = "".join(f'<th scope="col">{e(c)}</th>' for c in COLUMNS)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<title>Moonlight</title>
<style>{_STYLE}</style>
</head>
<body>
<header class="site-header"><div class="wrap"><a class="wordmark" href="/">Moonlight</a></div></header>
<div class="safety" role="note"><div class="wrap safety-inner"><span>{e(SAFETY_LINE)}</span></div></div>
<main class="main"><div class="wrap">
<h1>{e(HEADING)}</h1>
<table>
<thead><tr>{heads}</tr></thead>
<tbody>
{chr(10).join(body)}
</tbody>
</table>
</div></main>
<footer class="site-footer"><div class="wrap">
<p>Found something wrong or have any feedback? Contact <a href="mailto:hello@moonlightclues.com">hello@moonlightclues.com</a></p>
<p>Moonlight · Research exploration only · Not clinical findings · Data from Open Targets and ClinicalTrials.gov</p>
</div></footer>
</body>
</html>
"""
