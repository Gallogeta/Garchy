#!/usr/bin/env bash
if pgrep -f "theme-switcher-gui.py" >/dev/null; then
    pkill -f "theme-switcher-gui.py"
else
    python3 "$HOME/.config/hypr/scripts/theme-switcher-gui.py"
fi
