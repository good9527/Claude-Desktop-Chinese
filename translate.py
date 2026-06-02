#!/usr/bin/env python3
"""
Translate Claude Desktop UI strings from English to Chinese using Google Translate.
Handles 15000+ keys with batching and rate limiting.
"""
import json
import os
import sys
import time
import re

# Try to use googletrans
try:
    from googletrans import Translator
    translator = Translator()
    USE_GOOGLE = True
    print("Using Google Translate API")
except ImportError:
    USE_GOOGLE = False
    print("googletrans not available, using fallback")

SOURCE = r"H:\2026年项目\5.Claude汉化\en-US-957k.json"
OUTPUT = r"H:\2026年项目\5.Claude汉化\zh-CN-ion.json"

with open(SOURCE, "r", encoding="utf-8") as f:
    data = json.load(f)

total = len(data)
print(f"Total keys to translate: {total}")

# Protect variables and tags from translation
def protect(text):
    """Replace variables/tags with placeholders before translation"""
    if not isinstance(text, str):
        return text, []
    placeholders = {}
    counter = [0]

    def replace_match(pattern, text):
        nonlocal counter
        matches = list(re.finditer(pattern, text))
        for m in matches:
            key = f"__PH{counter[0]}__"
            placeholders[key] = m.group(0)
            text = text.replace(m.group(0), key, 1)
            counter[0] += 1
        return text

    # Protect {variables}
    text = replace_match(r'\{[^}]+\}', text)
    # Protect <tags>
    text = replace_match(r'</?[a-zA-Z][^>]*>', text)
    # Protect URLs
    text = replace_match(r'https?://\S+', text)
    # Protect code blocks
    text = replace_match(r'`[^`]+`', text)

    return text, placeholders

def restore(text, placeholders):
    """Restore placeholders after translation"""
    for key, val in placeholders.items():
        text = text.replace(key, val)
    return text

# Skip strings that don't need translation
def skip_translate(value):
    """Check if value should be skipped (no real text to translate)"""
    if not isinstance(value, str):
        return True
    # Pure numbers, symbols, or very short
    if len(value.strip()) <= 2:
        return True
    # Pure variables
    if re.match(r'^[\s{}\[\]<>/\-\d.:]+$', value):
        return True
    return False

# Batch translate using googletrans
def translate_batch(texts, batch_size=20):
    """Translate a list of texts in batches"""
    results = list(texts)  # copy
    to_translate = []

    for i, text in enumerate(texts):
        if skip_translate(text):
            continue
        protected, placeholders = protect(text)
        to_translate.append((i, protected, placeholders))

    print(f"  {len(to_translate)} strings need translation (skipped {len(texts) - len(to_translate)})")

    # Process in batches
    for batch_start in range(0, len(to_translate), batch_size):
        batch = to_translate[batch_start:batch_start + batch_size]
        batch_texts = [b[1] for b in batch]

        try:
            translated = translator.translate(batch_texts, src='en', dest='zh-cn')
            for (idx, _, placeholders), t in zip(batch, translated):
                if t and t.text:
                    results[idx] = restore(t.text, placeholders)
                else:
                    results[idx] = restore(batch_texts[batch.index((idx, _, placeholders))], placeholders)
        except Exception as e:
            print(f"  [WARN] Batch failed at {batch_start}: {e}")
            # Fallback: translate one by one
            for idx, protected, placeholders in batch:
                try:
                    t = translator.translate(protected, src='en', dest='zh-cn')
                    if t and t.text:
                        results[idx] = restore(t.text, placeholders)
                    time.sleep(0.1)
                except:
                    pass  # Keep original

        progress = min(batch_start + batch_size, len(to_translate))
        print(f"  Progress: {progress}/{len(to_translate)} ({progress*100//len(to_translate)}%)")

        if batch_start + batch_size < len(to_translate):
            time.sleep(0.5)  # Rate limiting

    return results

# Process all keys
print("\nStarting translation...")
keys = list(data.keys())
values = list(data.values())

translated_values = translate_batch(values, batch_size=10)

# Build output
output = {}
for k, v in zip(keys, translated_values):
    output[k] = v

# Write output
with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\nDone! Written to {OUTPUT}")
print(f"Total keys: {len(output)}")

# Verify
with open(OUTPUT, "r", encoding="utf-8") as f:
    verify = json.load(f)
print(f"Verification: {len(verify)} keys in output file")
