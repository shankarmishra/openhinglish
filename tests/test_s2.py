from openhinglish.pipeline.s0_preprocess import tokenize
from openhinglish.pipeline.s1_classify import classify
from openhinglish.pipeline.s2_spellnorm import spell_normalize
from openhinglish.types import Category, Config


def _run(text):
    c = Config()
    return spell_normalize(classify(tokenize(text, c), c), c)


def test_abbrev_expansion_reclassifies():
    tok = {t.surface: t for t in _run("intv h")}
    assert tok["intv"].display_form == "interview"
    assert tok["intv"].category == Category.ENGLISH
    assert any("S2" in tr for tr in tok["intv"].trace)


def test_confident_exact_match_not_rewritten():
    tok = _run("interview")[0]
    assert tok.display_form == "interview"
    assert not any("typo" in tr for tr in tok.trace)


def test_original_kept_as_alternative_on_typo_fix():
    tok = _run("intervew")[0]
    assert tok.display_form == "interview"
    assert any(a.display_form == "intervew" for a in tok.alternatives)
