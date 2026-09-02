"""Comprehensive Translation Engine and Dictionary Builder for Claude Desktop Chinese."""

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
from pattern_translator import PATTERN_RULES

ROOT = Path(__file__).resolve().parents[2]
UNTRANSLATED_FILE = ROOT / ".agents" / "worker_m2_r2" / "untranslated.json"

with open(UNTRANSLATED_FILE, "r", encoding="utf-8") as f:
    untranslated = json.load(f)

print(f"Loaded {len(untranslated)} untranslated items.")

def has_cjk(s: str) -> bool:
    return any("\u4e00" <= c <= "\u9fff" for c in s)

# Expanded phrase mappings for common UI components
EXPANDED_PHRASES = {
    # Spend & Billing
    "Daily spend limit": "每日支出限额",
    "Weekly spend limit": "每周支出限额",
    "Monthly spend limit": "每月支出限额",
    "Spend limit": "支出限额",
    "Spend limits": "支出限额",
    "Set spend limit": "设置支出限额",
    "Edit spend limit": "编辑支出限额",
    "Remove spend limit": "移除支出限额",
    "Current spend limit": "当前支出限额",
    "Usage limit": "使用限额",
    "Usage limits": "使用限额",
    "Usage credits": "使用额度",
    "Buy usage credits": "购买使用额度",
    "Promotional credit usage": "促销额度使用情况",
    "Auto-reload": "自动充值",
    "Payment method": "支付方式",
    "Payment methods": "支付方式",
    "Add payment method": "添加支付方式",
    "Billing settings": "账单设置",
    "Billing address": "账单地址",
    "Invoices": "发票",
    "Past invoices": "历史发票",
    
    # Orgs, Members, Workspaces
    "Organization settings": "组织设置",
    "Workspace settings": "工作区设置",
    "Member settings": "成员设置",
    "Invite members": "邀请成员",
    "Pending invitations": "待处理邀请",
    "Remove member": "移除成员",
    "Remove from organization": "从组织中移除",
    "Remove from workspace": "从工作区中移除",
    "Primary Owner": "主所有者",
    "Admin": "管理员",
    "Member": "成员",
    "Guest": "访客",
    "Custom roles": "自定义角色",
    "Create role": "创建角色",
    "Edit role": "编辑角色",
    "Delete role": "删除角色",
    "Assign role": "分配角色",
    
    # Projects & Chat
    "New project": "新建项目",
    "Project settings": "项目设置",
    "Project instructions": "项目指令",
    "Project files": "项目文件",
    "Project memory": "项目记忆",
    "Starred projects": "已加星标的项目",
    "Archived projects": "已归档项目",
    "Delete project": "删除项目",
    "Leave project": "离开项目",
    "New chat": "新聊天",
    "New conversation": "新对话",
    "Clear chat": "清除聊天",
    "Clear conversation": "清除对话",
    "Delete chat": "删除聊天",
    "Delete conversation": "删除对话",
    "Rename chat": "重命名聊天",
    "Rename conversation": "重命名对话",
    "Pin chat": "置顶聊天",
    "Unpin chat": "取消置顶聊天",
    
    # Terminal & Code & Cowork
    "Claude Code terminal": "Claude Code 终端",
    "Run in terminal": "在终端中运行",
    "Terminal output": "终端输出",
    "Command line tools": "命令行工具",
    "iOS Simulator": "iOS 模拟器",
    "Android Emulator": "Android 模拟器",
    "Run Cowork and Code on your own machine": "在您自己的计算机上运行 Cowork 和 Code",
    "Cowork session": "协同 (Cowork) 会话",
    "Code session": "代码 (Code) 会话",
    "Remote session": "远程会话",
    "Local session": "本地会话",
    "Start Code session": "启动代码会话",
    "Start Cowork session": "启动协同会话",
    "End session": "结束会话",
    
    # Connectors & MCP
    "Connector settings": "连接器设置",
    "Add connector": "添加连接器",
    "Edit connector": "编辑连接器",
    "Delete connector": "删除连接器",
    "Configure connector": "配置连接器",
    "Connect to GitHub": "连接到 GitHub",
    "Connect to Google Drive": "连接到 Google Drive",
    "Connect to Slack": "连接到 Slack",
    "Connect to Box": "连接到 Box",
    "Connect to Box enterprise": "连接到 Box 企业版",
    "Connected services": "已连接的服务",
    "Available connectors": "可用连接器",
    "Installed connectors": "已安装的连接器",
    "Plugin directory": "插件目录",
    "Plugin marketplace": "插件市场",
    "Install plugin": "安装插件",
    "Uninstall plugin": "卸载插件",
    "Submit plugin": "提交插件",
    "Review plugins": "审查插件",
    "Available tools": "可用工具",
    "Installed tools": "已安装的工具",
    "Always allow tool": "始终允许工具",
    "Ask every time for tool": "每次询问工具",
    
    # Errors & Statuses
    "Something went wrong": "发生错误",
    "An error occurred": "发生错误",
    "Network connection error": "网络连接错误",
    "Failed to fetch data": "获取数据失败",
    "Unable to load content": "无法加载内容",
    "Please try again in a moment": "请稍后重试",
    "Please check your network connection": "请检查您的网络连接",
    "Authentication failed": "身份验证失败",
    "Session expired": "会话已过期",
    "Please sign in again": "请重新登录",
    "Access denied": "访问被拒绝",
    "Permission denied": "权限不足",
    "Not authorized": "未授权",
    "Page not found": "页面未找到",
    "File not found": "文件未找到",
    "Directory not found": "目录未找到",
    "Invalid input": "输入无效",
    "Invalid parameter": "参数无效",
    "Invalid URL": "URL 无效",
    "Invalid email address": "邮箱地址无效",
    "Password too short": "密码太短",
    "Passwords do not match": "密码不匹配",
    "This field is required": "此字段为必填项",
    "Changes saved": "更改已保存",
    "All changes saved": "所有更改已保存",
    "Successfully deleted": "删除成功",
    "Successfully updated": "更新成功",
    "Successfully created": "创建成功",
    "Successfully connected": "连接成功",
    "Successfully disconnected": "断开连接成功",
    "Copied to clipboard": "已复制到剪贴板",
}

# Pre-compiled word replacement dict for clause translation
WORD_MAP = {}
WORD_MAP.update(LEXICON if 'LEXICON' in globals() else {})
WORD_MAP.update(VERBS)
WORD_MAP.update(NOUNS)

# Common helper words
HELPERS = {
    "the": "", "a": "一个", "an": "一个", "this": "此", "these": "这些",
    "that": "该", "those": "那些", "your": "您的", "my": "我的",
    "our": "我们的", "their": "他们的", "its": "其", "you": "您",
    "we": "我们", "they": "他们", "it": "它", "i": "我",
    "in": "在", "on": "在", "at": "在", "to": "到", "for": "为",
    "from": "从", "with": "使用", "by": "由", "of": "的",
    "and": "和", "or": "或", "not": "不", "no": "无",
    "is": "是", "are": "是", "was": "曾是", "were": "曾是",
    "can": "可以", "could": "可以", "will": "将", "would": "将",
    "should": "应当", "must": "必须", "may": "可能", "might": "可能",
    "all": "全部", "any": "任何", "some": "部分", "each": "每个",
    "every": "每个", "both": "两者", "other": "其他", "another": "另一个",
    "new": "新建", "old": "旧", "first": "首次", "last": "最后",
    "more": "更多", "less": "更少", "most": "最多", "least": "最少",
    "only": "仅", "also": "也", "now": "现在", "then": "然后",
    "here": "此处", "there": "彼处", "when": "当...时", "where": "在...处",
    "why": "为何", "how": "如何", "what": "什么", "which": "哪个",
    "who": "谁", "if": "如果", "because": "因为", "since": "由于",
    "so": "因此", "after": "在...之后", "before": "在...之前",
    "again": "再次", "later": "稍后", "soon": "即将", "always": "始终",
    "never": "从不", "sometimes": "有时", "often": "经常",
    "usually": "通常", "already": "已经", "still": "仍然",
    "yet": "尚未", "just": "刚刚", "almost": "几乎",
    "very": "非常", "too": "太", "enough": "足够",
}

print("Loaded comprehensive lexical rules.")
