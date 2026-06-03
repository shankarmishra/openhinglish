# OpenHinglish — Repository Structure

> Status: V0.1 "Foundation" — updated to reflect actual repo state as of V0.1 GA.
> Items marked `[planned]` are not yet created; all others exist on `main`.
> Read alongside `ARCHITECTURE.md` (pipeline design) and `DATASETS.md` (data provenance).

---

## 1. Final Repository Tree

Items marked `[exists]` are present in the V0.1 codebase. Items marked `[planned]` are not yet
created; their location is specified here so contributors know exactly where to put them.

```
openhinglish/                              ← repo root
│
├── .github/                               [exists]
│   ├── workflows/
│   │   ├── ci.yml                         [exists]   pytest on push/PR (ubuntu + windows, py 3.11/3.12)
│   │   └── publish.yml                    [planned]  PyPI release on version tag
│   ├── ISSUE_TEMPLATE/                    [exists]
│   └── PULL_REQUEST_TEMPLATE.md           [exists]
│
├── src/
│   └── openhinglish/
│       ├── __init__.py                    [exists]   normalize() public API
│       ├── types.py                       [exists]   Token, Candidate, Category, Config, NormalizationResult
│       ├── data_loader.py                 [exists]   load_map / load_set / load_gazetteer (lru_cache)
│       ├── disambiguator.py               [exists]   Disambiguator Protocol + FrequencyDisambiguator (V1 no-op)
│       │
│       ├── pipeline/
│       │   ├── __init__.py                [exists]
│       │   ├── s0_preprocess.py           [exists]   tokenize()
│       │   ├── s1_classify.py             [exists]   classify()
│       │   ├── s2_spellnorm.py            [exists]   spell_normalize()
│       │   ├── s3_translit.py             [exists]   transliterate() + akshara_fallback()
│       │   ├── s4_names_brands.py         [exists]   resolve_entities()
│       │   ├── s5_numerals.py             [exists]   expand_numerals()
│       │   └── s6_assemble.py             [exists]   assemble()
│       │
│       ├── data/
│       │   ├── __init__.py                [exists]
│       │   ├── lexicons/
│       │   │   ├── __init__.py            [exists]
│       │   │   ├── roman_hindi.tsv        [exists]   Roman→Devanagari + frequency (13 rows, seed)
│       │   │   ├── english_freq.tsv       [exists]   English word + frequency (8 rows, seed)
│       │   │   ├── english_tts.tsv        [exists]   English word → Devanagari TTS form (6 rows, seed)
│       │   │   ├── sms_abbrev.tsv         [exists]   SMS abbreviation → expansion (6 rows, seed)
│       │   │   │
│       │   │   ├── marathi/                    [exists — scaffold, not yet wired into engine]
│       │   │   │   ├── roman_marathi.tsv              [exists]
│       │   │   │
│       │   │   ├── punjabi/                    [exists — scaffold, not yet wired into engine]
│       │   │   ├── gu/                    [planned V2]  Gujarati lexicons
│       │   │   ├── bn/                    [planned V2]  Bengali lexicons
│       │   │   ├── ta/                    [planned V2]  Tamil lexicons
│       │   │   └── te/                    [planned V2]  Telugu lexicons
│       │   │
│       │   └── gazetteers/
│       │       ├── __init__.py            [exists]
│       │       ├── names.tsv              [exists]   Indian names: key|display|pron_deva (4 rows, seed)
│       │       ├── brands.tsv             [exists]   Indian brands: key|display|pron_deva (4 rows, seed)
│       │       │
│       │       ├── mr/                    [planned V2]
│       │       ├── pa/                    [planned V2]
│       │       └── ...
│       │
│       ├── eval/
│       │   ├── __init__.py                [exists]
│       │   ├── metrics.py                 [exists]   exact_match(), cer(), per_category()
│       │   ├── run_bench.py               [exists]   CLI entry point for benchmark run
│       │   └── bench_mini/
│       │       ├── __init__.py            [exists]
│       │       └── sentences.tsv          [exists]   6 seed rows; grow to 300+ for V1
│       │
│       └── api/                           [exists]
│           ├── cli.py                     [exists]   typer CLI: openhinglish "..."
│           └── server.py                  [exists]   FastAPI POST /normalize; also webui.py
│
├── tests/
│   ├── test_types.py                      [exists]
│   ├── test_data_loader.py                [exists]
│   ├── test_s0.py                         [exists]
│   ├── test_s1.py                         [exists]
│   ├── test_s2.py                         [exists]
│   ├── test_s3.py                         [exists]
│   ├── test_s4.py                         [exists]
│   ├── test_s5.py                         [exists]
│   ├── test_s6.py                         [exists]
│   ├── test_normalize.py                  [exists]   end-to-end normalize() tests
│   ├── test_normalize.py                  [exists]   end-to-end normalize() tests
│   ├── test_metrics.py                    [exists]
│   ├── test_disambiguator.py              [exists]
│   └── test_server.py                     [exists]   skipped when [server] extra absent
├── examples/                              [exists]
│   ├── quickstart.py                  [exists]   4 sentences, per-token table
│   ├── inspect_traces.py              [exists]   per-token trace pretty-print
│   └── README.md                      [exists]
│
├── docs/
│   ├── _BLUEPRINT_BRIEF.md                [exists]   canonical internal brief
│   ├── ARCHITECTURE.md                    [exists]   this companion doc (pipeline + data model)
│   ├── REPO_STRUCTURE.md                  [exists]   this file
│   └── superpowers/
│       ├── specs/
│       │   └── 2026-06-02-openhinglish-normalization-engine-design.md  [exists]
│       └── plans/
│           └── 2026-06-02-openhinglish-normalization-engine.md         [exists]
│
├── pyproject.toml                         [exists]   build config, optional extras, entry points
├── README.md                              [exists]   production README with install, usage, API reference
├── LICENSE                                [exists]   MIT license text
├── CONTRIBUTING.md                        [exists]   how to add lexicon/gazetteer entries; PR flow
├── CODE_OF_CONDUCT.md                     [exists]   Contributor Covenant
├── SECURITY.md                            [exists]   responsible disclosure policy
├── GOVERNANCE.md                          [exists]   decision-making process; maintainer rights
├── DATA_LICENSES.md                       [exists]   per-file license table
└── .gitignore                             [exists]
```

---

## 2. Folder Responsibilities

| Path | Responsibility |
|---|---|
| `src/openhinglish/` | Installable Python package. All runtime code lives here. |
| `src/openhinglish/pipeline/` | The 7 pure-function pipeline stages. One file per stage, named `sN_name.py`. |
| `src/openhinglish/data/` | TSV data files packaged with the library via `importlib.resources`. Community contribution surface. |
| `src/openhinglish/data/lexicons/` | Word-level lookup tables: Roman↔Devanagari, English frequency, English TTS forms, SMS abbreviations. |
| `src/openhinglish/data/lexicons/<lang>/` | (V2) Per-language lexicons following the same TSV schemas as the Hindi root. |
| `src/openhinglish/data/gazetteers/` | Entity gazetteers: personal names and brand names with pronunciation fields. |
| `src/openhinglish/eval/` | Benchmark runner and metrics. `bench_mini/sentences.tsv` is the gold evaluation set. |
| `src/openhinglish/api/` | (Planned) CLI and optional FastAPI HTTP server. Depends only on `__init__.py`. |
| `tests/` | Unit tests. One test file per pipeline stage + integration tests. Never imports internals beyond the public API for integration tests. |
| `examples/` | (Planned) Runnable, self-contained examples for the README and docs. |
| `docs/` | Architecture, repo structure, canonical brief, design specs. No auto-generated API docs. |
| `.github/workflows/` | (Planned) CI (test + lint) and release automation. |
| `.github/ISSUE_TEMPLATE/` | (Planned) Issue templates including a dedicated data-correction template. |
| Root level | Package metadata (`pyproject.toml`), community health files (`LICENSE`, `CONTRIBUTING.md`, etc.), and `DATA_LICENSES.md` (required before first PyPI release). |

---

## 3. Naming Conventions

### Python modules

- All module names are `snake_case`.
- Pipeline stage modules are named exactly `sN_name.py` where `N` is the zero-based stage index
  and `name` is a short snake_case descriptor. The prefix `sN_` makes stage ordering visible in
  directory listings without opening any file.
  - Correct: `s0_preprocess.py`, `s3_translit.py`
  - Incorrect: `preprocess.py`, `stage3_translit.py`, `S3Translit.py`
- Support modules (`types.py`, `data_loader.py`, `disambiguator.py`) use plain snake_case names
  with no numeric prefix.
- Test files follow `pytest` convention: `test_<subject>.py`, where `<subject>` is either the
  module name (e.g. `test_s3.py`) or a logical grouping (e.g. `test_normalize.py` for
  end-to-end tests).

### TSV data files — exact column schemas

All TSV files are UTF-8, tab-delimited, with `#`-prefixed comment lines. Column names are for
documentation only; files do not have header rows in V0.1 (the loader skips comment lines but
does not skip a header row — add `#` before a header if you include one for human readability).

**`lexicons/roman_hindi.tsv`** — Roman-Hinglish to Devanagari mapping

| Col | Index | Type | Example | Description |
|---|---|---|---|---|
| `roman` | 0 | str (lowercase) | `bhai` | Roman-script Hindi word (always stored lowercase). |
| `devanagari` | 1 | str | `भाई` | Canonical Devanagari form (both display and TTS). |
| `frequency` | 2 | int | `8000` | Usage frequency proxy. Used by S1 to compute confidence score. Higher = more common. |

Loader: `load_map(rel_path, key_col=0, val_col=1)` for the Devanagari; `load_map(..., val_col=2)` for frequency.

---

**`lexicons/english_freq.tsv`** — English vocabulary with frequency

| Col | Index | Type | Example | Description |
|---|---|---|---|---|
| `word` | 0 | str (lowercase) | `interview` | English word (always stored lowercase). |
| `frequency` | 1 | int | `5000` | Usage frequency. Used by S1 to compute confidence; used by S2 for close-match lookup. |

Loader: `load_set(rel_path, col=0)` for membership; `load_map(..., key_col=0, val_col=1)` for frequency.

---

**`lexicons/english_tts.tsv`** — English words with Devanagari TTS pronunciations

| Col | Index | Type | Example | Description |
|---|---|---|---|---|
| `word` | 0 | str (lowercase) | `interview` | English word (always stored lowercase). Must also appear in `english_freq.tsv`. |
| `tts_deva` | 1 | str | `इंटरव्यू` | Devanagari phonetic rendering for TTS. Set on `tts_form` only; `display_form` stays Latin. |

Loader: `load_map(rel_path, key_col=0, val_col=1)`.

---

**`lexicons/sms_abbrev.tsv`** — SMS / chat abbreviation expansions

| Col | Index | Type | Example | Description |
|---|---|---|---|---|
| `abbrev` | 0 | str (lowercase) | `intv` | Abbreviated form as typed in chat (always stored lowercase). |
| `expansion` | 1 | str | `interview` | Full expanded form. May be English or Hindi; S2 reclassifies after expansion. |

Loader: `load_map(rel_path, key_col=0, val_col=1)`.

---

**`gazetteers/names.tsv`** — Indian personal names gazetteer

| Col | Index | Type | Example | Description |
|---|---|---|---|---|
| `key` | 0 | str (lowercase) | `shankar` | Lookup key (always stored lowercase; matched case-insensitively). |
| `display` | 1 | str | `Shankar` | Canonical display form (title-cased or as registered). Used for `display_form`. |
| `pron_deva` | 2 | str | `शंकर` | Devanagari pronunciation. Used for `tts_form`. |

Loader: `load_gazetteer(rel_path)` → `dict[str, Entity]` where `Entity(display, pron_deva)`.

---

**`gazetteers/brands.tsv`** — Indian brand names gazetteer

| Col | Index | Type | Example | Description |
|---|---|---|---|---|
| `key` | 0 | str (lowercase) | `paytm` | Lookup key (always stored lowercase). |
| `display` | 1 | str | `Paytm` | Registered brand name (Latin, as the brand uses it). Used for `display_form`. |
| `pron_deva` | 2 | str | `पे-टी-एम` | Devanagari phonetic rendering for TTS. Hyphens between syllables are conventional (they signal prosodic breaks to TTS engines). |

Loader: same as `names.tsv` — `load_gazetteer(rel_path)`.

---

### Branch naming

| Pattern | Use |
|---|---|
| `feat/<short-description>` | New feature or data expansion (e.g. `feat/scale-roman-hindi-lexicon`) |
| `fix/<short-description>` | Bug fix or data correction |
| `eval/<short-description>` | Benchmark additions or metrics changes |
| `docs/<short-description>` | Documentation only |
| `chore/<short-description>` | Maintenance: deps, CI, project config |

### Commit message style

```
<type>: <short imperative summary>  (≤72 chars)

[Optional body: what and why, not how. Wrap at 72 chars.]

[Optional: "Data: adds N rows to roman_hindi.tsv (source: Dakshina CC-BY-SA-4.0)"]
[Optional: "Fixes #NNN"]
```

Types: `feat`, `fix`, `data`, `eval`, `docs`, `test`, `chore`, `refactor`.

The `data:` type is reserved for commits that change only TSV files (no Python changes). This
makes it possible to filter the git log for data-only changes — important for auditing license
provenance.

---

## 4. Where Things Go — Decision Guide

**"I want to add a Hindi word (Roman → Devanagari mapping)."**
→ Append a row to `src/openhinglish/data/lexicons/roman_hindi.tsv` following the schema:
`roman_lowercase<TAB>devanagari<TAB>frequency_int`. Use a commit of type `data:`.
If you derived the entry from Dakshina, note the source in your commit message body.
If you are unsure of the frequency, use `1000` as a conservative default.

**"I want to add an English word's TTS pronunciation."**
→ First add the word to `english_freq.tsv` if it is not already there (column 0: word, column 1: frequency).
Then add the TTS mapping to `english_tts.tsv` (column 0: word, column 1: Devanagari pronunciation).
Both files must be in sync; `english_tts.tsv` only covers words that S1 can classify as ENGLISH.

**"I want to add a new SMS abbreviation."**
→ Append to `src/openhinglish/data/lexicons/sms_abbrev.tsv`: `abbrev_lowercase<TAB>expansion`.
S2 handles reclassification automatically after expansion.

**"I want to add a new brand."**
→ Append to `src/openhinglish/data/gazetteers/brands.tsv`:
`key_lowercase<TAB>DisplayName<TAB>DevanagariPronunciation`.
For the pronunciation, use hyphen-separated syllables (e.g. `ज़ो-मैटो`) to help TTS engines
apply correct prosodic stress. Cite the source (e.g. "brand's own Hindi marketing materials" or
"Wikidata QID: Qxxxxxxx") in the commit body for provenance tracking.

**"I want to fix a wrong transliteration."**
→ Edit the relevant row in `roman_hindi.tsv`. If the word is not in the file (OOV → `akshara_fallback`),
add it with the correct Devanagari and a frequency estimate. File a commit of type `fix: data`.

**"I want to add a new pipeline stage."**
→ Create `src/openhinglish/pipeline/sN_name.py` where `N` is the next sequential index.
The function signature must be `def your_function(tokens: list[Token], config: Config) -> list[Token]`.
Wire it into `__init__.py`'s `normalize()`. Add a corresponding `tests/test_sN.py`.

**"I want to add a new language (V2)."**
→ Create `src/openhinglish/data/lexicons/<iso639-1-code>/` and
`src/openhinglish/data/gazetteers/<iso639-1-code>/` (e.g. `mr/` for Marathi).
Follow the same TSV schemas as the Hindi root. Add the language code to `Config.language` and
update `data_loader.py` to route to the correct subfolder. Do not create new pipeline stage files
for language-specific logic — keep differences in data, not code.

**"I want to add a new evaluation benchmark sentence."**
→ Append to `src/openhinglish/eval/bench_mini/sentences.tsv`:
`input<TAB>ref_display<TAB>ref_tts<TAB>category`.
Human-verify the reference forms before committing. Use one of the existing category labels
(`code-switch`, `roman-hindi`, `brand`, `name`, `numeral`, `acronym`, `date`, `abbrev`, `ambiguous`)
or propose a new category label with justification in your PR description.

**"I want to add a root-level community health file."**
→ Place it at the repo root. `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`,
`GOVERNANCE.md`, and `DATA_LICENSES.md` all live at the root, not inside `docs/`. The `docs/`
folder is for technical documentation; root-level files are for GitHub's community health
detection and for contributors who land on the repo.

**"I want to add a new data source entry."**
→ Edit `DATA_LICENSES.md` (root level). This file is required to be clean of non-commercial
license terms before any PyPI release. Every external data source must have: source name, URL,
license (SPDX identifier), version/commit hash used, and any derived-file paths in this repo.

---

## 5. Challenged Assumptions / Risks

**R1 — Per-language data scaling will break the flat TSV approach.**
Each language needs a Roman transliteration lexicon, a frequency list, a TTS mapping table,
and a gazetteer. At V2 with 6 languages, that is at minimum 24 additional TSV files. The current
`data_loader.py` (using `importlib.resources` with hardcoded relative paths) does not yet support
language-parameterized routing. This must be redesigned before V2 lands; the per-language folder
convention defined in this document anticipates that design but does not implement it.

**R2 — TSV file size limits at V1 lexicon scale.**
The V1 target is 10,000+ rows in `roman_hindi.tsv`. At ~30 bytes/row, that is ~300 KB — well
within Git and pip package limits. However, `lru_cache` on `load_map` loads the entire file into
memory on first access. At V2 scale across 6 languages, memory consumption may become a concern
for environments with tight constraints (e.g. serverless functions, embedded contexts). A lazy
or demand-paged loader may be needed.

**R3 — Monorepo vs split packages for V2+ language packs.**
Keeping all language packs in one monorepo (under `data/lexicons/<lang>/`) simplifies CI and
versioning but means the base `openhinglish` install carries data for all languages. Splitting
into `openhinglish-marathi`, `openhinglish-punjabi`, etc., keeps the base install small but
introduces cross-repo version coordination complexity. This is an unresolved architectural
decision that should be settled before V2 work begins.

**R4 — The JS/WASM port (V4) may require a different repo layout entirely.**
A JS port shares no file format conventions with the Python package (no pyproject.toml, no
importlib.resources, different test infrastructure). Sharing TSV data files between the Python
and JS repos will require a versioned `data/` git submodule or a separate `openhinglish-data`
package. Deferring this decision to V4 is correct, but the current repo layout should not
introduce conventions that are hard to separate later. The `src/openhinglish/data/` path is
nested inside the Python package — extracting it later will require a breaking structural change.

**R5 — No authoritative canonical romanization for Indian names.**
Indian names have no single standard romanization (the same person may spell their name
differently on different ID documents). `names.tsv` keys are stored lowercase but the same name
may appear as `shankar`, `sankar`, `shankara`, all referring to the same entity. The current
schema has one row per canonical spelling. A V1 task is to decide how to handle alternate
spellings (separate rows with same display/pron, or a synonyms column), before the gazetteer
is scaled to 5,000+ entries.

**R6 — `DATA_LICENSES.md` is non-optional but not yet created.**
This file is described in the blueprint as a hard requirement before any PyPI release. Its
absence in V0.1 is acceptable (nothing is released yet), but it must be created and populated
with accurate provenance before the V1 PyPI publication. The risk is that a solo maintainer
under release pressure skips the license audit. It should be treated as a blocking item on the
V1 release checklist, not a nice-to-have.
