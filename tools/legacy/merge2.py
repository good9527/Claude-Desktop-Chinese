#!/usr/bin/env python3
"""Merge translated chunks with light JSON repair for malformed quote output."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_CHUNK_DIR = ROOT / "chunks"
DEFAULT_OUTPUT = ROOT / "zh-CN-ion.json"


def fix_json_quotes(content: str) -> str:
    """Replace likely unescaped inner quotes in JSON string values."""
    fixed: list[str] = []
    for line in content.splitlines():
        match = re.match(r'^(\s*"[^"]+":\s*")(.*)("[\s,]*$)', line)
        if not match:
            fixed.append(line)
            continue

        prefix, value, suffix = match.groups()
        if '"' not in value:
            fixed.append(line)
            continue

        new_value: list[str] = []
        opening = True
        for char in value:
            if char == '"':
                new_value.append("“" if opening else "”")
                opening = not opening
            else:
                new_value.append(char)
        fixed.append(prefix + "".join(new_value) + suffix)

    return "\n".join(fixed)


def extract_kv_pairs(content: str) -> dict[str, str]:
    """Extract simple JSON string key/value pairs as a last-resort fallback."""
    result: dict[str, str] = {}
    for match in re.finditer(r'"([^"]+)":\s*"((?:[^"\\]|\\.)*)"\s*[,}\n]', content):
        key, value = match.group(1), match.group(2)
        result[key] = value.replace('\\"', '"').replace("\\n", "\n").replace("\\t", "\t")
    return result


def load_chunk(path: Path) -> dict[str, object]:
    content = path.read_text(encoding="utf-8-sig")

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        fixed = fix_json_quotes(content)
        try:
            data = json.loads(fixed)
        except json.JSONDecodeError as exc:
            print(f"  [WARN] {path.name} still has JSON errors after quote repair: {exc}")
            data = extract_kv_pairs(content)

    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def write_json(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def has_cjk(value: object) -> bool:
    return isinstance(value, str) and any("\u4e00" <= char <= "\u9fff" for char in value)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunk-dir", type=Path, default=DEFAULT_CHUNK_DIR, help="directory containing *_zh.json files")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="merged zh-CN output file")
    args = parser.parse_args()

    files = sorted(args.chunk_dir.glob("*_zh.json"))
    if not files:
        raise SystemExit(f"No translated chunks found in {args.chunk_dir}")

    merged: dict[str, object] = {}
    duplicate_keys: set[str] = set()

    for path in files:
        data = load_chunk(path)
        duplicate_keys.update(set(merged) & set(data))
        merged.update(data)
        print(f"  {path.name}: {len(data)} keys")

    write_json(args.output, merged)

    chinese = sum(1 for value in merged.values() if has_cjk(value))
    print(f"\nTotal keys: {len(merged)}")
    print(f"Keys with Chinese: {chinese}/{len(merged)} ({chinese * 100 // len(merged)}%)")
    print(f"Duplicate keys overwritten: {len(duplicate_keys)}")
    print(f"Output: {args.output}")
    print(f"Size: {args.output.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
