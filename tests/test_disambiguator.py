"""Tests for the ContextDisambiguator.

Tests prove that:
  1. "main road hai"  -> "main" resolves to ENGLISH (display "main", tts "मेन")
  2. "main ghar ja raha hu" -> "main" resolves to HINDI_ROMAN (display "मैं")
  3. "to" between two English tokens resolves to ENGLISH.
  4. FrequencyDisambiguator is a pure no-op (regression guard).
"""
from __future__ import annotations
from openhinglish import normalize
from openhinglish.types import Category
from openhinglish.disambiguator import FrequencyDisambiguator


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _token(result, surface_lower: str):
    """Return the first token whose surface (lowercased) matches."""
    for t in result.tokens:
        if t.surface.lower() == surface_lower:
            return t
    raise KeyError(f"No token with surface '{surface_lower}' in result")


# ---------------------------------------------------------------------------
# Core disambiguation rules
# ---------------------------------------------------------------------------

class TestMainRule:
    def test_main_before_english_noun_resolves_to_english(self):
        """'main road hai' — 'main' should be treated as English adjective."""
        res = normalize("main road hai")
        tok = _token(res, "main")
        assert tok.category == Category.ENGLISH, (
            f"Expected ENGLISH but got {tok.category}; trace={tok.trace}"
        )
        assert tok.display_form == "main"

    def test_main_before_english_noun_tts_is_english(self):
        """TTS for English 'main' should be the Hinglish phonetic 'मेन'."""
        res = normalize("main road hai")
        tok = _token(res, "main")
        assert tok.tts_form == "मेन", (
            f"Expected tts 'मेन' but got '{tok.tts_form}'"
        )

    def test_main_before_hindi_noun_resolves_to_hindi(self):
        """'main ghar ja raha hu' — 'main' should remain Hindi pronoun मैं."""
        res = normalize("main ghar ja raha hu")
        tok = _token(res, "main")
        assert tok.category == Category.HINDI_ROMAN, (
            f"Expected HINDI_ROMAN but got {tok.category}; trace={tok.trace}"
        )
        assert tok.display_form == "मैं"

    def test_main_before_hindi_noun_tts_is_hindi(self):
        res = normalize("main ghar ja raha hu")
        tok = _token(res, "main")
        assert tok.tts_form == "मैं"

    def test_main_hindi_trace_present(self):
        """HINDI_ROMAN path leaves no V3 trace (no disambiguation needed)."""
        res = normalize("main ghar ja raha hu")
        tok = _token(res, "main")
        v3_traces = [t for t in tok.trace if t.startswith("V3:")]
        assert len(v3_traces) == 0

    def test_main_english_trace_present(self):
        """ENGLISH path appends a V3 trace entry."""
        res = normalize("main road hai")
        tok = _token(res, "main")
        v3_traces = [t for t in tok.trace if t.startswith("V3:")]
        assert len(v3_traces) == 1
        assert "ENGLISH" in v3_traces[0]
        assert "context" in v3_traces[0]


class TestToRule:
    def test_to_between_english_tokens_resolves_to_english(self):
        """'call to work' — both neighbours are ENGLISH, so 'to' is English preposition."""
        res = normalize("call to work")
        tok = _token(res, "to")
        assert tok.category == Category.ENGLISH, (
            f"Expected ENGLISH but got {tok.category}; trace={tok.trace}"
        )

    def test_to_after_hindi_resolves_to_hindi(self):
        """'suno to bhai' — 'to' is Hindi 'तो' (particle); prev is HINDI_ROMAN."""
        res = normalize("suno to bhai")
        tok = _token(res, "to")
        # Both neighbours are HINDI_ROMAN, so rule should not fire → stays HINDI_ROMAN.
        assert tok.category == Category.HINDI_ROMAN, (
            f"Expected HINDI_ROMAN but got {tok.category}; trace={tok.trace}"
        )


# ---------------------------------------------------------------------------
# End-to-end display string sanity
# ---------------------------------------------------------------------------

class TestDisplayOutput:
    def test_main_road_display(self):
        """Full display string for 'main road hai'."""
        res = normalize("main road hai")
        # "main" stays roman (ENGLISH display = surface), "road" stays roman,
        # "hai" → "है"
        assert res.display == "main road है"

    def test_main_ghar_display(self):
        """Full display string for 'main ghar ja raha hu'."""
        res = normalize("main ghar ja raha hu")
        # "main" → मैं, "ghar" → घर, "ja" → जा, "raha" → रहा, "hu" → UNKNOWN (surface)
        assert res.display == "मैं घर जा रहा hu"


# ---------------------------------------------------------------------------
# Regression: FrequencyDisambiguator must remain a pure no-op
# ---------------------------------------------------------------------------

class TestFrequencyDisambiguatorNoOp:
    def test_noop_returns_same_list(self):
        from openhinglish.types import Config
        from openhinglish.pipeline.s0_preprocess import tokenize
        from openhinglish.pipeline.s1_classify import classify

        cfg = Config()
        tokens = classify(tokenize("main road hai", cfg), cfg)
        fd = FrequencyDisambiguator()
        result = fd.resolve(tokens, cfg)
        assert result is tokens  # same object, no mutation

    def test_noop_does_not_change_category(self):
        from openhinglish.types import Config
        from openhinglish.pipeline.s0_preprocess import tokenize
        from openhinglish.pipeline.s1_classify import classify

        cfg = Config()
        tokens = classify(tokenize("main road hai", cfg), cfg)
        cats_before = [t.category for t in tokens]
        FrequencyDisambiguator().resolve(tokens, cfg)
        cats_after = [t.category for t in tokens]
        assert cats_before == cats_after


# ---------------------------------------------------------------------------
# Determinism: disambiguator must be deterministic
# ---------------------------------------------------------------------------

def test_disambiguation_is_deterministic():
    a = normalize("main road hai")
    b = normalize("main road hai")
    assert a.display == b.display
    assert a.tts == b.tts


# ---------------------------------------------------------------------------
# Safety: unknown surface not in rules leaves token untouched
# ---------------------------------------------------------------------------

def test_unknown_word_not_in_rules_unchanged():
    """A word not in _RULES must pass through completely unmodified."""
    res = normalize("kya chal raha hai")
    tok = _token(res, "kya")
    assert tok.category == Category.HINDI_ROMAN
    v3_traces = [t for t in tok.trace if t.startswith("V3:")]
    assert len(v3_traces) == 0
