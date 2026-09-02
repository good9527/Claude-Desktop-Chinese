"""Master translation script for Claude Desktop Chinese localization."""

import json
import re
import sys
from pathlib import Path

# Load submodules
from .dictionary_builder import apply_glossary_harmonization, clean_chinese_spacing

def has_cjk(s: str) -> bool:
    return any('\u4e00' <= c <= '\u9fff' for c in s)

print("Master translator loaded.")
