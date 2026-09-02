import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
agent_dir = Path(r"C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese\.agents\worker_m2")
icu_raw = json.load(open(agent_dir / "icu_raw.json", "r", encoding="utf-8"))

print(f"Total ICU entries: {len(icu_raw)}")
for k, v in list(icu_raw.items())[:30]:
    print(f"[{k}] {v}")
