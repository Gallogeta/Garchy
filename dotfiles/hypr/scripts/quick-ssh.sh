#!/usr/bin/env bash

TARGET="$1"

case "$TARGET" in
    "itsusi")
        kitty --title "SSH: itsusi (192.168.1.100)" zsh -c "echo 'Connecting to itsusi (gallo@192.168.1.100)...'; ssh gallo@192.168.1.100; exec zsh"
        ;;
    "prox")
        kitty --title "SSH: prox (192.168.1.106)" zsh -c "echo 'Connecting to prox (root@192.168.1.106)...'; ssh root@192.168.1.106; exec zsh"
        ;;
    "flix")
        kitty --title "SSH: flix (192.168.1.105)" zsh -c "echo 'Connecting to flix (tv@192.168.1.105)...'; ssh tv@192.168.1.105; exec zsh"
        ;;
    *)
        kitty --title "SSH: $TARGET" zsh -c "ssh $TARGET; exec zsh"
        ;;
esac
