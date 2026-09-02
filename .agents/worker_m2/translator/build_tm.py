"""Build translation memory from existing 14,959 translated keys."""

import json
import re
import sys
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(r"C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese")
ZH_DIST = ROOT / "dist" / "zh-CN.json"

data = json.load(ZH_DIST.open('r', encoding='utf-8-sig'))

def has_cjk(s: str) -> bool:
    return any('\u4e00' <= c <= '\u9fff' for c in s)

# Many translated keys have mixed English-Chinese or known parallel structures
cjk_entries = {k: v for k, v in data.items() if has_cjk(v)}
print(f"Total existing CJK entries: {len(cjk_entries)}")

# Look for patterns in existing CJK entries
print("Sample existing CJK entries:")
for k, v in list(cjk_entries.items())[:20]:
    print(f"  {k}: {repr(v)}")
