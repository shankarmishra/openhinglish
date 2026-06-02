# OpenHinglish — Governance

> **Status: V0.1 Foundation — solo BDFL, bus-factor = 1.**
> This document is honest about that and describes the path forward.

---

## Table of Contents

1. [Contribution Rules](#1-contribution-rules)
2. [Decision-Making and Maintainer Model](#2-decision-making-and-maintainer-model)
3. [Data Policies](#3-data-policies)
4. [Licensing Policies](#4-licensing-policies)
5. [Voice and Data Compliance](#5-voice-and-data-compliance)
6. [Conduct and Security](#6-conduct-and-security)
7. [Challenged Assumptions / Risks](#7-challenged-assumptions--risks)

---

## 1. Contribution Rules

### 1.1 What you can contribute

| Contribution type | File(s) affected | Skill required |
|---|---|---|
| New or corrected lexicon entries | `src/openhinglish/data/lexicons/*.tsv` | Can read a TSV |
| New or corrected gazetteer entries (names, brands) | `src/openhinglish/data/gazetteers/*.tsv` | Can read a TSV |
| Pipeline bug fixes | `src/openhinglish/pipeline/s*.py` | Python 3.11+, must include tests |
| New pipeline stage or major feature | `src/openhinglish/pipeline/` | Python 3.11+, design discussion first |
| Benchmark sentence additions | `src/openhinglish/eval/bench_mini/sentences.tsv` | Must provide human-verified expected output |
| New language support (V2+) | New lexicon dir + transliterator + tests | Coordinate with maintainer first |
| Documentation fixes | `docs/`, `README.md` | Plain text |

### 1.2 How to contribute lexicon or gazetteer data

1. Open a PR editing the relevant `.tsv` file under `src/openhinglish/data/`.
2. Each new row **must** include a `source` column value pointing to a named, citable, permissively-licensed corpus or public resource (see Section 3 for details).
3. Do not add rows derived from:
   - scraped web text without confirmed licensing
   - copyrighted word lists (e.g., proprietary dictionaries)
   - private individuals' names, phone numbers, or addresses
4. If the source is a dataset with a share-alike license (e.g., Dakshina CC-BY-SA-4.0), note it explicitly; the lexicon file's own header comment and `DATA_LICENSES.md` will carry the share-alike obligation downstream.
5. Keep entries normalized: lowercase Roman keys, Devanagari values, no trailing whitespace, Unix line endings.

### 1.3 How to contribute code

1. **Fork → branch → PR.** Branch naming convention: `fix/<short-description>`, `feat/<short-description>`, `lang/<language-code>`.
2. **Tests are required for every code PR.** The project uses `pytest`. Add tests in `tests/test_<stage>.py` covering the new or changed behavior. PRs that break existing tests will not be merged.
3. **No ML at inference.** Any use of ML models (e.g., IndicXlit) must be offline and build-time only — producing static TSV lookup tables. Do not introduce runtime ML dependencies.
4. **No new runtime dependencies without discussion.** The engine targets CPU-only, lightweight deployment. Heavy inference libraries (torch, transformers, etc.) are explicitly excluded from the runtime dependency set.
5. **Pure functions only in pipeline stages.** Each stage has the signature `(tokens: list[Token], config: Config) -> list[Token]`. Do not introduce side effects, global state, or I/O into stage functions.
6. Ensure `pyproject.toml` is updated if adding a new optional dependency group.

### 1.4 The review process

All changes go through GitHub Pull Requests.

**For data-only PRs (TSV edits):**
- Maintainer reviews provenance of the `source` column.
- Spot-checks 5–10 rows for correctness.
- Merges if provenance is clean and entries are format-compliant.
- Turnaround target: 7 days, but this is a solo project — no SLA guarantee.

**For code PRs:**
- CI must pass (all existing tests green).
- New tests must be included and green.
- Maintainer reads the diff for architectural consistency with the 7-stage pipeline model.
- Complex PRs (new stage, new language) require a design issue/discussion filed *before* the PR.

**For benchmark additions:**
- Each new sentence must have human-verified `display` and `tts` expected outputs.
- Annotator identity and rationale for the expected output must be in the PR description.
- Multiple valid outputs should be listed as alternatives (the eval harness supports n-best coverage scoring).

### 1.5 Definition of done — a single change

A change (code or data) is considered **done** when:
- [ ] All existing `pytest` tests pass.
- [ ] New tests cover the changed behavior (code PRs only).
- [ ] The `source` column is populated and license-verified (data PRs only).
- [ ] `DATA_LICENSES.md` is updated if a new data source is introduced.
- [ ] PR description explains what changed and why.
- [ ] The maintainer has merged and the CI build is green on `main`.

### 1.6 Definition of done — adding a new language (V2+)

A new language is considered **shippable** when:
- [ ] A new lexicon directory exists under `src/openhinglish/data/lexicons/<lang_code>/`.
- [ ] A transliterator for that language is implemented and wired into S3.
- [ ] A per-language benchmark TSV exists under `src/openhinglish/eval/bench_<lang_code>/` with at least 50 human-verified sentences.
- [ ] Accuracy on that benchmark meets a minimum threshold agreed before work begins (documented in the language's PR).
- [ ] A language maintainer (human, not a bot) is identified and listed in `CODEOWNERS` or this file.
- [ ] All data sources for the new language are logged in `DATA_LICENSES.md` with verified licenses.
- [ ] A `CHANGELOG` entry documents the language addition.

---

## 2. Decision-Making and Maintainer Model

### 2.1 Current model — Solo BDFL

**Shankar Mishra** is the sole Benevolent Dictator For Life (BDFL). All final decisions on architecture, roadmap, data acceptance, and releases rest with him. This is an honest reflection of the current state: V0.1 is a foundation project, and community governance overhead would slow down the critical V1 lexicon-scaling work more than it helps.

### 2.2 Bus-factor = 1 — explicit acknowledgment

**This is the top existential risk for a project with a 5-year roadmap.**

If the sole maintainer becomes unavailable, the project has no one with merge authority, no one with PyPI upload credentials, and no documented succession. This is acceptable at V0.1 but must be resolved before V1 release (PyPI publish).

**Mitigation checklist (work-in-progress):**

| Action | Target milestone | Status |
|---|---|---|
| Store PyPI token and credentials in a documented (offline) location | Pre-V1 | Pending |
| Write a `MAINTAINER_RUNBOOK.md` covering release steps, CI secrets, and data refresh | Pre-V1 | Pending |
| Identify at least one co-maintainer candidate from early contributors | V1 | Pending |
| Formally grant co-maintainer rights (GitHub org, PyPI trusted publisher) | V1–V2 | Pending |
| Establish a community Discussions or Discord with at least one active moderator | V1 | Pending |

### 2.3 Criteria and path to adding co-maintainers

A co-maintainer candidate should:

1. Have contributed at least **3 merged PRs** (code or substantial data), demonstrating understanding of the project's architecture and data standards.
2. Have demonstrated good judgment on **data provenance** — the single most dangerous failure mode for the project.
3. Be reachable and responsive over a period of at least 2–3 months.
4. Explicitly agree to the project's licensing and data policies.

The path:
- BDFL opens a GitHub issue titled "Co-maintainer nomination: [name]" and gives a 7-day comment window.
- If no blocking objection is raised by existing contributors, the nominee is added as a GitHub collaborator and PyPI trusted publisher.
- Co-maintainer responsibilities are documented: each co-maintainer "owns" one or more lanes (see below).

### 2.4 Maintainer lanes — areas that need owners

As the project grows, these are the natural ownership lanes:

| Lane | Description | Current owner |
|---|---|---|
| **Core pipeline** | S0–S6 stage code, types, disambiguator | Shankar Mishra |
| **Hindi+English lexicons** | Roman-Hindi TSVs, abbreviations, SMS | Shankar Mishra |
| **Names/Brands gazetteer** | Wikidata-derived names and brands | Shankar Mishra |
| **Benchmark / eval** | IndianTTSBench-mini, metrics, gold set curation | Shankar Mishra |
| **Per-language lexicons (V2+)** | Marathi, Punjabi, Gujarati, Bengali, Tamil, Telugu | *Vacant — recruiting* |
| **Packaging / CI** | PyPI, GitHub Actions, dependency management | Shankar Mishra |
| **Documentation** | README, docs/, tutorials | Shankar Mishra |

Each language added in V2 **must** have a named human maintainer before it ships. A language without a maintainer will not be merged regardless of code quality — it will otherwise become abandoned scaffolding.

### 2.5 Succession plan

In the event the BDFL becomes permanently unavailable:

1. The GitHub repository, with its full history, is MIT-licensed and forkable by anyone.
2. Whoever has been the most recent active co-maintainer may declare a fork or continue under the name, provided they announce the transition clearly in the repository's README.
3. If no co-maintainer exists and the project is dormant for 6+ months with open issues, a community member may open a GitHub Discussion titled "Adopting maintenance of OpenHinglish" — the community can resolve this via rough consensus.
4. PyPI package ownership transfer follows PyPI's official abandoned package policy.

This is not ideal. It is the honest plan for a solo project with no funding.

---

## 3. Data Policies

Data quality and provenance are more important than code quality for this project. A bug in S3 can be patched; a compromised data license can force a full dataset purge and a broken release.

### 3.1 Provenance is required for every data contribution

Every row added to any TSV file under `src/openhinglish/data/` must carry a `source` field. Acceptable source values:

- Named open dataset with a verifiable license (e.g., `dakshina-v1.0`, `wikidata-Q{id}`, `mozilla-common-voice-17`).
- Personal knowledge / native-speaker judgment, labeled as `contributor-knowledge` — acceptable for small numbers of obvious corrections, not for bulk additions.
- Formal citation to a published wordlist with confirmed permissive license.

"I found it online" or "from a website" is not acceptable. If you cannot name the source, the row will not be merged.

### 3.2 No scraping

Do not contribute data scraped from websites, social media, or any source without explicit licensing for derived use. This includes:
- Twitter/X Hinglish data (Terms of Service restrict derived datasets)
- WhatsApp message dumps
- Blog or news site scrapes
- Any source that says "for research use only" without explicit commercial-OK permission

### 3.3 License vetting before merge

Before any new data source is introduced, the maintainer must:
1. Read the license text directly (not just the SPDX tag in a README — licenses change; see Spark-TTS going silently from Apache to NC).
2. Confirm the license allows redistribution and commercial use.
3. Record the license in `DATA_LICENSES.md` with a version or commit hash, a retrieval date, and the SPDX identifier.
4. Verify share-alike obligations and propagate them to any derived TSV files.

### 3.4 Attribution and licensing of contributed lexicon data

- Data contributed from CC0 sources (Wikidata, Mozilla Common Voice text): no attribution required in the output, but still logged in `DATA_LICENSES.md`.
- Data contributed from CC-BY-4.0 sources (AI4Bharat IndicVoices/IndicVoices-R): attribution in `DATA_LICENSES.md` and in the TSV file header comment. No obligation to share derivatives under the same terms.
- Data contributed from CC-BY-SA-4.0 sources (Google Dakshina): **share-alike applies**. The derived lexicon TSV file must carry a CC-BY-SA-4.0 header comment; downstream users who incorporate that TSV in their own data pipelines must apply share-alike. This is documented clearly in `DATA_LICENSES.md`. The *code* remains MIT; only the *data file* carries the SA obligation.
- Contributor-knowledge rows (small corrections, native-speaker judgments): the contributor grants an irrevocable CC0 dedication to that row by submitting the PR, documented in the PR itself.

### 3.5 Bulk data contributions

PR authors submitting more than 50 rows must include a "Provenance Declaration" in the PR description stating:
- Source name and URL
- License SPDX identifier and verification date
- Whether the data was derived, filtered, or used verbatim from the source
- Whether the contribution would change the license obligations of the receiving TSV file

Bulk contributions without this declaration will be closed without review.

---

## 4. Licensing Policies

### 4.1 Code: MIT

All source code under `src/`, `tests/`, `pyproject.toml`, and all documentation is licensed under the **MIT License**. This is a hard constraint and cannot be weakened by contributors. Do not submit code copied from GPL, LGPL, or any copyleft source.

### 4.2 Data files carry their source license

Data files (`.tsv` files under `src/openhinglish/data/`) are **not** automatically MIT. They carry the license of their contributing source. A TSV file derived entirely from CC0 sources is effectively CC0. A TSV file containing rows from Dakshina must carry CC-BY-SA-4.0. Mixed files should be split, not blended, when licenses conflict.

### 4.3 NEVER accept CC-BY-NC data

No data file may be derived from any source with a NonCommercial (NC) restriction. This includes:
- CC-BY-NC (any version)
- CC-BY-NC-SA (any version)
- CC-BY-NC-ND (any version)
- Any academic dataset with "non-commercial use only" in its terms, even without a standard SPDX tag

NC data cannot be shipped in a release that targets commercial Indian AI products. A PR introducing NC data will be rejected. If you are unsure, link the exact license text in the PR and ask.

### 4.4 CC-BY-SA share-alike handling

CC-BY-SA data can be accepted, but with obligations:

1. The derived data file must carry a CC-BY-SA-4.0 license header comment.
2. `DATA_LICENSES.md` must document the source and the share-alike obligation.
3. Downstream users are informed in the README that some data files carry CC-BY-SA.
4. **The code (MIT) and the data (CC-BY-SA) are legally distinct artifacts.** The code license does not change. Only the data file inherits the SA obligation. This is the same pattern used by projects like OpenStreetMap (ODbL data, MIT tools).
5. If share-alike contamination makes a file unworkable (e.g., a TSV that must be MIT for commercial embedding), the SA rows must be removed or replaced with CC0/CC-BY equivalents before that file can be relicensed.

### 4.5 The DATA_LICENSES.md ledger

`DATA_LICENSES.md` (to be created at repo root) is the **single source of truth for data provenance**. It must contain one row per data source, with:
- Source name
- URL or DOI
- License SPDX identifier
- Version or commit hash
- Date of retrieval/verification
- Files that derive from this source
- Any special obligations (share-alike, attribution text)

This file is reviewed and updated before every version release.

### 4.6 License re-verification before releases

Before any PyPI release (V1 and beyond), the maintainer must:
1. Re-read the license for every source in `DATA_LICENSES.md`.
2. Confirm no source has changed its license to NC or a more restrictive form since last verification.
3. Update the "last verified" date in `DATA_LICENSES.md`.
4. If any source has changed adversely, remove derived rows from the release and document the removal in the CHANGELOG.

This step is mandatory, not optional. The Spark-TTS case (silent Apache → NC change) is a real-world example of why this exists.

---

## 5. Voice and Data Compliance

### 5.1 India DPDP Act 2023 — awareness

The Digital Personal Data Protection (DPDP) Act 2023 is the governing data protection law in India. OpenHinglish does not collect, store, or process personal data as part of its operation — it is a stateless text normalizer. However:

- **Downstream TTS applications built on OpenHinglish may process personal data** (e.g., user utterances, names). Downstream developers are responsible for their own DPDP compliance.
- If this project ever adds a hosted API, server-side logging, or any form of telemetry, a formal DPDP compliance assessment is required before launch.
- This document and the README should warn downstream voice-application developers of their DPDP obligations.

### 5.2 No unconsented voice cloning

OpenHinglish is a **text normalization engine, not a voice synthesis tool.** It does not produce audio and does not contain voice embeddings or speaker identity data.

That said, its primary intended use case is as a preprocessing layer for TTS systems. The project explicitly:
- Does **not** include voice samples of real individuals.
- Does **not** provide tooling for cloning a specific person's voice.
- Does **not** recommend or endorse using TTS output to impersonate real individuals.

Contributors must not add data (e.g., phonetic annotations, audio-text pairs) derived from voice recordings of identifiable individuals without documented, verifiable consent. This rule applies even if the voice recording is "found online."

### 5.3 PII handling — names data

The names gazetteer (`src/openhinglish/data/gazetteers/names.tsv`) is used for proper noun detection and preservation. Rules:

- Names must come from **public, aggregate sources** — Wikidata entities (Q-IDs), census-grade name frequency lists, or similar.
- Do **not** add real individuals' phone numbers, addresses, or unique identifiers.
- "Shankar Mishra is a common Hindi name" is fine. "Shankar Mishra's phone number is..." is not data and would never appear in a TSV, but this principle extends to any PII.
- Name gazetteer entries are public names, not private-person data. If a name appears as a celebrity or public figure name, it may be included as a named entity with category `NAME`. No private individual profiles.

### 5.4 Relationship to downstream TTS responsibly

OpenHinglish's output (Devanagari text with `display_form` and `tts_form`) is consumed by TTS engines like IndicF5 or CosyVoice2. The project:
- Has no control over what voice the downstream TTS uses.
- Does not facilitate or enable any specific speaker's voice being used without consent.
- Encourages downstream integrators to:
  - Use consent-obtained speaker embeddings.
  - Disclose to end-users when AI-generated voice is being used.
  - Comply with the DPDP Act and applicable laws in their jurisdiction.

This project's README and any official integration guides will include a responsible-use notice for TTS developers.

---

## 6. Conduct and Security

### 6.1 Code of Conduct

This project follows a Code of Conduct documented in `CODE_OF_CONDUCT.md` (to be created; the Contributor Covenant 2.1 is the planned base). All participants — contributors, issue reporters, discussion participants — are expected to follow it. The current maintainer (Shankar Mishra) is the enforcement contact until a co-maintainer with moderation responsibilities is appointed.

### 6.2 Security disclosure

Security vulnerabilities (including data provenance fraud — a contributor deliberately submitting NC-licensed data as CC0) should be disclosed privately before public disclosure.

**Security contact:** Open a private GitHub Security Advisory at `https://github.com/<org>/openhinglish/security/advisories/new`. Do not open a public issue for a security vulnerability.

The full disclosure and response process will be documented in `SECURITY.md` (to be created). Expected response time: 7 business days for acknowledgment, 30 days for resolution or status update.

**Note:** `CODE_OF_CONDUCT.md` and `SECURITY.md` are referenced here but not yet created. They must be created before the V1 PyPI release.

---

## 7. Challenged Assumptions / Risks

This section is required by the project's own brief. It applies the same honesty demanded of all docs.

**7.1 Sustainability of solo curation**

The highest-value V1 work is scaling lexicons to 10k+ entries and building a 300-sentence gold benchmark. This is months of tedious, careful work for one person alongside a day job. There is no guarantee it gets done at the pace the roadmap implies. The governance model cannot fix this — only finding real co-maintainers or contributors early can.

**7.2 Contributor trust for data provenance**

This governance doc places heavy responsibility on contributors to self-certify provenance. In practice, a motivated contributor (or a naive one) could submit NC-licensed data with an incorrect CC0 declaration. The maintainer's review is a spot-check, not a legal audit. The mitigation is: keep a clear audit trail in `DATA_LICENSES.md`, re-verify before releases, and be prepared to yank and republish a release if contamination is discovered. The risk is real and cannot be eliminated by documentation alone.

**7.3 Governance overhead vs project size**

At V0.1 with zero external contributors, this governance document is significantly more elaborate than the project warrants. That is intentional — setting standards early is cheaper than retrofitting them. But there is a real risk of governance theater: writing policies that no one reads and that don't reflect actual practice. These policies are only useful if the maintainer actually enforces them when the first real PR arrives.

**7.4 Bus-factor = 1 remains unresolved**

All the mitigation steps in Section 2.2 are marked "Pending." Until at least one co-maintainer exists with PyPI access and repository admin rights, the project can realistically disappear if the BDFL becomes unavailable. This is the project's top existential risk. No governance document changes that — only action does.

**7.5 No CODE_OF_CONDUCT.md or SECURITY.md yet**

Both are referenced in this document but do not yet exist in the repository. This is a known gap that must be closed before V1 public release. Operating without them is acceptable at the foundation stage but not at the point of PyPI publication and active community recruitment.
