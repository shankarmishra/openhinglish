# Security Policy

OpenHinglish is a pure-Python text-processing library with no network or filesystem side effects
at runtime. Still, we take a few classes of issue seriously and welcome responsible disclosure.

## Reporting a vulnerability
Please report security issues **privately** — do **not** open a public issue for a security problem.

**Preferred:** use GitHub's private vulnerability reporting on this repository
([Security tab → "Report a vulnerability"](https://github.com/shankarmishra/openhinglish/security/advisories/new)).
This keeps the report confidential between you and the maintainer, with no email exposed.

If you cannot use GitHub advisories, you may email **xshankarmishra@gmail.com** as a fallback.

Include, if possible:
- A description of the issue and its impact.
- Steps to reproduce (input text, code, environment).
- Any suggested fix.

We aim to acknowledge reports within a few days and to address confirmed issues as quickly as is
practical for a volunteer-maintained project.

## In scope
- **ReDoS** (catastrophic regex backtracking) in the tokenizer or any stage's regular expressions.
- **Data-poisoning** concerns in the lexicons/gazetteers (entries that could cause harmful or
  systematically wrong normalizations).
- Crashes / unhandled exceptions on adversarial input that break the `normalize()` contract.
- Issues in the optional web console (`api/webui`) or server when run locally.

## Out of scope
- The optional audio adapter's third-party model dependencies (report those upstream to the model
  authors, e.g. IndicF5 / CosyVoice2).
- Running the local web console exposed to an untrusted network (it is intended for local use).

## Supported versions
The project is pre-1.0. Security fixes are applied to the latest `main` only.
