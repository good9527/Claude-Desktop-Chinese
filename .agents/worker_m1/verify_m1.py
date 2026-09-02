import json
import xml.etree.ElementTree as ET
import re
import sys

def main():
    print("=== 1. Validating sitemap.xml ===")
    tree = ET.parse("sitemap.xml")
    root = tree.getroot()
    print(f"Root tag: {root.tag}")
    urls = root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url")
    print(f"Found {len(urls)} URLs in sitemap.xml")
    assert len(urls) >= 5, f"Expected at least 5 URLs, got {len(urls)}"
    for u in urls:
        loc = u.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        priority = u.find("{http://www.sitemaps.org/schemas/sitemap/0.9}priority")
        print(f"  URL: {loc.text} (priority: {priority.text if priority is not None else 'N/A'})")

    print("\n=== 2. Validating sitemap.json ===")
    with open("sitemap.json", "r", encoding="utf-8") as f:
        sitemap_json = json.load(f)
    routes = sitemap_json.get("routes", [])
    print(f"Loaded sitemap.json with {len(routes)} routes")
    assert len(routes) >= 5, f"Expected at least 5 routes, got {len(routes)}"
    for r in routes:
        print(f"  Route: {r['id']} -> {r['url']} (priority: {r.get('priority')})")

    print("\n=== 3. Validating JSON-LD in README.md ===")
    with open("README.md", "r", encoding="utf-8") as f:
        readme_content = f.read()

    scripts = re.findall(r'<script type="application/ld\+json">(.*?)</script>', readme_content, re.DOTALL)
    print(f"Found {len(scripts)} JSON-LD blocks in README.md")
    assert len(scripts) >= 2, f"Expected at least 2 JSON-LD blocks, got {len(scripts)}"
    for i, script in enumerate(scripts):
        data = json.loads(script.strip())
        print(f"  Block {i+1}: @context={data.get('@context')}, @type={data.get('@type')}, name={data.get('name')}")

    print("\n=== 4. Validating JSON blocks in SEO_GEO_INDEX.md ===")
    with open("SEO_GEO_INDEX.md", "r", encoding="utf-8") as f:
        seo_content = f.read()

    json_blocks = re.findall(r'```json\s*(\{.*?\})\s*```', seo_content, re.DOTALL)
    print(f"Found {len(json_blocks)} JSON blocks in SEO_GEO_INDEX.md")
    assert len(json_blocks) >= 3, f"Expected at least 3 JSON blocks, got {len(json_blocks)}"
    for i, block in enumerate(json_blocks):
        data = json.loads(block.strip())
        schema_type = data.get("@type") or data.get("project")
        print(f"  JSON block {i+1}: @type/project={schema_type}, name={data.get('name')}")

    print("\n==============================================")
    print("SUCCESS: ALL M1 ASSETS VALIDATED WITH ZERO ERRORS!")
    print("==============================================")

if __name__ == "__main__":
    main()
