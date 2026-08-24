#!/usr/bin/env bash
# Garchy Launchpad Toggle
if pgrep -x "rofi" >/dev/null; then
    pkill -x "rofi"
else
    rofi -show drun -theme "$HOME/.config/rofi/launchpad.rasi"
fi
