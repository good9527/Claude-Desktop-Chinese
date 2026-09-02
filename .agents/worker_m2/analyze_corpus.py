import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(r"C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese")
ZH_FILE = ROOT / "dist" / "zh-CN.json"

data = json.load(ZH_FILE.open('r', encoding='utf-8-sig'))

def has_cjk(s: str) -> bool:
    return any('\u4e00' <= c <= '\u9fff' for c in s)

total = len(data)
cjk_keys = {k: v for k, v in data.items() if has_cjk(v)}
non_cjk_keys = {k: v for k, v in data.items() if not has_cjk(v)}

print(f"Total keys: {total}")
print(f"Keys with CJK: {len(cjk_keys)} ({len(cjk_keys)/total:.2%})")
print(f"Keys without CJK: {len(non_cjk_keys)} ({len(non_cjk_keys)/total:.2%})")

# Look at non_cjk keys
categories = {
    "pure_numbers_symbols": [],
    "single_words_technical": [],
    "icu_templates": [],
    "short_phrases": [],
    "long_sentences": [],
    "urls_paths": [],
}

for k, v in non_cjk_keys.items():
    s = v.strip()
    if not re.search(r'[a-zA-Z]', s):
        categories["pure_numbers_symbols"].append((k, v))
    elif re.match(r'^(?:https?://|mailto:|api://|wss://|urn:)\S+$', s) or s.startswith(('/', '~/', './')):
        categories["urls_paths"].append((k, v))
    elif '{' in s and ('plural' in s or 'select' in s):
        categories["icu_templates"].append((k, v))
    else:
        words = re.findall(r'[a-zA-Z0-9_\-]+', s)
        if len(words) == 1:
            categories["single_words_technical"].append((k, v))
        elif len(words) <= 4:
            categories["short_phrases"].append((k, v))
        else:
            categories["long_sentences"].append((k, v))

for cat, items in categories.items():
    print(f"Category '{cat}': {len(items)} keys")

print("\n--- Terminology Scan in existing CJK keys ---")
# Artifacts
art_en = [k for k, v in data.items() if 'Artifact' in v or 'artifact' in v]
art_gongjian1 = [k for k, v in data.items() if '工件' in v]
art_gongjian2 = [k for k, v in data.items() if '构件' in v]
art_chanwu = [k for k, v in data.items() if '产物' in v]
art_zhipin = [k for k, v in data.items() if '制品' in v]

print(f"Artifact/Artifacts in string: {len(art_en)}")
print(f"工件: {len(art_gongjian1)}")
print(f"构件: {len(art_gongjian2)}")
print(f"产物: {len(art_chanwu)}")
print(f"制品: {len(art_zhipin)}")

# Computer Use
cu_en = [k for k, v in data.items() if re.search(r'\bcomputer\s+use\b', v, re.IGNORECASE)]
cu_zh = [k for k, v in data.items() if '计算机使用' in v]
print(f"Computer Use (en): {len(cu_en)}")
print(f"计算机使用 (zh): {len(cu_zh)}")

# MCP
mcp_en = [k for k, v in data.items() if 'Model Context Protocol' in v]
mcp_zh = [k for k, v in data.items() if '模型上下文协议' in v]
mcp_abbr = [k for k, v in data.items() if 'MCP' in v]
print(f"Model Context Protocol (en): {len(mcp_en)}")
print(f"模型上下文协议 (zh): {len(mcp_zh)}")
print(f"MCP (abbr): {len(mcp_abbr)}")

# Context Window
cw_en = [k for k, v in data.items() if re.search(r'\bcontext\s+window\b', v, re.IGNORECASE)]
cw_zh = [k for k, v in data.items() if '上下文窗口' in v]
print(f"Context Window (en): {len(cw_en)}")
print(f"上下文窗口 (zh): {len(cw_zh)}")

# Extended Thinking / Thinking Mode
th_en = [k for k, v in data.items() if re.search(r'\b(extended\s+thinking|thinking\s+mode)\b', v, re.IGNORECASE)]
th_zh = [k for k, v in data.items() if '扩展思考' in v or '深度思考' in v]
print(f"Extended Thinking / Thinking Mode (en): {len(th_en)}")
print(f"扩展思考 / 深度思考 (zh): {len(th_zh)}")

# Connectors
conn_en = [k for k, v in data.items() if re.search(r'\bconnectors?\b', v, re.IGNORECASE)]
conn_zh = [k for k, v in data.items() if '连接器' in v]
print(f"Connectors (en): {len(conn_en)}")
print(f"连接器 (zh): {len(conn_zh)}")
