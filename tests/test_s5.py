from openhinglish.pipeline.s5_numerals import expand_numerals, number_to_hindi_words
from openhinglish.types import Token, Category, Config


def _num(surface):
    return Token(surface=surface, start=0, end=len(surface), category=Category.NUMBER,
                 display_form=surface, tts_form=surface)


def test_number_words_hindi():
    assert number_to_hindi_words(4) == "चार"
    assert number_to_hindi_words(100) == "सौ"
    assert number_to_hindi_words(0) == "शून्य"


def test_number_tts_uses_hindi_by_default():
    out = expand_numerals([_num("4")], Config())[0]
    assert out.display_form == "4"
    assert out.tts_form == "चार"


def test_number_tts_english_config():
    out = expand_numerals([_num("4")], Config(number_words_lang="english"))[0]
    assert out.tts_form == "four"


def test_acronym_expanded_letterwise():
    t = Token(surface="RBI", start=0, end=3, category=Category.ENGLISH,
              display_form="RBI", tts_form="RBI")
    out = expand_numerals([t], Config())[0]
    assert out.category == Category.ACRONYM
    assert out.tts_form == "आर बी आई"
