# Claude Desktop Chinese Patch / Claude 桌面版中文汉化补丁

> 一行命令，让 Windows 版 Claude Desktop 显示简体中文界面。

[![Validate](https://github.com/good9527/Claude-Desktop-Chinese/actions/workflows/validate.yml/badge.svg)](https://github.com/good9527/Claude-Desktop-Chinese/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Windows](https://img.shields.io/badge/Platform-Windows%2010%2F11-blue.svg)]()
[![Coverage](https://img.shields.io/badge/Coverage-99.6%25-green.svg)]()

本项目为 Windows 上的 Claude Desktop 提供简体中文界面补丁。脚本会读取 Claude 自带的英文语言文件 `en-US.json`，将已翻译的文本替换为中文，并在安装前自动备份原始文件。

> 注意：这不是官方语言切换功能。Claude 设置里仍会显示 `English (United States)`，但界面文本会显示为中文。

## 特性

- 支持 Microsoft Store 安装的 Claude Desktop
- 支持一行命令在线安装，也支持下载 ZIP 后离线安装
- 自动请求管理员权限并关闭正在运行的 Claude
- 首次安装自动备份原始 `en-US.json`
- 可重复安装，适合 Claude 更新后重新应用补丁
- 提供卸载脚本，可恢复到原始英文界面
- 提供验证脚本和 GitHub Actions，便于开源协作维护

## 系统要求

- Windows 10 或 Windows 11
- 从 [Microsoft Store](https://apps.microsoft.com/detail/claude/) 安装的 Claude Desktop
- 管理员权限

## 安装

### 方法一：一行命令安装

打开 Windows Terminal 或 PowerShell，粘贴以下命令并回车：

```powershell
iwr -useb https://raw.githubusercontent.com/good9527/Claude-Desktop-Chinese/main/install.ps1 | iex
```

如果当前窗口不是管理员权限，脚本会自动弹出 UAC 请求并在新的管理员窗口中继续执行。

### 方法二：下载后安装

1. 点击 GitHub 页面上的 `Code` -> `Download ZIP`
2. 解压到任意目录
3. 双击 `install.bat`
4. 按提示允许管理员权限

下载方式会优先使用本地 `dist/zh-CN.json`，因此可以离线安装。

## 卸载

### 一行命令卸载

```powershell
iwr -useb https://raw.githubusercontent.com/good9527/Claude-Desktop-Chinese/main/uninstall.ps1 | iex
```

### 下载后卸载

双击解压目录中的 `uninstall.bat`。

卸载脚本会从 `%LOCALAPPDATA%\Claude-Chinese-Patch\en-US-original.json` 恢复原始英文文件。备份文件会保留，方便后续再次安装或排查问题。

## Claude 更新后怎么办

Claude 自动更新后可能会恢复官方语言文件，导致中文界面失效。重新运行安装命令即可再次应用补丁。

如果 Claude 新版本增加了新的文本 key，未翻译的少量文本会保留英文；后续更新 `dist/zh-CN.json` 后即可覆盖。

## 文件说明

| 文件 | 作用 |
| --- | --- |
| `dist/zh-CN.json` | 发布用中文翻译字典（15,170 条，覆盖约 99.6%） |
| `zh-CN-ion.json` | 翻译源文件，内容应与 `dist/zh-CN.json` 保持一致 |
| `install.ps1` | 主安装脚本，支持在线和本地字典 |
| `install.bat` | 双击安装入口 |
| `uninstall.ps1` | 卸载还原脚本 |
| `uninstall.bat` | 双击卸载入口 |
| `scripts/validate.py` | 项目质量校验脚本 |
| `.github/workflows/validate.yml` | GitHub Actions 校验流程 |

## 工作原理

1. 自动检测 Claude Desktop 的安装目录
2. 关闭正在运行的 Claude 进程
3. 首次安装时备份原始 `en-US.json`
4. 读取 Claude 当前版本的英文 key
5. 用 `dist/zh-CN.json` 中存在的翻译替换对应 value
6. 对未翻译或新版本新增的 key 保留英文原文
7. 写回并重新解析 JSON 做基础校验
8. 重启 Claude

这种合并方式比直接覆盖整份语言文件更兼容新版本：当 Claude 新增 key 时，脚本不会删除它们。

## 常见问题

### 安装后语言设置显示什么？

仍然显示 `English (United States)`，但实际界面文本会显示中文。

### 安装失败怎么办？

- 确认 Claude Desktop 已从 Microsoft Store 安装
- 确认允许了管理员权限
- 确认 Claude 已完全关闭
- 在线安装失败时，可以下载 ZIP 后双击 `install.bat` 离线安装

### 卸载后还是中文怎么办？

重新运行卸载脚本并确认允许管理员权限。如果备份文件丢失，可以从 Microsoft Store 重新安装 Claude。

### 这个项目安全吗？

- 项目只发布翻译文件和安装脚本，不包含 Anthropic 的程序代码
- 安装前会备份原始语言文件
- 卸载脚本会恢复备份
- 代码开源，可自行审查

## 维护与校验

开发者可以在提交前运行：

```powershell
python scripts/validate.py
```

校验内容包括：

- 翻译 JSON 是否可解析
- `dist/zh-CN.json` 是否与 `zh-CN-ion.json` 一致
- 翻译覆盖率是否保持在合理范围
- README 中声明的翻译数量是否与实际文件一致
- 安装/卸载脚本是否能被 PowerShell 解析
- 仓库中是否出现明显的密钥格式

## 法律声明

本项目仅发布社区维护的中文翻译内容和安装脚本，不包含 Anthropic 或 Claude Desktop 的版权程序代码。本项目与 Anthropic 公司无关。

## Credits

- 翻译：Claude AI 辅助生成和人工整理
- 覆盖率：15,153 / 15,209 个参考 key（约 99.6%）
- 协议：MIT
