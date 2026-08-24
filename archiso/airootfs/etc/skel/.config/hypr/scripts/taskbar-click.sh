#!/usr/bin/env bash

ACTION="${1:-toggle-active}"

case "$ACTION" in
    "minimize-active")
        ADDR=$(hyprctl activewindow -j 2>/dev/null | jq -r '.address // empty')
        if [ -n "$ADDR" ] && [ "$ADDR" != "null" ]; then
            hyprctl dispatch movetoworkspacesilent "special:minimized,address:$ADDR"
        fi
        ;;
    "maximize-active")
        hyprctl dispatch fullscreen 1
        ;;
    "close-active")
        ADDR=$(hyprctl activewindow -j 2>/dev/null | jq -r '.address // empty')
        if [ -n "$ADDR" ] && [ "$ADDR" != "null" ]; then
            hyprctl dispatch closewindow "address:$ADDR"
        fi
        ;;
    "toggle-active")
        ADDR=$(hyprctl activewindow -j 2>/dev/null | jq -r '.address // empty')
        if [ -n "$ADDR" ] && [ "$ADDR" != "null" ]; then
            hyprctl dispatch movetoworkspacesilent "special:minimized,address:$ADDR"
        fi
        ;;
esac
