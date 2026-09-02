"""Comprehensive translation engine for Claude Desktop Chinese."""

import re
import json
from typing import Dict, Tuple, List, Optional
from glossary import harmonize_text

# Regular expressions for protected elements
RE_ICU = re.compile(r"\{[^{}]*,\s*(?:plural|select|number|date|time)[^{}]*(?:\{[^{}]*\}[^{}]*)*\}")
RE_PLACEHOLDER = re.compile(r"\{[^{}]+\}")
RE_TAG = re.compile(r"</?[a-zA-Z0-9_\-]+(?:\s+[^>]*)?>")
RE_URL = re.compile(r"https?://[^\s\"'<>)]+")
RE_CODE = re.compile(r"`[^`]+`")
RE_SHORTCUT = re.compile(r"\b(?:Ctrl|Cmd|Option|Alt|Shift|Enter|Space|Esc|Tab)\b(?:\s*\+\s*\b(?:Ctrl|Cmd|Option|Alt|Shift|Enter|Space|Esc|Tab|[A-Z0-9])\b)+")

def mask_text(text: str) -> Tuple[str, Dict[str, str]]:
    """Mask placeholders, tags, URLs, code blocks, and shortcuts."""
    placeholders = {}
    counter = 0

    def add_mask(m):
        nonlocal counter
        k = f"__TOKEN_PH_{counter}__"
        placeholders[k] = m.group(0)
        counter += 1
        return k

    # Mask in order of complexity
    masked = RE_CODE.sub(add_mask, text)
    masked = RE_URL.sub(add_mask, masked)
    masked = RE_TAG.sub(add_mask, masked)
    masked = RE_ICU.sub(add_mask, masked)
    masked = RE_PLACEHOLDER.sub(add_mask, masked)
    
    return masked, placeholders

def unmask_text(text: str, placeholders: Dict[str, str]) -> str:
    """Restore masked placeholders."""
    result = text
    for k, v in placeholders.items():
        result = result.replace(k, v)
    return result
