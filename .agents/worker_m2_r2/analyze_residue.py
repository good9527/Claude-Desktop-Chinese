"""Analyze untranslated residue from translation pipeline."""

import json
import re
import sys
from pathlib import Path
from collections import Counter

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from run_translation_pipeline import results, untranslated, has_cjk

residue = {k: untranslated[k] for k, v in results.items() if not has_cjk(v)}
print(f"Total residue (no CJK): {len(residue)}")

# Let's inspect length distribution of residue
short = {k: v for k, v in residue.items() if len(v) < 20}
medium = {k: v for k, v in residue.items() if 20 <= len(v) < 80}
long = {k: v for k, v in residue.items() if len(v) >= 80}

print(f"Short (<20): {len(short)}")
print(f"Medium (20-79): {len(medium)}")
print(f"Long (>=80): {len(long)}")

print("\n--- 30 Sample Residue Items ---")
for k, v in list(residue.items())[:30]:
    print(f"[{k}] ({len(v)}) {repr(v)}")

# Save residue to file
ROOT = Path(__file__).resolve().parents[2]
with open(ROOT / ".agents" / "worker_m2_r2" / "residue.json", "w", encoding="utf-8") as out:
    json.dump(residue, out, ensure_ascii=False, indent=2)

print("Saved residue.json")
