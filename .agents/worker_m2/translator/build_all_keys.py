"""Build all translations and update dist/zh-CN.json and zh-CN-ion.json."""

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(r"C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese")
ZH_DIST = ROOT / "dist" / "zh-CN.json"
ZH_ION = ROOT / "zh-CN-ion.json"

# Load original dictionary
data = json.load(ZH_DIST.open('r', encoding='utf-8-sig'))

def has_cjk(s: str) -> bool:
    return any('\u4e00' <= c <= '\u9fff' for c in s)

print(f"Total keys: {len(data)}")
