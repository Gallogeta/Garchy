#!/usr/bin/env bash
if pgrep -x "gnome-calendar" >/dev/null 2>&1; then
    killall gnome-calendar 2>/dev/null
else
    gnome-calendar &
fi
