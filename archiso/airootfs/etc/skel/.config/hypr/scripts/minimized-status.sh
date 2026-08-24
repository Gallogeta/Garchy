#!/usr/bin/env bash

# Fetch all minimized windows from special workspaces
MINIMIZED_JSON=$(hyprctl clients -j 2>/dev/null | jq -c '[.[] | select(.workspace.name | startswith("special"))]')
COUNT=$(echo "$MINIMIZED_JSON" | jq 'length')

if [ -n "$COUNT" ] && [ "$COUNT" -gt 0 ]; then
    TITLES=$(echo "$MINIMIZED_JSON" | jq -r '.[].title' | head -n 5)
    FIRST_TITLE=$(echo "$MINIMIZED_JSON" | jq -r '.[0].class // .[0].title')
    
    if [ "$COUNT" -eq 1 ]; then
        TEXT="󰖯 Minimized: ${FIRST_TITLE:0:15}"
    else
        TEXT="󰖯 Minimized ($COUNT)"
    fi
    
    TOOLTIP="🗔 Minimized Windows ($COUNT):\n"
    while IFS= read -r line; do
        [ -n "$line" ] && TOOLTIP="${TOOLTIP}• ${line:0:40}\n"
    done <<< "$TITLES"
    TOOLTIP="${TOOLTIP}───────────────────────\n• Left Click: RESTORE to active screen\n• Right Click: Minimized Windows Manager"
    
    echo "{\"text\":\"$TEXT\",\"tooltip\":\"$TOOLTIP\",\"class\":\"has-minimized\"}"
else
    echo "{\"text\":\"\",\"tooltip\":\"No minimized windows\",\"class\":\"empty\"}"
fi
