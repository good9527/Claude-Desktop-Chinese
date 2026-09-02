#!/usr/bin/env bash
set -e

REPO_OWNER="good9527"
REPO_NAME="Claude-Desktop-Chinese"
CACHE_DIR="$HOME/.claude-chinese-patch"
BACKUP_FILE="$CACHE_DIR/en-US-original.json"

echo "=========================================================="
echo "     Claude Desktop Chinese Patch Universal Installer     "
echo "=========================================================="

# Find Claude i18n path on macOS
if [ -d "/Applications/Claude.app" ]; then
    I18N_FILE="/Applications/Claude.app/Contents/Resources/app/resources/ion-dist/i18n/en-US.json"
fi

if [ -z "$I18N_FILE" ] || [ ! -f "$I18N_FILE" ]; then
    echo "Searching for Claude en-US.json..."
    I18N_FILE=$(find /Applications/Claude.app -name "en-US.json" 2>/dev/null | head -n 1 || true)
fi

if [ -z "$I18N_FILE" ] || [ ! -f "$I18N_FILE" ]; then
    echo "Error: Claude Desktop en-US.json not found. Please install Claude first."
    exit 1
fi

echo "Found language file: $I18N_FILE"
mkdir -p "$CACHE_DIR"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Creating clean backup..."
    cp "$I18N_FILE" "$BACKUP_FILE"
fi

# Download dictionary
DICT_FILE="$CACHE_DIR/zh-CN.json"
echo "Downloading latest translation dictionary..."
curl -fsSL "https://fastly.jsdelivr.net/gh/$REPO_OWNER/$REPO_NAME@main/dist/zh-CN.json" -o "$DICT_FILE"

# Python merge
python3 -c "
import json
with open('$I18N_FILE', 'r', encoding='utf-8') as f: en = json.load(f)
with open('$DICT_FILE', 'r', encoding='utf-8') as f: zh = json.load(f)
merged = {k: zh.get(k, v) for k, v in en.items()}
with open('$I18N_FILE', 'w', encoding='utf-8') as f: json.dump(merged, f, ensure_ascii=False, separators=(',', ':'))
print('Successfully patched Claude Desktop!')
"

echo "=========================================================="
echo "     [+] 汉化补丁安装成功！(Patch Successfully Installed) "
echo "=========================================================="
