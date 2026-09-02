#!/usr/bin/env python3
"""Validate release assets for the Claude Desktop Chinese patch project."""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE_EN = ROOT / "local" / "en-US.json"
RELEASE_ZH = ROOT / "dist" / "zh-CN.json"
SOURCE_ZH = ROOT / "zh-CN-ion.json"
POWERSHELL_SCRIPTS = (
    ROOT / "install.ps1",
    ROOT / "uninstall.ps1",
    ROOT / "install-old-working.ps1",
    ROOT / "patch_claude.ps1",
    ROOT / "watcher" / "watcher.ps1",
)
PYTHON_SCRIPTS = (
    ROOT / "create_hacked_enus.py",
    ROOT / "merge.py",
    ROOT / "merge2.py",
    ROOT / "scripts" / "validate.py",
    ROOT / "split_chunks.py",
    ROOT / "translate.py",
    ROOT / "translate2.py",
    ROOT / "translate3.py",
    ROOT / "win-automation-mcp" / "server.py",
    ROOT / "win-automation-mcp" / "test_server.py",
)
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
    zh_data = load_json(RELEASE_ZH)
    source_zh_data = load_json(SOURCE_ZH)

    if zh_data != source_zh_data:
        fail("dist/zh-CN.json must match zh-CN-ion.json")

    chinese_values = sum(1 for value in zh_data.values() if has_cjk(value))
    chinese_ratio = chinese_values / len(zh_data)
    if chinese_ratio < MIN_CHINESE_RATIO:
        fail(f"Chinese-looking value ratio is {chinese_ratio:.2%}, expected at least {MIN_CHINESE_RATIO:.0%}")

    empty_values = [key for key, value in zh_data.items() if isinstance(value, str) and not value.strip()]
    if empty_values:
        sample = ", ".join(empty_values[:10])
        fail(f"translation file contains empty string values: {sample}")

    print("[OK] JSON assets")
    print(f"     zh-CN release keys:   {len(zh_data)}")
    print(f"     values with Chinese:  {chinese_values} ({chinese_ratio:.2%})")

    if REFERENCE_EN.exists():
        en_data = load_json(REFERENCE_EN)
        en_keys = set(en_data)
        zh_keys = set(zh_data)
        matched_keys = en_keys & zh_keys
        extra_keys = zh_keys - en_keys
        missing_keys = en_keys - zh_keys

        coverage = len(matched_keys) / len(en_keys)
        if coverage < MIN_COVERAGE:
            fail(f"translation coverage is {coverage:.2%}, expected at least {MIN_COVERAGE:.0%}")

        print(f"     en-US reference keys: {len(en_data)}")
        print(f"     matched keys:         {len(matched_keys)} ({coverage:.2%})")
        print(f"     missing reference:    {len(missing_keys)}")
        print(f"     extra release keys:   {len(extra_keys)}")
    else:
        print("     en-US reference:      skipped (place a local copy at local/en-US.json for coverage checks)")


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
    ps_cmd = shutil.which("pwsh") or shutil.which("powershell")
    if not ps_cmd:
        print("[SKIP] PowerShell syntax check (neither pwsh nor powershell found in PATH)")
        return

    for script in POWERSHELL_SCRIPTS:
        if not script.exists():
            continue
        escaped_path = str(script.resolve()).replace("'", "''")
        cmd = (
            f"$tokens = $null; $errors = $null; "
            f"$null = [System.Management.Automation.Language.Parser]::ParseFile('{escaped_path}', [ref]$tokens, [ref]$errors); "
            f"if ($errors.Count) {{ $errors | ForEach-Object {{ Write-Error $_.Message }}; exit 1 }}"
        )
        res = subprocess.run(
            [ps_cmd, "-NoProfile", "-Command", cmd],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if res.returncode != 0:
            fail(f"PowerShell syntax error in {script.relative_to(ROOT)}: {res.stderr}")
        print(f"[OK] PowerShell syntax: {script.relative_to(ROOT)}")


def validate_python_syntax() -> None:
    for script in PYTHON_SCRIPTS:
        if not script.exists():
            continue
        text = script.read_text(encoding="utf-8-sig")
        try:
            ast.parse(text, filename=str(script))
        except SyntaxError as exc:
            fail(f"Python syntax error in {script.relative_to(ROOT)}: {exc}")
        print(f"[OK] Python syntax: {script.relative_to(ROOT)}")


def validate_no_local_absolute_paths() -> None:
    path_patterns = [
        re.compile(r"(?<![A-Za-z0-9_])[A-Za-z]:\\"),
        re.compile(r"\\\\Users\\\\", re.IGNORECASE),
        re.compile(r"AppData\\Local\\Packages\\Claude_", re.IGNORECASE),
    ]
    scanned_suffixes = {".bat", ".md", ".ps1", ".py", ".toml", ".yml"}
    allowed_paths = {
        ROOT / "README.md",
        ROOT / "scripts" / "validate.py",
        ROOT / "SEO_GEO_INDEX.md",
        ROOT / "PROJECT.md",
        ROOT / ".github" / "pull_request_template.md",
    }

    for path in tracked_text_files():
        if "win-automation-mcp" in path.parts or "tests" in path.parts:
            continue
        if path.suffix.lower() not in scanned_suffixes:
            continue
        if path in allowed_paths:
            continue
        text = read_text_or_none(path)
        if text is None:
            continue
        for pattern in path_patterns:
            if pattern.search(text):
                fail(f"local absolute path found in {path.relative_to(ROOT)}")

    print("[OK] local absolute path scan")


def tracked_text_files() -> list[Path]:
    result = subprocess.run(
        ["git", "-c", "core.quotepath=false", "ls-files"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=True,
    )
    paths: list[Path] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        path = ROOT / line
        if path.suffix.lower() in {".png", ".pyc"}:
            continue
        paths.append(path)
    return paths


def read_text_or_none(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        return None


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
    validate_no_local_absolute_paths()
    validate_python_syntax()
    if not args.skip_powershell:
        validate_powershell_syntax()


if __name__ == "__main__":
    main()
