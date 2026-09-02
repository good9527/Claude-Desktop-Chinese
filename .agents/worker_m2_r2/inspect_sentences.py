import json
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
with open(ROOT / ".agents" / "worker_m2_r2" / "untranslated.json", "r", encoding="utf-8") as f:
    untranslated = json.load(f)

items = list(untranslated.items())
print(f"Total items: {len(items)}")

# Print 50 sentences from index 100 to 150
for k, v in items[100:150]:
    print(f"[{k}] {repr(v)}")
