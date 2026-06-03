"""FastAPI REST server for OpenHinglish.

Run via:
    python -m openhinglish.api.server
    python -m openhinglish.api.server --host 0.0.0.0 --port 9000

Or with uvicorn directly (after pip install 'openhinglish[server]'):
    uvicorn openhinglish.api.server:app
"""
from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from openhinglish import normalize
from openhinglish.types import Config

app = FastAPI(title="OpenHinglish", version="0.1.0")


class NormalizeRequest(BaseModel):
    text: str
    number_words_lang: str = "hindi"  # "hindi" | "english"


def _result_to_dict(res) -> dict:
    return {
        "input": res.input,
        "display": res.display,
        "tts": res.tts,
        "confidence": res.confidence,
        "tokens": [
            {
                "surface": t.surface,
                "category": t.category.value,
                "display_form": t.display_form,
                "tts_form": t.tts_form,
                "confidence": round(t.confidence, 3),
                "alternatives": [
                    {
                        "category": a.category.value,
                        "display_form": a.display_form,
                        "tts_form": a.tts_form,
                        "score": round(a.score, 3),
                    }
                    for a in t.alternatives
                ],
                "trace": t.trace,
            }
            for t in res.tokens
        ],
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/normalize")
def normalize_endpoint(req: NormalizeRequest) -> dict:
    config = Config(number_words_lang=req.number_words_lang)
    res = normalize(req.text, config)
    return _result_to_dict(res)


def main(host: str = "127.0.0.1", port: int = 8000) -> None:
    try:
        import uvicorn
    except ImportError as exc:
        raise ImportError(
            "uvicorn is not installed. "
            "Run: pip install 'openhinglish[server]'"
        ) from exc
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="OpenHinglish FastAPI server")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Bind port (default: 8000)")
    args = parser.parse_args()
    main(host=args.host, port=args.port)
