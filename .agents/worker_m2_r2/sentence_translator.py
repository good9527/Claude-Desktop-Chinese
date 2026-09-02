"""Sentence and Clause Level Translation Engine for Claude Desktop Chinese."""

import re
from typing import Dict, Tuple, List, Optional
from glossary import harmonize_text
from masking import mask_text, unmask_text
from vocab_tables import VERBS, NOUNS

# Grammar Pattern Mappings
CLAUSE_PATTERNS = [
    # Conditional / If clauses
    (re.compile(r"^If you get stuck,\s*(.*)$", re.I), r"如果您遇到问题，\1"),
    (re.compile(r"^If you don’t know or trust the source,\s*(.*)$", re.I), r"如果您不认识或不信任来源，\1"),
    (re.compile(r"^If you haven’t (.*?) yet,\s*(.*)$", re.I), r"如果您尚未\1，\2"),
    (re.compile(r"^If you’re interested,\s*(.*)$", re.I), r"如果您感兴趣，\1"),
    (re.compile(r"^If you’re (.*?),\s*(.*)$", re.I), r"如果您是\1，\2"),
    (re.compile(r"^If anyone still needs to (.*?),\s*(.*)$", re.I), r"如果有人仍需要\1，\2"),
    (re.compile(r"^If it doesn’t (.*?),\s*(.*)$", re.I), r"如果未\1，\2"),
    (re.compile(r"^If it isn’t (.*?),\s*(.*)$", re.I), r"如果未\1，\2"),
    (re.compile(r"^If none is selected,\s*(.*)$", re.I), r"如果未选择任何项，\1"),
    (re.compile(r"^If enabled,\s*(.*)$", re.I), r"如果已启用，\1"),
    (re.compile(r"^If disabled,\s*(.*)$", re.I), r"如果已禁用，\1"),

    # Once / When clauses
    (re.compile(r"^Once enabled,\s*(.*)$", re.I), r"启用后，\1"),
    (re.compile(r"^Once disabled,\s*(.*)$", re.I), r"禁用后，\1"),
    (re.compile(r"^Once allowed,\s*(.*)$", re.I), r"允许后，\1"),
    (re.compile(r"^Once members start using (.*?),\s*(.*)$", re.I), r"成员开始使用\1后，\2"),
    (re.compile(r"^When Xcode first opens,\s*(.*)$", re.I), r"首次打开 Xcode 时，\1"),
    (re.compile(r"^When you’re ready,\s*(.*)$", re.I), r"准备就绪后，\1"),

    # To ... / In order to ...
    (re.compile(r"^To record your screen and actions,\s*(.*)$", re.I), r"如需录制屏幕和操作，\1"),
    (re.compile(r"^To use (.*?),\s*(.*)$", re.I), r"如需使用\1，\2"),
    (re.compile(r"^To invite (.*?),\s*(.*)$", re.I), r"如需邀请\1，\2"),
    (re.compile(r"^To continue,\s*(.*)$", re.I), r"如需继续，\1"),
    (re.compile(r"^To get started,\s*(.*)$", re.I), r"如需开始使用，\1"),

    # Common prompts
    (re.compile(r"^Help me outline (.*?)$", re.I), r"帮我列出\1的大纲"),
    (re.compile(r"^Help me plan (.*?)$", re.I), r"帮我规划\1"),
    (re.compile(r"^Help me organize (.*?)$", re.I), r"帮我整理\1"),
    (re.compile(r"^Help me find (.*?)$", re.I), r"帮我查找\1"),
    (re.compile(r"^Help me turn (.*?)$", re.I), r"帮我将\1"),
    (re.compile(r"^Help me catch up on (.*?)$", re.I), r"帮我了解\1的最新动态"),
    (re.compile(r"^Help me (.*?)$", re.I), r"帮我\1"),
    (re.compile(r"^Explain (.*?) as simply as possible,\s*(.*)$", re.I), r"尽可能简单地解释\1，\2"),
    (re.compile(r"^Explain (.*?)$", re.I), r"解释\1"),
    (re.compile(r"^Summarize (.*?)$", re.I), r"总结\1"),
    (re.compile(r"^Review (.*?)$", re.I), r"审查\1"),
    (re.compile(r"^I want to (.*?)$", re.I), r"我想要\1"),
    (re.compile(r"^I’d like to (.*?)$", re.I), r"我想\1"),
    (re.compile(r"^I have a (.*?)$", re.I), r"我有一个\1"),
    (re.compile(r"^I’ll paste (.*?)$", re.I), r"我将在下方粘贴\1"),
    (re.compile(r"^I’m on a page with (.*?)$", re.I), r"我当前在一个包含\1的页面上"),
    (re.compile(r"^I keep running into (.*?)$", re.I), r"我一直遇到\1"),

    # Common UI sentences
    (re.compile(r"^This folder contains (.*?) and can’t be shared with this session\. Try a more specific folder instead\.$", re.I), r"此文件夹包含\1，无法与此会话共享。请尝试选择更具体的文件夹。"),
    (re.compile(r"^This setting can’t be changed in this chat$", re.I), r"无法在此聊天中更改此设置"),
    (re.compile(r"^This host is not allowed\.$", re.I), r"不允许访问此主机。"),
    (re.compile(r"^This channel is at (.*?) of its current spend limit\. Changes take effect immediately\.$", re.I), r"此频道已达到当前支出限额的 \1。更改会立即生效。"),
    (re.compile(r"^Only users in “(.*?)” organization can access (.*?)\. (.*)$", re.I), r"只有“\1”组织中的用户可以访问\2。\3"),
    (re.compile(r"^Folders where Claude may work\. (.*)$", re.I), r"Claude 可在其中工作的文件夹。\1"),
    (re.compile(r"^Routine created, but (.*?)\. (.*)$", re.I), r"例程已创建，但\1。\2"),
    (re.compile(r"^Microphone access wasn’t granted\. (.*)$", re.I), r"未授予麦克风访问权限。\1"),
    (re.compile(r"^Reconnection failed\. (.*)$", re.I), r"重新连接失败。\1"),
    (re.compile(r"^Cowork requires (.*)$", re.I), r"协同 (Cowork) 需要\1"),
    (re.compile(r"^Couldn’t load this environment\. Try again later\.$", re.I), r"无法加载此环境。请稍后重试。"),
    (re.compile(r"^Automatic approval couldn’t be turned on\. You can try again\.$", re.I), r"无法开启自动批准。您可以重试。"),
    (re.compile(r"^Please ensure you are not using your personal account\. (.*)$", re.I), r"请确保您使用的不是个人账户。\1"),
    (re.compile(r"^We’ll email you after we review your account\. (.*)$", re.I), r"我们审核您的账户后会向您发送电子邮件。\1"),
    (re.compile(r"^Can’t save your sign-in because (.*?)\. (.*)$", re.I), r"无法保存您的登录信息，因为\1。\2"),
]

def translate_clause(clause: str) -> str:
    """Translate a single clause using patterns and vocabularies."""
    c = clause.strip()
    for pat, repl in CLAUSE_PATTERNS:
        if pat.search(c):
            return pat.sub(repl, c)
    return c
