from __future__ import annotations
from openhinglish.types import Token, NormalizationResult, Category, Config

_NO_SPACE_BEFORE = {".", ",", "!", "?", ";", ":", "।", ")", "]", "}", "%"}


def _join(parts: list[tuple[str, Category]]) -> str:
    out = ""
    for i, (text, cat) in enumerate(parts):
        if i == 0:
            out = text
        elif cat == Category.PUNCT and text in _NO_SPACE_BEFORE:
            out += text
        else:
            out += " " + text
    return out


def assemble(tokens: list[Token], config: Config, input_text: str) -> NormalizationResult:
    display = _join([(t.display_form, t.category) for t in tokens])
    tts = _join([(t.tts_form, t.category) for t in tokens])
    scored = [t.confidence for t in tokens if t.category != Category.PUNCT]
    confidence = sum(scored) / len(scored) if scored else 1.0
    for t in tokens:
        t.trace.append("S6: assembled into display/tts")
    return NormalizationResult(input=input_text, display=display, tts=tts,
                               confidence=confidence, tokens=tokens)
