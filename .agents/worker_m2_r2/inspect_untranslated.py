import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
dist_file = ROOT / "dist" / "zh-CN.json"

with open(dist_file, "r", encoding="utf-8") as f:
    d = json.load(f)

def has_cjk(s):
    return any("\u4e00" <= c <= "\u9fff" for c in s)

no_cjk = {k: v for k, v in d.items() if not has_cjk(v)}
cjk = {k: v for k, v in d.items() if has_cjk(v)}

print(f"Total keys: {len(d)}")
print(f"Has CJK: {len(cjk)}")
print(f"No CJK: {len(no_cjk)}")

# Let's see lengths of no_cjk values
lengths = [len(v) for v in no_cjk.values()]
print(f"No CJK min len: {min(lengths)}, max len: {max(lengths)}, avg len: {sum(lengths)/len(lengths):.1f}")

# Look at distribution of no_cjk strings
single_words = {k: v for k, v in no_cjk.items() if " " not in v.strip()}
sentences = {k: v for k, v in no_cjk.items() if " " in v.strip()}
print(f"Single word/tokens without spaces: {len(single_words)}")
print(f"Multi-word phrases/sentences: {len(sentences)}")

# Let's inspect some single word tokens
print("\nSample single words/tokens:")
for k, v in list(single_words.items())[:30]:
    print(f"  {k}: {repr(v)}")

# Let's inspect some multi-word phrases/sentences
print("\nSample multi-word phrases/sentences:")
for k, v in list(sentences.items())[:30]:
    print(f"  {k}: {repr(v)}")
