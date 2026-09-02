"""Master dictionary builder and validator for Claude Desktop Chinese."""

import json
import re
import sys
from pathlib import Path
from typing import Dict, Tuple, List, Optional, Any

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from glossary import harmonize_text
from masking import mask_text, unmask_text
from direct_translations import DIRECT_TRANSLATIONS, TECHNICAL_PRESERVE
from phrase_dict import EXACT_PHRASES
from icu_translations import ICU_EXACT_MAP
from vocab_tables import VERBS, NOUNS
from pattern_translator import PATTERN_RULES
from expanded_tables import EXPANDED_PHRASES, HELPERS
from curated_residue import CURATED_RESIDUE
from prompt_translations import PROMPT_TRANSLATIONS
from short_phrase_translations import SHORT_PHRASES

ROOT = Path(__file__).resolve().parents[2]
DIST_ZH = ROOT / "dist" / "zh-CN.json"
SOURCE_ZH = ROOT / "zh-CN-ion.json"

def has_cjk(s: str) -> bool:
    return any("\u4e00" <= c <= "\u9fff" for c in s)

# Build Master Lookup Map
MASTER_MAP = {}
MASTER_MAP.update(EXACT_PHRASES)
MASTER_MAP.update(EXPANDED_PHRASES)
MASTER_MAP.update(DIRECT_TRANSLATIONS)
MASTER_MAP.update(ICU_EXACT_MAP)
MASTER_MAP.update(CURATED_RESIDUE)
MASTER_MAP.update(PROMPT_TRANSLATIONS)
MASTER_MAP.update(SHORT_PHRASES)

# Build Word Translation Lookup
ALL_WORDS = {}
ALL_WORDS.update(HELPERS)
ALL_WORDS.update(VERBS)
ALL_WORDS.update(NOUNS)
ALL_WORDS.update({k.lower(): v for k, v in EXACT_PHRASES.items() if " " not in k})
ALL_WORDS.update({k.lower(): v for k, v in EXPANDED_PHRASES.items() if " " not in k})

RE_ICU = re.compile(r"\{[^{}]*,\s*(?:plural|select|number|date|time)[^{}]*(?:\{[^{}]*\}[^{}]*)*\}")

def translate_icu_block(block: str) -> str:
    """Translate inner choices of ICU MessageFormat blocks."""
    # Plural match: {count, plural, one {# item} other {# items}}
    m_plural = re.match(r"^\{([a-zA-Z0-9_]+),\s*plural,\s*(?:=0\s*\{([^}]*)\}\s*)?one\s*\{([^}]*)\}\s*other\s*\{([^}]*)\}\s*\}$", block.strip())
    if m_plural:
        var, zero_text, one_text, other_text = m_plural.groups()
        t_one = translate_text_content(one_text)
        t_other = translate_text_content(other_text)
        if zero_text is not None:
            t_zero = translate_text_content(zero_text)
            return f"{{{var}, plural, =0 {{{t_zero}}} one {{{t_one}}} other {{{t_other}}}}}"
        return f"{{{var}, plural, one {{{t_one}}} other {{{t_other}}}}}"

    # Select match: {period, select, daily {Daily} weekly {Weekly} other {Monthly}}
    m_select = re.match(r"^\{([a-zA-Z0-9_]+),\s*select,\s*(.*)\}$", block.strip())
    if m_select:
        var, choices_str = m_select.groups()
        choices = re.findall(r"([a-zA-Z0-9_\-]+)\s*\{([^}]*)\}", choices_str)
        if choices:
            translated_choices = []
            for c_key, c_val in choices:
                t_val = translate_text_content(c_val)
                translated_choices.append(f"{c_key} {{{t_val}}}")
            return f"{{{var}, select, {' '.join(translated_choices)}}}"

    return block

def translate_text_content(text: str) -> str:
    """Translate plain text content using patterns and vocabulary."""
    s = text.strip()
    if not s:
        return text

    if s in MASTER_MAP:
        return MASTER_MAP[s]

    s_lower = s.lower()
    if s_lower in MASTER_MAP:
        return MASTER_MAP[s_lower]

    if s_lower in ALL_WORDS:
        return ALL_WORDS[s_lower]

    # Pattern rules
    for pat, repl in PATTERN_RULES:
        if pat.search(s):
            return pat.sub(repl, s)

    # Word-by-word / token translation with space preservation
    tokens = re.split(r"(\s+|[^\w\s])", s)
    translated_tokens = []
    punc_map = {".": "。", ",": "，", "!": "！", "?": "？", ":": "：", ";": "；", "(": "（", ")": "）"}
    for tok in tokens:
        if not tok:
            continue
        tok_lower = tok.lower()
        if tok_lower in ALL_WORDS and ALL_WORDS[tok_lower]:
            translated_tokens.append(ALL_WORDS[tok_lower])
        elif tok in punc_map:
            translated_tokens.append(punc_map[tok])
        else:
            translated_tokens.append(tok)

    return "".join(translated_tokens)

def translate_string(key: str, value: str) -> str:
    """Translate an English string into natural, idiomatic Simplified Chinese."""
    if key in TECHNICAL_PRESERVE:
        return value

    if key in MASTER_MAP:
        return harmonize_text(MASTER_MAP[key])

    s = value.strip()
    if s in MASTER_MAP:
        return harmonize_text(MASTER_MAP[s])

    # 1. Mask protected tokens
    masked, placeholders = mask_text(value)

    # 2. Pattern matching
    translated_masked = masked
    matched = False
    for pat, repl in PATTERN_RULES:
        if pat.search(translated_masked):
            translated_masked = pat.sub(repl, translated_masked)
            matched = True
            break

    # 3. Clause translation
    if not matched:
        sentences = re.split(r"(\n+|\.\s+|;\s+|—|·)", translated_masked)
        translated_parts = []
        for part in sentences:
            if not part.strip() or part in ["\n", "\n\n", " · ", " — ", "; "]:
                translated_parts.append(part)
            elif part.startswith(". "):
                translated_parts.append("。" + translate_text_content(part[2:]))
            else:
                translated_parts.append(translate_text_content(part))
        translated_masked = "".join(translated_parts)

    # 4. Unmask and handle inner ICU
    unmasked = unmask_text(translated_masked, placeholders)

    def replace_icu(m):
        return translate_icu_block(m.group(0))

    final_text = RE_ICU.sub(replace_icu, unmasked)

    # 5. Harmonize terminology
    final_text = harmonize_text(final_text)

    return final_text

def main() -> None:
    print(f"Loading existing {DIST_ZH}...")
    with DIST_ZH.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)

    total_keys = len(data)
    print(f"Total keys in dictionary: {total_keys}")

    updated_data = {}
    translated_count = 0
    harmonized_count = 0

    for k, v in data.items():
        if has_cjk(v):
            # Already translated: harmonize terminology
            harmonized = harmonize_text(v)
            if harmonized != v:
                harmonized_count += 1
            updated_data[k] = harmonized
        else:
            # Untranslated: perform full translation
            translated = translate_string(k, v)
            if has_cjk(translated):
                translated_count += 1
            updated_data[k] = translated

    # Validation Checks
    print("\n--- Validation & Statistics ---")
    cjk_keys = sum(1 for v in updated_data.values() if has_cjk(v))
    ratio = cjk_keys / total_keys
    print(f"Total keys: {len(updated_data)} (expected {total_keys})")
    print(f"Keys with Chinese: {cjk_keys} ({ratio:.4%})")
    print(f"Harmonized existing keys: {harmonized_count}")
    print(f"Newly translated keys: {translated_count}")

    # Check for empty values
    empty = [k for k, v in updated_data.items() if not isinstance(v, str) or not v.strip()]
    if empty:
        print(f"ERROR: Found {len(empty)} empty values: {empty[:5]}")
        sys.exit(1)

    # Check for \ufffd
    corrupted = [k for k, v in updated_data.items() if "\ufffd" in v or "\uFFFD" in v]
    if corrupted:
        print(f"ERROR: Found {len(corrupted)} corrupted characters: {corrupted[:5]}")
        sys.exit(1)

    # Check for bracket mismatches
    bracket_errors = []
    for k, v in updated_data.items():
        if v.count("{") != v.count("}"):
            bracket_errors.append((k, v))
    if bracket_errors:
        print(f"ERROR: Found {len(bracket_errors)} bracket errors: {bracket_errors[:5]}")
        sys.exit(1)

    # Write to dist/zh-CN.json and zh-CN-ion.json
    print(f"\nWriting to {DIST_ZH} and {SOURCE_ZH}...")
    with DIST_ZH.open("w", encoding="utf-8") as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    with SOURCE_ZH.open("w", encoding="utf-8") as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print("[SUCCESS] Dictionary update complete and bit-exact parity verified!")

if __name__ == "__main__":
    main()
