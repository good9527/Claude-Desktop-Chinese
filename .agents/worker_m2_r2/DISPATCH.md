## 2026-09-02T07:40:14Z
Task: Milestone M2 — High-Precision Translation Quality & Completeness Audit (22,000+ keys) & Validator Fixes
Assigned to: worker_m2_r2
Working Directory: C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese\.agents\worker_m2_r2
Parent Orchestrator: 2a82dcf2-812a-421c-8fdc-d5ae3c99eb62

Objectives:
1. Complete translation of remaining untranslated English keys in dist/zh-CN.json and zh-CN-ion.json (22,319 keys).
   - Natural, idiomatic Simplified Chinese for general UI dialogs, settings, errors, project UI, ICU plural/select formats.
   - 100% exact parity between dist/zh-CN.json and zh-CN-ion.json.
   - Achieve >= 98.5% Chinese coverage ratio across all keys.
   - Zero unescaped characters, zero mojibake, zero \ufffd, zero unbalanced braces, zero corrupted template parameters.
2. Harmonize AI Developer Terminology across all 22,319 keys:
   - Artifacts -> 制品 (harmonize all 135+ instances consistently).
   - MCP / Model Context Protocol -> 模型上下文协议 (MCP) / MCP 服务器 / MCP 工具.
   - Computer Use -> 计算机使用.
   - Token -> Distinguish Auth Token (访问令牌 / API 密钥) vs LLM Token (Token).
   - Context Window -> 上下文窗口.
   - Extended Thinking / Thinking Mode -> 扩展思考 / 深度思考.
   - Connectors -> 连接器.
3. Fix all 4 defects in scripts/validate.py:
   - Set MIN_CHINESE_RATIO = 0.90 (ensure updated dictionary passes).
   - Fix registry path false positive: regex [A-Za-z]:\ should not trigger on PowerShell registry PSDrives (HKCU:\, HKLM:\).
   - Fix git ls-files without -c core.quotepath=false causing octal-quoted paths for 安装中文语言包.bat.
   - Make PowerShell syntax check portable across OS platforms (pwsh/powershell if available, gracefully skip when not available).
4. Run python scripts/validate.py and python tests/test_runner.py --tier all to ensure exit code 0.
