#!/usr/bin/env bash

# Clipboard history selector
case "$1" in
    "wipe")
        cliphist wipe
        notify-send -a "Clipboard" "Clipboard History Cleared"
        ;;
    *)
        cliphist list | rofi -dmenu -i -p "󰅌 Clipboard" -config ~/.config/rofi/config.rasi | cliphist decode | wl-copy
        ;;
esac
