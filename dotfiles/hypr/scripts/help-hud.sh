#!/usr/bin/env bash
if pgrep -f "help-hud.py" >/dev/null; then
    pkill -f "help-hud.py"
else
    python3 "$HOME/.config/hypr/scripts/help-hud.py"
fi
