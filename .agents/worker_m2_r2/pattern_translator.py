"""Comprehensive Translation Engine for Claude Desktop Chinese."""

import json
import re
import sys
from pathlib import Path
from typing import Dict, Tuple, List, Optional, Any

from glossary import harmonize_text
from masking import mask_text, unmask_text
from direct_translations import DIRECT_TRANSLATIONS, TECHNICAL_PRESERVE
from phrase_dict import EXACT_PHRASES
from icu_translations import ICU_EXACT_MAP
from vocab_tables import VERBS, NOUNS

ROOT = Path(__file__).resolve().parents[2]
UNTRANSLATED_FILE = ROOT / ".agents" / "worker_m2_r2" / "untranslated.json"

with open(UNTRANSLATED_FILE, "r", encoding="utf-8") as f:
    untranslated = json.load(f)

print(f"Loaded {len(untranslated)} untranslated items.")

def has_cjk(s: str) -> bool:
    return any("\u4e00" <= c <= "\u9fff" for c in s)

# Pattern-based translation rules
PATTERN_RULES = [
    # Failed / Couldn't / Unable to / Can't
    (re.compile(r"^Failed to save (.*?)\. Try again\.$", re.I), r"保存\1失败。请重试。"),
    (re.compile(r"^Failed to load (.*?)\. Try again\.$", re.I), r"加载\1失败。请重试。"),
    (re.compile(r"^Failed to update (.*?)\. Try again\.$", re.I), r"更新\1失败。请重试。"),
    (re.compile(r"^Failed to delete (.*?)\. Try again\.$", re.I), r"删除\1失败。请重试。"),
    (re.compile(r"^Failed to create (.*?)\. Try again\.$", re.I), r"创建\1失败。请重试。"),
    (re.compile(r"^Failed to upload (.*?)\. Try again\.$", re.I), r"上传\1失败。请重试。"),
    (re.compile(r"^Failed to connect to (.*?)\. Try again\.$", re.I), r"连接到\1失败。请重试。"),
    (re.compile(r"^Failed to (.*?)\. Try again\.$", re.I), r"\1失败。请重试。"),
    (re.compile(r"^Failed to (.*?)$", re.I), r"\1失败"),
    (re.compile(r"^Couldn’t save (.*?)\. Try again\.$", re.I), r"无法保存\1。请重试。"),
    (re.compile(r"^Couldn’t load (.*?)\. Try again\.$", re.I), r"无法加载\1。请重试。"),
    (re.compile(r"^Couldn’t update (.*?)\. Try again\.$", re.I), r"无法更新\1。请重试。"),
    (re.compile(r"^Couldn’t delete (.*?)\. Try again\.$", re.I), r"无法删除\1。请重试。"),
    (re.compile(r"^Couldn’t create (.*?)\. Try again\.$", re.I), r"无法创建\1。请重试。"),
    (re.compile(r"^Couldn’t find (.*?)\. Try again\.$", re.I), r"未找到\1。请重试。"),
    (re.compile(r"^Couldn’t (.*?)\. Try again later\.$", re.I), r"无法\1。请稍后重试。"),
    (re.compile(r"^Couldn’t (.*?)\. Try again\.$", re.I), r"无法\1。请重试。"),
    (re.compile(r"^Couldn’t (.*?)\. You can try again\.$", re.I), r"无法\1。您可以重试。"),
    (re.compile(r"^Couldn’t (.*?)$", re.I), r"无法\1"),
    (re.compile(r"^Could not (.*?)$", re.I), r"无法\1"),
    (re.compile(r"^Unable to (.*?)\. Try again\.$", re.I), r"无法\1。请重试。"),
    (re.compile(r"^Unable to (.*?)$", re.I), r"无法\1"),
    (re.compile(r"^Can’t (.*?)$", re.I), r"无法\1"),
    (re.compile(r"^Cannot (.*?)$", re.I), r"无法\1"),

    # Confirmation & Questions
    (re.compile(r"^Are you sure you want to delete (.*?)\?$", re.I), r"您确定要删除\1吗？"),
    (re.compile(r"^Are you sure you want to remove (.*?)\?$", re.I), r"您确定要移除\1吗？"),
    (re.compile(r"^Are you sure you want to (.*?)\?$", re.I), r"您确定要\1吗？"),
    (re.compile(r"^Allow Claude to (.*?)\?$", re.I), r"允许 Claude \1？"),
    (re.compile(r"^Delete (.*?)\?$", re.I), r"删除\1？"),
    (re.compile(r"^Remove (.*?)\?$", re.I), r"移除\1？"),
    (re.compile(r"^Archive (.*?)\?$", re.I), r"归档\1？"),
    (re.compile(r"^Reset (.*?)\?$", re.I), r"重置\1？"),

    # Common UI actions with parameters
    (re.compile(r"^Add (.*?)$", re.I), r"添加\1"),
    (re.compile(r"^Create (.*?)$", re.I), r"创建\1"),
    (re.compile(r"^Delete (.*?)$", re.I), r"删除\1"),
    (re.compile(r"^Remove (.*?)$", re.I), r"移除\1"),
    (re.compile(r"^Edit (.*?)$", re.I), r"编辑\1"),
    (re.compile(r"^Update (.*?)$", re.I), r"更新\1"),
    (re.compile(r"^Save (.*?)$", re.I), r"保存\1"),
    (re.compile(r"^Select (.*?)$", re.I), r"选择\1"),
    (re.compile(r"^Choose (.*?)$", re.I), r"选择\1"),
    (re.compile(r"^Manage (.*?)$", re.I), r"管理\1"),
    (re.compile(r"^View (.*?)$", re.I), r"查看\1"),
    (re.compile(r"^Open (.*?)$", re.I), r"打开\1"),
    (re.compile(r"^Close (.*?)$", re.I), r"关闭\1"),
    (re.compile(r"^Download (.*?)$", re.I), r"下载\1"),
    (re.compile(r"^Upload (.*?)$", re.I), r"上传\1"),
    (re.compile(r"^Import (.*?)$", re.I), r"导入\1"),
    (re.compile(r"^Export (.*?)$", re.I), r"导出\1"),
    (re.compile(r"^Share (.*?)$", re.I), r"分享\1"),
    (re.compile(r"^Publish (.*?)$", re.I), r"发布\1"),
    (re.compile(r"^Archive (.*?)$", re.I), r"归档\1"),
    (re.compile(r"^Enable (.*?)$", re.I), r"启用\1"),
    (re.compile(r"^Disable (.*?)$", re.I), r"禁用\1"),
    (re.compile(r"^Turn on (.*?)$", re.I), r"开启\1"),
    (re.compile(r"^Turn off (.*?)$", re.I), r"关闭\1"),
    (re.compile(r"^Switch to (.*?)$", re.I), r"切换至\1"),
    (re.compile(r"^Switch (.*?)$", re.I), r"切换\1"),
    (re.compile(r"^Connecting to (.*?)\.\.\.$", re.I), r"正在连接到\1..."),
    (re.compile(r"^Connecting to (.*?)$", re.I), r"正在连接到\1"),
    (re.compile(r"^Connected to (.*?)$", re.I), r"已连接到\1"),
    (re.compile(r"^Searching for (.*?)\.\.\.$", re.I), r"正在搜索\1..."),
    (re.compile(r"^Searching (.*?)\.\.\.$", re.I), r"正在搜索\1..."),
    (re.compile(r"^Loading (.*?)\.\.\.$", re.I), r"正在加载\1..."),
    (re.compile(r"^Loading (.*?)$", re.I), r"正在加载\1"),
    (re.compile(r"^Waiting for (.*?)\.\.\.$", re.I), r"正在等待\1..."),
    (re.compile(r"^Waiting for (.*?)$", re.I), r"正在等待\1"),
    (re.compile(r"^Enter a valid (.*?)$", re.I), r"请输入有效的\1"),
    (re.compile(r"^Enter (.*?)$", re.I), r"输入\1"),
    (re.compile(r"^Copy (.*?)$", re.I), r"复制\1"),
]

def translate_phrase(text: str) -> str:
    """Translate an English phrase to Simplified Chinese using lexical dictionary."""
    text_lower = text.strip().lower()
    if text_lower in LEXICON:
        return LEXICON[text_lower]
    if text_lower in NOUNS:
        return NOUNS[text_lower]
    if text_lower in VERBS:
        return VERBS[text_lower]
    return text

print(f"Loaded {len(PATTERN_RULES)} pattern rules.")
