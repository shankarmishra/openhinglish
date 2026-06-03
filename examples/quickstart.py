"""
quickstart.py — OpenHinglish basic usage demo.

Run:
    python examples/quickstart.py
"""

import sys

sys.stdout.reconfigure(encoding="utf-8")

from openhinglish import normalize

SENTENCES = [
    "Aaj mausam bahut accha hai",
    "Main Zomato se pizza order kar raha hoon",
    "Kal meeting hai toh please on time aana",
    "Yaar, WhatsApp pe message kar dena",
]


def print_token_table(tokens):
    col = "{:<18} {:<16} {:<20} {:<20} {:<10}"
    header = col.format("surface", "category", "display_form", "tts_form", "confidence")
    print(header)
    print("-" * len(header))
    for tok in tokens:
        print(
            col.format(
                tok.surface,
                tok.category,
                tok.display_form,
                tok.tts_form,
                f"{tok.confidence:.3f}",
            )
        )


def main():
    for sentence in SENTENCES:
        print("=" * 60)
        print(f"INPUT   : {sentence}")

        result = normalize(sentence)

        print(f"DISPLAY : {result.display}")
        print(f"TTS     : {result.tts}")
        print(f"CONF    : {result.confidence:.3f}")
        print()
        print("Tokens:")
        print_token_table(result.tokens)
        print()


if __name__ == "__main__":
    main()
