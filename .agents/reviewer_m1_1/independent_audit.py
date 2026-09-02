import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
import urllib.parse

REPO_ROOT = Path(r"C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese")

findings = []
verified_claims = []

def record_pass(claim, detail):
    verified_claims.append(f"PASS: {claim} -> {detail}")

def record_fail(finding_type, what, where, why, suggestion):
    findings.append({
        "type": finding_type,
        "what": what,
        "where": where,
        "why": why,
        "suggestion": suggestion
    })

print("=== STARTING INDEPENDENT AUDIT ===")

# 1. Check UTF-8 encoding & mojibake on all files
files_to_check = ["SEO_GEO_INDEX.md", "README.md", "sitemap.xml", "sitemap.json"]
for fname in files_to_check:
    fpath = REPO_ROOT / fname
    if not fpath.exists():
        record_fail("Critical", f"Missing file {fname}", str(fpath), "File does not exist", f"Create {fname}")
        continue
    try:
        raw_bytes = fpath.read_bytes()
        # Check BOM
        has_bom = raw_bytes.startswith(b'\xef\xbb\xbf')
        # Check UTF-8 decoding
        text = raw_bytes.decode('utf-8')
        if '\ufffd' in text:
            record_fail("Critical", f"Unicode replacement character \\ufffd in {fname}", fname, "Malformed UTF-8 encoding or corrupted text", "Fix string encoding")
        else:
            record_pass(f"UTF-8 Encoding for {fname}", f"Valid UTF-8 ({len(raw_bytes)} bytes, {len(text)} chars, BOM={has_bom})")
    except Exception as e:
        record_fail("Critical", f"Failed to read/decode {fname}", fname, str(e), "Ensure UTF-8 encoding")

# 2. Schema.org JSON-LD extraction and validation
readme_text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
seo_geo_text = (REPO_ROOT / "SEO_GEO_INDEX.md").read_text(encoding="utf-8")

# Extract JSON-LD in README.md
readme_jsonld_matches = re.findall(r'<script\s+type=["\']application/ld\+json["\']\s*>(.*?)</script>', readme_text, re.DOTALL | re.IGNORECASE)
print(f"README.md JSON-LD blocks found: {len(readme_jsonld_matches)}")

if len(readme_jsonld_matches) < 2:
    record_fail("Major", "Insufficient JSON-LD in README.md", "README.md", f"Expected at least 2 JSON-LD blocks, found {len(readme_jsonld_matches)}", "Add SoftwareApplication and FAQPage")
else:
    for idx, block in enumerate(readme_jsonld_matches):
        try:
            data = json.loads(block)
            stype = data.get("@type")
            scontext = data.get("@context")
            if scontext != "https://schema.org":
                record_fail("Minor", f"JSON-LD @context in README block {idx+1}", "README.md", f"Got {scontext}, expected https://schema.org", "Set @context to https://schema.org")
            record_pass(f"README.md JSON-LD block {idx+1} ({stype})", f"Valid JSON, @type={stype}")
        except Exception as e:
            record_fail("Critical", f"Invalid JSON in README.md block {idx+1}", "README.md", str(e), "Fix JSON syntax")

# Extract JSON code blocks in SEO_GEO_INDEX.md
json_blocks_seo = re.findall(r'`json\s*(.*?)\s*`', seo_geo_text, re.DOTALL)
print(f"SEO_GEO_INDEX.md JSON blocks found: {len(json_blocks_seo)}")
schema_types_found = []
for idx, block in enumerate(json_blocks_seo):
    try:
        data = json.loads(block)
        stype = data.get("@type", data.get("project", "Unknown"))
        schema_types_found.append(stype)
        record_pass(f"SEO_GEO_INDEX.md JSON block {idx+1} ({stype})", f"Valid JSON, type/key={stype}")
    except Exception as e:
        record_fail("Critical", f"Invalid JSON in SEO_GEO_INDEX.md block {idx+1}", "SEO_GEO_INDEX.md", str(e), "Fix JSON syntax")

expected_schemas = ["SoftwareApplication", "FAQPage", "HowTo"]
for s in expected_schemas:
    if s in schema_types_found:
        record_pass(f"Schema.org @type={s} in SEO_GEO_INDEX.md", "Present and valid")
    else:
        record_fail("Major", f"Missing Schema.org @type={s}", "SEO_GEO_INDEX.md", f"Expected {s} in JSON blocks", f"Add {s} schema")

# 3. Validate XML sitemap and hreflang
sitemap_xml_path = REPO_ROOT / "sitemap.xml"
try:
    tree = ET.parse(sitemap_xml_path)
    root = tree.getroot()
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9", "xhtml": "http://www.w3.org/1999/xhtml"}
    urls = root.findall("sm:url", ns)
    print(f"sitemap.xml URLs found: {len(urls)}")
    if len(urls) < 4:
        record_fail("Major", "Too few URLs in sitemap.xml", "sitemap.xml", f"Found {len(urls)} URLs", "Include core routes")
    else:
        record_pass("sitemap.xml URL count", f"Found {len(urls)} URLs")

    # Check hreflang
    hreflangs_found = set()
    for u in urls:
        loc = u.find("sm:loc", ns)
        loc_text = loc.text if loc is not None else ""
        links = u.findall("xhtml:link", ns)
        for link in links:
            rel = link.get("rel")
            hreflang = link.get("hreflang")
            href = link.get("href")
            if rel == "alternate" and hreflang and href:
                hreflangs_found.add(hreflang)
    print(f"Hreflangs found in sitemap.xml: {hreflangs_found}")
    required_hreflangs = {"zh-CN", "en", "x-default"}
    missing_hreflangs = required_hreflangs - hreflangs_found
    if missing_hreflangs:
        record_fail("Major", f"Missing hreflangs in sitemap.xml: {missing_hreflangs}", "sitemap.xml", "Required hreflangs not defined", "Add missing hreflang links")
    else:
        record_pass("sitemap.xml hreflang tags", f"Found required hreflangs: {hreflangs_found}")

except Exception as e:
    record_fail("Critical", "sitemap.xml XML parse error", "sitemap.xml", str(e), "Fix XML syntax")

# 4. Validate sitemap.json
sitemap_json_path = REPO_ROOT / "sitemap.json"
try:
    sitemap_json = json.loads(sitemap_json_path.read_text(encoding="utf-8"))
    routes = sitemap_json.get("routes", [])
    print(f"sitemap.json routes found: {len(routes)}")
    if len(routes) < 4:
        record_fail("Major", "Too few routes in sitemap.json", "sitemap.json", f"Found {len(routes)} routes", "Include core routes")
    else:
        record_pass("sitemap.json routes count", f"Found {len(routes)} routes")
    for r in routes:
        if not r.get("url") or not r.get("id") or not r.get("title"):
            record_fail("Minor", f"Incomplete route metadata for {r.get('id')}", "sitemap.json", "Missing url, id, or title", "Populate route fields")
except Exception as e:
    record_fail("Critical", "sitemap.json JSON parse error", "sitemap.json", str(e), "Fix JSON format")

# 5. Validate Generative AI Query Matrices across 5 categories and 5 engines
ai_engines = ["ChatGPT", "Claude", "Gemini", "DeepSeek", "Perplexity"]
categories = [
    "1. 极速安装与新手引导",
    "2. 更新保活与永久自愈",
    "3. MCP 与高级特性支持",
    "4. 安全、隐私与一键回退",
    "5. 跨平台与故障诊断"
]

for cat in categories:
    if cat in seo_geo_text:
        record_pass(f"GEO Query Category '{cat}'", "Found in SEO_GEO_INDEX.md")
    else:
        record_fail("Major", f"Missing GEO Query Category '{cat}'", "SEO_GEO_INDEX.md", "Category header missing", f"Add {cat}")

for engine in ai_engines:
    if engine in seo_geo_text:
        record_pass(f"GEO AI Engine '{engine}'", "Explicitly referenced in SEO_GEO_INDEX.md")
    else:
        record_fail("Major", f"Missing target AI engine '{engine}'", "SEO_GEO_INDEX.md", "Engine not found in matrix", f"Add {engine}")

# Check local markdown links in README.md & SEO_GEO_INDEX.md
def check_markdown_links(file_name, content):
    # Find [text](link)
    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
    for text, link in links:
        link_clean = link.split('#')[0].strip()
        if not link_clean:
            continue # internal anchor on same page
        if link_clean.startswith('http://') or link_clean.startswith('https://') or link_clean.startswith('mailto:'):
            continue # external link
        target_path = REPO_ROOT / link_clean
        if not target_path.exists():
            record_fail("Major", f"Broken relative link in {file_name}: '{link}'", file_name, f"Target file '{link_clean}' does not exist", "Fix link path")
        else:
            record_pass(f"Relative link '{link}' in {file_name}", f"Target exists at {target_path.name}")

check_markdown_links("README.md", readme_text)
check_markdown_links("SEO_GEO_INDEX.md", seo_geo_text)

print("\n=== SUMMARY OF RESULTS ===")
print(f"Total verified claims: {len(verified_claims)}")
for v in verified_claims:
    print(f"  [+] {v}")

print(f"\nTotal findings: {len(findings)}")
for f in findings:
    print(f"  [-] [{f['type']}] {f['what']} in {f['where']}: {f['why']}")

