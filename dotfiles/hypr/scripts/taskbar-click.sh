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
            hyprctl eval '
            local wins = hl.get_windows()
            for _, w in ipairs(wins) do
                if w.address == "'"$TARGET_ADDR"'" then
                    hl.dispatch(hl.dsp.window.move({ window = w, workspace = "special:minimized", silent = true }))
                    break
                end
            end
            ' >/dev/null 2>&1
        fi
        ;;
    "maximize-active")
        hyprctl dispatch "hl.dsp.window.fullscreen({ mode = 1 })" >/dev/null 2>&1
        ;;
    "close-active")
        if [ -n "$TARGET_ADDR" ] && [ "$TARGET_ADDR" != "null" ]; then
            hyprctl eval '
            local wins = hl.get_windows()
            for _, w in ipairs(wins) do
                if w.address == "'"$TARGET_ADDR"'" then
                    hl.dispatch(hl.dsp.focus({ window = w }))
                    hl.dispatch(hl.dsp.window.close())
                    break
                end
            end
            ' >/dev/null 2>&1
        fi
        ;;
esac
