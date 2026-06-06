# OpenHinglish — Ecosystem Strategy

> **Status: V0.1 Foundation. Real-world coverage is near-zero. Everything in this document describes a path, not an achievement.**
> Senior-honest tone throughout. Claims marked UNPROVEN are unproven.

---

## Table of Contents

1. [Positioning](#1-positioning)
2. [The Wedge](#2-the-wedge)
3. [Target Adopters](#3-target-adopters)
4. [Adoption Strategy](#4-adoption-strategy)
5. [Community Strategy](#5-community-strategy)
6. [Developer Outreach Plan](#6-developer-outreach-plan)
7. [Moats](#7-moats)
8. [Challenged Assumptions / Risks](#8-challenged-assumptions--risks)

---

## 1. Positioning

### What OpenHinglish is

**The standard Roman-Hinglish normalization layer for Indian AI.**

Specifically: a deterministic, explainable, CPU-only Python library that converts informal Roman-script Hinglish (code-switched Hindi-English) into structured Devanagari output with separate `display_form` and `tts_form`, per-token confidence, n-best alternatives, and full decision traces.

It is **infrastructure**. It sits between raw user text and downstream consumers — TTS engines, ASR post-processors, chatbots, search indexes, translation inputs. It does one thing, does it transparently, and does it without a GPU.

### What OpenHinglish is NOT

| Not this | Why it matters |
|---|---|
| Not a TTS engine | Does not produce audio; does not compete with IndicF5, CosyVoice2, or ElevenLabs |
| Not an ASR model | Does not transcribe speech; can post-process ASR output as a downstream consumer |
| Not a machine translator | Does not reorder grammar or translate meaning; word order is preserved by design |
| Not a language model | No neural inference at runtime; deterministic and CPU-only |
| Not a dataset | Ships with seed lexicons as data, but is not a research corpus |
| Not a hosted API (yet) | V0.1–V1 is a pip-installable library; hosted API is V4 roadmap |
| Not a finished product | V0.1 coverage on arbitrary Hinglish is near-zero; V1 is the first usable release |

This framing matters for positioning in the Indian AI ecosystem, where IndicF5, Sarvam, and CosyVoice2 are acoustic modeling solutions. OpenHinglish is not competing with them — it is the missing preprocessing step they all need for Roman-script input.

---

## 2. The Wedge

### The problem IndicF5 and others do not solve

IndicF5 (MIT, 11 languages, near-human quality), Indic-Parler-TTS (Apache-2.0), and CosyVoice2-0.5B (Apache-2.0) are excellent acoustic models. They all share one documented limitation: **they expect native-script input** (Devanagari for Hindi, etc.).

Indian users type in Roman script. A chatbot or IVR that receives `"bhai kal mera intv h paytm me"` cannot pass that directly to IndicF5. The common workarounds today are:
- Ad-hoc regex with hand-rolled replacements (fragile, unmaintainable, company-specific)
- Passing the Roman text as-is and hoping the TTS handles it (it does not, or does so inconsistently)
- Using IndicXlit at inference time (adds latency, non-deterministic, no brand/abbreviation handling)

None of these are systematic, explainable, or community-maintained.

### The killer integration: drop-in preprocessor for IndicF5

The primary wedge is a **one-function preprocessor** that takes Roman-Hinglish and returns IndicF5-ready Devanagari:

```python
from openhinglish import normalize

result = normalize("bhai kal mera intv h paytm me")
tts_input = result.tts   # "भाई कल मेरा इंटरव्यू है पे-टी-एम में"

# Pass tts_input directly to IndicF5
```

This is the entire pitch: one import, one function call, IndicF5 now handles Hinglish. No GPU needed for the normalization step. No retraining.

### Proof-of-pain demos (to be built)

These do not exist yet. Building them is the single most important marketing activity before V1 outreach.

**Demo 1 — IndicF5 mangling:**
Run IndicF5 on `"aaj mera interview hai, main ready hoon"` (raw Roman input). Show the acoustic output — likely garbled or silent for unknown tokens. Then run OpenHinglish first, pass the Devanagari `tts_form` to IndicF5. Show the clean result. Side-by-side audio comparison.

**Demo 2 — Brand/abbreviation failure:**
Input: `"UPI se payment karo, NEFT slow hoga"`. Without normalization: IndicF5 or a Sarvam API either reads the acronym letter-by-letter awkwardly or mispronounces it. With OpenHinglish: `"यूपीआई से पेमेंट करो, एनईएफटी स्लो होगा"` — the pronunciation is correct.

**Demo 3 — SMS/abbreviation expansion:**
Input: `"bhai kl aaunga, rn busy hoon"`. Show that `kl` → `कल`, `rn` → `अभी` is handled by the lexicon layer, and the TTS gets clean text.

**Demo 4 — IVR failure case (ElevenLabs):**
ElevenLabs is a closed system but is widely used by Indian startups. Pass it a typical Hinglish IVR script. Document the mispronunciations. This is reproducible by anyone. The contrast with a normalized input is the proof-of-pain.

Until these demos exist, the positioning is a thesis, not a demonstrated gap. Building Demo 1 should be Task 1 after V1 lexicon scaling.

### Why TTS first, not ASR post-processing

Both are valid wedges, but TTS is:
- Easier to demo visually/aurally (you can hear the difference immediately)
- More immediately actionable (the fix is just "call normalize() before your TTS call")
- More likely to produce word-of-mouth among Indian AI devs who are building voice products

ASR post-processing (cleaning ASR output that contains Hinglish transcriptions) is a real use case but requires an ASR system in the demo chain. TTS is simpler and faster to validate.

---

## 3. Target Adopters

### Primary adopters (V1 target)

| Segment | Why they need OpenHinglish | Entry point |
|---|---|---|
| **Indian TTS developers** using IndicF5, CosyVoice2, or Indic-Parler-TTS | Their models expect Devanagari; their users type Roman | `pip install openhinglish` + one-function preprocessor |
| **Indian voicebot / IVR developers** (startups, BPO-tech, fintech) | Customer queries arrive in Hinglish; they need clean TTS output | Same entry point; abbreviation/brand handling is their specific pain |
| **Indian chatbot developers** (WhatsApp bots, app assistants) | Text normalization improves display quality; brand casing matters | `display_form` output is immediately useful |
| **Sarvam AI ecosystem users** | Sarvam Bulbul v2 API targets Indian languages; preprocessing layer improves inputs | Community touchpoint via Sarvam Discord/community |

### Secondary adopters (V2–V3 target)

| Segment | Why |
|---|---|
| **Indian edtech / accessibility** | Read-aloud features for Hinglish content; pronunciation for language learners |
| **ASR post-processing developers** | Normalize ASR output containing Roman-Hinglish before downstream NLU |
| **Search and retrieval** | Index normalization for Hinglish queries |
| **NLP researchers** | Clean benchmark and eval tooling for code-switched Hindi-English |

### Segments to de-prioritize at V1

- **Non-Indian language users**: Out of scope until V2.
- **English-only TTS users**: ElevenLabs and similar handle English fine; OpenHinglish adds no value.
- **Academic-only users**: Can adopt, but PyPI publication and integrations are the priority over academic-only adoption paths.

---

## 4. Adoption Strategy

### Land-and-expand in three stages

**Stage 1 — Land (V1):**
Minimize activation energy to zero. The entire value proposition must be accessible in under 5 minutes:

```
pip install openhinglish
python -c "from openhinglish import normalize; print(normalize('bhai kl milte h').tts)"
```

If someone needs to configure a server, install system dependencies, or read more than one page of documentation to get a result, most people will not try it. The library must be stateless, dependency-light, and importable with no setup.

Publish to PyPI. Include a one-page README with one concrete example showing the IndicF5 integration. Nothing else matters at this stage.

**Stage 2 — Integrate (V1–V2):**
Once someone installs the library, the next ask is: wire it into their TTS pipeline. Provide an `openhinglish.integrations.indicf5` thin wrapper (V4 roadmap, but a code snippet in the README is sufficient at V1). Make the IndicF5 integration a literal copy-paste.

The goal: one integration article, one Jupyter notebook on Hugging Face, one short devlog. Each with a reproducible demo.

**Stage 3 — Contribute (V2+):**
Once users encounter missing words (they will), give them an obvious, easy path to fix it: edit a TSV file in the repo. No Python required. No environment setup. Just open the file on GitHub, add a row, submit a PR. This is the community flywheel trigger point.

Lower activation energy at each stage:
- V1: pip install → try it → works on demo inputs (but limited on real text — be honest)
- Integration: one code snippet → plugged into their pipeline
- Contribution: "this word is wrong" → TSV PR → fix is live in next release

### PyPI packaging requirements (pre-V1 checklist)

- [ ] Version pinned at 1.0.0 following semver; no 0.x PyPI release unless clearly labeled alpha/beta
- [ ] `data/` files included in the wheel via `package_data` / `include_package_data`
- [ ] No runtime ML dependencies; only stdlib + one or two lightweight packages
- [ ] `openhinglish "..." ` CLI entry point works after pip install
- [ ] README on PyPI page renders correctly and shows the one-liner example

---

## 5. Community Strategy

### The data-contribution flywheel as the core moat

The engine's accuracy is bounded by lexicon coverage. Lexicons are TSV files. TSV files are editable by anyone. This is intentional — it means the project's most important work can be crowdsourced without requiring Python skills.

The flywheel:

```
More lexicon entries → better coverage → developers trust it for real use
        ^                                           |
        |                                           v
Developers submit missing words             Word spreads in Indian AI community
        ^                                           |
        |                                           v
Community grows                         More developers try it → hit missing words
```

The critical activation: a developer tries OpenHinglish, hits a missing word (e.g., `"zomato"` not in the brands gazetteer), sees the TSV file is right there in the repo, adds one row, submits a PR. That PR is merged in a week. They tell someone. The flywheel turns.

The flywheel **does not start** until V1 has real coverage and real users hitting real missing words. At V0.1 the coverage is so low that there is nothing to contribute to — everything is missing. V1 lexicon scaling is the prerequisite.

### Language maintainers

Every V2 language needs a dedicated maintainer (see GOVERNANCE.md Section 2.4). For community strategy, this means:
- Recruit language maintainers **before** starting V2 work, not after.
- Approach the AI4Bharat Marathi/Tamil/Telugu communities, regional NLP communities, and university NLP groups.
- A language maintainer gets a named `CODEOWNERS` entry, public credit in the README, and is the person whose name appears on the Hugging Face model card if/when a language-specific benchmark is published.

### Recognition

Contributors who add more than 50 lexicon entries are listed in `CONTRIBUTORS.md`. Language maintainers are listed prominently in the README. Benchmark contributors (who provide human-annotated gold sentences) are credited in the benchmark TSV file itself.

No paid rewards, no NFTs, no points systems. This is a straightforward open-source project. The recognition is attribution.

---

## 6. Developer Outreach Plan

This is a realistic plan for a solo maintainer with a full-time job. Not everything can happen at once.

### Priority order (solo-maintainer-honest)

1. **Hugging Face (highest leverage per effort):**
   - Publish an OpenHinglish organization on Hugging Face.
   - Upload the IndianTTSBench-mini eval set as a Hugging Face Dataset. Tag it with `hinglish`, `roman-hindi`, `text-normalization`.
   - Write a Hugging Face Space (or Gradio demo) that demonstrates the IndicF5 proof-of-pain demo. This is the single most discoverable artifact in the Indian AI community.
   - This is V1 launch-day work. Everything else is secondary to having something live on Hugging Face.

2. **GitHub (discoverability and trust):**
   - README must include: the one-liner demo, the IndicF5 integration snippet, the honest "current state" note (real-world coverage is limited until V1), and a link to contribute missing words via TSV PR.
   - Use accurate GitHub topics: `hinglish`, `text-normalization`, `indian-languages`, `tts`, `nlp`, `romanized-hindi`, `devanagari`.
   - A well-maintained `CHANGELOG.md` is more trust-building than a blog post.

3. **Indian AI/ML community touchpoints:**
   - **AI4Bharat Discord / community:** OpenHinglish's primary wedge is as a preprocessor for their models. Introduce the project there once V1 is out. Not before. A half-working demo reflects poorly.
   - **Sarvam community:** Sarvam Bulbul v2 users have the same Hinglish input problem. A focused integration note is a legitimate touchpoint.
   - **IndiaML / Papers with Code India:** Submit the IndianTTSBench-mini as an eval standard once it has 300+ sentences.

4. **Content and devlogs (low-cost, high-leverage for solo):**
   - One LinkedIn post at V1 launch: "I built an open-source Roman-Hinglish normalizer because IndicF5 can't read 'bhai kl milte h'. Here's why that matters for Indian voice AI." Short, specific, honest about the state.
   - One Dev.to or Hashnode article: technical walkthrough of the 7-stage pipeline. Indian developers read these. This is also SEO for `roman hinglish tts normalization`.
   - One Jupyter notebook on Hugging Face or Colab: reproduce the IndicF5 proof-of-pain demo end-to-end. This is the most shareable artifact.
   - Avoid over-announcing. One good demo notebook beats five "we launched" tweets.

5. **Conference and meetup angles (V2+, not V1):**
   - **ICON (International Conference on NLP, India):** The IndianTTSBench-mini, once grown to a proper eval set, is a short paper or workshop submission. Code-switch normalization evaluation is an underserved area.
   - **PYCON India:** A talk on "building a deterministic NLP pipeline for Hinglish" is a natural fit. The deterministic + explainable angle is unusual in an era of neural everything.
   - **Regional meetups (Delhi/Noida NLP groups):** Lower activation energy than conferences; earlier in the timeline.
   - None of this is worth pursuing before V1 is on PyPI with real coverage. Announcing a skeleton project at a conference is a mistake.

### What NOT to do

- Do not spam Indian AI Discord servers with unsolicited announcements before V1.
- Do not claim production-readiness before the lexicons are at V1 scale (10k+ entries).
- Do not create a Twitter/X presence that cannot be maintained consistently. One good GitHub README is worth more than 50 inconsistent tweets.
- Do not pursue conference submissions with the current 59-sentence single-author benchmark. It will not pass peer review until it reaches V1 scale (300+ multi-annotator sentences).

---

## 7. Moats

These are the factors that make OpenHinglish defensible as a standard, not just a utility. None of them are strong at V0.1. They are investments made through consistent execution.

### 7.1 Data / lexicon flywheel

The core moat. Proprietary lexicons built by community contributors — thousands of verified Roman-Hinglish spellings, brand pronunciations, names gazetteer entries — that took years of crowdsourced curation. No one can replicate this instantly even if they fork the code. This moat only forms at V2+ with an active contributor community. At V0.1, there is no moat on data.

### 7.2 The benchmark as a standard

If IndianTTSBench becomes the reference eval for Hinglish text normalization — cited in papers, used by IndicF5 evaluators, linked in Hugging Face leaderboards — then every competing solution is measured against OpenHinglish's benchmark. This is a first-mover advantage that is hard to dislodge once established.

This requires growing the benchmark to 300+ human-verified sentences (V1) and publishing it as a Hugging Face Dataset. The benchmark is as important as the library itself for long-term positioning.

### 7.3 Clean permissive license

MIT code + CC0/CC-BY data (with share-alike flagged, not hidden) means Indian startups and enterprise developers can use and embed this commercially with no legal risk. Closed alternatives (ElevenLabs preprocessing, Sarvam's internal pipeline) are not community-extensible. A clean license removes procurement friction that would otherwise kill adoption at the enterprise level.

### 7.4 Edge / offline deployment

No GPU at inference. No API call. No internet dependency. Deterministic output. This is a significant operational advantage for IVR systems, on-device voice assistants, and low-connectivity deployments. Neural alternatives require GPU infrastructure or an API subscription.

### 7.5 First-mover on the specific Roman-Hinglish gap

Roman-script Hinglish normalization as a discrete, packaged, community-maintained library does not currently exist as an open-source artifact (per the brief's verified competitive landscape). Being the first package that specifically solves this problem with a permissive license creates discoverability and citation advantages. First-mover does not mean forever-winner, but it means the ecosystem conversation starts with this project.

---

## 8. Challenged Assumptions / Risks

This section is required by the project brief. These are honest, not performative.

### 8.1 Unproven demand — the core risk

**The fundamental assumption of this entire strategy is unproven: that Indian TTS/chatbot developers need a dedicated Roman-Hinglish normalization library rather than their existing ad-hoc solutions.**

The competitive landscape says the gap is real. Independent sources confirm Hinglish handling is poor. But "Hinglish handling is poor" does not automatically mean "developers will adopt a library to fix it." The alternative is that most developers:
- Are building English-only or native-script-only products and the Hinglish case is rarer than assumed
- Have already built internal ad-hoc solutions they consider "good enough"
- Will just prompt-engineer their way around it with an LLM preprocessor

**How to validate this early, before V1:**
1. Post the proof-of-pain IndicF5 demo (even without V1 lexicon coverage) on Hugging Face and in the AI4Bharat community. Measure responses — not views, actual reactions and comments.
2. Ask directly in relevant Discord channels: "Does anyone have a solved solution for normalizing Hinglish before IndicF5?" If the answer is "yes, here's our regex" repeatedly, that is market research.
3. If zero traction after 3 months of V1 being on PyPI with real demos, revisit the wedge thesis rather than doubling down.

### 8.2 Risk of a big lab (AI4Bharat or Sarvam) shipping their own

AI4Bharat has deeper data resources, more contributors, institutional funding, and existing TTS model relationships. If they ship a Roman-Hinglish preprocessor module as part of IndicF5 or IndicXlit, it would likely eclipse OpenHinglish for their own user base.

Mitigation: This is a real risk but not a reason to stop. If AI4Bharat builds it, they will almost certainly release it permissively, which validates the need and potentially allows OpenHinglish to complement or integrate with their solution rather than compete. The benchmark moat (Section 7.2) survives this scenario. The lexicon flywheel (Section 7.1) survives too if the community is already invested. The worst case is irrelevance, not damage.

### 8.3 Solo outreach bandwidth

A solo maintainer doing V1 lexicon scaling, benchmark curation, packaging, CI, documentation, and community outreach simultaneously is not realistic. These must be sequenced, not parallelized.

Realistic sequencing:
1. V1 lexicon scaling (the work, not the announcement) — months 1–3
2. PyPI packaging and Hugging Face Dataset upload — month 3
3. First public announcement (Hugging Face Space + LinkedIn post) — month 3
4. Respond to initial feedback, patch missing words — months 3–4
5. Conference/meetup outreach — month 6+

Announcing before the library has real coverage will burn the first-impression opportunity. The outreach plan in Section 6 is staged for this reason.

### 8.4 The benchmark score needs an honest disclaimer

The current IndianTTSBench-mini scores **0.92 display exact-match (0.92 TTS) on 59 single-author sentences** across 11 categories. This is a real, reproducible signal — and it honestly surfaces weak spots (roman-hindi 0.667 on long-tail vocabulary; code-switch 0.917 on one ambiguity). But it must never be cited as a production accuracy guarantee. Until the benchmark reaches V1 scale (300+ diverse, multi-annotator sentences), always pair the number with the context that it is single-author and lexicon-leaning; quoting a bare score as evidence of quality will damage credibility with anyone who reads the methodology.

### 8.5 CC-BY-SA from Dakshina could limit commercial embedding

Dakshina (CC-BY-SA-4.0) is the primary source for scaling the Roman-Hindi lexicon to V1. Share-alike means TSV files derived from Dakshina must carry CC-BY-SA. Downstream users who embed those TSV files in their own commercial products may face share-alike obligations — depending on how legal counsel reads the dataset's redistribution terms in their specific use case.

This is documented and flagged in GOVERNANCE.md and DATA_LICENSES.md, but it is worth noting here because it affects the "clean permissive license" moat in Section 7.3. The code moat remains clean (MIT). The data moat has a partial asterisk.

If this becomes an adoption blocker, the long-term solution is to replace Dakshina-derived rows with CC0 or CC-BY equivalents (from IndicVoices-R, Wikidata, or contributor knowledge). That is a V2+ data quality initiative, not a V1 blocker.
