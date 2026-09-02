"""Comprehensive translation generator with extensive vocabulary and pattern coverage."""

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(r"C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese")
agent_dir = Path(r"C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese\.agents\worker_m2")

print("Full dataset builder initialized.")
