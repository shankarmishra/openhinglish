"""Command-line interface for OpenHinglish.

    openhinglish "bhai kal mera intv h paytm me"
    openhinglish --json "shankar ka interview RBI me hai"
    openhinglish --english-numbers "paytm pe 4 order"
"""
from __future__ import annotations

import json as _json
import sys

from openhinglish import normalize
from openhinglish.types import Config


def _result_to_dict(res) -> dict:
    return {
        "input": res.input,
        "display": res.display,
        "tts": res.tts,
        "confidence": res.confidence,
        "tokens": [
            {
                "surface": t.surface,
                "category": t.category.value,
                "display_form": t.display_form,
                "tts_form": t.tts_form,
                "confidence": round(t.confidence, 3),
                "alternatives": [
                    {"category": a.category.value, "display_form": a.display_form,
                     "tts_form": a.tts_form, "score": round(a.score, 3)}
                    for a in t.alternatives
                ],
                "trace": t.trace,
            }
            for t in res.tokens
        ],
    }


def app() -> None:
    # Windows consoles default to cp1252 and crash on Devanagari; force UTF-8.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    args = sys.argv[1:]
    as_json = "--json" in args
    lang = "english" if "--english-numbers" in args else "hindi"
    text = " ".join(a for a in args if not a.startswith("--"))

    if not text:
        print('usage: openhinglish [--json] [--english-numbers] "your hinglish text"')
        return

    res = normalize(text, Config(number_words_lang=lang))
    if as_json:
        print(_json.dumps(_result_to_dict(res), ensure_ascii=False, indent=2))
    else:
        print(f"display: {res.display}")
        print(f"tts    : {res.tts}")


if __name__ == "__main__":
    app()
