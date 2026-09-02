import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
agent_dir = Path(r"C:\Users\19901\.gemini\antigravity\scratch\Claude-Desktop-Chinese\.agents\worker_m2")
untranslated = json.load(open(agent_dir / "untranslated_raw.json", "r", encoding="utf-8"))

# Check how many strings start with common sentence beginnings
patterns = [
    r"^(?:You|Your|You’re|You’ve|You’ll|You’d)\b",
    r"^(?:This|These|That|Those)\b",
    r"^(?:Couldn’t|Could not|Can’t|Cannot|Failed to|Unable to)\b",
    r"^(?:Please|Select|Enter|Choose|Add|Remove|Delete|Create|Edit|View|Show|Hide|Open|Close|Save|Cancel|Allow|Deny|Enable|Disable|Connect|Disconnect|Sign in|Sign out|Log in|Log out|Turn on|Turn off|Manage|Configure|Set up|Setting|Search|Filter|Sort|Upload|Download|Export|Import|Share|Publish|Unpublish|Copy|Paste|Retry|Refresh|Check|Clear|Reset)\b",
    r"^(?:Claude|Anthropic|Google|GitHub|Microsoft|Slack|Chrome|AWS|Bedrock|Vertex)\b",
    r"^(?:Are you sure|Do you want to|Would you like to|How do I|Why is|What is)\b",
    r"^(?:Only|All|Some|No|Any|Each|Every)\b",
    r"^(?:If|When|Once|After|Before|While)\b",
]

matched = 0
for k, v in untranslated.items():
    if any(re.search(p, v, re.IGNORECASE) for p in patterns):
        matched += 1

print(f"Total untranslated: {len(untranslated)}")
print(f"Matched common sentence beginnings: {matched} ({matched/len(untranslated):.2%})")
