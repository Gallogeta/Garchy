#!/usr/bin/env bash

# Garchy Linux - Autonomous Background System Updater
# Safely updates packages with Btrfs/Snapper snapshot protection

LOG_FILE="/tmp/garchy-update.log"
NOTIFY_TITLE="Garchy System"

notify() {
    local msg="$1"
    local urgency="${2:-normal}"
    if command -v notify-send >/dev/null 2>&1; then
        notify-send -u "$urgency" -a "$NOTIFY_TITLE" "System Update" "$msg"
    fi
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $msg" | tee -a "$LOG_FILE"
}

# 1. Check network connectivity
if ! ping -c 1 -W 2 archlinux.org >/dev/null 2>&1; then
    echo "No internet connection. Skipping update."
    exit 0
fi

# 2. Check if updates exist
if command -v checkupdates >/dev/null 2>&1; then
    UPDATES=$(checkupdates 2>/dev/null)
    COUNT=$(echo "$UPDATES" | grep -c -v '^$' || true)
    if [ "$COUNT" -eq 0 ]; then
        echo "System is already up to date."
        exit 0
    fi
else
    COUNT="available"
fi

# 3. Create Btrfs Snapshot if Snapper is available
SNAPSHOT_MSG=""
if command -v snapper >/dev/null 2>&1; then
    SNAP_NAME="Pre-Garchy-Auto-Update-$(date +'%Y-%m-%d_%H-%M')"
    if sudo snapper create -c timeline -d "$SNAP_NAME" 2>/dev/null; then
        SNAPSHOT_MSG=" (Snapshot created)"
    fi
fi

# 4. Perform package upgrade cleanly
notify "Updating packages in background ($COUNT updates)${SNAPSHOT_MSG}..." "low"

if sudo pacman -Syu --noconfirm >> "$LOG_FILE" 2>&1; then
    # 5. Prune package cache
    if command -v paccache >/dev/null 2>&1; then
        sudo paccache -rk2 >/dev/null 2>&1 || true
    fi
    notify "System update completed successfully!${SNAPSHOT_MSG}" "normal"
else
    notify "Update encountered an issue. Check /tmp/garchy-update.log" "critical"
    exit 1
fi
