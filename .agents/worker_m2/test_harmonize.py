import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(r"C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese")
ZH_FILE = ROOT / "dist" / "zh-CN.json"
data = json.load(ZH_FILE.open('r', encoding='utf-8-sig'))

def harmonize_string(text: str) -> str:
    original = text
    
    # 1. Artifacts -> 制品
    # Replace variants: 工件, 构件, 产物 (in context of artifact)
    text = text.replace('工件', '制品')
    text = text.replace('构件', '制品')
    text = text.replace('切换产物', '切换制品')
    
    # Replace English Artifacts / Artifact in Chinese sentences
    # e.g., "AI 驱动的 Artifacts 已禁用", "在 Artifacts 中", "创建 Artifact", "Artifact 已分享"
    text = re.sub(r'(?i)\bArtifacts\b', '制品', text)
    text = re.sub(r'(?i)\bArtifact\b', '制品', text)
    
    # 2. Computer Use -> 计算机使用
    text = re.sub(r'(?i)\bcomputer\s+use\b', '计算机使用', text)
    
    # 3. Model Context Protocol -> 模型上下文协议 (MCP)
    text = text.replace('Model Context Protocol 文档', '模型上下文协议 (MCP) 文档')
    text = text.replace('Model Context Protocol', '模型上下文协议 (MCP)')
    
    # 4. Context Window -> 上下文窗口
    text = re.sub(r'(?i)\bcontext\s+window\b', '上下文窗口', text)
    
    # 5. Thinking mode -> 思考模式 / 深度思考
    text = re.sub(r'(?i)\bthinking\s+mode\b', '思考模式', text)
    text = re.sub(r'(?i)\bextended\s+thinking\b', '扩展思考', text)
    
    # 6. Connectors in Chinese context
    # Only if surrounded by Chinese or in Chinese context
    text = re.sub(r'(?<=[\u4e00-\u9fff])\s*Connectors?\s*(?=[\u4e00-\u9fff])', '连接器', text)
    text = re.sub(r'Connectors\s*设置', '连接器设置', text)
    text = re.sub(r'Connectors\s*目录', '连接器目录', text)
    
    return text

changes = []
for k, v in data.items():
    h = harmonize_string(v)
    if h != v:
        changes.append((k, v, h))

print(f"Total keys affected by harmonization in current dataset: {len(changes)}")
print("\nSample harmonization changes (first 20):")
for k, before, after in changes[:20]:
    print(f"[{k}]")
    print(f"  BEFORE: {before}")
    print(f"  AFTER:  {after}")
