from __future__ import annotations
from openhinglish.types import Token, Candidate, Category, Config
from openhinglish.data_loader import load_gazetteer


def _is_titlecase(surface: str) -> bool:
    return surface[:1].isupper() and surface[1:].islower()


def resolve_entities(tokens: list[Token], config: Config) -> list[Token]:
    names = load_gazetteer("gazetteers/names.tsv")
    brands = load_gazetteer("gazetteers/brands.tsv")

    for idx, tok in enumerate(tokens):
        low = tok.surface.lower()
        ent = None
        cat = None
        if low in brands:
            ent, cat = brands[low], Category.BRAND
        elif low in names:
            ent, cat = names[low], Category.NAME

        if ent is None:
            continue

        sentence_initial = idx == 0
        # A lowercase, non-sentence-initial token that already resolved to a
        # known common Hindi word should keep that reading — do not let a name
        # or brand override it (e.g. "zara" = ज़रा "a little", not the brand
        # "Zara"; "diya" = दिया, not the name "Diya"). The entity stays as an
        # alternative so the signal is not lost.
        hindi_word_wins = (
            tok.category == Category.HINDI_ROMAN
            and not _is_titlecase(tok.surface)
            and not sentence_initial
        )
        supports_entity = (not hindi_word_wins) and (
            _is_titlecase(tok.surface) or sentence_initial or cat == Category.BRAND
            or tok.category in (Category.NAME, Category.BRAND, Category.UNKNOWN)
        )

        entity_candidate = Candidate(cat, ent.display, ent.pron_deva, 0.92)
        if supports_entity:
            if tok.category not in (Category.NAME, Category.BRAND):
                prev = Candidate(tok.category, tok.display_form, tok.tts_form, tok.confidence)
                tok.alternatives = [prev] + tok.alternatives[: config.nbest_k - 1]
            tok.category = cat
            tok.display_form = ent.display
            tok.tts_form = ent.pron_deva
            tok.confidence = 0.92
            tok.trace.append(f"S4: entity {cat.value} {low} -> {ent.display}/{ent.pron_deva}")
        else:
            tok.alternatives = [entity_candidate] + tok.alternatives[: config.nbest_k - 1]
            tok.trace.append(f"S4: entity {cat.value} kept as alternative (no casing/context support)")
    return tokens
