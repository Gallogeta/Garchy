#!/usr/bin/env bash
if pgrep -f "gally-ai-hud.py" >/dev/null; then
    pkill -f "gally-ai-hud.py"
else
    python3 "$HOME/.config/hypr/scripts/gally-ai-hud.py"
fi
