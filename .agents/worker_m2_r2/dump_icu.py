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

untrans_icu = {k: v for k, v in untranslated.items() if any(kw in v for kw in ["plural", "select"])}

print(f"Total untranslated ICU strings: {len(untrans_icu)}")

# Let's categorize ICU strings:
# 1. Pure plural: "{count, plural, one {# item} other {# items}}"
# 2. Plural in sentence: "Failed to load {count, plural, one {# item} other {# items}}."
# 3. Select in sentence: "{period, select, daily {Daily spend limit} weekly {Weekly spend limit} other {Monthly spend limit}}"

with open(ROOT / ".agents" / "worker_m2_r2" / "untrans_icu.json", "w", encoding="utf-8") as out:
    json.dump(untrans_icu, out, ensure_ascii=False, indent=2)

print("Saved untrans_icu.json")
