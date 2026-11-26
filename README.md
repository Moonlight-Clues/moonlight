# Moonlight

**What open research records about the medicines for a disease, each with its source.** · [moonlightclues.com](https://www.moonlightclues.com) · MIT · hello@moonlightclues.com

> **Not medical advice.** Moonlight is for learning and research. Never start, stop or change any medicine without a doctor.

**Vision:** anyone, anywhere, can see what research records about the medicines linked to a disease, and the source behind each one.

**Mission:** turn open drug–disease research into plain cards. Each card links to its source record, and every error we find is logged in public and reported upstream.

## Why it matters (30 seconds)

**Doctors anywhere** see in one page what is approved for a disease, what is in trials and what is worth reading about, each with a link to its source record. **Researchers and pharma teams** get an open, auditable view of the same records, with every correction published. **Patients and carers**, especially families living with rare diseases, can see what research says about their condition, in plain words, with links to show their doctor. It's free and open source, built in Kochi, India.

## Built on Open Targets

The [Open Targets Platform](https://platform.opentargets.org) is a free, open-source resource from [Open Targets](https://www.opentargets.org), a public–private partnership founded in 2014 by EMBL-EBI, the Wellcome Sanger Institute and GSK, and now also including Genentech, MSD, Pfizer and Sanofi. It brings together genetics, genomics, literature, clinical-trial and drug data to link targets (proteins) to diseases, and it's updated every quarter. Moonlight is a window onto this one open database, so its gaps are our gaps, on top of our own.

## Three tabs per disease

- **Approved:** medicines Open Targets records as approved for the disease. Each card says whether a DailyMed, FDA, EMA or PMDA record is attached.
- **In trials:** some of the medicines in clinical trials for the disease, each with its trial or research record. Not every trial is listed yet.
- **New clues:** approved medicines that act on a protein linked to the disease but have no trial recorded for it in Open Targets. They're things to read about, never treatments.

## Corrections and studies

- **Open Targets** confirmed seven wrong approval records we reported and is fixing them in release 26.12 ([thread 2105](https://community.opentargets.org/t/2105)). We have also written to the **Therapeutic Target Database (TTD)** maintainers about the same seven entries.
- **124-disease study** ([report](https://github.com/Moonlight-Clues/moonlight/blob/probe-approval-proof/fixtures/probe_p3/REPORT.md)): 724 of the 2,096 medicines on the Approved lists had no DailyMed, FDA or EMA approval report attached. That measures the strength of the proof, not whether each card is right, and those cards are now marked. **50-disease study** of "up or down" data: [report](https://github.com/Moonlight-Clues/moonlight/blob/probe-direction/fixtures/probe_p4/REPORT.md).
- Confirmed fixes live in [moonlight/corrections.json](moonlight/corrections.json).

## Found a wrong medicine?

Open a **"Wrong medicine"** issue or email hello@moonlightclues.com with the disease, the medicine, what's wrong and a source (a regulator label or trial ID) if you have one. Please don't send personal health information.

Please read [CONTRIBUTING.md](CONTRIBUTING.md) and the [Code of Conduct](CODE_OF_CONDUCT.md) before opening a pull request.

## Run it

```bash
pip install -r requirements.txt
uvicorn moonlight.api:app --port 8080   # http://localhost:8080
pytest                                  # uses saved answers in fixtures/
```


## Team, funding, licence

**The SMAKS Project**, Kochi: Kashish Dugar (product lead), Shreshth Dugar (co-founder and maintainer), Sidha Mogha (design). Licence: [MIT](LICENSE) © 2026 The SMAKS Project. Data: Open Targets Platform.

The project has applied to [Open Source Collective](https://opencollective.com/opensource) for fiscal hosting. If accepted, donations and spending will be public on Open Collective. Moonlight does not sell data and does not run advertisements. See also [GOVERNANCE.md](GOVERNANCE.md) and [CONTRIBUTING.md](CONTRIBUTING.md).
