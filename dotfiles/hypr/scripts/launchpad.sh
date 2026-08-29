#!/usr/bin/env bash
# ==============================================================================
# 🌌 Garchy OS — Caelestia Launchpad & Command HUD (<Super>+Space)
# ==============================================================================

LP_INST=$(quickshell list --all 2>/dev/null | grep -B 2 "caelestia-launchpad" | grep "Instance" | awk '{print $2}' | tr -d ':')

if [ -n "$LP_INST" ]; then
    quickshell kill --id "$LP_INST" 2>/dev/null || true
    exit 0
fi

killall rofi 2>/dev/null || true

exec quickshell -c caelestia-launchpad
