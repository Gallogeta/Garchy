#!/usr/bin/env bash
if pgrep -f "wallpaper-gallery-gui.py" >/dev/null; then
    pkill -f "wallpaper-gallery-gui.py"
else
    python3 "$HOME/.config/hypr/scripts/wallpaper-gallery-gui.py"
fi
