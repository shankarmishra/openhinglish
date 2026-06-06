# OpenHinglish — Datasets Reference

> **Canonical source of truth** for every data dependency in the project.
> Read alongside `DATA_LICENSES.md` (per-file provenance ledger).
> Senior, honest tone: nothing is oversold; risks are stated plainly.

---

## 1. Datasets Required, by Version

Each version of OpenHinglish demands a specific data investment. The table below maps every dataset category to the version that first needs it and explains why.

| Dataset / Source | V1 | V2 | V3 | V4 | V5 | Rationale |
|---|:---:|:---:|:---:|:---:|:---:|---|
| **Dakshina** Roman↔Devanagari word pairs | core | reuse | reuse | reuse | reuse | Backbone of the Roman-Hindi lexicon; primary source for S3 translit lookup table |
| **IndicXlit** offline build tool | build | build | build | build | build | Used offline at build-time only to precompute static transliteration tables; never at inference |
| **SCOWL / English freq lists** | core | reuse | reuse | reuse | reuse | S1 classifier and S3 English-word recognition; permissive license, easy to update |
| **Wikidata names/brands** | core | expand | expand | expand | expand | S4 gazetteer for names + brands; V1 needs Indian first names + top 500 brand tokens |
| **Census / UIDAI name frequency data** | V1+ | expand | expand | expand | expand | Supplements Wikidata for Indian given-name coverage, particularly regional names |
| **Mozilla Common Voice (text)** | supplement | expand | expand | reuse | reuse | Validated Hindi/English utterance text for spell-norm and classifier training data |
| **AI4Bharat IndicVoices / IndicVoices-R** | supplement | expand | expand | reuse | reuse | Reference utterance text; CC-BY-4.0 so commercial use is safe with attribution |
| **SMS/chat abbreviation corpus** | core | reuse | reuse | reuse | reuse | S2 abbrev expansion table; V1 target ≥ 1 000 entries (currently ~70) |
| **Hand-curated GOLD EVAL sentences** | core | grow | grow | grow | full | IndianTTSBench-mini; V1 target ≥ 300 verified; V5 target ≥ 1 000+ with public leaderboard |
| **Per-language translit/G2P tables** (Marathi, Punjabi, Gujarati, Bengali, Tamil, Telugu) | — | core | reuse | reuse | reuse | New language frontends in V2; reuse the same pipeline skeleton |
| **HiACC Hinglish code-switch corpus (2025)** | candidate | candidate | core | reuse | reuse | Code-switch eval; license UNVERIFIED — confirm before any use |
| **Learned disambiguator training data** | — | — | core | reuse | reuse | Feeds the pluggable `Disambiguator` at Path C (V3); must be permissively licensed |

**Current state (early-functional):** Lexicons have grown well past the original seeds — ~470+ Roman-Hindi words, ~70 SMS abbreviations, ~200 names, ~100 brands, ~260 English-TTS words (~1,500+ entries total). Real-world coverage on the long tail of uncommon tokens is still limited. The V1 data-scaling effort (target ~10k via Dakshina) remains the single highest-leverage task in the project.

---

## 2. License Status Table

Every source's verified license, what it enables, and what it restricts. **This table is the canonical license ledger; expand but keep it consistent with `DATA_LICENSES.md`.**

| Source | License | Verified? | Commercial use | Modification | Distribution | Key restriction |
|---|---|:---:|:---:|:---:|:---:|---|
| Google **Dakshina** | CC-BY-SA-4.0 | Yes | Yes | Yes | Yes — under SA | **Share-alike**: any derived data file (lexicons, lookup tables) must be redistributed under CC-BY-SA-4.0, not MIT. Code that merely *reads* it is unaffected. |
| AI4Bharat **IndicXlit** | Open (Apache-2.0 codebase) | Yes — code | Yes | Yes | Yes | Used offline only; do not bundle weights at inference. Verify exact weights license before any model-file distribution. |
| Mozilla **Common Voice** (text) | CC0-1.0 | Yes | Yes | Yes | Yes | None; safest possible. Audio has separate per-contributor licenses — OpenHinglish uses text only. |
| AI4Bharat **IndicVoices / IndicVoices-R** | CC-BY-4.0 | Yes | Yes | Yes | Yes | Attribution required in documentation and release notes. |
| **Wikidata** dumps | CC0-1.0 | Yes | Yes | Yes | Yes | None. Preferred source for names/brands gazetteers. |
| **SCOWL** English word lists | LGPL-compatible / permissive mix | Yes | Yes | Yes | Yes | See per-wordlist license within SCOWL; do not redistribute raw files without checking individual list licenses. |
| Census / UIDAI name data | Government open data (India) | Partial | Unclear | Unclear | Unclear | **Unverified** for derived redistribution; treat as internal reference only until legally confirmed. |
| **HiACC** (2025 code-switch corpus) | **UNVERIFIED** | No | Unknown | Unknown | Unknown | **Block on use** until license is confirmed. Do not ship any derived artifact. |
| **OpenSubtitles / web-scraped Hinglish** | Mixed / often restricted | No | No (default) | No | No | Scraping may violate ToS; do not include without explicit permission audit. |

**The standing rule:**

> Nothing CC-BY-NC enters the release. Code is MIT. Data files carry their source license. Pin commit hashes. Re-verify before every release.

---

## 3. The License Trap

### 3.1 CC-BY-SA Share-Alike Contamination

Dakshina is the richest freely available Roman↔Devanagari dataset. It carries CC-BY-SA-4.0 — a **copyleft (share-alike)** license. This is not a minor footnote; it determines the legal character of every data artifact built from it.

**What share-alike means in practice:**

- Any lexicon, lookup table, transliteration map, or frequency list that is a *derived work* of Dakshina must be distributed under CC-BY-SA-4.0, not MIT and not any less-restrictive license.
- "Derived work" includes: filtered subsets, merged tables where Dakshina entries are identifiable, reformatted TSVs where Dakshina content is preserved.
- "Not derived" includes: independently created entries, outputs of the running system applied to new user text, statistical aggregates that cannot be reverse-engineered to individual source entries (debatable — get legal advice for commercial use).

**The code/data split is critical:**

The Python source code (MIT) reads these data files at runtime. Reading a CC-BY-SA file does not infect the code's MIT license. The infection boundary is the *data file itself*. Concretely:

```
src/openhinglish/data/lexicons/roman_hindi.tsv   ← CC-BY-SA-4.0  (derived from Dakshina)
src/openhinglish/pipeline/s3_translit.py         ← MIT           (code that reads the TSV)
```

Both must be present in the repository. Both carry their own license. The `pyproject.toml` `license = "MIT"` refers to the code. The data subdirectory must contain a `LICENSE.data` file pointing to CC-BY-SA-4.0 for any Dakshina-derived files.

### 3.2 The Provenance Ledger: `DATA_LICENSES.md`

Every data file in `src/openhinglish/data/` must have a corresponding entry in `DATA_LICENSES.md` at the repo root. The minimum entry schema:

```
| File path | Source dataset | Source URL | Commit/version hash | License | Date verified | Notes |
```

**Pin commit hashes.** Dataset maintainers can change license terms without announcement. Pinning the exact commit you used ensures reproducibility and proves you operated in good faith under the license in effect at the time of ingestion.

### 3.3 The Spark-TTS Cautionary Tale

Spark-TTS-0.5B was originally released under Apache-2.0 (commercial-friendly). It subsequently drifted to CC-BY-NC-SA without a major version bump. Projects that had already built commercial products on it found themselves in an ambiguous legal position — their derivative works existed under a license the upstream had silently invalidated.

**Lesson for OpenHinglish:** Re-verify every dataset license before each tagged release, not just at initial ingestion. Record the verification date in `DATA_LICENSES.md`. If an upstream license becomes more restrictive, treat the last permissive commit as a frozen vendor copy and document why.

### 3.4 The "MIT project" Framing Risk

Marketing OpenHinglish as "MIT licensed" without qualification is technically accurate for the code but misleading for consumers who want to use the data. The release notes, README, and PyPI metadata must clearly state:

> Code: MIT. Data files: see `DATA_LICENSES.md`. Dakshina-derived lexicons carry CC-BY-SA-4.0.

Downstream TTS product builders — the primary audience — need to know that embedding the distributed lexicon TSVs in a closed product may require them to open-source their modifications to those files under SA. This is a real integration friction and must not be hidden.

---

## 4. Collection Strategy

### 4.1 Roman-Hindi Lexicon (S3 Translit Lookup Table)

**Primary source: Google Dakshina.**
The Dakshina dataset (Roark et al., 2020) provides romanization variants alongside Devanagari ground truth for Hindi (and other Indic scripts). Target: extract ≥ 10 000 unique Roman → Devanagari word pairs for V1.

Build process:
1. Download Dakshina at a pinned commit; record in `DATA_LICENSES.md`.
2. Parse the Hindi split; filter entries by frequency ≥ N (tune N to balance coverage vs. table size).
3. Resolve one-to-many romanizations: keep all variants as n-best alternatives — do not discard them. The engine surfaces alternatives; discarding them is a permanent coverage loss.
4. Output: `roman_hindi.tsv` (two-column: `roman_form TAB devanagari_form`), licensed CC-BY-SA-4.0.

**Secondary tool: AI4Bharat IndicXlit.**
IndicXlit is used **offline at build-time only** to fill gaps not covered by Dakshina. Run it over a target wordlist; add outputs to the same TSV with provenance tag `source=indicxlit`. Never invoke IndicXlit at inference — it violates the CPU-only, deterministic, no-ML-at-inference commitment.

### 4.2 Names and Brands Gazetteer (S4)

**Primary source: Wikidata (CC0).**
- Indian given names: SPARQL query over `instance of: given name`, language `hi`/`ur`, filter by sitelinks ≥ threshold for frequency proxy.
- Indian surnames: similarly.
- Brand names: SPARQL query over `instance of: brand`, country `India`, plus top global brands with significant Indian market presence.
- Output: `names.tsv`, `brands.tsv` — both CC0.

**Supplement: Census / UIDAI frequency data.**
Provides frequency-ranked given names unavailable in Wikidata. License status is unconfirmed for redistribution; use only as internal enrichment and do not ship raw census data in the package.

**Pronunciation annotation for brands:**
Brands need a `tts_form` column with Hindi phonetic rendering (e.g., `Paytm → पे-टी-एम`). This must be hand-curated; no automated source is reliable. Target 500 entries for V1.

### 4.3 English Frequency List (S1 Classifier)

**Source: SCOWL (Spell Checker Oriented Word Lists).**
SCOWL provides frequency-stratified English wordlists with a permissive license. Use the 60 or 70 frequency threshold to capture common English words a Hinglish writer would code-switch in, without over-extending to obscure English.

### 4.4 SMS / Chat Abbreviation Table (S2)

No single open dataset covers Indian SMS abbreviations comprehensively. Build strategy:
1. Start from documented Hindi internet slang lists (Wikipedia, published linguistics papers — cite and verify licenses per source).
2. Crowdsource additions through GitHub Issues with a defined contribution template.
3. Hand-verify every entry: `abbrev → expansion → Devanagari → TTS form`. Flag ambiguous expansions (e.g., `brb` → "be right back" vs. rare alternative uses) as n-best candidates.
4. License: entries from open sources carry their source license; community-contributed entries enter under CC0.

### 4.5 The GOLD EVAL Set (IndianTTSBench-mini)

This is the most important data artifact in the project. It is also the hardest to build correctly.

**Current state:** 59 single-author rows across 11 categories in `eval/bench_mini/sentences.tsv` (0.92 display EM / 0.92 TTS). Large enough to surface real weak spots (address, code-switch) but not yet multi-annotator validated; not a production capability claim.

**V1 target: ≥ 300 human-verified sentences across all benchmark categories.**

Build methodology:
1. **LLM-draft, human-verify.** Use an LLM to draft candidate sentences covering all categories (names, brands, code-switch, numerals, dates, addresses, SMS-abbrev, ambiguity). Draft sentences are *zero cost* to generate but must be treated as unverified until a human adjudicator reviews them.
2. **Human adjudication.** At least two independent annotators validate each sentence's `ref_display` and `ref_tts`. Disagreements are logged and resolved by majority (with the disagreement recorded as a second valid alternative — not discarded).
3. **Crowdsourcing supplement.** GitHub contributors can submit candidate sentences via PR, with a checklist template. All submissions require maintainer review before merging.
4. **No single-reference constraint.** The evaluation format stores *multiple* accepted references per sentence to reflect genuine Hinglish ambiguity (see BENCHMARK.md).

The GOLD EVAL set is CC0 where entirely original, or CC-BY-SA-4.0 where any reference output was derived from Dakshina vocabulary. Tag per-row provenance in the TSV.

### 4.6 Per-Language Data for V2

V2 adds Marathi, Punjabi, Gujarati, Bengali, Tamil, Telugu. Each language needs:
- A Roman ↔ native-script lexicon (equivalent of Dakshina for that language).
- A G2P / transliteration table.
- A per-language bench subset (minimum 50 sentences before claiming language support).

Dakshina covers several of these scripts. Verify license status for each language split independently — they are the same CC-BY-SA-4.0 terms, but confirm before ingestion.

---

## 5. Data Quality and Bias

### 5.1 Regional Bias

Dakshina and most open Hinglish datasets over-represent Delhi/NCR, Mumbai, and Bengaluru usage. Spelling variants from UP/Bihar, Rajasthan, or southern-state Hinglish speakers may be absent or under-represented. The practical consequence: the engine will achieve high accuracy on "standard internet Hinglish" and poor accuracy on regional spelling conventions.

Mitigation: annotate the source dialect/region in `roman_hindi.tsv` where known. Track coverage by region in quarterly data audits. Solicit contributions explicitly from regional speakers.

### 5.2 Gender and Name Coverage

Name gazetteers built from Wikidata tend to over-represent male names and names of historically prominent figures. Female names, non-binary names, names common in Dalit/OBC communities, and tribal names are statistically under-represented.

This bias will cause S4 to mis-classify some Indian names as UNKNOWN, degrading confidence scores for users with less-represented names. Document this limitation explicitly in the README.

### 5.3 Dialect and Script Variation

- Urdu-origin vocabulary romanized by Urdu speakers follows different conventions than the same words romanized by Hindi speakers (e.g., `kya` vs. `kia`, `hai` vs. `hae`).
- South Indian speakers writing Hinglish introduce distinct phonetic mappings.
- The V1 engine treats these as spelling variants and covers them via n-best. The long tail is large; the seed lexicon covers almost none of it.

### 5.4 The Long Tail of Spelling Variants

Hinglish spelling is not standardized. A single Hindi word can appear in dozens of Roman spellings across a corpus. Dakshina captures many variants but not all. The V1 akshara fallback (phoneme-level matching) handles unseen spellings with lower confidence, but its accuracy on extreme variants is unmeasured.

Implication for the eval set: if benchmark sentences are drawn only from Dakshina vocabulary, the benchmark score is an upper bound on Dakshina coverage, not on real-world performance. V1 bench sentences must include "out-of-lexicon" variants that exercise the fallback path.

---

## 6. Risks

| Risk | Severity | Likelihood | Mitigation |
|---|:---:|:---:|---|
| **Provenance gap** — a data file ships without a traceable source | Critical | Medium | Enforce `DATA_LICENSES.md` entry as a PR merge gate; block releases if any file is unlisted |
| **License drift** — upstream changes terms post-ingestion | High | Medium | Re-verify all sources before each tagged release; pin commit hashes; keep a frozen vendor copy for each pinned version |
| **CC-BY-SA contamination spreads** — derived lexicons mislabeled MIT | High | Low-Medium | Lint `DATA_LICENSES.md` in CI; never let data files carry the code's MIT header |
| **Scraping prohibition** — web-scraped Hinglish from social platforms added to corpus | Critical | Medium | Zero-tolerance policy; no scraped data without explicit written permission |
| **HiACC unverified license** — used before confirmation | High | Low (if gated) | Hard block in task tracker: no HiACC artifact merges until license doc is on file |
| **GOLD EVAL quality** — LLM-drafted sentences used without human review | High | Medium | Every eval sentence must carry an `adjudicated_by` field; CI rejects rows without it |
| **Annotator bias** — single annotator defines ground truth | Medium | High | Require ≥ 2 annotators; record IAA score per batch; surface disagreements as multi-reference |
| **Sustainability** — hand-curation at scale requires time OpenHinglish currently does not have | High | High | Plan community contribution infrastructure (GitHub templates, clear contribution guides) before V1 data sprint |
| **Demand unproven** — building large datasets for a capability nobody uses | Medium | Medium | Validate with at least one real TTS integration proof-of-pain before V1 data sprint; do not pre-build V2 data in absence of V1 adoption signal |

---

## Challenged Assumptions / Risks / Open Questions

1. **"Dakshina is sufficient for V1."** Dakshina covers written Hindi but under-represents conversational Hinglish code-switching patterns. The V1 lexicon built from it will have systematic blind spots. The 10k target may yield lower real-world coverage than it implies.

2. **"CC-BY-SA is acceptable to downstream users."** For purely academic TTS research it is. For commercial TTS product builders who want to embed the lexicon without open-sourcing their modifications, it is a blocker. Consider whether a dual-licensing path (paid commercial license for the data) is worth exploring at V2+.

3. **"IndicXlit fill-in is neutral."** IndicXlit's translit outputs are themselves model outputs and may contain errors. Build-time use means errors are baked into static tables. Audit a sample of IndicXlit-generated entries before shipping.

4. **"The GOLD EVAL can be hand-curated at 300+ sentences by one maintainer."** At realistic annotation throughput, 300 carefully adjudicated Hinglish sentences with dual-annotation is 30–60 hours of work. Plan accordingly. Do not promise V1 bench growth without a realistic capacity estimate.

5. **"Census name data is usable."** Confirmed: not verified for redistribution. Do not use as a shipping data source without legal confirmation.
