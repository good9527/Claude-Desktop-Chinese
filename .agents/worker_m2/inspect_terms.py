import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(r"C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese")
ZH_FILE = ROOT / "dist" / "zh-CN.json"

data = json.load(ZH_FILE.open('r', encoding='utf-8-sig'))

print("=== 1. ARTIFACTS / 工件 / 构件 / 产物 ===")
for k, v in data.items():
    if any(term in v for term in ['工件', '构件', '产物', 'Artifact', 'artifact']):
        print(f"{k}: {v}")

print("\n=== 2. COMPUTER USE / 计算机使用 ===")
for k, v in data.items():
    if re.search(r'\bcomputer\s+use\b', v, re.IGNORECASE) or '计算机使用' in v:
        print(f"{k}: {v}")

print("\n=== 3. MODEL CONTEXT PROTOCOL / MCP ===")
for k, v in data.items():
    if 'Model Context Protocol' in v or '模型上下文协议' in v:
        print(f"{k}: {v}")

print("\n=== 4. CONTEXT WINDOW / 上下文窗口 ===")
for k, v in data.items():
    if re.search(r'\bcontext\s+window\b', v, re.IGNORECASE) or '上下文' in v:
        if '窗口' in v or 'window' in v.lower():
            print(f"{k}: {v}")

print("\n=== 5. EXTENDED THINKING / THINKING MODE ===")
for k, v in data.items():
    if re.search(r'\b(extended\s+thinking|thinking\s+mode)\b', v, re.IGNORECASE) or '扩展思考' in v or '深度思考' in v:
        print(f"{k}: {v}")

print("\n=== 6. CONNECTORS / 连接器 ===")
for k, v in data.items():
    if re.search(r'\bconnectors?\b', v, re.IGNORECASE):
        print(f"{k}: {v}")
