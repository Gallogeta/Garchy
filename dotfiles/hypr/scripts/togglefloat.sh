#!/usr/bin/env bash

# Toggle floating state in Hyprland 0.56.2+ Lua architecture
hyprctl dispatch "hl.dsp.window.float({ action = \"toggle\" })"

sleep 0.05

floating=$(hyprctl activewindow -j 2>/dev/null | jq -r '.floating // false')

if [ "$floating" = "true" ]; then
    hyprctl eval 'local w = hl.get_active_window(); if w and w.floating then local mon = hl.get_active_monitor(); if mon then local tw = math.floor(mon.width * 0.7); local th = math.floor(mon.height * 0.7); hl.dispatch(hl.dsp.window.resize({ x = tw, y = th, relative = false })); local tx = (mon.x or 0) + math.floor((mon.width - tw) / 2); local ty = (mon.y or 0) + math.floor((mon.height - th) / 2); hl.dispatch(hl.dsp.window.move({ x = tx, y = ty, relative = false })) end end' >/dev/null 2>&1
fi
