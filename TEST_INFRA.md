# E2E Test Infrastructure & Test Architecture

**Project**: `Claude-Desktop-Chinese`  
**Document Version**: 1.0.0  
**Status**: Authoritative E2E Test Specification  

---

## 1. Test Philosophy & Principles

The `Claude-Desktop-Chinese` End-to-End (E2E) Test Suite provides rigorous, automated verification of the entire localization ecosystem. The test infrastructure adheres to four core testing principles:

### 1.1 Opaque-Box Validation
Tests treat all components—the linguistic core, installer scripts, background auto-healing daemons, and SEO/GEO structured data—as opaque systems. Tests assert verifiable behaviors, file artifacts, syntax integrity, and interface contracts without relying on internal private implementation details.

### 1.2 Requirement-Driven Expected Output Derivation
Every test case derives its assertions and expected values directly from authoritative requirements specified in:
- `ORIGINAL_REQUEST.md` (R1 Deep SEO/GEO, R2 Translation Audit, R3 Multi-OS CI/CD, R4 Self-Healing Ecosystem)
- `PROJECT.md` (Interface Contracts §1 Linguistic Dictionary, §2 CLI & Diagnostic Schema, §3 CI/CD & Validation)
- Architectural surveys (`survey_r1_r4.md`, `survey_r2.md`, `survey_r3.md`)

### 1.3 Progressive Testability & Milestones
Tests are designed to be verifiable against completed and parallel milestones:
- Tests validate both static contract guarantees (full 22,319 key quantification, ICU format safety, terminology glossary) and dynamic operations (synthetic dictionary merges, atomic file replacements, multi-CDN fallback simulations).
- Graceful fallbacks and multi-source checks ensure test execution succeeds across diverse developer environments (Windows, macOS, Linux, Python 3.10–3.13).

### 1.4 Test Independence & State Isolation
Each test case is completely self-contained:
- File system mutations (mock installation trees, temporary backup targets, simulated Electron packages) are executed in isolated `tempfile.TemporaryDirectory()` contexts.
- No test depends on execution order or side-effects from preceding tests.
- All temporary artifacts are strictly cleaned up during `tearDown()`.

---

## 2. Feature Inventory to Test Tier Mapping

All system features defined in `PROJECT.md` (F1.1 through F5.1) are mapped to 4 foundational test tiers:

| Feature ID | Feature Name | Target Scope | Test Tier | Primary Test Class / Method |
|:---|:---|:---|:---:|:---|
| **F1.1** | Schema.org JSON-LD Structured Data | Embedded `SoftwareApplication`, `FAQPage`, `HowTo` schemas | **Tier 1** | `test_f1_1_schema_org_structured_data` |
| **F1.2** | AI Natural Language Query Matrices | 5-category search query matrices across AI models | **Tier 1** | `test_f1_2_ai_query_matrices_structure` |
| **F1.3** | Dynamic Sitemap & Metadata Index | `sitemap.xml`, `sitemap.json`, search taxonomy | **Tier 1** | `test_f1_3_sitemap_metadata_integrity` |
| **F1.4** | README & Metadata Optimization | Badges, translation count declarations, fast-start commands | **Tier 1** | `test_f1_4_readme_statistics_parity` |
| **F2.1** | 22,319 Keys Translation & JSON Syntax | Full 22,319 key quantification, JSON syntax, UTF-8 validity | **Tier 1** | `test_f2_1_dictionary_quantification_and_syntax` |
| **F2.1** | Boundary & Empty Value Checks | Zero empty strings, zero whitespace-only values | **Tier 2** | `test_f2_1_no_empty_or_whitespace_values` |
| **F2.1** | Dictionary Parity | 100% key and value identity between `dist/zh-CN.json` & `zh-CN-ion.json` | **Tier 3** | `test_f2_1_dictionary_bit_parity` |
| **F2.2** | AI Developer Terminology Consistency | Harmonization: `Artifacts` (`制品`), `MCP` (`模型上下文协议`), etc. | **Tier 3** | `test_f2_2_terminology_glossary_consistency` |
| **F2.3** | ICU MessageFormat & Placeholder Safety | Bracket balance, `{var}`, `{count, plural}`, `{select}` preservation | **Tier 2** | `test_f2_3_icu_messageformat_and_placeholders` |
| **F2.4** | Non-ASCII Filename Handling | Git quotepath and UTF-8 filename resilience | **Tier 2** | `test_f2_4_non_ascii_filename_handling` |
| **F3.1** | Cross-Platform Compatibility | Multi-OS path resolution (Windows, macOS, Linux) | **Tier 4** | `test_f3_1_multi_os_path_resolution` |
| **F3.3** | Registry PSDrive Collision Safeguards | Regex distinction between Windows drive letters and `HKCU:\` | **Tier 2** | `test_f3_3_psdrive_path_scan_collision_safeguard` |
| **F4.1** | 3-Tier Auto-Healing Standard | Simulated watcher daemon lifecycle & auto-heal re-patching | **Tier 4** | `test_f4_1_auto_healing_watcher_lifecycle` |
| **F4.1** | In-Place Atomic Backup & Restore | Initial backup creation and bit-exact rollback | **Tier 4** | `test_f4_1_atomic_backup_and_restore_workflow` |
| **F4.2** | CLI Options & Parameters Contract | Standardized CLI flags (`-i`, `-u`, `-c`, `-r`, `--daemon`, `-q`, `--json`)| **Tier 1** | `test_f4_2_cli_interface_parameter_contract` |
| **F4.2** | Simulated Full Install & Patch Workflow | Synthetic `en-US.json` merge overlay, key preservation | **Tier 4** | `test_f4_2_simulated_full_install_patch_workflow` |
| **F4.3** | 4-Tier Multi-CDN Waterfall | Multi-mirror failover (Fastly -> Cloudflare -> Ghfast -> GitHub) | **Tier 3** | `test_f4_3_cdn_waterfall_failover_simulation` |
| **F4.4** | Unified Health Diagnostic Reporting | Standardized JSON diagnostic schema and type constraints | **Tier 3** | `test_f4_4_diagnostic_json_schema_validation` |

---

## 3. Test Architecture & Tier Structure

The test runner `tests/test_runner.py` is architected into four distinct test suites, structured using Python's standard `unittest` framework:

```
tests/test_runner.py
│
├── Tier 1: Feature Coverage (Tier1FeatureCoverageTests)
│   ├── Dictionary Structure & Exact 22,319 Key Quantification
│   ├── Complete 22,319 Key Unicode & UTF-8 Integrity (Zero \ufffd, Zero Mojibake)
│   ├── Schema.org JSON-LD Structured Data Verification (SoftwareApplication, FAQPage, HowTo)
│   ├── Dynamic Sitemap & Search Metadata Integrity
│   ├── README Translation Count & Statistics Parity
│   └── CLI Interface & Script Parameter Contract Compliance
│
├── Tier 2: Boundary & Corner Cases (Tier2BoundaryCornerCaseTests)
│   ├── Zero Empty String / Whitespace-Only Translations
│   ├── Extreme Length Translations & Complex HTML Tag Integrity
│   ├── Comprehensive ICU MessageFormat Braces & Variable Balance
│   ├── 4-Byte UTF-8 Surrogates, Emojis & CJK Extension Boundaries
│   ├── Non-ASCII Filename Encoding (Git Quotepath Safety)
│   └── PowerShell Registry PSDrive (`HKCU:\`) Path Scan Regex Collision Safeguards
│
├── Tier 3: Cross-Feature Interactions (Tier3CrossFeatureInteractionTests)
│   ├── Strict Dictionary Parity (`dist/zh-CN.json` == `zh-CN-ion.json`)
│   ├── AI Developer Terminology Consistency Glossary Matrix
│   ├── 4-Tier Multi-CDN Waterfall Acceleration & Failover Simulation
│   └── Standardized Health Diagnostic JSON Schema Validation
│
└── Tier 4: Real-World Workload Scenarios (Tier4RealWorldWorkloadTests)
    ├── Simulated Full In-Place Install & Dictionary Merge Workflow
    ├── In-Place Atomic Backup Creation & 100% Bit-Exact Rollback
    ├── Background Watcher Daemon Auto-Healing & Update Recovery Lifecycle
    └── Cross-Platform Multi-OS Target Discovery (Windows, macOS, Linux)
```

---

## 4. Test Runner CLI & Execution Options

`tests/test_runner.py` provides a unified command-line interface supporting granular tier filtering, verbose diagnostic output, and machine-readable JSON reports.

### 4.1 CLI Syntax

```bash
# Run all tiers (Tier 1 through Tier 4)
python tests/test_runner.py --tier all

# Run specific tier
python tests/test_runner.py --tier 1
python tests/test_runner.py --tier 2
python tests/test_runner.py --tier 3
python tests/test_runner.py --tier 4

# Run with verbose test descriptions and timings
python tests/test_runner.py --tier all --verbose

# Run and output machine-readable JSON summary (for CI/CD pipelines)
python tests/test_runner.py --tier all --json

# Standard unittest runner discovery (IDE and tool agnostic)
python -m unittest discover -s tests -p "test_*.py"
```

### 4.2 CLI Argument Specifications

| Option | Short | Description |
|:---|:---|:---|
| `--tier <1\|2\|3\|4\|all>` | `-t` | Selects which test tier(s) to execute (default: `all`) |
| `--verbose` | `-v` | Enables detailed per-test execution logging and timing benchmarks |
| `--json` | `-j` | Emits structured JSON payload containing test metrics, pass/fail status, and execution duration |
| `--help` | `-h` | Displays usage summary and available options |

### 4.3 Pass / Fail Semantics

- **Exit Code `0`**: All executed test cases passed successfully.
- **Exit Code `1`**: One or more test cases failed or encountered an unexpected exception.
- When run with `--json`, the JSON output includes `"success": true|false`, total test counts, failures, errors, skipped tests, and detailed failure traceback descriptions.

---

## 5. Continuous Integration (CI) Integration

The test suite is integrated into GitHub Actions CI workflows (`.github/workflows/validate.yml` and `release.yml`) across:
- **Operating Systems**: Windows (`windows-latest`), macOS (`macos-latest`), Linux (`ubuntu-latest`).
- **Python Runtimes**: Python 3.10, 3.11, 3.12, 3.13.
- **Verification Commands**:
  ```yaml
  - name: Run 5-Tier E2E Test Suite
    run: python tests/test_runner.py --tier all --verbose
  ```
