# Claude-Desktop-Chinese (Claude Desktop 全平台通用中文汉化补丁)

<p align="center">
  <a href="https://github.com/good9527/Claude-Desktop-Chinese">
    <img src="https://img.shields.io/badge/Language-Chinese%20%26%20English-brightgreen.svg?style=for-the-badge" alt="Bilingual Support">
    <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue.svg?style=for-the-badge" alt="Platform Support">
    <img src="https://img.shields.io/badge/Coverage-99.8%25%20(20000%2B%20Keys)-orange.svg?style=for-the-badge" alt="Coverage">
    <img src="https://img.shields.io/badge/Persistence-3--Tier%20Self--Healing-red.svg?style=for-the-badge" alt="Self Healing">
    <img src="https://img.shields.io/badge/License-MIT-purple.svg?style=for-the-badge" alt="MIT License">
  </a>
</p>

这是一个针对 Anthropic 出品的强大 AI 对话与智能体桌面客户端 **Claude Desktop (Claude 桌面版)** 的开源、零依赖、永久自愈的通用中文汉化补丁系统。

This is an open-source, zero-dependency, permanent self-healing Chinese localization patch for **Claude Desktop** (Windows, macOS, and Linux).

---

## ⚡ 极速一键安装 | Quick 1-Click Install

### 🪟 Windows (PowerShell 终端直接运行)
```powershell
iwr -useb https://fastly.jsdelivr.net/gh/good9527/Claude-Desktop-Chinese@main/install.ps1 | iex
```

### 🍎 macOS & 🐧 Linux (终端直接运行)
```bash
curl -fsSL https://fastly.jsdelivr.net/gh/good9527/Claude-Desktop-Chinese@main/install.sh | bash
```

---

## 🤖 常见问答 / FAQ（为什么选择本项目？）

### Q1: 什么是 Claude Desktop？如何将它汉化为中文？
**答**：Claude Desktop 是 Anthropic 官方推出的桌面客户端，支持更快的响应、Artifacts 交互、MCP 服务器连接与计算机控制能力。由于官方原生未内置中文语言，本项目通过智能合并与本地语言层替换，只需复制上方的一行命令即可实现 **接近 100% 完整深度中文界面**。

### Q2: 为什么别的汉化补丁在 Claude 更新后会失效，而本项目能“永久保活（自愈）”？
**答**：Claude 官方升级机制会在更新时重置语言文件。本项目内置 **三级自愈守护体系（Auto-Healing Daemon）**：
- 后台守护进程（Windows FileSystemWatcher / macOS launchd）毫秒级监听客户端目录，一旦官方静默更新覆盖了文件，将在 **50 毫秒内从本地离线缓存自动重新合并汉化**，真正做到一次安装、永久保活。

### Q3: 汉化会破坏我的代码高亮、MCP 配置或 Prompt 吗？
**答**：**绝对不会！** 补丁仅针对 UI 界面与交互文案，严禁修改用户输入、代码块与模型原始回复。

### Q4: 如何一键恢复官方原版英文？
**答**：安装时会自动在本地创建纯净的官方备份（`en-US-original.json`）。运行带 `--restore` 参数的命令或在管理菜单中选择 `[4] 一键恢复官方原版`，即可 100% 精确还原。

---

## 🌟 核心特性 | Features

### 🇨🇳 20,000+ 词条全量覆盖 (99.8% Coverage)
- **最新官方版本同步**：完整覆盖 Claude Desktop 最新版的 19,913+ 核心词条（包含 Artifacts v2、MCP Servers 连接器、计算机控制 Computer Use、知识库管理与多模型切换等）。
- **智能合并兼容新版本**：采用增量合并算法，当官方版本新增 key 时，自动保留新 key 英文而不会导致界面崩溃。

### ⚡ 零依赖极速注入
- **Windows 免装 Python / Node.js**：直接调用系统底层 PowerShell 与 .NET 引擎，50 毫秒完成热补丁。
- **自动处理管理员 UAC 提权**：自动适配 Microsoft Store（WindowsApps）权限控制。

---

## 🎛️ 本地控制台管理面板 | Interactive Console Menu

Windows 用户可以直接双击仓库中的 `安装中文语言包.bat` 或运行 `patch_claude.ps1`：

```text
======================================================================
          Claude Desktop 中文汉化管理面板 (Elite Toolkit)
          永久自愈 · 零依赖原生注入 · 20000+ 词条全量覆盖
======================================================================

  [1] 一键安装 / 更新中文语言包 (Install Patch)
  [2] 环境与健康状态诊断 (Health Diagnostics)
  [3] 开启 / 关闭后台自动守护 (Auto-Healing Daemon)
  [4] 一键恢复官方原版英文 (One-Click Rollback)
  [5] 退出控制台 (Exit)

======================================================================
请输入选项 [1-5]:
```

---

## ⚙️ CLI 命令行参数 | CLI Flags

| 参数 / Flag | 缩写 | 说明 / Description |
|---|---|---|
| `--install` | `-i` | 执行一键注入安装，创建备份并激活自愈守护 |
| `--uninstall` | `-u` | 还原官方原版备份，清理离线缓存并注销守护服务 |
| `--check` | `-c` | 执行环境与健康状态诊断 |
| `--restore` | `-r` | 一键还原官方原版英文 |
| `--daemon <enable\|disable\|status>` | - | 配置后台自愈守护状态 |
| `--quiet` / `--silent` | `-q` | 静默模式，无控制台交互输出 |
| `--json` | - | 输出标准 JSON 格式诊断数据 |

---

## 🌐 多源 CDN 瀑布流加速 | Multi-CDN Waterfall Acceleration

国内与海外用户均可享受极速下载：
`[1. jsDelivr Fastly CDN]` → `[2. cdnjs Cloudflare CDN]` → `[3. Ghfast 镜像源]` → `[4. GitHub 官方源]`

---

## 📈 Star History

<p align="center">
  <a href="https://star-history.com/#good9527/Claude-Desktop-Chinese&Date">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=good9527/Claude-Desktop-Chinese&type=Date&theme=dark" />
      <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=good9527/Claude-Desktop-Chinese&type=Date" />
      <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=good9527/Claude-Desktop-Chinese&type=Date" width="100%" />
    </picture>
  </a>
</p>

---

## 🔍 搜索引擎与 AI 检索关键词 | Search Index & Tags

`Claude Desktop 汉化` · `Claude 中文补丁` · `Claude 桌面版 中文` · `Claude 怎么改成中文` · `Claude Desktop Chinese Patch` · `Claude Localization` · `Claude 官方更新自愈汉化` · `Claude UI Translation` · `Anthropic Claude 汉化包`

---

## ⚖️ 免责声明 | Disclaimer

- 本项目为开源技术研究成果，仅供个人学习与交流使用，不含任何商业盈利行为。
- 补丁所翻译的界面文案及原客户端版权均归 Anthropic 官方所有。
- This project is an open-source localization research toolkit for personal learning purposes only. All intellectual properties belong to their respective copyright holders.
