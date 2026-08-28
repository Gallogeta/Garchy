#!/usr/bin/env bash
if pgrep -f "garchy-ai-hud.py" >/dev/null; then
    pkill -f "garchy-ai-hud.py"
else
    python3 "$HOME/.config/hypr/scripts/garchy-ai-hud.py"
fi
