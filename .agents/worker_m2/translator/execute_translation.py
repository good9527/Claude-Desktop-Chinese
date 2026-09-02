"""Execute full translation and harmonization on dist/zh-CN.json and zh-CN-ion.json."""

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(r"C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese")
agent_dir = Path(r"C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese\.agents\worker_m2")
ZH_DIST = ROOT / "dist" / "zh-CN.json"
ZH_ION = ROOT / "zh-CN-ion.json"

data = json.load(ZH_DIST.open('r', encoding='utf-8-sig'))

def has_cjk(s: str) -> bool:
    return any('\u4e00' <= c <= '\u9fff' for c in s)

print(f"Loaded {len(data)} keys.")
