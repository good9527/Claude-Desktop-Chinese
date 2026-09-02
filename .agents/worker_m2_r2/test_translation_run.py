"""Test translation coverage across all 7,360 untranslated keys."""

import json
import re
import sys
from pathlib import Path
from typing import Dict, Tuple, List, Optional, Any

from glossary import harmonize_text
from masking import mask_text, unmask_text
from direct_translations import DIRECT_TRANSLATIONS, TECHNICAL_PRESERVE
from phrase_dict import EXACT_PHRASES
from icu_translations import ICU_EXACT_MAP
from vocab_tables import VERBS, NOUNS

ROOT = Path(__file__).resolve().parents[2]
UNTRANSLATED_FILE = ROOT / ".agents" / "worker_m2_r2" / "untranslated.json"

with open(UNTRANSLATED_FILE, "r", encoding="utf-8") as f:
    untranslated = json.load(f)

print(f"Total untranslated: {len(untranslated)}")

def has_cjk(s: str) -> bool:
    return any("\u4e00" <= c <= "\u9fff" for c in s)

translated_results: Dict[str, str] = {}

# Combine dictionaries
COMBINED_MAP = {}
COMBINED_MAP.update(EXACT_PHRASES)
COMBINED_MAP.update(DIRECT_TRANSLATIONS)
COMBINED_MAP.update(ICU_EXACT_MAP)

for k, v in untranslated.items():
    if k in TECHNICAL_PRESERVE:
        translated_results[k] = v
        continue
    
    if k in COMBINED_MAP:
        translated_results[k] = COMBINED_MAP[k]
        continue
        
    s = v.strip()
    if s in COMBINED_MAP:
        translated_results[k] = COMBINED_MAP[s]
        continue

has_cjk_count = sum(1 for v in translated_results.values() if has_cjk(v))
print(f"Pass 1 direct matches translated: {len(translated_results)} ({has_cjk_count} with CJK)")
print(f"Remaining to translate: {len(untranslated) - len(translated_results)}")
