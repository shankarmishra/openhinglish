# DEVLOG 001 — Introducing OpenHinglish

**Date:** 2026-06-02  
**Author:** Shankar Mishra (solo maintainer)  
**Status:** V0.1 — Foundation complete. Skeleton, not yet a product.

---

## The moment that started this

I was testing a voice-bot pipeline a few months ago. The input was a WhatsApp-style
message:

> `bhai kal mera intv h paytm me`

The TTS engine received that string more or less as-is, because no one on the team had
thought to write normalization code yet. What came out of the speakers was something like
"bye-ee kal mera int-v aitch pay-tee-em may" — each token pronounced with English letter
rules, with no concept of what language it was in or what the abbreviations meant.

Nobody laughed. This was a real product in pre-launch testing.

Someone patched it with a regex. Someone else added a few hardcoded replacements. The
patch made that specific sentence work. Three weeks later a new set of user queries broke
it again in a different way. I watched this cycle happen twice before I stopped and asked
the obvious question: why does this not exist as a library?

---

## Why existing solutions don't solve it

The honest answer is that the acoustic modeling problem for Indian languages is largely
solved. **AI4Bharat IndicF5** (MIT license, 11 languages, near-human quality) is
genuinely excellent. **Indic-Parler-TTS** (Apache-2.0) and **CosyVoice2-0.5B**
(Apache-2.0, about 150 ms latency) are also strong. If you hand any of these a clean
Devanagari sentence, the output audio is good.

The operative word is "clean Devanagari." IndicF5's documentation describes Devanagari
input. It does not document what to do with `bhai kal mera intv h paytm me`. That gap —
between the Roman-script Hinglish that users actually type and the native-script input
that TTS engines expect — is the normalization problem. Every team that integrates one of
these TTS engines has to solve it themselves.

**ElevenLabs** and **Sarvam Bulbul v2** (11 Indian languages, API) are capable closed
systems. They are not an answer here: you cannot inspect what they do, you cannot fix it
when it is wrong, and they carry per-call cost. The moment "paytm" comes out as
"pay-tee-em" instead of "पे-टी-एम" in a Sarvam integration, you have no lever to correct
it.

**The ad-hoc regex approach** is what everyone actually uses, and it is what I want to
replace. It does not generalize. It has no concept of confidence or ambiguity. It is not
testable in any principled way. It is not community-maintainable. Every team that writes
it throws it away and rewrites it for the next project.

---

## What V0.1 actually does today

I want to be direct about what exists and what does not.

**What exists:**

A deterministic, 7-stage normalization pipeline that takes a Roman-Hinglish string and
returns a structured result with two outputs:

```python
from openhinglish import normalize

result = normalize("bhai kal mera intv h paytm me")
print(result.display)  # भाई कल मेरा interview है Paytm में
print(result.tts)      # भाई कल मेरा इंटरव्यू है पे-टी-एम में
print(result.confidence)  # per-utterance aggregated confidence
```

Each token carries its own `confidence`, up to `k=3` n-best alternatives, and a
`trace` list that records which stage made each decision and why. The output is never a
flat string — it is a `NormalizationResult` with a `tokens` list. You can inspect every
decision.

The pipeline stages, in order:

1. **S0 Preprocess/Tokenize** — whitespace and boundary tokenization, span tracking.
2. **S1 Classify** — language-ID per token, ranked n-best candidates.
3. **S2 SpellNorm** — abbreviation expansion (`intv` → `interview`), conservative
   typo correction.
4. **S3 Translit** — Roman-Hindi to Devanagari via lookup, with akshara fallback;
   English-to-Devanagari TTS forms for known words.
5. **S4 Names/Brands** — gazetteer lookup with casing and context guard (`paytm` →
   `Paytm` display, `पे-टी-एम` TTS).
6. **S5 Numerals/Time/Acronyms** — `4` → `4` display / `चार` TTS; `RBI` → `आर बी आई`
   TTS.
7. **S6 Assemble** — build final `display` and `tts` strings, aggregate confidence.

The architecture has one important design seam: a pluggable `Disambiguator` Protocol.
Right now it is a no-op (`FrequencyDisambiguator`). In V3, a learned context model slots
in here without rewriting any pipeline code. The seam exists now so that V3 is an
addition, not a rewrite.

32 unit tests pass. The 6-row `IndianTTSBench-mini` benchmark passes at 1.000 n-best
coverage.

**What does not exist yet:**

The seed lexicons are tiny. ~13 Roman-Hindi words, 6 SMS abbreviations, 4 names
(`shankar`, `mishra`, `dwivedi`, `aaradhya`), 4 brands (`paytm`, `zomato`, `rapido`,
`zepto`). The bench-mini rows were chosen specifically to match these seeds. If you run
V0.1 on your own Hinglish text, most tokens will fall through to UNKNOWN. Real-world
coverage is near-zero.

The 1.000 bench score does not mean the engine is accurate on real text. It means I
hand-picked 6 sentences that the seed vocabulary covers. That is the honest interpretation
of the number.

The CLI and FastAPI server are scaffolded in the package metadata but not yet implemented.
The PyPI package does not exist yet. All of that is V1 work.

V0.1 is a foundation with a sound architecture and a working pipeline. It is not yet
useful on arbitrary input.

---

## The design bets

A few decisions I made deliberately and want to document while the reasoning is fresh.

**Deterministic and explainable first.** Every normalization decision is traceable to a
specific rule, lexicon entry, or stage. This is slower to build than a neural sequence
model, but it means: (a) a contributor can fix "zomato" pronunciation by editing a TSV
file, not retraining a model; (b) a downstream team can audit why a specific token was
normalized the way it was; (c) the engine works on CPU with no GPU dependency, which
matters for the zero-budget constraint and for embedding in edge devices.

**Two outputs, not one.** `display` and `tts` are not the same. `display` is what you
show a human — mixed script is fine, English words stay as English. `tts` is what you
feed an acoustic model — every token needs a pronounceable native-script form. Collapsing
these into one output string was the most common mistake I saw in ad-hoc implementations.
The data model enforces the distinction from the start.

**N-best + confidence + traces are first-class.** The output type is never a plain string.
It is a `NormalizationResult` with a `tokens` list. Every token has `confidence`,
`alternatives`, and `trace`. This is more verbose to consume, but it means downstream
systems can make informed decisions: use the top-1 form for fast paths, inspect
alternatives for ambiguous cases, surface low-confidence tokens for human review.

**Lexicons are editable TSV files, not code.** The `roman_hindi.tsv`, `names.tsv`,
`brands.tsv`, and `sms_abbrev.tsv` files are plain tab-separated text. Anyone can open
them, add a row, and submit a pull request. No Python knowledge required. This is the
community contribution model: the long tail of names and brands is not something one
person can maintain, but it is something a community can maintain if the barrier is "edit
a TSV file."

**Path A → C.** V1 is fully deterministic. The `Disambiguator` interface exists now so
that V3 can slot in a learned model without a rewrite. Any ML used in the build process
(e.g. IndicXlit for generating translit tables) runs offline at build-time and produces
a static lookup table. Nothing loads a model at inference time.

---

## Why developers should care

If you are building anything in Indian AI that touches user-typed text — a voicebot, an
ASR pipeline, a chatbot, a search index, a translation system — you are going to hit this
normalization problem. Right now, your options are: write your own ad-hoc solution,
pay for a closed API, or use a TTS engine that assumes you will hand it clean native
script (which you probably will not).

OpenHinglish is an attempt to build the shared solution that everyone currently re-invents
badly, and to build it in the open so the Indian developer community can contribute and
own it. That only works if people contribute. The seed lexicons are tiny by design — the
work of growing them is exactly the work I am asking for help with.

---

## How to contribute right now

V0.1 is the right time to contribute data, not code. The pipeline architecture is stable.
What it needs is entries.

**Add lexicon entries:** Open
`src/openhinglish/data/lexicons/roman_hindi.tsv` and add rows in the format:

```
roman_word<TAB>devanagari_form<TAB>frequency_score
```

For example: `yaar<TAB>यार<TAB>7000`

**Add name entries:** Open
`src/openhinglish/data/gazetteers/names.tsv` and add rows:

```
roman_surface<TAB>canonical_display<TAB>devanagari_tts_form
```

**Add brand entries:** Same format in `gazetteers/brands.tsv`. Brand TTS forms are
particularly valuable and particularly hard to get right — "Zepto" pronounced as
"ज़ेप्टो" is not something a generic G2P system produces.

**Add bench sentences:** Open
`src/openhinglish/eval/bench_mini/sentences.tsv` and add rows:

```
input<TAB>expected_display<TAB>expected_tts<TAB>tags
```

Sentences that expose failure modes (ambiguous tokens, uncommon brands, regional names)
are more valuable than sentences the engine already handles.

**Report UNKNOWN tokens:** If you run V0.1 on your own text and get back tokens with
`category=UNKNOWN`, that is useful signal. Open an issue with the token and its correct
normalization.

The project is at: [GitHub — shankarmishra/openhinglish] (link to follow when the repo is
public). License: MIT (code), CC-BY-SA-4.0 (Dakshina-derived data files).

---

## What is next

V1 is the scale-up. The goal is to make the engine genuinely useful on real Hinglish text,
not just on the 6 seed sentences. That means:

- 10 000+ Roman-Hindi lexicon entries from Google Dakshina.
- 5 000+ names from Wikidata.
- 500+ brand forms, curated.
- A 300-row human-verified benchmark replacing bench-mini.
- PyPI publication.
- One public end-to-end demo: OpenHinglish → IndicF5, full paragraph, audible output.

If you have worked with Hinglish normalization before — in any context, any language, any
domain — I would like to hear what broke your ad-hoc solution. That is the data I need
to prioritize the V1 lexicon work.

---

*Shankar Mishra — building in public, zero budget, one sentence at a time.*
