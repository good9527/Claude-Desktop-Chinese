#!/usr/bin/env bash
set -e

# ==========================================================
#     Claude Desktop Chinese Patch Universal Installer
#     Supports: macOS (Apple Silicon / Intel) & Linux
# ==========================================================

REPO_OWNER="good9527"
REPO_NAME="Claude-Desktop-Chinese"
CACHE_DIR="$HOME/.claude-chinese-patch"
BACKUP_FILE="$CACHE_DIR/en-US-original.json"
CACHED_DICT="$CACHE_DIR/zh-CN.json"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_DICT="$SCRIPT_DIR/dist/zh-CN.json"

ACTION="install"
for arg in "$@"; do
    case "$arg" in
        --restore|-r|--uninstall|-u) ACTION="restore" ;;
        --check|-c) ACTION="check" ;;
    esac
done

# 1. Locate Claude i18n file
I18N_FILE=""
CANDIDATES=(
    "/Applications/Claude.app/Contents/Resources/app/resources/ion-dist/i18n/en-US.json"
    "$HOME/Applications/Claude.app/Contents/Resources/app/resources/ion-dist/i18n/en-US.json"
    "/usr/share/claude/resources/app/resources/ion-dist/i18n/en-US.json"
    "/opt/Claude/resources/app/resources/ion-dist/i18n/en-US.json"
    "$HOME/.local/share/claude/resources/app/resources/ion-dist/i18n/en-US.json"
)

for path in "${CANDIDATES[@]}"; do
    if [ -f "$path" ]; then
        I18N_FILE="$path"
        break
    fi
done

if [ -z "$I18N_FILE" ] && [ -d "/Applications/Claude.app" ]; then
    I18N_FILE=$(find /Applications/Claude.app -name "en-US.json" 2>/dev/null | grep "ion-dist" | head -n 1 || true)
fi

if [ "$ACTION" == "check" ]; then
    echo "=========================================================="
    echo "     Claude Desktop Chinese Patch Diagnostics (Unix)      "
    echo "=========================================================="
    echo "  Language File Location : ${I18N_FILE:-NOT FOUND}"
    echo "  Backup File Present    : $([ -f "$BACKUP_FILE" ] && echo "PRESENT [OK]" || echo "MISSING")"
    echo "=========================================================="
    exit $([ -n "$I18N_FILE" ] && echo 0 || echo 1)
fi

if [ "$ACTION" == "restore" ]; then
    if [ -n "$I18N_FILE" ] && [ -f "$BACKUP_FILE" ]; then
        cp "$BACKUP_FILE" "$I18N_FILE"
        echo "Successfully restored official English language file!"
        exit 0
    else
        echo "Error: Cannot restore. Backup file or Claude installation not found."
        exit 1
    fi
fi

if [ -z "$I18N_FILE" ] || [ ! -f "$I18N_FILE" ]; then
    echo "Error: Claude Desktop en-US.json not found. Please ensure Claude Desktop is installed."
    exit 1
fi

echo "Target language file: $I18N_FILE"
mkdir -p "$CACHE_DIR"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Creating clean official backup..."
    cp "$I18N_FILE" "$BACKUP_FILE"
fi

# 2. Acquire dictionary (Local -> Multi-CDN)
if [ -f "$LOCAL_DICT" ]; then
    echo "Loading dictionary from local package..."
    cp "$LOCAL_DICT" "$CACHED_DICT"
elif [ ! -f "$CACHED_DICT" ]; then
    echo "Downloading dictionary via multi-source CDN..."
    MIRRORS=(
        "https://fastly.jsdelivr.net/gh/$REPO_OWNER/$REPO_NAME@main/dist/zh-CN.json"
        "https://cdn.jsdelivr.net/gh/$REPO_OWNER/$REPO_NAME@main/dist/zh-CN.json"
        "https://ghfast.top/https://raw.githubusercontent.com/$REPO_OWNER/$REPO_NAME/main/dist/zh-CN.json"
        "https://raw.githubusercontent.com/$REPO_OWNER/$REPO_NAME/main/dist/zh-CN.json"
    )
    DOWNLOADED=false
    for url in "${MIRRORS[@]}"; do
        if curl -fsSL "$url" -o "$CACHED_DICT" 2>/dev/null && [ -s "$CACHED_DICT" ]; then
            DOWNLOADED=true
            break
        fi
    done
    if [ "$DOWNLOADED" != "true" ]; then
        echo "Error: Failed to download translation dictionary. Please check your network."
        exit 1
    fi
fi

# 3. Apply Merge in Python
python3 -c "
import json
with open('$I18N_FILE', 'r', encoding='utf-8') as f: en = json.load(f)
with open('$CACHED_DICT', 'r', encoding='utf-8') as f: zh = json.load(f)
merged = {k: zh.get(k, v) for k, v in en.items()}
with open('$I18N_FILE', 'w', encoding='utf-8') as f: json.dump(merged, f, ensure_ascii=False, separators=(',', ':'))
print('Successfully patched Claude Desktop!')
"

echo "=========================================================="
echo "     [+] 汉化补丁安装成功！(Patch Successfully Installed) "
echo "=========================================================="
