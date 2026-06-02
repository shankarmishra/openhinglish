from openhinglish.eval.metrics import exact_match, cer, per_category


def test_exact_match():
    assert exact_match("कल", "कल") == 1.0
    assert exact_match("कल", "आज") == 0.0


def test_cer():
    assert cer("कल", "कल") == 0.0
    assert 0.0 < cer("कल", "कक") <= 1.0


def test_per_category_groups_and_averages():
    rows = [
        {"category": "code-switch", "display_em": 1.0},
        {"category": "code-switch", "display_em": 0.0},
        {"category": "names", "display_em": 1.0},
    ]
    out = per_category(rows, "display_em")
    assert out["code-switch"] == 0.5
    assert out["names"] == 1.0
