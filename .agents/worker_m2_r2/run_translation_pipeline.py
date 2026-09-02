"""Translation Pipeline & Generator for Claude Desktop Chinese."""

import json
import re
import sys
from pathlib import Path
from typing import Dict, Tuple, List, Optional, Any

from glossary import harmonize_text
from masking import mask_text, unmask_text
from direct_translations import DIRECT_TRANSLATIONS, TECHNICAL_PRESERVE
from phrase_dict import EXACT_PHRASES
from icu_translations import ICU_EXACT_MAP
from vocab_tables import VERBS, NOUNS
from pattern_translator import PATTERN_RULES
from expanded_tables import EXPANDED_PHRASES, HELPERS

ROOT = Path(__file__).resolve().parents[2]
UNTRANSLATED_FILE = ROOT / ".agents" / "worker_m2_r2" / "untranslated.json"
RE_ICU = re.compile(r"\{[^{}]*,\s*(?:plural|select|number|date|time)[^{}]*(?:\{[^{}]*\}[^{}]*)*\}")

with open(UNTRANSLATED_FILE, "r", encoding="utf-8") as f:
    untranslated = json.load(f)

print(f"Total untranslated items to process: {len(untranslated)}")

def has_cjk(s: str) -> bool:
    return any("\u4e00" <= c <= "\u9fff" for c in s)

# Build Master Translation Lookup Table
MASTER_LOOKUP = {}
MASTER_LOOKUP.update(EXACT_PHRASES)
MASTER_LOOKUP.update(EXPANDED_PHRASES)
MASTER_LOOKUP.update(DIRECT_TRANSLATIONS)
MASTER_LOOKUP.update(ICU_EXACT_MAP)

# Combine word lookup
ALL_WORDS = {}
ALL_WORDS.update(HELPERS)
ALL_WORDS.update(VERBS)
ALL_WORDS.update(NOUNS)
ALL_WORDS.update({k.lower(): v for k, v in EXACT_PHRASES.items() if " " not in k})
ALL_WORDS.update({k.lower(): v for k, v in EXPANDED_PHRASES.items() if " " not in k})

def translate_icu_block(block: str) -> str:
    """Translate inner choices of ICU MessageFormat blocks."""
    # Plural match: {count, plural, one {# item} other {# items}}
    m_plural = re.match(r"^\{([a-zA-Z0-9_]+),\s*plural,\s*(?:=0\s*\{([^}]*)\}\s*)?one\s*\{([^}]*)\}\s*other\s*\{([^}]*)\}\s*\}$", block.strip())
    if m_plural:
        var, zero_text, one_text, other_text = m_plural.groups()
        # Translate one_text and other_text
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
        # Parse choices: key {val} key {val}
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

    if s in MASTER_LOOKUP:
        return MASTER_LOOKUP[s]

    s_lower = s.lower()
    if s_lower in MASTER_LOOKUP:
        return MASTER_LOOKUP[s_lower]

    if s_lower in ALL_WORDS:
        return ALL_WORDS[s_lower]

    # Pattern rules
    for pat, repl in PATTERN_RULES:
        if pat.search(s):
            res = pat.sub(repl, s)
            return res

    # Word-by-word / phrase-by-phrase replacement for short phrases
    words = re.findall(r"[a-zA-Z0-9_]+|[^\w\s]", s)
    translated_tokens = []
    for w in words:
        wl = w.lower()
        if wl in ALL_WORDS and ALL_WORDS[wl]:
            translated_tokens.append(ALL_WORDS[wl])
        elif w in [".", ",", "!", "?", ":", ";", "(", ")", "[", "]", "\"", "'", "-", "_", "/"]:
            # Convert punctuation where appropriate
            punc_map = {".": "。", ",": "，", "!": "！", "?": "？", ":": "：", ";": "；", "(": "（", ")": "）"}
            translated_tokens.append(punc_map.get(w, w))
        else:
            translated_tokens.append(w)

    return "".join(translated_tokens)

def translate_single_entry(key: str, value: str) -> str:
    """Translate a single dictionary entry."""
    # 1. Technical preservation
    if key in TECHNICAL_PRESERVE:
        return value

    # 2. Exact match
    if key in MASTER_LOOKUP:
        return harmonize_text(MASTER_LOOKUP[key])

    s = value.strip()
    if s in MASTER_LOOKUP:
        return harmonize_text(MASTER_LOOKUP[s])

    # 3. Mask protected tokens (code, URLs, tags, ICU, simple placeholders)
    masked, placeholders = mask_text(value)

    # 4. Pattern matching on masked text
    translated_masked = masked
    matched_pattern = False
    for pat, repl in PATTERN_RULES:
        if pat.search(translated_masked):
            translated_masked = pat.sub(repl, translated_masked)
            matched_pattern = True
            break

    # If pattern didn't match, translate sentences / clauses
    if not matched_pattern:
        # Split into sentences
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

    # 5. Unmask and handle inner ICU translations
    unmasked = unmask_text(translated_masked, placeholders)

    # Translate any ICU blocks inside unmasked
    def replace_icu(m):
        return translate_icu_block(m.group(0))

    final_text = RE_ICU.sub(replace_icu, unmasked)

    # 6. Apply glossary harmonization
    final_text = harmonize_text(final_text)

    return final_text

# Run test on all untranslated items
results = {}
for k, v in untranslated.items():
    results[k] = translate_single_entry(k, v)

has_cjk_count = sum(1 for v in results.values() if has_cjk(v))
total = len(results)
print(f"\n--- Translation Test Results ---")
print(f"Total keys processed: {total}")
print(f"Keys with Chinese: {has_cjk_count} ({has_cjk_count/total:.2%})")
print(f"Keys without Chinese: {total - has_cjk_count}")

# Sample 20 results
print("\n--- 20 Sample Translated Results ---")
for k in list(results.keys())[:20]:
    print(f"[{k}] EN: {repr(untranslated[k])}\n     ZH: {repr(results[k])}")
