from openhinglish.pipeline.s0_preprocess import tokenize
from openhinglish.pipeline.s1_classify import classify
from openhinglish.types import Category, Config


def _classify(text):
    return classify(tokenize(text, Config()), Config())


def test_devanagari_is_hindi_deva():
    toks = _classify("कल")
    assert toks[0].category == Category.HINDI_DEVA


def test_roman_hindi_and_english_and_brand():
    toks = {t.surface: t for t in _classify("kal interview paytm")}
    assert toks["kal"].category == Category.HINDI_ROMAN
    assert toks["interview"].category == Category.ENGLISH
    assert toks["paytm"].category == Category.BRAND


def test_collision_keeps_alternatives_sorted():
    tok = _classify("me")[0]
    cats = [tok.category] + [a.category for a in tok.alternatives]
    assert Category.HINDI_ROMAN in cats
    scores = [tok.confidence] + [a.score for a in tok.alternatives]
    assert scores == sorted(scores, reverse=True)


def test_structural_tokens_untouched():
    tok = _classify("!")[0]
    assert tok.category == Category.PUNCT
