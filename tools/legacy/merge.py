#!/usr/bin/env python3
"""Merge translated chunk JSON files into zh-CN-ion.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_CHUNK_DIR = ROOT / "chunks"
DEFAULT_OUTPUT = ROOT / "zh-CN-ion.json"


def load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8-sig") as fh:
        data = json.load(fh)
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
        data = load_json(path)
        duplicate_keys.update(set(merged) & set(data))
        merged.update(data)
        print(f"  Merged {path.name}: {len(data)} keys")

    write_json(args.output, merged)

    chinese = sum(1 for value in merged.values() if has_cjk(value))
    print(f"\nTotal keys: {len(merged)}")
    print(f"Keys with Chinese: {chinese}/{len(merged)} ({chinese * 100 // len(merged)}%)")
    print(f"Duplicate keys overwritten: {len(duplicate_keys)}")
    print(f"Output: {args.output}")
    print(f"Size: {args.output.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
