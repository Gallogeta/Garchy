#!/usr/bin/env bash

ACTION="${1:-minimize-active}"

get_target_addr() {
    # 1. Try activewindow
    local ADDR
    ADDR=$(hyprctl activewindow -j 2>/dev/null | jq -r '.address // empty')
    if [ -n "$ADDR" ] && [ "$ADDR" != "null" ] && [ "$ADDR" != "0x0" ]; then
        echo "$ADDR"
        return
    fi
    # 2. Fallback to most recent focused window (focusHistoryID == 0)
    ADDR=$(hyprctl clients -j 2>/dev/null | jq -r '[.[] | select(.workspace.name | startswith("special") | not)] | sort_by(.focusHistoryID) | .[0].address // empty')
    echo "$ADDR"
}

TARGET_ADDR=$(get_target_addr)

case "$ACTION" in
    "minimize-active"|"toggle-active")
        if [ -n "$TARGET_ADDR" ] && [ "$TARGET_ADDR" != "null" ]; then
            hyprctl dispatch movetoworkspacesilent "special:minimized,address:$TARGET_ADDR"
        fi
        ;;
    "maximize-active")
        if [ -n "$TARGET_ADDR" ] && [ "$TARGET_ADDR" != "null" ]; then
            hyprctl dispatch fullscreen 1
        fi
        ;;
    "close-active")
        if [ -n "$TARGET_ADDR" ] && [ "$TARGET_ADDR" != "null" ]; then
            hyprctl dispatch closewindow "address:$TARGET_ADDR"
        fi
        ;;
esac
