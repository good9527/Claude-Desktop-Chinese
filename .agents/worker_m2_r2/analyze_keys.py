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

pure_symbols_or_numbers = {}
short_tokens = {}
urls_or_code = {}
icu_patterns = {}
regular_english = {}

for k, v in no_cjk.items():
    if re.fullmatch(r"[\d\s.,:;!?_/\-+*=<>{}()\[\]#%&@\'\"`~|^$\\\\]+", v):
        pure_symbols_or_numbers[k] = v
    elif "{" in v and any(kw in v for kw in ["plural", "select", "number", "date", "time"]):
        icu_patterns[k] = v
    elif re.match(r"^(https?://|api://|[a-z0-9_]+\.[a-z0-9_]+)", v, re.I) and " " not in v:
        urls_or_code[k] = v
    elif len(v.strip()) <= 4 and re.fullmatch(r"[A-Za-z0-9_\-.]+", v.strip()):
        short_tokens[k] = v
    else:
        regular_english[k] = v

print(f"Total keys: {len(d)}")
print(f"Total no CJK: {len(no_cjk)}")
print(f"Pure symbols / numbers: {len(pure_symbols_or_numbers)}")
print(f"Short tokens (<=4 chars): {len(short_tokens)}")
print(f"URLs / single code identifiers: {len(urls_or_code)}")
print(f"ICU patterns: {len(icu_patterns)}")
print(f"Regular English sentences/phrases: {len(regular_english)}")

print("\nSample pure symbols/numbers:")
for k, v in list(pure_symbols_or_numbers.items())[:5]:
    print(f"  {k}: {repr(v)}")

print("\nSample short tokens:")
for k, v in list(short_tokens.items())[:5]:
    print(f"  {k}: {repr(v)}")

print("\nSample URLs / identifiers:")
for k, v in list(urls_or_code.items())[:5]:
    print(f"  {k}: {repr(v)}")

print("\nSample ICU patterns:")
for k, v in list(icu_patterns.items())[:5]:
    print(f"  {k}: {repr(v)}")

print("\nSample regular English:")
for k, v in list(regular_english.items())[:10]:
    print(f"  {k}: {repr(v)}")
