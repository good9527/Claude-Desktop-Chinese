import json
import re
import sys
from pathlib import Path
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
agent_dir = Path(r"C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese\.agents\worker_m2")
untranslated = json.load(open(agent_dir / "untranslated_raw.json", "r", encoding="utf-8"))

print(f"Total untranslated keys: {len(untranslated)}")

# Let's inspect the most frequent sentences / templates in untranslated
templates = Counter()
for k, v in untranslated.items():
    # replace {...} with {PARAM} and numbers with #
    t = re.sub(r'\{[^{}]+\}', '{PARAM}', v)
    t = re.sub(r'\b\d+\b', '#', t)
    templates[t] += 1

print(f"Total unique template structures: {len(templates)}")
print("\nTop 50 template structures:")
for t, c in templates.most_common(50):
    print(f"  [{c:3d}] {repr(t)}")
