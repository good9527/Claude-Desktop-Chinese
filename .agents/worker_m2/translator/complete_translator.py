"""Complete translation compiler for Claude Desktop Chinese localization."""

import json
import re
import sys
from pathlib import Path

# Load submodules
from .dictionary_builder import apply_glossary_harmonization, clean_chinese_spacing
from .icu_translations import ICU_TRANSLATIONS
from .text_translator import EXACT_TRANSLATIONS
from .phrase_dict import PHRASE_DICT
from .sentence_patterns import SENTENCE_PATTERNS
from .engine import VOCABULARY

def has_cjk(s: str) -> bool:
    return any('\u4e00' <= c <= '\u9fff' for c in s)

print("Complete translator loaded.")
