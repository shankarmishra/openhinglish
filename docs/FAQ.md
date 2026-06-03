# OpenHinglish — Frequently Asked Questions

Common questions about converting Roman-script Hinglish (Hindi typed in English letters) into clean Devanagari for text-to-speech and other Indian-language NLP pipelines.

---

## What is OpenHinglish?

OpenHinglish is a free, open-source (MIT-licensed) Python library that normalizes **Roman-script Hinglish** — Hindi written in the Latin alphabet, code-switched with English, brand names, abbreviations, and digits — into clean **Devanagari** text. It is deterministic (no machine-learning model at runtime), CPU-only, and requires no GPU, no API key, and no network access.

## What problem does it solve?

Indian users type in Roman script (`bhai kal mera intv h paytm me`), but Indian text-to-speech (TTS) engines like AI4Bharat IndicF5, Indic-Parler-TTS, and CosyVoice2 expect clean Devanagari input. The missing piece is the normalization layer between them. Most teams re-implement it with ad-hoc regexes that break on new inputs. OpenHinglish is that layer, built as a shared, community-maintainable library.

## How do I convert romanized Hindi to Devanagari in Python?

```python
from openhinglish import normalize

result = normalize("bhai kal mera intv h paytm me")
print(result.display)  # भाई कल मेरा interview है Paytm में
print(result.tts)      # भाई कल मेरा इंटरव्यू है पे-टी-एम में
```

`display` keeps recognized English words and brand names in Roman script for readability; `tts` converts everything to Devanagari for a speech engine.

## Why are there two outputs (`display` and `tts`)?

Because what a human reads and what an acoustic model should receive are genuinely different. A reader recognizes "interview" and "Paytm" faster in Roman script, but a TTS engine needs `इंटरव्यू` and `पे-टी-एम` to pronounce them correctly. Forcing a single normalized form would compromise one of the two use cases.

## Is OpenHinglish production-ready?

Not yet. It is **early-functional (alpha)**: 51 unit tests pass, the lexicons hold ~1,400+ entries, and the honest 43-sentence benchmark scores **0.93 display exact-match / 0.88 on the stricter TTS channel**. That benchmark is single-author and not multi-annotator validated, so treat it as an early signal, not a production guarantee. Multi-word addresses and code-switch boundaries are the known weak spots. It works well for vocabulary it knows and marks everything else as `UNKNOWN` so nothing fails silently.

## Does it use an LLM or any AI model?

No. The core pipeline is fully deterministic and rule + lexicon based — no large language model, no neural network at runtime, no API calls. This makes it auditable, reproducible, fast, and runnable on any laptop, CI runner, or edge device. (An optional, experimental adapter can feed the output into a separate TTS model, but that model is never part of the core library.)

## How is it different from a neural transliterator like IndicXlit?

OpenHinglish is deterministic and explainable: every token carries a `trace[]` showing which pipeline stage made each decision, plus n-best alternatives with confidence scores. If a word is wrong, you fix it by editing one line in a TSV file and opening a PR — no model retraining. A neural transliterator is a black box you cannot directly correct.

## Does it generate audio?

No. OpenHinglish produces **text only**. Feed its `tts` Devanagari string into any Devanagari-input TTS engine (IndicF5, Indic-Parler-TTS, CosyVoice2) to get speech.

## Which languages are supported?

Hindi + English (Hinglish) today. Marathi and Punjabi seed lexicons exist in the codebase as a scaffold but are not yet wired into the engine. More Indian languages are on the V2 roadmap.

## How can I contribute?

The single most useful contribution is **adding lexicon entries** — it requires no Python knowledge, just editing a plain TSV file. Add an Indian brand, a personal name, or an informal Roman-Hindi word with its correct Devanagari form, and open a PR. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## What license is it under?

The **code** is MIT — free for commercial use. Some **data files** carry their source license (e.g. Dakshina-derived entries are CC-BY-SA-4.0). See [DATA_LICENSES.md](../DATA_LICENSES.md) before commercial use.

## Where do I report a wrong pronunciation or a missing word?

Open an issue using the "lexicon contribution" template, or submit a PR editing the relevant TSV in `src/openhinglish/data/`. Wrong pronunciations are exactly the kind of report that improves coverage fastest.
