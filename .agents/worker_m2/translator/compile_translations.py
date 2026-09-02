"""Script to compile all translations for Claude Desktop Chinese localization."""

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

agent_dir = Path(r"C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese\.agents\worker_m2")
untranslated = json.load(open(agent_dir / "untranslated_raw.json", "r", encoding="utf-8"))

print(f"Total untranslated keys to process: {len(untranslated)}")
