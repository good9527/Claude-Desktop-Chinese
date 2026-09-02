import json
import re
import sys
from pathlib import Path
from collections import Counter

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
untranslated_file = ROOT / ".agents" / "worker_m2_r2" / "untranslated.json"

with open(untranslated_file, "r", encoding="utf-8") as f:
    untranslated = json.load(f)

# Collect all words
words = Counter()
for v in untranslated.values():
    clean = re.sub(r"\{[^}]+\}", " ", v)
    clean = re.sub(r"<[^>]+>", " ", clean)
    clean = re.sub(r"[^\w\s]", " ", clean)
    for w in clean.split():
        if len(w) > 1:
            words[w.lower()] += 1

print(f"Total unique words: {len(words)}")
print("\n--- Top 50 Most Frequent Words ---")
for w, count in words.most_common(50):
    print(f"{w:15}: {count}")
