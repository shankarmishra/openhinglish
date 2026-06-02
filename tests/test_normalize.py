from openhinglish import normalize


def test_worked_example_end_to_end():
    res = normalize("bhai kal mera intv h paytm me")
    assert res.display == "भाई कल मेरा interview है Paytm में"
    assert res.tts == "भाई कल मेरा इंटरव्यू है पे-टी-एम में"


def test_every_token_has_a_trace():
    res = normalize("bhai kal mera intv h paytm me")
    assert all(t.trace for t in res.tokens)


def test_determinism():
    a = normalize("bhai kal mera intv h paytm me")
    b = normalize("bhai kal mera intv h paytm me")
    assert a.display == b.display and a.tts == b.tts
