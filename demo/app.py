"""OpenHinglish — live demo (Hugging Face Space / local Gradio app).

Type Roman-Hinglish text and instantly see both normalized outputs
(`display` and `tts`), per-token detail, confidence, and the explainability
trace. No install required for the visitor — that is the whole point.

Run locally:   python demo/app.py
Deploy:        push app.py + requirements.txt + README.md to a Gradio HF Space.
"""

import gradio as gr

from openhinglish import normalize, Config

EXAMPLES = [
    ["bhai kal mera intv h paytm me", False],
    ["main road pe interview hai", False],
    ["UPI se payment karo", False],
    ["yaar mujhe 2 din me reply karo", False],
    ["priya ne flipkart se order kiya", False],
    ["office me meeting hai kal subah", False],
    ["mujhe 2 din chahiye", True],
]


def analyze(text: str, english_numbers: bool):
    """Run normalization and return (display, tts, summary_md, token_rows)."""
    text = (text or "").strip()
    if not text:
        return "", "", "_Type some Roman-Hinglish text above._", []

    cfg = Config(number_words_lang="english" if english_numbers else "hindi")
    result = normalize(text, config=cfg)

    summary = (
        f"**Aggregate confidence:** {result.confidence:.2f} &nbsp;|&nbsp; "
        f"**Tokens:** {len(result.tokens)}"
    )

    rows = []
    for tok in result.tokens:
        alts = ", ".join(
            f"{a.display_form}/{a.tts_form} ({a.score:.2f})" for a in tok.alternatives
        ) or "—"
        trace = "  →  ".join(tok.trace)
        rows.append(
            [
                tok.surface,
                tok.category.name,
                tok.display_form,
                tok.tts_form,
                f"{tok.confidence:.2f}",
                alts,
                trace,
            ]
        )
    return result.display, result.tts, summary, rows


DESCRIPTION = """
# 🪔 OpenHinglish — Roman-Hinglish → Devanagari normalization

The missing pre-processing layer for Indian voice & language AI. Type how Indians
actually type — Roman-script Hindi, code-switched with English, brands, and
abbreviations — and get **two** clean outputs:

- **`display`** — human-readable, mixed-script (keeps `interview`, `Paytm` in Roman)
- **`tts`** — fully Devanagari, ready to feed a TTS engine (IndicF5 / Indic-Parler-TTS / CosyVoice2)

Deterministic · explainable · CPU-only · no API key · MIT-licensed.
[GitHub](https://github.com/shankarmishra/openhinglish) ·
honest benchmark: **0.92 display EM / 0.92 TTS EM** on 59 sentences (alpha — coverage still growing).
"""

with gr.Blocks(title="OpenHinglish Demo", theme=gr.themes.Soft()) as demo:
    gr.Markdown(DESCRIPTION)

    with gr.Row():
        with gr.Column(scale=3):
            inp = gr.Textbox(
                label="Roman-Hinglish input",
                placeholder="bhai kal mera intv h paytm me",
                lines=2,
            )
        with gr.Column(scale=1, min_width=160):
            eng_num = gr.Checkbox(label="Numbers as English words", value=False)
            btn = gr.Button("Normalize", variant="primary")

    with gr.Row():
        out_display = gr.Textbox(label="display  (for humans)", interactive=False)
        out_tts = gr.Textbox(label="tts  (for the TTS engine)", interactive=False)

    summary = gr.Markdown()

    tokens = gr.Dataframe(
        headers=["surface", "category", "display", "tts", "conf", "alternatives", "trace"],
        label="Per-token detail (with explainability trace)",
        wrap=True,
    )

    gr.Examples(examples=EXAMPLES, inputs=[inp, eng_num])

    btn.click(analyze, inputs=[inp, eng_num], outputs=[out_display, out_tts, summary, tokens])
    inp.submit(analyze, inputs=[inp, eng_num], outputs=[out_display, out_tts, summary, tokens])


if __name__ == "__main__":
    demo.launch()
