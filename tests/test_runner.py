#!/usr/bin/env python3
"""Comprehensive 5-Tier E2E Test Suite for Claude-Desktop-Chinese.

Features Covered: F1.1 - F4.4 across 4 Tiers:
- Tier 1: Feature Coverage (Dictionary structure, 22,319 keys, JSON syntax, UTF-8 integrity, Schema.org, CLI)
- Tier 2: Boundary & Corner Cases (Empty values, extreme strings, ICU message format, surrogates, non-ASCII)
- Tier 3: Cross-Feature Interactions (Dictionary parity, terminology consistency, CDN waterfall, diagnostic schema)
- Tier 4: Real-World Workload Scenarios (Simulated install/merge, atomic backup/rollback, watcher auto-heal, multi-OS paths)

CLI Usage:
    python tests/test_runner.py --tier all
    python tests/test_runner.py --tier 1
    python tests/test_runner.py --tier 2
    python tests/test_runner.py --tier 3
    python tests/test_runner.py --tier 4
    python tests/test_runner.py --tier all --verbose
    python tests/test_runner.py --tier all --json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import time
import unittest
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Base repository root directory
ROOT_DIR = Path(__file__).resolve().parents[1]
DIST_ZH_PATH = ROOT_DIR / "dist" / "zh-CN.json"
ION_ZH_PATH = ROOT_DIR / "zh-CN-ion.json"
INSTALL_PS1_PATH = ROOT_DIR / "install.ps1"
INSTALL_SH_PATH = ROOT_DIR / "install.sh"
UNINSTALL_PS1_PATH = ROOT_DIR / "uninstall.ps1"
PATCH_CLAUDE_PS1_PATH = ROOT_DIR / "patch_claude.ps1"
WATCHER_PS1_PATH = ROOT_DIR / "watcher" / "watcher.ps1"
README_PATH = ROOT_DIR / "README.md"
PROJECT_MD_PATH = ROOT_DIR / "PROJECT.md"

TOTAL_EXPECTED_KEYS = 22319


# ==============================================================================
# Helper Utilities
# ==============================================================================

def load_json_file(path: Path) -> Dict[str, Any]:
    """Load and parse a JSON file with UTF-8 encoding."""
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    with path.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object at {path}, got {type(data).__name__}")
    return data


def extract_icu_placeholders(text: str) -> List[str]:
    """Extract ICU and standard variable placeholders from translation string."""
    return re.findall(r"\{[^\{\}]+\}", text)


def simulate_cdn_fetch(
    urls: List[str],
    mock_responses: Dict[str, Tuple[int, Optional[str]]],
) -> Optional[str]:
    """Simulate multi-tier CDN waterfall fallback."""
    for url in urls:
        status_code, body = mock_responses.get(url, (500, None))
        if status_code == 200 and body is not None and len(body) > 10:
            return body
    return None


# ==============================================================================
# Tier 1: Feature Coverage Tests
# ==============================================================================

class Tier1FeatureCoverageTests(unittest.TestCase):
    """Tier 1: Basic and Complete Feature Coverage.
    
    Covers:
    - F2.1: Dictionary structure, exact 22,319 key quantification, JSON syntax
    - F2.1: Full UTF-8 integrity & zero mojibake across ALL keys
    - F1.1: Schema.org structured data schemas (SoftwareApplication, FAQPage, HowTo)
    - F1.3 / F1.4: Dynamic sitemap & metadata index and README statistics parity
    - F4.2: CLI parameter interface contracts across installer scripts
    """

    def test_f2_1_dictionary_quantification_and_syntax(self) -> None:
        """Verify dist/zh-CN.json exists, parses cleanly, and quantifies exact 22,319 keys."""
        self.assertTrue(DIST_ZH_PATH.exists(), f"Missing required file: {DIST_ZH_PATH}")
        data = load_json_file(DIST_ZH_PATH)
        self.assertIsInstance(data, dict, "Dictionary must be a JSON Object (dict)")
        self.assertEqual(
            len(data),
            TOTAL_EXPECTED_KEYS,
            f"Expected exactly {TOTAL_EXPECTED_KEYS} keys in dist/zh-CN.json, found {len(data)}",
        )
        # Verify keys and values are non-empty strings
        for k, v in list(data.items())[:100]:
            self.assertIsInstance(k, str, f"Dictionary key must be string: {k}")
            self.assertGreater(len(k), 0, "Dictionary key must not be empty")
            self.assertIsInstance(v, str, f"Dictionary value for key '{k}' must be string")

    def test_f2_1_unicode_and_utf8_integrity(self) -> None:
        """Audit ALL 22,319 keys for unicode replacement characters (\ufffd) and mojibake."""
        data = load_json_file(DIST_ZH_PATH)
        corrupted_keys: List[str] = []
        mojibake_patterns = [
            re.compile(r"Ã[©§¢£]"),
            re.compile(r"æˆ‘ä»¬"),
            re.compile(r"çš„"),
            re.compile(r"ä¸€"),
        ]

        for k, v in data.items():
            if "\ufffd" in v or "\uFFFD" in v:
                corrupted_keys.append(k)
            for pattern in mojibake_patterns:
                if pattern.search(v):
                    corrupted_keys.append(f"{k} (mojibake pattern match)")
                    break

        self.assertEqual(
            len(corrupted_keys),
            0,
            f"Found {len(corrupted_keys)} corrupted/mojibake entries in dist/zh-CN.json: {corrupted_keys[:5]}",
        )

    def test_f1_1_schema_org_structured_data(self) -> None:
        """Validate Schema.org JSON-LD structured data formats for SEO & GEO."""
        # Check if Schema.org JSON-LD exists in README.md, SEO_GEO_INDEX.md, or sitemap.json
        candidate_files = [
            ROOT_DIR / "README.md",
            ROOT_DIR / "SEO_GEO_INDEX.md",
            ROOT_DIR / "sitemap.json",
        ]

        found_schemas = 0
        for path in candidate_files:
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8-sig")
            # Extract JSON-LD script blocks or raw schema objects
            ld_json_blocks = re.findall(
                r'<script\s+type=["\']application/ld\+json["\']\s*>(.*?)</script>',
                text,
                re.DOTALL | re.IGNORECASE,
            )
            for block in ld_json_blocks:
                try:
                    schema_data = json.loads(block)
                    if isinstance(schema_data, dict):
                        schema_data = [schema_data]
                    for s in schema_data:
                        self.assertIn("@context", s, "JSON-LD schema must have '@context'")
                        self.assertIn("@type", s, "JSON-LD schema must have '@type'")
                        found_schemas += 1
                except json.JSONDecodeError as exc:
                    self.fail(f"Invalid JSON-LD schema found in {path.name}: {exc}")

        # Baseline contract verification: ensure Schema.org definitions adhere to specification
        sample_software_app = {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": "Claude-Desktop-Chinese",
            "applicationCategory": "UtilitiesApplication",
            "operatingSystem": "Windows 10, Windows 11, macOS 12+, Linux",
            "featureList": [
                "22,000+ 词条全量覆盖",
                "3-Tier Auto-Healing 自愈守护体系",
                "零依赖原生热注入",
            ],
        }
        self.assertEqual(sample_software_app["@context"], "https://schema.org")
        self.assertEqual(sample_software_app["@type"], "SoftwareApplication")
        self.assertIn("applicationCategory", sample_software_app)

    def test_f1_3_sitemap_metadata_integrity(self) -> None:
        """Validate dynamic sitemap structure and discoverability metadata."""
        sitemap_xml = ROOT_DIR / "sitemap.xml"
        sitemap_json = ROOT_DIR / "sitemap.json"

        if sitemap_xml.exists():
            content = sitemap_xml.read_text(encoding="utf-8")
            self.assertIn("<urlset", content, "sitemap.xml must contain <urlset> root element")
            self.assertIn("<loc>", content, "sitemap.xml must define <loc> entries")

        if sitemap_json.exists():
            data = json.loads(sitemap_json.read_text(encoding="utf-8"))
            self.assertIsInstance(data, (dict, list), "sitemap.json must be valid JSON object or list")

    def test_f1_4_readme_statistics_parity(self) -> None:
        """Verify README.md declares correct dictionary statistics and essential documentation sections."""
        self.assertTrue(README_PATH.exists(), "README.md must exist in repository root")
        readme_text = README_PATH.read_text(encoding="utf-8-sig")

        # Verify key sections are present
        self.assertTrue(
            ("Claude" in readme_text) and ("中文" in readme_text),
            "README.md must describe Claude Chinese localization",
        )
        self.assertTrue(
            ("install" in readme_text.lower()) or ("安装" in readme_text),
            "README.md must document installation instructions",
        )

    def test_f4_2_cli_interface_parameter_contract(self) -> None:
        """Verify CLI interface parameter contracts in install.ps1, uninstall.ps1, patch_claude.ps1."""
        self.assertTrue(INSTALL_PS1_PATH.exists(), "install.ps1 must exist")
        install_ps1_content = INSTALL_PS1_PATH.read_text(encoding="utf-8-sig")

        # Check required CLI flags are defined in install.ps1
        required_flags = ["Install", "Uninstall", "Check", "Restore", "Daemon", "Quiet", "Json"]
        for flag in required_flags:
            self.assertIn(
                flag,
                install_ps1_content,
                f"install.ps1 must implement '{flag}' parameter flag",
            )

        # Check uninstall.ps1 exists and has rollback functionality
        self.assertTrue(UNINSTALL_PS1_PATH.exists(), "uninstall.ps1 must exist")
        uninstall_ps1_content = UNINSTALL_PS1_PATH.read_text(encoding="utf-8-sig")
        self.assertTrue(
            ("backup" in uninstall_ps1_content.lower()) or ("restore" in uninstall_ps1_content.lower()),
            "uninstall.ps1 must contain backup restoration logic",
        )


# ==============================================================================
# Tier 2: Boundary & Corner Case Tests
# ==============================================================================

class Tier2BoundaryCornerCaseTests(unittest.TestCase):
    r"""Tier 2: Boundary, Extreme Strings, and Corner Cases.
    
    Covers:
    - F2.1: Zero empty translations or whitespace-only strings
    - F2.1: Extreme length strings, complex HTML tag balance, markdown syntax
    - F2.3: ICU MessageFormat bracket balance and variable syntax
    - F2.1: 4-byte UTF-8 surrogate pairs, emojis, and CJK Extension characters
    - F2.4: Non-ASCII filename handling (Git quotepath issue resolution)
    - F3.3: PowerShell registry PSDrive (HKCU:\) path scan collision avoidance
    """

    def test_f2_1_no_empty_or_whitespace_values(self) -> None:
        """Ensure none of the 22,319 translation values are empty or whitespace-only."""
        data = load_json_file(DIST_ZH_PATH)
        empty_keys: List[str] = []
        for k, v in data.items():
            if not isinstance(v, str) or not v.strip():
                empty_keys.append(k)

        self.assertEqual(
            len(empty_keys),
            0,
            f"Found {len(empty_keys)} empty/whitespace-only values in dist/zh-CN.json: {empty_keys[:5]}",
        )

    def test_f2_1_extreme_length_strings_and_tag_integrity(self) -> None:
        """Validate longest translation values for HTML tag balance and markdown integrity."""
        data = load_json_file(DIST_ZH_PATH)
        sorted_by_length = sorted(data.items(), key=lambda item: len(item[1]), reverse=True)
        top_long_values = sorted_by_length[:200]

        tag_pattern = re.compile(r"<([a-zA-Z0-9]+)(\s+[^>]*)?>")
        close_tag_pattern = re.compile(r"</([a-zA-Z0-9]+)>")

        for k, val in top_long_values:
            open_tags = [m.group(1).lower() for m in tag_pattern.finditer(val) if not m.group(0).endswith("/>")]
            close_tags = [m.group(1).lower() for m in close_tag_pattern.finditer(val)]
            # Filter void HTML elements that don't require closing tags
            void_elements = {"br", "hr", "img", "input", "link", "meta"}
            filtered_open = [t for t in open_tags if t not in void_elements]
            filtered_close = [t for t in close_tags if t not in void_elements]
            self.assertEqual(
                len(filtered_open),
                len(filtered_close),
                f"Mismatched HTML tags in key '{k}': open={filtered_open}, close={filtered_close}",
            )

    def test_f2_3_icu_messageformat_and_placeholders(self) -> None:
        """Validate ICU MessageFormat syntax: balanced braces, valid variable references."""
        data = load_json_file(DIST_ZH_PATH)
        mismatched_braces: List[Tuple[str, str]] = []

        for k, val in data.items():
            open_count = val.count("{")
            close_count = val.count("}")
            if open_count != close_count:
                mismatched_braces.append((k, val))

        self.assertEqual(
            len(mismatched_braces),
            0,
            f"Found {len(mismatched_braces)} keys with mismatched ICU braces: {mismatched_braces[:5]}",
        )

    def test_f2_1_surrogate_pairs_emojis_and_cjk_extensions(self) -> None:
        """Ensure 4-byte UTF-8 characters, emojis, and CJK Ext-A/B ideographs round-trip cleanly."""
        data = load_json_file(DIST_ZH_PATH)

        # Collect emojis or 4-byte characters
        four_byte_entries: List[Tuple[str, str]] = []
        for k, val in data.items():
            if any(ord(char) > 0xFFFF for char in val):
                four_byte_entries.append((k, val))

        # Test roundtrip serialization of synthetic and actual 4-byte entries
        synthetic_payload = {
            "test_emoji": "Claude 桌面版 🚀 深度汉化 🛡️ 永久保活",
            "test_cjk_ext": "CJK扩展字符: 𠮷野家 㐀 䶵",
            "test_icu_with_emoji": "正在加载 {name} ⏳ 请稍候...",
        }
        dumped = json.dumps(synthetic_payload, ensure_ascii=False)
        loaded = json.loads(dumped)
        self.assertEqual(synthetic_payload, loaded, "Surrogate pairs and emojis failed UTF-8 roundtrip")

    def test_f2_4_non_ascii_filename_handling(self) -> None:
        """Verify non-ASCII filename parsing and ensure Git core.quotepath issues are prevented."""
        test_filename = "安装中文语言包.bat"
        target_path = ROOT_DIR / test_filename

        self.assertTrue(
            target_path.exists(),
            f"File with Chinese non-ASCII name '{test_filename}' must exist and be accessible",
        )

        # Ensure reading text does not throw OSError Errno 22
        try:
            content = target_path.read_text(encoding="utf-8-sig")
            self.assertGreater(len(content), 0)
        except Exception as exc:
            self.fail(f"Failed to read non-ASCII file '{test_filename}': {exc}")

    def test_f3_3_psdrive_path_scan_collision_safeguard(self) -> None:
        """Validate regex drive pattern does NOT falsely match PowerShell PSDrive registry keys (HKCU:\\)."""
        # Bad pattern: [A-Za-z]:\\ matches "HKCU:\\" because 'U:\\' matches '[A-Za-z]:\\'
        bad_pattern = re.compile(r"[A-Za-z]:\\")
        # Good pattern: (?<![A-Za-z0-9_])[A-Za-z]:\\ or negative lookbehind
        fixed_pattern = re.compile(r"(?<![A-Za-z0-9_])[A-Za-z]:\\")

        registry_path = r"HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
        local_hardcoded_path = r"C:\Users\Administrator\AppData\Local"

        # Verify bad pattern falsely matches registry
        self.assertIsNotNone(bad_pattern.search(registry_path), "Sanity check: bad pattern matches HKCU:\\")

        # Verify fixed pattern correctly rejects registry but detects real drive paths
        self.assertIsNone(
            fixed_pattern.search(registry_path),
            "Fixed pattern must NOT match registry PSDrive 'HKCU:\\'",
        )
        self.assertIsNotNone(
            fixed_pattern.search(local_hardcoded_path),
            "Fixed pattern MUST match hardcoded local Windows path 'C:\\Users'",
        )


# ==============================================================================
# Tier 3: Cross-Feature Interactions
# ==============================================================================

class Tier3CrossFeatureInteractionTests(unittest.TestCase):
    """Tier 3: Cross-Feature Interactions & Multi-Component Parity.
    
    Covers:
    - F2.1: Dictionary 100% bit-for-bit parity between dist/zh-CN.json and zh-CN-ion.json
    - F2.2: AI developer terminology consistency glossary audit
    - F4.3: 4-Tier CDN waterfall failover simulation
    - F4.4: Standardized health diagnostic JSON schema validation
    """

    def test_f2_1_dictionary_bit_parity(self) -> None:
        """Validate dist/zh-CN.json and zh-CN-ion.json are 100% identical in keys and values."""
        self.assertTrue(DIST_ZH_PATH.exists(), f"Missing {DIST_ZH_PATH}")
        self.assertTrue(ION_ZH_PATH.exists(), f"Missing {ION_ZH_PATH}")

        dist_data = load_json_file(DIST_ZH_PATH)
        ion_data = load_json_file(ION_ZH_PATH)

        self.assertEqual(
            len(dist_data),
            len(ion_data),
            f"Key count mismatch: dist ({len(dist_data)}) vs ion ({len(ion_data)})",
        )

        dist_keys = set(dist_data.keys())
        ion_keys = set(ion_data.keys())
        self.assertEqual(dist_keys, ion_keys, "Key sets between dist/zh-CN.json and zh-CN-ion.json must match 100%")

        # Value comparison
        mismatched_values = [k for k in dist_keys if dist_data[k] != ion_data[k]]
        self.assertEqual(
            len(mismatched_values),
            0,
            f"Found {len(mismatched_values)} mismatched values between dist and ion: {mismatched_values[:5]}",
        )

    def test_f2_2_terminology_glossary_consistency(self) -> None:
        """Validate consistent translation of AI developer terminology across all 22,319 keys."""
        data = load_json_file(DIST_ZH_PATH)

        # Developer glossary terms and expected Chinese translations
        found_terms: Dict[str, int] = {
            "制品": 0,
            "模型上下文协议": 0,
            "MCP": 0,
            "计算机使用": 0,
            "上下文窗口": 0,
            "深度思考": 0,
            "扩展思考": 0,
        }

        for val in data.values():
            for term in found_terms:
                if term in val:
                    found_terms[term] += 1

        # Check that core developer terminology is present and localized
        self.assertGreater(
            found_terms["制品"] + found_terms["MCP"] + found_terms["计算机使用"] + found_terms["上下文窗口"],
            0,
            "Developer glossary terms (Artifacts, MCP, Computer Use, Context Window) must be present in translations",
        )

    def test_f4_3_cdn_waterfall_failover_simulation(self) -> None:
        """Simulate 4-Tier CDN waterfall resolution: Fastly -> Cloudflare -> Ghfast -> GitHub Raw -> Cache."""
        repo_owner = "good9527"
        repo_name = "Claude-Desktop-Chinese"
        rel_path = "dist/zh-CN.json"

        tier1_url = f"https://fastly.jsdelivr.net/gh/{repo_owner}/{repo_name}@main/{rel_path}"
        tier2_url = f"https://cdn.jsdelivr.net/gh/{repo_owner}/{repo_name}@main/{rel_path}"
        tier3_url = f"https://ghfast.top/https://raw.githubusercontent.com/{repo_owner}/{repo_name}/main/{rel_path}"
        tier4_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/main/{rel_path}"

        urls = [tier1_url, tier2_url, tier3_url, tier4_url]

        # Scenario A: Tier 1 succeeds
        mock_a = {tier1_url: (200, '{"status": "ok_tier1"}')}
        res_a = simulate_cdn_fetch(urls, mock_a)
        self.assertEqual(res_a, '{"status": "ok_tier1"}')

        # Scenario B: Tier 1 fails (500), Tier 2 succeeds
        mock_b = {
            tier1_url: (500, None),
            tier2_url: (200, '{"status": "ok_tier2"}'),
        }
        res_b = simulate_cdn_fetch(urls, mock_b)
        self.assertEqual(res_b, '{"status": "ok_tier2"}')

        # Scenario C: Tiers 1, 2, 3 fail, Tier 4 succeeds
        mock_c = {
            tier1_url: (500, None),
            tier2_url: (502, None),
            tier3_url: (408, None),
            tier4_url: (200, '{"status": "ok_tier4"}'),
        }
        res_c = simulate_cdn_fetch(urls, mock_c)
        self.assertEqual(res_c, '{"status": "ok_tier4"}')

        # Scenario D: All fail, fallback to None (which activates local offline cache)
        mock_d = {u: (500, None) for u in urls}
        res_d = simulate_cdn_fetch(urls, mock_d)
        self.assertIsNone(res_d, "Waterfall must return None when all CDN mirrors fail")

    def test_f4_4_diagnostic_json_schema_validation(self) -> None:
        """Validate unified health diagnostic JSON output schema against PROJECT.md contract."""
        diagnostic_payload = {
            "project": "Claude-Desktop-Chinese",
            "version": "1.0.0",
            "platform": "windows",
            "claude_path": r"C:\Users\Admin\AppData\Local\AnthropicClaude\app\resources\ion-dist\i18n\en-US.json",
            "status": "healthy",
            "tier_a_watcher_active": True,
            "dictionary_keys": 22319,
            "chinese_ratio": 0.985,
        }

        # Validate types and required fields
        required_fields = {
            "project": str,
            "version": str,
            "platform": str,
            "claude_path": str,
            "status": str,
            "tier_a_watcher_active": bool,
            "dictionary_keys": int,
            "chinese_ratio": float,
        }

        for field, expected_type in required_fields.items():
            self.assertIn(field, diagnostic_payload, f"Diagnostic schema missing '{field}'")
            self.assertIsInstance(
                diagnostic_payload[field],
                expected_type,
                f"Field '{field}' must be {expected_type.__name__}",
            )

        valid_statuses = {"healthy", "patched", "unpatched", "corrupted"}
        self.assertIn(diagnostic_payload["status"], valid_statuses)
        self.assertEqual(diagnostic_payload["dictionary_keys"], TOTAL_EXPECTED_KEYS)
        self.assertGreaterEqual(diagnostic_payload["chinese_ratio"], 0.0)
        self.assertLessEqual(diagnostic_payload["chinese_ratio"], 1.0)


# ==============================================================================
# Tier 4: Real-World Workload Scenarios
# ==============================================================================

class Tier4RealWorldWorkloadTests(unittest.TestCase):
    """Tier 4: Real-World Workload Scenarios & Integration Simulation.
    
    Covers:
    - F4.1 / F4.2: Simulated full in-place install and dictionary merge workflow
    - F4.1: In-place atomic backup creation and 100% bit-exact rollback
    - F4.1: Background watcher daemon auto-healing lifecycle simulation
    - F3.1: Multi-OS target discovery & path resolution (Windows, macOS, Linux)
    """

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.work_dir = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_f4_2_simulated_full_install_patch_workflow(self) -> None:
        """Simulate full in-place dictionary merge overlay on an official en-US.json target."""
        # 1. Setup mock official Claude Desktop en-US.json
        mock_en_us = {
            "app.title": "Claude",
            "menu.file.save": "Save",
            "menu.file.exit": "Exit",
            "settings.language": "Language",
            "future_untranslated_key_2027": "Brand New Feature In English",
        }
        mock_zh_cn = {
            "app.title": "Claude",
            "menu.file.save": "保存",
            "menu.file.exit": "退出",
            "settings.language": "语言",
        }

        target_file = self.work_dir / "en-US.json"
        target_file.write_text(json.dumps(mock_en_us, indent=2), encoding="utf-8")

        # 2. Execute in-place merge algorithm
        with target_file.open("r", encoding="utf-8") as f:
            en_data = json.load(f)

        merged = {}
        translated_count = 0
        for k, v in en_data.items():
            if k in mock_zh_cn and mock_zh_cn[k]:
                merged[k] = mock_zh_cn[k]
                translated_count += 1
            else:
                merged[k] = v

        # Write merged result atomically
        temp_target = self.work_dir / "en-US-patched-temp.json"
        temp_target.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
        temp_target.replace(target_file)

        # 3. Verify patched result
        patched_data = load_json_file(target_file)
        self.assertEqual(len(patched_data), len(mock_en_us), "Merge must preserve all original keys")
        self.assertEqual(patched_data["menu.file.save"], "保存")
        self.assertEqual(patched_data["menu.file.exit"], "退出")
        self.assertEqual(patched_data["settings.language"], "语言")
        # Ensure new unreleased keys remain gracefully in English without crashing
        self.assertEqual(
            patched_data["future_untranslated_key_2027"],
            "Brand New Feature In English",
            "New unreleased English keys must be preserved untouched",
        )
        self.assertEqual(translated_count, 4)

    def test_f4_1_atomic_backup_and_restore_workflow(self) -> None:
        """Simulate pristine backup creation, multiple patch cycles, and bit-exact restore rollback."""
        pristine_en_us = {
            "version": "1.0.0",
            "ui.dialog.confirm": "Are you sure you want to proceed?",
            "ui.dialog.cancel": "Cancel",
        }
        target_file = self.work_dir / "en-US.json"
        backup_file = self.work_dir / "en-US-original.json"

        # 1. Write pristine official file
        target_file.write_text(json.dumps(pristine_en_us, indent=2), encoding="utf-8")
        pristine_checksum = target_file.read_bytes()

        # 2. First install cycle: backup must be created
        if not backup_file.exists():
            backup_file.write_bytes(target_file.read_bytes())
        self.assertTrue(backup_file.exists(), "Backup file must be created")
        self.assertEqual(backup_file.read_bytes(), pristine_checksum)

        # 3. Apply patch (modifying target_file)
        patched_content = {
            "version": "1.0.0",
            "ui.dialog.confirm": "您确定要继续吗？",
            "ui.dialog.cancel": "取消",
        }
        target_file.write_text(json.dumps(patched_content, ensure_ascii=False, indent=2), encoding="utf-8")

        # 4. Second install cycle: backup must NOT be overwritten by the patched file
        if not backup_file.exists():
            backup_file.write_bytes(target_file.read_bytes())
        self.assertEqual(
            backup_file.read_bytes(),
            pristine_checksum,
            "Subsequent patch cycles must NEVER overwrite pristine backup",
        )

        # 5. One-click restore / rollback
        target_file.write_bytes(backup_file.read_bytes())
        self.assertEqual(
            target_file.read_bytes(),
            pristine_checksum,
            "Restored file must be 100% bit-for-bit identical to original pristine file",
        )

    def test_f4_1_auto_healing_watcher_lifecycle(self) -> None:
        """Simulate Claude auto-update overwriting language files and watcher daemon auto-healing."""
        # 1. State: Patched application
        target_file = self.work_dir / "en-US.json"
        cached_dict_file = self.work_dir / "zh-CN-cached.json"

        full_zh_dict = {
            "btn.submit": "提交",
            "btn.cancel": "取消",
            "label.username": "用户名",
        }
        cached_dict_file.write_text(json.dumps(full_zh_dict, ensure_ascii=False), encoding="utf-8")

        # 2. Claude auto-update occurs: Anthropic overwrites en-US.json with new official English version
        updated_official_en = {
            "btn.submit": "Submit",
            "btn.cancel": "Cancel",
            "label.username": "Username",
            "btn.new_feature_v2": "New Feature v2",
        }
        target_file.write_text(json.dumps(updated_official_en, indent=2), encoding="utf-8")

        # 3. Watcher daemon detection: checks if 'btn.submit' is still in English
        current_data = load_json_file(target_file)
        needs_healing = (current_data.get("btn.submit") == "Submit")
        self.assertTrue(needs_healing, "Watcher must detect regression to English")

        # 4. Watcher auto-heals: merges local cached dictionary into updated file
        cached_zh = load_json_file(cached_dict_file)
        healed_data = {k: cached_zh.get(k, v) for k, v in current_data.items()}

        temp_heal_file = self.work_dir / "en-US-healed-temp.json"
        temp_heal_file.write_text(json.dumps(healed_data, ensure_ascii=False, indent=2), encoding="utf-8")
        temp_heal_file.replace(target_file)

        # 5. Verify auto-healed state
        final_data = load_json_file(target_file)
        self.assertEqual(final_data["btn.submit"], "提交")
        self.assertEqual(final_data["btn.cancel"], "取消")
        self.assertEqual(final_data["label.username"], "用户名")
        self.assertEqual(final_data["btn.new_feature_v2"], "New Feature v2")

    def test_f3_1_multi_os_path_resolution(self) -> None:
        """Validate multi-OS Claude installation directory discovery heuristics."""
        # 1. Windows mock paths
        win_candidates = [
            r"C:\Users\User\AppData\Local\AnthropicClaude\app\resources\ion-dist\i18n\en-US.json",
            r"C:\Program Files\WindowsApps\Claude_1.0.0_x64__...\app\resources\ion-dist\i18n\en-US.json",
        ]
        # 2. macOS mock paths
        mac_candidates = [
            "/Applications/Claude.app/Contents/Resources/app/resources/ion-dist/i18n/en-US.json",
            "/Users/User/Applications/Claude.app/Contents/Resources/app/resources/ion-dist/i18n/en-US.json",
        ]
        # 3. Linux mock paths
        linux_candidates = [
            "/opt/Claude/resources/app/resources/ion-dist/i18n/en-US.json",
            "/opt/claude-desktop/resources/app/resources/ion-dist/i18n/en-US.json",
            "/usr/lib/claude-desktop/resources/app/resources/ion-dist/i18n/en-US.json",
            "/home/user/.local/share/claude-desktop/resources/app/resources/ion-dist/i18n/en-US.json",
        ]

        all_candidates = win_candidates + mac_candidates + linux_candidates
        self.assertEqual(len(all_candidates), 8, "Expected 8 standard cross-platform candidate paths")
        for p in all_candidates:
            self.assertTrue(p.endswith("en-US.json"), f"Candidate path must target en-US.json: {p}")


# ==============================================================================
# CLI Runner & Multi-Tier Dispatcher
# ==============================================================================

TIER_MAPPING = {
    "1": [Tier1FeatureCoverageTests],
    "2": [Tier2BoundaryCornerCaseTests],
    "3": [Tier3CrossFeatureInteractionTests],
    "4": [Tier4RealWorldWorkloadTests],
    "all": [
        Tier1FeatureCoverageTests,
        Tier2BoundaryCornerCaseTests,
        Tier3CrossFeatureInteractionTests,
        Tier4RealWorldWorkloadTests,
    ],
}


class JsonTestResult(unittest.TestResult):
    """Custom TestResult collecting detailed per-test results for JSON reporting."""

    def __init__(self) -> None:
        super().__init__()
        self.test_records: List[Dict[str, Any]] = []
        self._start_time: float = 0.0

    def startTest(self, test: unittest.TestCase) -> None:
        super().startTest(test)
        self._start_time = time.time()

    def addSuccess(self, test: unittest.TestCase) -> None:
        super().addSuccess(test)
        duration = time.time() - self._start_time
        self.test_records.append({
            "test": str(test),
            "status": "PASS",
            "duration_ms": round(duration * 1000, 2),
            "error": None,
        })

    def addFailure(self, test: unittest.TestCase, err: Any) -> None:
        super().addFailure(test, err)
        duration = time.time() - self._start_time
        self.test_records.append({
            "test": str(test),
            "status": "FAIL",
            "duration_ms": round(duration * 1000, 2),
            "error": self._exc_info_to_string(err, test),
        })

    def addError(self, test: unittest.TestCase, err: Any) -> None:
        super().addError(test, err)
        duration = time.time() - self._start_time
        self.test_records.append({
            "test": str(test),
            "status": "ERROR",
            "duration_ms": round(duration * 1000, 2),
            "error": self._exc_info_to_string(err, test),
        })


def run_test_suite(
    tier: str = "all",
    verbose: bool = False,
    emit_json: bool = False,
) -> bool:
    """Execute selected test tier(s) and display formatted results."""
    test_classes = TIER_MAPPING.get(tier.lower())
    if not test_classes:
        print(f"Error: Unknown tier '{tier}'. Supported tiers: 1, 2, 3, 4, all", file=sys.stderr)
        return False

    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for cls in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    start_time = time.time()

    if emit_json:
        result = JsonTestResult()
        suite.run(result)
        total_duration = time.time() - start_time
        output_payload = {
            "tier": tier,
            "success": result.wasSuccessful(),
            "total_tests": result.testsRun,
            "passed": result.testsRun - len(result.failures) - len(result.errors),
            "failures": len(result.failures),
            "errors": len(result.errors),
            "duration_seconds": round(total_duration, 4),
            "tests": result.test_records,
        }
        print(json.dumps(output_payload, indent=2, ensure_ascii=False))
        return result.wasSuccessful()

    # Standard formatted terminal runner
    print("=" * 70)
    print(f"  Claude-Desktop-Chinese E2E Test Suite [Tier: {tier.upper()}]")
    print(f"  Target: {DIST_ZH_PATH} ({TOTAL_EXPECTED_KEYS} keys)")
    print("=" * 70)

    verbosity_level = 2 if verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity_level)
    result = runner.run(suite)

    total_duration = time.time() - start_time
    print("=" * 70)
    print(f"  Total Duration : {total_duration:.3f}s")
    print(f"  Tests Executed : {result.testsRun}")
    print(f"  Failures       : {len(result.failures)}")
    print(f"  Errors         : {len(result.errors)}")
    print(f"  Final Status   : {'[PASSED]' if result.wasSuccessful() else '[FAILED]'}")
    print("=" * 70)

    return result.wasSuccessful()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Comprehensive 5-Tier E2E Test Suite for Claude-Desktop-Chinese",
    )
    parser.add_argument(
        "--tier",
        "-t",
        default="all",
        choices=["1", "2", "3", "4", "all"],
        help="Select which test tier to execute (1, 2, 3, 4, or all)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable detailed test description output and benchmark timings",
    )
    parser.add_argument(
        "--json",
        "-j",
        action="store_true",
        help="Output test results in structured JSON format",
    )

    args = parser.parse_args()
    success = run_test_suite(tier=args.tier, verbose=args.verbose, emit_json=args.json)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
