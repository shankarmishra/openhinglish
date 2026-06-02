from openhinglish.pipeline.s3_translit import transliterate, akshara_fallback
from openhinglish.types import Token, Category, Config


def _tok(surface, category, display=None, tts=None):
    return Token(surface=surface, start=0, end=len(surface), category=category,
                 display_form=display or surface, tts_form=tts or surface)


def test_known_roman_hindi_uses_lookup():
    toks = transliterate([_tok("kal", Category.HINDI_ROMAN)], Config())
    assert toks[0].display_form == "कल"
    assert toks[0].tts_form == "कल"


def test_english_keeps_latin_display_but_devanagari_tts_when_known():
    t = _tok("interview", Category.ENGLISH)
    out = transliterate([t], Config())[0]
    assert out.display_form == "interview"
    assert out.tts_form == "इंटरव्यू"


def test_oov_roman_hindi_uses_akshara_fallback():
    out = transliterate([_tok("ghar", Category.HINDI_ROMAN)], Config())[0]
    assert out.display_form == akshara_fallback("ghar")
    assert out.display_form != "ghar"
