import re
from pathlib import Path

REPO_ROOT = Path(r"C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese")

def check_all_links(filename):
    text = (REPO_ROOT / filename).read_text(encoding="utf-8")
    urls = re.findall(r'https?://[^\s\)\]\"\'\<\>]+', text)
    print(f"[{filename}] Found {len(urls)} URLs:")
    for u in sorted(set(urls)):
        print(f"  - {u}")

check_all_links("README.md")
check_all_links("SEO_GEO_INDEX.md")
check_all_links("sitemap.xml")
check_all_links("sitemap.json")
