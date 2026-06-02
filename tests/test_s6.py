from openhinglish.pipeline.s6_assemble import assemble
from openhinglish.types import Token, Category, Config


def test_assemble_builds_two_strings_and_confidence():
    toks = [
        Token(surface="kal", start=0, end=3, category=Category.HINDI_ROMAN,
              display_form="कल", tts_form="कल", confidence=0.9),
        Token(surface="!", start=3, end=4, category=Category.PUNCT,
              display_form="!", tts_form="!", confidence=0.0),
    ]
    res = assemble(toks, Config(), "kal!")
    assert res.display == "कल!"          # no space before punctuation
    assert res.tts == "कल!"
    assert 0.0 < res.confidence <= 1.0   # PUNCT excluded from confidence average
