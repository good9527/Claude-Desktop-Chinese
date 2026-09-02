"""Domain-based high-precision translation compiler for Claude Desktop Chinese localization."""

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
agent_dir = Path(r"C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese\.agents\worker_m2")
domains = json.load(open(agent_dir / "domains.json", "r", encoding="utf-8"))

print("Loaded domains:")
for d, items in domains.items():
    print(f"  {d}: {len(items)} items")
