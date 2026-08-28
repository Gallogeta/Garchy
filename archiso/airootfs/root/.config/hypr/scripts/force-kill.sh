#!/usr/bin/env bash

# Fetch current active window details from Hyprland
WINDOW_JSON=$(hyprctl activewindow -j 2>/dev/null)

PID=$(echo "$WINDOW_JSON" | jq -r '.pid // empty')
CLASS=$(echo "$WINDOW_JSON" | jq -r '.class // "Window"')
TITLE=$(echo "$WINDOW_JSON" | jq -r '.title // ""')

if [ -n "$PID" ] && [ "$PID" != "null" ] && [ "$PID" != "0" ]; then
    kill -9 "$PID" 2>/dev/null
    notify-send -u normal -t 2500 -a "Hyprland" "Force Killed" "Terminated ${CLASS} (PID: ${PID})"
else
    # Fallback to interactive Hyprland kill cursor
    hyprctl kill
fi
