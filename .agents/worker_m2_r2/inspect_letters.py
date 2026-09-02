import json
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
with open(ROOT / ".agents" / "worker_m2_r2" / "remaining_827.json", "r", encoding="utf-8") as f:
    items = json.load(f)

print(f"Total: {len(items)}")

# Let's see all strings that contain English letters
with_letters = {k: v for k, v in items.items() if re.search(r"[a-zA-Z]", v)}
print(f"With English letters: {len(with_letters)}")

for i, (k, v) in enumerate(list(with_letters.items())):
    if i < 100 or i % 10 == 0:
        print(f"[{i:03d}] {k:12}: {repr(v)}")
