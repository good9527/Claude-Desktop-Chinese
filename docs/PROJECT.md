# Project: Claude-Desktop-Chinese Optimization & Ecosystem

## Architecture

The system consists of five primary layers:
1. **Linguistic Core (`dist/zh-CN.json`, `zh-CN-ion.json`)**:
   - 22,319 React-Intl / FormatJS AST hash keys.
   - Professional developer terminology glossary (MCP, Artifacts, Computer Use, token management).
   - Strict ICU MessageFormat syntax `{param, select/plural, ...}` preservation and zero mojibake guarantee.
2. **SEO & GEO AI Discoverability Layer (`SEO_GEO_INDEX.md`, `README.md`, `sitemap.xml`, `sitemap.json`)**:
   - Schema.org JSON-LD structured schemas (`SoftwareApplication`, `FAQPage`, `HowTo`).
   - Generative AI Search Engine Query Matrices (ChatGPT, Claude, Gemini, DeepSeek, Perplexity).
   - Multi-engine search indexing metadata (Google, Baidu, Bing).
3. **Cross-Platform Installer & 3-Tier Self-Healing Engine (`install.ps1`, `install.sh`, `watcher/*`, `patch_claude.*`)**:
   - Tier A: OS File Watcher Daemon (`watcher.ps1` on Windows, `launchd` plist on macOS, `systemd` on Linux).
   - Tier B: Application Startup Hook / Shell wrapper.
   - Tier C: Zero-Lock In-Place Hot Patch with atomic backup/restore.
   - Interactive Elite Toolkit CLI with standardized flags (`-i`, `-u`, `-c`, `-r`, `--daemon`, `-q`, `--json`).
   - 4-Tier Zero-Latency CDN waterfall (Fastly / Cloudflare / jsDelivr / GitHub Raw).
4. **Validation & Quality Assurance Suite (`scripts/validate.py`, `tests/test_runner.py`)**:
   - Full 22,319-key Unicode integrity, CJK ratio, ICU placeholder syntax parser.
   - Cross-platform PowerShell/Bash syntax validators and path traversal safeguards.
   - 5-Tier E2E test runner (Tiers 1-5).
5. **Multi-OS CI/CD Pipeline (`.github/workflows/validate.yml`, `.github/workflows/release.yml`)**:
   - GitHub Actions matrix across Windows, macOS, Ubuntu on Python 3.10–3.13.
   - Automated tag-triggered release generation with pre-compiled offline packages (`.zip`, `.tar.gz`) and SHA256 checksums.

---

## Feature Inventory

| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| F1.1 | Schema.org JSON-LD Structured Data | Integrate `SoftwareApplication`, `FAQPage`, and `HowTo` schemas into docs | M1 | survey_r1_r4 |
| F1.2 | AI Natural Language Query Matrices | 5-category query matrices for ChatGPT, Claude, Gemini, DeepSeek, Perplexity | M1 | survey_r1_r4 |
| F1.3 | Dynamic Sitemap & Metadata Index | Dynamic `sitemap.xml`, `sitemap.json`, and search taxonomy (Google/Baidu/Bing) | M1 | survey_r1_r4 |
| F1.4 | README & Topic Metadata Optimization | Optimized badges, rich snippets, fast-start commands, and discoverability index | M1 | survey_r1_r4 |
| F2.1 | 22,319 Keys Translation Completion | Complete remaining ~7,332 untranslated keys achieving >=98.5% Chinese coverage | M2 | survey_r2 |
| F2.2 | AI Developer Terminology Harmonization | Harmonize terms: Artifacts (`制品`), MCP (`模型上下文协议`), Computer Use, etc. | M2 | survey_r2 |
| F2.3 | ICU MessageFormat & Placeholder Safety | Validate all ICU `{var, plural/select}` syntax and zero placeholder corruption | M2 | survey_r2 |
| F2.4 | Validator Script Enhancement | Upgrade `scripts/validate.py` with multi-OS support, regex fixes, 22K checks | M2 | survey_r2 |
| F3.1 | Multi-OS GitHub Actions CI Matrix | Upgrade `validate.yml` for Windows, macOS, Linux on Python 3.10–3.13 | M3 | survey_r3 |
| F3.2 | Automated Release Workflow | Implement `release.yml` with tag triggers, offline `.zip`/`.tar.gz` and SHA256 | M3 | survey_r3 |
| F3.3 | Pull Request & Linters Hooks | Cross-platform linter and dictionary parity check on all PRs | M3 | survey_r3 |
| F4.1 | 3-Tier Auto-Healing Standard | Cross-platform daemons: Windows (`watcher.ps1`), macOS (`launchd`), Linux (`systemd`)| M4 | survey_r1_r4 |
| F4.2 | Interactive Elite Toolkit CLI | Full CLI flag parity across `install.ps1`/`install.sh` (`-i`, `-u`, `-c`, `-r`, `--daemon`, `-q`, `--json`)| M4 | survey_r1_r4 |
| F4.3 | Zero-Latency 4-Tier CDN Waterfall | CDN failover (Fastly -> Cloudflare -> jsDelivr -> GitHub Raw) | M4 | survey_r1_r4 |
| F4.4 | Unified Health Diagnostic Reporting | Standardized JSON diagnostic schema and health reporting output | M4 | survey_r1_r4 |
| F5.1 | 5-Tier E2E Test Suite | Modular test suite in `tests/test_runner.py` spanning Tiers 1–4 | E2E Track | survey_r3 |
| F5.2 | Tier 5 Adversarial Coverage Hardening | White-box stress tests, corrupt input resilience, in-place lock recovery | Final Milestone | survey_r3 |

---

## Milestones

| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | SEO & GEO AI Discoverability | F1.1, F1.2, F1.3, F1.4 (`SEO_GEO_INDEX.md`, `README.md`, `sitemap.*`) | None | PLANNED |
| M2 | Translation Audit & Terminology Harmonization | F2.1, F2.2, F2.3, F2.4 (`dist/zh-CN.json`, `zh-CN-ion.json`, `scripts/validate.py`) | None | PLANNED |
| M3 | Multi-OS CI/CD Pipeline & Automated Release | F3.1, F3.2, F3.3 (`.github/workflows/validate.yml`, `release.yml`) | M2 | PLANNED |
| M4 | Cross-Project Synergies & Self-Healing Ecosystem | F4.1, F4.2, F4.3, F4.4 (`install.sh`, `uninstall.sh`, `patch_claude.*`, `watcher/*`) | M2 | PLANNED |
| E2E | E2E Testing Track | F5.1 (Tiers 1–4 Test Suite & Infrastructure -> `TEST_READY.md`) | None (Parallel Track) | PLANNED |
| M5 | Final Milestone: 100% E2E Pass & Tier 5 Hardening | F5.2 (Tier 1–4 verification + Tier 5 Adversarial Coverage Hardening) | M1, M2, M3, M4, E2E | PLANNED |

---

## Interface Contracts

### 1. Linguistic Dictionary Contract
- File path: `dist/zh-CN.json` and `zh-CN-ion.json` (must remain 100% identical in key set and values).
- Exact key count: 22,319 keys.
- Encoding: UTF-8 without BOM or UTF-8-sig transparently accepted. Zero `\ufffd` or mojibake.
- Placeholder rules: Preserve all `{param}`, `{0}`, `%s`, `{count, plural, ...}`, `{gender, select, ...}` exactly.
- Terminology glossary:
  - `Artifacts` -> `制品` (consistent developer standard)
  - `Model Context Protocol / MCP` -> `模型上下文协议 (MCP)` / `MCP 服务器`
  - `Computer Use` -> `计算机使用`
  - `API Key / Auth Token` -> `访问令牌 / API 密钥` (distinguished from LLM `Token`)
  - `Context Window` -> `上下文窗口`
  - `Extended Thinking` -> `扩展思考 / 深度思考`

### 2. CLI Interface & Diagnostic Schema Contract
Both `install.ps1` and `install.sh` must accept:
- `-i, --install`: Install or update localization.
- `-u, --uninstall`: Uninstall localization and restore original files.
- `-c, --check`: Run diagnostic health check and print status.
- `-r, --restore`: Restore from backup.
- `--daemon`: Start or install the Tier A background watcher daemon.
- `-q, --quiet`: Non-interactive quiet mode.
- `--json`: Output diagnostic reports in standardized JSON schema:
```json
{
  "project": "Claude-Desktop-Chinese",
  "version": "1.0.0",
  "platform": "windows|darwin|linux",
  "claude_path": "/path/to/resources",
  "status": "healthy|patched|unpatched|corrupted",
  "tier_a_watcher_active": true,
  "dictionary_keys": 22319,
  "chinese_ratio": 0.985
}
```

### 3. CI/CD & Validation Contract
- `python scripts/validate.py` must return exit code 0 on all platforms.
- `python -m unittest tests/test_runner.py` or `python tests/test_runner.py --tier all` must pass all test cases with exit code 0.
- GitHub Actions `validate.yml` must execute matrix `[windows-latest, macos-latest, ubuntu-latest]` on Python `[3.10, 3.11, 3.12, 3.13]`.

---

## Code Layout & Write Ownership

| Path / Module | Owning Milestone / Track | Concurrency Safety |
|---|---|---|
| `SEO_GEO_INDEX.md`, `README.md`, `sitemap.xml`, `sitemap.json` | M1 (SEO & GEO) | Exclusive to M1 |
| `dist/zh-CN.json`, `zh-CN-ion.json`, `scripts/validate.py` | M2 (Translation & Validator) | Exclusive to M2 |
| `.github/workflows/validate.yml`, `.github/workflows/release.yml` | M3 (CI/CD Pipeline) | Exclusive to M3 |
| `install.sh`, `uninstall.sh`, `patch_claude.sh`, `patch_claude.ps1`, `watcher/*` | M4 (Self-Healing & CLI) | Exclusive to M4 |
| `tests/test_runner.py`, `tests/` | E2E Testing Track / M5 | Exclusive to E2E / M5 |


