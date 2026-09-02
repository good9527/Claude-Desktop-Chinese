import json
import re
import sys
from pathlib import Path
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(r"C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese")
ZH_FILE = ROOT / "dist" / "zh-CN.json"

data = json.load(ZH_FILE.open('r', encoding='utf-8-sig'))

def has_cjk(s: str) -> bool:
    return any('\u4e00' <= c <= '\u9fff' for c in s)

untranslated = {k: v for k, v in data.items() if not has_cjk(v)}

print(f"Total untranslated keys: {len(untranslated)}")

# Let's inspect different patterns in untranslated
icu_entries = {}
pure_symbol_entries = {}
url_entries = {}
acronym_entries = {}
translatable_entries = {}

for k, v in untranslated.items():
    s = v.strip()
    if not re.search(r'[a-zA-Z]', s):
        pure_symbol_entries[k] = v
    elif re.match(r'^(?:https?://|mailto:|api://|wss://|urn:)\S+$', s):
        url_entries[k] = v
    elif re.search(r'\{[^{}]+,\s*(?:plural|select|selectordinal)', v):
        icu_entries[k] = v
    else:
        translatable_entries[k] = v

print(f"ICU entries: {len(icu_entries)}")
print(f"Pure symbol entries: {len(pure_symbol_entries)}")
print(f"URL entries: {len(url_entries)}")
print(f"Other translatable entries: {len(translatable_entries)}")

# Write all untranslated entries to a JSON file in our agent directory for deep processing
agent_dir = Path(r"C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese\.agents\worker_m2")
with open(agent_dir / "untranslated_raw.json", "w", encoding="utf-8") as f:
    json.dump(untranslated, f, ensure_ascii=False, indent=2)

with open(agent_dir / "icu_raw.json", "w", encoding="utf-8") as f:
    json.dump(icu_entries, f, ensure_ascii=False, indent=2)

with open(agent_dir / "translatable_raw.json", "w", encoding="utf-8") as f:
    json.dump(translatable_entries, f, ensure_ascii=False, indent=2)

print("Saved raw untranslated files to .agents/worker_m2/")
