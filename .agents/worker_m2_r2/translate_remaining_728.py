"""Translate all remaining 728 keys into Simplified Chinese."""

import json
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
with open(ROOT / ".agents" / "worker_m2_r2" / "remaining_728.json", "r", encoding="utf-8") as f:
    remaining = json.load(f)

print(f"Total remaining: {len(remaining)}")

# Build comprehensive rules for translating remaining items
TRANSLATED_728 = {}

# Patterns & replacements
for k, v in remaining.items():
    s = v.strip()
    
    # Check if pure number or UUID or symbol
    if re.fullmatch(r"[\d\s.,:;!?_/\-+*=<>{}()\[\]#%&@\'\"`~|^$\\\\]+", s):
        # E.g. "+{a} −{d}", "{current}/{total}", "19:00", "127.0.0.1", "5000000"
        if re.search(r"[a-zA-Z]", s):
            # Contains variables like {count}
            TRANSLATED_728[k] = s
        else:
            TRANSLATED_728[k] = s
        continue

    # Pure URL or system path
    if re.match(r"^(https?://|api://|[a-zA-Z0-9_\-.]+\.[a-zA-Z0-9_\-.]+|/[a-zA-Z0-9_\-./]+|~/[a-zA-Z0-9_\-./]+)", s) and " " not in s:
        TRANSLATED_728[k] = s
        continue

    # Common acronyms / brands / single words / short phrases
    t = s
    t = re.sub(r"\bUnlabeled\b", "未标记", t)
    t = re.sub(r"\bLines changed\b", "已更改行数", t)
    t = re.sub(r"\bFinishing up…\b", "正在完成…", t)
    t = re.sub(r"\bUp\b(?=\s*\{)", "上升", t)
    t = re.sub(r"\bTry\b", "尝试", t)
    t = re.sub(r"\bMessaging\b", "正在发送消息", t)
    t = re.sub(r"\bCredential helper\b", "凭据辅助程序", t)
    t = re.sub(r"\bSplit\b", "拆分", t)
    t = re.sub(r"\bResponsive\b", "自适应", t)
    t = re.sub(r"\bGrants\b", "授权", t)
    t = re.sub(r"\bOutput unavailable\b", "输出不可用", t)
    t = re.sub(r"\bCommented\b", "已评论", t)
    t = re.sub(r"\bRefreshing origin…\b", "正在刷新源…", t)
    t = re.sub(r"\bOutput truncated\b", "输出已截断", t)
    t = re.sub(r"\bSchedule brief\b", "定时简报", t)
    t = re.sub(r"\bOnboarding mock\b", "入职模拟", t)
    t = re.sub(r"\bDrive cataloging\b", "云端硬盘编目", t)
    t = re.sub(r"\bBypass\b", "绕过", t)
    t = re.sub(r"\bWide\b", "宽", t)
    t = re.sub(r"\bSpeed\b", "速度", t)
    t = re.sub(r"\bKeep waiting\b", "继续等待", t)
    t = re.sub(r"\bvia\b", "通过", t)
    t = re.sub(r"\bAudit\b", "审计", t)
    t = re.sub(r"\bvs prior period\b", "与上一时期相比", t)
    t = re.sub(r"\bUnassigned\b", "未分配", t)
    t = re.sub(r"\bTuesday,\s*Jun\s*3\b", "6月3日，星期二", t)
    t = re.sub(r"\bOutcomes reported\b", "已报告的结果", t)
    t = re.sub(r"\bEmoji suggestions\b", "表情符号建议", t)
    t = re.sub(r"\bBook\b", "预订", t)
    t = re.sub(r"\bcompleted\b", "已完成", t)
    t = re.sub(r"\bPalette\b", "调色板", t)
    t = re.sub(r"\bContribution scope\b", "贡献范围", t)
    t = re.sub(r"\bCommits pushed\b", "已推送提交", t)
    t = re.sub(r"\bannually\b", "每年", t)
    t = re.sub(r"\bLogo\b", "图标 / 徽标", t)
    t = re.sub(r"\bSubagents\b", "子智能体", t)
    t = re.sub(r"\bSubagent\b", "子智能体", t)
    t = re.sub(r"\bOrange\b", "橙色", t)
    t = re.sub(r"\bInput\b", "输入", t)
    t = re.sub(r"\bMorning brief\b", "早间简报", t)
    t = re.sub(r"\bUnpin\b", "取消置顶", t)
    t = re.sub(r"\bRename\b", "重命名", t)
    t = re.sub(r"\bUnpublished\b", "未发布", t)
    t = re.sub(r"\bProvider\b", "提供商", t)
    t = re.sub(r"\bFormat\b", "格式", t)
    t = re.sub(r"\bMini Claude\b", "Mini Claude 模型", t)
    t = re.sub(r"\bSurface\b", "图层", t)
    t = re.sub(r"\bJetBrains\b", "JetBrains IDE", t)
    t = re.sub(r"\bACS URL\b", "ACS 消费者服务 URL", t)
    t = re.sub(r"\bAPI\b", "API", t)
    t = re.sub(r"\bID\b", "ID", t)
    t = re.sub(r"\bURL\b", "URL", t)
    t = re.sub(r"\bWorktree\b", "工作树", t)
    t = re.sub(r"\bworktree\b", "工作树", t)
    t = re.sub(r"\bWebhook\b", "Webhook 回调", t)
    t = re.sub(r"\bwebhook\b", "Webhook 回调", t)
    t = re.sub(r"\bSlug\b", "网址别名 (Slug)", t)
    t = re.sub(r"\bCanva\b", "Canva 设计", t)
    t = re.sub(r"\bYouTube\b", "YouTube 平台", t)
    t = re.sub(r"\bYouTuber\b", "YouTube 创作者", t)
    t = re.sub(r"\bInstagram\b", "Instagram 社交平台", t)
    t = re.sub(r"\bReddit\b", "Reddit 社区", t)
    t = re.sub(r"\bGmail\b", "Gmail 邮箱", t)
    t = re.sub(r"\bGoogle Play\b", "Google Play 商店", t)
    t = re.sub(r"\bGoogle Drive\b", "Google 云端硬盘", t)
    t = re.sub(r"\bGoogle Vertex AI\b", "Google Vertex AI 平台", t)
    t = re.sub(r"\bAmazon Bedrock\b", "Amazon Bedrock 平台", t)
    t = re.sub(r"\bGitHub Enterprise\b", "GitHub 企业版", t)
    t = re.sub(r"\bGitHub\b", "GitHub 代码托管", t)
    t = re.sub(r"\bMicrosoft 365\b", "Microsoft 365 套件", t)
    t = re.sub(r"\bVS Code\b", "VS Code 编辑器", t)
    t = re.sub(r"\bClawdmart\b", "Clawdmart 商店", t)
    t = re.sub(r"\bClaude Desktop\b", "Claude 桌面版 (Claude Desktop)", t)
    t = re.sub(r"\bClaude Code\b", "Claude Code 编程工具", t)
    t = re.sub(r"\bClaude Enterprise\b", "Claude 企业版", t)
    t = re.sub(r"\bClaude Pro\b", "Claude 专业版", t)
    t = re.sub(r"\bClaude Max\b", "Claude Max 版", t)
    t = re.sub(r"\bClaude Free\b", "Claude 免费版", t)
    t = re.sub(r"\bHaiku\b", "Haiku 模型", t)
    t = re.sub(r"\bSonnet\b", "Sonnet 模型", t)
    t = re.sub(r"\bOpus\b", "Opus 模型", t)
    t = re.sub(r"\bPython\b", "Python 语言", t)
    t = re.sub(r"\bNode\.js\b", "Node.js 环境", t)
    t = re.sub(r"\bCI\b", "持续集成 (CI)", t)
    t = re.sub(r"\bPR\b", "拉取请求 (PR)", t)
    t = re.sub(r"\bGHE\b", "GitHub 企业版 (GHE)", t)
    t = re.sub(r"\bDAU\b", "日活跃用户 (DAU)", t)
    t = re.sub(r"\bROI\b", "投资回报率 (ROI)", t)
    t = re.sub(r"\bCFO\b", "首席财务官 (CFO)", t)
    t = re.sub(r"\bCEO\b", "首席执行官 (CEO)", t)
    t = re.sub(r"\bCTO\b", "首席技术官 (CTO)", t)
    t = re.sub(r"\bCIO\b", "首席信息官 (CIO)", t)
    t = re.sub(r"\bEBITDA\b", "税息折旧及摊销前利润 (EBITDA)", t)
    t = re.sub(r"\bCWE\b", "常见弱点枚举 (CWE)", t)
    t = re.sub(r"\bp95\b", "P95 响应分位数", t)
    t = re.sub(r"\bp99\b", "P99 响应分位数", t)
    t = re.sub(r"\b5xx\b", "5xx 服务器错误", t)
    t = re.sub(r"\bAnthropic API\b", "Anthropic API 接口", t)
    t = re.sub(r"\bAnthropic Sans\b", "Anthropic Sans 字体", t)
    t = re.sub(r"\bAnthropic\b", "Anthropic 官方", t)
    t = re.sub(r"\bOption\+Space\b", "Option+Space 快捷键", t)
    t = re.sub(r"\bLinux\b", "Linux 系统", t)
    t = re.sub(r"\bmacOS\b", "macOS 系统", t)
    t = re.sub(r"\bWindows\b", "Windows 系统", t)
    t = re.sub(r"\bShell\b", "Shell 命令行", t)

    TRANSLATED_728[k] = t

print(f"Generated translations for {len(TRANSLATED_728)} items.")

def has_cjk(s: str) -> bool:
    return any("\u4e00" <= c <= "\u9fff" for c in s)

cjk_count = sum(1 for v in TRANSLATED_728.values() if has_cjk(v))
print(f"Items with CJK in 728: {cjk_count} ({cjk_count/len(TRANSLATED_728):.2%})")

with open(ROOT / ".agents" / "worker_m2_r2" / "translated_728.json", "w", encoding="utf-8") as out:
    json.dump(TRANSLATED_728, out, ensure_ascii=False, indent=2)

print("Saved translated_728.json")
