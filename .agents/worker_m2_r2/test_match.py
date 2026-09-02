import json
import re
import sys
from pathlib import Path
from phrase_dict import EXACT_PHRASES
from glossary import harmonize_text

ROOT = Path(__file__).resolve().parents[2]
with open(ROOT / ".agents" / "worker_m2_r2" / "untranslated.json", "r", encoding="utf-8") as f:
    untranslated = json.load(f)

print(f"Total untranslated: {len(untranslated)}")

# Test exact matching
exact_matched = {}
for k, v in untranslated.items():
    s = v.strip()
    if s in EXACT_PHRASES:
        exact_matched[k] = EXACT_PHRASES[s]

print(f"Exact matched: {len(exact_matched)}")
