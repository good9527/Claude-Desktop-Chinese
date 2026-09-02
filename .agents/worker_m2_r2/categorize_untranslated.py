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

print(f"Loaded {len(untranslated)} untranslated items.")

# Patterns
# 1. Non-translatable technical strings: URLs, UUIDs, hex, IP addresses, pure symbols, single numbers, system paths
re_uuid = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
re_url = re.compile(r"^(https?://|api://|mailto:|ftp://|file://)[^\s]+$")
re_path = re.compile(r"^(/[a-zA-Z0-9_\-.]+)+$|^([a-zA-Z]:\\[^\s]+)$|^~/[^\s]+$")
re_num_sym = re.compile(r"^[\d\s.,:;!?_/\-+*=<>{}()\[\]#%&@\'\"`~|^$\\\\]+$")
re_icu = re.compile(r"\{[^{}]*,\s*(plural|select|number|date|time)[^{}]*\}")
re_simple_placeholder_only = re.compile(r"^\{[a-zA-Z0-9_]+\}$")

categories = {
    "uuid": {},
    "url": {},
    "path": {},
    "num_sym": {},
    "simple_placeholder": {},
    "icu": {},
    "brand_or_code": {},
    "sentences_or_phrases": {}
}

known_brands_or_code = {
    "Claude", "Sonnet", "Haiku", "Opus", "Anthropic", "Python", "JavaScript", "TypeScript",
    "JSON", "YAML", "Markdown", "HTML", "CSS", "SQL", "Bash", "Shell", "PowerShell",
    "GitHub", "Google", "Google Play", "Gmail", "Apple", "Slack", "AWS", "Azure",
    "Docker", "Linux", "macOS", "Windows", "iOS", "Android", "API", "URL", "UUID", "ID",
    "OAuth", "SAML", "SSO", "JWT", "REST", "SDK", "MCP", "CLI", "UI", "OS", "IP", "CI", "PR"
}

for k, v in untranslated.items():
    s = v.strip()
    if re_uuid.match(s):
        categories["uuid"][k] = v
    elif re_url.match(s):
        categories["url"][k] = v
    elif re_path.match(s):
        categories["path"][k] = v
    elif re_simple_placeholder_only.match(s):
        categories["simple_placeholder"][k] = v
    elif re_num_sym.match(s):
        categories["num_sym"][k] = v
    elif re_icu.search(s):
        categories["icu"][k] = v
    elif s in known_brands_or_code:
        categories["brand_or_code"][k] = v
    else:
        categories["sentences_or_phrases"][k] = v

print("\n--- Category Breakdown ---")
for cat, items in categories.items():
    print(f"{cat:25}: {len(items)}")

print("\n--- Sample ICU strings (first 10) ---")
for k, v in list(categories["icu"].items())[:10]:
    print(f"  [{k}] {v}")

print("\n--- Sample Sentences / Phrases (first 20) ---")
for k, v in list(categories["sentences_or_phrases"].items())[:20]:
    print(f"  [{k}] {v}")
