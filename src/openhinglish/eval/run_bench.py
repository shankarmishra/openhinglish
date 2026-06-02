from __future__ import annotations
import csv
from importlib.resources import files
from openhinglish import normalize
from openhinglish.eval.metrics import exact_match, cer, per_category


def load_bench() -> list[dict]:
    path = files("openhinglish.eval.bench_mini").joinpath("sentences.tsv")
    with path.open("r", encoding="utf-8") as fh:
        return [
            {"input": r[0], "ref_display": r[1], "ref_tts": r[2], "category": r[3]}
            for r in csv.reader(fh, delimiter="\t") if r and not r[0].startswith("#")
        ]


def main() -> None:
    rows = []
    for ex in load_bench():
        res = normalize(ex["input"])
        rows.append({
            "category": ex["category"],
            "display_em": exact_match(res.display, ex["ref_display"]),
            "tts_em": exact_match(res.tts, ex["ref_tts"]),
            "tts_cer": cer(res.tts, ex["ref_tts"]),
        })
    for field in ("display_em", "tts_em", "tts_cer"):
        print(f"\n== {field} (per category) ==")
        for cat, val in sorted(per_category(rows, field).items()):
            print(f"  {cat:14s} {val:.3f}")
    n = len(rows)
    print(f"\nOverall display EM: {sum(r['display_em'] for r in rows)/n:.3f}  (n={n})")


if __name__ == "__main__":
    main()
