"""Generate comprehensive Chinese translation dataset for Claude Desktop."""

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

untranslated = {k: v for k, v in data.items() if not has_cjk(v)}
print(f"Total keys: {len(data)}, Untranslated: {len(untranslated)}")
