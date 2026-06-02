# OpenHinglish — Roman-Hinglish Normalization Engine (V1)
## Design Specification

- **Status:** Approved (design), pending implementation plan
- **Date:** 2026-06-02
- **Owner:** Shankar Mishra
- **License (target):** MIT
- **Slice:** #1 of the OpenHinglish platform (Normalization Engine). Slices #2 (Names/Brands DB) and #3 (IndianTTSBench) follow.

---

## 1. Problem & Goal

Every Indian voice/NLP product (TTS, ASR, voice bots, chatbots, search, translation) must first
understand messy real-world Indian text. The same intent appears in many forms:

```
kal interview h
kal interview hai
kal intervew h
kl interview h
kal intv h
```

No open-source system reliably turns informal Roman-Hinglish into clean, pronounceable,
structured text while handling spelling variation, code-switching, names, brands, numerals,
dates and abbreviations.

**Goal of V1:** a deterministic, explainable, CPU-only, community-fixable engine that converts
informal Roman-Hinglish into a structured result carrying both a human-readable `display` form
and a TTS-ready `tts` form, with confidence scores and n-best alternatives.

**Worked example**

```
input :  "bhai kal mera intv h paytm me"
display: "भाई कल मेरा interview है Paytm में"
tts    : "भाई कल मेरा इंटरव्यू है पे-टी-एम में"
```

(Note: punctuation/capitalization insertion — e.g. the comma in "भाई, कल…" — is explicitly
deferred to V1.1; see §10.)

### 1.1 Non-negotiable principles (locked with user)
1. Text-first and TTS-agnostic. The engine never depends on any specific TTS model.
2. Output is never a single string. `confidence` and `alternatives` (n-best) are first-class.
3. `display_form` and `tts_form` are separate outputs from day one.
4. Every normalization decision is traceable and explainable (`trace` per token).
5. Community contributors can fix many errors by editing rules/lexicons/mappings — no retraining.
6. A gold evaluation set ships *inside* V1. If we cannot measure accuracy, we cannot claim improvement.
7. Deterministic, CPU-only, no GPU at inference, no training pipeline in V1.

### 1.2 Architecture commitment
**Path A → C.** V1 is a deterministic pipeline (Path A), architected with the seams
(confidence, n-best, a pluggable `Disambiguator` interface) so a learned disambiguator can be
added in V1.1 (Path C) without a rewrite. Any ML (e.g. IndicXlit) is used **offline at build
time** to generate static lookup tables/data — never at inference.

---

## 2. Hidden assumptions addressed (design rationale)

- **A — "one correct normalization" is false.** `kal` (yesterday/tomorrow), `main` (English/मैं),
  `to` (English/तो) are context-dependent. → n-best + confidence are mandatory; we never force a
  single answer in early stages.
- **B — spelling-correction and transliteration interfere.** `intervew` must be recognized as
  misspelled *English* and protected from transliteration. → language-ID precedes both; spelling
  normalization is conservative and reversible (original kept as alternative).
- **C — names/brands are not a clean override.** `Aman`(name)/`aman`(peace), `Karan`/`karan`. →
  casing/context guard before override; collisions keep both candidates.
- **D — Devanagari output is not automatically better for TTS.** A Devanagari-native TTS may not
  voice Latin `Paytm`. → two outputs: `display` (Paytm stays Latin) and `tts` (पे-टी-एम).
- **E — cannot claim success without a labeled set.** → `IndianTTSBench-mini` is part of V1.
- **F — value must not hinge on an untested TTS.** → engine is measured at the text level and is
  useful regardless of downstream model.

---

## 3. Pipeline Architecture

A linear pipeline of 7 stages. Each stage is a pure function `Stage(tokens, config) -> tokens`
operating on one growing annotation object (never a re-parsed string), so each stage is unit-testable
and replaceable in isolation.

```
raw text
 └─ S0 Preprocess/Tokenize
     └─ S1 Classify (language-ID, ranked candidates)
         └─ S2 Spell-normalize (Roman side, conservative)
             └─ S3 Transliterate (Roman-Hindi → Devanagari, lookup-first)
                 └─ S4 Names/Brands (NER-lite + override)
                     └─ S5 Numerals/Dates/Time/Abbrev (rule-based)
                         └─ S6 Assemble → NormalizationResult
```

### Stage specs

- **S0 Preprocess/Tokenize:** Unicode NFC; tokenize preserving punctuation, emoji, URLs, digits;
  tag token *shape* (all-Latin / all-Devanagari / digits / mixed). Already-Devanagari tokens pass
  through unchanged.
- **S1 Classify (language-ID):** lexicon-first (English frequency list, Roman-Hindi lexicon, names
  gazetteer, brands gazetteer, abbreviation list) + casing/shape priors. Emits a **ranked candidate
  set per token** (source of n-best). Collisions (`main`, `to`, `kal`) keep all candidates with
  frequency-prior scores; no forced choice here.
- **S2 Spell-normalize (Roman, conservative):**
  - (a) curated SMS/abbreviation lexicon (`h→hai`, `intv→interview`, `pls→please`) — deterministic;
  - (b) genuine typos via weighted (phonetic-aware) edit distance to a canonical vocab with a
    frequency prior.
  - Never rewrites a confident exact match. Original always retained as an alternative.
- **S3 Transliterate (Roman-Hindi → Devanagari):** lookup-first against a precomputed Roman→Devanagari
  table (top-N words) generated offline from IndicXlit/Dakshina; rule-based akshara fallback for OOV;
  carries n-best.
- **S4 Names/Brands:** gazetteer match + casing/context guard to prevent over-firing. Owns `tts_form`
  for entities via a `pronunciation` field (`Paytm→पे-टी-एम`, `Shankar→शंकर`). Seam where Slice #2
  (full names DB) later plugs in; V1 ships a seed gazetteer.
- **S5 Numerals/Dates/Time/Abbrev:** rule-based, config-driven (`4 PM`→ tts `चार बजे` or `4 PM` per
  config; `RBI`→`आर बी आई`; phone/currency/date grammars); n-best where ambiguous.
- **S6 Assemble:** rebuild `display` + `tts`; normalize spacing and existing punctuation; sentence-final
  `।`/`.` handling; compute aggregate confidence.

---

## 4. Core Data Contract

```text
NormalizationResult:
  input: str
  display: str          # human-readable; English/brands stay Latin
  tts: str              # fully resolved for a Devanagari-native TTS
  confidence: float     # aggregate
  tokens: Token[]

Token:
  surface: str                  # original substring
  span: (start, end)            # offsets into input → traceability
  category: enum                # HINDI_ROMAN | HINDI_DEVA | ENGLISH | NAME | BRAND |
                                # NUMBER | DATE | TIME | ACRONYM | PUNCT | EMOJI | URL | UNKNOWN
  display_form: str
  tts_form: str
  confidence: float
  alternatives: Candidate[]     # n-best: {category, display_form, tts_form, score}
  trace: str[]                  # which stage/rule/lexicon fired → explainability

Candidate:
  category: enum
  display_form: str
  tts_form: str
  score: float
```

Invariants:
- `display_form != tts_form` is permitted and expected (Assumption D).
- Every token carries at least one `trace` entry per stage that touched it.
- `alternatives` is sorted by descending `score`; rank-1 is the chosen form.

---

## 5. Data Sources (free / license-checked)

| Need | Source | License | Notes |
|---|---|---|---|
| Roman↔Devanagari + romanization variants | Google Dakshina | verify (CC-BY-SA family) | canonical romanized-Indic resource |
| Offline transliteration (build-time table) | AI4Bharat IndicXlit | open | used offline only |
| English frequency wordlist | SCOWL / permissive freq list | permissive | language-ID + spell |
| Indian names gazetteer | Census name lists + Wikidata | CC0 | seed for V1 |
| Brands gazetteer | Wikidata companies + curated seed | CC0 + ours | seed for V1 |
| SMS/abbreviation lexicon | curated seed | MIT (ours) | community-extensible |

- Lexicons are editable data files (YAML/TSV), not code → contributors PR fixes without touching Python.
- Every external source recorded in `DATA_LICENSES.md`.
- Nothing under CC-BY-NC (or any non-commercial term) may enter the released package. Pin source
  commit hashes; re-verify licenses before each release (licenses have drifted in this ecosystem).
- **Code vs data license split (license-trap guard):** the Python package is MIT, but **data files
  derived from a ShareAlike source (e.g. Dakshina, if confirmed CC-BY-SA-4.0) must be released under
  that same ShareAlike license, not MIT.** Keep derived data in clearly-licensed subfolders with their
  own `LICENSE` and attribution; never relabel CC-BY-SA-derived tables as MIT. **Action before release:**
  confirm Dakshina's exact license; if it is ShareAlike and that is undesirable, regenerate the
  affected tables from a non-copyleft source (e.g. IndicXlit output + CC0/permissive wordlists) so the
  shipped data can be permissively licensed.

---

## 6. Evaluation — `IndianTTSBench-mini` (ships in V1)

- 300–500 hand-verified sentences spanning: names, brand-mixing, code-switch, numerals, dates,
  addresses, SMS/abbreviations, and ambiguity traps (`main`/`to`/`kal`).
- Drafts may be bootstrapped by an offline LLM, then **human-verified** (verification is what makes
  it gold).
- Metrics, reported per category:
  - token-classification accuracy
  - transliteration CER / WER vs reference
  - normalization exact-match @ `display` and @ `tts`
  - name/brand pronunciation accuracy
  - **n-best coverage** (is the correct answer in top-k, even when rank-1 is wrong?)
- This is the seed of Slice #3 and the only mechanism that makes "V1 works" falsifiable.

---

## 7. Public API, Packaging, Repo

- Pure-Python pip package **`openhinglish`** (MIT). Core API:

```python
from openhinglish import normalize, Config

result = normalize("bhai kal mera intv h paytm me", config=Config())
result.display  # "भाई कल मेरा interview है Paytm में"
result.tts      # "भाई कल मेरा इंटरव्यू है पे-टी-एम में"
result.tokens[0].trace  # ["S1: lexicon=roman_hindi", "S3: translit lookup bhai→भाई"]
```

- CLI: `openhinglish "bhai kal mera intv h paytm me"`
- Optional thin FastAPI server (`POST /normalize`) for HTTP consumers (ASR/chatbots/search).

Repository layout:

```
openhinglish/
  pipeline/
    s0_preprocess.py  s1_classify.py  s2_spellnorm.py  s3_translit.py
    s4_names_brands.py  s5_numerals.py  s6_assemble.py
    types.py          # NormalizationResult, Token, Candidate, Config
    disambiguator.py  # pluggable interface (no-op in V1; learned impl in V1.1)
  data/
    lexicons/         # *.yaml / *.tsv  (english_freq, roman_hindi, sms_abbrev)
    translit_table/   # precomputed Roman→Devanagari lookup
    gazetteers/       # names.tsv, brands.tsv  (with pronunciation field)
  eval/
    bench_mini/       # IndianTTSBench-mini sentences + references
    metrics.py
  api/
    cli.py  server.py
  DATA_LICENSES.md
  README.md
  CONTRIBUTING.md     # how to add a lexicon/gazetteer entry
```

---

## 8. Component boundaries (isolation & testability)

- Each stage `Sx` depends only on the annotation object + `Config` + its own data files. No stage
  reaches across to another stage's internals.
- `Disambiguator` is an interface consumed by S1/S2/S4 for tie-breaking; V1 ships a deterministic
  no-op (rank by frequency prior). V1.1 supplies a learned implementation behind the same interface.
- Data files are the contributor surface; code is the maintainer surface. The two evolve independently.

---

## 9. Error handling & edge cases

- **Unknown tokens:** category `UNKNOWN`, `display_form = tts_form = surface`, low confidence,
  `trace` records the miss. Never crash; always pass text through.
- **Mixed-script tokens** (e.g. `WhatsApp` inside Devanagari run): treated as ENGLISH/BRAND candidate;
  retained verbatim in `display`, given a pronunciation in `tts` if gazetteer-known, else
  passed through.
- **Empty/whitespace/emoji/URL:** preserved verbatim, categorized, excluded from transliteration.
- **Over-correction guard:** S2 must not change a token whose exact form is in a trusted lexicon.
- **Determinism:** identical input + identical data files + identical config ⇒ identical output.

---

## 10. Scope boundaries

### In scope (V1)
Deterministic pipeline; token classification; conservative spell-normalization; transliteration
(lookup + rule fallback); names/brands seed gazetteer; numerals/dates/time/abbreviations; confidence
scoring; n-best; `display`/`tts` split; explainability traces; `IndianTTSBench-mini`; Python API +
CLI + optional HTTP server; Hindi + English only.

### Out of scope (deferred)
1. **Punctuation/capitalization insertion** (restoration) → V1.1 (learned layer). V1 only
   preserves/normalizes existing punctuation + sentence-final marks. Consequence: V1 output for the
   worked example omits the inserted comma.
2. **Learned disambiguator / context-aware resolution** → V1.1 (behind the `Disambiguator` interface).
3. **Languages beyond Hindi + English** (Marathi/Punjabi/Gujarati/Urdu/…) → V2.
4. **Audio / TTS integration** → separate `openhinglish-tts` adapter repo, later.
5. **Emotion/prosody tags** → out of scope.

### V1.1 roadmap (forward reference, not built now)
Pluggable learned disambiguator; context-aware resolution for ambiguous tokens; NER improvements;
hybrid scoring; punctuation/capitalization restoration.

---

## 11. Success criteria (V1 "done")

1. `normalize()` returns the full structured contract (§4) for arbitrary Roman-Hinglish input
   without crashing.
2. `display`/`tts` split correct on the worked example and the bench set.
3. `IndianTTSBench-mini` exists (≥300 verified sentences) and `metrics.py` reports per-category numbers.
4. Lexicons/gazetteers are editable data files with a documented contribution path.
5. Pure-Python, CPU-only, pip-installable, MIT, with `DATA_LICENSES.md` clean of non-commercial terms.
6. Every token in any output carries a non-empty `trace`.
```
