# LinkedIn Post — OpenHinglish

---

## Post

I was testing a voice pipeline for an Indian product. The input message was: **"bhai kal mera intv h paytm me"**

The TTS engine received it almost as-is. What came out of the speakers was: "bye-ee kal mera int-v aitch pay-tee-em may."

Nobody laughed. This was a real pre-launch product. Someone patched it with a regex. Three weeks later a different set of queries broke it again in a new way.

I watched this happen twice before I asked: **why does a shared solution for this not exist?**

---

Here's the actual gap. Indian TTS engines — IndicF5, CosyVoice2, Indic-Parler-TTS — are genuinely excellent. Near-human quality Hindi audio if you hand them clean Devanagari. But Indian users type in Roman script. Code-switched Hinglish like "bhai kal milte h, rn busy hoon" is not something these models were designed to receive raw.

Every Indian AI team that hits this problem solves it the same way: a regex, some hardcoded replacements, a patch. It works for the specific sentences they tested. Then new user inputs arrive and the cycle repeats.

---

So I started building **OpenHinglish** — an open-source, MIT-licensed, CPU-only Python library for Roman-Hinglish text normalization.

One function call:

```python
from openhinglish import normalize
result = normalize("bhai kal mera intv h paytm me")
# result.display → भाई कल मेरा interview है Paytm में
# result.tts     → भाई कल मेरा इंटरव्यू है पे-टी-एम में
```

Two outputs because `display` (what a human reads) and `tts` (what an acoustic model should receive) are genuinely different. Brand acronyms are the clearest case — "Paytm" stays spelled out for a user to read, but needs to be "पे-टी-एम" for a TTS engine to pronounce it right.

The pipeline is deterministic — every decision is traceable. No GPU needed, no API, no runtime ML model. If "Zomato" is being pronounced wrong, you fix it by editing a TSV file in the repo and submitting a PR.

---

**Honest status:** This is V0.1. The architecture is built, 32 unit tests pass, but the lexicons are still tiny — only a handful of seed words. Real-world coverage on arbitrary text is limited right now. V1 is the first genuinely useful release, which requires scaling the word lists to ~10,000+ entries via open data and community contributions.

The most useful thing right now: if you've ever dealt with Hinglish normalization in a real project — any approach, any language — I'd genuinely like to know what broke your ad-hoc solution.

GitHub: [shankarmishra/openhinglish] (link coming)

Building in public, zero budget, one sentence at a time.

---

#OpenSource #IndianAI #NLP #HinglishAI #TextToSpeech #BuildingInPublic #IndiaML #NaturalLanguageProcessing #VoiceAI #MachineLearning
