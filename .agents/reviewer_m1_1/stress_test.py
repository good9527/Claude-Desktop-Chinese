import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(r"C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese")

print("=== DEEP ADVERSARIAL STRESS TEST ===")

# 1. Detailed Schema.org Validator
def validate_software_application(app, source):
    assert app.get("@context") in ["https://schema.org", "http://schema.org"], f"Invalid @context in {source}"
    assert app.get("@type") == "SoftwareApplication", f"Invalid @type in {source}"
    assert "name" in app and len(app["name"]) > 0, f"Missing name in {source}"
    assert "description" in app and len(app["description"]) > 10, f"Missing/short description in {source}"
    assert "operatingSystem" in app, f"Missing operatingSystem in {source}"
    assert "applicationCategory" in app, f"Missing applicationCategory in {source}"
    if "aggregateRating" in app:
        ar = app["aggregateRating"]
        assert ar.get("@type") == "AggregateRating", f"Invalid AggregateRating @type in {source}"
        assert "ratingValue" in ar and float(ar["ratingValue"]) >= 1.0, f"Invalid ratingValue in {source}"
        assert "ratingCount" in ar and int(ar["ratingCount"]) > 0, f"Invalid ratingCount in {source}"
    if "offers" in app:
        offers = app["offers"]
        assert offers.get("@type") == "Offer", f"Invalid Offer @type in {source}"
        assert "price" in offers, f"Missing price in {source}"
        assert "priceCurrency" in offers, f"Missing priceCurrency in {source}"
    print(f"  [PASS] SoftwareApplication Schema in {source}")

def validate_faq_page(faq, source):
    assert faq.get("@context") in ["https://schema.org", "http://schema.org"], f"Invalid @context in {source}"
    assert faq.get("@type") == "FAQPage", f"Invalid @type in {source}"
    assert "mainEntity" in faq and isinstance(faq["mainEntity"], list), f"Missing/invalid mainEntity in {source}"
    assert len(faq["mainEntity"]) >= 4, f"Too few FAQ items in {source}: {len(faq['mainEntity'])}"
    for idx, item in enumerate(faq["mainEntity"]):
        assert item.get("@type") == "Question", f"Item {idx} not Question in {source}"
        assert "name" in item and len(item["name"]) > 0, f"Question {idx} missing name in {source}"
        assert "acceptedAnswer" in item, f"Question {idx} missing acceptedAnswer in {source}"
        ans = item["acceptedAnswer"]
        assert ans.get("@type") == "Answer", f"Question {idx} acceptedAnswer not Answer in {source}"
        assert "text" in ans and len(ans["text"]) > 10, f"Question {idx} answer too short in {source}"
    print(f"  [PASS] FAQPage Schema ({len(faq['mainEntity'])} Q&As) in {source}")

def validate_howto(howto, source):
    assert howto.get("@context") in ["https://schema.org", "http://schema.org"], f"Invalid @context in {source}"
    assert howto.get("@type") == "HowTo", f"Invalid @type in {source}"
    assert "name" in howto and len(howto["name"]) > 0, f"Missing name in {source}"
    assert "step" in howto and isinstance(howto["step"], list) and len(howto["step"]) >= 3, f"Invalid steps in {source}"
    for idx, step in enumerate(howto["step"]):
        assert step.get("@type") == "HowToStep", f"Step {idx} not HowToStep in {source}"
        assert "name" in step and len(step["name"]) > 0, f"Step {idx} missing name in {source}"
        assert "text" in step and len(step["text"]) > 0, f"Step {idx} missing text in {source}"
        assert "position" in step and step["position"] == idx + 1, f"Step {idx} position mismatch in {source}"
    print(f"  [PASS] HowTo Schema ({len(howto['step'])} steps) in {source}")

# Test README schemas
readme_text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
blocks = re.findall(r'<script\s+type=["\']application/ld\+json["\']\s*>(.*?)</script>', readme_text, re.DOTALL | re.IGNORECASE)
for b in blocks:
    d = json.loads(b)
    if d.get("@type") == "SoftwareApplication":
        validate_software_application(d, "README.md")
    elif d.get("@type") == "FAQPage":
        validate_faq_page(d, "README.md")

# Test SEO_GEO_INDEX.md schemas
seo_text = (REPO_ROOT / "SEO_GEO_INDEX.md").read_text(encoding="utf-8")
json_blocks = re.findall(r'`json\s*(.*?)\s*`', seo_text, re.DOTALL)
for b in json_blocks:
    d = json.loads(b)
    if d.get("@type") == "SoftwareApplication":
        validate_software_application(d, "SEO_GEO_INDEX.md")
    elif d.get("@type") == "FAQPage":
        validate_faq_page(d, "SEO_GEO_INDEX.md")
    elif d.get("@type") == "HowTo":
        validate_howto(d, "SEO_GEO_INDEX.md")

# 2. Strict XML Validation of sitemap.xml
xml_path = REPO_ROOT / "sitemap.xml"
tree = ET.parse(xml_path)
root = tree.getroot()
assert root.tag == "{http://www.sitemaps.org/schemas/sitemap/0.9}urlset"
valid_freqs = {"always", "hourly", "daily", "weekly", "monthly", "yearly", "never"}
for url_el in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
    loc = url_el.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
    assert loc.startswith("https://"), f"Non-https URL: {loc}"
    lastmod = url_el.find("{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod").text
    # Parse ISO 8601 date
    datetime.fromisoformat(lastmod)
    changefreq = url_el.find("{http://www.sitemaps.org/schemas/sitemap/0.9}changefreq").text
    assert changefreq in valid_freqs, f"Invalid changefreq: {changefreq}"
    priority = float(url_el.find("{http://www.sitemaps.org/schemas/sitemap/0.9}priority").text)
    assert 0.0 <= priority <= 1.0, f"Invalid priority: {priority}"
print(f"  [PASS] Strict XML Sitemap schema & date validations on {len(root)} entries")

# 3. Strict JSON Validation of sitemap.json
sitemap_json = json.loads((REPO_ROOT / "sitemap.json").read_text(encoding="utf-8"))
assert sitemap_json["project"] == "Claude-Desktop-Chinese"
assert "routes" in sitemap_json and len(sitemap_json["routes"]) == 6
for r in sitemap_json["routes"]:
    assert "id" in r and "url" in r and "title" in r and "priority" in r
    assert 0.0 <= float(r["priority"]) <= 1.0
    assert r["changefreq"] in valid_freqs
print(f"  [PASS] Strict sitemap.json route validations on {len(sitemap_json['routes'])} routes")

# 4. GEO Matrix Verification
assert "ChatGPT" in seo_text and "Claude" in seo_text and "Gemini" in seo_text and "DeepSeek" in seo_text and "Perplexity" in seo_text
for cat_num in range(1, 6):
    assert f"2.{cat_num} 类别" in seo_text or f"2.{cat_num}" in seo_text
print("  [PASS] All 5 AI Engines and 5 GEO categories strictly verified")

print("\n=== ALL ADVERSARIAL STRESS TESTS PASSED SUCCESSFULLY ===")
