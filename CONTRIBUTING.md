# Contributing to OpenHinglish

Thank you for your interest in contributing. OpenHinglish is a deterministic, CPU-only
Roman-Hinglish text normalization engine. Every contribution — from a single TSV row to
a new normalization rule — is welcome.

---

## Table of Contents

1. [Dev Setup](#dev-setup)
2. [TDD Requirement for Code Changes](#tdd-requirement-for-code-changes)
3. [The Easiest High-Value Contribution: Expanding the Lexicons](#the-easiest-high-value-contribution-expanding-the-lexicons)
4. [Adding a Benchmark Sentence](#adding-a-benchmark-sentence)
5. [PR Process](#pr-process)
6. [Definition of Done](#definition-of-done)

---

## Dev Setup

```bash
# 1. Clone the repo
git clone https://github.com/shankarmishra/openhinglish.git
cd openhinglish

# 2. Create and activate a virtual environment
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate

# 3. Install the package in editable mode with dev + server extras
pip install -e ".[dev,server]"

# 4. Run the test suite to confirm everything is green
pytest
```

All tests must pass before you open a PR. If something fails on a clean clone, open an
issue — that is itself a valid bug report.

---

## TDD Requirement for Code Changes

Any change to Python source code (anything under `src/`) **must** follow
test-driven development:

1. Write a failing test that exercises the new behavior.
2. Write the minimum code to make the test pass.
3. Refactor if needed, keeping tests green.

Do not submit a PR that adds or modifies Python code without a corresponding test.
Tests live under `tests/` and use `pytest`. Name test files `test_<module>.py`.

---

## The Easiest High-Value Contribution: Expanding the Lexicons

The single easiest and most impactful thing you can do is **add rows to the TSV data
files**. No Python knowledge is required. Open any TSV in a plain text editor or
spreadsheet app, add rows, save as UTF-8, and open a PR.

**Golden rules for TSV edits:**

- **Only ADD rows.** Do not delete or reorder existing rows without a discussion issue.
- **Keep entries correct.** Wrong normalizations are worse than missing ones.
- **Provide a source/note.** Even a brief note ("common WhatsApp usage", "verified
  against news corpus") helps reviewers.
- **No tabs inside cell values.** Columns are tab-separated; a stray tab breaks parsing.
- **UTF-8, no BOM.**

### File Schemas and Example Rows

#### `src/openhinglish/data/lexicons/roman_hindi.tsv`

Maps a Roman-script Hinglish surface form to its canonical normalized form.

| Column | Name | Description |
|--------|------|-------------|
| 1 | `surface` | Raw token as it appears in user text |
| 2 | `normalized` | Preferred normalized Roman-Hinglish form |
| 3 | `pos` | Part of speech tag (`NOUN`, `VERB`, `ADJ`, `ADV`, `PARTICLE`, `OTHER`) |
| 4 | `notes` | Free-text provenance / usage note |

**Example row:**

```
kal	kal	NOUN	tomorrow or yesterday depending on context; very common
```

---

#### `src/openhinglish/data/lexicons/english_freq.tsv`

Assigns an English word a frequency tier used to decide whether it should pass through
unchanged or be treated as a potential Hinglish token.

| Column | Name | Description |
|--------|------|-------------|
| 1 | `word` | Lowercase English word |
| 2 | `tier` | `1` = very high frequency (always pass through), `2` = high, `3` = medium |
| 3 | `notes` | Optional source or rationale |

**Example row:**

```
because	1	core English function word; always pass through
```

---

#### `src/openhinglish/data/lexicons/english_tts.tsv`

Provides a pronunciation hint for English words that are commonly read aloud in
Hinglish contexts, helping downstream TTS systems.

| Column | Name | Description |
|--------|------|-------------|
| 1 | `word` | English word (mixed case preserved) |
| 2 | `tts_hint` | Phonetic hint or ARPABET-style pronunciation |
| 3 | `notes` | Optional context note |

**Example row:**

```
WiFi	WY-fy	ubiquitous in Indian English; common in Hinglish sentences
```

---

#### `src/openhinglish/data/lexicons/sms_abbrev.tsv`

Expands SMS/chat abbreviations to their full Roman-Hinglish or English forms.

| Column | Name | Description |
|--------|------|-------------|
| 1 | `abbrev` | Abbreviation as it appears in messages (case-sensitive) |
| 2 | `expansion` | Full expanded form |
| 3 | `register` | Usage register: `sms`, `chat`, `social`, `all` |
| 4 | `notes` | Optional provenance / example context |

**Example row:**

```
tbh	to be honest	all	extremely common across English and Hinglish chat
```

---

#### `src/openhinglish/data/gazetteers/names.tsv`

Indian personal names gazetteer. Used to prevent name tokens from being
mis-normalized.

| Column | Name | Description |
|--------|------|-------------|
| 1 | `name` | Name in Roman script (capitalize first letter) |
| 2 | `type` | `first`, `last`, or `both` |
| 3 | `region` | Broad region hint: `pan-india`, `north`, `south`, `east`, `west` |
| 4 | `notes` | Optional note |

**Example row:**

```
Arjun	first	pan-india	common Hindu male first name; also a character from Mahabharata
```

---

#### `src/openhinglish/data/gazetteers/brands.tsv`

Indian brand and product name gazetteer. Ensures brand names are preserved exactly.

| Column | Name | Description |
|--------|------|-------------|
| 1 | `brand` | Canonical brand name (exact casing) |
| 2 | `category` | Product category (`food`, `telecom`, `ecommerce`, `finance`, `other`) |
| 3 | `notes` | Optional note |

**Example row:**

```
Zomato	ecommerce	major Indian food delivery brand; preserve exact casing
```

---

## Adding a Benchmark Sentence

Benchmark sentences live in `tests/bench/` (or the path documented in `docs/`). Each
sentence exercises a normalization path end-to-end. To add one:

1. Find the benchmark file (e.g., `tests/bench/sentences.tsv` or similar).
2. Add a row: `input_sentence<TAB>expected_normalized_output`.
3. Make sure the expected output is genuinely correct — wrong benchmarks degrade the
   project's ability to detect regressions.
4. Run `pytest` and confirm the new sentence passes.

If you are adding a sentence specifically to reproduce a bug, add the sentence in the
same PR as the bug fix, with the test failing before the fix and passing after.

---

## PR Process

1. **Open an issue first** for anything beyond trivial TSV additions, so the approach
   can be agreed before you invest time writing code.
2. **Branch naming:** `feat/<short-description>`, `fix/<short-description>`, or
   `data/<short-description>` for TSV-only PRs.
3. **PR description must include:**
   - What changed and why.
   - For data PRs: source/provenance of new rows.
   - For code PRs: which tests cover the change.
4. **One logical change per PR.** Do not bundle unrelated lexicon edits with code
   refactors.
5. A maintainer will review within a reasonable time. Please be patient on a V0 project.

---

## Definition of Done

A PR is ready to merge when **all** of the following are true:

- [ ] `pytest` exits green with no skipped tests (unless the skip is pre-existing and
      documented).
- [ ] Benchmark scores have not regressed (run the bench suite if one exists; note
      results in the PR description).
- [ ] Any new data rows include a source/note column value.
- [ ] `DATA_LICENSES.md` has been updated if any new data file was added or any
      external source was used.
- [ ] Code changes are covered by tests (TDD — see above).
- [ ] The PR description is complete (what, why, provenance).
