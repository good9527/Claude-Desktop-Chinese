import json
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
with open(ROOT / ".agents" / "worker_m2_r2" / "untranslated.json", "r", encoding="utf-8") as f:
    untranslated = json.load(f)

# Sort by length descending
sorted_by_len = sorted(untranslated.items(), key=lambda x: len(x[1]), reverse=True)
print(f"Total: {len(sorted_by_len)}")
print(f"Top 20 longest:")
for k, v in sorted_by_len[:20]:
    print(f"[{k}] ({len(v)} chars) {repr(v[:100])}...")

print(f"\nItems between 1000 and 1020:")
for k, v in sorted_by_len[1000:1020]:
    print(f"[{k}] ({len(v)} chars) {repr(v)}")

print(f"\nItems between 3000 and 3020:")
for k, v in sorted_by_len[3000:3020]:
    print(f"[{k}] ({len(v)} chars) {repr(v)}")

print(f"\nItems between 5000 and 5020:")
for k, v in sorted_by_len[5000:5020]:
    print(f"[{k}] ({len(v)} chars) {repr(v)}")
