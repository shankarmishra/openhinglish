from __future__ import annotations
import re
import unicodedata
from openhinglish.types import Token, Category, Config

_TOKEN_RE = re.compile(
    r"https?://\S+|www\.\S+"                                  # URL
    r"|[A-Za-zऀ-ॿ]+"                                # word (latin / devanagari)
    r"|\d+(?:[.,:]\d+)*"                                      # number
    r"|[\U0001F300-\U0001FAFF☀-➿]"                  # emoji-ish
    r"|[^\sA-Za-z0-9ऀ-ॿ]"                           # single punctuation char
)


def _category(text: str) -> Category:
    if text.startswith(("http://", "https://", "www.")):
        return Category.URL
    if text[0].isdigit():
        return Category.NUMBER
    if re.fullmatch(r"[A-Za-zऀ-ॿ]+", text):
        return Category.UNKNOWN
    if re.fullmatch(r"[\U0001F300-\U0001FAFF☀-➿]", text):
        return Category.EMOJI
    return Category.PUNCT


def tokenize(text: str, config: Config) -> list[Token]:
    text = unicodedata.normalize("NFC", text)
    tokens: list[Token] = []
    for m in _TOKEN_RE.finditer(text):
        surface = m.group(0)
        cat = _category(surface)
        tokens.append(Token(
            surface=surface, start=m.start(), end=m.end(),
            category=cat, display_form=surface, tts_form=surface,
            trace=[f"S0: tokenized as {cat.value}"],
        ))
    return tokens
