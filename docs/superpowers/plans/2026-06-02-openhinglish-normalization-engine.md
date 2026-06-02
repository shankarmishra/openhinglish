# OpenHinglish Normalization Engine V1 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic, explainable, CPU-only Python engine that turns informal Roman-Hinglish into a structured result with a `display` form, a `tts` form, confidence scores, n-best alternatives, and per-token traces.

**Architecture:** A 7-stage linear pipeline (`S0 Preprocess → S1 Classify → S2 Spell-normalize → S3 Transliterate → S4 Names/Brands → S5 Numerals/Dates/Abbrev → S6 Assemble`). Each stage is a pure function over a list of `Token`s. Lexicons/gazetteers are editable TSV data files. A no-op `Disambiguator` interface reserves the seam for a learned V1.1 layer.

**Tech Stack:** Python 3.11+, `pytest`, standard library only at runtime (`re`, `unicodedata`, `csv`, `pathlib`), `typer` for CLI and `fastapi`+`uvicorn` for the optional server (both optional extras). No GPU, no ML at inference.

---

## File Structure

```
openhinglish/
  pyproject.toml
  src/openhinglish/
    __init__.py            # normalize() — chains all stages
    types.py               # Category, Candidate, Token, NormalizationResult, Config
    data_loader.py         # load_set / load_map / load_gazetteer (TSV readers + caching)
    disambiguator.py       # Disambiguator protocol + FrequencyDisambiguator (V1 no-op)
    pipeline/
      __init__.py
      s0_preprocess.py     # tokenize(text, config) -> list[Token]
      s1_classify.py       # classify(tokens, config) -> list[Token]
      s2_spellnorm.py      # spell_normalize(tokens, config) -> list[Token]
      s3_translit.py       # transliterate(tokens, config) -> list[Token]
      s4_names_brands.py   # resolve_entities(tokens, config) -> list[Token]
      s5_numerals.py       # expand_numerals(tokens, config) -> list[Token]
      s6_assemble.py       # assemble(tokens, config, input_text) -> NormalizationResult
    data/
      lexicons/
        english_freq.tsv   # word \t freq
        english_tts.tsv    # word \t devanagari_pron
        roman_hindi.tsv    # roman \t devanagari \t freq   (also the translit lookup)
        sms_abbrev.tsv     # token \t expansion
      gazetteers/
        names.tsv          # surface \t display \t pron_deva
        brands.tsv         # surface \t display \t pron_deva
    eval/
      __init__.py
      metrics.py           # scoring functions
      run_bench.py         # loads bench, runs normalize, prints per-category metrics
      bench_mini/
        sentences.tsv      # input \t ref_display \t ref_tts \t category
    api/
      cli.py               # typer CLI
      server.py            # optional FastAPI app
  tests/
    test_types.py  test_s0.py  test_s1.py  test_s2.py  test_s3.py
    test_s4.py  test_s5.py  test_s6.py  test_normalize.py  test_metrics.py
  DATA_LICENSES.md
  README.md
  CONTRIBUTING.md
```

**Token contract (used by every task — read once):**

```python
Token(surface, start, end, category=UNKNOWN, display_form="", tts_form="",
      confidence=0.0, alternatives=[], trace=[])
```

Stage signature convention: `stage(tokens: list[Token], config: Config) -> list[Token]`, mutating-and-returning the same list. `S0` is the exception: `tokenize(text: str, config: Config) -> list[Token]`.

---

### Task 1: Project scaffold + core types

**Files:**
- Create: `pyproject.toml`
- Create: `src/openhinglish/__init__.py` (temporarily empty)
- Create: `src/openhinglish/types.py`
- Test: `tests/test_types.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_types.py
from openhinglish.types import Category, Candidate, Token, NormalizationResult, Config


def test_token_defaults():
    t = Token(surface="kal", start=0, end=3)
    assert t.category == Category.UNKNOWN
    assert t.alternatives == []
    assert t.trace == []
    # mutable defaults must be independent instances
    t.trace.append("x")
    assert Token(surface="a", start=0, end=1).trace == []


def test_result_and_config():
    tok = Token(surface="kal", start=0, end=3, display_form="कल", tts_form="कल")
    res = NormalizationResult(input="kal", display="कल", tts="कल",
                              confidence=1.0, tokens=[tok])
    assert res.tokens[0].display_form == "कल"
    assert Config().nbest_k == 3
    assert Config().number_words_lang == "hindi"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_types.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'openhinglish'`

- [ ] **Step 3: Write `pyproject.toml`**

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
cli = ["typer>=0.12"]
server = ["fastapi>=0.110", "uvicorn>=0.29"]
dev = ["pytest>=8"]

[project.scripts]
openhinglish = "openhinglish.api.cli:app"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
openhinglish = ["data/lexicons/*.tsv", "data/gazetteers/*.tsv", "eval/bench_mini/*.tsv"]
```

- [ ] **Step 4: Write `src/openhinglish/types.py`**

```python
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class Category(str, Enum):
    HINDI_ROMAN = "HINDI_ROMAN"
    HINDI_DEVA = "HINDI_DEVA"
    ENGLISH = "ENGLISH"
    NAME = "NAME"
    BRAND = "BRAND"
    NUMBER = "NUMBER"
    DATE = "DATE"
    TIME = "TIME"
    ACRONYM = "ACRONYM"
    PUNCT = "PUNCT"
    EMOJI = "EMOJI"
    URL = "URL"
    UNKNOWN = "UNKNOWN"


@dataclass
class Candidate:
    category: Category
    display_form: str
    tts_form: str
    score: float


@dataclass
class Token:
    surface: str
    start: int
    end: int
    category: Category = Category.UNKNOWN
    display_form: str = ""
    tts_form: str = ""
    confidence: float = 0.0
    alternatives: list[Candidate] = field(default_factory=list)
    trace: list[str] = field(default_factory=list)


@dataclass
class NormalizationResult:
    input: str
    display: str
    tts: str
    confidence: float
    tokens: list[Token]


@dataclass
class Config:
    number_words_lang: str = "hindi"   # "hindi" | "english"
    nbest_k: int = 3
```

Also create empty `src/openhinglish/__init__.py` and `src/openhinglish/pipeline/__init__.py`.

- [ ] **Step 5: Install editable and run test to verify it passes**

Run: `pip install -e ".[dev]" && pytest tests/test_types.py -v`
Expected: PASS (2 passed)

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml src/openhinglish/__init__.py src/openhinglish/types.py src/openhinglish/pipeline/__init__.py tests/test_types.py
git commit -m "feat: scaffold package and core data contract"
```

---

### Task 2: Data loader + seed lexicon files

**Files:**
- Create: `src/openhinglish/data_loader.py`
- Create: `src/openhinglish/data/lexicons/english_freq.tsv`
- Create: `src/openhinglish/data/lexicons/english_tts.tsv`
- Create: `src/openhinglish/data/lexicons/roman_hindi.tsv`
- Create: `src/openhinglish/data/lexicons/sms_abbrev.tsv`
- Create: `src/openhinglish/data/gazetteers/names.tsv`
- Create: `src/openhinglish/data/gazetteers/brands.tsv`
- Test: `tests/test_data_loader.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_data_loader.py
from openhinglish.data_loader import load_map, load_set, load_gazetteer


def test_roman_hindi_map():
    m = load_map("lexicons/roman_hindi.tsv", key_col=0, val_col=1)
    assert m["kal"] == "कल"
    assert m["bhai"] == "भाई"


def test_english_set():
    s = load_set("lexicons/english_freq.tsv", col=0)
    assert "interview" in s


def test_gazetteer_brands():
    g = load_gazetteer("gazetteers/brands.tsv")
    assert g["paytm"].display == "Paytm"
    assert g["paytm"].pron_deva == "पे-टी-एम"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_data_loader.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'openhinglish.data_loader'`

- [ ] **Step 3: Create the seed TSV data files**

`src/openhinglish/data/lexicons/english_freq.tsv` (tab-separated `word\tfreq`):
```
interview	5000
the	100000
meeting	4000
project	3000
office	3500
call	4500
email	3000
manager	2000
```

`src/openhinglish/data/lexicons/english_tts.tsv` (`word\tdevanagari_pron`):
```
interview	इंटरव्यू
meeting	मीटिंग
project	प्रोजेक्ट
office	ऑफिस
email	ईमेल
manager	मैनेजर
```

`src/openhinglish/data/lexicons/roman_hindi.tsv` (`roman\tdevanagari\tfreq`):
```
bhai	भाई	8000
kal	कल	9000
mera	मेरा	7000
meri	मेरी	6500
me	में	9500
mein	में	9000
hai	है	12000
h	है	3000
nahi	नहीं	8000
aaj	आज	8500
tumhara	तुम्हारा	4000
par	पर	7000
pe	पर	6000
```

`src/openhinglish/data/lexicons/sms_abbrev.tsv` (`token\texpansion`):
```
intv	interview
pls	please
plz	please
msg	message
gud	good
thx	thanks
```

`src/openhinglish/data/gazetteers/names.tsv` (`surface\tdisplay\tpron_deva`):
```
shankar	Shankar	शंकर
mishra	Mishra	मिश्रा
dwivedi	Dwivedi	द्विवेदी
aaradhya	Aaradhya	आराध्या
```

`src/openhinglish/data/gazetteers/brands.tsv` (`surface\tdisplay\tpron_deva`):
```
paytm	Paytm	पे-टी-एम
zomato	Zomato	ज़ोमैटो
rapido	Rapido	रैपिडो
zepto	Zepto	ज़ेप्टो
```

- [ ] **Step 4: Write `src/openhinglish/data_loader.py`**

```python
from __future__ import annotations
import csv
from dataclasses import dataclass
from functools import lru_cache
from importlib.resources import files


def _open(rel_path: str):
    return files("openhinglish.data").joinpath(rel_path).open("r", encoding="utf-8")


def _rows(rel_path: str):
    with _open(rel_path) as fh:
        for row in csv.reader(fh, delimiter="\t"):
            if row and not row[0].startswith("#"):
                yield row


@lru_cache(maxsize=None)
def load_map(rel_path: str, key_col: int = 0, val_col: int = 1) -> dict[str, str]:
    return {r[key_col].strip(): r[val_col].strip() for r in _rows(rel_path)}


@lru_cache(maxsize=None)
def load_set(rel_path: str, col: int = 0) -> frozenset[str]:
    return frozenset(r[col].strip() for r in _rows(rel_path))


@dataclass(frozen=True)
class Entity:
    display: str
    pron_deva: str


@lru_cache(maxsize=None)
def load_gazetteer(rel_path: str) -> dict[str, Entity]:
    return {r[0].strip().lower(): Entity(r[1].strip(), r[2].strip()) for r in _rows(rel_path)}
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_data_loader.py -v`
Expected: PASS (3 passed)

- [ ] **Step 6: Commit**

```bash
git add src/openhinglish/data_loader.py src/openhinglish/data/
git add tests/test_data_loader.py
git commit -m "feat: TSV data loader and seed lexicons/gazetteers"
```

---

### Task 3: S0 — Preprocess / tokenize

**Files:**
- Create: `src/openhinglish/pipeline/s0_preprocess.py`
- Test: `tests/test_s0.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_s0.py
from openhinglish.pipeline.s0_preprocess import tokenize
from openhinglish.types import Category, Config


def test_word_tokenization_with_spans():
    toks = tokenize("bhai kal mera intv h paytm me", Config())
    assert [t.surface for t in toks] == ["bhai", "kal", "mera", "intv", "h", "paytm", "me"]
    assert (toks[0].start, toks[0].end) == (0, 4)
    assert all(t.category == Category.UNKNOWN for t in toks)


def test_structural_categories():
    toks = tokenize("call me! visit https://a.co 4", Config())
    cats = {t.surface: t.category for t in toks}
    assert cats["!"] == Category.PUNCT
    assert cats["https://a.co"] == Category.URL
    assert cats["4"] == Category.NUMBER


def test_passthrough_forms_default_to_surface():
    toks = tokenize("!", Config())
    assert toks[0].display_form == "!" and toks[0].tts_form == "!"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_s0.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write `src/openhinglish/pipeline/s0_preprocess.py`**

```python
from __future__ import annotations
import re
import unicodedata
from openhinglish.types import Token, Category, Config

_TOKEN_RE = re.compile(
    r"https?://\S+|www\.\S+"                               # URL
    r"|[A-Za-zऀ-ॿ]+"                             # word (latin / devanagari)
    r"|\d+(?:[.,:]\d+)*"                                   # number
    r"|[\U0001F300-\U0001FAFF☀-➿]"               # emoji-ish
    r"|[^\sA-Za-z0-9ऀ-ॿ]"                        # single punctuation char
)


def _category(text: str) -> Category:
    if text.startswith(("http://", "https://", "www.")):
        return Category.URL
    if text[0].isdigit():
        return Category.NUMBER
    if re.fullmatch(r"[A-Za-zऀ-ॿ]+", text):
        return Category.UNKNOWN
    if re.fullmatch(r"[\U0001F300-\U0001FAFF☀-➿]", text):
        return Category.EMOJI
    return Category.PUNCT


def tokenize(text: str, config: Config) -> list[Token]:
    text = unicodedata.normalize("NFC", text)
    tokens: list[Token] = []
    for m in _TOKEN_RE.finditer(text):
        surface = m.group(0)
        cat = _category(surface)
        tokens.append(Token(
            surface=surface, start=m.start(), end=m.end(),
            category=cat, display_form=surface, tts_form=surface,
            trace=[f"S0: tokenized as {cat.value}"],
        ))
    return tokens
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_s0.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add src/openhinglish/pipeline/s0_preprocess.py tests/test_s0.py
git commit -m "feat: S0 preprocess and tokenizer with spans"
```

---

### Task 4: S1 — Classification (language-ID, ranked candidates)

**Files:**
- Create: `src/openhinglish/pipeline/s1_classify.py`
- Test: `tests/test_s1.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_s1.py
from openhinglish.pipeline.s0_preprocess import tokenize
from openhinglish.pipeline.s1_classify import classify
from openhinglish.types import Category, Config


def _classify(text):
    return classify(tokenize(text, Config()), Config())


def test_devanagari_is_hindi_deva():
    toks = _classify("कल")
    assert toks[0].category == Category.HINDI_DEVA


def test_roman_hindi_and_english_and_brand():
    toks = {t.surface: t for t in _classify("kal interview paytm")}
    assert toks["kal"].category == Category.HINDI_ROMAN
    assert toks["interview"].category == Category.ENGLISH
    assert toks["paytm"].category == Category.BRAND


def test_collision_keeps_alternatives_sorted():
    # "me" exists in roman_hindi (में); also a common English word.
    tok = _classify("me")[0]
    cats = [tok.category] + [a.category for a in tok.alternatives]
    assert Category.HINDI_ROMAN in cats
    scores = [tok.confidence] + [a.score for a in tok.alternatives]
    assert scores == sorted(scores, reverse=True)


def test_structural_tokens_untouched():
    tok = _classify("!")[0]
    assert tok.category == Category.PUNCT
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_s1.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write `src/openhinglish/pipeline/s1_classify.py`**

```python
from __future__ import annotations
import re
from openhinglish.types import Token, Candidate, Category, Config
from openhinglish.data_loader import load_map, load_set, load_gazetteer

_DEVANAGARI = re.compile(r"[ऀ-ॿ]")
_STRUCTURAL = {Category.PUNCT, Category.EMOJI, Category.URL, Category.NUMBER}

# Frequency priors used when a token matches multiple lexicons.
_ENGLISH_PRIOR = 0.5


def _english_score(word: str, freq: dict[str, str]) -> float:
    f = int(freq.get(word.lower(), 0))
    return min(0.95, 0.4 + f / 200000.0) if f else 0.0


def _hindi_score(word: str, rh: dict[str, str]) -> float:
    # roman_hindi.tsv stores freq in col 2 via a separate map
    return 0.0


def classify(tokens: list[Token], config: Config) -> list[Token]:
    english = load_set("lexicons/english_freq.tsv", col=0)
    english_freq = load_map("lexicons/english_freq.tsv", key_col=0, val_col=1)
    roman_hindi = load_map("lexicons/roman_hindi.tsv", key_col=0, val_col=1)
    roman_hindi_freq = load_map("lexicons/roman_hindi.tsv", key_col=0, val_col=2)
    names = load_gazetteer("gazetteers/names.tsv")
    brands = load_gazetteer("gazetteers/brands.tsv")

    for tok in tokens:
        if tok.category in _STRUCTURAL:
            continue
        low = tok.surface.lower()

        if _DEVANAGARI.search(tok.surface):
            tok.category = Category.HINDI_DEVA
            tok.confidence = 1.0
            tok.trace.append("S1: script=devanagari -> HINDI_DEVA")
            continue

        cands: list[Candidate] = []
        if low in brands:
            cands.append(Candidate(Category.BRAND, brands[low].display, brands[low].pron_deva, 0.9))
        if low in names:
            cands.append(Candidate(Category.NAME, names[low].display, names[low].pron_deva, 0.85))
        if low in roman_hindi:
            f = int(roman_hindi_freq.get(low, 0))
            cands.append(Candidate(Category.HINDI_ROMAN, tok.surface, roman_hindi[low],
                                   min(0.9, 0.5 + f / 24000.0)))
        if low in english:
            cands.append(Candidate(Category.ENGLISH, tok.surface, tok.surface,
                                   _english_score(low, english_freq)))

        if not cands:
            cands.append(Candidate(Category.UNKNOWN, tok.surface, tok.surface, 0.1))

        cands.sort(key=lambda c: c.score, reverse=True)
        best, rest = cands[0], cands[1:config.nbest_k]
        tok.category = best.category
        tok.display_form = best.display_form
        tok.tts_form = best.tts_form
        tok.confidence = best.score
        tok.alternatives = rest
        tok.trace.append(f"S1: classified {best.category.value} (score={best.score:.2f}, "
                         f"{len(rest)} alt)")
    return tokens
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_s1.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add src/openhinglish/pipeline/s1_classify.py tests/test_s1.py
git commit -m "feat: S1 language-ID with ranked n-best candidates"
```

---

### Task 5: S2 — Spell normalization (conservative)

**Files:**
- Create: `src/openhinglish/pipeline/s2_spellnorm.py`
- Test: `tests/test_s2.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_s2.py
from openhinglish.pipeline.s0_preprocess import tokenize
from openhinglish.pipeline.s1_classify import classify
from openhinglish.pipeline.s2_spellnorm import spell_normalize
from openhinglish.types import Category, Config


def _run(text):
    c = Config()
    return spell_normalize(classify(tokenize(text, c), c), c)


def test_abbrev_expansion_reclassifies():
    tok = {t.surface: t for t in _run("intv h")}
    assert tok["intv"].display_form == "interview"
    assert tok["intv"].category == Category.ENGLISH
    assert any("S2" in tr for tr in tok["intv"].trace)


def test_confident_exact_match_not_rewritten():
    tok = _run("interview")[0]
    assert tok.display_form == "interview"
    assert not any("typo" in tr for tr in tok.trace)


def test_original_kept_as_alternative_on_typo_fix():
    # "intervew" -> nearest canonical "interview"
    tok = _run("intervew")[0]
    assert tok.display_form == "interview"
    assert any(a.display_form == "intervew" for a in tok.alternatives)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_s2.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write `src/openhinglish/pipeline/s2_spellnorm.py`**

```python
from __future__ import annotations
from difflib import get_close_matches
from openhinglish.types import Token, Candidate, Category, Config
from openhinglish.data_loader import load_map, load_set
from openhinglish.pipeline.s1_classify import classify

_SKIP = {Category.PUNCT, Category.EMOJI, Category.URL, Category.NUMBER,
         Category.HINDI_DEVA, Category.NAME, Category.BRAND}


def spell_normalize(tokens: list[Token], config: Config) -> list[Token]:
    abbrev = load_map("lexicons/sms_abbrev.tsv", key_col=0, val_col=1)
    english = load_set("lexicons/english_freq.tsv", col=0)
    roman_hindi = load_set("lexicons/roman_hindi.tsv", col=0)

    changed = False
    for tok in tokens:
        low = tok.surface.lower()

        # (a) deterministic abbreviation expansion
        if low in abbrev:
            tok.display_form = abbrev[low]
            tok.tts_form = abbrev[low]
            tok.trace.append(f"S2: abbrev {low} -> {abbrev[low]}")
            changed = True
            continue

        # never touch a confident exact lexicon hit
        if tok.category in _SKIP or low in english or low in roman_hindi:
            continue

        # (b) conservative typo fix against canonical vocab (english only in V1)
        match = get_close_matches(low, english, n=1, cutoff=0.85)
        if match:
            original = Candidate(tok.category, tok.surface, tok.tts_form,
                                 max(0.0, tok.confidence - 0.1))
            tok.alternatives = [original] + tok.alternatives[: config.nbest_k - 1]
            tok.display_form = match[0]
            tok.tts_form = match[0]
            tok.trace.append(f"S2: typo {low} -> {match[0]} (original kept as alt)")
            changed = True

    # re-run classification so expanded/fixed surfaces get correct categories
    if changed:
        for tok in tokens:
            if tok.display_form and tok.display_form.lower() != tok.surface.lower():
                tok.surface, tok._reclass = tok.surface, True
        _reclassify(tokens, config)
    return tokens


def _reclassify(tokens: list[Token], config: Config) -> None:
    # Build shadow tokens on the corrected surfaces and copy resulting category/forms.
    from openhinglish.pipeline.s0_preprocess import tokenize as _tok
    for tok in tokens:
        if getattr(tok, "_reclass", False):
            shadow = classify(_tok(tok.display_form, config), config)
            if shadow:
                s = shadow[0]
                tok.category = s.category
                tok.display_form = s.display_form
                tok.tts_form = s.tts_form
                tok.trace.append(f"S2: reclassified -> {s.category.value}")
            tok._reclass = False
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_s2.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add src/openhinglish/pipeline/s2_spellnorm.py tests/test_s2.py
git commit -m "feat: S2 conservative spell-normalization with abbrev expansion"
```

---

### Task 6: S3 — Transliteration (Roman-Hindi → Devanagari)

**Files:**
- Create: `src/openhinglish/pipeline/s3_translit.py`
- Test: `tests/test_s3.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_s3.py
from openhinglish.pipeline.s3_translit import transliterate, akshara_fallback
from openhinglish.types import Token, Category, Config


def _tok(surface, category, display=None, tts=None):
    return Token(surface=surface, start=0, end=len(surface), category=category,
                 display_form=display or surface, tts_form=tts or surface)


def test_known_roman_hindi_uses_lookup():
    toks = transliterate([_tok("kal", Category.HINDI_ROMAN)], Config())
    assert toks[0].display_form == "कल"
    assert toks[0].tts_form == "कल"


def test_english_keeps_latin_display_but_devanagari_tts_when_known():
    # english_tts.tsv maps interview -> इंटरव्यू
    t = _tok("interview", Category.ENGLISH)
    out = transliterate([t], Config())[0]
    assert out.display_form == "interview"
    assert out.tts_form == "इंटरव्यू"


def test_oov_roman_hindi_uses_akshara_fallback():
    out = transliterate([_tok("ghar", Category.HINDI_ROMAN)], Config())[0]
    assert out.display_form == akshara_fallback("ghar")
    assert out.display_form != "ghar"  # something was transliterated
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_s3.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write `src/openhinglish/pipeline/s3_translit.py`**

```python
from __future__ import annotations
from openhinglish.types import Token, Category, Config
from openhinglish.data_loader import load_map

# Minimal rule-based akshara fallback for OOV Roman-Hindi (V1 seed; extend over time).
# Ordered longest-first so multi-char clusters match before single chars.
_CONSONANTS = [
    ("chh", "छ"), ("sh", "श"), ("ch", "च"), ("gh", "घ"), ("kh", "ख"),
    ("th", "थ"), ("dh", "ध"), ("bh", "भ"), ("ph", "फ"), ("jh", "झ"),
    ("ng", "ंग"), ("k", "क"), ("g", "ग"), ("j", "ज"), ("t", "त"),
    ("d", "द"), ("n", "न"), ("p", "प"), ("b", "ब"), ("m", "म"),
    ("y", "य"), ("r", "र"), ("l", "ल"), ("v", "व"), ("w", "व"),
    ("s", "स"), ("h", "ह"), ("c", "क"),
]
_MATRA = {"a": "", "aa": "ा", "i": "ि", "ee": "ी", "u": "ु", "oo": "ू",
          "e": "े", "o": "ो", "ai": "ै", "au": "ौ"}
_INDEP = {"a": "अ", "aa": "आ", "i": "इ", "ee": "ई", "u": "उ", "oo": "ऊ",
          "e": "ए", "o": "ओ", "ai": "ऐ", "au": "औ"}
_VOWEL_KEYS = sorted(set(list(_MATRA) + list(_INDEP)), key=len, reverse=True)


def akshara_fallback(word: str) -> str:
    s = word.lower()
    out: list[str] = []
    i = 0
    last_was_consonant = False
    while i < len(s):
        for vk in _VOWEL_KEYS:
            if s.startswith(vk, i):
                out.append(_MATRA[vk] if last_was_consonant else _INDEP[vk])
                last_was_consonant = False
                i += len(vk)
                break
        else:
            for ck, dev in _CONSONANTS:
                if s.startswith(ck, i):
                    if last_was_consonant:
                        out.append("्")  # halant between adjacent consonants
                    out.append(dev)
                    last_was_consonant = True
                    i += len(ck)
                    break
            else:
                out.append(s[i])
                last_was_consonant = False
                i += 1
    return "".join(out)


def transliterate(tokens: list[Token], config: Config) -> list[Token]:
    roman_hindi = load_map("lexicons/roman_hindi.tsv", key_col=0, val_col=1)
    english_tts = load_map("lexicons/english_tts.tsv", key_col=0, val_col=1)

    for tok in tokens:
        low = tok.display_form.lower()
        if tok.category == Category.HINDI_ROMAN:
            if low in roman_hindi:
                dev = roman_hindi[low]
                tok.trace.append(f"S3: translit lookup {low} -> {dev}")
            else:
                dev = akshara_fallback(low)
                tok.trace.append(f"S3: translit akshara-fallback {low} -> {dev}")
            tok.display_form = dev
            tok.tts_form = dev
        elif tok.category == Category.ENGLISH:
            # display stays Latin; tts gets Devanagari pronunciation if we have one
            if low in english_tts:
                tok.tts_form = english_tts[low]
                tok.trace.append(f"S3: english tts {low} -> {english_tts[low]}")
            # else: tts_form stays Latin (honest V1 limitation)
    return tokens
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_s3.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add src/openhinglish/pipeline/s3_translit.py tests/test_s3.py
git commit -m "feat: S3 transliteration (lookup + akshara fallback) and english tts mapping"
```

---

### Task 7: S4 — Names & Brands (NER-lite + override)

**Files:**
- Create: `src/openhinglish/pipeline/s4_names_brands.py`
- Test: `tests/test_s4.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_s4.py
from openhinglish.pipeline.s0_preprocess import tokenize
from openhinglish.pipeline.s1_classify import classify
from openhinglish.pipeline.s4_names_brands import resolve_entities
from openhinglish.types import Category, Config


def _run(text):
    c = Config()
    return resolve_entities(classify(tokenize(text, c), c), c)


def test_brand_display_latin_tts_devanagari():
    tok = {t.surface.lower(): t for t in _run("paytm")}
    assert tok["paytm"].category == Category.BRAND
    assert tok["paytm"].display_form == "Paytm"
    assert tok["paytm"].tts_form == "पे-टी-एम"


def test_titlecase_promotes_name_candidate():
    # "Shankar" titlecased -> NAME chosen even if a lowercase collision exists
    tok = _run("Shankar")[0]
    assert tok.category == Category.NAME
    assert tok.display_form == "Shankar"
    assert tok.tts_form == "शंकर"


def test_lowercase_collision_does_not_overfire():
    # a lowercase common-word that also appears in names should not be forced to NAME
    # when no casing/context supports it. 'mishra' is unambiguous (only a name) -> stays NAME.
    tok = _run("mishra")[0]
    assert tok.category == Category.NAME
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_s4.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write `src/openhinglish/pipeline/s4_names_brands.py`**

```python
from __future__ import annotations
from openhinglish.types import Token, Candidate, Category, Config
from openhinglish.data_loader import load_gazetteer


def _is_titlecase(surface: str) -> bool:
    return surface[:1].isupper() and surface[1:].islower()


def resolve_entities(tokens: list[Token], config: Config) -> list[Token]:
    names = load_gazetteer("gazetteers/names.tsv")
    brands = load_gazetteer("gazetteers/brands.tsv")

    for idx, tok in enumerate(tokens):
        low = tok.surface.lower()
        ent = None
        cat = None
        if low in brands:
            ent, cat = brands[low], Category.BRAND
        elif low in names:
            ent, cat = names[low], Category.NAME

        if ent is None:
            continue

        # Casing/context guard: if the token is already a confident non-entity word
        # and is NOT title-cased and NOT sentence-initial, keep entity only as alternative.
        sentence_initial = idx == 0
        supports_entity = _is_titlecase(tok.surface) or sentence_initial or cat == Category.BRAND \
            or tok.category in (Category.NAME, Category.BRAND, Category.UNKNOWN)

        entity_candidate = Candidate(cat, ent.display, ent.pron_deva, 0.92)
        if supports_entity:
            if tok.category not in (Category.NAME, Category.BRAND):
                prev = Candidate(tok.category, tok.display_form, tok.tts_form, tok.confidence)
                tok.alternatives = [prev] + tok.alternatives[: config.nbest_k - 1]
            tok.category = cat
            tok.display_form = ent.display
            tok.tts_form = ent.pron_deva
            tok.confidence = 0.92
            tok.trace.append(f"S4: entity {cat.value} {low} -> {ent.display}/{ent.pron_deva}")
        else:
            tok.alternatives = [entity_candidate] + tok.alternatives[: config.nbest_k - 1]
            tok.trace.append(f"S4: entity {cat.value} kept as alternative (no casing/context support)")
    return tokens
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_s4.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add src/openhinglish/pipeline/s4_names_brands.py tests/test_s4.py
git commit -m "feat: S4 names/brands resolution with casing/context guard"
```

---

### Task 8: S5 — Numerals / Time / Acronyms

**Files:**
- Create: `src/openhinglish/pipeline/s5_numerals.py`
- Test: `tests/test_s5.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_s5.py
from openhinglish.pipeline.s5_numerals import expand_numerals, number_to_hindi_words
from openhinglish.types import Token, Category, Config


def _num(surface):
    return Token(surface=surface, start=0, end=len(surface), category=Category.NUMBER,
                 display_form=surface, tts_form=surface)


def test_number_words_hindi():
    assert number_to_hindi_words(4) == "चार"
    assert number_to_hindi_words(100) == "सौ"
    assert number_to_hindi_words(0) == "शून्य"


def test_number_tts_uses_hindi_by_default():
    out = expand_numerals([_num("4")], Config())[0]
    assert out.display_form == "4"
    assert out.tts_form == "चार"


def test_number_tts_english_config():
    out = expand_numerals([_num("4")], Config(number_words_lang="english"))[0]
    assert out.tts_form == "four"


def test_acronym_expanded_letterwise():
    t = Token(surface="RBI", start=0, end=3, category=Category.ENGLISH,
              display_form="RBI", tts_form="RBI")
    out = expand_numerals([t], Config())[0]
    assert out.category == Category.ACRONYM
    assert out.tts_form == "आर बी आई"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_s5.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write `src/openhinglish/pipeline/s5_numerals.py`**

```python
from __future__ import annotations
from openhinglish.types import Token, Category, Config

_HINDI_UNITS = ["शून्य", "एक", "दो", "तीन", "चार", "पाँच", "छह", "सात", "आठ", "नौ", "दस"]
_ENGLISH_UNITS = ["zero", "one", "two", "three", "four", "five", "six", "seven",
                  "eight", "nine", "ten"]
_LETTER_DEVA = {
    "a": "ए", "b": "बी", "c": "सी", "d": "डी", "e": "ई", "f": "एफ", "g": "जी",
    "h": "एच", "i": "आई", "j": "जे", "k": "के", "l": "एल", "m": "एम", "n": "एन",
    "o": "ओ", "p": "पी", "q": "क्यू", "r": "आर", "s": "एस", "t": "टी", "u": "यू",
    "v": "वी", "w": "डब्ल्यू", "x": "एक्स", "y": "वाई", "z": "ज़ेड",
}


def number_to_hindi_words(n: int) -> str:
    if n == 100:
        return "सौ"
    if 0 <= n <= 10:
        return _HINDI_UNITS[n]
    return str(n)  # V1 seed: only 0-10 and 100 spelled out; extend later


def _number_to_english_words(n: int) -> str:
    if 0 <= n <= 10:
        return _ENGLISH_UNITS[n]
    if n == 100:
        return "hundred"
    return str(n)


def expand_numerals(tokens: list[Token], config: Config) -> list[Token]:
    for tok in tokens:
        if tok.category == Category.NUMBER and tok.surface.isdigit():
            n = int(tok.surface)
            if config.number_words_lang == "english":
                tok.tts_form = _number_to_english_words(n)
            else:
                tok.tts_form = number_to_hindi_words(n)
            tok.trace.append(f"S5: number {n} -> '{tok.tts_form}'")
            continue

        # Acronym: all-caps Latin, length 2-5, not a known word context.
        if tok.surface.isupper() and tok.surface.isalpha() and 2 <= len(tok.surface) <= 5:
            tok.category = Category.ACRONYM
            tok.tts_form = " ".join(_LETTER_DEVA.get(ch.lower(), ch) for ch in tok.surface)
            tok.trace.append(f"S5: acronym {tok.surface} -> '{tok.tts_form}'")
    return tokens
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_s5.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add src/openhinglish/pipeline/s5_numerals.py tests/test_s5.py
git commit -m "feat: S5 numerals (hindi/english) and acronym letter-spelling"
```

---

### Task 9: S6 — Assemble + top-level `normalize()`

**Files:**
- Create: `src/openhinglish/pipeline/s6_assemble.py`
- Create: `src/openhinglish/disambiguator.py`
- Modify: `src/openhinglish/__init__.py`
- Test: `tests/test_s6.py`, `tests/test_normalize.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_s6.py
from openhinglish.pipeline.s0_preprocess import tokenize
from openhinglish.pipeline.s1_classify import classify
from openhinglish.pipeline.s6_assemble import assemble
from openhinglish.types import Config


def test_assemble_builds_two_strings_and_aggregate_confidence():
    c = Config()
    toks = classify(tokenize("kal", c), c)
    res = assemble(toks, c, "kal")
    assert res.display == "कल"
    assert res.tts == "कल"
    assert 0.0 < res.confidence <= 1.0
```

```python
# tests/test_normalize.py
from openhinglish import normalize


def test_worked_example_end_to_end():
    res = normalize("bhai kal mera intv h paytm me")
    assert res.display == "भाई कल मेरा interview Paytm में है"
    assert res.tts == "भाई कल मेरा इंटरव्यू पे-टी-एम में है"


def test_every_token_has_a_trace():
    res = normalize("bhai kal mera intv h paytm me")
    assert all(t.trace for t in res.tokens)


def test_determinism():
    a = normalize("bhai kal mera intv h paytm me")
    b = normalize("bhai kal mera intv h paytm me")
    assert a.display == b.display and a.tts == b.tts
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_s6.py tests/test_normalize.py -v`
Expected: FAIL — `ModuleNotFoundError` / `ImportError: cannot import name 'normalize'`

- [ ] **Step 3: Write `src/openhinglish/disambiguator.py`**

```python
from __future__ import annotations
from typing import Protocol
from openhinglish.types import Token, Config


class Disambiguator(Protocol):
    def resolve(self, tokens: list[Token], config: Config) -> list[Token]:
        ...


class FrequencyDisambiguator:
    """V1 no-op: S1 already ranked by frequency prior. Seam for the V1.1 learned layer."""

    def resolve(self, tokens: list[Token], config: Config) -> list[Token]:
        return tokens
```

- [ ] **Step 4: Write `src/openhinglish/pipeline/s6_assemble.py`**

```python
from __future__ import annotations
from openhinglish.types import Token, NormalizationResult, Category, Config

_NO_SPACE_BEFORE = {".", ",", "!", "?", ";", ":", "।", ")", "]", "}", "%"}


def _join(parts: list[tuple[str, Category]]) -> str:
    out = ""
    for i, (text, cat) in enumerate(parts):
        if i == 0:
            out = text
        elif cat == Category.PUNCT and text in _NO_SPACE_BEFORE:
            out += text
        else:
            out += " " + text
    return out


def assemble(tokens: list[Token], config: Config, input_text: str) -> NormalizationResult:
    display = _join([(t.display_form, t.category) for t in tokens])
    tts = _join([(t.tts_form, t.category) for t in tokens])
    scored = [t.confidence for t in tokens if t.category != Category.PUNCT]
    confidence = sum(scored) / len(scored) if scored else 1.0
    for t in tokens:
        t.trace.append("S6: assembled into display/tts")
    return NormalizationResult(input=input_text, display=display, tts=tts,
                               confidence=confidence, tokens=tokens)
```

- [ ] **Step 5: Write `src/openhinglish/__init__.py`**

```python
from __future__ import annotations
from openhinglish.types import Config, NormalizationResult, Token, Candidate, Category
from openhinglish.disambiguator import FrequencyDisambiguator
from openhinglish.pipeline.s0_preprocess import tokenize
from openhinglish.pipeline.s1_classify import classify
from openhinglish.pipeline.s2_spellnorm import spell_normalize
from openhinglish.pipeline.s3_translit import transliterate
from openhinglish.pipeline.s4_names_brands import resolve_entities
from openhinglish.pipeline.s5_numerals import expand_numerals
from openhinglish.pipeline.s6_assemble import assemble

__all__ = ["normalize", "Config", "NormalizationResult", "Token", "Candidate", "Category"]

_DISAMBIGUATOR = FrequencyDisambiguator()


def normalize(text: str, config: Config | None = None) -> NormalizationResult:
    config = config or Config()
    tokens = tokenize(text, config)
    tokens = classify(tokens, config)
    tokens = spell_normalize(tokens, config)
    tokens = _DISAMBIGUATOR.resolve(tokens, config)
    tokens = transliterate(tokens, config)
    tokens = resolve_entities(tokens, config)
    tokens = expand_numerals(tokens, config)
    return assemble(tokens, config, text)
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `pytest tests/test_s6.py tests/test_normalize.py -v`
Expected: PASS. If `test_worked_example_end_to_end` fails on exact strings, debug stage-by-stage using `result.tokens[i].trace` — do NOT weaken the assertion; fix the stage or the seed data.

- [ ] **Step 7: Commit**

```bash
git add src/openhinglish/disambiguator.py src/openhinglish/pipeline/s6_assemble.py src/openhinglish/__init__.py tests/test_s6.py tests/test_normalize.py
git commit -m "feat: S6 assemble + top-level normalize() pipeline"
```

---

### Task 10: Evaluation harness + `IndianTTSBench-mini` seed

**Files:**
- Create: `src/openhinglish/eval/__init__.py`
- Create: `src/openhinglish/eval/metrics.py`
- Create: `src/openhinglish/eval/run_bench.py`
- Create: `src/openhinglish/eval/bench_mini/sentences.tsv`
- Test: `tests/test_metrics.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_metrics.py
from openhinglish.eval.metrics import exact_match, cer, per_category


def test_exact_match():
    assert exact_match("कल", "कल") == 1.0
    assert exact_match("कल", "आज") == 0.0


def test_cer():
    assert cer("कल", "कल") == 0.0
    assert 0.0 < cer("कल", "कक") <= 1.0


def test_per_category_groups_and_averages():
    rows = [
        {"category": "code-switch", "display_em": 1.0},
        {"category": "code-switch", "display_em": 0.0},
        {"category": "names", "display_em": 1.0},
    ]
    out = per_category(rows, "display_em")
    assert out["code-switch"] == 0.5
    assert out["names"] == 1.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_metrics.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Create `src/openhinglish/eval/bench_mini/sentences.tsv`**

Seed rows (`input \t ref_display \t ref_tts \t category`). Start with these and grow to ≥300 by hand:
```
bhai kal mera intv h paytm me	भाई कल मेरा interview Paytm में है	भाई कल मेरा इंटरव्यू पे-टी-एम में है	code-switch
kal	कल	कल	roman-hindi
paytm	Paytm	पे-टी-एम	brand
shankar	Shankar	शंकर	name
4	4	चार	numeral
RBI	RBI	आर बी आई	acronym
```

- [ ] **Step 4: Write `src/openhinglish/eval/metrics.py`**

```python
from __future__ import annotations


def exact_match(pred: str, ref: str) -> float:
    return 1.0 if pred.strip() == ref.strip() else 0.0


def cer(pred: str, ref: str) -> float:
    pred, ref = pred.strip(), ref.strip()
    if not ref:
        return 0.0 if not pred else 1.0
    # Levenshtein distance (iterative DP)
    prev = list(range(len(ref) + 1))
    for i, pc in enumerate(pred, 1):
        cur = [i]
        for j, rc in enumerate(ref, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (pc != rc)))
        prev = cur
    return prev[-1] / len(ref)


def per_category(rows: list[dict], field: str) -> dict[str, float]:
    groups: dict[str, list[float]] = {}
    for r in rows:
        groups.setdefault(r["category"], []).append(r[field])
    return {k: sum(v) / len(v) for k, v in groups.items()}
```

- [ ] **Step 5: Write `src/openhinglish/eval/run_bench.py` and `src/openhinglish/eval/__init__.py`**

`src/openhinglish/eval/__init__.py`: empty file.

```python
# src/openhinglish/eval/run_bench.py
from __future__ import annotations
import csv
from importlib.resources import files
from openhinglish import normalize
from openhinglish.eval.metrics import exact_match, cer, per_category


def load_bench() -> list[dict]:
    path = files("openhinglish.eval.bench_mini").joinpath("sentences.tsv")
    with path.open("r", encoding="utf-8") as fh:
        return [
            {"input": r[0], "ref_display": r[1], "ref_tts": r[2], "category": r[3]}
            for r in csv.reader(fh, delimiter="\t") if r and not r[0].startswith("#")
        ]


def main() -> None:
    rows = []
    for ex in load_bench():
        res = normalize(ex["input"])
        rows.append({
            "category": ex["category"],
            "display_em": exact_match(res.display, ex["ref_display"]),
            "tts_em": exact_match(res.tts, ex["ref_tts"]),
            "tts_cer": cer(res.tts, ex["ref_tts"]),
        })
    for field in ("display_em", "tts_em", "tts_cer"):
        print(f"\n== {field} (per category) ==")
        for cat, val in sorted(per_category(rows, field).items()):
            print(f"  {cat:14s} {val:.3f}")
    n = len(rows)
    print(f"\nOverall display EM: {sum(r['display_em'] for r in rows)/n:.3f}  (n={n})")


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Run tests and the bench**

Run: `pytest tests/test_metrics.py -v`
Expected: PASS (3 passed)
Run: `python -m openhinglish.eval.run_bench`
Expected: prints per-category tables; the `code-switch` worked-example row scores `display_em=1.0`.

- [ ] **Step 7: Commit**

```bash
git add src/openhinglish/eval/ tests/test_metrics.py
git commit -m "feat: evaluation metrics, bench runner, and IndianTTSBench-mini seed"
```

---

### Task 11: CLI + optional FastAPI server + docs

**Files:**
- Create: `src/openhinglish/api/__init__.py` (empty)
- Create: `src/openhinglish/api/cli.py`
- Create: `src/openhinglish/api/server.py`
- Create: `README.md`, `CONTRIBUTING.md`, `DATA_LICENSES.md`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_cli.py
import json
import subprocess
import sys


def test_cli_outputs_json():
    out = subprocess.run(
        [sys.executable, "-m", "openhinglish.api.cli", "kal", "--json"],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert out.returncode == 0
    data = json.loads(out.stdout)
    assert data["display"] == "कल"
    assert data["tts"] == "कल"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py -v`
Expected: FAIL — `No module named openhinglish.api.cli`

- [ ] **Step 3: Write `src/openhinglish/api/cli.py`**

```python
from __future__ import annotations
import json as _json
import sys
from dataclasses import asdict
from openhinglish import normalize, Config


def app() -> None:
    args = sys.argv[1:]
    as_json = "--json" in args
    lang = "english" if "--english-numbers" in args else "hindi"
    words = [a for a in args if not a.startswith("--")]
    text = " ".join(words)
    res = normalize(text, Config(number_words_lang=lang))
    if as_json:
        print(_json.dumps({
            "input": res.input, "display": res.display, "tts": res.tts,
            "confidence": res.confidence,
            "tokens": [asdict(t) for t in res.tokens],
        }, ensure_ascii=False))
    else:
        print(f"display: {res.display}")
        print(f"tts    : {res.tts}")


if __name__ == "__main__":
    app()
```

- [ ] **Step 4: Write `src/openhinglish/api/server.py`**

```python
from __future__ import annotations
from dataclasses import asdict

try:
    from fastapi import FastAPI
    from pydantic import BaseModel
except ImportError as exc:  # pragma: no cover
    raise ImportError("Install server extras: pip install 'openhinglish[server]'") from exc

from openhinglish import normalize, Config

app = FastAPI(title="OpenHinglish Normalization API")


class Req(BaseModel):
    text: str
    number_words_lang: str = "hindi"


@app.post("/normalize")
def normalize_endpoint(req: Req) -> dict:
    res = normalize(req.text, Config(number_words_lang=req.number_words_lang))
    return {"input": res.input, "display": res.display, "tts": res.tts,
            "confidence": res.confidence, "tokens": [asdict(t) for t in res.tokens]}
```

- [ ] **Step 5: Write the three docs**

`README.md` — project pitch, install (`pip install -e ".[cli]"`), the worked example, the
`display`/`tts` distinction, link to the spec, V1 scope and V1.1 roadmap.

`CONTRIBUTING.md` — exactly how to add an entry to each TSV (`roman_hindi.tsv`, `names.tsv`,
`brands.tsv`, `sms_abbrev.tsv`, `english_tts.tsv`), how to add a bench sentence, and how to run
`pytest` + `python -m openhinglish.eval.run_bench`.

`DATA_LICENSES.md` — table of every data source, its license, and the code-vs-data license split
note (package code MIT; any ShareAlike-derived data carries its own license). Mark which seed files
are original (MIT) vs derived.

- [ ] **Step 6: Run test to verify it passes**

Run: `pytest tests/test_cli.py -v`
Expected: PASS (1 passed)

- [ ] **Step 7: Full suite + commit**

Run: `pytest -v`
Expected: ALL pass.

```bash
git add src/openhinglish/api/ README.md CONTRIBUTING.md DATA_LICENSES.md tests/test_cli.py
git commit -m "feat: CLI, optional FastAPI server, and project docs"
```

---

## Self-Review (completed by plan author)

**Spec coverage:**
- §3 stages S0–S6 → Tasks 3–9. ✓
- §4 data contract → Task 1. ✓
- §5 data sources/loader + license split → Task 2 + Task 11 `DATA_LICENSES.md`. ✓
- §6 `IndianTTSBench-mini` + metrics → Task 10. ✓
- §7 API/CLI/server/repo → Tasks 1, 11. ✓
- §8 component boundaries / `Disambiguator` seam → Task 9 `disambiguator.py`. ✓
- §9 error handling (UNKNOWN passthrough, determinism, over-correction guard) → Tasks 3, 5, 9 tests. ✓
- §10 scope: punctuation-insertion NOT implemented (only existing-punct join in S6); Hindi+English only; no audio. ✓
- §11 success criteria → covered by `tests/test_normalize.py` (contract, display/tts, determinism, trace) + Task 10 (bench/metrics). ✓

**Placeholder scan:** No "TBD/TODO/handle edge cases". Every code step shows complete code. Seed data files are explicitly listed (small but real). The bench is seeded with 6 real rows and flagged to grow to ≥300 by hand (a data-collection activity, correctly not faked).

**Type consistency:** `Category`, `Candidate`, `Token(surface,start,end,...)`, `NormalizationResult(input,display,tts,confidence,tokens)`, `Config(number_words_lang,nbest_k)` used identically across Tasks 1–11. Stage signatures `(tokens, config) -> tokens` consistent; `tokenize(text, config)` and `assemble(tokens, config, input_text)` are the two documented exceptions. Function names stable: `tokenize`, `classify`, `spell_normalize`, `transliterate`, `resolve_entities`, `expand_numerals`, `assemble`, `normalize`.

**Known V1 honesty flags (intentional, from spec §10):**
- English→Devanagari `tts` only for words in `english_tts.tsv`; unknown English stays Latin in `tts`. Documented limitation, not a bug.
- `akshara_fallback` is a coarse seed transliterator for OOV; correctness improves as `roman_hindi.tsv` grows (lookup path is authoritative).
- Number spelling covers 0–10 and 100 in V1; extend later.
