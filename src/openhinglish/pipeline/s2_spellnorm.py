from __future__ import annotations
from difflib import get_close_matches
from openhinglish.types import Token, Candidate, Category, Config
from openhinglish.data_loader import load_map, load_set
from openhinglish.pipeline.s1_classify import classify

_SKIP = {Category.PUNCT, Category.EMOJI, Category.URL, Category.NUMBER,
         Category.HINDI_DEVA, Category.NAME, Category.BRAND}


def spell_normalize(tokens: list[Token], config: Config) -> list[Token]:
    abbrev = load_map("lexicons/sms_abbrev.tsv", key_col=0, val_col=1)
    english = load_set("lexicons/english_freq.tsv", col=0)
    roman_hindi = load_set("lexicons/roman_hindi.tsv", col=0)

    changed = False
    for tok in tokens:
        low = tok.surface.lower()

        # (a) deterministic abbreviation expansion
        if low in abbrev:
            tok.display_form = abbrev[low]
            tok.tts_form = abbrev[low]
            tok.trace.append(f"S2: abbrev {low} -> {abbrev[low]}")
            changed = True
            continue

        # never touch a confident exact lexicon hit
        if tok.category in _SKIP or low in english or low in roman_hindi:
            continue

        # (b) conservative typo fix against canonical vocab (english only in V1)
        match = get_close_matches(low, english, n=1, cutoff=0.85)
        if match:
            original = Candidate(tok.category, tok.surface, tok.tts_form,
                                 max(0.0, tok.confidence - 0.1))
            tok.alternatives = [original] + tok.alternatives[: config.nbest_k - 1]
            tok.display_form = match[0]
            tok.tts_form = match[0]
            tok.trace.append(f"S2: typo {low} -> {match[0]} (original kept as alt)")
            changed = True

    # re-run classification so expanded/fixed surfaces get correct categories
    if changed:
        for tok in tokens:
            if tok.display_form and tok.display_form.lower() != tok.surface.lower():
                tok.surface, tok._reclass = tok.surface, True
        _reclassify(tokens, config)
    return tokens


def _reclassify(tokens: list[Token], config: Config) -> None:
    # Build shadow tokens on the corrected surfaces and copy resulting category/forms.
    from openhinglish.pipeline.s0_preprocess import tokenize as _tok
    for tok in tokens:
        if getattr(tok, "_reclass", False):
            shadow = classify(_tok(tok.display_form, config), config)
            if shadow:
                s = shadow[0]
                tok.category = s.category
                tok.display_form = s.display_form
                tok.tts_form = s.tts_form
                tok.trace.append(f"S2: reclassified -> {s.category.value}")
            tok._reclass = False
