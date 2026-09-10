#!/usr/bin/env python3
"""
Create a merged en-US.json that contains Chinese translations.
This replaces the en-US.json content with zh-CN translations,
so selecting "English" in Claude Settings shows Chinese.
"""
import json, os, subprocess

def find_claude_dir():
    """Auto-detect Claude installation directory via PowerShell."""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-AppxPackage | Where-Object { $_.Name -eq 'Claude' } | Select-Object -ExpandProperty InstallLocation"],
            capture_output=True, text=True, encoding="utf-8"
        )
        path = result.stdout.strip()
        if path and os.path.isdir(path):
            return path
    except Exception:
        pass
    return None

claude_dir = find_claude_dir()
if not claude_dir:
    print("[ERROR] Claude installation not found.")
    exit(1)

EN_US = os.path.join(claude_dir, r"app\resources\ion-dist\i18n\en-US.json")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ZH_CN = os.path.join(SCRIPT_DIR, "zh-CN-ion.json")
OUTPUT = os.path.join(SCRIPT_DIR, "en-US-hacked.json")

print(f"Claude dir: {claude_dir}")
print(f"Loading en-US.json...")
with open(EN_US, "r", encoding="utf-8-sig") as f:
    en_data = json.load(f)
print(f"  en-US keys: {len(en_data)}")

print("Loading zh-CN translations...")
with open(ZH_CN, "r", encoding="utf-8") as f:
    zh_data = json.load(f)
print(f"  zh-CN keys: {len(zh_data)}")

# Merge: replace en-US values with zh-CN where available
merged = {}
replaced = 0
for key, en_val in en_data.items():
    if key in zh_data:
        merged[key] = zh_data[key]
        replaced += 1
    else:
        merged[key] = en_val  # Keep original English

print(f"\nReplaced {replaced}/{len(en_data)} keys with Chinese ({replaced*100//len(en_data)}%)")

# Write output
with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

size_kb = os.path.getsize(OUTPUT) / 1024
print(f"Output: {OUTPUT}")
print(f"Size: {size_kb:.0f} KB")
print(f"Total keys: {len(merged)}")
