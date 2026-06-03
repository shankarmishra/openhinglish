from __future__ import annotations
from typing import Protocol
from openhinglish.types import Token, Candidate, Category, Config


class Disambiguator(Protocol):
    def resolve(self, tokens: list[Token], config: Config) -> list[Token]:
        ...


class FrequencyDisambiguator:
    """V1 no-op: S1 already ranked by frequency prior. Seam for the V1.1 learned layer."""

    def resolve(self, tokens: list[Token], config: Config) -> list[Token]:
        return tokens


# ---------------------------------------------------------------------------
# Deterministic context rules
# ---------------------------------------------------------------------------
# Each entry maps a lowercase surface to a callable that receives
# (prev_tok | None, tok, next_tok | None) and returns "ENGLISH" | "HINDI_ROMAN" | None.
# None means "no clear signal — leave untouched".

def _prev_cat(prev: Token | None) -> Category | None:
    return prev.category if prev is not None else None


def _next_cat(nxt: Token | None) -> Category | None:
    return nxt.category if nxt is not None else None


def _rule_main(prev: Token | None, tok: Token, nxt: Token | None) -> str | None:
    """'main' → ENGLISH when next token is English (e.g. 'main road');
       'main' → HINDI_ROMAN (मैं) otherwise."""
    if _next_cat(nxt) == Category.ENGLISH:
        return "ENGLISH"
    return None  # keep existing (HINDI_ROMAN wins by frequency)


def _rule_to(prev: Token | None, tok: Token, nxt: Token | None) -> str | None:
    """'to' → ENGLISH only when BOTH neighbours are English tokens
       (e.g. 'going to office'); Hindi 'तो' otherwise."""
    prev_en = _prev_cat(prev) == Category.ENGLISH
    next_en = _next_cat(nxt) == Category.ENGLISH
    if prev_en and next_en:
        return "ENGLISH"
    return None


# Table of known-ambiguous words → rule function
_RULES: dict[str, object] = {
    "main": _rule_main,
    "to": _rule_to,
}


def _find_alt(tok: Token, target_cat: Category) -> Candidate | None:
    """Return the first alternative whose category matches target_cat, or None."""
    for alt in tok.alternatives:
        if alt.category == target_cat:
            return alt
    return None


def _promote(tok: Token, alt: Candidate, reason: str) -> None:
    """Swap alt into the primary slot; demote the old primary into alternatives."""
    old = Candidate(
        category=tok.category,
        display_form=tok.display_form,
        tts_form=tok.tts_form,
        score=tok.confidence,
    )
    # Replace alt in list with old primary so alternatives stay informative.
    tok.alternatives = [old] + [a for a in tok.alternatives if a is not alt]
    tok.category = alt.category
    tok.display_form = alt.display_form
    tok.tts_form = alt.tts_form
    tok.confidence = alt.score
    tok.trace.append(
        f"V3: disambiguated '{tok.surface}' -> {alt.category.value} ({reason})"
    )


class ContextDisambiguator:
    """Rule-based context resolver (V1.1).

    For each token whose lowercase surface appears in _RULES:
      - evaluates the rule with (prev, tok, next) neighbours
      - if the rule signals a category different from the current one,
        AND that category exists in tok.alternatives,
        promotes it and demotes the old choice
      - otherwise leaves the token untouched

    Conservatism guarantee: never crashes on missing alternatives;
    only acts when a rule fires AND the target candidate is present.
    """

    def resolve(self, tokens: list[Token], config: Config) -> list[Token]:
        n = len(tokens)
        for i, tok in enumerate(tokens):
            low = tok.surface.lower()
            if low not in _RULES:
                continue
            rule = _RULES[low]
            prev = tokens[i - 1] if i > 0 else None
            nxt = tokens[i + 1] if i < n - 1 else None
            decision = rule(prev, tok, nxt)  # type: ignore[operator]
            if decision is None:
                continue
            target_cat = Category(decision)
            if tok.category == target_cat:
                # Already the right category; nothing to do.
                continue
            alt = _find_alt(tok, target_cat)
            if alt is None:
                # Target candidate not in n-best — stay conservative.
                continue
            _promote(tok, alt, "context")
        return tokens
