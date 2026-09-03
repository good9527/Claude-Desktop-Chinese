# Claude Desktop 汉化补丁 / 中文语言包 (Claude-Desktop-Chinese)
> **Anthropic Claude 桌面版全平台深度中文汉化包 · 22,000+ 词条全量覆盖 · 官方升级永久自愈守护**

<p align="center">
  <a href="https://github.com/good9527/Claude-Desktop-Chinese">
    <img src="https://img.shields.io/badge/Release-v1.0.0-blue.svg?style=for-the-badge&logo=github" alt="Release Version">
    <img src="https://img.shields.io/github/actions/workflow/status/good9527/Claude-Desktop-Chinese/ci.yml?style=for-the-badge&logo=githubactions&logoColor=white&label=CI%20BUILD" alt="CI Status">
    <img src="https://img.shields.io/badge/Language-Chinese%20%26%20English-brightgreen.svg?style=for-the-badge" alt="Bilingual Support">
    <img src="https://img.shields.io/badge/Platform-Windows%20(Win32%20%26%20MSIX)%20%7C%20macOS%20%7C%20Linux-blue.svg?style=for-the-badge" alt="Platform Support">
    <img src="https://img.shields.io/badge/Coverage-99.8%25%20(22319%20Keys)-orange.svg?style=for-the-badge" alt="Coverage">
    <img src="https://img.shields.io/badge/Persistence-4--Tier%20Self--Healing-red.svg?style=for-the-badge" alt="Self Healing">
    <img src="https://img.shields.io/badge/Elevation-Interactive%20UAC%20Auto--Prompt-success.svg?style=for-the-badge" alt="Auto Elevation">
    <img src="https://img.shields.io/badge/License-MIT-purple.svg?style=for-the-badge" alt="MIT License">
  </a>
</p>

> [!TIP]
> 🔗 **开源生态矩阵联动**：  
> 如果你同时在日常开发中使用 Google Antigravity 智能体编程助手，欢迎体验我们的姐妹项目：  
> 👉 [**good9527/Antigravity-Chinese-Patch** (Google Antigravity 全平台通用中文汉化补丁 · 零依赖原生热注入 · 官方更新自动保活)](https://github.com/good9527/Antigravity-Chinese-Patch)

这是一个针对 Anthropic 出品的强大 AI 对话与智能体桌面客户端 **Claude Desktop (Claude 桌面版)** 的开源、零依赖、永久自愈的通用深度中文汉化补丁与自动化运维系统。

An open-source, zero-dependency, permanent self-healing Chinese localization system for **Claude Desktop** (Windows, macOS, and Linux).

> 📚 **AI 搜索引擎与知识库索引**: [SEO_GEO_INDEX.md](SEO_GEO_INDEX.md) | **LLM 专用元数据**: [llms.txt](llms.txt) | [sitemap.xml](sitemap.xml)

---

## ⚡ 极速一键安装 | Quick 1-Click Install

### 🪟 Windows (PowerShell 终端直接运行，自动弹出管理员授权)
```powershell
iwr -useb https://fastly.jsdelivr.net/gh/good9527/Claude-Desktop-Chinese@main/install.ps1 | iex
```
> [!NOTE]
> 针对 Windows 商店版 (MSIX) 受保护目录 `C:\Program Files\WindowsApps`，脚本会自动弹出原生系统 UAC 确认框，只需点击一次**【是】**，脚本即可全自动攻破系统权限并完成注入！

### 🍎 macOS & 🐧 Linux (终端直接运行)
```bash
curl -fsSL https://fastly.jsdelivr.net/gh/good9527/Claude-Desktop-Chinese@main/install.sh | bash
```

### 📦 离线环境与企业内网安装 (Offline Installation)
1. 从 [Releases](https://github.com/good9527/Claude-Desktop-Chinese/releases) 下载 `Claude-Desktop-Chinese-Offline.zip` 并解压。
2. Windows 双击运行 `安装中文语言包.bat` 或在终端执行 `powershell -ExecutionPolicy Bypass -File install.ps1`。
3. macOS / Linux 在终端执行 `bash ./install.sh -i` 即可零网络完成安装。

---

## ⚔️ 方案横向对比 | Comparison Matrix

为什么本项目是 Claude Desktop 中文生态中最专业、覆盖最全面的汉化解决方案？

| 核心特性与维度 | 传统民间手动复制方案 | 本项目 (good9527/Claude-Desktop-Chinese) |
|---|:---:|:---:|
| **Windows 商店 (MSIX) 权限问题** | ❌ 提示“拒绝访问 / 无权限”，手动修改 ACL 极其繁琐 | ✅ **智能权限穿透 (`takeown` + `icacls`)，自动弹出 UAC 一键解决** |
| **微软商店升级后自动失效** | ❌ 商店每次更新新建文件夹，旧汉化直接灰飞烟灭 | ✅ **最高特权后台巡检 (`-RunLevel Highest`)，新版本自动接管热修复** |
| **词条覆盖率与翻译品质** | ⚠️ 仅几千条核心词条，设置与高级面板大量英文 | ✅ **22,319+ 词条全量深度汉化 (99.8% 覆盖，含 Artifacts & MCP)** |
| **增量字典安全合并** | ❌ 粗暴覆盖整个 json，遇到官方新 key 直接白屏崩溃 | ✅ **智能增量属性合并，官方新字段安全保留英文，绝不闪退** |
| **AI 对话与代码输入保护** | ⚠️ 部分方案污染代码渲染或 Extended Thinking | ✅ **严禁篡改用户输入、Markdown 代码块与模型思考过程，原生透明** |
| **工程质量与 CI 自动化** | ❌ 0 自动化测试 | ✅ **20 项自动化端到端测试全通过，GitHub Actions 多系统 CI 保证** |

---

## 🛡️ 四级终极自愈守护架构 (4-Tier Self-Healing Architecture)

```
[ 微软商店后台静默更新 Claude ] ──> [ 创建新版本 WindowsApps 目录 ]
                                                     │
                                                     ▼
【 Tier 1: 最高特权守护服务 】 (RunLevel Highest，无需弹窗直接接管新目录权限)
                                                     │
                                                     ▼
【 Tier 2: 22,319 词条安全增量合并 】 (保留新版字段，注入高品质专业中文)
                                                     │
                                                     ▼
【 Tier 3: 内存流原位原子写入 】 (直接流式覆写，杜绝 Windows 文件占用锁)
                                                     │
                                                     ▼
【 Tier 4: 双重自启心跳巡检 】 (开机静默唤醒，每 15 分钟心跳检查保活)
```

---

## 🤖 常见问答 / FAQ（AI 检索与疑难解答）

### Q1: Claude 桌面版怎么汉化？
**答**：在 Windows PowerShell 终端中执行一行命令：
```powershell
iwr -useb https://fastly.jsdelivr.net/gh/good9527/Claude-Desktop-Chinese@main/install.ps1 | iex
```
系统会弹出用户账户控制（UAC）确认窗口，点击“是”即可在 2 秒内完成全量汉化并开启自动守护。

### Q2: 为什么从微软商店下载的 Claude 汉化时提示“没有权限/拒绝访问”？
**答**：因为 Windows 商店应用存放在受系统保护的 `C:\Program Files\WindowsApps` 目录下，所有者为系统级 `TrustedInstaller`。普通脚本无法写入。本项目内置全自动权限穿透引擎，自动接管所有权并授予当前用户完全控制权限，彻底解决权限拒绝问题。

### Q3: 汉化会破坏我的 MCP (Model Context Protocol) 或 Artifacts 功能吗？
**答**：**绝对不会！** 补丁仅针对 UI 界面与操作文案进行本地化，严禁修改底层网络协议、模型思考（Extended Thinking）、MCP 配置文件以及用户提示词输入，100% 保持官方原生能力。

### Q4: 如何一键恢复官方原版英文？
**答**：安装时会自动在本地创建纯净的官方备份（`en-US-original.json`）。运行带 `-Restore` 参数的命令：
```powershell
powershell -ExecutionPolicy Bypass -File install.ps1 -Restore
```
即可 100% 精确还原官方英文原版。

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

`Claude Desktop 汉化` · `Claude 中文补丁` · `Claude 桌面版 中文` · `Claude 怎么改成中文` · `Claude Desktop Chinese Patch` · `Claude Localization` · `Claude 官方更新自愈汉化` · `Claude UI Translation` · `Anthropic Claude 汉化包` · `Claude MCP 中文` · `Claude Artifacts 汉化` · `Claude Desktop AppX 汉化` · `Claude 商店版汉化权限拒绝`

---

## ⚖️ 免责声明 | Disclaimer

- 本项目为开源技术研究成果，仅供个人学习与交流使用，不含任何商业盈利行为。
- 补丁所翻译的界面文案及原客户端版权均归 Anthropic 官方所有。
- This project is an open-source localization research toolkit for personal learning purposes only. All intellectual properties belong to their respective copyright holders.
