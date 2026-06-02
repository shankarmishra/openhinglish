from __future__ import annotations
import csv
from dataclasses import dataclass
from functools import lru_cache
from importlib.resources import files


def _open(rel_path: str):
    return files("openhinglish.data").joinpath(rel_path).open("r", encoding="utf-8")


def _rows(rel_path: str):
    with _open(rel_path) as fh:
        for row in csv.reader(fh, delimiter="\t"):
            if row and not row[0].startswith("#"):
                yield row


@lru_cache(maxsize=None)
def load_map(rel_path: str, key_col: int = 0, val_col: int = 1) -> dict[str, str]:
    return {r[key_col].strip(): r[val_col].strip() for r in _rows(rel_path)}


@lru_cache(maxsize=None)
def load_set(rel_path: str, col: int = 0) -> frozenset[str]:
    return frozenset(r[col].strip() for r in _rows(rel_path))


@dataclass(frozen=True)
class Entity:
    display: str
    pron_deva: str


@lru_cache(maxsize=None)
def load_gazetteer(rel_path: str) -> dict[str, Entity]:
    return {r[0].strip().lower(): Entity(r[1].strip(), r[2].strip()) for r in _rows(rel_path)}
