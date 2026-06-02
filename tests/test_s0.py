from openhinglish.pipeline.s0_preprocess import tokenize
from openhinglish.types import Category, Config


def test_word_tokenization_with_spans():
    toks = tokenize("bhai kal mera intv h paytm me", Config())
    assert [t.surface for t in toks] == ["bhai", "kal", "mera", "intv", "h", "paytm", "me"]
    assert (toks[0].start, toks[0].end) == (0, 4)
    assert all(t.category == Category.UNKNOWN for t in toks)


def test_structural_categories():
    toks = tokenize("call me! visit https://a.co 4", Config())
    cats = {t.surface: t.category for t in toks}
    assert cats["!"] == Category.PUNCT
    assert cats["https://a.co"] == Category.URL
    assert cats["4"] == Category.NUMBER


def test_passthrough_forms_default_to_surface():
    toks = tokenize("!", Config())
    assert toks[0].display_form == "!" and toks[0].tts_form == "!"
