"""Protein: one sentence on what a protein does, in UniProt's own words.

    sentence(texts) -> the sentence, or None

"texts" is Open Targets' functionDescriptions list for one protein. UniProt
wrote the words. Moonlight reads them through Open Targets and never asks
UniProt. The sentence comes from the FIRST text in the list only.

The function is like taking a letter out of its envelope. The packaging
comes off, the first sentence is kept, and no word is changed, added or
moved. Step by step (steps 1 to 5 are the study's, from
fixtures/probe_p8/cleaned_sentences/clean.py on the branch probe-uniprot;
steps 6 and 7 are ticket 3.8):

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
     left alone: "alpha- and beta-tubulin", "5'- to 3'".
  5. keep the first sentence: everything up to the first full stop that is
     followed by a space and then a capital letter, a digit or an opening
     bracket. A full stop right after a known abbreviation ("e.g.", "i.e."
     ...) does not end the sentence. A single capital letter before the
     stop DOES end it ("vitamin K.", "complex I.").
  6. citations in round brackets that start "PubMed:" go, with the space
     before them:
         "...cells (PubMed:123, PubMed:456)."  ->  "...cells."
  7. if what is left is longer than 200 characters, there is no sentence
     at all. A sentence is never cut short and never gets "...".

No sentence is None, never an empty string. No AI touches the sentence.
"""

import re
from typing import Iterable, Optional

LIMIT = 200  # characters; Kashish, 23 Nov 2026

CURLY = re.compile(r"\s*\{[^{}]*\}\.?")
TRAILING = re.compile(r"(\s+\.)+\s*$")
LABEL = re.compile(r"^\s*\[([^\]]+)\]:\s*")
HANGING = ("and", "or", "to", "nor", "but", "versus", "vs", "as", "than", "rather", "through")
WRAP = re.compile(r"(?<=\S)(?:-(?= (?!(?:%s)\b)[\w(\[])|/(?= [\w(\[])) " % "|".join(HANGING))
ABBREVIATIONS = ("e.g", "i.e", "approx", "ca", "cf", "vs", "sp", "spp", "subsp", "etc", "al", "no",
                 "fig", "ref", "resp", "viz", "incl", "esp", "ser", "var", "st", "dr")
STOP = re.compile(r"\.(?=\s+[A-Z0-9(\[])")
CITATION = re.compile(r"\s*\(PubMed:[^()]*\)")


def sentence(texts: Optional[Iterable[str]]) -> Optional[str]:
    """The first sentence of the first text, with the packaging off.

    None if there is no text, or if the sentence is longer than LIMIT.
    """
    texts = list(texts or ())
    if not texts or not texts[0]:
        return None
    text = texts[0]
    text = CURLY.sub("", text)                                   # 1
    text = TRAILING.sub("", text)                                # 2
    label = LABEL.match(text)
    if label:                                                    # 3
        text = text[label.end():]
    text = " ".join(text.split())
    text = WRAP.sub(lambda mark: mark.group(0)[0], text)         # 4
    end = len(text)                                              # 5
    for stop in STOP.finditer(text):
        before = re.split(r"[\s(\[/]", text[:stop.start()])[-1]
        if before.lower() in ABBREVIATIONS:
            continue
        end = stop.end()
        break
    text = text[:end]
    text = CITATION.sub("", text)                                # 6
    if not text.strip(" ."):
        return None
    if len(text) > LIMIT:                                        # 7
        return None
    return text
