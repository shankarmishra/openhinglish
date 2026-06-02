# OpenHinglish

**Deterministic, explainable Roman-Hinglish text normalization for TTS, ASR, search, and chatbots.**

Roman-script Hinglish code-switching is everywhere — WhatsApp, social media, customer support — and every downstream AI system (TTS, ASR, search) needs it in native Devanagari. OpenHinglish is the missing pre-processing layer: a pure-Python, CPU-only engine that turns informal Hinglish text into two structured outputs (human-readable `display` and TTS-ready `tts`) with per-token confidence, n-best alternatives, and full explainability traces.

---

> **Status: Early / Foundation (V0.1)**
>
> The 7-stage deterministic pipeline is functionally complete and 32 unit tests pass. Seed lexicons are tiny (~13 Roman-Hindi words, 6 SMS abbreviations, 4 names, 4 brands). Real-world coverage on arbitrary Hinglish is currently near-zero. **This is a foundation / skeleton, not yet a usable product.** The hardest work — scaling lexicons to 10k+ entries, growing the benchmark to 300+ human-verified sentences, and publishing to PyPI — is the V1 milestone ahead of us. Contributions to lexicons and benchmark sentences are the highest-value thing you can do right now.

---

## Why two outputs?

Most normalization tools produce a single string. OpenHinglish produces two, because `display` and `tts` have different audiences and different rules:

| Output | Audience | Example |
|---|---|---|
| `display` | Human reader on a screen | `भाई कल मेरा interview है Paytm में` |
| `tts` | Text-to-speech engine (phoneme input) | `भाई कल मेरा इंटरव्यू है पे-टी-एम में` |

- **display** keeps recognized English words in Roman script (readers recognize "interview" and "Paytm" faster in their familiar script).
- **tts** converts everything to Devanagari, including English words and brand names spelled out phonetically, so a TTS model gets unambiguous native-script input.

Neither is just "transliteration." Both preserve the original word order exactly — OpenHinglish does not reorder grammar (that is translation, which is out of scope).

---

## The demo

```python
from openhinglish import normalize

result = normalize("bhai kal mera intv h paytm me")

print(result.display)
# भाई कल मेरा interview है Paytm में

print(result.tts)
# भाई कल मेरा इंटरव्यू है पे-टी-एम में

print(result.confidence)
# 0.87  (example; actual value depends on lexicon coverage)

# Per-token detail
for tok in result.tokens:
    print(f"{tok.surface:12} → display={tok.display_form:20} tts={tok.tts_form:20} conf={tok.confidence:.2f}")
# bhai         → display=भाई                  tts=भाई                  conf=0.95
# kal          → display=कल                   tts=कल                   conf=0.92
# mera         → display=मेरा                 tts=मेरा                 conf=0.93
# intv         → display=interview            tts=इंटरव्यू             conf=0.81
# h            → display=है                   tts=है                   conf=0.90
# paytm        → display=Paytm               tts=पे-टी-एम             conf=0.78
# me           → display=में                  tts=में                   conf=0.88

# N-best alternatives for an ambiguous token
for alt in result.tokens[4].alternatives:
    print(alt.form, alt.confidence)
# है   0.90
# हे   0.62

# Explainability trace
for step in result.tokens[3].trace:
    print(step)
# S2: abbrev_expand intv → interview
# S3: english_tts_lookup interview → इंटरव्यू
# S4: skip (not a name/brand token)
```

---

## Install

### From PyPI (once V1 publishes)

```bash
pip install openhinglish
```

Optional extras:

```bash
pip install "openhinglish[cli]"       # adds the openhinglish CLI command
pip install "openhinglish[server]"    # adds the FastAPI REST server
pip install "openhinglish[dev]"       # adds pytest for running tests
```

### From source (current recommended method)

```bash
git clone https://github.com/shankarmishra/openhinglish.git
cd openhinglish

# Windows (PowerShell)
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"

# Linux / macOS
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Requires **Python 3.11 or newer**. No GPU, no CUDA, no external model downloads.

---

## Quickstart

### Python API

```python
from openhinglish import normalize, Config

# Basic usage
result = normalize("yaar mujhe 2 din me reply karo")
print(result.display)   # यार मुझे 2 दिन में reply करो
print(result.tts)       # यार मुझे दो दिन में रिप्लाई करो

# With config: spell numbers as words in Hindi
result = normalize("call me at 5 pm", config=Config(number_words_lang="hi"))
print(result.tts)       # कॉल मी ऐट पाँच पीएम

# Inspect the full structured result
print(result.confidence)           # aggregate confidence (float, 0–1)
print(len(result.tokens))          # one Token per surface word/symbol
print(result.tokens[0].category)   # Category.HINDI_ROMAN, Category.ENGLISH, etc.
```

### CLI (planned — Task 11, not yet implemented)

```
# This command is PLANNED. It does not work yet.
openhinglish "bhai kal mera intv h paytm me"
```

When Task 11 ships, the CLI will accept a string or a file path, support `--format json|plain`, and respect the same `Config` fields via flags. Follow [Task 11 in the issue tracker] for progress.

---

## Features

- **Deterministic** — same input always produces the same output; no sampling, no randomness.
- **Explainable traces** — every `Token` carries a `trace[]` list showing which stage made which decision and why. Debugging a bad transliteration means reading the trace, not running ablations.
- **N-best + confidence** — ambiguous tokens expose their top-k alternatives with individual confidence scores; callers can use or discard them.
- **CPU-only, zero network calls** — runs on any laptop, CI runner, or edge device; no GPU, no internet access required at inference.
- **MIT licensed (code)** — use freely in commercial products; see the data license note below.
- **Community-fixable lexicons** — all vocabulary is stored as editable TSV files; fixing a wrong transliteration or adding a brand name is a one-line PR, no retraining required.
- **Two structured outputs** — `display` (human-readable, mixed script) and `tts` (full Devanagari for TTS engines) are first-class outputs, not post-processing hacks.
- **TTS-agnostic** — output feeds directly into AI4Bharat IndicF5, Indic-Parler-TTS, CosyVoice2, or any other Devanagari-input TTS; OpenHinglish does not do acoustic modeling.
- **Gold evaluation set ships with the engine** — `eval/bench_mini/sentences.tsv` provides a 6-sentence baseline benchmark (V0.1); growing this to 300+ human-verified sentences is the core V1 goal.

---

## Roadmap

Full details: [docs/MASTER_ROADMAP.md](MASTER_ROADMAP.md) _(planned — not yet written)_

| Version | Theme | Status |
|---|---|---|
| **V0.1 "Foundation"** | Deterministic pipeline, seed lexicons, n-best + traces, 6-row benchmark, CLI/API skeleton | **Done (current)** |
| **V1 "Usable Hindi+English"** | 10k+ Roman-Hindi lexicon (Dakshina), 5k+ names, 500+ brands, 300+ bench sentences, PyPI publish | In progress |
| **V2 "Multilingual frontends"** | Marathi, Punjabi, Gujarati, Bengali, Tamil, Telugu — same pipeline, per-language translit + lexicons | Planned |
| **V3 "Context-aware (Path C)"** | Pluggable learned `Disambiguator` (CPU-friendly), NER for names, punctuation restoration | Planned |
| **V4 "Ecosystem & integrations"** | TTS adapters (IndicF5, CosyVoice2), ASR post-processing, hosted API, JS/WASM port | Planned |
| **V5 "The standard"** | IndianTTSBench full public benchmark + leaderboard as community standard; foundation governance | Planned |

---

## Contributing

Contributions to **lexicons and benchmark sentences** are the highest-value work right now — the pipeline is built, but coverage is near-zero without vocabulary data.

### Adding a word, name, or brand

The lexicons are plain TSV files inside `src/openhinglish/data/`. Each file has a header row explaining the columns. No code change required.

| File | What to add |
|---|---|
| `data/lexicons/roman_hindi.tsv` | Roman-script Hinglish word → Devanagari display form → Devanagari TTS form |
| `data/lexicons/sms_abbrev.tsv` | SMS/chat abbreviation → expanded English or Hindi form |
| `data/lexicons/english_freq.tsv` | Common English words with frequency rank |
| `data/lexicons/english_tts.tsv` | English word → Devanagari phonetic rendering for TTS |
| `data/gazetteers/names.tsv` | Indian personal name (Roman) → Devanagari canonical form |
| `data/gazetteers/brands.tsv` | Brand/product name → display form → TTS spelling-out |

Steps for a lexicon PR:

1. Fork the repo and create a branch: `git checkout -b add-lexicon-<word-or-source>`.
2. Edit the relevant TSV file. Follow the column format in the header.
3. Add a sentence to `eval/bench_mini/sentences.tsv` that exercises the new entry (if the entry is non-trivial).
4. Run `pytest tests/ -v` — all 32 tests must still pass.
5. Run `python -m openhinglish.eval.run_bench` — benchmark score must not decrease.
6. Open a PR describing the source of the data and its license.

**License note for data contributions:** if you are contributing data derived from Dakshina (CC-BY-SA-4.0), label it clearly in the PR. SA data can be included in the TSV files, but it carries the SA license, not MIT. See [DATA_LICENSES.md](DATA_LICENSES.md) _(planned)_.

### Adding benchmark sentences

A good benchmark sentence is:
- Naturally occurring Hinglish (not synthetic).
- Unambiguous — the correct `display` and `tts` outputs can be agreed on by two native speakers.
- Annotated with its source and whether the source is CC0 or CC-BY.

Add rows to `eval/bench_mini/sentences.tsv` following the existing format.

### Code contributions

Read [CONTRIBUTING.md](CONTRIBUTING.md) _(planned)_ before opening a code PR. Key constraints:
- Every pipeline stage must remain a pure function `(tokens, config) -> tokens`.
- No network calls in the production codepath.
- No GPU dependencies, ever.
- All changes to `normalize()`, `NormalizationResult`, or `Token` must be discussed in an issue first — these are the stable API surface.

### Governance

See [GOVERNANCE.md](GOVERNANCE.md) _(planned)_ for decision-making process, maintainer responsibilities, and how to become a committer.

---

## License

**Code:** MIT — see [LICENSE](../LICENSE).

**Data files** (`src/openhinglish/data/**/*.tsv`) carry their own source licenses, which vary by file:

- Dakshina-derived entries: **CC-BY-SA-4.0** (share-alike — derived data must carry the same license).
- Wikidata-derived entries (names, brands): **CC0**.
- Other sources: documented per-file in [DATA_LICENSES.md](DATA_LICENSES.md) _(planned)_.

**Before using this package in a commercial product**, read `DATA_LICENSES.md` to understand which data files apply to your use case. The CC-BY-SA-4.0 share-alike requirement applies to the data, not to the Python code.

If a data file's license is incompatible with your use case, the relevant rows can be identified by their source column in the TSV and excluded or replaced. The engine will continue to work — just with reduced coverage for those entries.

---

_OpenHinglish is a solo, zero-budget open-source project. Star the repo, open an issue, or submit a lexicon PR — every contribution accelerates the path to V1._
