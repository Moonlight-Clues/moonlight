# Contributing to Moonlight

Thank you for wanting to help. Moonlight is an open-source, source-linked
interface to the [Open Targets Platform](https://platform.opentargets.org).
The live site is [moonlightclues.com](https://www.moonlightclues.com).

Moonlight is not medical advice. Please do not send personal health
information. Please do not add treatment advice, treatment-outcome claims, or
wording that implies Open Targets endorses this project.

This project follows the [Code of Conduct](CODE_OF_CONDUCT.md). Please read it
before taking part.

## Report a wrong medicine

If a card looks wrong, open a **"Wrong medicine"** issue or email
hello@moonlightclues.com with:

- the disease
- the medicine
- what looks wrong
- a source, if you have one (a regulator label or a trial ID)

Please do not include personal health information.

## Run the project locally

```bash
pip install -r requirements.txt
uvicorn moonlight.api:app --port 8080   # http://localhost:8080
pytest                                  # uses saved answers in fixtures/
```

## What a useful contribution looks like

Any of the following is welcome:

- a careful issue, with a source where you have one
- a fix or test for something already described in an issue or ticket
- documentation that makes the project easier to run or to check
- a pull request that keeps the existing tone: plain words, each fact tied
  to a source, no medical advice

You do not have to write code. Careful reports are useful work.

## Pull requests

1. Branch from `main`.
2. Keep the change as small as the job allows.
3. If behaviour changes, add or update a test, and run `pytest`.
4. In the pull request, say what you changed and how you checked it.
5. Do not add secrets, personal health information, PAN or bank details, or
   visitor counts.

Maintainers review pull requests. Please be patient; this is a small team.

## Becoming a maintainer

Maintainer access is granted by the existing maintainers after a record of
careful, source-linked work, and after the person has shown they can follow
this guide and the Code of Conduct. To ask, email hello@moonlightclues.com.
Roles are described in [GOVERNANCE.md](GOVERNANCE.md).
