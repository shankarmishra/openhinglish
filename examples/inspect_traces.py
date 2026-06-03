"""
inspect_traces.py — Show the full per-token trace for one sentence.

The trace list exposes every decision the normalization pipeline made for
each token: which rule fired, which lexicon matched, confidence deltas, etc.
This is useful for debugging or understanding why a word was rendered a
certain way.

Run:
    python examples/inspect_traces.py
"""

import sys

sys.stdout.reconfigure(encoding="utf-8")

import textwrap

from openhinglish import normalize

SENTENCE = "Bhai, mujhe Bengaluru ka train ticket book karna hai"


def pretty_trace(token):
    print(f"  surface      : {token.surface}")
    print(f"  category     : {token.category}")
    print(f"  display_form : {token.display_form}")
    print(f"  tts_form     : {token.tts_form}")
    print(f"  confidence   : {token.confidence:.3f}")

    if token.alternatives:
        alts = ", ".join(
            f"{a.display_form}({a.confidence:.2f})" for a in token.alternatives
        )
        print(f"  alternatives : {alts}")

    if token.trace:
        print(f"  trace ({len(token.trace)} step(s)):")
        for i, step in enumerate(token.trace, start=1):
            # Each trace entry may be a string or a structured object/dict;
            # format generically so it works regardless of internal type.
            step_text = str(step)
            wrapped = textwrap.indent(
                textwrap.fill(step_text, width=70), prefix="      "
            )
            print(f"    [{i}] {wrapped.strip()}")
    else:
        print("  trace        : (empty)")


def main():
    print(f"Sentence: {SENTENCE}")
    print()

    result = normalize(SENTENCE)

    print(f"Display : {result.display}")
    print(f"TTS     : {result.tts}")
    print(f"Conf    : {result.confidence:.3f}")
    print()
    print(f"Tokens  : {len(result.tokens)}")
    print()

    for idx, token in enumerate(result.tokens, start=1):
        print(f"--- Token {idx} ---")
        pretty_trace(token)
        print()


if __name__ == "__main__":
    main()
