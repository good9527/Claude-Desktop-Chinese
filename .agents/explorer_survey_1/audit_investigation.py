#!/usr/bin/env python3
"""Audit script for Claude Desktop Chinese translations."""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[2]
ZH_DIST = ROOT / "dist" / "zh-CN.json"
ZH_ION = ROOT / "zh-CN-ion.json"

print(f"Loading {ZH_DIST}...")
with ZH_DIST.open("r", encoding="utf-8-sig") as f:
    dist_data = json.load(f)

with ZH_ION.open("r", encoding="utf-8-sig") as f:
    ion_data = json.load(f)

print(f"dist/zh-CN.json keys: {len(dist_data)}")
print(f"zh-CN-ion.json keys: {len(ion_data)}")
print(f"Files identical: {dist_data == ion_data}")

# 1. Structure & Length Analysis
print("\n" + "="*50)
print("1. KEY & VALUE STRUCTURE ANALYSIS")
print("="*50)

def has_cjk(s):
    return any('\u4e00' <= c <= '\u9fff' for c in s)

total = len(dist_data)
cjk_count = sum(1 for v in dist_data.values() if has_cjk(v))
pure_en = sum(1 for v in dist_data.values() if not has_cjk(v) and re.search(r'[a-zA-Z]', v))
pure_num_sym = sum(1 for v in dist_data.values() if not has_cjk(v) and not re.search(r'[a-zA-Z]', v))

print(f"Total keys: {total}")
print(f"Values containing Chinese (CJK): {cjk_count} ({cjk_count/total*100:.2f}%)")
print(f"Values in Pure English/Latin:    {pure_en} ({pure_en/total*100:.2f}%)")
print(f"Values with Numbers/Symbols:    {pure_num_sym} ({pure_num_sym/total*100:.2f}%)")

# 2. Leftover Placeholders and Broken Tags
print("\n" + "="*50)
print("2. PLACEHOLDER & FORMAT INTEGRITY AUDIT")
print("="*50)

ph_leftovers = []
for k, v in dist_data.items():
    m = re.findall(r'(__PH\d*__?|PH\d+X|__PH|\bPH\d+\b)', v)
    if m:
        ph_leftovers.append((k, v, m))

print(f"Leftover translation tokens (PH0X, __PH0__, etc.): {len(ph_leftovers)}")
for k, v, m in ph_leftovers[:10]:
    print(f"  [{k}] (matches: {m}) -> {v}")

unbalanced_braces = []
for k, v in dist_data.items():
    oc = v.count('{')
    cc = v.count('}')
    if oc != cc:
        unbalanced_braces.append((k, v, oc, cc))

print(f"\nUnbalanced curly braces {{}}: {len(unbalanced_braces)}")
for k, v, oc, cc in unbalanced_braces[:10]:
    print(f"  [{k}] (open={oc}, close={cc}) -> {v}")

icu_format_strings = []
for k, v in dist_data.items():
    if re.search(r'\{\s*\w+\s*,\s*(plural|select|selectordinal|number|date|time)', v):
        icu_format_strings.append((k, v))

print(f"\nICU MessageFormat strings (plural/select/etc.): {len(icu_format_strings)}")
icu_untranslated = sum(1 for k, v in icu_format_strings if not has_cjk(v))
print(f"  - Untranslated ICU strings (all English): {icu_untranslated}")
print(f"  - Translated / partially translated ICU: {len(icu_format_strings) - icu_untranslated}")
for k, v in icu_format_strings[:5]:
    print(f"  Sample [{k}] -> {v}")

printf_placeholders = []
for k, v in dist_data.items():
    m = re.findall(r'%[0-9]*\$?[a-zA-Z]', v)
    if m:
        printf_placeholders.append((k, v, m))
print(f"\nPrintf-style placeholders (%s, %d, %1$s, etc.): {len(printf_placeholders)}")
for k, v, m in printf_placeholders[:5]:
    print(f"  Sample [{k}] -> {v} (tokens: {m})")

html_tag_issues = []
for k, v in dist_data.items():
    if '<' in v or '>' in v:
        # Check matching tags
        opening_tags = re.findall(r'<([a-zA-Z][a-zA-Z0-9]*)[^>]*>', v)
        closing_tags = re.findall(r'</([a-zA-Z][a-zA-Z0-9]*)>', v)
        if set(opening_tags) != set(closing_tags) and not any(t in ['br', 'hr', 'img', 'input'] for t in opening_tags):
            html_tag_issues.append((k, v, opening_tags, closing_tags))
print(f"\nHTML tag balance anomalies: {len(html_tag_issues)}")
for k, v, ot, ct in html_tag_issues[:5]:
    print(f"  Sample [{k}] -> {v} (open={ot}, close={ct})")

# 3. Mojibake & Encoding Corruption
print("\n" + "="*50)
print("3. MOJIBAKE & ENCODING CORRUPTION AUDIT")
print("="*50)

mojibake_checks = {
    "Unicode Replacement Char (\\ufffd)": lambda v: "\ufffd" in v,
    "Standard GBK Mojibake (锟斤拷 / 烫烫烫 / 屯屯屯)": lambda v: any(w in v for w in ["锟斤拷", "烫烫", "屯屯", "锟"]),
    "Double-encoded UTF-8 chars (Ã, Â, â€)": lambda v: bool(re.search(r'[\xc2\xc3][\x80-\xbf]|â€[™œž“”’‘]', v)),
    "HTML entity remnants (&amp;, &quot;, &lt;, &#39;)": lambda v: bool(re.search(r'(&amp;|&quot;|&lt;|&gt;|&#\d+;|&apos;|&nbsp;)', v)),
    "Control characters (except \\t, \\n, \\r)": lambda v: bool(re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', v)),
    "Space-padded placeholder errors (e.g. { name } instead of {name})": lambda v: bool(re.search(r'\{\s+[a-zA-Z0-9_]+\s+\}', v)),
    "Corrupted URL protocols (e.g. http s : / /)": lambda v: bool(re.search(r'https?\s*:\s*/\s*/', v)),
}

for name, check_fn in mojibake_checks.items():
    matched = [(k, v) for k, v in dist_data.items() if check_fn(v)]
    print(f"{name}: {len(matched)}")
    for k, v in matched[:5]:
        print(f"  [{k}] -> {v[:100]}")

# 4. Developer Terminology Consistency
print("\n" + "="*50)
print("4. DEVELOPER & CLAUDE TERMINOLOGY AUDIT")
print("="*50)

terms = {
    "MCP / Model Context Protocol": [
        r'\bMCP\b', r'Model Context Protocol', r'模型上下文协议', r'MCP\s*服务器', r'MCP\s*工具', r'MCP\s*扩展'
    ],
    "Artifacts": [
        r'\bArtifacts?\b', r'制品', r'工件', r'构件', r'产物', r'项目制品'
    ],
    "Computer Use": [
        r'Computer Use', r'计算机使用', r'电脑使用', r'计算机控制', r'屏幕使用'
    ],
    "Token / Token Management": [
        r'\bTokens?\b', r'令牌', r'代币', r'Token\s*管理', r'令牌管理'
    ],
    "Context Window": [
        r'Context Window', r'上下文窗口', r'上下文长度', r'上下文大小', r'上下文限制'
    ],
    "Thinking / Extended Thinking": [
        r'Extended Thinking', r'Thinking mode', r'深度思考', r'扩展思考', r'思考模式', r'思考时间'
    ],
    "Prompt Caching": [
        r'Prompt Cach(ing|e)', r'提示词缓存', r'提示缓存', r'指令缓存'
    ],
    "Projects": [
        r'\bProjects?\b', r'项目', r'方案'
    ],
    "Connectors / Integrations": [
        r'\bConnectors?\b', r'连接器', r'适配器', r'集成'
    ],
    "Custom Instructions / System Prompt": [
        r'Custom Instructions', r'System Prompt', r'自定义指令', r'自定义提示词', r'系统提示词'
    ]
}

for term_cat, patterns in terms.items():
    print(f"\n--- Term Category: {term_cat} ---")
    cat_counts = Counter()
    samples = defaultdict(list)
    for pat in patterns:
        rx = re.compile(pat, re.IGNORECASE)
        for k, v in dist_data.items():
            if rx.search(v):
                cat_counts[pat] += 1
                if len(samples[pat]) < 3:
                    samples[pat].append((k, v))
    for pat, cnt in cat_counts.most_common():
        print(f"  Pattern `{pat}`: {cnt} occurrences")
        for k, v in samples[pat][:2]:
            print(f"    Sample [{k}] -> {v[:90]}")

print("\nAudit script complete.")
