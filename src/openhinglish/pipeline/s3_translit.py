from __future__ import annotations
from openhinglish.types import Token, Category, Config
from openhinglish.data_loader import load_map

# Minimal rule-based akshara fallback for OOV Roman-Hindi (V1 seed; extend over time).
# Ordered longest-first so multi-char clusters match before single chars.
_CONSONANTS = [
    ("chh", "छ"), ("sh", "श"), ("ch", "च"), ("gh", "घ"), ("kh", "ख"),
    ("th", "थ"), ("dh", "ध"), ("bh", "भ"), ("ph", "फ"), ("jh", "झ"),
    ("ng", "ंग"), ("k", "क"), ("g", "ग"), ("j", "ज"), ("t", "त"),
    ("d", "द"), ("n", "न"), ("p", "प"), ("b", "ब"), ("m", "म"),
    ("y", "य"), ("r", "र"), ("l", "ल"), ("v", "व"), ("w", "व"),
    ("s", "स"), ("h", "ह"), ("c", "क"),
]
_MATRA = {"a": "", "aa": "ा", "i": "ि", "ee": "ी", "u": "ु", "oo": "ू",
          "e": "े", "o": "ो", "ai": "ै", "au": "ौ"}
_INDEP = {"a": "अ", "aa": "आ", "i": "इ", "ee": "ई", "u": "उ", "oo": "ऊ",
          "e": "ए", "o": "ओ", "ai": "ऐ", "au": "औ"}
_VOWEL_KEYS = sorted(set(list(_MATRA) + list(_INDEP)), key=len, reverse=True)


def akshara_fallback(word: str) -> str:
    s = word.lower()
    out: list[str] = []
    i = 0
    last_was_consonant = False
    while i < len(s):
        for vk in _VOWEL_KEYS:
            if s.startswith(vk, i):
                out.append(_MATRA[vk] if last_was_consonant else _INDEP[vk])
                last_was_consonant = False
                i += len(vk)
                break
        else:
            for ck, dev in _CONSONANTS:
                if s.startswith(ck, i):
                    if last_was_consonant:
                        out.append("्")  # halant between adjacent consonants
                    out.append(dev)
                    last_was_consonant = True
                    i += len(ck)
                    break
            else:
                out.append(s[i])
                last_was_consonant = False
                i += 1
    return "".join(out)


def transliterate(tokens: list[Token], config: Config) -> list[Token]:
    roman_hindi = load_map("lexicons/roman_hindi.tsv", key_col=0, val_col=1)
    english_tts = load_map("lexicons/english_tts.tsv", key_col=0, val_col=1)

    for tok in tokens:
        low = tok.display_form.lower()
        if tok.category == Category.HINDI_ROMAN:
            if low in roman_hindi:
                dev = roman_hindi[low]
                tok.trace.append(f"S3: translit lookup {low} -> {dev}")
            else:
                dev = akshara_fallback(low)
                tok.trace.append(f"S3: translit akshara-fallback {low} -> {dev}")
            tok.display_form = dev
            tok.tts_form = dev
        elif tok.category == Category.ENGLISH:
            if low in english_tts:
                tok.tts_form = english_tts[low]
                tok.trace.append(f"S3: english tts {low} -> {english_tts[low]}")
            elif " " in low:
                # Multi-word token (e.g. an expanded abbreviation like
                # "btw" -> "by the way"): transliterate word-by-word for TTS,
                # keeping any word we have no mapping for as-is.
                parts = [english_tts.get(w, w) for w in low.split()]
                tok.tts_form = " ".join(parts)
                tok.trace.append(f"S3: english tts (multi-word) {low} -> {tok.tts_form}")
    return tokens
