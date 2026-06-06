from openhinglish.types import Category, Token, NormalizationResult, Config


def test_token_defaults():
    t = Token(surface="kal", start=0, end=3)
    assert t.category == Category.UNKNOWN
    assert t.alternatives == []
    assert t.trace == []
    # mutable defaults must be independent instances
    t.trace.append("x")
    assert Token(surface="a", start=0, end=1).trace == []


def test_result_and_config():
    tok = Token(surface="kal", start=0, end=3, display_form="कल", tts_form="कल")
    res = NormalizationResult(input="kal", display="कल", tts="कल",
                              confidence=1.0, tokens=[tok])
    assert res.tokens[0].display_form == "कल"
    assert Config().nbest_k == 3
    assert Config().number_words_lang == "hindi"
