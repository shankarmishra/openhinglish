---
name: Bug report
about: Report incorrect normalization, wrong Devanagari output, or a crash
title: "[BUG] "
labels: bug
assignees: ''
---

## Input text

Paste the exact string you passed to `normalize()` (include the original casing and script):

```
<paste input here>
```

## Expected output

**display:** (what the Devanagari display form should look like)

**tts:** (what the TTS phoneme string should look like)

## Actual output

**display:**

**tts:**

**confidence:** (if shown)

## Token trace (if available)

Run the following snippet and paste the output:

```python
from openhinglish import normalize

result = normalize("<your input>")
for tok in result.tokens:
    print(tok.surface, tok.category, tok.display_form, tok.tts_form)
    for step in tok.trace:
        print("  trace:", step)
```

```
<paste trace output here>
```

## Environment

- OS:
- Python version (`python --version`):
- openhinglish version (`pip show openhinglish | grep Version`):
- Installed via: `pip install openhinglish` / `pip install -e ".[dev]"` / other

## Additional context

Any other details, edge cases, or related words that exhibit the same issue.
