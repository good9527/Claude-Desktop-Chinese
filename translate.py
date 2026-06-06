#!/usr/bin/env python3
"""Translate en-US strings to zh-CN using googletrans."""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_SOURCE = ROOT / "local" / "en-US.json"
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


def protect(text: str) -> tuple[str, dict[str, str]]:
    placeholders: dict[str, str] = {}
    counter = 0

    def replace(pattern: str, value: str) -> str:
        nonlocal counter
        for match in list(re.finditer(pattern, value)):
            key = f"__PH{counter}__"
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


def skip_translate(value: object) -> bool:
    if not isinstance(value, str) or len(value.strip()) <= 2:
        return True
    return bool(re.match(r"^[\s{}\[\]<>/\-\d.:]+$", value))


def translate_batch(translator: object, texts: list[object], batch_size: int, sleep: float) -> list[object]:
    results = list(texts)
    to_translate: list[tuple[int, str, dict[str, str]]] = []

    for index, text in enumerate(texts):
        if isinstance(text, str) and not skip_translate(text):
            protected, placeholders = protect(text)
            to_translate.append((index, protected, placeholders))

    print(f"  {len(to_translate)} strings need translation (skipped {len(texts) - len(to_translate)})")

    for batch_start in range(0, len(to_translate), batch_size):
        batch = to_translate[batch_start : batch_start + batch_size]
        batch_texts = [item[1] for item in batch]

        try:
            translated = translator.translate(batch_texts, src="en", dest="zh-cn")
            for (index, _, placeholders), result in zip(batch, translated):
                if result and result.text:
                    results[index] = restore(result.text, placeholders)
        except Exception as exc:
            print(f"  [WARN] Batch failed at {batch_start}: {exc}")
            for index, protected, placeholders in batch:
                try:
                    translated = translator.translate(protected, src="en", dest="zh-cn")
                    if translated and translated.text:
                        results[index] = restore(translated.text, placeholders)
                    time.sleep(0.1)
                except Exception:
                    pass

        progress = min(batch_start + batch_size, len(to_translate))
        percent = progress * 100 // len(to_translate) if to_translate else 100
        print(f"  Progress: {progress}/{len(to_translate)} ({percent}%)")

        if batch_start + batch_size < len(to_translate):
            time.sleep(sleep)

    return results


def has_cjk(value: object) -> bool:
    return isinstance(value, str) and any("\u4e00" <= char <= "\u9fff" for char in value)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="source en-US JSON file")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="translated zh-CN output file")
    parser.add_argument("--batch-size", type=int, default=10, help="number of strings per batch")
    parser.add_argument("--sleep", type=float, default=0.5, help="delay between batches")
    args = parser.parse_args()

    if args.batch_size <= 0:
        raise SystemExit("--batch-size must be greater than zero")

    data = load_json(args.source)
    keys = list(data.keys())
    values = list(data.values())

    print("Using googletrans")
    print(f"Source: {args.source}")
    print(f"Total keys to translate: {len(data)}")
    print("\nStarting translation...")

    try:
        from googletrans import Translator
    except Exception as exc:
        raise SystemExit("googletrans is unavailable or incompatible. Try: pip install googletrans==4.0.0rc1") from exc

    translator = Translator()
    translated_values = translate_batch(translator, values, batch_size=args.batch_size, sleep=args.sleep)
    output = dict(zip(keys, translated_values))
    write_json(args.output, output)

    chinese = sum(1 for value in output.values() if has_cjk(value))
    print(f"\nDone! Output: {args.output}")
    print(f"Total keys: {len(output)}")
    print(f"Keys with Chinese: {chinese}/{len(output)} ({chinese * 100 // len(output)}%)")


if __name__ == "__main__":
    main()
