#!/usr/bin/env bash
# ==============================================================================
# 🌌 Garchy OS — Real-Time Low Disk Space Guardian
# Warns user with critical notifications & status badge when free space < 5 GB.
# ==============================================================================

THRESHOLD_MB=5120  # 5 GB in Megabytes
CRITICAL_MB=2048   # 2 GB emergency critical threshold
STATUS_FILE="/tmp/garchy_disk_status.json"
LAST_NOTIF_FILE="/tmp/garchy_disk_last_notif"

# Get available disk space on root filesystem (in MB)
AVAIL_MB=$(df -m / | awk 'NR==2 {print $4}')

# Calculate GB for human-readable display
AVAIL_GB=$(awk "BEGIN {printf \"%.1f\", $AVAIL_MB / 1024}")
TOTAL_GB=$(df -h / | awk 'NR==2 {print $2}')
USE_PCT=$(df -h / | awk 'NR==2 {print $5}')

# Write status JSON for Quickshell Garchy Bar
if [ "$AVAIL_MB" -le "$THRESHOLD_MB" ]; then
    IS_LOW=true
else
    IS_LOW=false
fi

cat <<EOF > "$STATUS_FILE.tmp"
{
  "warning": $IS_LOW,
  "avail_mb": $AVAIL_MB,
  "avail_gb": "$AVAIL_GB",
  "total_gb": "$TOTAL_GB",
  "use_pct": "$USE_PCT",
  "threshold_gb": 5
}
EOF
mv "$STATUS_FILE.tmp" "$STATUS_FILE"

# If space is below 5 GB threshold, send notification
if [ "$AVAIL_MB" -le "$THRESHOLD_MB" ]; then
    NOW=$(date +%s)
    LAST_NOTIF=0
    [ -f "$LAST_NOTIF_FILE" ] && LAST_NOTIF=$(cat "$LAST_NOTIF_FILE")

    # Throttle notifications: warn at most once every 5 minutes (or immediately if < 2GB)
    TIME_DIFF=$((NOW - LAST_NOTIF))
    if [ "$TIME_DIFF" -ge 300 ] || [ "$AVAIL_MB" -le "$CRITICAL_MB" ]; then
        if [ "$AVAIL_MB" -le "$CRITICAL_MB" ]; then
            URGENCY="critical"
            TITLE="🚨 CRITICAL DISK SPACE: ONLY ${AVAIL_GB} GB LEFT!"
            BODY="System disk is nearly FULL (${USE_PCT} used of ${TOTAL_GB}). System stability and save games may fail! Clean files immediately."
        else
            URGENCY="critical"
            TITLE="⚠️ LOW DISK SPACE WARNING (< 5 GB)"
            BODY="Root filesystem has only ${AVAIL_GB} GB remaining (${USE_PCT} used). Consider clearing package and browser caches."
        fi

        notify-send -u "$URGENCY" \
                    -i "drive-harddisk-warning" \
                    -a "Garchy Disk Guardian" \
                    "$TITLE" "$BODY"

        # Play warning sound if canberra or paplay available
        if command -v paplay >/dev/null 2>&1 && [ -f "/usr/share/sounds/freedesktop/stereo/dialog-warning.oga" ]; then
            paplay /usr/share/sounds/freedesktop/stereo/dialog-warning.oga 2>/dev/null &
        fi

        echo "$NOW" > "$LAST_NOTIF_FILE"
    fi
fi
