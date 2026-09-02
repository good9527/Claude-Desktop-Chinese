"""Inspect remaining untranslated residue in detail."""

import json
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
with open(ROOT / ".agents" / "worker_m2_r2" / "residue.json", "r", encoding="utf-8") as f:
    residue = json.load(f)

print(f"Total residue items: {len(residue)}")

medium = {k: v for k, v in residue.items() if len(v) >= 20}
short = {k: v for k, v in residue.items() if len(v) < 20}

print(f"\n--- ALL {len(medium)} Medium/Long Residue Items ---")
for k, v in medium.items():
    print(f"[{k}] {repr(v)}")

print(f"\n--- First 50 Short Residue Items ---")
for k, v in list(short.items())[:50]:
    print(f"[{k}] {repr(v)}")
