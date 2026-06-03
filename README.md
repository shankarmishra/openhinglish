# OpenHinglish

**Deterministic, explainable Roman-Hinglish text normalization — the missing pre-processing layer for Indian AI.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange)](docs/MASTER_ROADMAP.md)

---

> **Early-functional — not production-ready.**
> The 7-stage deterministic pipeline is working and **51 unit tests pass**. Lexicons have grown from ~35 seed entries to **~1,300+ entries** (roman_hindi ~460+, plus verb conjugations, function words, English, names including cities, and brands). A **deterministic context disambiguator (V3)** is implemented, resolving structurally ambiguous tokens such as "main road" vs "main ghar" by neighbour context. A **REST API server, web test console, and CLI** are available. A **multilingual scaffold** (Marathi + Punjabi seed lexicons) exists but is not yet wired into the engine. The honest benchmark is **43 gold sentences at ~0.81 exact-match** — real gaps remain in addresses, some verb forms, multi-word abbreviations, and large numbers. **Not production-ready.** The highest-value contribution right now is adding lexicon entries — no coding required.

---

## What it does

Roman-Hinglish — Hindi typed in Latin script, code-switched with English, brand names, abbreviations, and digits — is how hundreds of millions of people actually type. Every downstream AI system (TTS, ASR, chatbots, search) needs clean native-script input. OpenHinglish is the normalization layer that sits in between: CPU-only, zero network calls, fully deterministic, MIT-licensed Python.

Given the input `bhai kal mera intv h paytm me`, OpenHinglish returns **two structured outputs**:

| Output | Purpose | Result |
|---|---|---|
| `display` | Human-readable, mixed-script | `भाई कल मेरा interview है Paytm में` |
| `tts` | Full Devanagari for a TTS engine | `भाई कल मेरा इंटरव्यू है पे-टी-एम में` |

- `display` keeps recognized English words and brand names in Roman script (readers recognize "interview" and "Paytm" faster that way).
- `tts` converts everything to Devanagari — including English words and brand names spelled out phonetically — so a TTS model gets unambiguous native-script input.
- **Word order is preserved exactly.** OpenHinglish does not reorder grammar or insert punctuation (those are translation-level operations, out of V1 scope).

---

## Quick demo

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

# Explainability trace — see exactly which pipeline stage made each decision
for step in result.tokens[3].trace:
    print(step)
# S2: abbrev_expand intv → interview
# S3: english_tts_lookup interview → इंटरव्यू
# S4: skip (not a name/brand token)
```

---

## How audio fits in

OpenHinglish produces **text only** — it does not generate audio. Feed the `tts` string into any Devanagari-input TTS engine to get speech.

```
Roman Hinglish input
        │
        ▼
  ┌─────────────┐
  │ OpenHinglish│  ← this library
  └──────┬──────┘
         │  tts string (clean Devanagari)
         ▼
  ┌──────────────────────────────────┐
  │ TTS model (IndicF5 / CosyVoice2) │  ← separate open model
  └──────────────────────────────────┘
         │
         ▼
      Audio output
```

Good open TTS options that consume clean Devanagari:

| Model | License | Notes |
|---|---|---|
| [AI4Bharat IndicF5](https://github.com/AI4Bharat/IndicF5) | MIT | 11 Indic languages, near-human quality |
| [Indic-Parler-TTS](https://github.com/AI4Bharat/indic-parler-tts) | Apache-2.0 | Fast, multi-speaker |
| [CosyVoice2](https://github.com/FunAudioLLM/CosyVoice) | Apache-2.0 | ~150 ms latency |

A pre-built adapter connecting OpenHinglish to IndicF5 is available as an **experimental optional extra** (`pip install -e ".[tts]"`). It requires a separate model download and is not part of the core library. Audio generation is never performed by the core engine.

---

## Install

### From source (recommended now — PyPI coming in V1)

```bash
git clone https://github.com/shankarmishra/openhinglish.git
cd openhinglish
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
```

**Linux / macOS:**
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Requires **Python 3.11 or newer**. No GPU, no CUDA, no external model downloads.

### From PyPI (coming soon)

```bash
pip install openhinglish   # not yet available — V1 milestone
```

---

## Usage

### Python API

```python
from openhinglish import normalize, Config

# Basic
result = normalize("yaar mujhe 2 din me reply karo")
print(result.display)   # यार मुझे 2 दिन में reply करो
print(result.tts)       # यार मुझे दो दिन में रिप्लाई करो

# With config: spell numbers as Hindi words
result = normalize("call me at 5 pm", config=Config(number_words_lang="hi"))
print(result.tts)       # कॉल मी ऐट पाँच पीएम

# Structured result
print(result.confidence)          # aggregate confidence (float, 0–1)
print(len(result.tokens))         # one Token per surface word/symbol
print(result.tokens[0].category)  # Category.HINDI_ROMAN, Category.ENGLISH, etc.
```

### CLI

```bash
python -m openhinglish.api.cli "bhai kal mera intv h paytm me"
```

### REST API server

```bash
python -m openhinglish.api.server
# POST /normalize  {"text": "bhai kal mera intv h"}
# GET  /health
```

The server exposes a FastAPI endpoint at `http://127.0.0.1:8000`. It returns the same structured JSON (`display`, `tts`, `confidence`, per-token detail) as the Python API.

### Web test console

```bash
python -m openhinglish.api.webui
# Open http://127.0.0.1:8000 in your browser
```

The web UI (zero dependencies beyond the core install) lets you type arbitrary Hinglish and inspect both outputs, per-token confidence, and explainability traces — no code required.

---

## Features

- **Deterministic** — same input always produces the same output; no sampling, no randomness, no model calls.
- **Explainable traces** — every `Token` carries a `trace[]` list showing which pipeline stage made which decision and why. Debug a wrong transliteration by reading the trace, not running ablations.
- **N-best alternatives + confidence** — ambiguous tokens expose their top-k alternatives with individual confidence scores.
- **CPU-only, zero network calls** — runs on any laptop, CI runner, or edge device; no GPU required.
- **Community-fixable lexicons** — all vocabulary is editable TSV files. Fixing a wrong transliteration or adding a brand name is a one-line PR, no retraining required.
- **Two structured outputs** — `display` and `tts` are first-class citizens, not post-processing hacks.
- **TTS-agnostic** — feeds into IndicF5, Indic-Parler-TTS, CosyVoice2, or any Devanagari-input TTS.
- **MIT licensed (code)** — use freely in commercial products; see data license note below.

---

## Why it exists

AI4Bharat IndicF5 (MIT), Indic-Parler-TTS (Apache-2.0), and CosyVoice2 (Apache-2.0) have largely solved acoustic modeling for native-script Indic text. The unfilled gap is the step before: **turning Roman-script Hinglish into the clean Devanagari those engines require**.

Every Indian AI team currently re-implements this normalization layer from scratch — one writes a regex for "paytm", another hard-codes "h" → "है", a third builds a names list that never gets shared. The result is duplicated work, no shared test suite, and no community contribution path.

OpenHinglish is designed to be the shared library — like `chardet` or `phonenumbers` — that a community can maintain and extend via plain TSV data files, without retraining any model.

---

## Roadmap

Full details: [docs/MASTER_ROADMAP.md](docs/MASTER_ROADMAP.md)

| Version | Theme | Status |
|---|---|---|
| **V0.1 "Foundation"** | Deterministic pipeline, seed lexicons, n-best + traces | **Done** |
| **V1 "Usable Hindi+English"** | ~1,300+ entries now, target 10k+ (Dakshina); 43-sentence benchmark at ~0.81 EM | **In progress** |
| **V2 "Multilingual"** | Marathi + Punjabi seed lexicons exist; not wired into engine yet | **Scaffold only** |
| **V3 "Context-aware"** | Deterministic neighbour-context disambiguator done; learned ML layer not started | **Started** |
| **V4 "Ecosystem"** | REST API + web UI + CLI + experimental IndicF5 adapter done; hosted API + JS port not started | **Partial** |
| **V5 "The Standard"** | 43-sentence honest benchmark done; public leaderboard + community governance not started | **Started** |

---

## Contributing

**Adding lexicon entries is the most useful thing you can do right now.** The pipeline is built; coverage is limited by vocabulary data alone.

### Adding a word, name, or brand

Lexicons are plain TSV files in `src/openhinglish/data/`. Each file has a header row explaining columns. No code change required.

| File | What to add |
|---|---|
| `data/lexicons/roman_hindi.tsv` | Roman Hinglish word → Devanagari display → Devanagari TTS |
| `data/lexicons/sms_abbrev.tsv` | SMS/chat abbreviation → expanded form |
| `data/lexicons/english_tts.tsv` | English word → Devanagari phonetic rendering |
| `data/gazetteers/names.tsv` | Indian personal name (Roman) → Devanagari canonical |
| `data/gazetteers/brands.tsv` | Brand name → display form → TTS spelling-out |

**Steps for a lexicon PR:**

1. Fork and branch: `git checkout -b add-lexicon-<word-or-source>`
2. Edit the relevant TSV. Follow the column format in the header.
3. Add a sentence to `eval/bench_mini/sentences.tsv` exercising the new entry.
4. Run `pytest tests/ -v` — all 51 tests must pass.
5. Open a PR describing the data source and its license.

**License note for data:** if contributing data derived from Dakshina (CC-BY-SA-4.0), label it clearly in the PR. SA data carries the SA license, not MIT. See [DATA_LICENSES.md](DATA_LICENSES.md).

### Code contributions

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a code PR. Key constraints:
- Every pipeline stage must be a pure function `(tokens, config) -> tokens`.
- No network calls in the production code path.
- No GPU dependencies, ever.
- Changes to `normalize()`, `NormalizationResult`, or `Token` must be discussed in an issue first — these are the stable API surface.

---

## License

**Code:** MIT — see [LICENSE](LICENSE).

**Data files** (`src/openhinglish/data/**/*.tsv`) carry their own source licenses:

- Dakshina-derived entries: **CC-BY-SA-4.0** (share-alike — derived data must carry the same license).
- Wikidata-derived entries (names, brands): **CC0**.
- Other sources: documented per-file in [DATA_LICENSES.md](DATA_LICENSES.md).

Before using this package in a commercial product, read `DATA_LICENSES.md` to understand which data files apply to your use case. The CC-BY-SA-4.0 share-alike requirement applies to the data, not to the Python code.

---

## Documentation

| Document | Description |
|---|---|
| [docs/MASTER_ROADMAP.md](docs/MASTER_ROADMAP.md) | Full V0.1→V5 roadmap with deliverables and exit criteria |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | 7-stage pipeline design and data model |
| [docs/BENCHMARK.md](docs/BENCHMARK.md) | Evaluation methodology and bench-mini results |
| [docs/DATASETS.md](docs/DATASETS.md) | Data sources, provenance, and license tracking |
| [docs/ECOSYSTEM_STRATEGY.md](docs/ECOSYSTEM_STRATEGY.md) | TTS/ASR integration strategy |
| [docs/GOVERNANCE.md](docs/GOVERNANCE.md) | Project governance and decision-making process |
| [docs/REPO_STRUCTURE.md](docs/REPO_STRUCTURE.md) | Directory layout explained |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guide |

---

_OpenHinglish is a zero-budget open-source project. Star the repo, open an issue, or submit a lexicon PR — every entry expands real-world coverage._
