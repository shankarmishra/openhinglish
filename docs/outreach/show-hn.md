# Show HN: OpenHinglish – an open Roman-Hinglish text normalization engine

**Title:** Show HN: OpenHinglish – open-source Roman-Hinglish text normalization for Indian TTS pipelines

---

## Post body

I've been building voice pipelines for Indian products and kept running into the same unglamorous problem: Indian TTS engines (IndicF5, CosyVoice2, Indic-Parler-TTS) expect clean Devanagari input. Indian users type in Roman script. The gap between them is always filled with a team's custom regex that breaks two weeks later.

OpenHinglish is my attempt to build that normalization layer as a proper library: deterministic, 7-stage pipeline, CPU-only, no runtime ML, MIT licensed. It takes a string like `"bhai kal mera intv h paytm me"` and returns two structured outputs:

```python
from openhinglish import normalize

result = normalize("bhai kal mera intv h paytm me")
print(result.display)  # भाई कल मेरा interview है Paytm में
print(result.tts)      # भाई कल मेरा इंटरव्यू है पे-टी-एम में
```

The `display` form is for showing humans (mixed script is intentional — English words stay English). The `tts` form is for feeding to an acoustic model — every token has a pronounceable Devanagari form, brands get their syllabified pronunciation, abbreviations are expanded. Each token carries confidence, n-best alternatives, and a trace of which pipeline stage made each decision, so nothing is a black box.

**Honest status:** This is V0.1 — the architecture is built and 32 unit tests pass, but the seed lexicons are tiny (~13 Roman-Hindi words, 6 abbreviations, ~8 names and brands). If you run it on arbitrary Hinglish, most tokens will fall through to UNKNOWN. Real-world coverage is near-zero. I am not claiming this is production-ready. V1 is the first usable release — the goal is to scale the lexicons to 10,000+ entries via a combination of Google Dakshina data and community contributions. The most useful thing anyone can do right now is add lexicon entries (it's editing a TSV file, no Python required).

**Demo:** [GitHub — shankarmishra/openhinglish] (link when public)

Interested in any feedback on: (1) whether the display/tts split is the right API boundary, (2) whether you've solved this problem yourself and what your approach looked like, (3) whether the 7-stage pipeline design has obvious gaps I haven't seen yet.
