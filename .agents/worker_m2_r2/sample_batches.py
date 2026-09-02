import json
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
untranslated_file = ROOT / ".agents" / "worker_m2_r2" / "untranslated.json"

with open(untranslated_file, "r", encoding="utf-8") as f:
    untranslated = json.load(f)

# Let's inspect untranslated keys in chunks of 500 or grouped by theme
# Let's see some samples across different index ranges
items = list(untranslated.items())
print(f"Total untranslated items: {len(items)}")

for idx in [0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 6500, 7000]:
    print(f"\n--- Batch starting at index {idx} ---")
    for k, v in items[idx:idx+10]:
        print(f"  [{k}] {repr(v)}")
