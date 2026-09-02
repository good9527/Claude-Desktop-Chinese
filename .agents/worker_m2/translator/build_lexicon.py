"""Lexicon and pattern generator for Claude Desktop localization."""

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(r"C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese")
agent_dir = Path(r"C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese\.agents\worker_m2")
raw_path = agent_dir / "untranslated_raw.json"

with open(raw_path, 'r', encoding='utf-8') as f:
    untranslated = json.load(f)

print(f"Loaded {len(untranslated)} untranslated items.")
