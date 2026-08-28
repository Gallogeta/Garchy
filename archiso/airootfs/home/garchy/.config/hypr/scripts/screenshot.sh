#!/usr/bin/env bash

DIR="$HOME/Pictures/Screenshots"
mkdir -p "$DIR"
TIMESTAMP="$(date +'%Y-%m-%d_%H-%M-%S')"
FILE="$DIR/screenshot_${TIMESTAMP}.png"

case "$1" in
    "full")
        grim "$FILE"
        wl-copy < "$FILE"
        notify-send -a "Screenshot" "Screenshot Saved" "Full desktop saved & copied to clipboard" -i "$FILE"
        ;;
    "region")
        GEOM=$(slurp)
        if [ -n "$GEOM" ]; then
            grim -g "$GEOM" "$FILE"
            wl-copy < "$FILE"
            notify-send -a "Screenshot" "Area Captured" "Selection saved & copied to clipboard" -i "$FILE"
        fi
        ;;
    "window")
        GEOM=$(hyprctl activewindow -j | jq -r '"\(.at[0]),\(.at[1]) \(.size[0])x\(.size[1])"')
        if [ -n "$GEOM" ] && [ "$GEOM" != "null,null nullxnull" ]; then
            grim -g "$GEOM" "$FILE"
            wl-copy < "$FILE"
            notify-send -a "Screenshot" "Window Captured" "Active window saved & copied to clipboard" -i "$FILE"
        fi
        ;;
    *)
        GEOM=$(slurp)
        if [ -n "$GEOM" ]; then
            grim -g "$GEOM" "$FILE"
            wl-copy < "$FILE"
            notify-send -a "Screenshot" "Area Captured" "Selection saved & copied to clipboard" -i "$FILE"
        fi
        ;;
esac
