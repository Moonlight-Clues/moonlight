"""Study P12. How often each fixed text shows, per page and tab, read from
text/ (the visible text of each picture, every box opened). Prints a
markdown table: page -> "approved / trials / clues" counts.

    python fixtures/probe_p12/count_text.py
"""
import pathlib
import re
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PAGES = ["huntington", "type2diabetes", "pah", "myasthenia", "haemophiliaA"]
TEXTS = [
    "A free, open-source explorer of medicines and trials for any disease, built from public research data.",
    "For learning and research exploration, not medical advice. Never start, stop or change any medicine without a doctor.",
    "Explore open research",
    "Research a disease: approved medicines, trials and new clues.",
    "Type a disease name to begin. Research clues, not treatment recommendations.",
    "Search by disease name",
    "New here?",
    "Quick start",
    "Disease results",
    "Also called:",
    "Show more",
    "Source: Open Targets",
    "What open research data says about medicines and this disease. Nothing here is medical advice.",
    "Print this page",
    "How to read a card",
    "Already approved for this disease in at least one country, according to the database. Nothing here says how well any of them works. Listed A to Z.",
    "Talk to your doctor before changing any medicine.",
    "more approved medicine",
    "The database lists no approved medicine under this exact name.",
    "Approved for a narrower disease",
    "Approved for a wider group",
    "The database lists these as approved, but gives no regulator record for them.",
    "The database lists these as approved for this disease. They look like mistakes.",
    "Tap to open",
    "Tap to close",
    "Not listed as approved for this exact disease.",
    "The database lists this as approved, but gives no regulator record for it.",
    "Approved in Japan, according to the database. Moonlight could not find the exact record for this disease.",
    "This approval is missing from the database. We added it from the official label.",
    "The label covers only some people with this disease.",
    "The database records a withdrawal for this medicine in some country or region.",
    "A doctor has told us this looks like a mistake in the database.",
    "This looks like a mistake in the database. The official label is for a different disease.",
    "Forms:",
    "RESEARCH PATHWAY",
    "are pieces of one machine, counted once.",
    "This medicine does not act on one of the 25 proteins most linked to this disease, so no path is shown.",
    "The data does not say which direction this disease needs.",
    "Source record",
    "The database gives no source link for this medicine.",
    "Already being studied for this disease",
    "Medicines being tested for this disease. A separate research category, not a prediction of effectiveness. Not every trial is listed.",
    "No medicine in this data is being studied for this disease.",
    "More medicines in trials for this disease. They do not act on one of the 25 proteins.",
    "New medicines being tested for this disease. The database records no approval for them for any disease.",
    "Never start, stop or change any medicine without a doctor.",
    "But there is a catch.",
    "Opposite way to the approved medicines for this disease.",
    "Approved for another disease, with no recorded link to this one. Connections worth reading about, never treatments.",
    "Ordered by how strongly the proteins are linked to the disease.",
    "Show only the medicines for one protein. Tap again to show all.",
    "No new clues found for this disease.",
    "These push the opposite way to the approved medicines for this disease.",
    "left out because",
    "Left-out counts",
    "Counts only. No medicine names are displayed here.",
    "Not approved anywhere",
    "Unclear link",
    "New search",
    "Found something wrong or have any feedback?",
    "Moonlight · Research exploration only · Not clinical findings · Data from Open Targets",
]


def count(text, words):
    return len(re.findall(re.escape(words), text, flags=re.IGNORECASE))


rows = ["| Text (start) | " + " | ".join(PAGES) + " |", "|---|" + "---|" * len(PAGES)]
for words in TEXTS:
    cells = []
    for n, page in enumerate(PAGES):
        tabs = [(HERE / "text" / f"{n + 2:02d}_{page}_{tab}.txt").read_text(encoding="utf-8")
                for tab in ("approved", "trials", "clues")]
        cells.append(" / ".join(str(count(t, words)) for t in tabs))
    rows.append(f"| {words[:70]} | " + " | ".join(cells) + " |")
front = (HERE / "text" / "00_front.txt").read_text(encoding="utf-8")
guide = (HERE / "text" / "01_guide.txt").read_text(encoding="utf-8")
print("\n".join(rows))
print("\nFront page and guide:")
for words in TEXTS:
    f, g = count(front, words), count(guide, words)
    if f or g:
        print(f"- {words[:70]}: front {f}, guide {g}")
