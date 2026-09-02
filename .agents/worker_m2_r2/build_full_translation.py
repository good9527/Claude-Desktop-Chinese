"""Comprehensive Multi-Tier Translation Compiler for Claude Desktop Chinese."""

import json
import re
import sys
from pathlib import Path
from typing import Dict, Tuple, List, Optional, Any

from glossary import harmonize_text

ROOT = Path(__file__).resolve().parents[2]
UNTRANSLATED_FILE = ROOT / ".agents" / "worker_m2_r2" / "untranslated.json"

with open(UNTRANSLATED_FILE, "r", encoding="utf-8") as f:
    untranslated = json.load(f)

print(f"Loaded {len(untranslated)} untranslated keys.")

# 1. Lexical and phrase dictionary
LEXICON = {
    # Actions & Verbs
    "add": "添加", "create": "创建", "delete": "删除", "remove": "移除",
    "edit": "编辑", "update": "更新", "save": "保存", "cancel": "取消",
    "confirm": "确认", "retry": "重试", "continue": "继续", "back": "返回",
    "next": "下一步", "close": "关闭", "open": "打开", "view": "查看",
    "search": "搜索", "filter": "筛选", "sort": "排序", "select": "选择",
    "choose": "选择", "download": "下载", "upload": "上传", "import": "导入",
    "export": "导出", "share": "分享", "publish": "发布", "archive": "归档",
    "unarchive": "取消归档", "enable": "启用", "disable": "禁用", "turn on": "开启",
    "turn off": "关闭", "switch": "切换", "upgrade": "升级", "downgrade": "降级",
    "manage": "管理", "configure": "配置", "install": "安装", "uninstall": "卸载",
    "connect": "连接", "disconnect": "断开连接", "reconnect": "重新连接",
    "invite": "邀请", "revoke": "撤销", "approve": "批准", "reject": "拒绝",
    "allow": "允许", "block": "阻止", "deny": "拒绝", "sign in": "登录",
    "sign out": "退出登录", "log in": "登录", "log out": "退出登录",
    "sign up": "注册", "register": "注册", "learn more": "了解更多",
    "read more": "阅读更多", "see all": "查看全部", "show all": "显示全部",
    "view all": "查看全部", "see details": "查看详情", "view details": "查看详情",
    "show more": "显示更多", "show less": "显示更少", "try again": "重试",
    "try now": "立即尝试", "upgrade now": "立即升级", "get started": "开始使用",
    "clear": "清除", "reset": "重置", "restore": "恢复", "copy": "复制",
    "paste": "粘贴", "cut": "剪切", "dismiss": "关闭", "ignore": "忽略",

    # UI Nouns
    "settings": "设置", "account": "账户", "profile": "个人资料",
    "security": "安全", "privacy": "隐私", "billing": "账单",
    "subscription": "订阅", "plan": "计划", "plans": "计划",
    "usage": "使用量", "limit": "限额", "limits": "限额",
    "spend limit": "支出限额", "spend limits": "支出限额",
    "usage credit": "使用额度", "usage credits": "使用额度",
    "credit": "额度", "credits": "额度",
    "member": "成员", "members": "成员",
    "group": "群组", "groups": "群组",
    "role": "角色", "roles": "角色",
    "permission": "权限", "permissions": "权限",
    "project": "项目", "projects": "项目",
    "artifact": "制品", "artifacts": "制品",
    "connector": "连接器", "connectors": "连接器",
    "plugin": "插件", "plugins": "插件",
    "marketplace": "市场", "directory": "目录",
    "skill": "技能", "skills": "技能",
    "tool": "工具", "tools": "工具",
    "session": "会话", "sessions": "会话",
    "chat": "聊天", "chats": "聊天",
    "conversation": "对话", "conversations": "对话",
    "message": "消息", "messages": "消息",
    "file": "文件", "files": "文件",
    "folder": "文件夹", "folders": "文件夹",
    "repository": "代码仓库", "repositories": "代码仓库",
    "repo": "代码仓库", "code": "代码",
    "terminal": "终端", "shell": "Shell",
    "runner": "运行器", "runners": "运行器",
    "workspace": "工作区", "workspaces": "工作区",
    "organization": "组织", "organizations": "组织",
    "admin": "管理员", "admins": "管理员",
    "owner": "所有者", "owners": "所有者",
    "user": "用户", "users": "用户",
    "guest": "访客", "guests": "访客",
    "seat": "席位", "seats": "席位",
    "routine": "例程", "routines": "例程",
    "prompt": "提示词", "prompts": "提示词",
    "model": "模型", "models": "模型",
    "environment": "环境", "environments": "环境",
    "task": "任务", "tasks": "任务",
    "status": "状态", "detail": "详情", "details": "详情",
    "error": "错误", "warning": "警告", "info": "信息",
    "help": "帮助", "support": "支持", "docs": "文档",
    "feedback": "反馈", "version": "版本",
    "name": "名称", "description": "描述", "title": "标题",
    "date": "日期", "time": "时间", "month": "月份", "year": "年份",
    "day": "天", "hour": "小时", "minute": "分钟", "second": "秒",
    "email": "邮箱", "password": "密码", "token": "令牌", "key": "密钥",
    "channel": "频道", "channels": "频道",
    "integration": "集成", "integrations": "集成",
}

print(f"Loaded {len(LEXICON)} core lexical entries.")
