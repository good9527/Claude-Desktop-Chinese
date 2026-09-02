import json
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
dist_file = ROOT / "dist" / "zh-CN.json"

with open(dist_file, "r", encoding="utf-8") as f:
    d = json.load(f)

def has_cjk(s):
    return any("\u4e00" <= c <= "\u9fff" for c in s)

# Check terminology in already translated strings
term_stats = {
    "Artifacts (raw EN)": 0,
    "制品": 0,
    "工件": 0,
    "构件": 0,
    "产物": 0,
    "MCP (raw)": 0,
    "模型上下文协议": 0,
    "MCP 服务器": 0,
    "MCP 工具": 0,
    "Computer Use (raw)": 0,
    "计算机使用": 0,
    "Context Window (raw)": 0,
    "上下文窗口": 0,
    "Extended Thinking (raw)": 0,
    "Thinking Mode (raw)": 0,
    "扩展思考": 0,
    "深度思考": 0,
    "Connectors (raw)": 0,
    "连接器": 0,
}

for k, v in d.items():
    if "Artifacts" in v or "Artifact" in v:
        term_stats["Artifacts (raw EN)"] += 1
    if "制品" in v:
        term_stats["制品"] += 1
    if "工件" in v:
        term_stats["工件"] += 1
    if "构件" in v:
        term_stats["构件"] += 1
    if "产物" in v:
        term_stats["产物"] += 1
    if "MCP" in v:
        term_stats["MCP (raw)"] += 1
    if "模型上下文协议" in v:
        term_stats["模型上下文协议"] += 1
    if "MCP 服务器" in v:
        term_stats["MCP 服务器"] += 1
    if "MCP 工具" in v:
        term_stats["MCP 工具"] += 1
    if "Computer Use" in v or "computer use" in v:
        term_stats["Computer Use (raw)"] += 1
    if "计算机使用" in v:
        term_stats["计算机使用"] += 1
    if "Context Window" in v or "context window" in v:
        term_stats["Context Window (raw)"] += 1
    if "上下文窗口" in v:
        term_stats["上下文窗口"] += 1
    if "Extended Thinking" in v or "extended thinking" in v:
        term_stats["Extended Thinking (raw)"] += 1
    if "Thinking Mode" in v or "thinking mode" in v:
        term_stats["Thinking Mode (raw)"] += 1
    if "扩展思考" in v:
        term_stats["扩展思考"] += 1
    if "深度思考" in v:
        term_stats["深度思考"] += 1
    if "Connectors" in v or "Connector" in v:
        term_stats["Connectors (raw)"] += 1
    if "连接器" in v:
        term_stats["连接器"] += 1

print("--- Terminology Statistics ---")
for term, count in term_stats.items():
    print(f"{term:30}: {count}")

no_cjk = {k: v for k, v in d.items() if not has_cjk(v)}
print(f"\nTotal untranslated (no CJK): {len(no_cjk)}")

# Save all untranslated keys and values into a JSON for inspection and mapping
with open(ROOT / ".agents" / "worker_m2_r2" / "untranslated.json", "w", encoding="utf-8") as out:
    json.dump(no_cjk, out, ensure_ascii=False, indent=2)

print(f"Saved {len(no_cjk)} untranslated items to untranslated.json")
