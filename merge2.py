#!/usr/bin/env python3
"""Fix and merge all translated chunks with robust JSON repair"""
import json, os, glob, re

CHUNK_DIR = r"H:\2026年项目\5.Claude汉化\chunks"
OUTPUT = r"H:\2026年项目\5.Claude汉化\zh-CN-ion.json"

def fix_json_quotes(content):
    """Fix unescaped double quotes inside JSON string values"""
    lines = content.split('\n')
    fixed = []
    for line in lines:
        m = re.match(r'^(\s*"[^"]+":\s*")(.*)("[\s,]*$)', line)
        if m:
            prefix, value, suffix = m.groups()
            # Count quotes in value - if odd number, there are unescaped quotes
            if value.count('"') % 2 != 0 or ('"' in value and not value.startswith('{')):
                # Replace unescaped inner " with Chinese quotes
                # Find pairs of inner quotes
                new_val = []
                in_quote = False
                for ch in value:
                    if ch == '"':
                        if not in_quote:
                            new_val.append('“')  # left "
                            in_quote = True
                        else:
                            new_val.append('”')  # right "
                            in_quote = False
                    else:
                        new_val.append(ch)
                value = ''.join(new_val)
            fixed.append(prefix + value + suffix)
        else:
            fixed.append(line)
    return '\n'.join(fixed)

def load_chunk(filepath):
    """Load a chunk JSON file, fixing common issues"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Try direct parse first
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # Try fixing unescaped quotes
    fixed = fix_json_quotes(content)
    try:
        return json.loads(fixed)
    except json.JSONDecodeError as e:
        print(f"  [WARN] {os.path.basename(filepath)} still has errors after fix: {e}")
        # Try line-by-line extraction
        return extract_kv_pairs(content)

def extract_kv_pairs(content):
    """Extract key-value pairs using regex as fallback"""
    result = {}
    # Match "key": "value" patterns
    for m in re.finditer(r'"([^"]+)":\s*"((?:[^"\\]|\\.)*)"\s*[,\n}]', content):
        key, val = m.group(1), m.group(2)
        # Unescape JSON escapes
        val = val.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')
        result[key] = val
    return result

# Process all chunks
merged = {}
files = sorted(glob.glob(os.path.join(CHUNK_DIR, "*_zh.json")))

for f in files:
    basename = os.path.basename(f)
    data = load_chunk(f)
    merged.update(data)
    print(f"  {basename}: {len(data)} keys")

# Write output
with open(OUTPUT, "w", encoding="utf-8") as fh:
    json.dump(merged, fh, ensure_ascii=False, indent=2)

# Stats
chinese = sum(1 for v in merged.values() if isinstance(v, str) and any('一' <= c <= '鿿' for c in v))
print(f"\nTotal keys: {len(merged)}")
print(f"Keys with Chinese: {chinese}/{len(merged)} ({chinese*100//len(merged)}%)")
print(f"Output: {OUTPUT}")
print(f"Size: {os.path.getsize(OUTPUT) / 1024:.0f} KB")
