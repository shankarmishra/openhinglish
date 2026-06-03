# Dev.to / Hashnode Article Draft

**Title:** Why Hinglish breaks Indian AI (and an open-source fix I'm building)

**Tags:** nlp, opensource, india, machinelearning, python

---

## Why Hinglish breaks Indian AI (and an open-source fix I'm building)

I was testing a voice pipeline for an Indian product a few months ago. The input was a WhatsApp-style message:

> `bhai kal mera intv h paytm me`

The TTS engine received that string more or less as-is, because no one had written normalization code yet. What came out of the speakers was roughly: "bye-ee kal mera int-v aitch pay-tee-em may."

Nobody laughed. This was a real product in pre-launch testing.

Someone patched it with a regex. Someone else added a few hardcoded replacements. Three weeks later a new set of user queries broke it in a different way. I watched this cycle happen twice before I asked the obvious question: **why does a shared solution for this not exist as a library?**

That question is the reason I started building OpenHinglish.

---

## The actual problem: three layers, not one

Hinglish text normalization is not one problem. It's three problems stacked on top of each other, and most ad-hoc solutions address only the most visible one.

### 1. Romanization is not standardized

Hindi written in Roman script has no single convention. The same word can appear as: `yaar`, `yar`, `yaar`, `yar`. `paytm` or `PayTM`. `abhi` or `abhi` or `ab hi`. Every user spells differently, every chat platform has its own patterns, and there is no "correct" Roman Hindi orthography — it is entirely phonetic and personal.

This means you cannot write a simple lookup table that maps `yaar → यार` and call it done. You need fuzzy matching, frequency priors, and contextual disambiguation to handle the real distribution.

### 2. Code-switching is structural, not accidental

Indian users do not "switch" between Hindi and English randomly. Code-switching in Indian English-Hindi has documented structural patterns: function words (conjunctions, postpositions) tend to stay Hindi, content words (especially technical/brand terms) tend to stay English. "bhai mera UPI kaam nahi kar raha" is not a mistake — it is grammatically consistent code-switched speech.

A normalization system that forces everything to Devanagari will over-correct. `interview` in the middle of a Hindi sentence does not need to be transliterated to `इंटरव्यू` in the display form — that would look strange to a reader. But the TTS engine needs `इंटरव्यू` (or some pronounceable form) because it does not know how to handle an English word in a Hindi audio stream.

This is why `display` and `tts` are not the same output. More on this below.

### 3. Names and brands are a special category

Indian brand and product names are systematically mis-pronounced by generic text-to-speech systems. "Paytm" pronounced phonetically by an English G2P system becomes "pay-tee-em." "Zomato" might come out as "zo-mah-to" or "zo-may-to" depending on which letter rules fire. "Rapido" is close enough in English that some systems get it by accident.

The correct Hindi pronunciations — "पे-टी-एम", "ज़ोमैटो", "रैपिडो" — are not derivable by any rule-based system without a lookup table. They are vocabulary items that someone has to curate. No model trained on English text will produce them correctly. No model trained on standard Hindi text will have them either, because they are not standard Hindi.

This is the part that requires a community-maintained gazetteer. It cannot be solved with a generic approach.

---

## Why existing tools don't cover this

The honest competitive landscape:

**IndicF5, CosyVoice2, Indic-Parler-TTS** — excellent acoustic models, MIT/Apache licensed. They all document Devanagari input. None of them document what to do with Roman-script input. They solve the acoustic problem, not the normalization problem.

**IndicXlit** — romanization-to-Devanagari transliteration from AI4Bharat. Good at the core transliteration task. Does not handle abbreviations, does not have brand/name gazetteers, produces one output form (not a `display` / `tts` split), and runs a model at inference time (adds latency, non-deterministic).

**ElevenLabs, Sarvam Bulbul** — capable closed systems. When "Paytm" comes out wrong, you have no lever to fix it. No inspection, no community-fixable layer, per-call cost.

**Ad-hoc regex** — what everyone actually uses. It does not generalize. It has no confidence or ambiguity handling. It is not community-maintainable. Every team writes it and throws it away on the next project.

The gap is not about acoustic quality. The acoustic quality problem is largely solved. The gap is in the normalization layer every team re-implements badly before they even get to the TTS engine.

---

## How OpenHinglish approaches it

OpenHinglish is a deterministic, 7-stage Python pipeline. No GPU, no runtime model loading, no API calls. MIT licensed. Every decision is traceable.

### The two-output design

```python
from openhinglish import normalize

result = normalize("bhai kal mera intv h paytm me")
print(result.display)
# भाई कल मेरा interview है Paytm में

print(result.tts)
# भाई कल मेरा इंटरव्यू है पे-टी-एम में

print(result.confidence)
# per-utterance aggregated confidence score
```

`display` is what you render for a human reader. English words stay as English where they naturally appear in Hinglish — forcing `interview` to `इंटरव्यू` in a user-facing chat message would look odd. Brand casing is normalized (`paytm` → `Paytm`).

`tts` is what you pass to an acoustic model. Every token needs to be in a form the model can pronounce — which means Devanagari for Hindi words, and a syllabified Devanagari form for brands and acronyms (`पे-टी-एम`, not `Paytm`).

Collapsing these into a single output is the most common mistake in ad-hoc implementations. The two-output design is enforced in the data model from the start.

### The 7-stage pipeline

**S0: Preprocess / Tokenize**
Whitespace and boundary tokenization. Span tracking so you can map output tokens back to positions in the original string. Simple, but critical for the trace system downstream.

**S1: Language Classify**
Per-token language identification with ranked n-best candidates. Is `"ready"` an English word in a Hinglish sentence, or is it a romanized Hindi word? The classifier returns probabilities, not a hard binary label, and the downstream stages use those probabilities to guide their decisions.

**S2: SpellNorm / Abbreviation Expand**
Conservative abbreviation expansion (`intv` → `interview`, `kl` → `कल`, `h` → `है`) and typo correction. "Conservative" matters — aggressive correction will mangle deliberate informal spellings. The abbreviation lexicon is a TSV file; anyone can add entries.

**S3: Transliterate**
Roman-Hindi words to Devanagari via lookup, with a letter-by-letter akshara fallback for words not in the lexicon. Also produces English-to-Devanagari TTS forms for known English words that appear in Hinglish context.

**S4: Names and Brands**
Gazetteer lookup with casing and context guard. `paytm` → `Paytm` for display, `पे-टी-एम` for TTS. `zomato` → `Zomato` display, `ज़ोमैटो` TTS. This is the stage that requires community-curated data — no rule-based system produces these pronunciations correctly without a lookup.

**S5: Numerals / Time / Acronyms**
`4` → `4` display / `चार` TTS. `RBI` → `आर बी आई` TTS. Time patterns, common units, and financial acronyms common in Indian informal text.

**S6: Assemble**
Build the final `display` and `tts` strings, aggregate confidence from per-token scores.

### What the output looks like

```python
result = normalize("UPI se payment karo")

for token in result.tokens:
    print(f"{token.surface:<12} conf={token.confidence:.2f}  tts={token.tts_form}")

# UPI          conf=0.91  tts=यूपीआई
# se           conf=0.99  tts=से
# payment      conf=0.87  tts=पेमेंट
# karo         conf=0.95  tts=करो
```

Every token has `confidence`, `alternatives` (up to k=3 n-best), and `trace` (which stage made the decision and why). This is more verbose to consume than a flat string, but it means downstream systems can make informed choices — use the top-1 form for fast paths, inspect alternatives for ambiguous tokens, surface low-confidence tokens for human review.

### Pluggable disambiguator

There is a `Disambiguator` Protocol in the architecture. Right now it uses a frequency-based no-op. In V3, a learned context model can slot into this interface without rewriting any pipeline code. The seam exists now so that adding learned context later is an addition, not a rewrite.

---

## Honest limitations

I want to be direct about what V0.1 is and is not.

**What it is:** A sound architecture with a working pipeline, 32 passing unit tests, and a clear design for community extension.

**What it is not:** Production-ready for arbitrary Hinglish input.

The seed lexicons are tiny — approximately 13 Roman-Hindi words, 6 SMS abbreviations, and a handful of names and brands. If you run V0.1 on your own text, most tokens will fall through to UNKNOWN. The evaluation benchmark (IndianTTSBench-mini) covers 6 hand-picked sentences that match the seed vocabulary — that 1.000 n-best score on those 6 rows does not mean the engine is accurate on real text. It means the 6 sentences were chosen specifically to match the seeds.

V1 is the first usable release. It requires scaling the lexicons to 10,000+ Roman-Hindi entries (via Google Dakshina data), 5,000+ names from Wikidata, 500+ curated brand forms, and a 300-row human-verified benchmark.

Real-world coverage is near-zero until V1. I am not claiming otherwise.

---

## How to contribute

The most useful work right now is adding lexicon entries. It requires no Python knowledge — just editing a TSV file on GitHub.

**Roman-Hindi words** (`src/openhinglish/data/lexicons/roman_hindi.tsv`):
```
roman_word<TAB>devanagari_form<TAB>frequency_score
yaar<TAB>यार<TAB>7000
```

**Brand TTS forms** (`src/openhinglish/data/gazetteers/brands.tsv`):
```
roman_surface<TAB>canonical_display<TAB>devanagari_tts_form
swiggy<TAB>Swiggy<TAB>स्विगी
```

**Benchmark sentences** that expose failure modes are especially valuable — sentences with uncommon brands, regional names, or ambiguous tokens that the engine currently gets wrong. Those are more useful than sentences it already handles.

If you run V0.1 on your own text and get back tokens with `category=UNKNOWN`, that's useful signal. Open a GitHub issue with the token and its correct normalization. That's directly actionable for V1.

---

## Where this goes next

V1 is about real coverage on real Hinglish text. The milestone that makes it genuinely useful is: install it, run it on a paragraph of WhatsApp-style Hinglish, get back clean Devanagari for a TTS pipeline, with most tokens normalized correctly rather than falling through to UNKNOWN.

After V1: a demo pipeline showing OpenHinglish → IndicF5 end-to-end, a PyPI package, and a Hugging Face Space for live testing. The benchmark grows to 300+ human-verified sentences and becomes the reference eval for Hinglish text normalization.

The longer-term bet: if Indian AI teams stop each re-implementing this normalization layer badly, and instead contribute to and use one shared community-maintained library — the Indian voice AI stack improves for everyone. That only happens if the library is actually useful and the contribution bar is genuinely low.

---

**GitHub:** [shankarmishra/openhinglish] (link when public)
**License:** MIT (code), CC-BY-SA-4.0 (Dakshina-derived data files)

If you've worked on Hinglish normalization, G2P for Indic scripts, or code-switch processing — I'd genuinely like to hear from you in the comments. What broke your ad-hoc solution? That's the question that drives V1 priorities.
