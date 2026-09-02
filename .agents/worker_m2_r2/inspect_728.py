import json
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
DIST_ZH = ROOT / "dist" / "zh-CN.json"

with open(DIST_ZH, "r", encoding="utf-8") as f:
    data = json.load(f)

def has_cjk(s: str) -> bool:
    return any("\u4e00" <= c <= "\u9fff" for c in s)

no_cjk = {k: v for k, v in data.items() if not has_cjk(v)}
print(f"Total remaining without CJK: {len(no_cjk)}")

with open(ROOT / ".agents" / "worker_m2_r2" / "remaining_728.json", "w", encoding="utf-8") as out:
    json.dump(no_cjk, out, ensure_ascii=False, indent=2)

for i, (k, v) in enumerate(list(no_cjk.items())):
    if i < 60 or i % 10 == 0:
        print(f"[{i:03d}] {k:12}: {repr(v)}")
