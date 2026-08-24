#!/usr/bin/env bash

# Query number of minimized / special workspace windows
count=$(hyprctl clients -j 2>/dev/null | jq '[.[] | select(.workspace.name | startswith("special"))] | length')

if [ -n "$count" ] && [ "$count" -gt 0 ]; then
    echo "{\"text\":\"󰖯 $count Minimized\",\"tooltip\":\"$count window(s) minimized. Click to restore.\",\"class\":\"has-minimized\"}"
else
    echo "{\"text\":\"\",\"tooltip\":\"No minimized windows\",\"class\":\"empty\"}"
fi
