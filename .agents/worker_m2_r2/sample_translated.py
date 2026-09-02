import json
import re
import sys
from pathlib import Path
from collections import Counter

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
dist_file = ROOT / "dist" / "zh-CN.json"

with open(dist_file, "r", encoding="utf-8") as f:
    d = json.load(f)

def has_cjk(s):
    return any("\u4e00" <= c <= "\u9fff" for c in s)

translated = {k: v for k, v in d.items() if has_cjk(v)}
untranslated = {k: v for k, v in d.items() if not has_cjk(v)}

print(f"Translated: {len(translated)}, Untranslated: {len(untranslated)}")

# Let's inspect some of the existing translated strings to see translation style and tone
print("\n--- 20 Sample Translated Strings ---")
for k, v in list(translated.items())[:20]:
    print(f"  [{k}] {v}")
