import json
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
with open(ROOT / ".agents" / "worker_m2_r2" / "untrans_icu.json", "r", encoding="utf-8") as f:
    icu_dict = json.load(f)

items = list(icu_dict.items())
print(f"Total: {len(items)}")
for i, (k, v) in enumerate(items):
    print(f"[{i:03d}] {k:12}: {repr(v)}")
