# Language Packs — Convention & Status

> **V2 scaffold — additive only.**  
> This document describes the multi-language directory convention introduced in V2.  
> The engine currently processes **Hindi only**. Marathi and Punjabi entries below
> are **SEED data, NOT wired into the pipeline**.

---

## 1. Directory convention

Each language lives in its own sub-folder under `data/lexicons/`:

```
src/openhinglish/data/lexicons/
├── roman_hindi.tsv          # active, wired into the engine (V1)
├── english_freq.tsv         # active
├── english_tts.tsv          # active
├── sms_abbrev.tsv           # active
├── marathi/
│   └── roman_marathi.tsv    # EXPERIMENTAL — seed only, not yet wired
└── punjabi/
    └── roman_punjabi.tsv    # EXPERIMENTAL — seed only, not yet wired
```

**Rule:** one folder per language, named in lowercase English (e.g. `bengali/`,
`tamil/`, `telugu/`).  Every file inside follows the schema below.

---

## 2. TSV schema

Every lexicon file uses a three-column tab-separated format:

| Column | Name | Description |
|--------|------|-------------|
| 0 | `roman` | Romanised / transliterated form (lowercase, no diacritics preferred) |
| 1 | `native_script` | Word in the language's native Unicode script |
| 2 | `freq` | Approximate corpus frequency (integer; higher = more common) |

Lines starting with `#` are comments and are ignored by the data loader.

Example row (Marathi):

```
ghar	घर	8500
```

Example row (Punjabi):

```
ghar	ਘਰ	8500
```

---

## 3. How to add a new language (future contributor guide)

Adding a language is a **multi-step process**. Dropping in a TSV is only step 1
of 5. Do not claim a language is "supported" until all five steps are done.

### Step 1 — Create the seed lexicon

1. Make a folder: `src/openhinglish/data/lexicons/<language>/`
2. Create `roman_<language>.tsv` following the schema above.
3. Aim for at least **5 000 entries** for usable coverage (50 is a seed only).
4. Add a `#`-comment header at the top (copy the style from `roman_marathi.tsv`).

### Step 2 — Add G2P / transliteration rules

The engine needs to know how to convert arbitrary romanised input to the target
script, not just look up known words.  Implement (or integrate) a
language-specific grapheme-to-phoneme / transliteration module under:

```
src/openhinglish/adapters/<language>/
```

Each script has different vowel matras, conjunct consonants, and schwa-deletion
rules.  Hindi's rules do **not** transfer to Marathi or Punjabi without
modification.

### Step 3 — Register the language pack in the pipeline

Edit the pipeline's language registry (TBD in V2 design) to recognise the new
language key.  The loader path will be something like:

```python
load_map("lexicons/<language>/roman_<language>.tsv")
```

### Step 4 — Write tests

Add a test file `tests/test_<language>.py` covering:
- Known-word lookups from the lexicon.
- G2P round-trip for at least 20 words not in the lexicon.
- Edge cases (null input, mixed-case, punctuation).

### Step 5 — Update this document

Change the language's status from **SEED** to **ACTIVE** in the table in
Section 4.

---

## 4. Language status table

| Language | Folder | Script | Status | Notes |
|----------|--------|--------|--------|-------|
| Hindi | `lexicons/` (root) | Devanagari | **ACTIVE — wired** | Default/only active language in V1 |
| Marathi | `lexicons/marathi/` | Devanagari | **SEED — NOT wired** | ~50-word seed; G2P not implemented |
| Punjabi | `lexicons/punjabi/` | Gurmukhi | **SEED — NOT wired** | ~50-word seed; G2P not implemented |

> **Honest disclaimer:** The Marathi and Punjabi files contain approximately
> 50 words each.  This is a structural placeholder to prove the directory
> convention works, not a usable transliteration resource.  Production-quality
> support requires thousands of entries plus custom linguistic rules.

---

## 5. What "NOT yet wired" means

- The existing Python engine (`data_loader.py`, `pipeline/`, `disambiguator.py`)
  does **not** import or reference the `marathi/` or `punjabi/` folders.
- No existing tests cover these files.
- The Hindi pipeline is unmodified.
- These TSV files will be silently ignored until a future PR explicitly wires
  them in (following Steps 2–5 above).

---

## 6. Licensing

All seed data in this repo is released under **CC0 1.0 Universal** unless noted
otherwise in a per-file header.  See `DATA_LICENSES.md` for full details.

---

*This document was introduced as part of the V2 language-pack scaffold (additive
only; no engine changes). See `MASTER_ROADMAP.md` for the V2 timeline.*
