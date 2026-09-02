import json
import xml.etree.ElementTree as ET
import re

def check_files():
    files = ["SEO_GEO_INDEX.md", "README.md", "sitemap.xml", "sitemap.json"]
    for file_path in files:
        with open(file_path, "rb") as f:
            raw = f.read()
        
        # Test UTF-8 decoding
        text = raw.decode("utf-8")
        assert "\ufffd" not in text, f"Found replacement character \ufffd in {file_path}"
        print(f"File {file_path}: {len(raw)} bytes, {len(text)} chars, valid UTF-8, no mojibake.")

if __name__ == "__main__":
    check_files()
