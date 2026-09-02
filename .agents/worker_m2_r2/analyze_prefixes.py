import json
import re
import sys
from pathlib import Path
from collections import defaultdict

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
untranslated_file = ROOT / ".agents" / "worker_m2_r2" / "untranslated.json"

with open(untranslated_file, "r", encoding="utf-8") as f:
    untranslated = json.load(f)

print(f"Total untranslated: {len(untranslated)}")

# Let's group untranslated strings by common prefix/patterns
# e.g., "Failed to...", "Could not...", "Cannot...", "Are you sure...", "Please...", "Select...", "Add...", "Remove...", "Delete...", "Edit...", "Manage...", "View...", "Learn more..."
prefix_patterns = [
    ("Failed to", r"^Failed to\b"),
    ("Couldn't", r"^Couldn’t\b|^Could not\b"),
    ("Cannot", r"^Cannot\b|^Can’t\b"),
    ("Unable to", r"^Unable to\b"),
    ("Are you sure", r"^Are you sure\b"),
    ("Please", r"^Please\b"),
    ("Select", r"^Select\b|^Choose\b"),
    ("Add", r"^Add\b"),
    ("Remove", r"^Remove\b"),
    ("Delete", r"^Delete\b"),
    ("Edit", r"^Edit\b"),
    ("Manage", r"^Manage\b"),
    ("View", r"^View\b"),
    ("Learn more", r"Learn more\b"),
    ("You’ve", r"^You’ve\b|^You have\b"),
    ("Your", r"^Your\b"),
    ("This", r"^This\b"),
    ("No", r"^No\b"),
    ("Enter", r"^Enter\b"),
    ("Open", r"^Open\b"),
    ("Close", r"^Close\b"),
    ("Enable", r"^Enable\b"),
    ("Disable", r"^Disable\b"),
    ("Turn on", r"^Turn on\b"),
    ("Turn off", r"^Turn off\b"),
    ("Switch", r"^Switch\b"),
    ("Upgrade", r"^Upgrade\b"),
    ("Download", r"^Download\b"),
    ("Upload", r"^Upload\b"),
    ("Save", r"^Save\b"),
    ("Cancel", r"^Cancel\b"),
    ("Confirm", r"^Confirm\b"),
    ("Retry", r"^Retry\b"),
    ("Continue", r"^Continue\b"),
    ("Back", r"^Back\b"),
    ("Next", r"^Next\b"),
    ("Done", r"^Done\b"),
    ("Loading", r"^Loading\b"),
]

matched_keys = set()
pattern_groups = defaultdict(list)

for k, v in untranslated.items():
    s = v.strip()
    matched = False
    for label, pat in prefix_patterns:
        if re.search(pat, s, re.IGNORECASE):
            pattern_groups[label].append((k, v))
            matched_keys.add(k)
            matched = True
            break

print("--- Prefix Pattern Groups ---")
for label, items in sorted(pattern_groups.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"{label:20}: {len(items)}")

unmatched_count = len(untranslated) - len(matched_keys)
print(f"\nUnmatched by common prefix: {unmatched_count}")
