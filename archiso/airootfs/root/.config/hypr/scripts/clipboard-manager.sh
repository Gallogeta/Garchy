#!/usr/bin/env bash

# Riced Rofi Clipboard History Manager using Cliphist
# Press Super+V to open, Enter to paste, Shift+Del to remove item

if ! command -v cliphist >/dev/null 2>&1; then
    notify-send -a "Clipboard" "cliphist is not installed"
    exit 1
fi

SELECTED=$(cliphist list | rofi -dmenu -i -p "󰅍 Clipboard History" -mesg "Enter to Paste | Type to search history" -config ~/.config/rofi/config.rasi)

if [ -n "$SELECTED" ]; then
    echo "$SELECTED" | cliphist decode | wl-copy
    notify-send -a "Clipboard" -t 1000 "Copied to Clipboard" "${SELECTED:0:40}..."
    # Auto-paste into focused window
    sleep 0.15
    wtype -M ctrl -k v -m ctrl 2>/dev/null || ydotool key 29:1 47:1 47:0 29:0 2>/dev/null || hyprctl dispatch sendshortcut "CTRL,v,activewindow" 2>/dev/null
fi
