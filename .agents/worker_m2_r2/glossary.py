"""Glossary and terminology harmonization rules for Claude Desktop Chinese."""

import re

# Terminology replacements to harmonize existing translations and standardize new ones
HARMONIZATION_RULES = [
    # 1. Artifacts -> 制品
    (re.compile(r"工件"), "制品"),
    (re.compile(r"构件"), "制品"),
    (re.compile(r"产物(?=中的|管理|列表|预览|分享|共享|创建|查看|删除)"), "制品"),
    (re.compile(r"\bArtifacts\b", re.IGNORECASE), "制品"),
    (re.compile(r"\bArtifact\b", re.IGNORECASE), "制品"),
    
    # 2. Model Context Protocol / MCP
    (re.compile(r"Model Context Protocol", re.IGNORECASE), "模型上下文协议 (MCP)"),
    (re.compile(r"\bMCP\s+servers?\b", re.IGNORECASE), "MCP 服务器"),
    (re.compile(r"\bMCP\s+tools?\b", re.IGNORECASE), "MCP 工具"),
    (re.compile(r"\bMCP\s+clients?\b", re.IGNORECASE), "MCP 客户端"),
    (re.compile(r"\bMCP\s+apps?\b", re.IGNORECASE), "MCP 应用"),
    (re.compile(r"\bMCP\s+applications?\b", re.IGNORECASE), "MCP 应用"),
    (re.compile(r"\bMCP\s+integrations?\b", re.IGNORECASE), "MCP 集成"),
    (re.compile(r"\bMCP\s+resources?\b", re.IGNORECASE), "MCP 资源"),
    (re.compile(r"\bMCP\s+prompts?\b", re.IGNORECASE), "MCP 提示词"),
    
    # 3. Computer Use -> 计算机使用
    (re.compile(r"\bComputer Use\b", re.IGNORECASE), "计算机使用"),
    (re.compile(r"\bcomputer use\b", re.IGNORECASE), "计算机使用"),
    
    # 4. Context Window -> 上下文窗口
    (re.compile(r"\bContext Window\b", re.IGNORECASE), "上下文窗口"),
    (re.compile(r"\bcontext window\b", re.IGNORECASE), "上下文窗口"),
    (re.compile(r"\bContext limit\b", re.IGNORECASE), "上下文限制"),
    (re.compile(r"\bcontext limit\b", re.IGNORECASE), "上下文限制"),
    
    # 5. Extended Thinking / Thinking Mode -> 扩展思考 / 思考模式 / 深度思考
    (re.compile(r"\bExtended Thinking\b", re.IGNORECASE), "扩展思考"),
    (re.compile(r"\bextended thinking\b", re.IGNORECASE), "扩展思考"),
    (re.compile(r"\bThinking Mode\b", re.IGNORECASE), "思考模式"),
    (re.compile(r"\bthinking mode\b", re.IGNORECASE), "思考模式"),
    (re.compile(r"\bThinking transcript\b", re.IGNORECASE), "思考过程记录"),
    (re.compile(r"\bthinking transcript\b", re.IGNORECASE), "思考过程记录"),
    (re.compile(r"\bThinking process\b", re.IGNORECASE), "思考过程"),
    (re.compile(r"\bthinking process\b", re.IGNORECASE), "思考过程"),
    
    # 6. Connectors -> 连接器
    (re.compile(r"\bConnectors\b", re.IGNORECASE), "连接器"),
    (re.compile(r"\bConnector\b", re.IGNORECASE), "连接器"),
    (re.compile(r"\bconnectors\b", re.IGNORECASE), "连接器"),
    (re.compile(r"\bconnector\b", re.IGNORECASE), "连接器"),
    
    # 7. Prompt Caching -> 提示词缓存
    (re.compile(r"\bPrompt Caching\b", re.IGNORECASE), "提示词缓存"),
    (re.compile(r"\bprompt caching\b", re.IGNORECASE), "提示词缓存"),
    (re.compile(r"\bPrompt Cache\b", re.IGNORECASE), "提示词缓存"),
    (re.compile(r"\bprompt cache\b", re.IGNORECASE), "提示词缓存"),
    
    # 8. Custom Instructions -> 自定义指令
    (re.compile(r"\bCustom Instructions\b", re.IGNORECASE), "自定义指令"),
    (re.compile(r"\bcustom instructions\b", re.IGNORECASE), "自定义指令"),
    
    # 9. Cowork / Routines
    (re.compile(r"\bCowork\b"), "协同 (Cowork)"),
    (re.compile(r"\bRoutines\b"), "例程"),
    (re.compile(r"\bRoutine\b"), "例程"),
]

def harmonize_text(text: str) -> str:
    """Apply terminology harmonization to a translated string."""
    result = text
    # Avoid replacing inside placeholders or URLs or tags
    # Mask placeholders first
    placeholders = {}
    counter = 0
    def mask_match(m):
        nonlocal counter
        k = f"__GLOSSARY_PH_{counter}__"
        placeholders[k] = m.group(0)
        counter += 1
        return k
    
    # Mask tags, placeholders, and URLs
    result = re.sub(r"\{[^{}]+\}", mask_match, result)
    result = re.sub(r"</?[a-zA-Z][^>]*>", mask_match, result)
    result = re.sub(r"https?://[^\s]+", mask_match, result)
    
    # Apply harmonization
    for pattern, replacement in HARMONIZATION_RULES:
        result = pattern.sub(replacement, result)
        
    # Unmask
    for k, v in placeholders.items():
        result = result.replace(k, v)
        
    return result
