#!/usr/bin/env bash

# Hyprland Dynamic Wallpaper Timer & Random Switcher
# Automatically cycles random wallpapers on a timer (default: 10 minutes)
# Directory: ~/Pictures/Wallpapers

WALL_DIR="${WALLPAPERS_DIR:-$HOME/Pictures/Wallpapers}"
PID_FILE="/tmp/hypr_wallpaper_timer.pid"
CURRENT_FILE="/tmp/hypr_current_wallpaper.txt"
DEFAULT_INTERVAL=600 # 10 minutes in seconds

ensure_daemon() {
    if ! pgrep -x "awww-daemon" >/dev/null 2>&1; then
        awww-daemon &
        sleep 0.4
    fi
}

get_wallpapers() {
    if [ ! -d "$WALL_DIR" ]; then
        return 1
    fi
    find "$WALL_DIR" -maxdepth 1 -type f \( \
        -iname "*.jpg" -o \
        -iname "*.jpeg" -o \
        -iname "*.png" -o \
        -iname "*.webp" -o \
        -iname "*.gif" \
    \)
}

set_random_wallpaper() {
    ensure_daemon

    mapfile -t WALLPAPERS < <(get_wallpapers)
    TOTAL=${#WALLPAPERS[@]}

    if [ "$TOTAL" -eq 0 ]; then
        return 1
    fi

    LAST_WALL=""
    if [ -f "$CURRENT_FILE" ]; then
        LAST_WALL=$(cat "$CURRENT_FILE" 2>/dev/null)
    fi

    # Pick random wallpaper, avoiding immediate duplicate if > 1 wallpaper exists
    if [ "$TOTAL" -gt 1 ]; then
        while :; do
            CHOSEN="${WALLPAPERS[$(( RANDOM % TOTAL ))]}"
            [ "$CHOSEN" != "$LAST_WALL" ] && break
        done
    else
        CHOSEN="${WALLPAPERS[0]}"
    fi

    # Randomize transition for subtle visual variety
    TRANSITIONS=("outer" "wipe" "wave" "grow" "center")
    TRANS="${TRANSITIONS[$(( RANDOM % ${#TRANSITIONS[@]} ))]}"

    # Apply wallpaper across all monitors
    awww img "$CHOSEN" --transition-type "$TRANS" --transition-step 90 --transition-fps 144

    echo "$CHOSEN" > "$CURRENT_FILE"
}

start_daemon() {
    local interval="${1:-$DEFAULT_INTERVAL}"

    # Kill other running instances if any
    if [ -f "$PID_FILE" ]; then
        local old_pid
        old_pid=$(cat "$PID_FILE" 2>/dev/null)
        if [ -n "$old_pid" ] && [ "$old_pid" != "$$" ] && kill -0 "$old_pid" 2>/dev/null; then
            kill "$old_pid" 2>/dev/null
        fi
    fi

    echo "$$" > "$PID_FILE"

    # Set initial random wallpaper immediately
    set_random_wallpaper

    # Main timer loop
    while true; do
        sleep "$interval"
        set_random_wallpaper
    done
}

stop_daemon() {
    if [ -f "$PID_FILE" ]; then
        local pid
        pid=$(cat "$PID_FILE" 2>/dev/null)
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null
        fi
        rm -f "$PID_FILE"
    fi
}

case "${1:-daemon}" in
    "daemon"|"start")
        start_daemon "${2:-$DEFAULT_INTERVAL}"
        ;;
    "next"|"random")
        set_random_wallpaper
        ;;
    "stop")
        stop_daemon
        ;;
    "status")
        if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE" 2>/dev/null)" 2>/dev/null; then
            echo "Wallpaper timer is running (PID: $(cat "$PID_FILE"))"
            [ -f "$CURRENT_FILE" ] && echo "Current: $(cat "$CURRENT_FILE")"
        else
            echo "Wallpaper timer is stopped"
        fi
        ;;
    *)
        start_daemon "$DEFAULT_INTERVAL"
        ;;
esac
