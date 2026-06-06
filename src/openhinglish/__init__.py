from __future__ import annotations
from openhinglish.types import Config, NormalizationResult, Token, Candidate, Category
from openhinglish.disambiguator import FrequencyDisambiguator, ContextDisambiguator
from openhinglish.pipeline.s0_preprocess import tokenize
from openhinglish.pipeline.s1_classify import classify
from openhinglish.pipeline.s2_spellnorm import spell_normalize
from openhinglish.pipeline.s3_translit import transliterate
from openhinglish.pipeline.s4_names_brands import resolve_entities
from openhinglish.pipeline.s5_numerals import expand_numerals
from openhinglish.pipeline.s6_assemble import assemble

__all__ = [
    "normalize", "Config", "NormalizationResult", "Token", "Candidate", "Category",
    "FrequencyDisambiguator", "ContextDisambiguator",
]

_DISAMBIGUATOR = ContextDisambiguator()


def normalize(text: str, config: Config | None = None) -> NormalizationResult:
    config = config or Config()
    tokens = tokenize(text, config)
    tokens = classify(tokens, config)
    tokens = spell_normalize(tokens, config)
    tokens = _DISAMBIGUATOR.resolve(tokens, config)
    tokens = transliterate(tokens, config)
    tokens = resolve_entities(tokens, config)
    tokens = expand_numerals(tokens, config)
    return assemble(tokens, config, text)
