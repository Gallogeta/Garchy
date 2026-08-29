#!/usr/bin/env bash
# Garchy OS — Native Quickshell Theme Gallery Toggle

if pgrep -f "quickshell.*theme-switcher" >/dev/null; then
    pkill -f "quickshell.*theme-switcher"
else
    setsid quickshell -c "$HOME/.config/quickshell/theme-switcher" >/dev/null 2>&1 &
fi
