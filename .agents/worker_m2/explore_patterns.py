import json
import re
import sys
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(r"C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese")
ZH_FILE = ROOT / "dist" / "zh-CN.json"
data = json.load(ZH_FILE.open('r', encoding='utf-8-sig'))

def has_cjk(s: str) -> bool:
    return any('\u4e00' <= c <= '\u9fff' for c in s)

untranslated = {k: v for k, v in data.items() if not has_cjk(v)}

# Let's inspect common prefixes/verbs/phrases in untranslated
prefix_counts = defaultdict(list)
common_starts = [
    "You ", "Your ", "The ", "This ", "These ", "Are you sure ", "Could not ", "Couldn’t ", "Cannot ", "Can’t ",
    "Failed to ", "Unable to ", "Error ", "Please ", "Select ", "Enter ", "Choose ", "Add ", "Remove ", "Delete ",
    "Create ", "Edit ", "View ", "Show ", "Hide ", "Open ", "Close ", "Save ", "Cancel ", "Allow ", "Deny ",
    "Enable ", "Disable ", "Connect ", "Disconnect ", "Sign in ", "Sign out ", "Learn more", "Click ", "Turn on ",
    "Turn off ", "Manage ", "Configure ", "Set up ", "Setting ", "Search ", "Filter ", "Sort by ", "Upload ",
    "Download ", "Export ", "Import ", "Share ", "Publish ", "Unpublish ", "Copy ", "Paste ", "Retry ",
]

for k, v in untranslated.items():
    matched = False
    for p in common_starts:
        if v.startswith(p) or v.startswith(p.lower()):
            prefix_counts[p.strip()].append((k, v))
            matched = True
            break
    if not matched:
        prefix_counts["OTHER"].append((k, v))

print(f"Total untranslated: {len(untranslated)}")
for p, items in sorted(prefix_counts.items(), key=lambda x: len(x[1]), reverse=True)[:30]:
    print(f"  {p:20s}: {len(items):4d} keys")

print(f"  Total with identified start prefixes: {len(untranslated) - len(prefix_counts['OTHER'])}")
print(f"  OTHER: {len(prefix_counts['OTHER'])}")
