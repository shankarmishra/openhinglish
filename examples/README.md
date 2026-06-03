# Examples

These scripts demonstrate the OpenHinglish public API and are meant to be run
from the repo root after installing the package.

## Prerequisites

```bash
pip install -e ".[dev,cli,server]"
```

## Scripts

### quickstart.py

Runs four example Hinglish sentences through `normalize()` and prints the
`display` form, `tts` form, overall confidence, and a per-token breakdown
table (surface, category, display_form, tts_form, confidence).

```bash
python examples/quickstart.py
```

### inspect_traces.py

Runs a single sentence and pretty-prints every token's full `trace` list,
showing each pipeline decision that led to the final normalization. Useful
for debugging or understanding the explainability data.

```bash
python examples/inspect_traces.py
```

## Windows note

Both scripts call `sys.stdout.reconfigure(encoding="utf-8")` at startup so
Devanagari characters render correctly in Windows terminals. If you still see
encoding errors, set the environment variable before running:

```powershell
$env:PYTHONIOENCODING = "utf-8"
python examples/quickstart.py
```
