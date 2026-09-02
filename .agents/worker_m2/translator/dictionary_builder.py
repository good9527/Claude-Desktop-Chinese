"""Dictionary builder and translation engine for Claude Desktop Chinese Localization.
Translates all untranslated keys and harmonizes AI developer terminology.
"""

import json
import re
import sys
from pathlib import Path

# Glossary for AI Developer Terminology & UI Standard
AI_GLOSSARY = {
    # Terminology Requirements
    "Artifacts": "制品",
    "Artifact": "制品",
    "artifacts": "制品",
    "artifact": "制品",
    "Model Context Protocol": "模型上下文协议 (MCP)",
    "MCP Server": "MCP 服务器",
    "MCP Servers": "MCP 服务器",
    "MCP server": "MCP 服务器",
    "MCP servers": "MCP 服务器",
    "MCP Tool": "MCP 工具",
    "MCP Tools": "MCP 工具",
    "MCP tool": "MCP 工具",
    "MCP tools": "MCP 工具",
    "MCP Directory": "MCP 目录",
    "MCP directory": "MCP 目录",
    "Computer Use": "计算机使用",
    "computer use": "计算机使用",
    "Context Window": "上下文窗口",
    "Context window": "上下文窗口",
    "context window": "上下文窗口",
    "Extended Thinking": "扩展思考",
    "extended thinking": "扩展思考",
    "Thinking Mode": "深度思考",
    "Thinking mode": "深度思考",
    "thinking mode": "深度思考",
    "Connectors": "连接器",
    "Connector": "连接器",
    "connectors": "连接器",
    "connector": "连接器",
    "Prompt Caching": "提示词缓存",
    "Custom Instructions": "自定义指令",
    "Knowledge Base": "知识库",
}

def clean_chinese_spacing(text: str) -> str:
    """Remove unnatural spaces between Chinese characters and punctuation."""
    # Remove spaces between Chinese characters
    text = re.sub(r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])', r'\1\2', text)
    # Remove spaces before Chinese punctuation
    text = re.sub(r'\s+([，。！？；：“”’‘（）《》【】])', r'\1', text)
    # Remove spaces after opening Chinese punctuation
    text = re.sub(r'([“‘（《【])\s+', r'\1', text)
    # Remove spaces between Chinese and Chinese punctuation
    text = re.sub(r'([\u4e00-\u9fff])\s+([，。！？；：）”’》】])', r'\1\2', text)
    text = re.sub(r'([（“‘《【])\s+([\u4e00-\u9fff])', r'\1\2', text)
    return text

def apply_glossary_harmonization(text: str) -> str:
    """Apply strict developer terminology harmonization across any string."""
    # Replace inconsistent artifact variants
    text = text.replace('工件', '制品')
    text = text.replace('构件', '制品')
    text = text.replace('切换产物', '切换制品')
    
    # Replace Artifacts / Artifact in Chinese sentences
    text = re.sub(r'(?i)\bArtifacts\b', '制品', text)
    text = re.sub(r'(?i)\bArtifact\b', '制品', text)
    
    # Computer Use
    text = re.sub(r'(?i)\bcomputer\s+use\b', '计算机使用', text)
    
    # Model Context Protocol
    text = text.replace('Model Context Protocol 文档', '模型上下文协议 (MCP) 文档')
    text = text.replace('Model Context Protocol', '模型上下文协议 (MCP)')
    
    # Context Window
    text = re.sub(r'(?i)\bcontext\s+window\b', '上下文窗口', text)
    
    # Thinking Mode
    text = re.sub(r'(?i)\bthinking\s+mode\b', '思考模式', text)
    text = re.sub(r'(?i)\bextended\s+thinking\b', '扩展思考', text)
    
    # Connectors in Chinese context
    text = re.sub(r'(?<=[\u4e00-\u9fff])\s*Connectors?\s*(?=[\u4e00-\u9fff])', '连接器', text)
    text = re.sub(r'Connectors\s*设置', '连接器设置', text)
    text = re.sub(r'Connectors\s*目录', '连接器目录', text)
    
    return clean_chinese_spacing(text)
