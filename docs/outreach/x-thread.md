# X/Twitter Thread — OpenHinglish

---

## Thread (6–8 tweets)

---

**Tweet 1 — Hook**

Indian voice AI has a quiet problem nobody talks about.

You can build near-human-quality Hindi TTS today with IndicF5 (MIT, free, excellent).

But the moment a user types "bhai kal mera intv h paytm me" — every pipeline silently breaks.

Here's why, and what I'm building to fix it. 🧵

---

**Tweet 2 — The problem**

IndicF5 and every other good Indian TTS engine documents one thing: clean Devanagari input.

Indian users don't type Devanagari. They type Roman-script Hinglish.

"bhai kal mera interview hai" → what users type
"भाई कल मेरा इंटरव्यू है" → what the TTS needs

Every team fills this gap with a regex. It breaks. Gets patched. Breaks again.

---

**Tweet 3 — The specific failure**

I tested a voice pipeline once. Input: `bhai kal mera intv h paytm me`

The TTS got it raw. Output: "bye-ee kal mera int-v aitch pay-tee-em may"

Nobody laughed — it was a real pre-launch product.

Someone fixed it with a hardcoded replacement. Three weeks later a new user query broke it differently.

This cycle is universal in Indian AI teams.

---

**Tweet 4 — The display/tts insight**

The insight that changed how I thought about this: `display` and `tts` are not the same output.

What a human reads on screen: "भाई कल मेरा interview है Paytm में" (English words stay English — that's natural)

What a voice engine should receive: "भाई कल मेरा इंटरव्यू है पे-टी-एम में" (everything pronounceable in script)

Collapsing these into one output is the most common mistake in ad-hoc implementations.

---

**Tweet 5 — What I built**

OpenHinglish: open-source, MIT, CPU-only, deterministic Roman-Hinglish normalization.

```python
from openhinglish import normalize
result = normalize("bhai kal mera intv h paytm me")
result.display  # भाई कल मेरा interview है Paytm में
result.tts      # भाई कल मेरा इंटरव्यू है पे-टी-एम में
```

7-stage pipeline. Every token decision is traceable. No GPU. No API. If a brand is pronounced wrong — edit a TSV file in the repo. Done.

---

**Tweet 6 — Why open-source matters here**

When "Paytm" comes out as "pay-tee-em" in a closed API, you have no lever to fix it.

When it happens in OpenHinglish — you open brands.tsv, add one row, submit a PR.

Community-maintainable is the entire point. Indian brands, names, regional terms — no single person can curate all of it. But a community can.

---

**Tweet 7 — Honest status + the ask**

Honest: this is V0.1. The architecture is solid, 32 tests pass, but the lexicons are tiny — only ~13 seed words.

Real-world coverage is near-zero right now. V1 is the first actually useful release.

The most useful help right now: adding lexicon entries. It's editing a TSV file. No Python knowledge required.

---

**Tweet 8 — Link + CTA**

GitHub: [shankarmishra/openhinglish] (link coming when public)
MIT licensed. CPU-only. No audio generation — this is the normalization layer you plug in *before* your TTS.

If you've dealt with Hinglish normalization before, reply or DM. I want to know what broke your solution. That's the data I need for V1.

Building in public. 🇮🇳

---

## Posting notes

- Post tweets sequentially, not all at once (gives algorithm time to serve each)
- Reply to substantive replies quickly — early engagement drives reach on X
- If tweet 2 or 4 gets picked up, quote-tweet with a link to the GitHub when it goes public
- Do not post the full thread until the GitHub repo is actually public — the broken link will kill trust immediately
