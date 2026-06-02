#!/usr/bin/env python3
"""
Batch translate Claude Desktop en-US.json to zh-CN.json
Splits the file into chunks and translates using local logic + dictionary
"""
import json
import re
import os
import sys

SOURCE = r"H:\2026年项目\5.Claude汉化\en-US-957k.json"
OUTPUT = r"H:\2026年项目\5.Claude汉化\zh-CN-ion.json"
CHUNK_DIR = r"H:\2026年项目\5.Claude汉化\chunks"

os.makedirs(CHUNK_DIR, exist_ok=True)

with open(SOURCE, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total keys: {len(data)}")

# Split into chunks of 500 keys each
keys = list(data.items())
CHUNK_SIZE = 500
chunks = []
for i in range(0, len(keys), CHUNK_SIZE):
    chunk = dict(keys[i:i+CHUNK_SIZE])
    chunks.append(chunk)

print(f"Split into {len(chunks)} chunks of ~{CHUNK_SIZE} keys")

# Write each chunk as a separate JSON file
for idx, chunk in enumerate(chunks):
    chunk_path = os.path.join(CHUNK_DIR, f"chunk_{idx:03d}.json")
    with open(chunk_path, "w", encoding="utf-8") as f:
        json.dump(chunk, f, ensure_ascii=False, indent=2)

print(f"Chunks written to {CHUNK_DIR}")
print("Ready for translation. Run translate_agent.py next.")
