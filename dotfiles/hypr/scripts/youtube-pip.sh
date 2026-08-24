#!/usr/bin/env bash

# Floating Picture-in-Picture YouTube & Video Player via MPV with Persistent History
URL="$1"

if [ -z "$URL" ]; then
    # 1. Check live clipboard
    CLIP=$(wl-paste 2>/dev/null | tr -d '\n\r' | xargs)

    # 2. If clipboard is empty or lacks URL (e.g. Brave closed), restore from cliphist
    if [[ ! "$CLIP" =~ ^https?:// ]] && command -v cliphist >/dev/null 2>&1; then
        HIST_URL=$(cliphist list 2>/dev/null | grep -m 1 -E 'https?://' | cliphist decode 2>/dev/null | tr -d '\n\r' | xargs)
        if [[ "$HIST_URL" =~ ^https?:// ]]; then
            CLIP="$HIST_URL"
        fi
    fi

    # 3. Build interactive menu with recent links
    ITEMS=""
    if [[ "$CLIP" =~ ^https?:// ]]; then
        ITEMS="󰕼 Play Copied Link: $CLIP\n"
    fi

    # Add other recent links from cliphist
    if command -v cliphist >/dev/null 2>&1; then
        while IFS= read -r line; do
            if [ -n "$line" ] && [[ "$line" != "$CLIP" ]]; then
                ITEMS="${ITEMS}󰕼 History: $line\n"
            fi
        done < <(cliphist list 2>/dev/null | grep -E 'https?://(www\.)?(youtube\.com|youtu\.be)' | head -n 4 | while read -r item; do echo "$item" | cliphist decode 2>/dev/null; done)
    fi

    ITEMS="${ITEMS}󰍉 Search YouTube Video...\n󰅖 Cancel"

    MENU_INPUT=$(printf "$ITEMS" | rofi -dmenu -i -p "󰕼 YouTube PiP" -mesg "Select link (Enter) or type search keywords" -config ~/.config/rofi/config.rasi)

    # Parse selection
    if [[ "$MENU_INPUT" == "󰅖 Cancel" ]] || [ -z "$MENU_INPUT" ]; then
        exit 0
    elif [[ "$MENU_INPUT" == "󰕼 Play Copied Link: "* ]]; then
        URL="${MENU_INPUT#󰕼 Play Copied Link: }"
    elif [[ "$MENU_INPUT" == "󰕼 History: "* ]]; then
        URL="${MENU_INPUT#󰕼 History: }"
    elif [[ "$MENU_INPUT" == *"Search YouTube Video..."* ]]; then
        SEARCH=$(rofi -dmenu -p "󰍉 Enter Search Term" -config ~/.config/rofi/config.rasi)
        [ -n "$SEARCH" ] && URL="ytdl://ytsearch:${SEARCH}"
    elif [[ "$MENU_INPUT" =~ (https?://[^\ ]+) ]]; then
        URL="${BASH_REMATCH[1]}"
    else
        URL="ytdl://ytsearch:${MENU_INPUT}"
    fi
fi

# Clean whitespace
URL=$(echo "$URL" | xargs)

if [ -n "$URL" ]; then
    killall mpv 2>/dev/null
    rm -f /tmp/mpvsocket /tmp/mpv_media_info.json

    (notify-send -a "PiP Video Player" "Launching Floating Player" "$URL" 2>/dev/null &)

    setsid -f mpv \
        --wayland-app-id=mpv-pip \
        --title="mpv-pip" \
        --input-ipc-server=/tmp/mpvsocket \
        --geometry=720x405-30-50 \
        --autofit=720x405 \
        --ontop \
        --ytdl-raw-options="yes-playlist=,cookies-from-browser=brave" \
        --ytdl-format="bestvideo[height<=1080]+bestaudio/best[height<=1080]/best" \
        --script-opts=osc-visibility=auto \
        "$URL" >/dev/null 2>&1
fi
