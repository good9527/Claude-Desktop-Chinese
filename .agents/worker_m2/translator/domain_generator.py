"""Domain translation generator implementing natural, idiomatic Simplified Chinese translation."""

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
agent_dir = Path(r"C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese\.agents\worker_m2")
domains = json.load(open(agent_dir / "domains.json", "r", encoding="utf-8"))

def clean_chinese(text: str) -> str:
    # Harmonize terminology
    text = text.replace('工件', '制品')
    text = text.replace('构件', '制品')
    text = text.replace('切换产物', '切换制品')
    
    text = re.sub(r'(?i)\bArtifacts\b', '制品', text)
    text = re.sub(r'(?i)\bArtifact\b', '制品', text)
    text = re.sub(r'(?i)\bcomputer\s+use\b', '计算机使用', text)
    text = text.replace('Model Context Protocol 文档', '模型上下文协议 (MCP) 文档')
    text = text.replace('Model Context Protocol', '模型上下文协议 (MCP)')
    text = re.sub(r'(?i)\bcontext\s+window\b', '上下文窗口', text)
    text = re.sub(r'(?i)\bthinking\s+mode\b', '思考模式', text)
    text = re.sub(r'(?i)\bextended\s+thinking\b', '扩展思考', text)
    text = re.sub(r'(?<=[\u4e00-\u9fff])\s*Connectors?\s*(?=[\u4e00-\u9fff])', '连接器', text)
    text = re.sub(r'Connectors\s*设置', '连接器设置', text)
    text = re.sub(r'Connectors\s*目录', '连接器目录', text)
    
    # Remove spacing
    text = re.sub(r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])', r'\1\2', text)
    text = re.sub(r'\s+([，。！？；：“”’‘（）《》【】])', r'\1', text)
    text = re.sub(r'([“‘（《【])\s+', r'\1', text)
    text = re.sub(r'([\u4e00-\u9fff])\s+([，。！？；：）”’》】])', r'\1\2', text)
    text = re.sub(r'([（“‘《【])\s+([\u4e00-\u9fff])', r'\1\2', text)
    return text

print("Domain generator helper initialized.")
