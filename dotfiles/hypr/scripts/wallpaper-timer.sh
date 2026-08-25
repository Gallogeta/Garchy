#!/usr/bin/env bash

# Hyprland Dynamic Wallpaper Timer & Random Switcher
# Automatically cycles random wallpapers on a timer based on ~/.config/gally/wallpaper_config.json
# Supports multiple custom wallpaper directories and user-configured intervals.

CONFIG_FILE="$HOME/.config/gally/wallpaper_config.json"
PID_FILE="/tmp/hypr_wallpaper_timer.pid"
CURRENT_FILE="/tmp/hypr_current_wallpaper.txt"
DEFAULT_INTERVAL=600 # 10 minutes in seconds

ensure_daemon() {
    if ! pgrep -x "awww-daemon" >/dev/null 2>&1; then
        awww-daemon &
        sleep 0.4
    fi
}

load_config_dirs() {
    local dirs=()
    if [ -f "$CONFIG_FILE" ]; then
        # Parse JSON directories array using python
        while IFS= read -r dir; do
            [ -n "$dir" ] && [ -d "$dir" ] && dirs+=("$dir")
        done < <(python3 -c "
import json, os
try:
    with open('$CONFIG_FILE') as f:
        data = json.load(f)
        for d in data.get('directories', []):
            exp = os.path.expanduser(d)
            if os.path.isdir(exp):
                print(exp)
except Exception:
    pass
" 2>/dev/null)
    fi

    if [ ${#dirs[@]} -eq 0 ]; then
        dirs=("$HOME/Pictures/Wallpapers")
    fi
    echo "${dirs[@]}"
}

get_config_interval() {
    local interval=$DEFAULT_INTERVAL
    if [ -f "$CONFIG_FILE" ]; then
        local val
        val=$(python3 -c "
import json
try:
    with open('$CONFIG_FILE') as f:
        data = json.load(f)
        if not data.get('timer_enabled', True):
            print('0')
        else:
            mins = int(data.get('interval_minutes', 10))
            print(max(30, mins * 60))
except Exception:
    print('$DEFAULT_INTERVAL')
" 2>/dev/null)
        [ -n "$val" ] && interval="$val"
    fi
    echo "$interval"
}

get_wallpapers() {
    local dirs
    read -r -a dirs <<< "$(load_config_dirs)"
    
    for dir in "${dirs[@]}"; do
        if [ -d "$dir" ]; then
            find "$dir" -maxdepth 2 -type f \( \
                -iname "*.jpg" -o \
                -iname "*.jpeg" -o \
                -iname "*.png" -o \
                -iname "*.webp" -o \
                -iname "*.gif" \
            \)
        fi
    done
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

    if [ "$TOTAL" -gt 1 ]; then
        while :; do
            CHOSEN="${WALLPAPERS[$(( RANDOM % TOTAL ))]}"
            [ "$CHOSEN" != "$LAST_WALL" ] && break
        done
    else
        CHOSEN="${WALLPAPERS[0]}"
    fi

    TRANSITIONS=("outer" "wipe" "wave" "grow" "center")
    TRANS="${TRANSITIONS[$(( RANDOM % ${#TRANSITIONS[@]} ))]}"

    awww img "$CHOSEN" --transition-type "$TRANS" --transition-step 90 --transition-fps 144
    echo "$CHOSEN" > "$CURRENT_FILE"
}

start_daemon() {
    local interval="$1"
    if [ -z "$interval" ]; then
        interval=$(get_config_interval)
    fi

    if [ "$interval" -le 0 ]; then
        echo "Wallpaper timer is disabled in config."
        stop_daemon
        return 0
    fi

    # Kill other running instances if any
    if [ -f "$PID_FILE" ]; then
        local old_pid
        old_pid=$(cat "$PID_FILE" 2>/dev/null)
        if [ -n "$old_pid" ] && [ "$old_pid" != "$$" ] && kill -0 "$old_pid" 2>/dev/null; then
            kill "$old_pid" 2>/dev/null
        fi
    fi

    echo "$$" > "$PID_FILE"

    # Main timer loop
    while true; do
        sleep "$interval"
        # Re-check config interval dynamically
        local cur_int
        cur_int=$(get_config_interval)
        if [ "$cur_int" -le 0 ]; then
            echo "Timer disabled, stopping daemon."
            break
        fi
        interval="$cur_int"
        set_random_wallpaper
    done
    rm -f "$PID_FILE"
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
        start_daemon "$2"
        ;;
    "next"|"random")
        set_random_wallpaper
        ;;
    "stop")
        stop_daemon
        ;;
    "status")
        if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE" 2>/dev/null)" 2>/dev/null; then
            echo "Wallpaper timer is running (PID: $(cat "$PID_FILE"), Interval: $(get_config_interval)s)"
            [ -f "$CURRENT_FILE" ] && echo "Current: $(cat "$CURRENT_FILE")"
        else
            echo "Wallpaper timer is stopped"
        fi
        ;;
    *)
        start_daemon "$2"
        ;;
esac
