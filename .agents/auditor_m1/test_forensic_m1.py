"""
Forensic Integrity Audit Script for Milestone M1 (SEO & GEO)
Author: Forensic Auditor (auditor_m1)
"""

import os
import re
import json
import xml.etree.ElementTree as ET
from pathlib import Path

WORKSPACE = Path(r"C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese")

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

def test_file_existence_and_size():
    files = {
        "SEO_GEO_INDEX.md": 10000, # minimum expected bytes
        "README.md": 5000,
        "sitemap.xml": 1000,
        "sitemap.json": 1000
    }
    results = {}
    for filename, min_size in files.items():
        filepath = WORKSPACE / filename
        if not filepath.exists():
            results[filename] = {"status": "FAIL", "reason": "File does not exist"}
        else:
            size = filepath.stat().st_size
            if size < min_size:
                results[filename] = {"status": "FAIL", "reason": f"File too small: {size} < {min_size}"}
            else:
                results[filename] = {"status": "PASS", "size": size}
    return results

def test_encoding_and_mojibake():
    targets = ["SEO_GEO_INDEX.md", "README.md", "sitemap.xml", "sitemap.json"]
    results = {}
    for filename in targets:
        filepath = WORKSPACE / filename
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            if "\ufffd" in content:
                results[filename] = {"status": "FAIL", "reason": "Contains Unicode replacement character \ufffd"}
            elif "\x00" in content:
                results[filename] = {"status": "FAIL", "reason": "Contains null bytes"}
            else:
                results[filename] = {"status": "PASS", "chars": len(content)}
        except Exception as e:
            results[filename] = {"status": "FAIL", "reason": str(e)}
    return results

def test_placeholder_and_stubs():
    targets = ["SEO_GEO_INDEX.md", "README.md", "sitemap.xml", "sitemap.json"]
    suspicious_patterns = [
        r"\bTODO\b",
        r"\bFIXME\b",
        r"\bTBD\b",
        r"\bPLACEHOLDER\b",
        r"\bLorem ipsum\b",
        r"\bxxx\b",
        r"sample_url",
        r"example\.com"
    ]
    findings = {}
    for filename in targets:
        filepath = WORKSPACE / filename
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        matches = []
        for idx, line in enumerate(lines, 1):
            for pat in suspicious_patterns:
                if re.search(pat, line, re.IGNORECASE):
                    # Check if it's legitimate context or stub
                    matches.append((idx, pat, line.strip()))
        findings[filename] = matches
    return findings

def test_sitemap_xml():
    filepath = WORKSPACE / "sitemap.xml"
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        namespaces = {
            "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
            "xhtml": "http://www.w3.org/1999/xhtml"
        }
        urls = root.findall("sm:url", namespaces)
        url_data = []
        for u in urls:
            loc = u.find("sm:loc", namespaces)
            lastmod = u.find("sm:lastmod", namespaces)
            changefreq = u.find("sm:changefreq", namespaces)
            priority = u.find("sm:priority", namespaces)
            alts = u.findall("xhtml:link", namespaces)
            url_data.append({
                "loc": loc.text if loc is not None else None,
                "lastmod": lastmod.text if lastmod is not None else None,
                "changefreq": changefreq.text if changefreq is not None else None,
                "priority": priority.text if priority is not None else None,
                "alternates": len(alts)
            })
        return {"status": "PASS", "count": len(urls), "urls": url_data}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

def test_sitemap_json():
    filepath = WORKSPACE / "sitemap.json"
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        required_root_keys = ["$schema", "project", "version", "lastUpdated", "baseUrl", "routes"]
        missing_root = [k for k in required_root_keys if k not in data]
        if missing_root:
            return {"status": "FAIL", "missing_keys": missing_root}
        routes = data.get("routes", [])
        if len(routes) < 5:
            return {"status": "FAIL", "reason": f"Too few routes: {len(routes)}"}
        for r in routes:
            for rk in ["id", "path", "url", "title", "description", "category", "priority"]:
                if rk not in r:
                    return {"status": "FAIL", "reason": f"Route {r.get('id')} missing {rk}"}
        return {"status": "PASS", "route_count": len(routes), "routes": [r["id"] for r in routes]}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

def extract_json_ld_from_readme():
    filepath = WORKSPACE / "README.md"
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    pattern = r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>'
    matches = re.findall(pattern, content, re.DOTALL)
    parsed = []
    errors = []
    for idx, m in enumerate(matches):
        try:
            data = json.loads(m)
            parsed.append(data)
        except Exception as e:
            errors.append((idx, str(e)))
    return {"status": "PASS" if not errors and len(parsed) >= 2 else "FAIL", "count": len(parsed), "types": [d.get("@type") for d in parsed], "errors": errors}

def extract_json_blocks_from_seo_geo_index():
    filepath = WORKSPACE / "SEO_GEO_INDEX.md"
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    pattern = r'```json\s*(\{.*?\})\s*```'
    matches = re.findall(pattern, content, re.DOTALL)
    parsed = []
    errors = []
    for idx, m in enumerate(matches):
        try:
            data = json.loads(m)
            parsed.append(data)
        except Exception as e:
            errors.append((idx, str(e)))
    return {"status": "PASS" if not errors and len(parsed) >= 3 else "FAIL", "count": len(parsed), "types": [d.get("@type") or d.get("project") for d in parsed], "errors": errors}

def test_cross_referencing():
    # Verify CLI flags consistency
    # CLI flags in PROJECT.md: -i, -u, -c, -r, --daemon, -q, --json
    project_md = (WORKSPACE / "PROJECT.md").read_text(encoding="utf-8")
    readme_md = (WORKSPACE / "README.md").read_text(encoding="utf-8")
    seo_md = (WORKSPACE / "SEO_GEO_INDEX.md").read_text(encoding="utf-8")
    
    flags = ["-i", "-u", "-c", "-r", "--daemon", "-q", "--json"]
    missing_in_readme = [f for f in flags if f not in readme_md]
    missing_in_seo = [f for f in flags if f not in seo_md]
    
    # Check Repo URLs
    repo_url = "https://github.com/good9527/Claude-Desktop-Chinese"
    
    return {
        "missing_flags_readme": missing_in_readme,
        "missing_flags_seo": missing_in_seo,
        "repo_url_in_readme": repo_url in readme_md,
        "repo_url_in_seo": repo_url in seo_md,
        "repo_url_in_xml": repo_url in (WORKSPACE / "sitemap.xml").read_text(encoding="utf-8"),
        "repo_url_in_json": repo_url in (WORKSPACE / "sitemap.json").read_text(encoding="utf-8")
    }

if __name__ == "__main__":
    print("=== FORENSIC INTEGRITY AUDIT: MILESTONE M1 ===")
    
    print("\n--- 1. File Existence & Size Checks ---")
    f_res = test_file_existence_and_size()
    print(json.dumps(f_res, indent=2))
    
    print("\n--- 2. Encoding & Mojibake Checks ---")
    enc_res = test_encoding_and_mojibake()
    print(json.dumps(enc_res, indent=2))
    
    print("\n--- 3. Placeholder & Stub Scan ---")
    stub_res = test_placeholder_and_stubs()
    print(json.dumps(stub_res, indent=2))
    
    print("\n--- 4. XML Sitemap Verification ---")
    xml_res = test_sitemap_xml()
    print(json.dumps(xml_res, indent=2))
    
    print("\n--- 5. JSON Sitemap Verification ---")
    json_res = test_sitemap_json()
    print(json.dumps(json_res, indent=2))
    
    print("\n--- 6. README JSON-LD Schema Extraction ---")
    r_ld_res = extract_json_ld_from_readme()
    print(json.dumps(r_ld_res, indent=2))
    
    print("\n--- 7. SEO_GEO_INDEX JSON-LD & Schemas Extraction ---")
    s_ld_res = extract_json_blocks_from_seo_geo_index()
    print(json.dumps(s_ld_res, indent=2))
    
    print("\n--- 8. Cross-Reference Consistency ---")
    cr_res = test_cross_referencing()
    print(json.dumps(cr_res, indent=2))
