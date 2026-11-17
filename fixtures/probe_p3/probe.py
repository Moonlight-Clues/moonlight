"""Night watch P3, step 1 and 2: ask Open Targets, save every raw answer.

Read-only study. It talks to Open Targets only. It never calls Moonlight's
site or Gemini, and it writes only under fixtures/probe_p3/.

Run from the repo root:   python3 fixtures/probe_p3/probe.py

For each disease name it sends fetch.py's SEARCH_QUERY, word for word, and
takes the hit whose name is exactly the name asked (capitals ignored). Then
it sends fetch.py's DISEASE_DRUGS_QUERY with ONE field added, "source"
inside clinicalReports. Like fetch.py, the medicine question is asked twice
(a third time if the two answers differ) and the answer with the most
reports is kept. It waits one second between requests. It can be stopped
and started again: an answer already saved is not asked again.
"""

import json
import pathlib
import re
import sys
import time

import requests

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from moonlight import fetch  # noqa: E402  (only its words are used: URL and the two queries)

HERE = pathlib.Path(__file__).resolve().parent
RESPONSES = HERE / "responses"
WAIT_SECONDS = 1.0
TIMEOUT_SECONDS = 120
AGENT_WANTED = 50

OLD_WORDS = "clinicalReports { url clinicalStage }"
NEW_WORDS = "clinicalReports { url clinicalStage source }"
assert fetch.DISEASE_DRUGS_QUERY.count(OLD_WORDS) == 1
PROBE_QUERY = fetch.DISEASE_DRUGS_QUERY.replace(OLD_WORDS, NEW_WORDS)

COMMON = """asthma, type 2 diabetes mellitus, hypertension, migraine,
epilepsy, rheumatoid arthritis, psoriasis, atopic eczema, Crohn's
disease, ulcerative colitis, osteoporosis, gout, heart failure, atrial
fibrillation, chronic obstructive pulmonary disease, chronic kidney
disease, hypothyroidism, depressive disorder, schizophrenia, bipolar
disorder, Parkinson disease, Alzheimer disease, multiple sclerosis,
glaucoma, endometriosis, tuberculosis, malaria, HIV infection,
hepatitis B, hepatitis C"""

CANCER = """breast cancer, prostate cancer, colorectal cancer, lung cancer,
melanoma, multiple myeloma, chronic myeloid leukemia, acute myeloid
leukemia, acute lymphoblastic leukemia, chronic lymphocytic leukemia,
Hodgkin lymphoma, ovarian cancer, pancreatic cancer, glioblastoma,
hepatocellular carcinoma, renal cell carcinoma, thyroid cancer,
bladder cancer, neuroblastoma, osteosarcoma"""

RARE = """cystic fibrosis, Duchenne muscular dystrophy, spinal muscular
atrophy, Huntington disease, amyotrophic lateral sclerosis, Gaucher
disease, Fabry disease, Pompe disease, phenylketonuria, hemophilia A,
hemophilia B, sickle cell anemia, beta-thalassemia, myasthenia gravis,
narcolepsy, Wilson disease, hereditary angioedema, acromegaly, Cushing
syndrome, sarcoidosis, systemic sclerosis, Behcet disease, hidradenitis
suppurativa, idiopathic pulmonary fibrosis, pulmonary arterial
hypertension, amyloidosis, Friedreich ataxia, Rett syndrome, Dravet
syndrome, tuberous sclerosis, neurofibromatosis type 1, retinitis
pigmentosa, achondroplasia, osteogenesis imperfecta, paroxysmal
nocturnal hemoglobinuria, immune thrombocytopenia, systemic lupus
erythematosus, ankylosing spondylitis, vitiligo, alopecia areata"""

# AGENT'S CHOICE. Written before any answer was seen: everyday names of
# diseases the agent believed have an approved medicine, grouped by body
# system. The candidates are tried one system after another, round and
# round (first of each system, then second of each, ...), so the 50 are
# spread out. A candidate is taken only if Open Targets has that exact name
# AND its answer holds at least one approved item (analyse.py's test, which
# is fetch.py's). The first 50 taken are the set. Every candidate that was
# tried and not taken is written down in agent_choice_log.json.
AGENT_POOL = [
    ("heart and blood vessels", ["angina pectoris", "myocardial infarction", "deep vein thrombosis",
                                 "hypercholesterolemia", "pulmonary embolism", "stroke"]),
    ("lungs and airways", ["allergic rhinitis", "pneumonia", "influenza", "COVID-19",
                           "bronchiectasis"]),
    ("stomach, gut and liver", ["gastroesophageal reflux disease", "irritable bowel syndrome",
                                "peptic ulcer disease", "constipation",
                                "primary biliary cholangitis", "pancreatitis"]),
    ("kidney and bladder", ["overactive bladder", "benign prostatic hyperplasia",
                            "urinary tract infection", "erectile dysfunction",
                            "nephrotic syndrome", "urinary incontinence"]),
    ("hormones and metabolism", ["type 1 diabetes mellitus", "obesity", "hyperthyroidism",
                                 "Graves disease", "growth hormone deficiency",
                                 "familial hypercholesterolemia"]),
    ("brain and nerves", ["insomnia", "restless legs syndrome", "neuropathic pain",
                          "essential tremor", "trigeminal neuralgia", "cluster headache"]),
    ("mind", ["anxiety disorder", "attention deficit hyperactivity disorder",
              "obsessive-compulsive disorder", "panic disorder",
              "post-traumatic stress disorder", "alcohol dependence"]),
    ("eye and ear", ["age-related macular degeneration", "dry eye syndrome", "uveitis",
                     "allergic conjunctivitis", "diabetic retinopathy", "Meniere disease"]),
    ("skin", ["acne", "rosacea", "urticaria", "actinic keratosis", "seborrheic dermatitis",
              "pemphigus vulgaris"]),
    ("bones, joints and muscles", ["osteoarthritis", "psoriatic arthritis", "fibromyalgia",
                                   "juvenile idiopathic arthritis", "Paget's disease of bone",
                                   "polymyalgia rheumatica"]),
    ("blood", ["iron deficiency anemia", "neutropenia", "venous thromboembolism",
               "polycythemia vera", "myelofibrosis", "aplastic anemia"]),
    ("infections", ["herpes zoster", "candidiasis", "leprosy", "toxoplasmosis",
                    "Lyme disease", "schistosomiasis", "onchocerciasis",
                    "cytomegalovirus infection"]),
    ("women's and men's health", ["polycystic ovary syndrome", "uterine fibroid", "infertility",
                                  "pre-eclampsia", "hypogonadism", "menopause"]),
    ("more cancers", ["basal cell carcinoma", "gastric cancer", "cervical cancer",
                      "mantle cell lymphoma", "follicular lymphoma", "mesothelioma"]),
]


def names_of(block: str) -> list:
    return [" ".join(name.split()) for name in block.split(",")]


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


_last_sent = [0.0]
_requests_sent = [0]


def send(body: dict) -> dict:
    """The one place this probe talks to Open Targets. One second apart."""
    wait = WAIT_SECONDS - (time.monotonic() - _last_sent[0])
    if wait > 0:
        time.sleep(wait)
    for attempt in range(4):
        try:
            response = requests.post(fetch.URL, json=body, timeout=TIMEOUT_SECONDS)
            response.raise_for_status()
            break
        except requests.RequestException as error:  # network trouble: wait and try again
            if attempt == 3:
                raise
            print(f"    network trouble ({error!r}), trying again", flush=True)
            time.sleep(2 ** (attempt + 1))
    _last_sent[0] = time.monotonic()
    _requests_sent[0] += 1
    return response.json()


def save(path: pathlib.Path, thing, indent=None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(thing, indent=indent, ensure_ascii=False) + "\n", encoding="utf-8")


def load(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def search(name: str) -> dict:
    """Search for one name. Saves the request and the raw answer."""
    request_path = RESPONSES / "search" / f"{slug(name)}.request.json"
    answer_path = RESPONSES / "search" / f"{slug(name)}.response.json"
    body = {"query": fetch.SEARCH_QUERY, "variables": {"text": name, "size": fetch.SEARCH_SIZE}}
    if answer_path.exists():
        answer = load(answer_path)
    else:
        answer = send(body)
        save(request_path, body, indent=2)
        save(answer_path, answer, indent=2)
    if answer.get("errors") or not answer.get("data"):
        return {"asked": name, "found": False, "why": f"search error: {answer.get('errors')}"}
    hits = [hit for hit in answer["data"]["search"]["hits"] if hit["entity"] == "disease"]
    exact = [hit for hit in hits if fetch.plain_words(hit["name"]) == fetch.plain_words(name)]
    seen = [{"id": hit["id"], "name": hit["name"]} for hit in hits]
    if not exact:
        return {"asked": name, "found": False, "why": "no hit with exactly this name",
                "hits_seen": seen}
    return {"asked": name, "found": True, "id": exact[0]["id"], "name": exact[0]["name"],
            "exact_hits": len(exact), "hits_seen": seen}


def rows_of(answer: dict) -> list:
    return answer["data"]["disease"]["drugAndClinicalCandidates"]["rows"]


def report_count(answer: dict) -> int:
    return sum(len(row.get("clinicalReports") or []) for row in rows_of(answer))


def medicine_ids(answer: dict) -> list:
    return sorted((row.get("drug") or {}).get("id") or "" for row in rows_of(answer))


def is_good(answer: dict) -> bool:
    return (not answer.get("errors") and answer.get("data") is not None
            and answer["data"].get("disease") is not None)


def disease_drugs(disease_id: str) -> dict:
    """The medicine list of one disease, asked the way fetch.py asks: twice,
    a third time if the two differ, the fullest kept. Saved as sent."""
    request_path = RESPONSES / "disease_drugs" / f"{disease_id}.request.json"
    answer_path = RESPONSES / "disease_drugs" / f"{disease_id}.response.json"
    note_path = RESPONSES / "disease_drugs" / f"{disease_id}.asks.json"
    if answer_path.exists() and note_path.exists():
        return load(note_path)
    body = {"query": PROBE_QUERY, "variables": {"diseaseId": disease_id}}
    answers = []
    note = {"disease_id": disease_id, "asks": 0, "report_counts": [], "kept": None, "problem": None}
    while len(answers) < fetch.ASKS_AT_MOST:
        answer = send(body)
        note["asks"] += 1
        if not is_good(answer):
            note["problem"] = f"not a good answer: {str(answer)[:300]}"
            save(note_path, note, indent=2)
            return note
        answers.append(answer)
        note["report_counts"].append(report_count(answer))
        if medicine_ids(answer) != medicine_ids(answers[0]):
            note["problem"] = "answers held different medicines; nothing saved"
            save(note_path, note, indent=2)
            return note
        if len(answers) == fetch.ASKS_AT_FIRST and answers[0] == answers[1]:
            break
    kept = max(answers, key=report_count)  # max keeps the earliest of equals
    note["kept"] = answers.index(kept) + 1
    note["answers_all_equal"] = all(answer == answers[0] for answer in answers)
    save(request_path, body, indent=2)
    save(answer_path, kept)  # as sent, not re-indented: some are large
    save(note_path, note, indent=2)
    return note


def main() -> int:
    sys.path.insert(0, str(HERE))
    import analyse  # the approved test lives there, next to the grouping

    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    version_answer = send({"query": fetch.VERSION_QUERY, "variables": {}})
    save(RESPONSES / "data_version.response.json", version_answer, indent=2)

    diseases = []
    for set_name, block in (("COMMON", COMMON), ("CANCER", CANCER), ("RARE", RARE)):
        for name in names_of(block):
            entry = search(name)
            entry["set"] = set_name
            if entry["found"]:
                entry["asks"] = disease_drugs(entry["id"])
            diseases.append(entry)
            print(set_name, name, "->", entry.get("id") or entry["why"], flush=True)

    taken_ids = {entry["id"] for entry in diseases if entry["found"]}
    order = []
    longest = max(len(names) for _, names in AGENT_POOL)
    for place in range(longest):
        for system, names in AGENT_POOL:
            if place < len(names):
                order.append((system, names[place]))
    choice_log = []
    taken = 0
    for system, name in order:
        if taken >= AGENT_WANTED:
            choice_log.append({"asked": name, "system": system, "taken": False,
                               "why": "not tried: 50 were already taken"})
            continue
        entry = search(name)
        entry["set"] = "AGENT"
        entry["system"] = system
        why = None
        if not entry["found"]:
            why = entry["why"]
        elif entry["id"] in taken_ids:
            why = f"same entry as a disease already in the study ({entry['id']})"
        else:
            entry["asks"] = disease_drugs(entry["id"])
            if entry["asks"]["problem"]:
                why = entry["asks"]["problem"]
            else:
                answer = load(RESPONSES / "disease_drugs" / f"{entry['id']}.response.json")
                approved = [f for f in analyse.families_of(answer).values() if f["approved"]]
                if not approved:
                    why = "exact name found, but no approved item on its list"
        if why is None:
            taken += 1
            taken_ids.add(entry["id"])
            diseases.append(entry)
        choice_log.append({"asked": name, "system": system, "taken": why is None, "why": why,
                           "id": entry.get("id"), "hits_seen": entry.get("hits_seen")})
        print("AGENT", name, "->", entry.get("id"), "taken" if why is None else why, flush=True)

    save(HERE / "diseases.json", {
        "started": started,
        "finished": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "data_version": version_answer["data"]["meta"]["dataVersion"],
        "requests_sent_this_run": _requests_sent[0],
        "diseases": diseases,
    }, indent=2)
    save(HERE / "agent_choice_log.json", choice_log, indent=2)
    print("requests sent this run:", _requests_sent[0])
    return 0


if __name__ == "__main__":
    sys.exit(main())
