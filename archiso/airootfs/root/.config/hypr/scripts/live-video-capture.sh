#!/usr/bin/env bash

# Live Video Stream & Window Snapshot for Desktop Music & Mini Video Player
OUTPUT_FILE="/tmp/live_video_thumb.jpg"
META_FILE="/tmp/live_video_meta.json"

CLIENTS=$(hyprctl clients -j 2>/dev/null)

# Check for visible browser/video window on active workspace (ws > 0)
WIN_INFO=$(echo "$CLIENTS" | jq -c '
    [.[] | select(
        (.class == "brave-browser" or .class == "firefox" or .class == "chromium" or .class == "google-chrome" or .class == "mpv" or .class == "vlc")
        and .workspace.id > 0
    )] | first
')

# Fallback: check any browser window even if minimized
ANY_BROWSER=$(echo "$CLIENTS" | jq -c '
    [.[] | select(
        .class == "brave-browser" or .class == "firefox" or .class == "chromium" or .class == "google-chrome" or .class == "mpv" or .class == "vlc"
    )] | first
')

ADDR=$(echo "$ANY_BROWSER" | jq -r '.address // empty')
TITLE=$(echo "$ANY_BROWSER" | jq -r '.title // empty')

if [ -n "$WIN_INFO" ] && [ "$WIN_INFO" != "null" ]; then
    X=$(echo "$WIN_INFO" | jq -r '.at[0]')
    Y=$(echo "$WIN_INFO" | jq -r '.at[1]')
    W=$(echo "$WIN_INFO" | jq -r '.size[0]')
    H=$(echo "$WIN_INFO" | jq -r '.size[1]')
    
    if [ -n "$X" ] && [ -n "$W" ] && [ "$W" -gt 50 ]; then
        grim -g "${X},${Y} ${W}x${H}" -s 0.2 "$OUTPUT_FILE.tmp" 2>/dev/null && mv "$OUTPUT_FILE.tmp" "$OUTPUT_FILE"
        echo "{\"hasLive\": true, \"address\": \"$ADDR\", \"title\": $(echo "$TITLE" | jq -R .)}" > "$META_FILE"
        exit 0
    fi
fi

if [ -n "$ADDR" ]; then
    echo "{\"hasLive\": false, \"address\": \"$ADDR\", \"title\": $(echo "$TITLE" | jq -R .)}" > "$META_FILE"
else
    echo '{"hasLive": false}' > "$META_FILE"
fi
