from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class Category(str, Enum):
    HINDI_ROMAN = "HINDI_ROMAN"
    HINDI_DEVA = "HINDI_DEVA"
    ENGLISH = "ENGLISH"
    NAME = "NAME"
    BRAND = "BRAND"
    NUMBER = "NUMBER"
    DATE = "DATE"
    TIME = "TIME"
    ACRONYM = "ACRONYM"
    PUNCT = "PUNCT"
    EMOJI = "EMOJI"
    URL = "URL"
    UNKNOWN = "UNKNOWN"


@dataclass
class Candidate:
    category: Category
    display_form: str
    tts_form: str
    score: float


@dataclass
class Token:
    surface: str
    start: int
    end: int
    category: Category = Category.UNKNOWN
    display_form: str = ""
    tts_form: str = ""
    confidence: float = 0.0
    alternatives: list[Candidate] = field(default_factory=list)
    trace: list[str] = field(default_factory=list)


@dataclass
class NormalizationResult:
    input: str
    display: str
    tts: str
    confidence: float
    tokens: list[Token]


@dataclass
class Config:
    number_words_lang: str = "hindi"   # "hindi" | "english"
    nbest_k: int = 3
