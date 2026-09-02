"""Batch translator processing all 7,360 untranslated keys."""

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

def protect_placeholders(text: str) -> tuple[str, dict[str, str]]:
    placeholders = {}
    counter = 0

    def mask(pattern: str, val: str) -> str:
        nonlocal counter
        for m in list(re.finditer(pattern, val)):
            key = f"__PH{counter}__"
            placeholders[key] = m.group(0)
            val = val.replace(m.group(0), key, 1)
            counter += 1
        return val

    # Mask ICU constructs or nested braces first
    text = mask(r"\{[^{}]+\}", text)
    text = mask(r"</?[a-zA-Z0-9_\-]+(?:\s+[^>]*)?>", text)
    text = mask(r"https?://\S+", text)
    text = mask(r"`[^`]+`", text)
    return text, placeholders

def unprotect_placeholders(text: str, placeholders: dict[str, str]) -> str:
    for k, v in placeholders.items():
        text = text.replace(k, v)
    return text

def translate_sentence(text: str) -> str:
    """Translate an English sentence or phrase into Simplified Chinese."""
    trimmed = text.strip()
    if not trimmed:
        return text
    
    # 1. Exact match
    if trimmed in EXACT_TRANSLATIONS:
        return EXACT_TRANSLATIONS[trimmed]
    if trimmed in PHRASE_DICT:
        return PHRASE_DICT[trimmed]
    
    # 2. Check Sentence Patterns
    for pattern, repl in SENTENCE_PATTERNS:
        if re.search(pattern, trimmed):
            return re.sub(pattern, repl, trimmed)
            
    return text

def process_entry(key: str, val: str) -> str:
    """Process a single key-value entry."""
    # 1. Check ICU Translations
    if key in ICU_TRANSLATIONS:
        return apply_glossary_harmonization(ICU_TRANSLATIONS[key])
    
    # 2. Check Exact Match Translations
    if val in EXACT_TRANSLATIONS:
        return apply_glossary_harmonization(EXACT_TRANSLATIONS[val])
    
    # 3. Check Phrase Dict
    if val in PHRASE_DICT:
        return apply_glossary_harmonization(PHRASE_DICT[val])
        
    # 4. Check Sentence Patterns
    for pattern, repl in SENTENCE_PATTERNS:
        if re.search(pattern, val):
            return apply_glossary_harmonization(re.sub(pattern, repl, val))
            
    # 5. Protected translation
    protected, placeholders = protect_placeholders(val)
    translated_protected = translate_sentence(protected)
    restored = unprotect_placeholders(translated_protected, placeholders)
    
    return apply_glossary_harmonization(restored)
