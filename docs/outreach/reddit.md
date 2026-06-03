# Reddit Posts — OpenHinglish

---

## r/developersIndia

**Title:** I got tired of every Indian voice/chatbot team writing the same broken Hinglish regex, so I started building a library to replace it

---

Context: I was testing a voicebot pipeline last year. Input was a WhatsApp-style message — `bhai kal mera intv h paytm me`. Nobody had written normalization code yet. The TTS engine got that string almost as-is. What came out of the speakers was "bye-ee kal mera int-v aitch pay-tee-em may." Someone patched it with a regex. Three weeks later a different set of queries broke it again. I watched this cycle twice.

The acoustic modeling problem for Indian languages is mostly solved — IndicF5 (MIT, 11 languages, near-human quality), CosyVoice2, Indic-Parler-TTS are genuinely good. They all document Devanagari input. None of them document what to do when your users type in Roman script, which is what Indian users actually do.

So I built **OpenHinglish** — a deterministic, 7-stage Python normalization pipeline that converts Roman Hinglish into two outputs:

- `display`: mixed-script, human-readable (`भाई कल मेरा interview है Paytm में`)
- `tts`: fully Devanagari, ready to pass to IndicF5 (`भाई कल मेरा इंटरव्यू है पे-टी-एम में`)

Each token carries confidence, n-best alternatives, and a full trace of which stage made the decision. No runtime ML, no GPU needed, MIT licensed. If "paytm" comes out wrong in your integration, you fix it by editing a TSV file in the repo.

**Honest caveat:** V0.1. Seed lexicons are tiny. Real-world coverage on arbitrary text is near-zero right now. V1 is the first genuinely useful release. The architecture is built; what it needs is lexicon entries, which is where I'm asking for help.

Specifically: if you've ever dealt with Roman Hinglish normalization — in any project, at any scale — I'd like to know what broke your solution. That's the data I need to prioritize V1 work.

GitHub: [shankarmishra/openhinglish] (link when public)

---

## r/india

**Title:** Indian apps mispronounce "Paytm" as "pay-tee-em" and "UPI" like it's English — this is why, and a small fix I'm building

---

Have you ever used a voice assistant or IVR in an Indian app where the Hindi-English pronunciation sounds completely off? Like it reads "Paytm" as "pay-tee-em" instead of "पे-टी-एम", or takes an abbreviation like "intv" (interview) literally?

This happens because most Indian AI voice products are built on top of excellent Hindi text-to-speech engines — but those engines were designed for clean Hindi script input. When you type a WhatsApp-style message like `bhai kal mera intv h paytm me`, the app often just passes that Roman text to the engine and hopes for the best. It doesn't.

The actual Hindi you're typing is perfectly normal code-switched Hinglish that every Indian person understands instantly. The TTS engine just doesn't have the preprocessing layer to convert it into something it can pronounce correctly.

I've started building that preprocessing layer as an open-source Python library called **OpenHinglish**. You give it your Roman Hinglish text, it gives you back clean Devanagari — one version for displaying on screen (`interview` stays as English in the displayed text), one version for feeding to the voice engine (`इंटरव्यू` fully in script so it's pronounced right).

It's very early — V0.1, the base architecture is built but the word lists are still small. The most useful help right now is people reporting words and brands that are missing or pronounced wrong. If you've ever cringed at how an Indian app pronounced a word, that's the kind of thing this project is trying to fix.

GitHub: [shankarmishra/openhinglish] (link when public) — MIT licensed, CPU-only, no app or subscription.

---

## r/MachineLearning

**Title:** OpenHinglish: a deterministic Roman-Hinglish text normalization pipeline for pre-processing Indian TTS input [V0.1, early, seeking feedback]

---

**Problem:** Code-switched Roman-script Hinglish (e.g., `"aaj mera interview hai, main ready hoon"`, `"bhai kl aaunga rn busy hoon"`) is the dominant user-input modality for Indian voice and chat products. Native-script Indic TTS models — IndicF5 (MIT, 11 languages), CosyVoice2-0.5B (Apache-2.0), Indic-Parler-TTS — expect Devanagari input. The normalization layer between them is universally re-implemented ad-hoc, project-by-project, with no shared tooling and no community-maintained solution.

**What I built:** A deterministic 7-stage normalization pipeline:

```
S0 Tokenize → S1 Language-classify → S2 SpellNorm/AbbrevExpand → S3 Translit →
S4 Names/Brands gazetteer → S5 Numerals/Acronyms → S6 Assemble
```

Two output forms per input:
- `display`: human-readable mixed-script (English words stay Roman where appropriate)
- `tts`: fully native-script, every token pronounceable by an acoustic model

Each token carries `confidence`, up to `k=3` n-best alternatives, and a `trace` list (which stage, which rule). Output is a `NormalizationResult` struct, not a flat string. A pluggable `Disambiguator` Protocol allows a learned context model to slot in at V3 without rewriting the pipeline.

**Design choices worth discussing:**
- Fully deterministic and explainable at V1. The Disambiguator seam is there for V3 learned context models, but runtime inference is deliberately deferred — this keeps it CPU-only, auditable, and edge-deployable. Interested in whether this tradeoff is defensible for production IVR use cases.
- `display` vs `tts` split: treating these as different output targets from the start, rather than one normalized form. The design assumption is that what a human reads and what an acoustic model should receive are genuinely different (brand acronyms being the clearest case). Feedback on this API surface welcome.
- Lexicons as TSV files, not embedded embeddings. The community contribution model is "edit a TSV, submit a PR." This limits coverage early but makes the data flywheel accessible to non-ML contributors.

**Honest status:** V0.1. Seed lexicons are approximately 13 Roman-Hindi words, 6 SMS abbreviations, 8 names and brands. The eval set (IndianTTSBench-mini) is 6 hand-picked sentences that match the seed vocabulary — 1.000 n-best coverage on those 6 rows, which is not meaningful on arbitrary input. Real-world coverage is near-zero. V1 will scale to ~10k lexicon entries via Google Dakshina + community.

No audio generation — this is purely the text normalization layer. The demo pipeline is: OpenHinglish → IndicF5 → audio.

If you've worked on code-switch normalization, G2P for Indic scripts, or Roman-Hindi romanization, I'm interested in what gaps you see in the pipeline design at this stage.

GitHub: [shankarmishra/openhinglish] (link when public) | MIT (code) | CC-BY-SA-4.0 (Dakshina-derived lexicon data)
