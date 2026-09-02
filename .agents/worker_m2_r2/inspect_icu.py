import json
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
dist_file = ROOT / "dist" / "zh-CN.json"

with open(dist_file, "r", encoding="utf-8") as f:
    d = json.load(f)

# Inspect existing ICU translations
icu_samples = []
for k, v in d.items():
    if any(kw in v for kw in ["plural", "select"]) and any("\u4e00" <= c <= "\u9fff" for c in v):
        icu_samples.append((k, v))

print(f"Total existing translated ICU strings: {len(icu_samples)}")
print("\n--- 15 Sample Existing Translated ICU strings ---")
for k, v in icu_samples[:15]:
    print(f"  [{k}] {v}")
