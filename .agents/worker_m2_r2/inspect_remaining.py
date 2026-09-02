"""Inspect remaining 827 keys without Chinese."""

import json
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
DIST_ZH = ROOT / "dist" / "zh-CN.json"

with open(DIST_ZH, "r", encoding="utf-8") as f:
    data = json.load(f)

def has_cjk(s: str) -> bool:
    return any("\u4e00" <= c <= "\u9fff" for c in s)

no_cjk = {k: v for k, v in data.items() if not has_cjk(v)}
print(f"Total keys without CJK: {len(no_cjk)}")

# Categorize them
pure_symbols_num = {}
urls_paths = {}
single_words = {}
multi_words = {}

for k, v in no_cjk.items():
    s = v.strip()
    if re.fullmatch(r"[\d\s.,:;!?_/\-+*=<>{}()\[\]#%&@\'\"`~|^$\\\\]+", s):
        pure_symbols_num[k] = v
    elif re.match(r"^(https?://|api://|[a-zA-Z0-9_\-.]+\.[a-zA-Z0-9_\-.]+|/[a-zA-Z0-9_\-./]+|~/[a-zA-Z0-9_\-./]+)", s) and " " not in s:
        urls_paths[k] = v
    elif " " not in s:
        single_words[k] = v
    else:
        multi_words[k] = v

print(f"Pure symbols/numbers/placeholders: {len(pure_symbols_num)}")
print(f"URLs/paths/identifiers: {len(urls_paths)}")
print(f"Single words: {len(single_words)}")
print(f"Multi-word phrases/sentences: {len(multi_words)}")

print("\n--- ALL Multi-word phrases/sentences (first 50) ---")
for k, v in list(multi_words.items())[:50]:
    print(f"[{k}] {repr(v)}")

print("\n--- ALL Single words (first 50) ---")
for k, v in list(single_words.items())[:50]:
    print(f"[{k}] {repr(v)}")
