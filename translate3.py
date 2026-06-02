#!/usr/bin/env python3
"""
Fast batch translation using direct Google Translate API.
Multiple concurrent requests for speed.
"""
import json, os, sys, time, re, urllib.request, urllib.parse, concurrent.futures, threading

SOURCE = r"H:\2026年项目\5.Claude汉化\en-US-957k.json"
OUTPUT = r"H:\2026年项目\5.Claude汉化\zh-CN-ion.json"
CHECKPOINT = r"H:\2026年项目\5.Claude汉化\zh-CN-checkpoint.json"

with open(SOURCE, "r", encoding="utf-8") as f:
    data = json.load(f)

# Load checkpoint if exists
checkpoint = {}
if os.path.exists(CHECKPOINT):
    with open(CHECKPOINT, "r", encoding="utf-8") as f:
        checkpoint = json.load(f)
    print(f"Resuming from checkpoint: {len(checkpoint)} already translated", flush=True)

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

def translate_text(text):
    """Translate a single text using Google Translate API"""
    try:
        protected, phs = protect(text)
        url = "https://translate.googleapis.com/translate_a/single"
        params = urllib.parse.urlencode({
            'client': 'gtx',
            'sl': 'en',
            'tl': 'zh-CN',
            'dt': 't',
            'q': protected
        })
        req = urllib.request.Request(f"{url}?{params}",
            headers={'User-Agent': 'Mozilla/5.0'})

        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            if result and result[0]:
                translated = ''.join(part[0] for part in result[0] if part[0])
                return restore(translated, phs)
    except Exception as e:
        pass
    return None

def translate_batch(texts_with_idx):
    """Translate a batch of (index, text) pairs"""
    results = {}
    for idx, text in texts_with_idx:
        if idx in checkpoint:
            results[idx] = checkpoint[idx]
            continue
        res = translate_text(text)
        if res:
            results[idx] = res
        else:
            results[idx] = text  # Keep original on failure
        time.sleep(0.05)  # Small delay between requests
    return results

# Prepare work
keys = list(data.keys())
values = list(data.values())
translated = dict(checkpoint) if checkpoint else {}

to_translate = []
for i, v in enumerate(values):
    if i in checkpoint:
        continue
    if not skip(v):
        to_translate.append((i, v))
    else:
        translated[i] = v

print(f"To translate: {len(to_translate)} | Already done: {len(checkpoint)}", flush=True)

# Use thread pool for concurrent translation
lock = threading.Lock()
done_count = [len(checkpoint)]
error_count = [0]
save_interval = 500

def process_item(item):
    idx, text = item
    res = translate_text(text)
    with lock:
        if res:
            translated[idx] = res
        else:
            translated[idx] = text
            error_count[0] += 1
        done_count[0] += 1
        if done_count[0] % 100 == 0:
            pct = done_count[0] * 100 // total
            print(f"\rProgress: {done_count[0]}/{total} ({pct}%) | Errors: {error_count[0]}", end="", flush=True)
        if done_count[0] % save_interval == 0:
            # Save checkpoint
            with open(CHECKPOINT, "w", encoding="utf-8") as f:
                json.dump(translated, f, ensure_ascii=False)

# Run with thread pool
WORKERS = 8
print(f"Starting {WORKERS} concurrent workers...", flush=True)

with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
    futures = [executor.submit(process_item, item) for item in to_translate]
    concurrent.futures.wait(futures)

print("", flush=True)

# Save final checkpoint
with open(CHECKPOINT, "w", encoding="utf-8") as f:
    json.dump(translated, f, ensure_ascii=False)

# Build and save output
output = {}
for i, key in enumerate(keys):
    output[key] = translated.get(i, values[i])

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

# Stats
chinese = sum(1 for v in output.values() if isinstance(v, str) and any('一' <= c <= '鿿' for c in v))
print(f"\nDone! Output: {OUTPUT}")
print(f"Total keys: {len(output)}")
print(f"Keys with Chinese: {chinese}/{len(output)} ({chinese*100//len(output)}%)")
