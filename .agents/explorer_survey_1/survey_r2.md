# R2 Technical Survey & Linguistic Audit Report
**Project:** `Claude-Desktop-Chinese`  
**Working Directory:** `C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese`  
**Investigator:** Explorer 1 (`explorer_survey_1`)  
**Date:** 2026-09-02  
**Requirement Focus:** R2 — High-Precision Translation Quality & Completeness Audit (22,000+ keys)

---

## 1. Executive Summary

A comprehensive linguistic, structural, and technical audit was conducted across the entire translation codebase of `Claude-Desktop-Chinese`. The primary release dictionary (`dist/zh-CN.json`) and source file (`zh-CN-ion.json`) were analyzed key-by-key using automated AST, regex, and encoding inspection tools.

### Core Metrics Summary
| Metric | Value | Status / Assessment |
|---|---|---|
| **Total Translation Keys** | **22,319** | Exact quantification of the 22,000+ keys requirement |
| **Dictionary File Size** | 1,495,397 bytes (~1.43 MB) | Identical between `dist/zh-CN.json` and `zh-CN-ion.json` |
| **Key Hash Format** | 22,189 (99.42%) 10-char Base64 | FormatJS / React-Intl AST hash identifiers |
| **Translated Keys (with CJK)** | **14,959 (67.02%)** | High quality, idiomatic Chinese for existing translations |
| **Untranslated Keys (Pure English)** | **7,332 (32.85%)** | Critical gap: ~4,200 sentences + ~945 ICU format strings |
| **Placeholders & ICU Strings** | 1,010 ICU format strings | 510 translated / 500 untranslated; 0 corrupted braces |
| **Encoding / Mojibake Anomalies** | **0 across all 22,319 keys** | Zero `\ufffd`, zero double UTF-8, zero GBK mojibake |
| **JSON Syntax Validity** | **100% valid JSON** | Flawless parsing via standard JSON decoders |
| **Terminology Consistency** | **Fragmented** | `Artifacts` translated 4 different ways (`制品`, `工件`, `构件`, `产物`) |
| **CI Script (`scripts/validate.py`)** | **FAILING** | Expects `>= 90%` Chinese ratio, actual is `67.02%` |

---

## 2. Translation Architecture & Asset Inventory

The repository contains a full toolchain for chunking, translating, merging, and injecting translation files into the Claude Desktop application runtime.

### File Inventory Table
| File Path | Lines | Size (Bytes) | Category | Description & Role |
|---|---|---|---|---|
| `dist/zh-CN.json` | 22,320 | 1,495,397 | Release Asset | Authoritative distribution dictionary for Claude Desktop |
| `zh-CN-ion.json` | 22,320 | 1,495,397 | Source File | Working dictionary in repository root (bit-for-bit identical to dist) |
| `scripts/validate.py` | 233 | 7,863 | CI Tooling | Validation script checking JSON validity, 90% CJK ratio, paths, secrets |
| `tests/test_runner.py` | 30 | 1,313 | Unit Test | Test suite checking dictionary existence, key count >= 15000, 500-key mojibake |
| `create_hacked_enus.py` | 65 | 2,144 | Local Patch | Merges local Claude `en-US.json` with `zh-CN-ion.json` into `en-US-hacked.json` |
| `split_chunks.py` | 61 | 2,010 | Tooling | Splits `local/en-US.json` into 500-key JSON chunk files in `chunks/` |
| `merge.py` | 66 | 2,170 | Tooling | Merges translated chunk files into `zh-CN-ion.json` |
| `merge2.py` | 113 | 3,782 | Tooling | Merges translated chunks with automated JSON quote repair logic |
| `translate.py` | 147 | 5,455 | Translation | Batch translation using `googletrans` with placeholder masking |
| `translate2.py` | 141 | 5,055 | Translation | Batch translation using `deep_translator` (GoogleTranslator) |
| `translate3.py` | 178 | 6,474 | Translation | Multi-threaded translation using public Google Translate endpoint |
| `install.ps1` | 266 | 11,596 | Installer | Windows PowerShell universal installer with auto-elevation and auto-heal |
| `install.sh` | 54 | 1,892 | Installer | macOS / Linux installer using curl and inline python merge |
| `patch_claude.ps1` | 74 | 2,470 | Admin Script | Windows interactive patching script |
| `watcher/watcher.ps1` | 108 | 4,212 | Auto-Healing | Background daemon monitoring `en-US.json` for silent updates |
| `.github/workflows/validate.yml` | 23 | 400 | CI/CD | GitHub Actions workflow executing `scripts/validate.py` on push/PR |

### Translation Pipeline Dataflow
```
[Claude Desktop Runtime]
   app/resources/ion-dist/i18n/en-US.json (Raw English strings)
                       │
                       ▼
             split_chunks.py (500-key chunks)
                       │
                       ▼
          translate1/2/3.py (Placeholder Protection __PH0__ / PH0X)
                       │
                       ▼
              merge.py / merge2.py (JSON Quote Repair)
                       │
                       ▼
            dist/zh-CN.json (22,319 keys)
                       │
                       ▼
      install.ps1 / install.sh (In-place merge into en-US.json)
```

---

## 3. Quantitative Key Audit & Schema Analysis

### 3.1 Key Identification & Structure
- **Total Keys:** 22,319
- **Key Hash Distribution:**
  - 10-Character Base64 Hashes (e.g., `+/yYn89HLV`, `+09/bm5myh`): **22,189 (99.42%)**
  - Variable-Length Base64 Hashes (e.g., `31se92/223`, `5RasbgfW2t`): **105 (0.47%)**
  - Dotted Path Keys (e.g., `app.settings.*`): **25 (0.11%)**
  - Natural English Keys: **0 (0.00%)**
- **Collision / Duplicate Status:** 0 duplicate keys (100% unique hash keys).

### 3.2 Value Content Distribution
| Value Type | Key Count | Percentage | Characteristics |
|---|---|---|---|
| **Pure Chinese Text** | 9,699 | 43.46% | Fully localized Chinese strings without Latin characters |
| **Chinese + Latin Mixed** | 5,260 | 23.57% | Chinese sentences containing technical terms, brand names, or placeholders |
| **Pure English / Latin** | 7,332 | 32.85% | Untranslated strings or English technical terms |
| **Numbers & Symbols Only** | 28 | 0.13% | Formatting tokens, punctuation, mathematical expressions |
| **Empty Strings** | 0 | 0.00% | Zero empty values |

### 3.3 Domain Breakdown of the 7,332 Untranslated Keys
```
General UI & Dialogues               [========================] 4,020 (54.8%)
ICU / Format Strings & Plurals      [=====]                    945 (12.9%)
Authentication, SSO & Org Admin     [====]                     865 (11.8%)
Tokens, Billing & Subscription      [==]                       419 ( 5.7%)
Projects & Knowledge Base           [=]                        265 ( 3.6%)
Settings & UI Customization         [=]                        230 ( 3.1%)
MCP & Server Configuration          [=]                        228 ( 3.1%)
Errors & Diagnostics                [=]                        182 ( 2.5%)
Artifacts & Sandbox Execution       [=]                        178 ( 2.4%)
```

---

## 4. Formatting Placeholders & ICU MessageFormat Audit

### 4.1 ICU MessageFormat Syntax
- **Total ICU Strings:** 1,010 strings containing `{name, plural, ...}`, `{select, ...}`, or `{number, ...}` formatting.
  - **Translated / Partially Translated ICU:** 510 strings
  - **Untranslated English ICU:** 500 strings
- **Sample Translated ICU String:**
  - Key `+8nVZyI6SB`: `<b>{category}</b> 需要 {count, plural, one {{label}} other {# 个字段}}`
  - Key `+Lgjm6TdiG`: `{sign}{count, plural, one {# 个 Research Labs Premium 席位} other {# 个 Research Labs Premium 席位}}（按年比例计算）`
- **Sample Untranslated ICU String:**
  - Key `31se92/223`: `{value, plural, one {#m} other {#m}}`
  - Key `lv+bhopVDB`: `{count, plural, one {# {singular}} other {# {plural}}}`
  - Key `++8r0fTTdU`: `{serverLabel} is still running. You can keep it running and re-open a tab any time by entering {host}...`

### 4.2 Placeholder & Tag Safety
- **Unbalanced Curly Braces (`{` vs `}`):** **0** (All open braces have matching closing braces).
- **Leftover Translation Engine Placeholders (`__PH0__`, `PH0X`):** **0** (All translation placeholders properly restored).
- **Printf Format Specifiers (`%s`, `%d`, `%1$s`):** **0** (Project relies entirely on ICU format `{var}`).
- **HTML Tag Balancing:** 5 strings contain CLI parameter syntax like `<name>` or `<device>` in untranslated simulator logs (`xcrun simctl boot '<device>'`), which are not actual HTML elements.

---

## 5. Character Encoding & Mojibake Audit

A full-corpus scan across all 22,319 keys verified:
1. **Unicode Replacement Character (`\ufffd` / ``):** 0 instances.
2. **Standard GBK Mojibake (`锟斤拷`, `烫烫烫`, `屯屯屯`):** 0 instances.
3. **Double UTF-8 Encoding (`Ã©`, `â€`, `\xc2\xc3`):** 0 instances.
4. **HTML Entity Remnants (`&amp;`, `&quot;`, `&lt;`, `&#39;`):** 0 instances.
5. **Control Characters (excluding standard `\t`, `\n`, `\r`):** 0 instances.
6. **JSON Escaping Integrity:** 100% compliant with standard JSON RFC 8259.

---

## 6. Developer Terminology Consistency Audit

### 6.1 Critical Terminology Inconsistencies Discovered

#### A. Artifacts (Extreme Fragmentation)
| Translation Used | Occurrence Count | Example String | Status |
|---|---|---|---|
| `Artifacts` (English) | 135 | `您的组织管理员已禁用 Artifacts 中的连接器。` | Untranslated brand noun |
| `制品` | 57 | `登录 Claude 以使用或自定义此制品。` | Standard translation |
| `工件` | 15 | `您组织中的任何人都可以查看此工件。` | Inconsistent variant |
| `构件` | 15 | `允许团队成员使用聊天、项目和构件。` | Inconsistent variant |
| `产物` | 1 | `切换产物` | Inconsistent variant |

**Audit Conclusion:** 4 different Chinese terms (`制品`, `工件`, `构件`, `产物`) coexist alongside raw English `Artifacts` in the same UI.  
**Standard Recommendation:** Unify to **`制品`** or **`制品 (Artifacts)`** consistently.

---

#### B. Model Context Protocol (MCP)
| Translation Used | Occurrence Count | Example String |
|---|---|---|
| `MCP` | 109 | `已有可视化 UI MCP 应用？` |
| `MCP 服务器` | 40 | `允许用户添加 MCP 服务器` |
| `Model Context Protocol` | 2 | `Model Context Protocol 文档` |
| `MCP 工具` | 2 | `MCP 工具` |
| `模型上下文协议` | 1 | `通过模型上下文协议 (MCP) 连接的外部服务和工具。` |

**Audit Conclusion:** MCP terminology is relatively well-adopted (`MCP 服务器` and `MCP 工具`), but descriptive text should consistently use **`模型上下文协议 (MCP)`** on first mention.

---

#### C. Computer Use
| Translation Used | Occurrence Count | Example String |
|---|---|---|
| `计算机使用` | 5 | `开启计算机使用功能？` |
| `Computer Use` (English) | 1 | `Turn on computer use in Settings, then try recording again.` |

**Audit Conclusion:** Needs complete translation to **`计算机使用 (Computer Use)`** across all prompt and settings keys.

---

#### D. Token & Context Management
| Translation Used | Occurrence Count | Usage Context |
|---|---|---|
| `令牌` | 97 | AWS/OAuth tokens (`您的 AWS 令牌已过期`) |
| `Token` / `Tokens` | 91 | LLM token count (`节省了 {tokens} 个 token`) |
| `上下文窗口` | 7 | Context window capacity (`增强上下文窗口`) |
| `Context Window` (English) | 4 | Untranslated (`Context window was full`) |
| `上下文限制` | 1 | Context limit reached (`对话已达到上下文限制`) |

**Audit Conclusion:** Clear linguistic distinction is needed:
- Authentication / OAuth -> **`令牌`** (e.g., `授权令牌`, `访问令牌`)
- LLM Token / Token Usage -> **`Token`** (e.g., `节省了 {tokens} 个 Token`)
- Context Window -> **`上下文窗口`**

---

#### E. Extended Thinking & Reasoning Mode
| Translation Used | Occurrence Count | Example String |
|---|---|---|
| `扩展思考` | 3 | `此项目需要扩展思考。` |
| `Thinking mode` (English) | 2 | `Change thinking mode?` |

**Audit Conclusion:** Standardize to **`深度思考`** or **`扩展思考 (Extended Thinking)`**.

---

#### F. Connectors & Integrations
| Translation Used | Occurrence Count | Example String |
|---|---|---|
| `连接器` | 252 | `允许连接器工具使用「始终允许」` |
| `Connectors` (English) | 164 | `{connector} 的权限` |
| `集成` | 31 | `连接最多的集成` |

**Audit Conclusion:** Standardize to **`连接器 (Connectors)`** for external data sources and **`集成`** for editor integrations (VS Code, Cursor).

---

### 6.2 Recommended Unified Terminology Glossary
```markdown
| English Original | Recommended Chinese Term | Scope / Rules |
|---|---|---|
| Artifacts | 制品 (Artifacts) / 制品 | Code blocks, React preview, SVG/HTML canvas |
| Model Context Protocol (MCP) | 模型上下文协议 (MCP) / MCP | Protocol definition and tool integrations |
| MCP Server | MCP 服务器 | External MCP server endpoint |
| MCP Tool | MCP 工具 | Executable tool exposed by MCP |
| Computer Use | 计算机使用 (Computer Use) | Agent desktop control capability |
| Token (LLM) | Token | LLM context token consumption |
| Token (Auth/API) | 访问令牌 / 授权令牌 | OAuth credentials and API keys |
| Context Window | 上下文窗口 | Maximum context length |
| Extended Thinking / Thinking Mode | 深度思考 / 扩展思考 | Claude 3.7 Sonnet reasoning mode |
| Prompt Caching | 提示词缓存 | Prompt cache mechanism |
| Projects | 项目 | Knowledge base and system prompt workspace |
| Custom Instructions | 自定义指令 | User-defined prompt instructions |
| Connectors | 连接器 | Data source connections (Google Drive, GitHub) |
| Workspaces / Organization | 工作区 / 组织 | Multi-user team collaboration spaces |
```

---

## 7. Existing Validation & CI/CD Script Audit

### 7.1 `scripts/validate.py` Analysis
1. **Critical Failure:** Line 33 defines `MIN_CHINESE_RATIO = 0.90`. Current Chinese ratio is `67.02%`, causing the script to **immediately exit with code 1**:
   ```
   [FAIL] Chinese-looking value ratio is 67.02%, expected at least 90%
   ```
2. **Missing Coverage Checks:** When `local/en-US.json` does not exist (the standard repository state), coverage comparison is silently skipped (Line 95).
3. **No ICU MessageFormat Linting:** Does not check if ICU plural/select arguments match between source and translation.
4. **No Terminology Glossary Enforcement:** Does not verify consistency of developer terms.

### 7.2 `tests/test_runner.py` Analysis
1. **Narrow Scope:** `test_02_no_mojibake_or_corrupted_characters` only slices `list(data.items())[:500]`, testing only 500 keys (2.2%) while leaving 21,819 keys (97.8%) untested.
2. **Low Minimum Key Threshold:** Line 14 asserts `len(data) >= 15000` instead of the full `22,000+` baseline.

### 7.3 `.github/workflows/validate.yml` Analysis
1. Runs only on `windows-latest`, missing Linux and macOS matrix validation.
2. Currently fails in CI due to `scripts/validate.py` failure.

---

## 8. Concrete Action Steps for R2 Implementation

```
┌────────────────────────────────────────────────────────────────────────────┐
│                    R2 IMPLEMENTATION ACTION PLAN                           │
├────────────────────────────────────────────────────────────────────────────┤
│ 1. Complete Translation of 7,332 Keys                                      │
│    • Batch-translate ~4,200 long UI sentences and dialogues               │
│    • Localize ~945 ICU plural/select format strings safely                 │
│    • Translate ~865 Auth, SSO, and Organization management strings         │
│    • Translate ~228 MCP server and ~178 Artifacts UI strings               │
│    • Target: Reach >= 98.5% Chinese translation coverage                   │
├────────────────────────────────────────────────────────────────────────────┤
│ 2. Apply Terminology Glossary Alignment                                    │
│    • Replace all 15 "工件", 15 "构件", 1 "产物" with "制品"                │
│    • Standardize 135 raw "Artifacts" into "制品 (Artifacts)" / "制品"      │
│    • Disambiguate "令牌" (Auth) vs "Token" (LLM)                           │
│    • Standardize "Computer Use" to "计算机使用"                            │
│    • Standardize "Thinking mode" to "深度思考 / 扩展思考"                  │
├────────────────────────────────────────────────────────────────────────────┤
│ 3. Build Enhanced Linguistic & ICU Validator Tool                          │
│    • Update scripts/validate.py with full-corpus ICU MessageFormat linter  │
│    • Validate 100% of 22,319 keys for mojibake and illegal escapes         │
│    • Implement automated glossary conformity check                         │
├────────────────────────────────────────────────────────────────────────────┤
│ 4. Upgrade Unit Tests & Multi-OS CI Workflow                               │
│    • Expand tests/test_runner.py to validate all 22,319 keys               │
│    • Set key count assertion to >= 22,000                                  │
│    • Enable multi-platform CI matrix (Windows, Ubuntu, macOS)              │
└────────────────────────────────────────────────────────────────────────────┘
```

---
*Report compiled and verified by Explorer 1 (`explorer_survey_1`).*
