#!/usr/bin/env python3
"""Validate release assets for the Claude Desktop Chinese patch project."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE_EN = ROOT / "en-US-957k.json"
RELEASE_ZH = ROOT / "dist" / "zh-CN.json"
SOURCE_ZH = ROOT / "zh-CN-ion.json"
POWERSHELL_SCRIPTS = (ROOT / "install.ps1", ROOT / "uninstall.ps1")
MIN_COVERAGE = 0.98
MIN_CHINESE_RATIO = 0.90


def fail(message: str) -> None:
    print(f"[FAIL] {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> dict[str, object]:
    try:
        with path.open("r", encoding="utf-8-sig") as fh:
            data = json.load(fh)
    except Exception as exc:  # noqa: BLE001 - show concise validation failure
        fail(f"{path.relative_to(ROOT)} is not valid JSON: {exc}")

    if not isinstance(data, dict):
        fail(f"{path.relative_to(ROOT)} must contain a JSON object")
    return data


def has_cjk(value: object) -> bool:
    return isinstance(value, str) and any("\u4e00" <= char <= "\u9fff" for char in value)


def validate_json_assets() -> None:
    en_data = load_json(REFERENCE_EN)
    zh_data = load_json(RELEASE_ZH)
    source_zh_data = load_json(SOURCE_ZH)

    if zh_data != source_zh_data:
        fail("dist/zh-CN.json must match zh-CN-ion.json")

    en_keys = set(en_data)
    zh_keys = set(zh_data)
    matched_keys = en_keys & zh_keys
    extra_keys = zh_keys - en_keys
    missing_keys = en_keys - zh_keys

    coverage = len(matched_keys) / len(en_keys)
    if coverage < MIN_COVERAGE:
        fail(f"translation coverage is {coverage:.2%}, expected at least {MIN_COVERAGE:.0%}")

    chinese_values = sum(1 for value in zh_data.values() if has_cjk(value))
    chinese_ratio = chinese_values / len(zh_data)
    if chinese_ratio < MIN_CHINESE_RATIO:
        fail(f"Chinese-looking value ratio is {chinese_ratio:.2%}, expected at least {MIN_CHINESE_RATIO:.0%}")

    empty_values = [key for key, value in zh_data.items() if isinstance(value, str) and not value.strip()]
    if empty_values:
        sample = ", ".join(empty_values[:10])
        fail(f"translation file contains empty string values: {sample}")

    print("[OK] JSON assets")
    print(f"     en-US reference keys: {len(en_data)}")
    print(f"     zh-CN release keys:   {len(zh_data)}")
    print(f"     matched keys:         {len(matched_keys)} ({coverage:.2%})")
    print(f"     missing reference:    {len(missing_keys)}")
    print(f"     extra release keys:   {len(extra_keys)}")
    print(f"     values with Chinese:  {chinese_values} ({chinese_ratio:.2%})")


def validate_readme_stats() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    zh_data = load_json(RELEASE_ZH)

    declared_count = re.search(r"dist/zh-CN\.json`\s*\|\s*中文翻译字典\(([\d,]+)\s*条", readme)
    if declared_count:
        count = int(declared_count.group(1).replace(",", ""))
        if count != len(zh_data):
            fail(f"README declares {count} translations, but dist/zh-CN.json has {len(zh_data)}")

    print("[OK] README statistics")


def validate_powershell_syntax() -> None:
    for script in POWERSHELL_SCRIPTS:
        text = script.read_text(encoding="utf-8-sig")
        subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "$tokens = $null; $errors = $null; "
                "$null = [System.Management.Automation.Language.Parser]::ParseInput($input, [ref]$tokens, [ref]$errors); "
                "if ($errors.Count) { $errors | ForEach-Object { Write-Error $_.Message }; exit 1 }",
            ],
            input=text,
            text=True,
            check=True,
        )
        print(f"[OK] PowerShell syntax: {script.relative_to(ROOT)}")


def validate_no_obvious_secrets() -> None:
    secret_patterns = [
        re.compile(r"ghp_[A-Za-z0-9_]{30,}"),
        re.compile(r"github_pat_[A-Za-z0-9_]{30,}"),
        re.compile(r"sk-[A-Za-z0-9_-]{32,}"),
    ]
    scan_files = [
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and "__pycache__" not in path.parts
        and path.suffix.lower() not in {".png", ".pyc"}
    ]

    for path in scan_files:
        try:
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            continue
        for pattern in secret_patterns:
            if pattern.search(text):
                fail(f"possible secret found in {path.relative_to(ROOT)}")

    print("[OK] secret pattern scan")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-powershell", action="store_true", help="skip PowerShell parser checks")
    args = parser.parse_args()

    validate_json_assets()
    validate_readme_stats()
    validate_no_obvious_secrets()
    if not args.skip_powershell:
        validate_powershell_syntax()


if __name__ == "__main__":
    main()
