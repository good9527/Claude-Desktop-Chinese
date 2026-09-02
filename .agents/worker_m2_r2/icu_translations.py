"""ICU MessageFormat translations for Claude Desktop Chinese."""

import re

# Comprehensive translations for the 275 untranslated ICU strings
ICU_EXACT_MAP = {
    "0zCqdBEnn7": "{selectedOption} / {totalOptions}",
    "31se92/223": "{value, plural, one {# 分钟} other {# 分钟}}",
    "lv+bhopVDB": "{count, plural, one {# {singular}} other {# {plural}}}",
    "ujskzPsMKK": "{count, plural, one {{label}} other {# {label}}}",
    "+6j0afrsj0": "未授予麦克风访问权限。请打开“系统设置”，前往“隐私与安全性”，选择“麦克风”，开启 Claude，然后重试。",
    "+JvGFb7mmY": "{used} 个使用中 · {idle} 个空闲{warming, plural, =0 {} one { · # 个预热中} other { · # 个预热中}}",
    "+SmMHRltda": "{period, select, daily {每日支出限额} weekly {每周支出限额} other {每月支出限额}}",
    "+yYWSDG5GS": "您的个人账户信誉良好，但{count, plural, one {您所属的一个组织已被暂停，因为我们发现由 18 岁以下人员使用的迹象。} other {您所属的 # 个组织已被暂停，因为我们发现由 18 岁以下人员使用的迹象。}}请在下方验证您的年龄以恢复访问。",
    "/gSr8QAgYy": "无法将包添加到{count, plural, one {# 个频道} other {# 个频道}}：{names}",
    "/phDxdw6Nl": "您在 {time} 发起的购买正在等待银行卡验证。请在银行应用程序或弹出窗口中完成验证，或稍候。未完成的尝试将在 {minutes, plural, one {# 分钟} other {# 分钟}}后过期。在此之前尝试其他卡将无法解决问题。",
    "01f9Rte4TR": "{count, plural, one {# 个修复} other {# 个修复}}正在进行中",
    "0jit/T4dmU": "Team 计划至少需要 {minimum, plural, one {# 个席位} other {# 个席位}}",
    "1OLmXcxHFj": "您已达到{period, select, daily {每日} weekly {每周} monthly {每月} other {}}支出限额，且额度已用尽。",
    "1UMAVNcQcB": "删除所选项？",
    "1X7s/Os9ie]": "未选择环境。请选择一个环境以启动 Code 会话。",
    "1X7s/Os9ie": "未选择环境。请选择一个环境以启动 Code 会话。",
    "1c+L0xUeGY": "{name} 已在 <places>{count, plural, one {# 处} other {# 处}}</places> 使用",
    "1gFauzEKGq": "所选模型已不再可用。",
    "1hkicTmaLD": "要从{count, plural, one {# 个项目} other {全部 # 个项目}}中移除此群组吗？",
    "1la72oveyT": "· {count, plural, one {# 项待修复} other {# 项待修复}}",
    "2CFYQq+sYg": "“{label}”合并了{count, plural, one {# 个更多系列} other {# 个更多系列}}",
    "3+jLYCsR90": "授予此{principalType, select, account {成员} other {群组}}的部分权限未显示，因为其设置被隐藏或不可用。",
    "31wrs0tjdf": "共享的制品在闲置 {count, plural, one {# 个月} other {# 个月}}后将被删除",
    "33eorYiZ7V": "将允许 Claude 使用此凭据访问{hostCount, plural, one {此主机} other {这些主机}}。",
    "3AehitIt9q]": "页面到达 {seconds, plural, one {# 秒} other {# 秒}}后未触发加载事件。",
    "3AehitIt9q": "页面到达 {seconds, plural, one {# 秒} other {# 秒}}后未触发加载事件。",
    "3aylW6HDWG": "连接容器后方可选择模型。",
    "4AXHifrAWE": "没有与“{query}”匹配的 {plural}",
    "4W1TXf3c2q": "保存 {failedList} 支出{count, plural, one {限额} other {限额}}失败。请重试。",
    "5OLgJ/o1N5": "编辑 {count, plural, one {# 个群组} other {# 个群组}}的设置",
    "5hkF/un5+o": "删除此角色后，<b>{count, plural, one {# 位用户} other {# 位用户}}</b>将没有分配任何自定义角色。他们将无法再访问由自定义角色启用的任何功能。",
    "6REI3LTKk3": "由于异常活动，我们暂停了您的账户{hasEmail, select, yes { ({email})} other {}}。您的聊天记录和数据是安全的，您的团队成员不受影响。",
}
