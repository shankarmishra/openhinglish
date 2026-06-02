from __future__ import annotations
from openhinglish.types import Token, Category, Config

_HINDI_UNITS = ["शून्य", "एक", "दो", "तीन", "चार", "पाँच", "छह", "सात", "आठ", "नौ", "दस"]
_ENGLISH_UNITS = ["zero", "one", "two", "three", "four", "five", "six", "seven",
                  "eight", "nine", "ten"]
_LETTER_DEVA = {
    "a": "ए", "b": "बी", "c": "सी", "d": "डी", "e": "ई", "f": "एफ", "g": "जी",
    "h": "एच", "i": "आई", "j": "जे", "k": "के", "l": "एल", "m": "एम", "n": "एन",
    "o": "ओ", "p": "पी", "q": "क्यू", "r": "आर", "s": "एस", "t": "टी", "u": "यू",
    "v": "वी", "w": "डब्ल्यू", "x": "एक्स", "y": "वाई", "z": "ज़ेड",
}


def number_to_hindi_words(n: int) -> str:
    if n == 100:
        return "सौ"
    if 0 <= n <= 10:
        return _HINDI_UNITS[n]
    return str(n)  # V1 seed: only 0-10 and 100 spelled out; extend later


def _number_to_english_words(n: int) -> str:
    if 0 <= n <= 10:
        return _ENGLISH_UNITS[n]
    if n == 100:
        return "hundred"
    return str(n)


def expand_numerals(tokens: list[Token], config: Config) -> list[Token]:
    for tok in tokens:
        if tok.category == Category.NUMBER and tok.surface.isdigit():
            n = int(tok.surface)
            if config.number_words_lang == "english":
                tok.tts_form = _number_to_english_words(n)
            else:
                tok.tts_form = number_to_hindi_words(n)
            tok.trace.append(f"S5: number {n} -> '{tok.tts_form}'")
            continue

        if tok.surface.isupper() and tok.surface.isalpha() and 2 <= len(tok.surface) <= 5:
            tok.category = Category.ACRONYM
            tok.tts_form = " ".join(_LETTER_DEVA.get(ch.lower(), ch) for ch in tok.surface)
            tok.trace.append(f"S5: acronym {tok.surface} -> '{tok.tts_form}'")
    return tokens
