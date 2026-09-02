import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
agent_dir = Path(r"C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese\.agents\worker_m2")
untranslated = json.load(open(agent_dir / "untranslated_raw.json", "r", encoding="utf-8"))

domains = {
    "icu": [],
    "symbols_urls_code": [],
    "short_labels": [],
    "errors_dialogs": [],
    "settings_org_billing": [],
    "projects_mcp_artifacts": [],
    "prompts_sentences": [],
    "other": [],
}

for k, v in untranslated.items():
    s = v.strip()
    if re.search(r'\{[^{}]+,\s*(?:plural|select|selectordinal)', v):
        domains["icu"].append((k, v))
    elif not re.search(r'[a-zA-Z]', s) or re.match(r'^(?:https?://|mailto:|api://|wss://|urn:)\S+$', s) or s.startswith(('/', '~/', './')):
        domains["symbols_urls_code"].append((k, v))
    elif len(re.findall(r'[a-zA-Z]+', s)) <= 3 and not '{' in s:
        domains["short_labels"].append((k, v))
    elif any(word in s.lower() for word in ["couldn’t", "failed to", "unable to", "can’t", "cannot", "error", "warning", "are you sure", "confirm"]):
        domains["errors_dialogs"].append((k, v))
    elif any(word in s.lower() for word in ["setting", "organization", "org", "member", "role", "billing", "plan", "seat", "invoice", "spend limit", "subscription", "sso", "scim", "saml"]):
        domains["settings_org_billing"].append((k, v))
    elif any(word in s.lower() for word in ["project", "mcp", "connector", "artifact", "tool", "server", "computer use", "context window", "thinking mode", "cowork", "claude code"]):
        domains["projects_mcp_artifacts"].append((k, v))
    elif len(re.findall(r'[a-zA-Z]+', s)) > 6:
        domains["prompts_sentences"].append((k, v))
    else:
        domains["other"].append((k, v))

for d, items in domains.items():
    print(f"Domain '{d}': {len(items)} keys")

with open(agent_dir / "domains.json", "w", encoding="utf-8") as f:
    json.dump({d: dict(items) for d, items in domains.items()}, f, ensure_ascii=False, indent=2)
