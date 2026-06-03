---
title: OpenHinglish Demo
emoji: 🪔
colorFrom: orange
colorTo: green
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
short_description: Roman-Hinglish to Devanagari text normalization for Indian TTS
---

# OpenHinglish — live demo

Type Roman-script Hinglish and instantly see both normalized outputs (`display`
and `tts`), per-token confidence, n-best alternatives, and the explainability
trace.

This Space is a thin Gradio front-end over the
[OpenHinglish](https://github.com/shankarmishra/openhinglish) library
(MIT-licensed, deterministic, CPU-only).

## Deploy this Space

1. Create a new **Gradio** Space on Hugging Face.
2. Upload `app.py`, `requirements.txt`, and this `README.md` (with the YAML
   front matter above — Hugging Face reads it to configure the Space).
3. The Space builds automatically and goes live at
   `https://huggingface.co/spaces/<your-username>/openhinglish-demo`.

## Run locally

```bash
pip install gradio openhinglish
python app.py
```
