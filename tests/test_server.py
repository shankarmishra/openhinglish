"""Tests for the FastAPI REST server.

Skipped automatically when fastapi is not installed, so the core test suite
remains clean in environments that don't have the [server] extra.
"""
import pytest

fastapi = pytest.importorskip("fastapi")

from fastapi.testclient import TestClient  # noqa: E402 — after importorskip

from openhinglish.api.server import app  # noqa: E402

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_normalize_display_and_tts():
    resp = client.post(
        "/normalize",
        json={"text": "bhai kal mera intv h paytm me"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["display"] == "भाई कल मेरा interview है Paytm में"
    assert data["tts"] == "भाई कल मेरा इंटरव्यू है पे-टी-एम में"


def test_tokens_category_is_string():
    resp = client.post(
        "/normalize",
        json={"text": "bhai kal mera intv h paytm me"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["tokens"], "tokens list must not be empty"
    for token in data["tokens"]:
        assert isinstance(token["category"], str), (
            f"category must be a string, got {type(token['category'])!r} "
            f"for token {token['surface']!r}"
        )


def test_tokens_have_non_empty_trace():
    resp = client.post(
        "/normalize",
        json={"text": "bhai kal mera intv h paytm me"},
    )
    assert resp.status_code == 200
    data = resp.json()
    for token in data["tokens"]:
        assert token["trace"], (
            f"token {token['surface']!r} has an empty trace"
        )


def test_normalize_english_numbers():
    resp = client.post(
        "/normalize",
        json={"text": "bhai kal mera intv h paytm me", "number_words_lang": "english"},
    )
    assert resp.status_code == 200
    data = resp.json()
    # display and tts fields must be present and non-empty strings
    assert isinstance(data["display"], str) and data["display"]
    assert isinstance(data["tts"], str) and data["tts"]
