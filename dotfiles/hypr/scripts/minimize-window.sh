#!/usr/bin/env python3
"""
Garchy OS — Window Minimization & Restoration Engine (Hyprland Lua)
Provides silent, reliable window minimization to background workspace 99.
"""

import os
import sys
import json
import subprocess

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

def get_active_context():
    try:
        cursor = json.loads(subprocess.check_output(['hyprctl', 'cursorpos', '-j'], stderr=subprocess.DEVNULL))
        monitors = json.loads(subprocess.check_output(['hyprctl', 'monitors', '-j'], stderr=subprocess.DEVNULL))
        clients = json.loads(subprocess.check_output(['hyprctl', 'clients', '-j'], stderr=subprocess.DEVNULL))
        active_win = json.loads(subprocess.check_output(['hyprctl', 'activewindow', '-j'], stderr=subprocess.DEVNULL))
    except Exception:
        return 1, None, [], []

    if not monitors:
        return 1, None, [], clients

    cx = cursor.get('x', 0)
    cy = cursor.get('y', 0)

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

    # All regular visible windows on this workspace
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

    return target_ws_id, target_win, ws_clients, clients

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
    ws_id, target_win, ws_clients, all_clients = get_active_context()
    if target_win and target_win.get('address'):
        addr = target_win['address']
        title = target_win.get('title', 'Window')
        c_class = target_win.get('class', 'App')

        lua = f'''
        local wins = hl.get_windows()
        for _, w in ipairs(wins) do
            if w.address == "{addr}" then
                hl.dispatch(hl.dsp.window.move({{ window = w, workspace = {MINIMIZED_WS}, silent = true }}))
                hl.dispatch(hl.dsp.focus({{ workspace = {ws_id} }}))
                break
            end
        end
        '''
        eval_lua(lua)
        save_minimized_history({
            "address": addr,
            "title": title,
            "class": c_class,
            "workspace_id": ws_id
        })
        notify("Window Minimized", f"{c_class} — {title[:30]}")
    else:
        notify("No Windows", f"Workspace {ws_id} has no active windows to minimize.")

def do_minimize_all():
    ws_id, _, ws_clients, _ = get_active_context()
    if ws_clients:
        count = len(ws_clients)
        for win in ws_clients:
            addr = win.get('address')
            if addr:
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
                save_minimized_history({
                    "address": addr,
                    "title": win.get("title", "Window"),
                    "class": win.get("class", "App"),
                    "workspace_id": ws_id
                })
        eval_lua(f'hl.dispatch(hl.dsp.focus({{ workspace = {ws_id} }}))')
        notify("Desktop Minimized", f"Minimized {count} window(s) on Workspace {ws_id}")
    else:
        notify("No Windows", f"Workspace {ws_id} has no windows to minimize.")

def do_restore_last():
    ws_id, _, _, all_clients = get_active_context()
    minimized_clients = [
        c for c in all_clients
        if c.get('workspace', {}).get('id') == MINIMIZED_WS
    ]

    if not minimized_clients:
        notify("No Minimized Windows", "All windows are currently visible.")
        return

    target_addr = None
    target_title = None
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                history = json.load(f)
            for h in history:
                if any(c.get('address') == h.get('address') for c in minimized_clients):
                    target_addr = h.get('address')
                    target_title = h.get('title')
                    break
        except Exception:
            pass

    if not target_addr and minimized_clients:
        target_addr = minimized_clients[0]['address']
        target_title = minimized_clients[0].get('title', 'Window')

    lua = f'''
    local wins = hl.get_windows()
    for _, w in ipairs(wins) do
        if w.address == "{target_addr}" then
            hl.dispatch(hl.dsp.window.move({{ window = w, workspace = {ws_id} }}))
            hl.dispatch(hl.dsp.focus({{ window = w }}))
            break
        end
    end
    '''
    eval_lua(lua)
    notify("Window Restored", f"Restored '{target_title[:30]}' to Workspace {ws_id}")

def do_restore_all():
    ws_id, _, _, all_clients = get_active_context()
    minimized_clients = [
        c for c in all_clients
        if c.get('workspace', {}).get('id') == MINIMIZED_WS
    ]
    if minimized_clients:
        for win in minimized_clients:
            addr = win.get('address')
            if addr:
                lua = f'''
                local wins = hl.get_windows()
                for _, w in ipairs(wins) do
                    if w.address == "{addr}" then
                        hl.dispatch(hl.dsp.window.move({{ window = w, workspace = {ws_id} }}))
                        hl.dispatch(hl.dsp.focus({{ window = w }}))
                        break
                    end
                end
                '''
                eval_lua(lua)
        notify("Restored All", f"Restored {len(minimized_clients)} window(s) to Workspace {ws_id}")
    else:
        notify("No Minimized Windows", "All windows are currently visible.")

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "minimize"

    if action == "minimize":
        do_minimize()
    elif action in ("minimize-all", "minimize_all"):
        do_minimize_all()
    elif action in ("restore-last", "restore_last"):
        do_restore_last()
    elif action in ("restore-all", "restore_all"):
        do_restore_all()
    elif action in ("menu", "selective", "manager"):
        subprocess.Popen(['python3', '/home/gallo/.config/hypr/scripts/taskbar-group-click.py'])
    else:
        do_minimize()

if __name__ == "__main__":
    main()
