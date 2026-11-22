"""Study P8b: the one cleaning function. Study folder only; Moonlight does
not use this file.

    clean(texts) -> (sentence, notes)

"texts" is Open Targets' functionDescriptions list for one protein. The
sentence comes from the FIRST text in the list only. The function takes
packaging off and then keeps the first sentence. It never rewords,
shortens or adds a letter. Step by step:

  1. evidence tags in curly braces go, with the full stop that closes them:
         "...mast cells. {ECO:0000269|PubMed:11418668}."  ->  "...mast cells."
  2. the trailing " ." goes:
         "...on the skin. ."  ->  "...on the skin."
  3. a label in square brackets at the very front goes:
         "[Isoform 1]: Cytokine that..."  ->  "Cytokine that..."
  4. line-wrap marks go. UniProt's text file breaks long lines after a
     hyphen or a slash, and the copy keeps a space there:
         "T-cell- attracting"  ->  "T-cell-attracting"
         "IL1RL1/ ST2"         ->  "IL1RL1/ST2"
     A hyphen followed by a joining word is a real "hanging hyphen" and is
     left alone: "alpha- and beta-tubulin", "5'- to 3'". The joining words
     are: and, or, to, nor, but, versus, vs, as, than, rather, through.
  5. keep the first sentence: everything up to the first full stop that is
     followed by a space and then a capital letter, a digit or an opening
     bracket. A full stop right after a known abbreviation ("e.g.", "i.e.",
     "approx.", "sp." ...; the full list is ABBREVIATIONS below) does not
     end the sentence. A single capital letter before the stop DOES end it,
     because "vitamin K." and "complex I." are common sentence ends here.

"notes" says what the function did, so the recount can list every place a
rule fired. "wraps_joined" lists only the joins inside the kept sentence.
Nothing in "notes" changes the sentence.
"""

import re

CURLY = re.compile(r"\s*\{[^{}]*\}\.?")
TRAILING = re.compile(r"(\s+\.)+\s*$")
LABEL = re.compile(r"^\s*\[([^\]]+)\]:\s*")
HANGING = ("and", "or", "to", "nor", "but", "versus", "vs", "as", "than", "rather", "through")
WRAP = re.compile(r"(?<=\S)(?:-(?= (?!(?:%s)\b)[\w(\[])|/(?= [\w(\[])) " % "|".join(HANGING))
ABBREVIATIONS = ("e.g", "i.e", "approx", "ca", "cf", "vs", "sp", "spp", "subsp", "etc", "al", "no",
                 "fig", "ref", "resp", "viz", "incl", "esp", "ser", "var", "st", "dr")
STOP = re.compile(r"\.(?=\s+[A-Z0-9(\[])")


def clean(texts: list) -> tuple:
    notes = {"texts": len(texts), "curly_removed": 0, "trailing_removed": False, "label_removed": "",
             "wraps_joined": [], "abbreviation_stops_skipped": [], "rest_dropped_chars": 0}
    if not texts:
        return "", notes
    text = texts[0]
    notes["curly_removed"] = len(CURLY.findall(text))
    text = CURLY.sub("", text)                                   # 1
    notes["trailing_removed"] = bool(TRAILING.search(text))
    text = TRAILING.sub("", text)                                # 2
    label = LABEL.match(text)
    if label:                                                    # 3
        notes["label_removed"] = label.group(1)
        text = text[label.end():]
    text = " ".join(text.split())
    joins = [(m.start() - i, text[max(0, m.start() - 18):m.end() + 18])      # 4
             for i, m in enumerate(WRAP.finditer(text))]
    text = WRAP.sub(lambda m: m.group(0)[0], text)
    end = len(text)                                              # 5
    for m in STOP.finditer(text):
        before = re.split(r"[\s(\[/]", text[:m.start()])[-1]
        if before.lower() in ABBREVIATIONS:
            notes["abbreviation_stops_skipped"].append(text[max(0, m.start() - 20):m.end() + 12])
            continue
        end = m.end()
        break
    notes["rest_dropped_chars"] = len(text) - end
    notes["wraps_joined"] = [shown for at, shown in joins if at < end]
    notes["wraps_joined_in_dropped_rest"] = len(joins) - len(notes["wraps_joined"])
    return text[:end], notes
