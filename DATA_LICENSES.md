# Data Provenance and Licenses

## Purpose

This document records the origin, license, and stewardship notes for every data file
shipped with OpenHinglish. It must be updated whenever a data file is added, modified,
or removed. Re-verify all licenses before each release.

---

## Current Data Files

All seed data under `src/openhinglish/data/` was **hand-authored original work** created
specifically for the OpenHinglish project. No data has been copied, derived, or scraped
from any third-party corpus. As original work, all current files are licensed under the
same **MIT License** as the project code.

| File | Location | Source | License | Notes |
|------|----------|--------|---------|-------|
| `roman_hindi.tsv` | `src/openhinglish/data/lexicons/` | Original hand-authored | MIT | Roman-script Hinglish ↔ normalized form mappings; no third-party corpus used |
| `english_freq.tsv` | `src/openhinglish/data/lexicons/` | Original hand-authored | MIT | English word frequency tiers for pass-through decisions; independently compiled |
| `english_tts.tsv` | `src/openhinglish/data/lexicons/` | Original hand-authored | MIT | English words with pronunciation hints for TTS-safe output; original curation |
| `sms_abbrev.tsv` | `src/openhinglish/data/lexicons/` | Original hand-authored | MIT | SMS/chat abbreviation expansions; independently authored, no corpus derived |
| `names.tsv` | `src/openhinglish/data/gazetteers/` | Original hand-authored | MIT | Indian personal name gazetteer; independently compiled, no external database derived |
| `brands.tsv` | `src/openhinglish/data/gazetteers/` | Original hand-authored | MIT | Indian brand/product name gazetteer; independently compiled |

---

## Future Data — Strict Rules

As the project grows, contributors may propose adding rows derived from external corpora.
The following rules are **mandatory** and not subject to override by PR consensus alone —
they require explicit maintainer sign-off:

### Google Dakshina Dataset

- The [Google Dakshina dataset](https://github.com/google-research-datasets/dakshina)
  is licensed **CC BY-SA 4.0 (share-alike)**.
- Any data file that contains rows **derived from Dakshina** — even partially — is
  itself a derivative work and **must be licensed CC BY-SA 4.0**, not MIT.
- Such files **must** live in a separately-licensed folder
  (e.g., `src/openhinglish/data/cc-by-sa/`) with its own `LICENSE` file stating
  CC BY-SA 4.0 clearly. They must **never** be placed alongside the MIT-licensed
  files or relabeled MIT.
- The source commit hash of the Dakshina snapshot used must be pinned in this document.

### CC BY-NC and Similar Non-Commercial Licenses

- **Nothing licensed CC BY-NC (Non-Commercial), CC BY-NC-SA, or any other
  non-commercial variant may ever enter this repository**, even in a separate folder.
  OpenHinglish is MIT-licensed for broad commercial use; non-commercial data would
  silently taint any derivative product.

### General Rules for All Future External Data

1. **Pin the source.** Record the dataset name, version, URL, and exact commit hash or
   release tag in this file before merging.
2. **Verify the license yourself.** Do not rely on secondary descriptions. Read the
   LICENSE file in the upstream repository. If the upstream has no LICENSE file, treat
   it as All Rights Reserved — do not use it.
3. **Re-verify before each release.** Upstream licenses can change. Check that all
   pinned sources still carry the same license at the pinned commit before cutting a
   release tag.
4. **One folder, one license.** Never mix files of different license families in the
   same directory. The directory structure itself signals the license regime.
5. **Attribution strings.** If a license requires attribution (CC BY variants), include
   the required attribution text in a `NOTICE` file in the same folder.

### Template Row for This Table (future entries)

| `example.tsv` | `src/openhinglish/data/cc-by-sa/` | Google Dakshina v1.0 — commit `abc1234` — https://github.com/google-research-datasets/dakshina | CC BY-SA 4.0 | Derived subset; share-alike applies; see `data/cc-by-sa/LICENSE` |
