"""Multi-pass translation pipeline for Claude Desktop Chinese."""

import json
import re
import sys
from pathlib import Path
from typing import Dict, Tuple, List, Optional, Any

from glossary import harmonize_text

ROOT = Path(__file__).resolve().parents[2]
DIST_ZH = ROOT / "dist" / "zh-CN.json"
SOURCE_ZH = ROOT / "zh-CN-ion.json"
UNTRANSLATED_FILE = ROOT / ".agents" / "worker_m2_r2" / "untranslated.json"

def has_cjk(s: str) -> bool:
    return any("\u4e00" <= c <= "\u9fff" for c in s)

# 1. Technical non-translatable strings that should remain as English/symbols/numbers/code
NON_TRANSLATABLE_EXACT = {
    "1yRrT11eFX": "5000000",
    "C9WGEuJVec": "/",
    "Ck5uU8xAnb": "11111111-1111-1111-1111-111111111111",
    "K6JkfClWz4": "19:00",
    "L4dIq9u0LB": "127.0.0.1",
    "7U5OZwbVj5": "https://intranet.example.com/usage-policy",
    "A2T4C1rkYn": "status.claude.com",
    "GjGGnRegQo": "settings.json",
    "Hw5q4zD5lS": "https://example.com/webhook",
    "IHENczwSR2": "https://config.example.com/claude-desktop",
    "NHvtv6jJcx": "https://REGION-aiplatform-ENDPOINT_ID.p.googleapis.com",
    "NUASktdfTk": "https://login.microsoftonline.com/TENANT/v2.0",
    "RFFH1lyEc7": "https://d-1234567890.awsapps.com/start",
    "19vfTFVJFY": "/usr/local/bin/corp-cred-helper",
    "/dk65J5QxC": "~/Documents/work",
    "AMhS+KPl2/": "/web-setup",
    "1QdLfinpa0": "openid email https://www.googleapis.com/auth/cloud-platform",
    "1fPbl8sb8U": "api://…/access_as_user offline_access",
    "2pwaqX5iEv": "GOCSPX-...",
    "30xtnSNBGE": "x-forwarded-email",
    "2uv2pR+wD2": "daily-code-review",
    "Kq/aajRMhf": '["https://api.box.com"]',
    "QkbhtcTa4t": "enduser.id",
    "QxWCILUZ/n": "us-west-2",
    "KER1zNW5fX": "alice@example.com",
    "QDztI5xXrQ": "admin@company.com",
    "+gBb3x0fj/": "X-Header-Name",
    "4EAtPWhM42": "Anthropic Sans",
    "LYwfyvAb+2": "p99",
    "MbygIJTreB": "0",
    "NcY80Li7iy": "D/E",
    "N2DECLxiUG": "DD",
    "3ZdJzKs+t/": "false",
    "K0kdPl7COj": "true",
    "MCSWARMox": "(null)",
    "MXPwVkq5Ri": "X",
    "ODGmphVeUJ": "！",
    "/XN7yFRPEj": "CI",
    "4XTG+LtKI0": "PR",
    "4b42RZpF6C": "GHE",
    "CnpuAfeNq+": "DAU",
    "P8Xs51Ghdg": "ROI",
    "OuGz8H1+p1": "CFO",
}

print(f"Loaded {len(NON_TRANSLATABLE_EXACT)} non-translatable exact items.")
