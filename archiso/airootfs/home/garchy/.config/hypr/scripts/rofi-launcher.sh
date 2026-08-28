#!/usr/bin/env bash

# Multi-Tool Super Launcher for Hyprland
# Modes: drun (default), clip, calc, window

MODE="${1:-drun}"

case "$MODE" in
    "clip"|"clipboard")
        $HOME/.config/hypr/scripts/clipboard-manager.sh
        ;;
    "window"|"windows")
        $HOME/.config/hypr/scripts/window-switch.sh
        ;;
    "calc"|"calculator")
        QUERY=$(rofi -dmenu -p "󰪚 Calculator" -mesg "Enter math expression (e.g. 250 * 1.25, sqrt(144), 2**10)" -config ~/.config/rofi/config.rasi)
        if [ -n "$QUERY" ]; then
            RESULT=$(python3 -c "import math; from math import *; print($QUERY)" 2>&1)
            if [ $? -eq 0 ]; then
                echo -n "$RESULT" | wl-copy
                notify-send -a "Calculator" "Result: $RESULT" "Copied to clipboard!"
            else
                notify-send -a "Calculator" "Error evaluating math expression" "$RESULT"
            fi
        fi
        ;;
    *)
        rofi -show drun -config ~/.config/rofi/config.rasi
        ;;
esac
