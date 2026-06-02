# OpenHinglish — Deployment & Packaging Guide

> Canonical reference for deploying, packaging, and distributing OpenHinglish.
> Keep consistent with `_BLUEPRINT_BRIEF.md`. Last updated: 2026-06-02.

---

## Table of Contents

1. [CPU-Only Strategy](#1-cpu-only-strategy)
2. [Windows-First Support](#2-windows-first-support)
3. [Docker Support](#3-docker-support)
4. [Offline Usage](#4-offline-usage)
5. [Packaging Plan](#5-packaging-plan)
6. [Versioning and Release Policy](#6-versioning-and-release-policy)
7. [Challenged Assumptions / Risks / Open Questions](#7-challenged-assumptions--risks--open-questions)

---

## 1. CPU-Only Strategy

OpenHinglish **never uses a GPU at inference time.** This is a deliberate design commitment, not a resource constraint — and it is a feature:

| Property | Consequence |
|---|---|
| No GPU dependency | Runs on any developer laptop, CI runner, or cheap VPS |
| Deterministic pipeline | Same input → same output, always; no stochastic model sampling |
| Zero model loading time | First call is fast; no CUDA initialization or weight sharding |
| Edge-friendly | Embeds in mobile/desktop apps, Raspberry Pi, IoT gateways |
| Offline-capable | Works without internet on an airplane, in a data center with no egress |
| Cost = $0 at runtime | No GPU instance billing; scales horizontally on commodity CPUs |

**How ML fits in (without breaking the promise).** The `IndicXlit` model and any future learned models are used **offline, at build time only** — to precompute static lookup tables that ship inside the package as TSV data files. Inference never loads a neural network; it does dictionary lookups and deterministic rule execution. The planned `Disambiguator` (V3, Path C) will also be designed to run on CPU: small BiLSTM/MLP or quantized transformer, not a 7B+ LLM.

---

## 2. Windows-First Support

The maintainer develops on **Windows 11 / PowerShell**. All tooling and instructions are validated on that environment first.

### Setting up the development environment (Windows)

```powershell
# 1. Clone
git clone https://github.com/shankarmishra/openhinglish.git
cd openhinglish

# 2. Create a virtual environment (Python 3.11+)
py -3.11 -m venv .venv

# 3. Activate (PowerShell)
.\.venv\Scripts\Activate.ps1

# If script execution is blocked, run once:
#   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 4. Install in editable mode with dev extras
pip install -e ".[dev]"

# 5. Run tests
pytest tests/ -v

# 6. Run the benchmark
.\.venv\Scripts\python -m openhinglish.eval.run_bench
```

> **Important:** Always use `.venv\Scripts\python` (or activate the venv first) rather than the system `python`. The system Python on Windows may be Python 3.9 or 3.10, which are below the 3.11 minimum.

### PowerShell tips

```powershell
# Check which Python the venv uses
.\.venv\Scripts\python --version

# Confirm the package is importable
.\.venv\Scripts\python -c "from openhinglish import normalize; print(normalize('kal h'))"

# Install optional CLI extra (once Task 11 ships)
pip install -e ".[cli]"

# Install optional server extra
pip install -e ".[server]"
```

### Cross-platform notes (Linux / macOS)

The source code has no platform-specific syscalls. The same `normalize()` API works identically on Linux/macOS. Only the virtual-environment activation path differs:

```bash
# Linux / macOS
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/ -v
```

**Known Windows-specific pitfalls** — see also [Section 7](#7-challenged-assumptions--risks--open-questions):

- Console Unicode: Windows default code page (CP 1252) will mangle Devanagari output printed to a terminal. Fix: `chcp 65001` in `cmd.exe`, or use Windows Terminal (UTF-8 by default).
- Path separators in `importlib.resources` / `pathlib`: the codebase uses `pathlib.Path` throughout — no hardcoded forward-slash strings — so this should not be an issue, but check after adding new data-loading code.
- Line endings: `.gitattributes` marks TSV data files as `text eol=lf` to prevent CRLF corruption of tab-delimited content.

---

## 3. Docker Support

A Docker container is the recommended way to run the **optional FastAPI server** (`[server]` extra) in production, or to provide a reproducible environment for CI.

> The CLI and the `normalize()` library do not require Docker. Use the virtualenv workflow for local development.

### Sample Dockerfile (minimal, library + server)

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.11-slim

# --- metadata ---
LABEL org.opencontainers.image.title="openhinglish" \
      org.opencontainers.image.description="Roman-Hinglish normalization engine + REST API" \
      org.opencontainers.image.licenses="MIT"

# --- system deps (none for pure-Python CPU-only package) ---
# Add only if a future optional dep requires a C extension:
# RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# --- copy only what pip needs first (layer cache) ---
COPY pyproject.toml ./
COPY src/ ./src/

# --- install with server extra; no GPU packages ---
RUN pip install --no-cache-dir ".[server]"

# --- non-root user for security ---
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

# --- entry: FastAPI via uvicorn (Task 11 endpoint, planned) ---
CMD ["uvicorn", "openhinglish.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Building and running

```bash
# Build
docker build -t openhinglish:0.1.0 .

# Run the API server
docker run --rm -p 8000:8000 openhinglish:0.1.0

# Quick smoke-test against the running container
curl -X POST http://localhost:8000/normalize \
     -H "Content-Type: application/json" \
     -d '{"text": "bhai kal mera intv h paytm me"}'
```

### Image size goals

| Layer | Target |
|---|---|
| Base (`python:3.11-slim`) | ~130 MB |
| Package + deps (library only) | < 20 MB |
| Package + deps (`[server]` extra) | < 40 MB |
| **Total target** | **< 180 MB** |

These targets are achievable because the package has zero C-extension or ML-framework dependencies at inference time. If a future V3 CPU-only disambiguator adds `onnxruntime` (~50 MB), the total stays well below 250 MB.

### Docker Compose (optional, for local API development)

```yaml
# docker-compose.yml
version: "3.9"
services:
  openhinglish-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
    read_only: true
    tmpfs:
      - /tmp
```

---

## 4. Offline Usage

**OpenHinglish has zero network calls at runtime.** This is enforced by design, not just convention:

- All lexicons (`roman_hindi.tsv`, `sms_abbrev.tsv`, `english_freq.tsv`, `english_tts.tsv`) ship inside the wheel under `src/openhinglish/data/lexicons/`.
- All gazetteers (`names.tsv`, `brands.tsv`) ship inside the wheel under `src/openhinglish/data/gazetteers/`.
- The benchmark sentences (`eval/bench_mini/sentences.tsv`) also ship in the wheel so `run_bench.py` works offline.
- Data is loaded via `importlib.resources` (Python 3.11 `importlib.resources.files()` API) — no `urllib`, `requests`, or `httpx` imports anywhere in the production codepath.

**Verifying offline behavior:**

```python
# Disconnect from the network, then:
from openhinglish import normalize
result = normalize("bhai kal mera intv h paytm me")
print(result.display)   # भाई कल मेरा interview है Paytm में
print(result.tts)       # भाई कल मेरा इंटरव्यू है पे-टी-एम में
# No network traffic should occur.
```

You can confirm with `python -m trace` or a firewall rule blocking the process — no DNS lookups, no HTTP requests.

**Implications for air-gapped / enterprise environments:**

The wheel (plus its zero runtime dependencies) can be copied to a USB drive and installed on an offline machine with `pip install --no-index openhinglish-0.1.0-py3-none-any.whl`. No PyPI access required after that point.

---

## 5. Packaging Plan

### `pyproject.toml` (current state)

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "openhinglish"
version = "0.1.0"
description = "Deterministic, explainable Roman-Hinglish text normalization engine"
readme = "README.md"
license = { text = "MIT" }
requires-python = ">=3.11"
dependencies = []

[project.optional-dependencies]
cli    = ["typer>=0.12"]
server = ["fastapi>=0.110", "uvicorn>=0.29"]
dev    = ["pytest>=8"]

[project.scripts]
openhinglish = "openhinglish.api.cli:app"   # PLANNED — Task 11, not yet implemented

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
openhinglish = [
    "data/lexicons/*.tsv",
    "data/gazetteers/*.tsv",
    "eval/bench_mini/*.tsv",
]
```

### Why `[tool.setuptools.package-data]` matters

Without this block, `setuptools` would build a wheel that contains only `.py` files. The TSV data files are the core of the engine — the wheel is useless without them. The globs above ensure every lexicon, every gazetteer, and the benchmark file are included when you run `python -m build`.

### Build and inspect the wheel

```bash
pip install build
python -m build --wheel

# Verify data files are present in the wheel
python -m zipfile -l dist/openhinglish-0.1.0-py3-none-any.whl | grep "\.tsv"
# Expected output:
# openhinglish/data/lexicons/roman_hindi.tsv
# openhinglish/data/lexicons/sms_abbrev.tsv
# openhinglish/data/lexicons/english_freq.tsv
# openhinglish/data/lexicons/english_tts.tsv
# openhinglish/data/gazetteers/names.tsv
# openhinglish/data/gazetteers/brands.tsv
# openhinglish/eval/bench_mini/sentences.tsv
```

### Optional extras summary

| Extra | Installs | Purpose |
|---|---|---|
| `[cli]` | `typer>=0.12` | `openhinglish "text"` command (Task 11, planned) |
| `[server]` | `fastapi>=0.110`, `uvicorn>=0.29` | REST API server (Task 11, planned) |
| `[dev]` | `pytest>=8` | Run unit tests + benchmark |

Install everything for local development:

```bash
pip install -e ".[cli,server,dev]"
```

### Supported Python versions

Python **3.11, 3.12, 3.13**. The `>=3.11` floor is set because:
- `importlib.resources.files()` (the stable traversable API) became fully stable in 3.11.
- `tomllib` (used by build tools) is in stdlib from 3.11.
- Type-hint features used in `types.py` require 3.11+ (`Self`, `TypeAlias`).

Python 3.9 and 3.10 are **not supported** and will not be back-ported.

### PyPI publication (when V1 is ready)

```bash
# Build source dist + wheel
python -m build

# Upload to TestPyPI first (mandatory dry-run before real PyPI)
pip install twine
twine upload --repository testpypi dist/*

# Install from TestPyPI to verify
pip install --index-url https://test.pypi.org/simple/ openhinglish

# When verified:
twine upload dist/*
```

---

## 6. Versioning and Release Policy

### SemVer

OpenHinglish follows **Semantic Versioning 2.0.0** (`MAJOR.MINOR.PATCH`):

- **MAJOR** bump: breaking change to the public API (see below).
- **MINOR** bump: backward-compatible feature additions (new pipeline stage, new `Config` field with a default, new `Category` value).
- **PATCH** bump: bug fixes, lexicon corrections, documentation updates — no API change.

### What counts as a breaking change

The following changes **require a MAJOR bump**:

| Change | Reason |
|---|---|
| Removing or renaming a field on `NormalizationResult` | Callers destructure this |
| Changing the type of `NormalizationResult.tokens` | Typed integrations break |
| Removing or renaming a field on `Token` | Same |
| Changing `normalize()` signature in a non-additive way | Every caller breaks |
| Removing a value from the `Category` enum | Match/switch exhaustiveness breaks |
| Changing the semantics of `display` or `tts` output for previously-correct tokens | Silent correctness regression in downstream TTS |

The following changes are **NOT breaking** (MINOR or PATCH):

- Adding a new optional keyword argument to `normalize()` with a default.
- Adding a new field to `Token` or `NormalizationResult` with a default value.
- Adding a new `Category` enum member.
- Adding, removing, or correcting lexicon entries (data-only releases, PATCH).
- Improving transliteration quality for previously unknown tokens.

### Data-only releases

When a contributor adds or corrects TSV lexicon/gazetteer entries with no code change, that is a **PATCH** release. Example: `0.1.0 → 0.1.1` for adding 500 new `roman_hindi.tsv` entries from Dakshina. The wheel is rebuilt and re-uploaded to PyPI; the changelog clearly marks it as "data update, no API change."

### Deprecation policy

- Deprecated fields/arguments will be announced in a MINOR release with a `DeprecationWarning`.
- They will be removed in the next MAJOR release, no sooner than **one MINOR release** after the deprecation announcement.
- V0.x releases (current) carry **no deprecation guarantees** — the API may change between any two V0.x releases. This will be prominently noted in the changelog until V1.0.0 ships.

### Release checklist (abbreviated)

1. Update `version` in `pyproject.toml`.
2. Update `CHANGELOG.md` (keep if you add one; document data provenance changes explicitly).
3. Re-verify all data file licenses have not drifted (check upstream repo tags/dates).
4. Run full test suite: `pytest tests/ -v`.
5. Run benchmark: `python -m openhinglish.eval.run_bench` — confirm score does not regress.
6. Build wheel and inspect TSV presence (see Section 5).
7. Upload to TestPyPI, install, smoke-test `normalize()`.
8. Tag `vMAJOR.MINOR.PATCH` in git, push tag.
9. Upload to real PyPI.

---

## 7. Challenged Assumptions / Risks / Open Questions

These are not hypothetical — they are the most likely failure modes for this project. Each doc author and contributor should read this section before shipping anything.

### Data file size in the wheel

**Assumption:** TSV lexicons are small and the wheel stays lean.
**Risk:** Dakshina's Roman-Hindi pairs run to ~90k rows; importing names and brand gazetteers at scale can push a wheel past 50 MB. Large wheels slow CI, bloat `pip install`, and complicate Docker layer caching.
**Mitigation:** Profile wheel size after each bulk lexicon import (`python -m zipfile -l dist/*.whl`). If the wheel exceeds 20 MB, evaluate splitting data into a separate `openhinglish-data` PyPI package that the main package declares as an optional dependency, or use lazy-loading (load a lexicon only on first access, not at import time). Do not merge bulk data drops without measuring.

### Windows Unicode / console pitfalls

**Assumption:** Devanagari output prints correctly on Windows.
**Risk:** The default Windows console code page is CP 1252 (Latin-1). `print(result.display)` will raise `UnicodeEncodeError` or silently corrupt output unless the user is on Windows Terminal or has run `chcp 65001`. This will create a very bad first impression for the most likely early adopters (Indian developers on Windows).
**Mitigation:** The CLI (Task 11) must explicitly set `sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')` before printing. Add a console-encoding smoke-test to CI. Document `chcp 65001` in the README Quickstart under Windows.

### Reproducibility of offline translit tables

**Assumption:** Offline precomputed tables (from IndicXlit) are stable and reproducible.
**Risk:** If the build script that generates `roman_hindi.tsv` from IndicXlit is not pinned to a specific model/commit, two contributors running the script will produce different tables. Floating upstream = non-reproducible data files = silent quality drift.
**Mitigation:** Pin the IndicXlit commit hash and Python environment used to generate each TSV file. Store that hash in a comment in the TSV header or in `DATA_LICENSES.md`. Never auto-regenerate data files in CI without a human review gate.

### Shared-alike contamination (Dakshina)

**Assumption:** Using Dakshina-derived data is safe under CC-BY-SA-4.0.
**Risk:** CC-BY-SA-4.0 requires that derived data files carry the same SA license — NOT the MIT code license. If the wheel is distributed with SA data and the LICENSE file says "MIT" without qualification, that is a license violation. This is existential: it can force a takedown or a full data rewrite.
**Mitigation:** `DATA_LICENSES.md` must clearly declare which TSV files are Dakshina-derived and carry CC-BY-SA-4.0. The PyPI page description must note this. Never combine SA data and MIT code into a single file. Review before every release.

### The entry point target does not exist yet

**Assumption:** `[project.scripts] openhinglish = "openhinglish.api.cli:app"` works.
**Risk:** `openhinglish.api.cli` does not exist (Task 11, deferred). Installing the package with `pip install openhinglish` and running `openhinglish "text"` currently crashes with `ModuleNotFoundError`. The entry point is defined in `pyproject.toml` ahead of the implementation.
**Mitigation:** Do not publish the `[cli]` extra or the bare entry point to PyPI until Task 11 is implemented. Add a test that imports `openhinglish.api.cli` — it will fail until the module exists, keeping the gap visible in CI.

### HiACC dataset license is unverified

**Assumption:** HiACC (Hinglish code-switch eval, 2025) can be used for the benchmark.
**Risk:** The brief explicitly marks HiACC as "UNVERIFIED." Using unverified data in a release benchmark exposes the project to license disputes and undermines credibility.
**Mitigation:** Do not incorporate HiACC into any shipped benchmark until the license is confirmed in writing and documented in `DATA_LICENSES.md`. Use only CC0 / CC-BY data for shipped eval sets until then.
