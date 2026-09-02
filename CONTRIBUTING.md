# 开源贡献指南 | Contributing Guide

感谢你对 **Claude-Desktop-Chinese** 的关注与支持！我们非常欢迎社区开发者提交翻译润色、新功能适配以及代码优化。

---

## 🛠️ 如何贡献翻译词条

1. **查找词典文件**：
   - 核心词典文件位于 `dist/zh-CN.json`。
2. **翻译规范**：
   - 保证符合开发者通用术语习惯（如：`Repository` -> `仓库`，`Commit` -> `提交`，`Workspace` -> `工作区`）。
   - 保留所有占位符与变量插值格式（如 `{name}`, `{n, plural, ...}`, `<link>...</link>`）。
   - 严禁破坏纯 UTF-8 编码，不要引入 BOM 头。
3. **本地自动化测试**：
   - 在提交 Pull Request 前，请务必运行测试套件：
     ```bash
     python tests/test_runner.py
     ```
   - 确保所有测试均通过（100% Passed）。

---

## 🐛 提交 Issue 规范

- 请使用 GitHub 提供的预设模版提交 Issue：
  - **界面未翻译反馈**：请提供原英文文案、所处界面位置及截图。
  - **运行异常排查**：请附带完整的终端日志输出与操作系统版本。

---

## 📜 代码准则

- 保持脚本的**零外部依赖（Zero External Dependency）**特性。
- 保证 Windows / macOS / Linux 全平台的兼容性。
