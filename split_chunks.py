#!/usr/bin/env python3
"""Split a Claude Desktop en-US JSON file into translation chunks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_SOURCE = ROOT / "en-US-957k.json"
DEFAULT_CHUNK_DIR = ROOT / "chunks"


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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="source en-US JSON file")
    parser.add_argument("--chunk-dir", type=Path, default=DEFAULT_CHUNK_DIR, help="directory for chunk files")
    parser.add_argument("--chunk-size", type=int, default=500, help="number of keys per chunk")
    args = parser.parse_args()

    if args.chunk_size <= 0:
        raise SystemExit("--chunk-size must be greater than zero")

    data = load_json(args.source)
    items = list(data.items())
    args.chunk_dir.mkdir(parents=True, exist_ok=True)

    print(f"Source: {args.source}")
    print(f"Total keys: {len(items)}")

    chunk_count = 0
    for index in range(0, len(items), args.chunk_size):
        chunk = dict(items[index : index + args.chunk_size])
        chunk_path = args.chunk_dir / f"chunk_{chunk_count:03d}.json"
        write_json(chunk_path, chunk)
        chunk_count += 1

    print(f"Split into {chunk_count} chunks of up to {args.chunk_size} keys")
    print(f"Chunks written to: {args.chunk_dir}")


if __name__ == "__main__":
    main()
