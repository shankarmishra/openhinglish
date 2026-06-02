# OpenHinglish — Master Roadmap

> **Status as of V0.1:** Deterministic pipeline complete, 32 unit tests passing, 6-row
> bench-mini included. Seed lexicons are tiny; real-world coverage on arbitrary Hinglish
> is near-zero. This document is a living plan, not a promise sheet.

---

## Vision

OpenHinglish aims to become the **standard open normalization layer for Roman-script
Hinglish and Indian code-switched text** — the missing plumbing that every Indian AI
product currently re-invents badly. The goal is a single, permissively licensed Python
library that takes informal Roman-Hinglish input and produces structured, deterministic
output: a human-readable `display` form, a TTS-ready `tts` form, per-token confidence,
n-best alternatives, and full explainability traces. Any TTS engine, ASR post-processor,
chatbot, or search backend can consume it without coupling to a specific acoustic model.

In the five-year arc, success is not a better voice model — that problem is largely solved
(IndicF5, Indic-Parler-TTS, CosyVoice2 all cover native-script Indic with permissive
licenses). Success is becoming the normalization standard that those engines and every
downstream Indian AI product depend on, governed by a community rather than one person,
and validated by an open public benchmark.

---

## Problem Statement

Roman-Hinglish — Hindi written in Latin script, code-switched with English, brand names,
abbreviations, and digits — is how hundreds of millions of people actually type. A
WhatsApp message, a voice-bot transcript, a search query, a support ticket: all of it
looks like this:

> `bhai kal mera intv h paytm me`
> `yaar plz 400 rs bhej de abhi SBI account mein`
> `aaj 9 bje meeting h zoom pe okay?`

The chaos is structural, not incidental:

- **Spelling is not standardized.** "kya" / "kia" / "kya" / "kyaa"; "nahi" / "nhi" /
  "nai" / "nahin" — all mean the same thing. No dictionary covers them all.
- **Code-switching is the rule, not the exception.** A single utterance mixes Hindi roots,
  English nouns, and branded product names with no markup.
- **Abbreviations are domain-specific.** "intv" = interview in job contexts; "msg" =
  message; "h" = है (is) in SMS register; "h" = hour in time context. Disambiguation
  requires register awareness.
- **Brand and proper-name surface forms are arbitrary.** "paytm" / "PayTM" / "pay-tm";
  "zomato" / "Zomato" / "ZOMATO". The correct TTS pronunciation of "Paytm" is not
  "pate-em" — it is "पे-टी-एम", which no generic G2P system produces correctly.
- **Numerals and dates are mixed.** "9 bje" = 9 बजे; "400 rs" → "चार सौ रुपये" for TTS.
  Hindi and English number-word conventions differ.

Every one of these failures is load-bearing for downstream systems:

- **TTS** mispronounces or crashes on untokenized brand names and Romanized Hindi.
  IndicF5 and Indic-Parler-TTS require clean Devanagari input — they are not designed to
  accept "bhai kal mera intv h" as-is.
- **ASR** post-processors need to normalize transcripts before storing or displaying them;
  raw hypotheses contain all the above variants simultaneously.
- **Chatbots** need to map "intv" → "interview" and "h" → "है" before intent detection or
  slot-filling; most NLU toolkits have no concept of Roman-Hinglish tokens.
- **Search** needs canonical forms: a search for "paytm" and "PayTM" and "pay-tm" should
  hit the same index entry.
- **Translation** systems (en→hi, hi→en) produce garbage on code-mixed input without
  prior normalization; they expect clean monolingual text.

The existing "solutions" are either native-script-only (and therefore useless on Roman
input), closed APIs, or ad-hoc regex patches that break on anything outside their original
context. There is no open, general-purpose, community-maintained library for this. That
gap is what OpenHinglish fills.

---

## Why OpenHinglish Exists

### The gap is real and unfilled

AI4Bharat's **IndicF5** (MIT, 11 languages, near-human quality), **Indic-Parler-TTS**
(Apache-2.0), and **CosyVoice2-0.5B** (Apache-2.0, ~150 ms latency) have largely solved
the acoustic modeling problem for native-script Indic text. This is genuine progress and
OpenHinglish does not compete with it. These engines take clean Devanagari (or other
native script) and produce excellent speech. What they do not document or handle is
**Roman-script Hinglish code-switch input**. The normalization step — turning `bhai kal
mera intv h paytm me` into clean Devanagari — is left to the integrator.

Every Indian AI product that handles user-typed text re-implements this normalization
layer from scratch: one team writes a regex for "paytm", another hard-codes "h" → "है",
a third builds a names list that never gets shared. The result is:

- Duplicated work across dozens of teams.
- No shared test suite, so regressions go undetected.
- No community contribution path for the long tail of names, brands, and abbreviations.
- Proprietary lock-in for anyone who buys a closed normalization API.

### Why closed tools don't solve it

**ElevenLabs**, **Sarvam Bulbul v2**, and **Cartesia Sonic** are capable closed systems
for Indian-language TTS. They are not an answer for three reasons: (1) they are APIs, not
libraries — you cannot inspect, audit, or correct their normalization decisions; (2) they
carry per-character cost, incompatible with the zero-budget constraint most open projects
operate under; (3) the normalization logic is a black box — when "Paytm" comes out wrong,
you have no lever to fix it.

### Why this must be infra, not another product

Normalization is boring infrastructure. No one wants to maintain it; everyone needs it.
The right model is a shared library — like `chardet`, `phonenumbers`, or `langdetect` —
that a community can maintain and extend via plain TSV data files, without retraining any
model. OpenHinglish is designed to be exactly that: the normalization layer that sits in
front of every Indian AI product, maintained once, used everywhere.

---

## Roadmap V0.1 → V5

Each version has a canonical theme, concrete deliverables, and explicit exit criteria.
Exit criteria define what must be empirically true before the version tag is published.

---

### V0.1 "Foundation" — **DONE**

**Theme:** Prove the architecture; establish the seams.

**Deliverables (all complete):**
- Linear 7-stage deterministic pipeline: S0 Preprocess → S1 Classify → S2 SpellNorm →
  S3 Translit → S4 Names/Brands → S5 Numerals → S6 Assemble.
- `Token`, `NormalizationResult`, `Config`, `Category`, `Candidate` data model.
- Pluggable `Disambiguator` Protocol with `FrequencyDisambiguator` no-op implementation
  (reserves the seam for V3 learned layer without a rewrite).
- Seed lexicons: ~13 Roman-Hindi entries, 6 SMS abbreviations, 4 names, 4 brands, ~8
  English TTS entries.
- `IndianTTSBench-mini`: 6 hand-labeled gold rows covering code-switch, numerals, brands,
  names, acronyms.
- Per-token confidence, n-best alternatives (k=3 default), explainability traces.
- 32 unit tests covering all stages and the public `normalize()` API.
- Installable package (`pip install -e .`); CLI entry point scaffolded.

**Exit criteria (met):**
- All 32 unit tests pass on a clean install.
- `normalize("bhai kal mera intv h paytm me")` returns `display="भाई कल मेरा interview
  है Paytm में"` and `tts="भाई कल मेरा इंटरव्यू है पे-टी-एम में"`.
- Bench-mini reports 1.000 n-best coverage over its 6 rows (trivially true: rows were
  selected to match seed vocab).

**Known limitations at exit:** Real-world coverage on arbitrary Hinglish is near-zero.
The 1.000 bench score is over 6 curated rows, not a capability claim.

---

### V1 "Usable Hindi+English"

**Theme:** Scale the data until the engine is genuinely useful on real Hinglish text.

**Deliverables:**
- Roman-Hindi lexicon: 10 000+ entries, sourced from Google Dakshina (CC-BY-SA-4.0;
  derived data files carry SA license — code remains MIT).
- Names gazetteer: 5 000+ Indian first/last names (Wikidata CC0 + curated).
- Brands gazetteer: 500+ Indian brand surface forms with canonical display and TTS forms.
- Abbreviation/SMS lexicon: 1 000+ entries.
- `IndianTTSBench-v1`: 300+ human-verified sentences (diverse register, spelling
  variants, brand/name density), with multiple acceptable gold outputs per row.
- Published on **PyPI** as `openhinglish`.
- CLI (`openhinglish "..."`) and optional FastAPI server (Task 11).
- `DATA_LICENSES.md` tracking every source with commit hashes.
- Eval tooling that scores n-best coverage and reports display-accuracy vs tts-accuracy
  separately, with human adjudication instructions for ambiguous rows.

**Exit criteria:**
- PyPI package installs cleanly (`pip install openhinglish`) on Python 3.11+.
- n-best coverage ≥ 85% on IndianTTSBench-v1 (300-row set), where "covered" means at
  least one of the top-k alternatives matches an accepted gold output.
- Display-accuracy ≥ 80% @k=1 on the Hindi+Hinglish subset of the bench.
- TTS-accuracy ≥ 75% @k=1 on the same subset.
- Dakshina-derived data files carry CC-BY-SA-4.0 header; no CC-BY-NC data in release.
- At least one public integration demo (e.g. OpenHinglish → IndicF5 pipeline on a sample
  paragraph).

---

### V2 "Multilingual Frontends"

**Theme:** Extend the same pipeline to other Indian code-switch registers.

**Deliverables:**
- Per-language translit/G2P tables and seed lexicons for: Marathi, Punjabi, Gujarati,
  Bengali, Tamil, Telugu. (6 languages; the pipeline architecture is language-agnostic —
  each adds a `lexicons/<lang>/` directory and a language tag in Config.)
- Per-language bench sub-sets (≥ 50 human-verified sentences each) appended to
  IndianTTSBench-v1 → v2.
- Language auto-detection in S1 extended to distinguish the 6 new languages from Hindi.
- Contributor guide for adding a new language without touching pipeline code.
- Community: at least 3 external contributors credited in CHANGELOG.

**Exit criteria:**
- n-best coverage ≥ 70% on each new language's bench sub-set.
- Hindi+English V1 accuracy does not regress (bench-v1 scores within ±2%).
- All 6 language modules ship with non-empty lexicons (≥ 500 entries each).
- Contributor guide tested: one new language added by a contributor who is not the
  original maintainer.

---

### V3 "Context-aware (learned layer, Path C)"

**Theme:** Slot in a learned disambiguator behind the existing `Disambiguator` interface;
no pipeline rewrite.

**Deliverables:**
- A trained `LearnedDisambiguator` implementation of the `Disambiguator` Protocol.
  Resolves structurally ambiguous tokens: "kal" (yesterday/tomorrow), "main" (I/main),
  "to" (Hindi particle / English "to"), "h" (है / hour), etc.
- Named-entity recognition for names not in the gazetteer (lightweight sequence model or
  rule-based heuristics with learned scoring).
- Punctuation and capitalization restoration (deferred from V1).
- Hybrid confidence scoring that combines deterministic rule confidence with learned
  posterior.
- All learned models: **CPU-only**, packaged as static weights, no GPU at inference.
  IndicXlit (or equivalent) used **offline at build-time** to pre-compute lookup tables —
  never loaded at inference.
- Updated bench-v3 including adversarial ambiguity cases.

**Exit criteria:**
- Ambiguity resolution accuracy ≥ 80% on a held-out set of 100 structurally ambiguous
  sentences.
- Pipeline with `LearnedDisambiguator` runs in ≤ 50 ms p95 on a modern CPU (no GPU).
- Deterministic fallback remains: users can instantiate `FrequencyDisambiguator` and get
  V1-equivalent behavior.
- No CC-BY-NC weights in the release; all model licenses documented in
  `DATA_LICENSES.md`.

---

### V4 "Ecosystem and Integrations"

**Theme:** Make OpenHinglish trivially consumable across the Indian AI stack.

**Deliverables:**
- **TTS adapters**: pre-built connector modules for IndicF5 (MIT) and CosyVoice2
  (Apache-2.0) that feed OpenHinglish `tts` output directly to the acoustic model.
- **ASR post-processing adapter**: takes raw ASR hypothesis text and normalizes before
  display/storage.
- **Chatbot/search integrations**: reference integration for a popular chatbot framework
  and a search indexing pipeline.
- **Hosted API**: zero-cost hosted demo endpoint (free tier, rate-limited; not a
  production SLA).
- **JS/WASM port**: compile the deterministic pipeline (no learned weights) to WebAssembly
  for browser and Node.js use.
- **Plugins**: documented plugin protocol for third-party stages.

**Exit criteria:**
- IndicF5 + OpenHinglish end-to-end demo reproduces the bench-v1 sentence set as audible
  audio with no mispronunciations on ≥ 80% of tokens (human-evaluated sample).
- JS/WASM build passes a subset of the bench in a Node.js test runner.
- ≥ 5 external integrations documented in the ecosystem page (community or official).
- PyPI download count ≥ 1 000/month (trailing 90 days).

---

### V5 "The Standard"

**Theme:** Governance maturity and community ownership; OpenHinglish as public
infrastructure, not a solo project.

**Deliverables:**
- **IndianTTSBench public leaderboard**: a hosted, reproducible benchmark where any
  normalization engine can submit results. Defines the evaluation standard for the field.
- **Governance**: at least 2 active maintainers beyond the original author; a written
  governance document; a code-of-conduct; a roadmap process open to community input.
- **Foundation consideration**: evaluated (not necessarily pursued) as a candidate for
  an open-source foundation (e.g. NumFOCUS-affiliated, PSF fiscal sponsor, or equivalent
  Indian entity).
- **Broad adoption**: documented use in ≥ 10 distinct Indian AI products or research
  projects.
- Language coverage: ≥ 8 Indian languages with maintained lexicons.

**Exit criteria:**
- IndianTTSBench leaderboard has ≥ 3 external engine submissions.
- Bus-factor ≥ 2: two maintainers each capable of cutting a release independently.
- GitHub stars ≥ 500 (lagging indicator, not a gate; included as a proxy for awareness).
- No single-point-of-failure data source: all critical lexicons have ≥ 2 independent
  contributors.

---

## Success Metrics

Metrics evolve per version. Numbers below are **targets and hypotheses** — not
commitments. They exist to force early falsification, not to impress anyone.

| Metric | V0.1 | V1 | V2 | V3 | V4 | V5 |
|---|---|---|---|---|---|---|
| Lexicon entries (Roman-Hindi) | ~13 | 10 000+ | 10 000+ (stable) | same | same | same |
| Names gazetteer entries | 4 | 5 000+ | 5 000+ | same + NER | same | same |
| Brands gazetteer entries | 4 | 500+ | 500+ | same | same | same |
| Bench size (gold rows) | 6 | 300+ | 300+ + 6×50 per lang | 300+ + adversarial | same | public leaderboard |
| n-best coverage @k=3 (Hindi+Hinglish bench) | 1.000 (6 rows) | ≥ 85% | ≥ 85% Hindi; ≥ 70% new langs | ≥ 90% Hindi | same | same |
| Display-accuracy @k=1 | unmeasured | ≥ 80% | ≥ 80% Hindi | ≥ 85% | same | public |
| TTS-accuracy @k=1 | unmeasured | ≥ 75% | ≥ 75% Hindi | ≥ 82% | same | public |
| Ambiguity resolution accuracy | N/A | N/A | N/A | ≥ 80% | same | same |
| CPU latency p95 (per utterance) | unmeasured | ≤ 20 ms | ≤ 25 ms | ≤ 50 ms | ≤ 50 ms (WASM: ≤ 100 ms) | same |
| PyPI downloads / month | 0 | first publish | ≥ 200 | ≥ 500 | ≥ 1 000 | ≥ 5 000 |
| GitHub stars | 0 | ≥ 20 | ≥ 75 | ≥ 150 | ≥ 300 | ≥ 500 |
| External integrations documented | 0 | 1 (demo) | 2 | 3 | ≥ 5 | ≥ 10 |
| Languages covered | 2 (Hindi+En) | 2 | 8 | 8 | 8 | ≥ 8 |
| Active contributors | 1 | 1 | ≥ 3 | ≥ 5 | ≥ 8 | bus-factor ≥ 2 |
| Bus-factor | 1 | 1 | 1–2 | 2 | 2 | ≥ 2 |

**How to read this table:** V0.1 numbers are actual. V1+ numbers are targets set today
with current knowledge; they will be revised as evidence accumulates. A missed target is
a signal to adjust, not a failure to hide.

---

## Challenged Assumptions / Risks / Open Questions

These are genuine open questions, not disclaimers. Each one could materially change the
direction.

### 1. Skeleton is not a product

V0.1 coverage on arbitrary Hinglish text is near-zero. The 7-stage pipeline is
architecturally sound and all tests pass, but "tests pass" means "the 6 seed bench rows
work." If someone installs V0.1 and tries it on their actual chatbot transcripts, most
tokens will fall through to UNKNOWN. The real work begins in V1.

### 2. Bus-factor = 1 is the existential risk

This is a 5-year infrastructure project with one maintainer who has no budget and a
full-time job. The most likely failure mode is not a bad architecture decision — it is
that the maintainer's available hours drop to zero. Every design decision (editable TSV
data, no training requirement, pure-function pipeline stages) is made with "a stranger
should be able to take this over" in mind. But architecture alone does not solve bus-factor.
The V2 exit criterion of at least 3 external contributors is the first real gate.

### 3. Demand is unproven

It is possible that the actual pain is not "normalization is hard" but "we already have
an ad-hoc solution that is good enough." We need evidence that developers would adopt an
open library rather than maintain their own regex. The V1 integration demo and PyPI
download numbers are the first demand signals. If downloads stay near zero after six
months of availability, the assumption of unmet demand must be revisited.

### 4. No ground truth for Hinglish — eval is genuinely hard

Hinglish normalization does not have a single correct answer. "kal" is correctly
transliterated as both "कल" (yesterday) and "कल" (tomorrow) — phonetically identical,
semantically opposite — and both are correct depending on context. The bench design must
encode multiple acceptable outputs per row, and the accuracy metrics must use n-best
coverage rather than exact-match. The 300-row V1 bench requires human adjudication, not
automated labeling. This is expensive and slow for a zero-budget project.

### 5. License / provenance can sink the project

Dakshina (CC-BY-SA-4.0) is the most important data source for V1 scale-up. CC-BY-SA is
**share-alike**: any data file derived from Dakshina must carry the SA license, even if
the code is MIT. This is manageable with clean separation (code MIT, data files carry
their source license), but it requires discipline. One accidental merge of CC-BY-NC
material (e.g. Spark-TTS weights, XTTS-v2, F5-TTS weights) into any distributed file
would force a license change that breaks the "permissive infra" value proposition. The
`DATA_LICENSES.md` file and pinned commit hashes are non-negotiable from V1 onward.
HiACC (2025 Hinglish code-switch dataset) has **unverified license** as of this writing
— do not use it until confirmed.

### 6. The V3 learned layer may not fit the CPU-only constraint

If the most effective disambiguator requires a transformer inference call per sentence,
the ≤ 50 ms p95 CPU latency target becomes implausible at V3 scale. The architecture
reserves the `Disambiguator` Protocol seam exactly for this scenario — the fallback is
always the deterministic V1 behavior — but the V3 promise of "context-aware and still
CPU-friendly" is a hypothesis, not a guarantee. It may resolve to a smaller model (e.g.
a CRF or a distilled bi-LSTM) or to a documented trade-off.

### 7. V5 governance may never materialize

Community governance assumes the project attracts enough sustained interest to support
multiple maintainers. Most open-source infra projects of this kind never reach bus-factor
≥ 2. V5 is a vision, not a plan with concrete dependencies. The honest framing is: if the
project reaches V3 with real adoption, governance becomes tractable. If it does not, V5
stays a sketch.
