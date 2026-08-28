#!/usr/bin/env python3
"""
Garchy OS — Taskbar & Window Controls Click Dispatcher
Coordinates 1-click minimize, maximize, and close operations across dual monitors.
Uses hidden background workspace 99 with atomic dual-monitor workspace retention.
"""

import sys
import json
import subprocess
import os

STATE_FILE = os.path.expanduser("~/.cache/garchy_minimized_history.json")
MINIMIZED_WS = 99

def eval_lua(code):
    try:
        subprocess.run(['hyprctl', 'eval', code], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def notify(title, msg):
    try:
        subprocess.Popen(['notify-send', '-a', 'Window Manager', '-t', '1400', title, msg])
    except Exception:
        pass

def get_target_window_and_monitors():
    try:
        cursor = json.loads(subprocess.check_output(['hyprctl', 'cursorpos', '-j'], stderr=subprocess.DEVNULL))
        monitors = json.loads(subprocess.check_output(['hyprctl', 'monitors', '-j'], stderr=subprocess.DEVNULL))
        clients = json.loads(subprocess.check_output(['hyprctl', 'clients', '-j'], stderr=subprocess.DEVNULL))
        active_win = json.loads(subprocess.check_output(['hyprctl', 'activewindow', '-j'], stderr=subprocess.DEVNULL))
    except Exception:
        return None, 1, {}

    cx = cursor.get('x', 0)
    cy = cursor.get('y', 0)

    ws_map = { m['name']: m['activeWorkspace']['id'] for m in monitors }

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
        and c.get('workspace', {}).get('id') != MINIMIZED_WS
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

    # Fallback to any active window across all visible workspaces if empty
    if not target_win and clients:
        normal_clients = [
            c for c in clients
            if c.get('workspace', {}).get('id') != MINIMIZED_WS
            and not c.get('workspace', {}).get('name', '').startswith('special')
        ]
        if normal_clients:
            normal_clients.sort(key=lambda c: c.get('focusHistoryID', 999))
            target_win = normal_clients[0]
            target_ws_id = target_win.get('workspace', {}).get('id', 1)

    return target_win, target_ws_id, ws_map

def restore_monitors_workspaces(ws_map):
    if not ws_map:
        return
    batch_cmds = ' ; '.join([f'dispatch hl.dsp.focus({{ workspace = {ws} }})' for ws in ws_map.values()])
    subprocess.run(['hyprctl', '--batch', batch_cmds], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def save_minimized_history(win_data):
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        history = []
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as f:
                history = json.load(f)
        history = [h for h in history if h.get("address") != win_data.get("address")]
        history.insert(0, win_data)
        with open(STATE_FILE, "w") as f:
            json.dump(history[:30], f, indent=2)
    except Exception:
        pass

def do_minimize():
    win, ws_id, ws_map = get_target_window_and_monitors()
    if not win or not win.get('address'):
        notify("No Windows", "No active window on this workspace to minimize.")
        return

    addr = win['address']
    title = win.get('title', 'Window')
    c_class = win.get('class', 'App')

    lua = f'''
    local wins = hl.get_windows()
    for _, w in ipairs(wins) do
        if w.address == "{addr}" then
            hl.dispatch(hl.dsp.window.move({{ window = w, workspace = {MINIMIZED_WS}, silent = true }}))
            break
        end
    end
    '''
    eval_lua(lua)
    restore_monitors_workspaces(ws_map)

    save_minimized_history({
        "address": addr,
        "title": title,
        "class": c_class,
        "workspace_id": win.get("workspace", {}).get("id", ws_id),
        "monitor": win.get("monitor")
    })
    notify("Window Minimized", f"{c_class} — {title[:30]}")

def do_maximize():
    win, _, _ = get_target_window_and_monitors()
    if not win or not win.get('address'):
        return

    addr = win['address']
    lua = f'''
    local wins = hl.get_windows()
    for _, w in ipairs(wins) do
        if w.address == "{addr}" then
            hl.dispatch(hl.dsp.focus({{ window = w }}))
            hl.dispatch(hl.dsp.window.fullscreen({{ mode = 1 }}))
            break
        end
    end
    '''
    eval_lua(lua)

def do_close():
    win, _, _ = get_target_window_and_monitors()
    if not win or not win.get('address'):
        return

    addr = win['address']
    title = win.get('title', 'Window')
    c_class = win.get('class', 'App')

    lua = f'''
    local wins = hl.get_windows()
    for _, w in ipairs(wins) do
        if w.address == "{addr}" then
            hl.dispatch(hl.dsp.focus({{ window = w }}))
            hl.dispatch(hl.dsp.window.close())
            break
        end
    end
    '''
    eval_lua(lua)
    notify("Window Closed", f"Closed {c_class} — {title[:25]}")

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "minimize-active"

    if action in ("minimize-active", "toggle-active", "minimize"):
        do_minimize()
    elif action in ("maximize-active", "maximize", "toggle-maximize"):
        do_maximize()
    elif action in ("close-active", "close"):
        do_close()
    else:
        do_minimize()

if __name__ == "__main__":
    main()
