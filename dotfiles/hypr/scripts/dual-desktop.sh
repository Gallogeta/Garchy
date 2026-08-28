#!/usr/bin/env bash

# Synchronized Dual-Monitor Desktop Switcher for Hyprland 0.56.2+
# Pairs Workspaces:
# Desktop 1  -> DP-2 (WS 1),  DP-1 (WS 2)
# Desktop 2  -> DP-2 (WS 3),  DP-1 (WS 4)
# Desktop 3  -> DP-2 (WS 5),  DP-1 (WS 6)
# Desktop 4  -> DP-2 (WS 7),  DP-1 (WS 8)
# Desktop 5  -> DP-2 (WS 9),  DP-1 (WS 10)
# Desktop 6  -> DP-2 (WS 11), DP-1 (WS 12)
# Desktop 7  -> DP-2 (WS 13), DP-1 (WS 14)
# Desktop 8  -> DP-2 (WS 15), DP-1 (WS 16)
# Desktop 9  -> DP-2 (WS 17), DP-1 (WS 18)
# Desktop 10 -> DP-2 (WS 19), DP-1 (WS 20)

ACTION="${1:-switch}"
NUM="${2:-1}"

# Clamp NUM to 1..10 (0 maps to 10)
if [ "$NUM" -eq 0 ]; then
    NUM=10
fi
if [ "$NUM" -lt 1 ] || [ "$NUM" -gt 10 ]; then
    NUM=1
fi

LEFT_WS=$(( 2 * NUM - 1 ))
RIGHT_WS=$(( 2 * NUM ))

case "$ACTION" in
    "switch")
        # Atomically switch both monitors
        hyprctl --batch "dispatch hl.dsp.focus({ workspace = $LEFT_WS }); dispatch hl.dsp.focus({ workspace = $RIGHT_WS })"
        ;;

    "move")
        # Identify which monitor the active window is on
        ACTIVE_WIN=$(hyprctl activewindow -j 2>/dev/null)
        ADDR=$(echo "$ACTIVE_WIN" | jq -r '.address // empty')
        MON_NAME=$(echo "$ACTIVE_WIN" | jq -r '.monitor // empty')

        if [ -n "$ADDR" ]; then
            if [ "$MON_NAME" = "0" ] || [ "$MON_NAME" = "DP-1" ]; then
                TARGET_WS=$RIGHT_WS
            else
                TARGET_WS=$LEFT_WS
            fi
            hyprctl dispatch "hl.dsp.window.move({ workspace = $TARGET_WS })"
        fi
        ;;

    "move-silent")
        ACTIVE_WIN=$(hyprctl activewindow -j 2>/dev/null)
        ADDR=$(echo "$ACTIVE_WIN" | jq -r '.address // empty')
        MON_NAME=$(echo "$ACTIVE_WIN" | jq -r '.monitor // empty')

        if [ -n "$ADDR" ]; then
            if [ "$MON_NAME" = "0" ] || [ "$MON_NAME" = "DP-1" ]; then
                TARGET_WS=$RIGHT_WS
            else
                TARGET_WS=$LEFT_WS
            fi
            hyprctl dispatch "hl.dsp.window.move({ workspace = $TARGET_WS })"
        fi
        ;;
esac
