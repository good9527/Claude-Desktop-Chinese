## 2026-09-02T06:53:39Z

You are Test Writer for the E2E Testing Track for the project at C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese.
Your working directory is C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese\.agents\test_writer_e2e.
Your parent orchestrator is at C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese\.agents\orchestrator_1.

Read the authoritative original request at C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese\.agents\ORIGINAL_REQUEST.md.
Read the project architecture and contracts at C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese\PROJECT.md.
Read the survey reports at:
- C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese\.agents\explorer_survey_2\survey_r3.md
- C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese\.agents\explorer_survey_3\survey_r1_r4.md

YOUR EXCLUSIVE WRITE OWNERSHIP:
- `tests/test_runner.py`
- `tests/`
- `TEST_INFRA.md`
- `TEST_READY.md`
Do NOT modify files outside your ownership.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

TASK: E2E Testing Track — Comprehensive 5-Tier E2E Test Suite & Test Readiness Publication
1. Author `TEST_INFRA.md` according to the E2E Testing Track principles in PROJECT.md:
   - Test Philosophy (opaque-box, requirement-driven, progressive testability).
   - Feature Inventory mapping all features F1.1–F4.4 to test tiers.
   - Architecture of test runners, pass/fail semantics, and CLI tier selection (`--tier 1`, `--tier 2`, ..., `--tier all`).
2. Implement comprehensive, production-grade test suite in `tests/test_runner.py`:
   - Tier 1: Feature Coverage (dictionary structure, full 22,319 key quantification, JSON syntax, UTF-8 integrity, Schema.org schemas, CLI help/version).
   - Tier 2: Boundary & Corner Cases (empty values, extreme strings, ICU plural/select edge cases, surrogate pair characters, non-ASCII filename handling, registry PSDrive collision checks).
   - Tier 3: Cross-Feature Interactions (dictionary parity between dist/zh-CN.json and zh-CN-ion.json, terminology consistency across all keys, CDN fallback waterfall simulation, diagnostic schema validation).
   - Tier 4: Real-World Workload Scenarios (simulated full install/patch workflow, in-place atomic backup and restore, background watcher daemon lifecycle simulation, multi-OS path resolution).
   - CLI flags: `--tier 1`, `--tier 2`, `--tier 3`, `--tier 4`, `--tier all`, `--verbose`, `--json`.
3. Run `python tests/test_runner.py --tier all` to ensure all tests execute and pass cleanly.
4. Author `TEST_READY.md` summarizing test counts across all tiers and execution instructions.
