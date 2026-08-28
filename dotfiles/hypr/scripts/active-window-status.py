#!/usr/bin/env python3
"""
Garchy OS — Active Window Status Indicator for Waybar
Displays the active application on the focused monitor with dual-monitor awareness.
"""

import sys
import json
import subprocess

def get_active_window_info():
    try:
        cursor = json.loads(subprocess.check_output(['hyprctl', 'cursorpos', '-j'], stderr=subprocess.DEVNULL))
        monitors = json.loads(subprocess.check_output(['hyprctl', 'monitors', '-j'], stderr=subprocess.DEVNULL))
        clients = json.loads(subprocess.check_output(['hyprctl', 'clients', '-j'], stderr=subprocess.DEVNULL))
        active_win = json.loads(subprocess.check_output(['hyprctl', 'activewindow', '-j'], stderr=subprocess.DEVNULL))
    except Exception:
        return {"text": "", "tooltip": "", "class": "empty"}

    cx = cursor.get('x', 0)
    cy = cursor.get('y', 0)

    # 1. Determine target monitor by cursor position
    target_mon = None
    for m in monitors:
        mx, my, mw, mh = m.get('x', 0), m.get('y', 0), m.get('width', 1920), m.get('height', 1080)
        if mx <= cx < mx + mw and my <= cy < my + mh:
            target_mon = m
            break

    if not target_mon:
        for m in monitors:
            if m.get('focused'):
                target_mon = m
                break

    if not target_mon and monitors:
        target_mon = monitors[0]

    target_ws_id = target_mon['activeWorkspace']['id'] if target_mon else 1

    # 2. Get visible regular windows on this monitor's active workspace
    ws_clients = [
        c for c in clients
        if c.get('workspace', {}).get('id') == target_ws_id
        and not c.get('workspace', {}).get('name', '').startswith('special')
    ]

    target_win = None
    if active_win and active_win.get('address') and active_win.get('address') != "0x0":
        for c in ws_clients:
            if c.get('address') == active_win.get('address'):
                target_win = c
                break

    if not target_win and ws_clients:
        ws_clients.sort(key=lambda c: c.get('focusHistoryID', 999))
        target_win = ws_clients[0]

    # Fallback to any active window across all workspaces if empty
    if not target_win and clients:
        normal_clients = [c for c in clients if not c.get('workspace', {}).get('name', '').startswith('special')]
        if normal_clients:
            normal_clients.sort(key=lambda c: c.get('focusHistoryID', 999))
            target_win = normal_clients[0]

    if not target_win:
        return {"text": "", "tooltip": "", "class": "empty"}

    title = target_win.get('title', '').strip()
    cls = target_win.get('class', '').strip()

    icon = "🗖"
    cls_lower = cls.lower()
    if "thunar" in cls_lower or "file" in cls_lower:
        icon = "📁"
    elif "brave" in cls_lower or "firefox" in cls_lower or "browser" in cls_lower:
        icon = "🌐"
    elif "kitty" in cls_lower or "terminal" in cls_lower:
        icon = ""
    elif "steam" in cls_lower or "game" in cls_lower:
        icon = "🎮"
    elif "code" in cls_lower:
        icon = "💻"
    elif "discord" in cls_lower:
        icon = "💬"
    elif "spotify" in cls_lower:
        icon = "🎵"

    short_title = title if len(title) <= 24 else title[:22] + "..."
    display_text = f"{icon} {cls}: {short_title}" if cls else f"{icon} {short_title}"
    tooltip = f"🗔 Active Window: {cls}\nTitle: {title}\n───────────────────────\n• Left Click: MINIMIZE window\n• Middle Click: Maximize / Restore\n• Right Click: CLOSE window"

    return {
        "text": display_text,
        "tooltip": tooltip,
        "class": "active-app"
    }

if __name__ == "__main__":
    data = get_active_window_info()
    print(json.dumps(data), flush=True)
