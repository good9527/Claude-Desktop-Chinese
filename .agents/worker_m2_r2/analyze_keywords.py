import json
import re
import sys
from pathlib import Path
from collections import Counter

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
untranslated_file = ROOT / ".agents" / "worker_m2_r2" / "untranslated.json"

with open(untranslated_file, "r", encoding="utf-8") as f:
    untranslated = json.load(f)

print(f"Total untranslated keys: {len(untranslated)}")

# Let's see how many items contain specific keywords
keywords = [
    "artifact", "artifacts", "mcp", "model context protocol", "computer use",
    "token", "tokens", "context window", "thinking", "connector", "connectors",
    "routine", "routines", "cowork", "code", "terminal", "slack", "permission",
    "permissions", "billing", "spend", "limit", "workspace", "organization",
    "admin", "member", "members", "invite", "credit", "credits", "account",
    "setting", "settings", "profile", "delete", "remove", "cancel", "save",
    "confirm", "warning", "error", "failed", "success", "loading", "please",
    "enter", "select", "choose", "file", "folder", "project", "chat", "message"
]

kw_counts = {}
for kw in keywords:
    count = sum(1 for v in untranslated.values() if re.search(r"\b" + kw + r"\b", v, re.IGNORECASE))
    if count > 0:
        kw_counts[kw] = count

sorted_kw = sorted(kw_counts.items(), key=lambda x: x[1], reverse=True)
print("\n--- Keyword Frequency in Untranslated ---")
for kw, count in sorted_kw:
    print(f"{kw:25}: {count}")
