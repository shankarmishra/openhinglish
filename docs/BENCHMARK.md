# OpenHinglish — Benchmark Reference (IndianTTSBench)

> Authoritative specification for the IndianTTSBench-mini evaluation harness and its path to becoming a community standard.
> Read alongside `DATASETS.md` (data provenance).
> Senior, honest tone: the current 59-sentence score is an early signal, not a production capability claim.

---

## 1. IndianTTSBench-mini Design

### 1.1 Purpose

IndianTTSBench-mini exists to answer one practical question:

> Given an informal Roman-Hinglish input sentence, does the OpenHinglish normalization engine produce an output that a TTS system would correctly synthesize?

It is not a language-model benchmark. It does not measure fluency, naturalness, or acoustic quality. It measures the engine's ability to deterministically map a raw text token to its correct `display_form` and `tts_form` — the two outputs that feed downstream synthesis. All other capabilities (speed, memory, API ergonomics) are out of scope for this benchmark.

Secondary purpose: regression gating. Every PR that touches lexicons, pipeline stages, or data files runs the full bench in CI. A score drop on an existing row blocks the merge until explicitly overridden with a documented justification.

### 1.2 Categories

**Actual current categories.** The benchmark TSV (`eval/bench_mini/sentences.tsv`) currently uses **11 category slugs**. Each row carries exactly one slug. These are the categories actually present and scored today:

| Category | What it tests | Rows | display EM | tts EM |
|---|---|---|---|---|
| **roman-hindi** | Core Roman → Devanagari transliteration of common Hindi words | 12 | 0.667 | 0.667 |
| **verb** | Verb conjugations and tense forms | 2 | 1.000 | 1.000 |
| **name** | Transliteration and TTS pronunciation of Indian personal names | 4 | 1.000 | 1.000 |
| **brand** | Brand-name recognition, casing in display, phonetic spell-out in TTS | 6 | 1.000 | 1.000 |
| **numeral** | Digit handling and Hindi/English number-word expansion per config | 4 | 1.000 | 1.000 |
| **acronym** | Letter-by-letter acronyms (e.g. `IIT`, `RBI`) | 4 | 1.000 | 1.000 |
| **abbrev** | SMS/chat abbreviation expansion (`intv` → interview) | 3 | 1.000 | 1.000 |
| **question** | Interrogative phrasings | 6 | 1.000 | 1.000 |
| **mixed** | Sentences combining several of the above | 4 | 1.000 | 1.000 |
| **code-switch** | Mid-sentence Hindi↔English transitions | 12 | 0.917 | 0.917 |
| **address** | Street addresses, sector/pin/locality tokens | 2 | 1.000 | 1.000 |

Scores above are from the current engine on the 59-sentence set (see §4.4). The two honest weak spots are now **roman-hindi** (0.667 — the long tail of uncommon vocabulary the lexicon does not yet cover, e.g. `kheti`, `bhatija`, `nukkad`) and **code-switch** (0.917 — one ambiguity case, `main` correctly = मैं "I" but the engine reads it as English "main"). Earlier weak spots — address, and the abbreviation TTS channel — were fixed in the latest engine round.

**Planned (not yet a separate slug).** A future taxonomy expansion will add an explicit **ambiguity-traps** category for tokens that require context to resolve (`main` = I / main road, `kal` = yesterday / tomorrow, `to` = then / to / too). These currently fall inside `code-switch`/`mixed` rows. Ambiguity-traps deserve extra weight because they expose the core limitation of a deterministic engine: without context, such tokens cannot always be resolved correctly. The V3 neighbour-context disambiguator addresses some of these (e.g. "main road" vs "main ghar"); the rest are deferred. The benchmark must honestly represent this limitation rather than hide it by avoiding ambiguous test cases.

### 1.3 Current Size and Growth Plan

| Release | Target rows | Status |
|---|---|---|
| V0.1 → current | 59 sentences across 11 categories | Done — single-maintainer authored; an early signal, not multi-annotator validated |
| V1 | ≥ 300 human-verified sentences | Requires data sprint; multi-annotator |
| V2 | 300+ per language (Hindi + 6 new) | Per-language frontier |
| V3 | 500+ including ambiguity-trap pairs | Ambiguity-trap set grows with V3 learned disambiguator |
| V5 | 1 000+ | Full public benchmark; community-submitted; governed leaderboard |

The current 59 sentences were authored by the maintainer who also wrote the engine. They are large enough to surface real weak spots (roman-hindi and code-switch both score below 1.0), but they are **not** multi-annotator validated and do not yet represent the diversity of real-world Hinglish. Treat 0.92 display EM as an early signal, not a production capability claim.

### 1.4 TSV Schema

The benchmark lives at `eval/bench_mini/sentences.tsv`. The canonical column schema:

```
input        TAB ref_display      TAB ref_tts           TAB category     TAB notes
```

**Column definitions:**

- `input` — raw Roman-Hinglish string exactly as a user would type it; no pre-processing applied.
- `ref_display` — the expected `display_form` output: human-readable mixed script, with Devanagari for Hindi tokens, English for English tokens, original casing for brands/names.
- `ref_tts` — the expected `tts_form` output: fully phonetic Devanagari rendering, ready for a TTS synthesizer; all brand/number tokens expanded to spoken Hindi or English words.
- `category` — exactly one of the 11 category slugs above. Sentences that exercise several challenges at once use the dedicated `mixed` slug rather than a pipe-separated list. (A future schema revision may allow multi-label rows; the harness does not require it today.)
- `notes` — free text; records adjudicator names, date, open ambiguity decisions, and any provenance if vocabulary derived from Dakshina.

**Multi-reference extension (V1+):** When a sentence has more than one valid normalization, additional reference columns are appended: `ref_display_2`, `ref_tts_2`, etc. The evaluation harness checks against all supplied references. See Section 3 for methodology.

Example rows (illustrative):

```tsv
input	ref_display	ref_tts	category	notes
bhai kal mera intv h paytm me	भाई कल मेरा interview है Paytm में	भाई कल मेरा इंटरव्यू है पे-टी-एम में	code-switch	seed; adj: maintainer
```

---

## 2. The No-Ground-Truth Problem

### 2.1 Why Hinglish Has No Single Correct Normalization

Hinglish normalization does not have a unique correct answer. This is not a data-quality problem; it is a property of the task. Consider:

- `bhai` can normalize to `भाई` (correct) but a transcript-style display might prefer keeping it Roman. Both are defensible.
- `interview` can be left as English in display (`interview`) or transliterated to Devanagari in display (`इंटरव्यू`). Style guides differ.
- For TTS, `Paytm` can render as `पे-टी-एम` (letter-by-letter) or `पेटीएम` (phonetic). Different TTS systems prefer different forms.
- `kal` is ambiguous between `कल` (yesterday/tomorrow) without context. A deterministic system cannot resolve it; both normalizations are correct given the input alone.

Evaluating against a single reference with exact-match metrics will therefore systematically under-report accuracy. A system that produces `पेटीएम` will be marked wrong if the sole reference is `पे-टी-एम`, even though both are valid.

### 2.2 Methodology to Handle It

**Three interlocking mechanisms:**

**A. N-best coverage (primary metric)**
Rather than asking "does the top-1 output match the reference?", ask: "is any correct answer present in the engine's top-k alternatives?" If k = 3 and the engine returns `पे-टी-एम`, `पेटीएम`, `पेटिम` as alternatives, a reference matching any of these constitutes a hit.

The engine already produces `Token.alternatives[]` as a first-class output. N-best coverage at k = 1, 3, 5 is reported separately so callers can see both precision (k=1) and recall (k=5).

**B. Multiple accepted references**
Each benchmark sentence may carry up to N reference normalizations, one per valid variant adjudicated by human annotators. The evaluation harness computes a hit if the engine's output matches *any* reference. Adding a new valid reference never hurts an existing system's score.

**C. Human adjudication with inter-annotator agreement (IAA)**
For V1 and beyond, every benchmark sentence must be validated by ≥ 2 independent annotators. Their independent outputs are compared:
- Where they agree: the single agreed form is the reference.
- Where they disagree: both forms are recorded as separate references, and the disagreement is logged with a rationale note.
- IAA score (Cohen's Kappa or exact-agreement percentage) is reported per batch and per category. Low IAA on a category is a signal that the category definition is under-specified, not that the annotators are wrong.

**What single-reference exact-match alone is misleading:**
It privileges one annotator's dialect and style choices as ground truth. It penalizes systems for producing equally valid but different valid outputs. It artificially inflates perceived accuracy gaps between systems. For any public leaderboard (V5), single-reference exact-match as the *sole* metric would be scientifically indefensible for Hinglish.

---

## 3. Metrics

Each metric is defined precisely below. All metrics are computed per-sentence and aggregated as macro-average across sentences in a category, then across all categories.

### 3.1 Token Classification Accuracy

**Definition:** Fraction of tokens where the engine's assigned `Category` matches the gold `Category` label in the annotated evaluation set.

```
token_classification_accuracy = correct_category_tokens / total_tokens
```

**Scope:** Requires a per-token annotated gold set (category labels per token, not just sentence-level). The current 59-sentence bench carries one category label per sentence, not per token. Add per-token annotation in V1.

**Caveat:** Category assignment is a prerequisite for all downstream stages; errors here cascade. Report separately for each Category enum value to expose which categories are weak.

### 3.2 Transliteration CER and WER

For tokens classified as HINDI_ROMAN, measure the quality of Roman → Devanagari conversion.

**Character Error Rate (CER):**
```
CER = (substitutions + insertions + deletions) / reference_length_in_characters
```
Computed with standard edit distance. Lower is better.

**Word Error Rate (WER):**
```
WER = (substitutions + insertions + deletions) / reference_length_in_words
```
For single-token evaluation WER = CER at the token level; useful at sentence level.

**Reference:** Best-matching reference from the multi-reference set (pick the reference that minimizes CER for each prediction — do not cherry-pick ex-post; document which reference was selected).

### 3.3 Normalization Exact-Match @ Display and @ TTS

Two separate exact-match scores, one for each output channel.

**Definition:**
```
exact_match@display = (sentences where predicted display == any ref_display) / total_sentences
exact_match@tts     = (sentences where predicted tts    == any ref_tts)     / total_sentences
```

Matching against *any* accepted reference (Section 2.2). Whitespace-normalized; case-sensitive (casing is semantically significant: `Paytm` ≠ `paytm`).

**Why two separate scores:** `display` and `tts` have different downstream consumers. A TTS system only sees `tts_form`; a human reader only sees `display_form`. Reporting both separately allows a caller to optimize for their use case.

### 3.4 Name and Brand Pronunciation Accuracy

**Definition:** For tokens in the `name` and `brand` categories, fraction where `tts_form` exactly matches an accepted reference TTS rendering.

Reported separately from the aggregate exact-match because name/brand handling is the most consequential failure mode for TTS — mispronouncing a person's name or a brand creates a trust failure with end-users.

### 3.5 N-best Coverage @ k

**Definition:**
```
nbest_coverage@k = (sentences where any of top-k alternatives matches any reference) / total_sentences
```

Reported for k = 1, 3, 5. Coverage@1 = exact-match accuracy. The gap between Coverage@1 and Coverage@5 quantifies how much correct signal the engine carries in its alternatives list that the top prediction misses.

### 3.6 Per-Category Breakdown

All metrics above are also reported disaggregated by category. A single aggregate score is insufficient for a multi-category benchmark — a system can score 90% overall while completely failing on `ambiguity-traps` (currently unresolvable by design in V1) and hiding that failure in aggregate. Per-category reporting makes systematic weaknesses visible.

---

## 4. Evaluation Methodology

### 4.1 Running `run_bench`

The evaluation harness is at `eval/run_bench.py`. Usage:

```bash
python eval/run_bench.py [--bench eval/bench_mini/sentences.tsv] [--k 5] [--format json|table]
```

The script:
1. Loads the benchmark TSV.
2. Calls `openhinglish.normalize(input)` for each row.
3. Computes all metrics defined in Section 3.
4. Writes a result JSON to `eval/results/bench_{timestamp}.json`.
5. Prints a summary table to stdout.

**Determinism requirement:** `run_bench` must produce identical output for the same input on every run. The pipeline is deterministic by design; any stochastic element (e.g., a future ML stage) must be seeded or disabled for bench runs.

### 4.2 Reporting Format

Every official score report must include:

```
OpenHinglish vX.Y.Z — IndianTTSBench-mini — {date}
Bench version: {git hash of sentences.tsv}
Row count: {N}   Categories: {list}

exact_match@display : {score}  (N={total_sentences})
exact_match@tts     : {score}
nbest_coverage@1    : {score}
nbest_coverage@3    : {score}
nbest_coverage@5    : {score}
token_classif_acc   : {score}  [if per-token annotation available]

Per-category breakdown:
  roman-hindi    : {em@display} / {em@tts}
  verb           : ...
  name           : ...
  brand          : ...
  numeral        : ...
  acronym        : ...
  abbrev         : ...
  question       : ...
  mixed          : ...
  code-switch    : ...
  address        : ...

Notes: {any known limitations, e.g., "roman-hindi EM is 0.667 — five rows fail on long-tail vocabulary not yet in the lexicon"}
```

### 4.3 Regression Gating in CI

Every PR triggers CI which runs `run_bench` and compares the result against the last merged score stored in `eval/results/baseline.json`.

Gating rule: any metric drop > 1% on any category blocks the PR. The PR author must either fix the regression or file an explicit override with a documented justification in the PR description. Overrides are tracked in git history and reviewed at the next minor release.

This gate applies at the current 59-row scale. A score drop on 59 rows means a real regression in the code or data; it cannot be dismissed as statistical noise at that scale.

### 4.4 Honesty About the Current 59-Sentence Score

**Current headline result (engine vs. `eval/bench_mini/sentences.tsv`, 59 sentences, 11 categories):**

```
exact_match@display : 0.915  (n=59)
exact_match@tts     : 0.915  (n=59)
```

Per-category exact-match (display / tts):

| Category | Rows | display EM | tts EM |
|---|---|---|---|
| roman-hindi | 12 | 0.667 | 0.667 |
| verb | 2 | 1.000 | 1.000 |
| name | 4 | 1.000 | 1.000 |
| brand | 6 | 1.000 | 1.000 |
| numeral | 4 | 1.000 | 1.000 |
| acronym | 4 | 1.000 | 1.000 |
| abbrev | 3 | 1.000 | 1.000 |
| question | 6 | 1.000 | 1.000 |
| mixed | 4 | 1.000 | 1.000 |
| code-switch | 12 | 0.917 | 0.917 |
| address | 2 | 1.000 | 1.000 |

Reproduce with: `python -m openhinglish.eval.run_bench`.

**What this score does and does not mean.** 0.92 exact-match is a real, reproducible number, and the benchmark surfaces honest weak spots instead of hiding them: **roman-hindi** is now the worst category (0.667 — five rows fail on long-tail vocabulary the lexicon does not yet cover, e.g. `kheti` "farming", `bhatija` "nephew", `nukkad` "street corner"), and **code-switch** sits at 0.917 because of one genuine ambiguity (`main` should be मैं "I" but the engine reads it as English "main"). Earlier weak spots — address and the abbreviation TTS channel — were fixed in the latest engine round. display and TTS EM are identical here because every remaining failure is a whole missing/ambiguous word that affects both channels.

But these 59 rows were authored by the maintainer who also wrote the engine, and they lean toward vocabulary the lexicons already cover. They do **not** adequately cover:
- Out-of-vocabulary Roman-Hindi words (the long tail of real Hinglish).
- Ambiguous tokens requiring context (no dedicated `ambiguity-traps` slice yet — see §1.2).
- Regional spelling variants.
- Any language other than Hindi + English.

The honest framing for any production evaluation: "0.92 display EM on a 59-sentence, single-author benchmark is an encouraging early signal; the roman-Hindi long tail and code-switch are known weak spots; accuracy on unseen, multi-annotator Hinglish is expected to be lower and is the V1 measurement goal." Do not quote 0.92 as a production accuracy guarantee.

---

## 5. Path to a Community Standard (V5)

### 5.1 Public Leaderboard

At V5, IndianTTSBench becomes a public leaderboard analogous to GLUE/SuperGLUE for English NLU, but scoped specifically to Roman-script Hinglish (and Indian code-switch) normalization. Any system — open-source, commercial API, or research prototype — can submit results.

**Submission format:**
```json
{
  "system_name": "...",
  "system_version": "...",
  "submission_date": "ISO-8601",
  "bench_version": "{git hash}",
  "results": {
    "exact_match_display": 0.XX,
    "exact_match_tts": 0.XX,
    "nbest_coverage_k1": 0.XX,
    ...
    "per_category": { ... }
  },
  "system_description_url": "...",
  "reproducible": true|false
}
```

Submissions where `reproducible: false` (closed, non-replicable systems) are listed separately from open systems. This mirrors the HumanEval / HELM precedent of distinguishing reproducible from "trust us" claims.

### 5.2 Governance of the Benchmark

A benchmark that a single maintainer can silently modify is not a community standard. Starting at V5:

- **Benchmark freeze policy:** The core sentence set (the "frozen track") is immutable after each versioned release. New sentences go into a "growing track" that is clearly labeled as not yet stable for comparison.
- **Multi-maintainer review:** Changes to the frozen track require ≥ 2 maintainer approvals and a public comment period (minimum 2 weeks).
- **Versioned releases:** Each stable benchmark version carries its own semver tag; leaderboard submissions reference a specific version.
- **Reference set governance:** New accepted references for existing sentences (extending the multi-reference set) require the same dual-approval process. Adding a reference can affect all historical submissions' scores; this must be communicated.

### 5.3 Preventing Overfitting to the Benchmark

An open public benchmark is gameable. Specific risks:

- **Teaching to the test:** A system specifically tuned on the benchmark sentences will show inflated scores. Mitigation: maintain a private hold-out set (not publicly released) that is scored by the governance committee for any system claiming a leaderboard top-3 position.
- **Reference expansion gaming:** Adding references that happen to match a specific system's outputs inflates that system's score without improving the benchmark. The multi-maintainer approval process for reference additions provides a partial guard; the governance committee checks proposed additions for conflict of interest.
- **Category gaming:** A system that excels at `numeral` but is catastrophic on `address` (or a future `ambiguity-traps` slice) can still post competitive aggregate scores. Per-category reporting (mandatory) makes this transparent; the leaderboard should surface per-category results by default.

---

## 6. Challenged Assumptions / Risks / Open Questions

1. **"A benchmark of 59 rows growing to 300 is straightforward."** Multi-annotator adjudication of 300 Hinglish sentences to the standard required (per-token labels, dual annotation, IAA reporting) is 50–100 person-hours minimum. With a bus-factor-1 project, this is a multi-month commitment. The V1 timeline must reflect this honestly.

2. **"The category taxonomy is complete."** The 11 current categories are a reasonable starting point but almost certainly incomplete, and lack a dedicated `ambiguity-traps` slice (see §1.2). Missing candidates: honorifics (`ji`, `sahab`), onomatopoeia, transliterated English idioms (`game changer` → correct Devanagari?), regional greetings (`namaskar` vs. `sat sri akal`). The category set should be treated as open and versioned.

3. **"N-best coverage at k=5 is a meaningful proxy for 'the correct answer is reachable.'"** Only if the engine's alternatives are genuinely diverse and not all minor variants of the same wrong answer. If the engine is confidently wrong, all 5 alternatives may be wrong together. N-best coverage is a necessary condition for "the engine has the right answer somewhere" but not sufficient.

4. **"The ambiguity-trap category will be fairly evaluated."** In V1, the engine deterministically picks one resolution for ambiguous tokens (e.g., defaults `kal` to `कल` without directional marking). It will score poorly on ambiguity-trap sentences where the context requires the other interpretation. This is not a bug — it is the stated V1 limitation. The benchmark must document this expectation explicitly, or the poor score will be misread as a regression rather than an acknowledged gap.

5. **"IAA will be high enough to produce a reliable benchmark."** Hinglish normalization has genuine subjective dimensions (transliteration style, whether to leave a word in Roman). If IAA is below ~0.70 on a category, the category definition may be too vague to be a reliable benchmark signal. Plan to compute and publish IAA scores as part of the V1 data release, and revise category definitions if IAA is low.

6. **"A public leaderboard prevents gaming."** It does not; it changes the economics. The V5 governance design (private hold-out set, conflict-of-interest review on reference additions) mitigates but does not eliminate gaming. The leaderboard's value ultimately depends on the community trusting the governance process. Trust is built slowly and lost quickly; the governance model should be conservative rather than permissive.

7. **"The benchmark is independent of OpenHinglish."** It should be. A benchmark designed and scored only against one engine will be optimized for that engine's failure modes. From V1 onward, the benchmark harness should be documented as engine-agnostic (any system that accepts a string and returns a structured result can be scored), and at least one external system should be run against it before any public leaderboard claim is made.
