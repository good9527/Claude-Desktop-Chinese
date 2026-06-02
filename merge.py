#!/usr/bin/env python3
"""Merge all translated chunks into zh-CN-ion.json"""
import json, os, glob

CHUNK_DIR = r"H:\2026年项目\5.Claude汉化\chunks"
OUTPUT = r"H:\2026年项目\5.Claude汉化\zh-CN-ion.json"

merged = {}
files = sorted(glob.glob(os.path.join(CHUNK_DIR, "*_zh.json")))

for f in files:
    with open(f, "r", encoding="utf-8") as fh:
        data = json.load(fh)
        merged.update(data)
    print(f"  Merged {os.path.basename(f)}: {len(data)} keys")

with open(OUTPUT, "w", encoding="utf-8") as fh:
    json.dump(merged, fh, ensure_ascii=False, indent=2)

# Verify
with open(OUTPUT, "r", encoding="utf-8") as fh:
    verify = json.load(fh)

chinese = sum(1 for v in verify.values() if isinstance(v, str) and any('一' <= c <= '鿿' for c in v))
print(f"\nTotal keys: {len(verify)}")
print(f"Keys with Chinese: {chinese}/{len(verify)} ({chinese*100//len(verify)}%)")
print(f"Output: {OUTPUT}")
print(f"Size: {os.path.getsize(OUTPUT) / 1024:.0f} KB")
