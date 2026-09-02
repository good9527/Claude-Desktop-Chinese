import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
agent_dir = Path(r"C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese\.agents\worker_m2")

short_items = json.load(open(agent_dir / "short_items.json", "r", encoding="utf-8"))
medium_items = json.load(open(agent_dir / "medium_items.json", "r", encoding="utf-8"))
template_items = json.load(open(agent_dir / "template_items.json", "r", encoding="utf-8"))
long_items = json.load(open(agent_dir / "long_items.json", "r", encoding="utf-8"))

print("=== SAMPLE SHORT ITEMS (20) ===")
for k, v in list(short_items.items())[:20]:
    print(f"  {k}: {repr(v)}")

print("\n=== SAMPLE MEDIUM ITEMS (20) ===")
for k, v in list(medium_items.items())[:20]:
    print(f"  {k}: {repr(v)}")

print("\n=== SAMPLE TEMPLATE ITEMS (20) ===")
for k, v in list(template_items.items())[:20]:
    print(f"  {k}: {repr(v)}")

print("\n=== SAMPLE LONG ITEMS (10) ===")
for k, v in list(long_items.items())[:10]:
    print(f"  {k}: {repr(v)}")
