# EXPERIMENTAL: Audio Adapter for OpenHinglish (IndicF5 TTS)

> **Status: EXPERIMENTAL** — API and model integration details may change.
> The base `openhinglish` package is unaffected; this adapter is entirely optional.

---

## What is this?

OpenHinglish converts Roman-Hinglish text (e.g. `"bhai kal mera intv h paytm me"`) into a clean Devanagari string optimised for Text-To-Speech engines (the `.tts` field of a `NormalizationResult`).  It does **not** generate audio itself.

This adapter bridges that `.tts` string to **AI4Bharat IndicF5**, an open-weight Hindi TTS model (MIT licence), so you get a complete pipeline:

```
Roman-Hinglish text
       │
       ▼  openhinglish.normalize()
Devanagari TTS string
       │
       ▼  IndicF5 (this adapter)
WAV audio file
```

---

## Why is it separate and optional?

| Reason | Detail |
|--------|--------|
| **Size** | IndicF5 weights are several gigabytes. Bundling them as a hard dependency would make `pip install openhinglish` unusable for most users. |
| **Hardware** | Inference requires either a CUDA GPU or extreme patience on CPU (see below). |
| **Choice** | Users may prefer a different TTS backend (e.g. CosyVoice2, Coqui TTS, Google TTS). The core package stays backend-agnostic. |

The base package (`openhinglish.normalize()` etc.) has **zero heavy dependencies** and always works without PyTorch or Transformers.

---

## Installation

```bash
pip install "openhinglish[tts]"
```

This installs:

| Package | Min version | Purpose |
|---------|-------------|---------|
| `torch` | 2.2 | Model inference |
| `transformers` | 4.40 | Load IndicF5 via AutoClass API |
| `soundfile` | 0.12 | Read/write WAV files |
| `huggingface-hub` | 0.23 | Manage model cache |

> **Note:** The model weights themselves are downloaded automatically on first use by Hugging Face Hub.

---

## Model download & CPU caveat

On first use the adapter downloads the IndicF5 checkpoint from Hugging Face Hub.

- **Download size:** several gigabytes (check the [IndicF5 model card](https://huggingface.co/ai4bharat/IndicF5) for the current size).
- **Cached location:** `~/.cache/huggingface/hub/` (standard HF cache; set `HF_HOME` to override).
- **GPU recommended:** inference on a CUDA GPU takes a few seconds per sentence.
- **CPU warning:** inference on CPU is very slow — expect **60–180 seconds** per short sentence on a mid-range laptop.  The adapter emits a `RuntimeWarning` when no GPU is detected.

---

## IndicF5 reference-voice requirement

IndicF5 is a **zero-shot, reference-conditioned** TTS model: it clones the voice style from a short audio clip you provide.  This means:

1. You need a **reference WAV file** — a 5–10 second clean recording of the target speaker.
2. You also need the **transcript** of that clip (Devanagari or Roman script).

Without these, the adapter raises a clear `ValueError` rather than silently producing bad output.

```python
synthesize(
    result,
    ref_audio="my_voice.wav",    # required
    ref_text="नमस्ते मेरा नाम शंकर है",  # required
)
```

If you do not have a reference clip, consider a non-reference TTS backend such as CosyVoice2 (see below).

---

## Runnable example

```python
from openhinglish.adapters.indicf5 import normalize_and_speak

# Full pipeline: Roman-Hinglish text → Devanagari → WAV
path = normalize_and_speak(
    "bhai kal mera intv h paytm me",
    "demo.wav",
    ref_audio="my_voice.wav",          # 5–10 s reference clip
    ref_text="नमस्ते मेरा नाम शंकर है",  # transcript of the clip
)
print(f"Audio written to: {path}")
```

Step-by-step (lower-level):

```python
import openhinglish
from openhinglish.adapters.indicf5 import synthesize

result = openhinglish.normalize("bhai kal mera intv h paytm me")
print(result.tts)   # e.g. "भाई कल मेरा इंटरव्यू है पेटीएम में"

path = synthesize(
    result,           # or pass result.tts directly as a string
    out_path="demo.wav",
    ref_audio="my_voice.wav",
    ref_text="नमस्ते मेरा नाम शंकर है",
)
```

---

## Alternative backend: CosyVoice2

[CosyVoice2](https://github.com/FunAudioLLM/CosyVoice) (Apache 2.0) is a strong alternative Hindi TTS model that also supports zero-shot voice cloning with a similar reference-audio interface.  A `cosyvoice2.py` adapter can be added to `src/openhinglish/adapters/` following the same lazy-import pattern used in `indicf5.py`.

Key differences:

| | IndicF5 | CosyVoice2 |
|-|---------|------------|
| Licence | MIT | Apache 2.0 |
| Hindi quality | Optimised for Indic scripts | Strong multilingual |
| Reference needed | Yes | Yes (for voice clone mode) |
| Inference API | Transformers AutoClass | Custom `CosyVoice` class |

---

## Troubleshooting

| Error | Likely cause | Fix |
|-------|-------------|-----|
| `ImportError: openhinglish[tts] optional dependencies are missing` | Heavy deps not installed | `pip install "openhinglish[tts]"` |
| `ValueError: IndicF5 is a reference-conditioned model` | `ref_audio`/`ref_text` not passed | Provide both arguments |
| `FileNotFoundError: ref_audio not found` | Wrong path to reference WAV | Check the path |
| Very slow inference | Running on CPU | Use a machine with a CUDA GPU |
| `AutoModelForTextToWaveform` not found | Transformers version too old | `pip install -U transformers>=4.40` |

---

## API surface

```
src/openhinglish/adapters/
    __init__.py       — empty (no top-level imports)
    indicf5.py
        synthesize(text_or_result, out_path, model_id, ref_audio, ref_text) -> str
        normalize_and_speak(raw_text, out_path, **kw) -> str
```

Both functions are safe to import without the heavy deps installed — they only raise `ImportError` at call time.
