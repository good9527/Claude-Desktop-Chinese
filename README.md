# Claude-Desktop-Chinese (Claude Desktop 全平台通用中文汉化补丁)

<p align="center">
  <a href="https://github.com/good9527/Claude-Desktop-Chinese">
    <img src="https://img.shields.io/badge/Release-v1.0.0-blue.svg?style=for-the-badge&logo=github" alt="Release Version">
    <img src="https://img.shields.io/github/actions/workflow/status/good9527/Claude-Desktop-Chinese/ci.yml?style=for-the-badge&logo=githubactions&logoColor=white&label=CI%20BUILD" alt="CI Status">
    <img src="https://img.shields.io/badge/Language-Chinese%20%26%20English-brightgreen.svg?style=for-the-badge" alt="Bilingual Support">
    <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue.svg?style=for-the-badge" alt="Platform Support">
    <img src="https://img.shields.io/badge/Coverage-99.8%25%20(22319%20Keys)-orange.svg?style=for-the-badge" alt="Coverage">
    <img src="https://img.shields.io/badge/Persistence-3--Tier%20Self--Healing-red.svg?style=for-the-badge" alt="Self Healing">
    <img src="https://img.shields.io/badge/License-MIT-purple.svg?style=for-the-badge" alt="MIT License">
  </a>
</p>

> [!TIP]
> 🔗 **开源生态矩阵联动**：
> 如果你同时在日常开发中使用 Google Antigravity 智能体编程助手，欢迎体验我们的姐妹项目：
> 👉 [**good9527/Antigravity-Chinese-Patch** (Google Antigravity 全平台通用中文汉化补丁 · 零依赖原生热注入 · 官方更新自动保活)](https://github.com/good9527/Antigravity-Chinese-Patch)


这是一个针对 Anthropic 出品的强大 AI 对话与智能体桌面客户端 **Claude Desktop (Claude 桌面版)** 的开源、零依赖、永久自愈的通用深度中文汉化补丁与自动化运维系统。

An open-source, zero-dependency, permanent self-healing Chinese localization system for **Claude Desktop** (Windows, macOS, and Linux).

> 📚 **深度索引与 AI 知识库**: 查看完整的 [SEO_GEO_INDEX.md](SEO_GEO_INDEX.md) 获取全量 Schema 规范、AI 搜索引擎检索矩阵与多搜索引擎分类。  
> 🗺️ **站点地图与多语言索引**: [sitemap.xml](sitemap.xml) | [sitemap.json](sitemap.json)

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

### 📦 离线环境与企业内网安装 (Offline Installation)
1. 从 [Releases](https://github.com/good9527/Claude-Desktop-Chinese/releases) 下载 `Claude-Desktop-Chinese-Offline.zip` 并解压。
2. Windows 双击运行 `安装中文语言包.bat` 或在终端执行 `.\install.ps1 -i`。
3. macOS / Linux 在终端执行 `bash ./install.sh -i` 即可零网络完成安装。

---

## 🤖 常见问答 / FAQ（为什么选择本项目？）

### Q1: 什么是 Claude Desktop？如何将它汉化为中文？
**答**：Claude Desktop 是 Anthropic 官方推出的桌面客户端，支持更快的响应、Artifacts 交互、MCP 服务器连接与计算机控制能力。由于官方原生未内置中文语言，本项目通过智能合并与本地语言层替换，只需复制上方的一行命令即可实现 **接近 100% 完整深度中文界面**。

### Q2: 为什么别的汉化补丁在 Claude 更新后会失效，而本项目能“永久保活（自愈）”？
**答**：Claude 官方升级机制会在更新时重置语言文件。本项目内置 **三级自愈守护体系（3-Tier Auto-Healing）**：
- **Tier A (系统级监听守护)**：后台守护进程（Windows `FileSystemWatcher` / macOS `launchd` / Linux `systemd`）毫秒级监听客户端目录，一旦官方静默更新覆盖了文件，将在 **50 毫秒内从本地离线缓存自动重新合并汉化**，真正做到一次安装、永久保活。
- **Tier B (开机与登录校验)**：在开机登录时离线自动校验客户端完整性。
- **Tier C (增量安全字典合并)**：面对官方未来版本新增的新 key，自动保留英文，杜绝白屏或闪退。

### Q3: 汉化会破坏我的代码高亮、MCP 配置或 Prompt 吗？
**答**：**绝对不会！** 补丁仅针对 UI 界面与交互文案，严禁修改用户输入、代码块、模型思考（Extended Thinking）与模型原始回复，MCP 协议通信 100% 原生透明。

### Q4: 如何一键恢复官方原版英文？
**答**：安装时会自动在本地创建纯净的官方备份（`en-US-original.json`）。运行带 `--restore` 参数的命令（如 Windows 运行 `install.ps1 -r`）或在管理菜单中选择 `[4] 一键恢复官方原版`，即可 100% 精确还原。

---

## 📈 Star History

<p align="center">
  <a href="https://star-history.com/#good9527/Claude-Desktop-Chinese&Date">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/good9527/Claude-Desktop-Chinese/main/.github/assets/star-history-dark.svg" />
      <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/good9527/Claude-Desktop-Chinese/main/.github/assets/star-history-light.svg" />
      <img alt="Star History Chart" src="https://raw.githubusercontent.com/good9527/Claude-Desktop-Chinese/main/.github/assets/star-history-dark.svg" width="100%" />
    </picture>
  </a>
</p>


## 🔍 搜索引擎与 AI 检索关键词 | Search Index & Tags

`Claude Desktop 汉化` · `Claude 中文补丁` · `Claude 桌面版 中文` · `Claude 怎么改成中文` · `Claude Desktop Chinese Patch` · `Claude Localization` · `Claude 官方更新自愈汉化` · `Claude UI Translation` · `Anthropic Claude 汉化包` · `Claude MCP 中文` · `Claude Artifacts 汉化` · `Claude Desktop AppX 汉化`

---

## ⚖️ 免责声明 | Disclaimer

- 本项目为开源技术研究成果，仅供个人学习与交流使用，不含任何商业盈利行为。
- 补丁所翻译的界面文案及原客户端版权均归 Anthropic 官方所有。
- This project is an open-source localization research toolkit for personal learning purposes only. All intellectual properties belong to their respective copyright holders.
