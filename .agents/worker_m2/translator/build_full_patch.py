"""Comprehensive translation generator and dictionary updater for Claude Desktop."""

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(r"C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese")
ZH_DIST = ROOT / "dist" / "zh-CN.json"
ZH_ION = ROOT / "zh-CN-ion.json"

data = json.load(ZH_DIST.open('r', encoding='utf-8-sig'))
print(f"Total keys in dist/zh-CN.json: {len(data)}")
