from __future__ import annotations


def exact_match(pred: str, ref: str) -> float:
    return 1.0 if pred.strip() == ref.strip() else 0.0


def cer(pred: str, ref: str) -> float:
    pred, ref = pred.strip(), ref.strip()
    if not ref:
        return 0.0 if not pred else 1.0
    prev = list(range(len(ref) + 1))
    for i, pc in enumerate(pred, 1):
        cur = [i]
        for j, rc in enumerate(ref, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (pc != rc)))
        prev = cur
    return prev[-1] / len(ref)


def per_category(rows: list[dict], field: str) -> dict[str, float]:
    groups: dict[str, list[float]] = {}
    for r in rows:
        groups.setdefault(r["category"], []).append(r[field])
    return {k: sum(v) / len(v) for k, v in groups.items()}
