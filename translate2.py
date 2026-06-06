#!/usr/bin/env python3
"""Translate en-US strings to zh-CN using deep-translator."""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

try:
    from deep_translator import GoogleTranslator
except ImportError as exc:
    raise SystemExit("Missing dependency: pip install deep-translator") from exc


ROOT = Path(__file__).resolve().parent
DEFAULT_SOURCE = ROOT / "en-US-957k.json"
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


def has_cjk(value: object) -> bool:
    return isinstance(value, str) and any("\u4e00" <= char <= "\u9fff" for char in value)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="source en-US JSON file")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="translated zh-CN output file")
    parser.add_argument("--batch-size", type=int, default=20, help="number of strings per batch")
    parser.add_argument("--sleep", type=float, default=0.3, help="delay between batches")
    args = parser.parse_args()

    if args.batch_size <= 0:
        raise SystemExit("--batch-size must be greater than zero")

    translator = GoogleTranslator(source="en", target="zh-CN")
    data = load_json(args.source)
    keys = list(data.keys())
    values = list(data.values())
    translated = list(values)

    to_translate: list[tuple[int, str, dict[str, str]]] = []
    for index, value in enumerate(values):
        if isinstance(value, str) and not skip(value):
            protected, placeholders = protect(value)
            to_translate.append((index, protected, placeholders))

    print(f"Source: {args.source}", flush=True)
    print(f"Total keys: {len(values)}", flush=True)
    print(f"Strings to translate: {len(to_translate)}", flush=True)
    print(f"Skipped: {len(values) - len(to_translate)}", flush=True)

    errors = 0
    for start in range(0, len(to_translate), args.batch_size):
        batch = to_translate[start : start + args.batch_size]
        texts = [item[1] for item in batch]

        try:
            results = translator.translate_batch(texts)
            for (index, _, placeholders), result in zip(batch, results):
                if result:
                    translated[index] = restore(result, placeholders)
        except Exception:
            errors += 1
            for index, text, placeholders in batch:
                try:
                    result = translator.translate(text)
                    if result:
                        translated[index] = restore(result, placeholders)
                    time.sleep(0.15)
                except Exception:
                    pass

        done = min(start + args.batch_size, len(to_translate))
        percent = done * 100 // len(to_translate) if to_translate else 100
        print(f"\rProgress: {done}/{len(to_translate)} ({percent}%) | Errors: {errors}", end="", flush=True)
        if start + args.batch_size < len(to_translate):
            time.sleep(args.sleep)

    print("", flush=True)
    output = dict(zip(keys, translated))
    write_json(args.output, output)

    chinese = sum(1 for value in output.values() if has_cjk(value))
    print(f"\nDone! Output: {args.output}")
    print(f"Total keys: {len(output)}")
    print(f"Keys with Chinese: {chinese}/{len(output)} ({chinese * 100 // len(output)}%)")


if __name__ == "__main__":
    main()
