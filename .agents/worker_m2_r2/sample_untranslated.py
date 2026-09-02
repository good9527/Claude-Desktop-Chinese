import json
import sys
from pathlib import Path
from collections import Counter

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
untranslated_file = ROOT / ".agents" / "worker_m2_r2" / "untranslated.json"

with open(untranslated_file, "r", encoding="utf-8") as f:
    untranslated = json.load(f)

# Let's inspect length distribution of untranslated
short_strings = {k: v for k, v in untranslated.items() if len(v) < 20}
medium_strings = {k: v for k, v in untranslated.items() if 20 <= len(v) < 80}
long_strings = {k: v for k, v in untranslated.items() if len(v) >= 80}

print(f"Short (<20 chars): {len(short_strings)}")
print(f"Medium (20-79 chars): {len(medium_strings)}")
print(f"Long (>=80 chars): {len(long_strings)}")

print("\n--- 20 Sample Short Strings ---")
for k, v in list(short_strings.items())[:20]:
    print(f"  {k:12}: {repr(v)}")

print("\n--- 20 Sample Medium Strings ---")
for k, v in list(medium_strings.items())[:20]:
    print(f"  {k:12}: {repr(v)}")

print("\n--- 20 Sample Long Strings ---")
for k, v in list(long_strings.items())[:20]:
    print(f"  {k:12}: {repr(v)}")
