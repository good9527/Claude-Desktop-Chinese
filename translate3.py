#!/usr/bin/env python3
"""Translate en-US strings to zh-CN using the public Google Translate endpoint."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import threading
import time
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_SOURCE = ROOT / "local" / "en-US.json"
DEFAULT_OUTPUT = ROOT / "zh-CN-ion.json"
DEFAULT_CHECKPOINT = ROOT / "zh-CN-checkpoint.json"


def load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8-sig") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def write_json(path: Path, data: dict[object, object], *, indent: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=indent)
        fh.write("\n")


def skip(value: object) -> bool:
    if not isinstance(value, str) or len(value.strip()) <= 2:
        return True
    return bool(re.match(r"^[\s{}\[\]<>/\-\d.:]+$", value))


def protect(text: str) -> tuple[str, dict[str, str]]:
    placeholders: dict[str, str] = {}
    counter = 0

    def replace(pattern: str, value: str) -> str:
        nonlocal counter
        for match in list(re.finditer(pattern, value)):
            key = f"PH{counter}X"
            placeholders[key] = match.group(0)
            value = value.replace(match.group(0), key, 1)
            counter += 1
        return value

    text = replace(r"\{[^}]+\}", text)
    text = replace(r"</?[a-zA-Z][^>]*>", text)
    text = replace(r"https?://\S+", text)
    text = replace(r"`[^`]+`", text)
    return text, placeholders


def restore(text: str, placeholders: dict[str, str]) -> str:
    for key, value in placeholders.items():
        text = text.replace(key, value)
    return text


def translate_text(text: str, timeout: int) -> str | None:
    try:
        protected, placeholders = protect(text)
        params = urllib.parse.urlencode(
            {
                "client": "gtx",
                "sl": "en",
                "tl": "zh-CN",
                "dt": "t",
                "q": protected,
            }
        )
        request = urllib.request.Request(
            f"https://translate.googleapis.com/translate_a/single?{params}",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if payload and payload[0]:
            translated = "".join(part[0] for part in payload[0] if part[0])
            return restore(translated, placeholders)
    except Exception:
        return None
    return None


def has_cjk(value: object) -> bool:
    return isinstance(value, str) and any("\u4e00" <= char <= "\u9fff" for char in value)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="source en-US JSON file")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="translated zh-CN output file")
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT, help="checkpoint JSON file")
    parser.add_argument("--workers", type=int, default=8, help="concurrent translation workers")
    parser.add_argument("--timeout", type=int, default=10, help="HTTP timeout in seconds")
    parser.add_argument("--save-interval", type=int, default=500, help="checkpoint save interval")
    args = parser.parse_args()

    if args.workers <= 0:
        raise SystemExit("--workers must be greater than zero")

    data = load_json(args.source)
    keys = list(data.keys())
    values = list(data.values())
    total = len(values)

    checkpoint: dict[int, object] = {}
    if args.checkpoint.exists():
        raw_checkpoint = load_json(args.checkpoint)
        checkpoint = {int(key): value for key, value in raw_checkpoint.items()}
        print(f"Resuming from checkpoint: {len(checkpoint)} entries", flush=True)

    translated: dict[int, object] = dict(checkpoint)
    to_translate: list[tuple[int, str]] = []

    for index, value in enumerate(values):
        if index in translated:
            continue
        if skip(value):
            translated[index] = value
        elif isinstance(value, str):
            to_translate.append((index, value))

    print(f"Source: {args.source}", flush=True)
    print(f"Total keys: {total}", flush=True)
    print(f"To translate: {len(to_translate)} | Already done: {len(checkpoint)}", flush=True)
    print(f"Starting {args.workers} workers...", flush=True)

    lock = threading.Lock()
    done_count = len(translated)
    error_count = 0

    def process_item(item: tuple[int, str]) -> None:
        nonlocal done_count, error_count
        index, text = item
        result = translate_text(text, timeout=args.timeout)
        with lock:
            translated[index] = result if result else text
            if not result:
                error_count += 1
            done_count += 1
            if done_count % 100 == 0 or done_count == total:
                percent = done_count * 100 // total
                print(f"\rProgress: {done_count}/{total} ({percent}%) | Errors: {error_count}", end="", flush=True)
            if done_count % args.save_interval == 0:
                write_json(args.checkpoint, translated)
        time.sleep(0.05)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(process_item, item) for item in to_translate]
        concurrent.futures.wait(futures)

    print("", flush=True)
    write_json(args.checkpoint, translated)

    output = {key: translated.get(index, values[index]) for index, key in enumerate(keys)}
    write_json(args.output, output, indent=2)

    chinese = sum(1 for value in output.values() if has_cjk(value))
    print(f"\nDone! Output: {args.output}")
    print(f"Total keys: {len(output)}")
    print(f"Keys with Chinese: {chinese}/{len(output)} ({chinese * 100 // len(output)}%)")


if __name__ == "__main__":
    main()
