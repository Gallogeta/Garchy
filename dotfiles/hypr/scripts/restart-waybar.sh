#!/usr/bin/env bash
killall -9 waybar 2>/dev/null || true
sleep 0.2
nohup waybar >/dev/null 2>&1 &
disown
