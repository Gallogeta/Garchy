#!/usr/bin/env bash

WALL_DIR="${WALLPAPERS_DIR:-$HOME/Pictures/Wallpapers}"
CURRENT_FILE="/tmp/hypr_current_wallpaper.txt"

if [ ! -d "$WALL_DIR" ]; then
    notify-send -a "Wallpapers" "Directory $WALL_DIR does not exist"
    exit 1
fi

if ! pgrep -x "awww-daemon" >/dev/null 2>&1; then
    awww-daemon &
    sleep 0.4
fi

# Get list of images
WALLPAPERS=$(find "$WALL_DIR" -maxdepth 1 -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.webp" -o -iname "*.gif" \) -printf "%f\n" | sort)

if [ -z "$WALLPAPERS" ]; then
    notify-send -a "Wallpapers" "No wallpapers found in $WALL_DIR"
    exit 1
fi

MENU="🎲 Random Wallpaper\n$WALLPAPERS"
CHOICE=$(echo -e "$MENU" | rofi -dmenu -i -p "󰸉 Wallpaper" -mesg "Select wallpaper (Enter) or choose 🎲 Random" -config ~/.config/rofi/config.rasi)

if [ "$CHOICE" = "🎲 Random Wallpaper" ]; then
    /home/gallo/.config/hypr/scripts/wallpaper-timer.sh random
    notify-send -a "Wallpaper" "Random Wallpaper Applied"
elif [ -n "$CHOICE" ]; then
    TARGET="$WALL_DIR/$CHOICE"
    if [ -f "$TARGET" ]; then
        awww img "$TARGET" --transition-type outer --transition-step 90 --transition-fps 144
        echo "$TARGET" > "$CURRENT_FILE"
        notify-send -a "Wallpaper" "Wallpaper Updated" "$CHOICE" -i "$TARGET"
    fi
fi
