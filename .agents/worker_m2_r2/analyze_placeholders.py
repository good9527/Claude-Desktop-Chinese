import json
import re
import sys
from pathlib import Path
from collections import defaultdict

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
untranslated_file = ROOT / ".agents" / "worker_m2_r2" / "untranslated.json"

with open(untranslated_file, "r", encoding="utf-8") as f:
    untranslated = json.load(f)

print(f"Total untranslated: {len(untranslated)}")

# Let's see how many strings have placeholders
with_placeholders = {k: v for k, v in untranslated.items() if "{" in v and "}" in v}
with_tags = {k: v for k, v in untranslated.items() if "<" in v and ">" in v}
pure_text = {k: v for k, v in untranslated.items() if k not in with_placeholders and k not in with_tags}

print(f"Strings with placeholders: {len(with_placeholders)}")
print(f"Strings with HTML/XML tags: {len(with_tags)}")
print(f"Pure text strings: {len(pure_text)}")

# Let's inspect some samples with placeholders
print("\n--- Sample placeholder strings ---")
for k, v in list(with_placeholders.items())[:15]:
    print(f"  [{k}] {v}")

# Let's inspect some samples with tags
print("\n--- Sample tag strings ---")
for k, v in list(with_tags.items())[:15]:
    print(f"  [{k}] {v}")
