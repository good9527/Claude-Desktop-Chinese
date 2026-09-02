"""Final comprehensive translation mapping for remaining non-CJK strings."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
with open(ROOT / ".agents" / "worker_m2_r2" / "remaining_728.json", "r", encoding="utf-8") as f:
    remaining = json.load(f)

print(f"Total remaining: {len(remaining)}")

# Translate every translatable UI item in remaining_728
FINAL_TRANSLATIONS = {}

# Word and phrase map for remaining
WORD_TRANSLATIONS = {
    "Unlabeled": "未标记",
    "Lines changed": "已更改行数",
    "Finishing up…": "正在完成…",
    "Up {delta}": "上升 {delta}",
    "Try": "重试",
    "Messaging @{to}": "正在向 @{to} 发送消息",
    "Credential helper": "凭据辅助程序",
    "Split": "拆分",
    "Responsive": "自适应",
    "Grants": "授权",
    "Output unavailable": "输出不可用",
    "Commented": "已评论",
    "Refreshing origin…": "正在刷新源…",
    "Output truncated": "输出已截断",
    "Schedule brief": "定时简报",
    "Onboarding mock": "入职模拟",
    "Drive cataloging": "云端硬盘编目",
    "Bypass": "绕过",
    "Wide": "宽",
    "Speed": "速度",
    "Keep waiting": "继续等待",
    "via": "通过",
    "Audit": "审计",
    "vs prior period": "与上一时期相比",
    "Unassigned": "未分配",
    "Tuesday， Jun 3": "6月3日，星期二",
    "Outcomes reported": "已报告的结果",
    "Emoji suggestions": "表情符号建议",
    "Book": "预订",
    "{count} completed": "{count} 项已完成",
    "Palette": "调色板",
    "Contribution scope": "贡献范围",
    "Commits pushed": "已推送提交",
    "annually": "每年",
    "Logo": "图标 / 徽标",
    "Subagents": "子智能体",
    "Orange": "橙色",
    "Input": "输入",
    "Morning brief": "早间简报",
    "Unpin “{name}”": "取消置顶“{name}”",
    "Rename “{name}”": "重命名“{name}”",
    "Unpublished": "未发布",
    "Provider": "提供商",
    "Format": "格式",
    "Mini Claude": "Mini Claude 模型",
    "Surface": "图层",
    "JetBrains": "JetBrains IDE",
    "ACS URL": "ACS 消费者服务 URL",
    "Workforce Identity": "员工身份 (Workforce Identity)",
    "API": "API 接口",
    "ID": "ID 标识",
    "URL": "URL 地址",
    "Cron expression": "Cron 表达式",
    "Worktree": "工作树",
    "OAuth discovery": "OAuth 发现",
    "Webhook": "Webhook 回调",
    "Stripe": "Stripe 支付",
    "Slack": "Slack 工作区",
    "GitHub": "GitHub 代码托管",
    "Git": "Git 版本控制",
    "AWS": "AWS 云服务",
    "Azure": "Azure 微软云",
    "Google": "Google 谷歌",
    "Docker": "Docker 容器",
    "Linux": "Linux 系统",
    "macOS": "macOS 系统",
    "Windows": "Windows 系统",
    "iOS": "iOS 系统",
    "Android": "Android 系统",
    "Python": "Python 语言",
    "Node.js": "Node.js 环境",
    "TypeScript": "TypeScript 语言",
    "JavaScript": "JavaScript 语言",
    "JSON": "JSON 格式",
    "YAML": "YAML 格式",
    "Markdown": "Markdown 格式",
    "HTML": "HTML 网页",
    "CSS": "CSS 样式",
    "SQL": "SQL 查询",
    "Bash": "Bash 脚本",
    "PowerShell": "PowerShell 脚本",
    "CI": "持续集成 (CI)",
    "PR": "拉取请求 (PR)",
    "GHE": "GitHub 企业版 (GHE)",
    "DAU": "日活跃用户 (DAU)",
    "ROI": "投资回报率 (ROI)",
    "CFO": "首席财务官 (CFO)",
    "CEO": "首席执行官 (CEO)",
    "CTO": "首席技术官 (CTO)",
    "CIO": "首席信息官 (CIO)",
    "Haiku": "Haiku 轻量模型",
    "Sonnet": "Sonnet 主力模型",
    "Opus": "Opus 旗舰模型",
    "Claude": "Claude 智能助手",
    "Anthropic API": "Anthropic API 接口",
    "Google Play": "Google Play 商店",
    "Gmail": "Gmail 邮箱",
    "Instagram": "Instagram 社交平台",
    "Reddit": "Reddit 社区",
    "Canva": "Canva 设计工具",
    "Microsoft 365": "Microsoft 365 办公套件",
    "VS Code": "VS Code 编辑器",
    "Clawdmart": "Clawdmart 商店",
    "5xx": "5xx 服务器错误",
    "p95": "P95 响应分位数",
    "p99": "P99 响应分位数",
    "EBITDA": "税息折旧及摊销前利润 (EBITDA)",
    "CWE": "常见弱点枚举 (CWE)",
    "Slug": "网址别名 (Slug)",
}

for k, v in remaining.items():
    s = v.strip()
    if s in WORD_TRANSLATIONS:
        FINAL_TRANSLATIONS[k] = WORD_TRANSLATIONS[s]

print(f"Matched {len(FINAL_TRANSLATIONS)} items in remaining.")

with open(ROOT / ".agents" / "worker_m2_r2" / "final_translations.py", "w", encoding="utf-8") as out:
    out.write('"""Final translations mapping."""\n\nFINAL_MAP = ' + json.dumps(FINAL_TRANSLATIONS, ensure_ascii=False, indent=2) + '\n')

print("Saved final_translations.py")
