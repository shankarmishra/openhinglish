from __future__ import annotations
import re
from openhinglish.types import Token, Candidate, Category, Config
from openhinglish.data_loader import load_map, load_set, load_gazetteer

_DEVANAGARI = re.compile(r"[ऀ-ॿ]")
_STRUCTURAL = {Category.PUNCT, Category.EMOJI, Category.URL, Category.NUMBER}


def _english_score(word: str, freq: dict[str, str]) -> float:
    f = int(freq.get(word.lower(), 0))
    return min(0.95, 0.4 + f / 200000.0) if f else 0.0


def classify(tokens: list[Token], config: Config) -> list[Token]:
    english = load_set("lexicons/english_freq.tsv", col=0)
    english_freq = load_map("lexicons/english_freq.tsv", key_col=0, val_col=1)
    roman_hindi = load_map("lexicons/roman_hindi.tsv", key_col=0, val_col=1)
    roman_hindi_freq = load_map("lexicons/roman_hindi.tsv", key_col=0, val_col=2)
    names = load_gazetteer("gazetteers/names.tsv")
    brands = load_gazetteer("gazetteers/brands.tsv")

    for tok in tokens:
        if tok.category in _STRUCTURAL:
            continue
        low = tok.surface.lower()

        if _DEVANAGARI.search(tok.surface):
            tok.category = Category.HINDI_DEVA
            tok.confidence = 1.0
            tok.trace.append("S1: script=devanagari -> HINDI_DEVA")
            continue

        cands: list[Candidate] = []
        if low in brands:
            cands.append(Candidate(Category.BRAND, brands[low].display, brands[low].pron_deva, 0.9))
        if low in names:
            cands.append(Candidate(Category.NAME, names[low].display, names[low].pron_deva, 0.85))
        if low in roman_hindi:
            f = int(roman_hindi_freq.get(low, 0))
            cands.append(Candidate(Category.HINDI_ROMAN, tok.surface, roman_hindi[low],
                                   min(0.9, 0.5 + f / 24000.0)))
        if low in english:
            cands.append(Candidate(Category.ENGLISH, tok.surface, tok.surface,
                                   _english_score(low, english_freq)))

        if not cands:
            cands.append(Candidate(Category.UNKNOWN, tok.surface, tok.surface, 0.1))

        cands.sort(key=lambda c: c.score, reverse=True)
        best, rest = cands[0], cands[1:config.nbest_k]
        tok.category = best.category
        tok.display_form = best.display_form
        tok.tts_form = best.tts_form
        tok.confidence = best.score
        tok.alternatives = rest
        tok.trace.append(f"S1: classified {best.category.value} (score={best.score:.2f}, "
                         f"{len(rest)} alt)")
    return tokens
