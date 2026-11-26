# Moonlight

**What open research records about the medicines for a disease, with the official label beside each one.**

[moonlightclues.com](https://www.moonlightclues.com) · open source (MIT) · hello@moonlightclues.com

> **Not medical advice.** Moonlight is for learning and research. Never start, stop or change any medicine without a doctor.

## What it is

Search a disease and get one page in plain words, with three tabs:

- **Approved:** medicines the database records as approved for the disease. Each card opens the regulator's label, or says that none was found.
- **In trials:** some of the medicines in trials for the disease. Not every trial is listed yet.
- **New clues:** approved medicines that act on a protein linked to the disease, with no trial for it recorded. Things to read about, never treatments.

## Why it matters

Records of approvals, trials and research are public, but they are scattered and written for scientists. Moonlight puts them on one page that a doctor, a researcher or a carer can read, and shows the source behind every card. When a record looks wrong, the card says so, and we report it to the source.

## What it has achieved

**1. A published audit: "Do the labels agree?"**
We checked 4,631 of Moonlight's "Approved" cards, on 1,313 disease pages, against official medicine labels. Where a label could be read (3,934 cards), it at least partly supports the card in 83.2% of cases and fully matches in 25.3%. A computer program read the labels; no doctor has checked its work yet. These figures show how far the database agrees with the labels, not whether any medicine works. The report, data and code are public: [doi.org/10.5281/zenodo.24549100](https://doi.org/10.5281/zenodo.24549100).

**2. Corrections confirmed by Open Targets.**
We reported seven records that listed a medicine as approved for a disease it is not approved for. Open Targets confirmed all seven and will correct them in release 26.12 ([thread 2105](https://community.opentargets.org/t/2105)). This is a correction to their data, not an endorsement of Moonlight.

## Found a wrong medicine?

Open a **"Wrong medicine"** issue, or email hello@moonlightclues.com, with the disease, the medicine, what is wrong and a source if you have one. Please do not send personal health information.

Every correction we have made by hand is in [moonlight/corrections.json](moonlight/corrections.json).

## Run it

```bash
pip install -r requirements.txt
uvicorn moonlight.api:app --port 8080   # http://localhost:8080
pytest                                  # uses saved answers in fixtures/
```

## Data

Moonlight reads one open database, the [Open Targets Platform](https://platform.opentargets.org). If a medicine is missing there, it is missing here.

## Team and licence

**The SMAKS Project**, Kochi: Kashish Dugar (product lead), Shreshth Dugar (co-founder and maintainer), Sidha Mogha (design).

Licence: [MIT](LICENSE) © 2026 The SMAKS Project. An application to Open Source Collective for fiscal hosting is pending.

See [CONTRIBUTING.md](CONTRIBUTING.md), the [Code of Conduct](CODE_OF_CONDUCT.md) and [GOVERNANCE.md](GOVERNANCE.md).
