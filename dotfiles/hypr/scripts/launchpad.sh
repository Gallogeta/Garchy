#!/usr/bin/env bash
# ==============================================================================
# 🌌 Garchy OS — Instantaneous 144Hz Fullscreen Launchpad Dashboard (<Super>+Space)
# ==============================================================================

if pidof rofi >/dev/null 2>&1; then
    killall rofi 2>/dev/null
else
    pkill -f "quickshell -p ~/.config/quickshell/launchpad" 2>/dev/null || true
    rofi -show drun -theme ~/.config/rofi/launchpad.rasi -show-icons
fi
