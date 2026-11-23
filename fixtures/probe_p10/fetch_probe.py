"""Study P10: how the saved answers in this folder were fetched.

Run once on 2026-11-23 from the repo root:  python3 fixtures/probe_p10/fetch_probe.py
It talks to the network. recount.py does not: it only reads the saved files.
It changes nothing in Moonlight. Every answer is saved exactly as it arrived,
next to the question that was sent.
"""
import json
import pathlib
import sys
import time

import requests

HERE = pathlib.Path(__file__).resolve().parent
OT = "https://api.platform.opentargets.org/api/v4/graphql"
CT = "https://clinicaltrials.gov/api/v2/studies"
PARENT = "MONDO_0016971"
TOP = 25  # Moonlight's TOP_TARGETS in moonlight/api.py

FAMILY_Q = """
query Family($diseaseId: String!) {
  meta { dataVersion { year month iteration } }
  disease(efoId: $diseaseId) {
    id name
    parents { id name }
    children { id name }
    descendants
  }
}
"""
# Moonlight's own DISEASE_DRUGS_QUERY fields, plus each report's id, stage
# words, status, title and the diseases the report itself names.
DISEASE_DRUGS_Q = """
query DiseaseDrugs($diseaseId: String!) {
  disease(efoId: $diseaseId) {
    id name
    parents { id name }
    children { id name }
    drugAndClinicalCandidates {
      count
      rows {
        id
        maxClinicalStage
        drug {
          id name drugType maximumClinicalStage
          drugWarnings { warningType }
          parentMolecule { id name maximumClinicalStage drugWarnings { warningType } }
          childMolecules { id name maximumClinicalStage drugWarnings { warningType } }
        }
        clinicalReports {
          id source url clinicalStage type trialPhase phaseFromSource
          trialOverallStatus trialStudyType title
          diseases { diseaseFromSource disease { id name } }
        }
      }
    }
  }
}
"""
# Moonlight's own TARGETS_QUERY.
TARGETS_Q = """
query AssociatedTargets($diseaseId: String!, $size: Int!) {
  disease(efoId: $diseaseId) {
    id
    associatedTargets(page: {index: 0, size: $size}) {
      count
      rows { score target { id approvedSymbol approvedName } }
    }
  }
}
"""
# Moonlight's own TARGET_DRUGS_QUERY, word for word.
TARGET_DRUGS_Q = """
query TargetDrugs($targetId: String!) {
  target(ensemblId: $targetId) {
    id
    drugAndClinicalCandidates {
      count
      rows {
        drug {
          id
          name
          maximumClinicalStage
          drugWarnings { warningType }
          parentMolecule { id name drugWarnings { warningType } }
          childMolecules { id name drugWarnings { warningType } }
          mechanismsOfAction {
            rows {
              actionType
              targets { id }
            }
          }
          indications {
            rows { maxClinicalStage disease { id } }
          }
        }
        clinicalReports { url }
      }
    }
  }
}
"""
# One medicine's own record: what it acts on and every disease it is linked to.
DRUG_Q = """
query Drug($drugId: String!) {
  drug(chemblId: $drugId) {
    id name drugType maximumClinicalStage
    drugWarnings { warningType }
    parentMolecule { id name maximumClinicalStage }
    childMolecules { id name maximumClinicalStage }
    mechanismsOfAction { rows { actionType mechanismOfAction targets { id approvedSymbol } } }
    indications { rows { maxClinicalStage disease { id name } } }
  }
}
"""

session = requests.Session()


def rows_of(answer):
    """How many rows an answer holds, to keep the fullest one."""
    text = json.dumps(answer)
    return len(text)


def ask(query, variables, folder, name, times=2):
    """Ask Open Targets `times` times, keep the fullest answer (Moonlight does
    the same, decision of 2026-11-12), save question and answer."""
    out = HERE / "opentargets" / folder
    out.mkdir(parents=True, exist_ok=True)
    answer_file = out / f"{name}.response.json"
    if answer_file.exists():
        return json.loads(answer_file.read_text())
    body = {"query": query, "variables": variables}
    best, sizes = None, []
    for _ in range(times):
        for attempt in range(4):
            try:
                reply = session.post(OT, json=body, timeout=90)
                reply.raise_for_status()
                answer = reply.json()
                break
            except (requests.RequestException, ValueError) as problem:
                print("  again:", name, problem, file=sys.stderr)
                time.sleep(2 * (attempt + 1))
        else:
            raise SystemExit(f"could not fetch {name}")
        if answer.get("errors"):
            raise SystemExit(f"Open Targets error for {name}: {answer['errors']}")
        sizes.append(rows_of(answer))
        if best is None or rows_of(answer) > rows_of(best):
            best = answer
    if len(set(sizes)) > 1:
        print("  answers differed in size:", name, sizes, file=sys.stderr)
        (out / f"{name}.sizes.json").write_text(json.dumps(sizes))
    (out / f"{name}.request.json").write_text(json.dumps(body, indent=1))
    # The protein answers are long, so they are saved without line breaks.
    if folder == "target_drugs":
        answer_file.write_text(json.dumps(best, separators=(",", ":")))
    else:
        answer_file.write_text(json.dumps(best, indent=1))
    return best


def open_targets():
    family = ask(FAMILY_Q, {"diseaseId": PARENT}, "family", PARENT)
    ids = [PARENT] + family["data"]["disease"]["descendants"]
    medicine_ids, target_ids = set(), {}
    for disease_id in ids:
        drugs = ask(DISEASE_DRUGS_Q, {"diseaseId": disease_id}, "disease_drugs", disease_id, times=3)
        for row in drugs["data"]["disease"]["drugAndClinicalCandidates"]["rows"]:
            drug = row["drug"]
            if drug:
                medicine_ids.add(drug["id"])
                if drug["parentMolecule"]:
                    medicine_ids.add(drug["parentMolecule"]["id"])
                for child in drug["childMolecules"] or []:
                    medicine_ids.add(child["id"])
        targets = ask(TARGETS_Q, {"diseaseId": disease_id, "size": TOP}, "top_targets", disease_id)
        for row in targets["data"]["disease"]["associatedTargets"]["rows"]:
            target_ids[row["target"]["id"]] = row["target"]["approvedSymbol"]
    print(len(ids), "diseases,", len(medicine_ids), "medicine ids,", len(target_ids), "proteins")
    for drug_id in sorted(medicine_ids):
        ask(DRUG_Q, {"drugId": drug_id}, "drug", drug_id)
    # Where does every protein sit for the parent, not only the first 25?
    ask(TARGETS_Q, {"diseaseId": PARENT, "size": 3000}, "top_targets", PARENT + ".all", times=1)
    for target_id in sorted(target_ids):
        ask(TARGET_DRUGS_Q, {"targetId": target_id}, "target_drugs", target_id)


def clinical_trials():
    """Every interventional study whose condition matches the words, all pages."""
    out = HERE / "clinicaltrials"
    out.mkdir(exist_ok=True)
    params = {
        "query.cond": '"limb-girdle muscular dystrophy"',
        "filter.advanced": "AREA[StudyType]INTERVENTIONAL",
        # Only the parts the study asks for. Nobody's contact details are saved.
        "fields": "NCTId,BriefTitle,OfficialTitle,OverallStatus,Phase,StudyType,Condition,"
                  "Keyword,InterventionType,InterventionName,InterventionOtherName,"
                  "ConditionMeshId,ConditionMeshTerm",
        "pageSize": 100,
        "countTotal": "true",
        "format": "json",
    }
    (out / "search.request.json").write_text(json.dumps({"url": CT, "params": params}, indent=1))
    page, token = 1, None
    while True:
        asked = dict(params, **({"pageToken": token} if token else {}))
        reply = session.get(CT, params=asked, timeout=90)
        reply.raise_for_status()
        answer = reply.json()
        (out / f"search.page{page}.response.json").write_text(json.dumps(answer, indent=1))
        print("ClinicalTrials.gov page", page, len(answer.get("studies", [])), "of", answer.get("totalCount"))
        token = answer.get("nextPageToken")
        if not token:
            break
        page += 1


if __name__ == "__main__":
    what = sys.argv[1:] or ["ot", "ct"]
    if "ot" in what:
        open_targets()
    if "ct" in what:
        clinical_trials()
