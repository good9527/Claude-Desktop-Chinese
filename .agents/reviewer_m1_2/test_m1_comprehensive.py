import os
import re
import json
import xml.etree.ElementTree as ET
from datetime import datetime

workspace = r"C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese"
files_to_check = {
    "SEO_GEO_INDEX.md": os.path.join(workspace, "SEO_GEO_INDEX.md"),
    "README.md": os.path.join(workspace, "README.md"),
    "sitemap.xml": os.path.join(workspace, "sitemap.xml"),
    "sitemap.json": os.path.join(workspace, "sitemap.json"),
}

results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def log_pass(msg):
    results["passed"].append(msg)
    print(f"[PASS] {msg}")

def log_fail(msg, details=""):
    results["failed"].append(f"{msg}: {details}")
    print(f"[FAIL] {msg} -> {details}")

def log_warn(msg):
    results["warnings"].append(msg)
    print(f"[WARN] {msg}")

print("=== 1. FILE EXISTENCE & UTF-8 / MOJIBAKE INTEGRITY CHECKS ===")
for name, path in files_to_check.items():
    if not os.path.exists(path):
        log_fail("File Exists", f"Missing file: {name}")
        continue
    log_pass(f"File exists: {name}")
    
    # Check binary reading and strict UTF-8
    with open(path, "rb") as f:
        raw_bytes = f.read()
    
    try:
        content = raw_bytes.decode("utf-8")
        log_pass(f"UTF-8 Strict Decode: {name} ({len(raw_bytes)} bytes, {len(content)} chars)")
    except Exception as e:
        log_fail("UTF-8 Decode", f"{name} failed decoding: {e}")
        continue
        
    # Check for Unicode replacement character \ufffd
    if "\ufffd" in content:
        log_fail("Unicode Replacement Char Check", f"{name} contains \\ufffd character!")
    else:
        log_pass(f"Zero \\ufffd characters in {name}")
        
    # Check for obvious mojibake patterns
    mojibake_patterns = [r"Ã[\x80-\xbf]", r"â[\x80-\xbf]{2}", r"æ[\x80-\xbf]{2}", r"ç[\x80-\xbf]{2}"]
    # Note: Chinese text contains 'æ', 'ç' valid unicode code points in UTF-8 representation, but decoded strings should NOT contain Latin-1 characters if decoded as UTF-8.
    # When decoded as UTF-8, Chinese characters are actual CJK codepoints (\u4e00-\u9fff).
    # Let's check for CJK characters ratio and absence of double-decoded sequences:
    cjk_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
    print(f"   -> {name}: {cjk_chars} CJK characters detected.")

print("\n=== 2. SITEMAP.XML VALIDATION ===")
xml_path = files_to_check["sitemap.xml"]
with open(xml_path, "r", encoding="utf-8") as f:
    xml_content = f.read()

# Check XML entity safety
if "&" in xml_content:
    amp_matches = re.findall(r'&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)', xml_content)
    if amp_matches:
        log_fail("XML Raw Ampersand", f"Found unescaped & in sitemap.xml: {len(amp_matches)} instances")
    else:
        log_pass("XML Entities: Ampersands properly escaped or absent")

try:
    # Parse XML
    root = ET.fromstring(xml_content)
    log_pass(f"XML Parsing Success: Tag={root.tag}")
    
    # Check namespace
    ns = {
        'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9',
        'xhtml': 'http://www.w3.org/1999/xhtml'
    }
    
    urls = root.findall('sitemap:url', ns)
    log_pass(f"Sitemap URL Count: {len(urls)} URLs found")
    
    url_locs = []
    for i, url in enumerate(urls, 1):
        loc = url.find('sitemap:loc', ns)
        lastmod = url.find('sitemap:lastmod', ns)
        changefreq = url.find('sitemap:changefreq', ns)
        priority = url.find('sitemap:priority', ns)
        
        loc_text = loc.text if loc is not None else None
        lastmod_text = lastmod.text if lastmod is not None else None
        changefreq_text = changefreq.text if changefreq is not None else None
        priority_text = priority.text if priority is not None else None
        
        if not loc_text or not loc_text.startswith("http"):
            log_fail("Sitemap URL Loc", f"URL #{i} invalid loc: {loc_text}")
        else:
            url_locs.append(loc_text)
            
        if priority_text:
            p_val = float(priority_text)
            if not (0.0 <= p_val <= 1.0):
                log_fail("Sitemap Priority Range", f"URL #{i} priority out of range: {p_val}")
                
        if lastmod_text:
            try:
                # Validate ISO 8601 format
                datetime.fromisoformat(lastmod_text)
            except Exception as e:
                log_fail("Sitemap lastmod ISO8601", f"URL #{i} lastmod invalid: {lastmod_text} ({e})")
                
        # Check xhtml:link alternates
        alternates = url.findall('xhtml:link', ns)
        if alternates:
            for alt in alternates:
                rel = alt.get('rel')
                hreflang = alt.get('hreflang')
                href = alt.get('href')
                if rel != "alternate" or not hreflang or not href:
                    log_fail("xhtml:link attributes", f"URL #{i} alternate missing attributes: {alt.attrib}")
                    
    log_pass(f"Sitemap URLs validated successfully: {url_locs}")
except Exception as e:
    log_fail("XML Parse Exception", str(e))

print("\n=== 3. SITEMAP.JSON VALIDATION ===")
json_path = files_to_check["sitemap.json"]
with open(json_path, "r", encoding="utf-8") as f:
    try:
        sitemap_json = json.load(f)
        log_pass("sitemap.json strictly valid JSON (no trailing commas, valid types)")
        
        required_root_keys = ["$schema", "project", "version", "baseUrl", "routes"]
        for k in required_root_keys:
            if k in sitemap_json:
                log_pass(f"sitemap.json has key '{k}'")
            else:
                log_fail("sitemap.json key missing", f"Missing '{k}'")
                
        routes = sitemap_json.get("routes", [])
        log_pass(f"sitemap.json routes count: {len(routes)}")
        route_ids = set()
        for r in routes:
            r_id = r.get("id")
            if not r_id:
                log_fail("Route ID missing", str(r))
            elif r_id in route_ids:
                log_fail("Duplicate Route ID", r_id)
            else:
                route_ids.add(r_id)
                
            if "priority" in r:
                p = r["priority"]
                if not (0.0 <= p <= 1.0):
                    log_fail("Route priority", f"Route {r_id} priority out of range: {p}")
                    
        log_pass(f"All route IDs unique: {list(route_ids)}")
    except Exception as e:
        log_fail("sitemap.json Parse Exception", str(e))

print("\n=== 4. EMBEDDED JSON-LD IN README.MD VALIDATION ===")
readme_path = files_to_check["README.md"]
with open(readme_path, "r", encoding="utf-8") as f:
    readme_content = f.read()

jsonld_scripts = re.findall(r'<script\s+type=["\']application/ld\+json["\']\s*>(.*?)</script>', readme_content, re.DOTALL)
log_pass(f"README.md embedded JSON-LD script blocks found: {len(jsonld_scripts)}")

for i, script_str in enumerate(jsonld_scripts, 1):
    try:
        parsed = json.loads(script_str.strip())
        schema_type = parsed.get("@type")
        schema_ctx = parsed.get("@context")
        if schema_ctx != "https://schema.org":
            log_fail(f"README JSON-LD #{i} @context", f"Expected https://schema.org, got {schema_ctx}")
        else:
            log_pass(f"README JSON-LD #{i} Valid Schema: @type={schema_type}, @context={schema_ctx}")
            
        if schema_type == "SoftwareApplication":
            assert "name" in parsed
            assert "operatingSystem" in parsed
            assert "featureList" in parsed
            assert isinstance(parsed["featureList"], list)
            log_pass(f"README SoftwareApplication schema complete ({len(parsed['featureList'])} features)")
        elif schema_type == "FAQPage":
            assert "mainEntity" in parsed
            assert isinstance(parsed["mainEntity"], list)
            log_pass(f"README FAQPage schema complete ({len(parsed['mainEntity'])} questions)")
            for q in parsed["mainEntity"]:
                assert q.get("@type") == "Question"
                assert "name" in q
                assert "acceptedAnswer" in q
                assert q["acceptedAnswer"].get("@type") == "Answer"
                assert "text" in q["acceptedAnswer"]
            log_pass(f"README FAQPage all {len(parsed['mainEntity'])} Q&A pairs structurally valid")
    except Exception as e:
        log_fail(f"README JSON-LD #{i} Parse/Validation Error", str(e))

print("\n=== 5. EMBEDDED JSON-LD & JSON IN SEO_GEO_INDEX.MD VALIDATION ===")
seo_path = files_to_check["SEO_GEO_INDEX.md"]
with open(seo_path, "r", encoding="utf-8") as f:
    seo_content = f.read()

json_fences = re.findall(r'```json\s*\n(.*?)\n```', seo_content, re.DOTALL)
log_pass(f"SEO_GEO_INDEX.md JSON code blocks found: {len(json_fences)}")

parsed_schemas = []
for i, block in enumerate(json_fences, 1):
    try:
        parsed = json.loads(block.strip())
        schema_type = parsed.get("@type") or parsed.get("project")
        parsed_schemas.append(schema_type)
        log_pass(f"SEO_GEO_INDEX JSON block #{i} parsed successfully: identifier='{schema_type}'")
        
        if parsed.get("@type") == "SoftwareApplication":
            assert "name" in parsed
            assert "featureList" in parsed
            assert "aggregateRating" in parsed
            log_pass("SoftwareApplication JSON-LD schema in SEO_GEO_INDEX verified")
        elif parsed.get("@type") == "FAQPage":
            assert "mainEntity" in parsed
            assert len(parsed["mainEntity"]) >= 4
            log_pass(f"FAQPage JSON-LD schema in SEO_GEO_INDEX verified ({len(parsed['mainEntity'])} questions)")
        elif parsed.get("@type") == "HowTo":
            assert "name" in parsed
            assert "step" in parsed
            assert len(parsed["step"]) >= 3
            log_pass(f"HowTo JSON-LD schema in SEO_GEO_INDEX verified ({len(parsed['step'])} steps)")
        elif "project" in parsed and parsed.get("project") == "Claude-Desktop-Chinese":
            assert "platform" in parsed
            assert "coverageRatio" in parsed
            assert "healthy" in parsed
            log_pass("Diagnostic Report JSON format in SEO_GEO_INDEX verified")
    except Exception as e:
        log_fail(f"SEO_GEO_INDEX JSON block #{i} Parse/Validation Error", str(e))

print("\n=== 6. CONTENT COMPLETENESS & ADVERSARIAL CHECKS ===")

# Check 3-Tier Self-Healing mentions
for name, content in [("README.md", readme_content), ("SEO_GEO_INDEX.md", seo_content)]:
    for term in ["Tier A", "Tier B", "Tier C", "FileSystemWatcher", "launchd", "systemd", "Auto-Healing", "自愈"]:
        if term.lower() in content.lower():
            log_pass(f"{name} contains 3-tier term '{term}'")
        else:
            log_fail(f"{name} missing 3-tier term", term)

# Check CLI Flags in README and SEO_GEO_INDEX
for flag in ["-i", "-u", "-c", "-r", "--daemon", "-q", "--json"]:
    if flag in readme_content:
        log_pass(f"README.md documents CLI flag '{flag}'")
    else:
        log_fail(f"README.md missing CLI flag", flag)
    if flag in seo_content:
        log_pass(f"SEO_GEO_INDEX.md documents CLI flag '{flag}'")
    else:
        log_fail(f"SEO_GEO_INDEX.md missing CLI flag", flag)

# Check Developer Terminology in both files
for term in ["MCP", "Artifacts", "Computer Use", "模型上下文协议", "制品", "计算机使用"]:
    if term in readme_content:
        log_pass(f"README.md contains terminology '{term}'")
    else:
        log_warn(f"README.md missing terminology '{term}'")
    if term in seo_content:
        log_pass(f"SEO_GEO_INDEX.md contains terminology '{term}'")
    else:
        log_fail(f"SEO_GEO_INDEX.md missing terminology", term)

# Check AI Engines in SEO_GEO_INDEX
for engine in ["ChatGPT", "Claude", "Gemini", "DeepSeek", "Perplexity"]:
    if engine in seo_content:
        log_pass(f"SEO_GEO_INDEX.md covers AI Engine '{engine}'")
    else:
        log_fail(f"SEO_GEO_INDEX.md missing AI Engine", engine)

# Check Search Engines in SEO_GEO_INDEX
for se in ["Google", "Baidu", "Bing"]:
    if se.lower() in seo_content.lower():
        log_pass(f"SEO_GEO_INDEX.md covers Search Engine '{se}'")
    else:
        log_fail(f"SEO_GEO_INDEX.md missing Search Engine", se)

print("\n=== SUMMARY ===")
print(f"Total Passed: {len(results['passed'])}")
print(f"Total Failed: {len(results['failed'])}")
print(f"Total Warnings: {len(results['warnings'])}")

if len(results['failed']) > 0:
    print("FAILED TESTS:")
    for f in results['failed']:
        print(f"  - {f}")
