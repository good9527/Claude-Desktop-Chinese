---
name: win-automation
description: Control Windows applications via MCP - screenshots, UI automation, keyboard/mouse input
---

# Windows Automation MCP Server

Windows 桌面自动化 MCP 服务器，提供截图、UI 自动化、键盘鼠标输入等功能。

## 功能列表

| 工具 | 功能 |
|------|------|
| `list_apps` | 列出正在运行的应用及其窗口 |
| `list_windows` | 列出所有可见窗口 |
| `get_window` | 通过 HWND 获取窗口信息 |
| `launch_app` | 启动应用 |
| `get_window_state` | 截图 + 无障碍树（带元素索引） |
| `click` | 坐标点击或元素索引点击 |
| `type_text` | 输入文本（支持中文） |
| `press_key` | 按键/快捷键 |
| `scroll` | 滚动 |
| `drag` | 拖拽 |
| `set_value` | 设置可编辑元素的值 |
| `perform_secondary_action` | 执行元素辅助操作 |
| `activate_window` | 将窗口带到前台 |

## 使用流程

### 1. 发现应用
```
list_apps() -> 获取所有运行中的应用和窗口
```

### 2. 获取窗口状态
```
get_window_state(hwnd=12345, include_screenshot=True, include_accessibility=True)
```
- 返回截图（PNG）和无障碍树
- 元素索引从 0 开始，深度优先遍历
- 索引是临时的，每次 get_window_state 会刷新

### 3. 交互操作
```
click(hwnd=12345, x=100, y=200)           # 坐标点击
click(hwnd=12345, index=5)                  # 元素点击
type_text(hwnd=12345, text="你好世界")       # 输入中文
press_key(hwnd=12345, keys="Control_L+c")   # 复制
scroll(hwnd=12345, x=500, y=300, scroll_y=-3)  # 向上滚动
```

## 坐标系统

- 所有坐标相对于窗口客户区（不含标题栏和边框）
- (0, 0) 是窗口客户区左上角
- 截图中的坐标与窗口坐标一致

## 元素索引

- 索引是临时的，仅在最近一次 `get_window_state` 调用后有效
- 如果操作失败提示索引无效，重新调用 `get_window_state` 刷新
- 某些应用（Electron、游戏）可能无障碍树为空，此时使用坐标操作

## 快捷键格式

使用 X11 keysym 风格名称，用 `+` 连接：
- `Control_L+c` → Ctrl+C
- `Control_L+Shift_L+s` → Ctrl+Shift+S
- `Alt_L+F4` → Alt+F4
- `Return` → 回车
- `Escape` → ESC
- `space` → 空格

## 中文输入

`type_text` 通过剪贴板粘贴方式输入，完全支持 Unicode/中文字符。

## 截图

- 使用 PrintWindow API，支持被遮挡窗口
- 默认最大宽度 1280 像素，可通过 `max_screenshot_width` 参数调整
- 最小化窗口需要先 `activate_window` 恢复

## 错误处理

- 窗口不存在：返回 "Window {hwnd} no longer exists"
- 元素索引过期：返回 "Element index N not found"
- 权限不足：某些系统窗口可能无法操作

## 安装和配置

### 依赖
```
pip install mcp comtypes pillow pyautogui
```

### Claude Code 配置
在 `.claude/settings.local.json` 中添加：
```json
{
  "mcpServers": {
    "win-automation": {
      "command": "python",
      "args": ["path/to/win-automation-mcp/server.py"]
    }
  }
}
```

### 测试
```bash
python server.py  # 应该无输出（等待 stdio 输入）
```
