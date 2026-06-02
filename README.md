# Claude Desktop Chinese Patch / Claude 桌面版中文汉化补丁

> **一行命令，让 Claude 桌面版变成中文界面。**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Windows](https://img.shields.io/badge/Platform-Windows%2010%2F11-blue.svg)]()
[![Coverage](https://img.shields.io/badge/Coverage-99.6%25-green.svg)]()

**Claude 桌面版中文语言包** | **Claude Desktop Chinese Patch** | **Claude 汉化补丁** | **Claude 中文界面** | **Claude Language Patch**

Windows 上的 Claude 桌面版本身不支持中文。本补丁通过替换内置翻译文件，将整个界面（聊天窗口、设置面板、菜单栏）汉化为简体中文，覆盖 15,000+ 条文本，覆盖率 99.6%。

> ⚠️ 本补丁会修改 Claude 的英文翻译文件内容（en-US.json），将其中的英文替换为中文。语言设置中仍然显示 "English (United States)"，但实际显示的是中文。这不是真正的语言切换，而是一种"偷梁换柱"的实现方式。

---

## 效果预览

安装后 Claude 桌面版界面：聊天对话、设置菜单、标题栏、按钮等全部显示中文。

---

## 系统要求

- **操作系统：** Windows 10 或 Windows 11
- **Claude 版本：** 从 [Microsoft Store](https://apps.microsoft.com/detail/claude/) 安装的 Claude Desktop
- **权限：** 需要管理员权限（修改系统保护目录需要）

---

## 安装方法（二选一）

### 方法一：一行命令安装（推荐）

1. **右键** Windows 开始菜单 → 选择 **"终端(管理员)"** 或 **"Windows PowerShell(管理员)"**
2. 粘贴以下命令，按回车：

```powershell
iwr -useb https://raw.githubusercontent.com/good9527/Claude-Desktop-Chinese/main/install.ps1 | iex
```

3. 等待自动完成，Claude 会自动重启并显示中文

### 方法二：下载安装包

1. 点击页面上方绿色 **Code** 按钮 → **Download ZIP**
2. 解压 ZIP 文件到任意位置
3. 双击 `install.bat`
4. 弹出管理员权限提示时点击 **"是"**
5. 等待自动完成

---

## 卸载还原（恢复英文）

### 一行命令卸载

1. **右键** 开始菜单 → **"终端(管理员)"**
2. 粘贴以下命令，按回车：

```powershell
iwr -useb https://raw.githubusercontent.com/good9527/Claude-Desktop-Chinese/main/uninstall.ps1 | iex
```

### 或双击卸载

双击解压目录中的 `uninstall.bat` 即可。

---

## 安装流程详解

以下是安装脚本的完整执行流程：

### 第 1 步：检测 Claude 安装位置
脚本通过 Windows 的 `Get-AppxPackage` 命令自动查找 Claude 的安装路径。无论你安装的是哪个版本（1.9xxx、2.0xxx 等），都能自动识别，无需手动指定路径。

### 第 2 步：加载中文字典
脚本从 GitHub 下载（在线模式）或从本地读取（离线模式）中文翻译字典文件 `zh-CN.json`，包含 15,170 条翻译。

### 第 3 步：关闭 Claude
自动关闭正在运行的 Claude 进程，以便修改翻译文件。

### 第 4 步：备份 + 合并 + 写入
- **备份：** 首次安装时，将原始英文 `en-US.json` 备份到 `%LOCALAPPDATA%\Claude-Chinese-Patch\en-US-original.json`（后续卸载时使用）
- **合并：** 读取原始英文文件的 15,209 个 key，将其中 15,153 个替换为中文翻译，剩余 56 个保留英文
- **写入：** 将合并后的文件写回 Claude 的翻译目录。由于 WindowsApps 目录有系统保护，使用 .NET 的 `IO.File.Copy` 方法绕过限制

### 第 5 步：启动 Claude
自动重启 Claude，界面将显示中文。关闭安装脚本窗口不会影响 Claude。

---

## 卸载流程详解

### 第 1 步：检测 Claude 安装位置
同安装流程。

### 第 2 步：关闭 Claude
自动关闭正在运行的 Claude 进程。

### 第 3 步：还原备份
从 `%LOCALAPPDATA%\Claude-Chinese-Patch\en-US-original.json` 读取原始英文文件，写回 Claude 的翻译目录。

### 第 4 步：启动 Claude
自动重启 Claude，界面恢复英文。

---

## Claude 更新后怎么办

Claude 会自动更新。更新后翻译文件会被还原为英文，补丁失效。

**解决方法：** 重新运行安装命令即可。备份文件不会丢失，可以反复安装。

---

## 文件说明

| 文件 | 作用 |
|------|------|
| `dist/zh-CN.json` | 中文翻译字典（15,170 条，907KB） |
| `install.ps1` | 安装脚本（支持在线和本地两种模式） |
| `install.bat` | 双击安装入口（自动请求管理员权限） |
| `uninstall.ps1` | 卸载脚本 |
| `uninstall.bat` | 双击卸载入口 |
| `LICENSE` | MIT 开源协议 |

---

## 常见问题

### Q: 安装后语言设置显示什么？
仍然显示 "English (United States)"，但实际界面是中文。这是因为我们修改的是英文翻译文件的内容，而不是添加新的语言选项。

### Q: 安装失败怎么办？
- 确保以**管理员身份**运行
- 确保 Claude 已从 Microsoft Store 安装
- 确保网络连接正常（在线模式需要下载翻译文件）

### Q: Claude 更新后中文消失了？
正常现象。重新运行安装命令即可恢复。

### Q: 卸载后中文还在？
确保以管理员身份运行卸载脚本。如果仍然不行，可以重装 Claude。

### Q: 这个补丁安全吗？
- 本项目只包含自研的中文翻译文件，不包含任何 Anthropic 版权代码
- 安装前会自动备份原始文件
- 卸载后完全恢复原状
- 代码开源，可自行审查

---

## 法律声明

本项目仅发布自研的中文翻译内容，不包含任何 Anthropic 版权代码。`zh-CN.json` 文件仅包含翻译键值对（如 `{"key": "中文值"}`），不包含原始英文内容。

本项目与 Anthropic 公司无关，为社区自发的汉化项目。

---

## Credits

- 翻译：Claude AI 辅助生成
- 覆盖率：15,153 / 15,209 字符串（99.6%）
- 协议：MIT
