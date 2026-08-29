#!/usr/bin/env bash
# ==============================================================================
# 🌌 Garchy OS — Universal Module Toggle Daemon
# ==============================================================================

ACTION="$1"

case "$ACTION" in
    "btop")
        if pgrep -f "btop" >/dev/null 2>&1; then
            pkill -f "btop" 2>/dev/null || true
            exit 0
        fi
        kitty --class garchy-btop -T "Garchy System Monitor (btop)" -e btop &
        ;;
    "ai")
        bash "$HOME/.config/hypr/scripts/gally-ai-hud.sh" &
        ;;
    "theme")
        if pgrep -f "theme-switcher.sh" >/dev/null 2>&1 || pgrep -x "rofi" >/dev/null 2>&1; then
            pkill -f "theme-switcher.sh" 2>/dev/null || true
            pkill -x "rofi" 2>/dev/null || true
            exit 0
        fi
        bash "$HOME/.config/hypr/scripts/theme-switcher.sh" &
        ;;
    "calendar")
        if pgrep -x "gnome-calendar" >/dev/null 2>&1 || pgrep -x "korganizer" >/dev/null 2>&1; then
            pkill -x "gnome-calendar" 2>/dev/null || pkill -x "korganizer" 2>/dev/null || true
            exit 0
        fi
        gnome-calendar || korganizer || xfce4-calendar &
        ;;
    "pavucontrol")
        if pgrep -x "pavucontrol" >/dev/null 2>&1; then
            pkill -x "pavucontrol" 2>/dev/null || true
            exit 0
        fi
        pavucontrol &
        ;;
    *)
        echo "Usage: garchy-toggle.sh [btop|ai|theme|calendar|pavucontrol]"
        ;;
esac
