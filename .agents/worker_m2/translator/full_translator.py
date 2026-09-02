"""Full comprehensive translation engine for Claude Desktop Chinese localization."""

import json
import re
import sys
from pathlib import Path

# Load modules
from .dictionary_builder import apply_glossary_harmonization, clean_chinese_spacing
from .icu_translations import ICU_TRANSLATIONS
from .text_translator import EXACT_TRANSLATIONS

def translate_phrase(text: str) -> str:
    """Translate short phrases or single words."""
    trimmed = text.strip()
    if trimmed in EXACT_TRANSLATIONS:
        return EXACT_TRANSLATIONS[trimmed]
    return text

def translate_key_value(key: str, val: str) -> str:
    """Translate a single key-value entry with all safety protections."""
    # 1. Check ICU translations first
    if key in ICU_TRANSLATIONS:
        return apply_glossary_harmonization(ICU_TRANSLATIONS[key])
    
    # 2. Check exact match translations
    if val in EXACT_TRANSLATIONS:
        return apply_glossary_harmonization(EXACT_TRANSLATIONS[val])
        
    return val
