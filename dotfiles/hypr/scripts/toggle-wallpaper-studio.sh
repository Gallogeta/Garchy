#!/usr/bin/env bash
# ==============================================================================
# 🌌 Garchy OS — Caelestia Wallpaper Studio Toggle
# ==============================================================================

WP_INST=$(quickshell list --all 2>/dev/null | grep -B 2 "caelestia-wallpaper" | grep "Instance" | awk '{print $2}' | tr -d ':')

if [ -n "$WP_INST" ]; then
    quickshell kill --id "$WP_INST" 2>/dev/null || true
    exit 0
fi

# Ensure fresh wallpaper index
python3 "$HOME/.config/hypr/scripts/wallpaper_indexer.py" &

exec quickshell -c caelestia-wallpaper
