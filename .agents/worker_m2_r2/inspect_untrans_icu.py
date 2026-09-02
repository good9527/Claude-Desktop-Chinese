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

untrans_icu = {}
for k, v in untranslated.items():
    if any(kw in v for kw in ["plural", "select"]):
        untrans_icu[k] = v

print(f"Total untranslated ICU strings: {len(untrans_icu)}")
print("\n--- All Untranslated ICU Strings ---")
for k, v in list(untrans_icu.items())[:30]:
    print(f"  [{k}] {repr(v)}")
