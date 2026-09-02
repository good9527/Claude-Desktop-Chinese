import json
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
with open(ROOT / ".agents" / "worker_m2_r2" / "untranslated.json", "r", encoding="utf-8") as f:
    untranslated = json.load(f)

short_strings = {k: v for k, v in untranslated.items() if len(v) < 20}
print(f"Total short strings: {len(short_strings)}")

# Dump to file for inspection
with open(ROOT / ".agents" / "worker_m2_r2" / "short_strings.json", "w", encoding="utf-8") as out:
    json.dump(short_strings, out, ensure_ascii=False, indent=2)

print("Saved short_strings.json")
