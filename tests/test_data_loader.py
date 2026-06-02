from openhinglish.data_loader import load_map, load_set, load_gazetteer


def test_roman_hindi_map():
    m = load_map("lexicons/roman_hindi.tsv", key_col=0, val_col=1)
    assert m["kal"] == "कल"
    assert m["bhai"] == "भाई"


def test_english_set():
    s = load_set("lexicons/english_freq.tsv", col=0)
    assert "interview" in s


def test_gazetteer_brands():
    g = load_gazetteer("gazetteers/brands.tsv")
    assert g["paytm"].display == "Paytm"
    assert g["paytm"].pron_deva == "पे-टी-एम"
