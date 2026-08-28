#!/usr/bin/env bash

# Garchy OS — Native Quickshell GPU Launchpad Toggle
QS_DIR="$HOME/.config/quickshell/launchpad"

if pgrep -f "quickshell -p $QS_DIR" >/dev/null 2>&1; then
    pkill -f "quickshell -p $QS_DIR" 2>/dev/null
else
    # Close rofi if open
    killall rofi 2>/dev/null
    
    # Launch Quickshell Launchpad on GPU overlay
    exec quickshell -p "$QS_DIR"
fi
