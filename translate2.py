#!/usr/bin/env python3
"""
Translate Claude Desktop en-US.json to zh-CN using deep_translator.
Fast batch translation with progress tracking.
"""
import json, os, sys, time, re
from deep_translator import GoogleTranslator

SOURCE = r"H:\2026年项目\5.Claude汉化\en-US-957k.json"
OUTPUT = r"H:\2026年项目\5.Claude汉化\zh-CN-ion.json"

translator = GoogleTranslator(source='en', target='zh-CN')

with open(SOURCE, "r", encoding="utf-8") as f:
    data = json.load(f)

total = len(data)
print(f"Total keys: {total}", flush=True)

def skip(val):
    if not isinstance(val, str) or len(val.strip()) <= 2:
        return True
    if re.match(r'^[\s{}\[\]<>/\-\d.:]+$', val):
        return True
    return False

def protect(text):
    phs = {}
    c = [0]
    def rep(pat, t):
        for m in list(re.finditer(pat, t)):
            k = f"PH{c[0]}X"
            phs[k] = m.group(0)
            t = t.replace(m.group(0), k, 1)
            c[0] += 1
        return t
    text = rep(r'\{[^}]+\}', text)
    text = rep(r'</?[a-zA-Z][^>]*>', text)
    text = rep(r'https?://\S+', text)
    return text, phs

def restore(text, phs):
    for k, v in phs.items():
        text = text.replace(k, v)
    return text

keys = list(data.keys())
values = list(data.values())
translated = list(values)

# Collect indices that need translation
to_translate = []
for i, v in enumerate(values):
    if not skip(v):
        protected, phs = protect(v)
        to_translate.append((i, protected, phs))

print(f"Strings to translate: {len(to_translate)}", flush=True)
print(f"Skipped (no translation needed): {total - len(to_translate)}", flush=True)

# Translate in batches
BATCH = 20
errors = 0
for start in range(0, len(to_translate), BATCH):
    batch = to_translate[start:start+BATCH]
    texts = [b[1] for b in batch]

    try:
        results = translator.translate_batch(texts)
        for (idx, _, phs), res in zip(batch, results):
            if res:
                translated[idx] = restore(res, phs)
    except Exception as e:
        errors += 1
        # Fallback: one by one
        for idx, text, phs in batch:
            try:
                res = translator.translate(text)
                if res:
                    translated[idx] = restore(res, phs)
                time.sleep(0.15)
            except:
                pass

    done = min(start + BATCH, len(to_translate))
    pct = done * 100 // len(to_translate)
    print(f"\rProgress: {done}/{len(to_translate)} ({pct}%) | Errors: {errors}", end="", flush=True)

    if start + BATCH < len(to_translate):
        time.sleep(0.3)

print("", flush=True)

# Build and save
output = dict(zip(keys, translated))
with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

# Verify
with open(OUTPUT, "r", encoding="utf-8") as f:
    v = json.load(f)
chinese_count = sum(1 for val in v.values() if isinstance(val, str) and any('一' <= c <= '鿿' for c in val))
print(f"\nDone! Output: {OUTPUT}")
print(f"Total keys: {len(v)}")
print(f"Keys with Chinese: {chinese_count}/{len(v)} ({chinese_count*100//len(v)}%)")
