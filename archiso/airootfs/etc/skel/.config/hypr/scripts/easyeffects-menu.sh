#!/usr/bin/env bash

# Easy Effects Quick Control Menu for Rofi

PRESETS=$(easyeffects -p 2>/dev/null | grep -E '^[0-9]+' | cut -f2-)

MENU="󰓃 Open Easy Effects GUI\n󰝟 Toggle Global Bypass\n󰝚 Preset: EQ bass"

if [ -n "$PRESETS" ]; then
    for p in $PRESETS; do
        if [ "$p" != "EQ bass" ]; then
            MENU="$MENU\n󰝚 Preset: $p"
        fi
    done
fi

CHOICE=$(echo -e "$MENU" | rofi -dmenu -i -p "󰓃 Audio EQ" -config ~/.config/rofi/config.rasi)

case "$CHOICE" in
    *"Open Easy Effects GUI"*)
        easyeffects &
        ;;
    *"Toggle Global Bypass"*)
        easyeffects --bypass-toggle
        STATE=$(easyeffects -b 3 2>/dev/null | grep -i 'bypass' || echo "Toggled")
        notify-send -a "Easy Effects" "Audio Bypass" "Toggled audio equalizer processing"
        ;;
    *"Preset:"*)
        PRESET_NAME=$(echo "$CHOICE" | sed 's/.*Preset: //')
        easyeffects -l "$PRESET_NAME"
        notify-send -a "Easy Effects" "Audio Preset Loaded" "$PRESET_NAME"
        ;;
esac
