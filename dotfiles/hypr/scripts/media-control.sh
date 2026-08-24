#!/usr/bin/env bash

ACTION="$1"

# Helper function to send command to MPV IPC socket
send_mpv() {
    local cmd="$1"
    if [ -S /tmp/mpvsocket ]; then
        echo "$cmd" | socat - /tmp/mpvsocket >/dev/null 2>&1
        return 0
    fi
    return 1
}

case "$ACTION" in
    "play-pause")
        # 1. Try MPV socket
        if send_mpv '{ "command": ["cycle", "pause"] }'; then
            exit 0
        fi

        # 2. Try MPRIS players
        playerctl -p plasma-browser-integration,spotify,brave,firefox,vlc,%any play-pause 2>/dev/null || playerctl play-pause 2>/dev/null
        ;;

    "stop"|"close")
        # 1. Stop and close MPV if open
        send_mpv '{ "command": ["quit"] }'
        killall mpv 2>/dev/null
        rm -f /tmp/mpvsocket /tmp/mpv_media_info.json

        # 2. Stop MPRIS players
        playerctl -a stop 2>/dev/null
        playerctl -a pause 2>/dev/null

        # 3. Send Pause (k) to YouTube / Browser windows
        hyprctl dispatch sendshortcut ",k,class:^(brave-browser)$" 2>/dev/null
        hyprctl dispatch sendshortcut ",k,class:^(firefox)$" 2>/dev/null
        ;;

    "next")
        # 1. MPV next
        if send_mpv '{ "command": ["playlist-next"] }'; then
            exit 0
        fi

        # 2. Dedicated media players
        if ! playerctl -p spotify,vlc next 2>/dev/null; then
            playerctl -p plasma-browser-integration,brave,firefox next 2>/dev/null
            # YouTube universal Next shortcut (Shift+N)
            hyprctl dispatch sendshortcut "SHIFT,N,class:^(brave-browser)$" 2>/dev/null
            hyprctl dispatch sendshortcut "SHIFT,N,class:^(firefox)$" 2>/dev/null
        fi
        ;;

    "previous")
        # 1. MPV prev
        if send_mpv '{ "command": ["playlist-prev"] }'; then
            exit 0
        fi

        # 2. Dedicated media players
        if ! playerctl -p spotify,vlc previous 2>/dev/null; then
            playerctl -p plasma-browser-integration,brave,firefox previous 2>/dev/null
            # YouTube universal Previous shortcut (Shift+P)
            hyprctl dispatch sendshortcut "SHIFT,P,class:^(brave-browser)$" 2>/dev/null
            hyprctl dispatch sendshortcut "SHIFT,P,class:^(firefox)$" 2>/dev/null
        fi
        ;;
esac
