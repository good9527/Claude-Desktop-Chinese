import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(r"C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese")
agent_dir = Path(r"C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese\.agents\worker_m2")

untranslated = json.load(open(agent_dir / "untranslated_raw.json", "r", encoding="utf-8"))

print(f"Total untranslated: {len(untranslated)}")

# Group by word length:
# 1-3 words: short labels, buttons, menu items
# 4-8 words: medium phrases, titles, confirmations
# 9+ words: long sentences, descriptions, policies

short_items = {k: v for k, v in untranslated.items() if len(re.findall(r'[a-zA-Z]+', v)) <= 3 and not '{' in v}
medium_items = {k: v for k, v in untranslated.items() if 4 <= len(re.findall(r'[a-zA-Z]+', v)) <= 8 and not '{' in v}
long_items = {k: v for k, v in untranslated.items() if len(re.findall(r'[a-zA-Z]+', v)) > 8 and not '{' in v}
template_items = {k: v for k, v in untranslated.items() if '{' in v}

print(f"Short items (1-3 words, no braces): {len(short_items)}")
print(f"Medium items (4-8 words, no braces): {len(medium_items)}")
print(f"Long items (>8 words, no braces): {len(long_items)}")
print(f"Template/ICU items (contains braces): {len(template_items)}")

with open(agent_dir / "short_items.json", "w", encoding="utf-8") as f:
    json.dump(short_items, f, ensure_ascii=False, indent=2)

with open(agent_dir / "medium_items.json", "w", encoding="utf-8") as f:
    json.dump(medium_items, f, ensure_ascii=False, indent=2)

with open(agent_dir / "long_items.json", "w", encoding="utf-8") as f:
    json.dump(long_items, f, ensure_ascii=False, indent=2)

with open(agent_dir / "template_items.json", "w", encoding="utf-8") as f:
    json.dump(template_items, f, ensure_ascii=False, indent=2)
