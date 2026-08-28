#!/usr/bin/env bash
if pgrep -f "launchpad-gui.py" >/dev/null; then
    pkill -f "launchpad-gui.py"
else
    python3 "$HOME/.config/hypr/scripts/launchpad-gui.py"
fi
