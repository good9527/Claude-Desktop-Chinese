"""Comprehensive sentence pattern translation rules for Claude Desktop."""

import re

# Sentence pattern rules (regex pattern -> replacement with Chinese template)
SENTENCE_PATTERNS = [
    # Error & Failure patterns
    (r"(?i)^couldn’t add this chat to a project\.?\s*you can try again\.?$", "无法将此对话添加到项目中。您可以重试。"),
    (r"(?i)^couldn’t create project\.?\s*you can try again\.?$", "无法创建项目。您可以重试。"),
    (r"(?i)^couldn’t update project\.?\s*you can try again\.?$", "无法更新项目。您可以重试。"),
    (r"(?i)^couldn’t delete project\.?\s*you can try again\.?$", "无法删除项目。您可以重试。"),
    (r"(?i)^couldn’t load project\.?\s*you can try again\.?$", "无法加载项目。您可以重试。"),
    (r"(?i)^couldn’t load projects\.?\s*you can try again\.?$", "无法加载项目列表。您可以重试。"),
    (r"(?i)^couldn’t load settings\.?\s*you can try again\.?$", "无法加载设置。您可以重试。"),
    (r"(?i)^couldn’t save settings\.?\s*you can try again\.?$", "无法保存设置。您可以重试。"),
    (r"(?i)^couldn’t load connector details\.?\s*please try again\.?$", "无法加载连接器详情。请重试。"),
    (r"(?i)^couldn’t load connectors\.?$", "无法加载连接器。"),
    (r"(?i)^couldn’t load the connector directory\.?\s*check your connection and retry\.?$", "无法加载连接器目录。请检查您的网络连接并重试。"),
    (r"(?i)^failed to suggest connectors$", "未能推荐连接器"),
    (r"(?i)^failed to add the connector$", "未能添加连接器"),
    (r"(?i)^no connectors available$", "没有可用的连接器"),
    (r"(?i)^no connectors match your search$", "没有与您的搜索匹配的连接器"),
    (r"(?i)^browse all connectors$", "浏览所有连接器"),
    (r"(?i)^top connectors$", "热门连接器"),
    (r"(?i)^related connectors$", "相关连接器"),
    (r"(?i)^refresh connectors$", "刷新连接器"),
    (r"(?i)^manage organization connectors$", "管理组织连接器"),
    (r"(?i)^manage mcp connectors$", "管理 MCP 连接器"),
    
    # Artifacts patterns
    (r"(?i)^only users in “\{orgName\}” organization can access artifacts you share\.?\s*new versions will be shared automatically when this artifact changes\.?$", "仅“{orgName}”组织中的用户可以访问您分享的制品。当此制品更改时，新版本将自动分享。"),
    (r"(?i)^shared artifacts will be deleted after \{count, plural, one \{# month\} other \{# months\}\} of inactivity$", "共享制品将在处于非活动状态 {count, plural, one {# 个月} other {# 个月}} 后被删除"),
    (r"(?i)^the \{artifactId\} live artifact uses connectors you haven’t set up yet:?$", "{artifactId} 实时制品使用了您尚未设置的连接器："),
    (r"(?i)^create your first artifact$", "创建您的第一个制品"),
    (r"(?i)^this artifact was previously unpublished\.?\s*create a new artifact to publish again\.?$", "此制品之前已取消发布。请创建新制品以重新发布。"),
    (r"(?i)^artifact unpublished$", "制品已取消发布"),
    (r"(?i)^artifact unshared$", "制品已取消分享"),
    (r"(?i)^limit reached\.?\s*this artifact uses claude to generate responses\.?\s*try again once your message limit resets\.?$", "已达到限额。此制品使用 Claude 生成回复。请在消息限额重置后重试。"),
    (r"(?i)^drafting artifact…$", "正在起草制品…"),
    (r"(?i)^anyone in your organization can view this artifact\.?\s*it will also have access to attachments and files in the chat\.?$", "您组织中的任何人都可以查看此制品。它还可以访问对话中的附件和文件。"),
    (r"(?i)^total artifacts created on \{date\} \(utc\)\.?\s*delta is relative to the same day of the prior week\.?$", "{date}（UTC）创建的制品总数。变化量相对于上周同日。"),

    # Computer Use patterns
    (r"(?i)^turn on computer use in settings, then try recording again\.?$", "在“设置”中开启计算机使用，然后重试录制。"),
    (r"(?i)^turn on computer use in settings\.?$", "在“设置”中开启计算机使用。"),
    (r"(?i)^computer use is disabled\.?$", "计算机使用已禁用。"),
    (r"(?i)^enable computer use$", "启用计算机使用"),
    (r"(?i)^disable computer use$", "禁用计算机使用"),

    # Thinking mode patterns
    (r"(?i)^change thinking mode\??$", "更改思考模式？"),
    (r"(?i)^this project requires extended thinking\.?$", "此项目需要扩展思考。"),
    (r"(?i)^extended thinking is enabled\.?$", "扩展思考已启用。"),
    (r"(?i)^extended thinking is disabled\.?$", "扩展思考已禁用。"),

    # Context window patterns
    (r"(?i)^context window was full\.?$", "上下文窗口已满。"),
    (r"(?i)^conversation reached the context limit\.?$", "对话已达到上下文限制。"),
    (r"(?i)^enhance context window$", "扩展上下文窗口"),

    # Usage & Limits patterns
    (r"(?i)^you’re out of extra usage\.?\s*buy more to keep going now\.?$", "您的额外用量已用尽。立即购买更多以继续使用。"),
    (r"(?i)^you’ve reached your daily read aloud limit\.?$", "您已达到每日朗读上限。"),
    (r"(?i)^for a better first pass, add details like format and audience upfront\.?$", "为了获得更好的初步效果，请预先提供格式和受众等详细信息。"),
    (r"(?i)^can’t move this task because it uses claude in chrome\.?$", "无法移动此任务，因为它使用了 Chrome 中的 Claude。"),
    (r"(?i)^confirm that your connector meets <link>anthropic’s directory policies</link>\.?\s*all items are required\.?$", "确认您的连接器符合 <link>Anthropic 目录政策</link>。所有项目均为必填项。"),
]
