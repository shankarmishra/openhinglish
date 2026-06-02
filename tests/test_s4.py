from openhinglish.pipeline.s0_preprocess import tokenize
from openhinglish.pipeline.s1_classify import classify
from openhinglish.pipeline.s4_names_brands import resolve_entities
from openhinglish.types import Category, Config


def _run(text):
    c = Config()
    return resolve_entities(classify(tokenize(text, c), c), c)


def test_brand_display_latin_tts_devanagari():
    tok = {t.surface.lower(): t for t in _run("paytm")}
    assert tok["paytm"].category == Category.BRAND
    assert tok["paytm"].display_form == "Paytm"
    assert tok["paytm"].tts_form == "पे-टी-एम"


def test_titlecase_promotes_name_candidate():
    tok = _run("Shankar")[0]
    assert tok.category == Category.NAME
    assert tok.display_form == "Shankar"
    assert tok.tts_form == "शंकर"


def test_lowercase_collision_does_not_overfire():
    tok = _run("mishra")[0]
    assert tok.category == Category.NAME
