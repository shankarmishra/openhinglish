from __future__ import annotations
from typing import Protocol
from openhinglish.types import Token, Config


class Disambiguator(Protocol):
    def resolve(self, tokens: list[Token], config: Config) -> list[Token]:
        ...


class FrequencyDisambiguator:
    """V1 no-op: S1 already ranked by frequency prior. Seam for the V1.1 learned layer."""

    def resolve(self, tokens: list[Token], config: Config) -> list[Token]:
        return tokens
