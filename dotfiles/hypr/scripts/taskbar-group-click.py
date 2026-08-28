#!/usr/bin/env python3
"""
Garchy OS — Grouped Taskbar Click & Dropdown Handler
Provides instant single-window minimize/restore toggle, and multi-window dropdown selector.
Preserves exact monitor and workspace origin on restore.
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

def get_hypr_state():
    try:
        cursor = json.loads(subprocess.check_output(['hyprctl', 'cursorpos', '-j'], stderr=subprocess.DEVNULL))
        monitors = json.loads(subprocess.check_output(['hyprctl', 'monitors', '-j'], stderr=subprocess.DEVNULL))
        clients = json.loads(subprocess.check_output(['hyprctl', 'clients', '-j'], stderr=subprocess.DEVNULL))
        active_win = json.loads(subprocess.check_output(['hyprctl', 'activewindow', '-j'], stderr=subprocess.DEVNULL))
    except Exception:
        return {}, [], [], {}
    return cursor, monitors, clients, active_win

def restore_monitors_workspaces(monitors):
    if not monitors:
        return
    ws_list = [m['activeWorkspace']['id'] for m in monitors if m.get('activeWorkspace', {}).get('id') != MINIMIZED_WS]
    if ws_list:
        batch_cmds = ' ; '.join([f'dispatch hl.dsp.focus({{ workspace = {ws} }})' for ws in ws_list])
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
            json.dump(history[:50], f, indent=2)
    except Exception:
        pass

def get_orig_workspace(addr, fallback_ws_id=1):
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as f:
                history = json.load(f)
            for h in history:
                if h.get("address") == addr:
                    saved_ws = h.get("workspace_id")
                    if saved_ws and saved_ws != MINIMIZED_WS:
                        return saved_ws
    except Exception:
        pass
    return fallback_ws_id

def get_active_workspace(monitors, cursor):
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
    return target_mon['activeWorkspace']['id'] if target_mon else 1

def open_dropdown_menu(clients, active_addr, active_ws_id, monitors):
    entries = []
    rofi_lines = []

    valid_clients = [c for c in clients if not c.get('workspace', {}).get('name', '').startswith('special')]

    # 1. Quick Global Actions if multiple windows exist
    if len(valid_clients) > 1:
        entries.append({'action': 'restore_all', 'address': '', 'title': 'All Windows'})
        rofi_lines.append(f"⚡ Restore All ({len(valid_clients)} Windows)\0icon\x1fview-restore")

        entries.append({'action': 'minimize_all', 'address': '', 'title': 'All Windows'})
        rofi_lines.append(f"🗕 Minimize All ({len(valid_clients)} Windows)\0icon\x1fwindow-minimize")

    # 2. Window Items (Grouped)
    for c in valid_clients:
        addr = c.get('address', '')
        if not addr:
            continue
        cls = c.get('class', 'App')
        title = c.get('title', 'Untitled')
        ws_id = c.get('workspace', {}).get('id', 1)
        ws_name = c.get('workspace', {}).get('name', '1')

        is_focused = (addr == active_addr)
        is_min = (ws_id == MINIMIZED_WS)

        if is_focused:
            badge = "[Active ✓]"
        elif is_min:
            orig_ws = get_orig_workspace(addr, ws_id)
            badge = f"[🗕 WS {orig_ws}]"
        else:
            badge = f"[WS {ws_name}]"

        icon = cls.lower()
        if "brave" in icon: icon = "brave-browser"
        elif "thunar" in icon: icon = "system-file-manager"
        elif "kitty" in icon: icon = "kitty"
        elif "code" in icon: icon = "code"

        display_text = f"󰖯 {cls} — {title[:42]} {badge}"
        entries.append({
            'action': 'select_window',
            'address': addr,
            'title': f"{cls} — {title[:28]}",
            'is_focused': is_focused,
            'is_minimized': is_min,
            'workspace_id': ws_id,
            'monitor': c.get('monitor')
        })
        rofi_lines.append(f"{display_text}\0icon\x1f{icon}")

    rofi_input = "\n".join(rofi_lines)
    rofi_theme = os.path.expanduser("~/.config/rofi/taskbar-dropdown.rasi")

    rofi_cmd = [
        "rofi",
        "-dmenu",
        "-i",
        "-format", "i",
        "-p", f"🗔 Open Applications ({len(valid_clients)})",
        "-theme", rofi_theme
    ]

    proc = subprocess.Popen(rofi_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, _ = proc.communicate(input=rofi_input)

    selected_str = stdout.strip()
    if not selected_str.isdigit():
        sys.exit(0)

    idx = int(selected_str)
    if idx < 0 or idx >= len(entries):
        sys.exit(0)

    chosen = entries[idx]
    action = chosen['action']
    target_addr = chosen['address']
    target_title = chosen['title']

    if action == "restore_all":
        for c in valid_clients:
            addr = c.get('address')
            if addr and c.get('workspace', {}).get('id') == MINIMIZED_WS:
                target_ws = get_orig_workspace(addr, active_ws_id)
                eval_lua(f'''
                local wins = hl.get_windows()
                for _, w in ipairs(wins) do
                    if w.address == "{addr}" then
                        hl.dispatch(hl.dsp.window.move({{ window = w, workspace = {target_ws} }}))
                        break
                    end
                end
                ''')
        notify("Restored All", "Restored all windows to their original monitors and workspaces.")

    elif action == "minimize_all":
        for c in valid_clients:
            addr = c.get('address')
            if addr and c.get('workspace', {}).get('id') != MINIMIZED_WS:
                cur_ws = c.get('workspace', {}).get('id', active_ws_id)
                save_minimized_history({
                    "address": addr,
                    "class": c.get('class', 'App'),
                    "title": c.get('title', 'Window'),
                    "workspace_id": cur_ws,
                    "monitor": c.get('monitor')
                })
                eval_lua(f'''
                local wins = hl.get_windows()
                for _, w in ipairs(wins) do
                    if w.address == "{addr}" then
                        hl.dispatch(hl.dsp.window.move({{ window = w, workspace = {MINIMIZED_WS}, silent = true }}))
                        break
                    end
                end
                ''')
        restore_monitors_workspaces(monitors)
        notify("Minimized All", f"Minimized {len(valid_clients)} windows")

    elif action == "select_window":
        if chosen.get('is_focused'):
            cur_ws = chosen.get('workspace_id', active_ws_id)
            save_minimized_history({
                "address": target_addr,
                "class": chosen.get('title', 'App').split(' — ')[0],
                "title": target_title,
                "workspace_id": cur_ws,
                "monitor": chosen.get('monitor')
            })
            eval_lua(f'''
            local wins = hl.get_windows()
            for _, w in ipairs(wins) do
                if w.address == "{target_addr}" then
                    hl.dispatch(hl.dsp.window.move({{ window = w, workspace = {MINIMIZED_WS}, silent = true }}))
                    break
                end
            end
            ''')
            restore_monitors_workspaces(monitors)
            notify("Window Minimized", target_title)
        else:
            target_ws = get_orig_workspace(target_addr, active_ws_id)
            eval_lua(f'''
            local wins = hl.get_windows()
            for _, w in ipairs(wins) do
                if w.address == "{target_addr}" then
                    hl.dispatch(hl.dsp.window.move({{ window = w, workspace = {target_ws} }}))
                    hl.dispatch(hl.dsp.focus({{ window = w }}))
                    break
                end
            end
            ''')
            notify("Window Focused", target_title)

def main():
    cursor, monitors, clients, active_win = get_hypr_state()
    valid_clients = [c for c in clients if not c.get('workspace', {}).get('name', '').startswith('special')]
    if not valid_clients:
        notify("No Applications", "No application windows are currently open.")
        sys.exit(0)

    active_addr = active_win.get('address', '')
    active_ws_id = get_active_workspace(monitors, cursor)

    # If only 1 single window exists across the OS, toggle minimize/restore directly
    if len(valid_clients) == 1:
        only_win = valid_clients[0]
        addr = only_win.get('address', '')
        title = only_win.get('title', 'Window')
        c_class = only_win.get('class', 'App')
        cur_ws = only_win.get('workspace', {}).get('id', active_ws_id)
        is_min = (cur_ws == MINIMIZED_WS)
        is_focused = (addr == active_addr)

        if is_focused and not is_min:
            save_minimized_history({
                "address": addr,
                "class": c_class,
                "title": title,
                "workspace_id": cur_ws,
                "monitor": only_win.get('monitor')
            })
            eval_lua(f'''
            local wins = hl.get_windows()
            for _, w in ipairs(wins) do
                if w.address == "{addr}" then
                    hl.dispatch(hl.dsp.window.move({{ window = w, workspace = {MINIMIZED_WS}, silent = true }}))
                    break
                end
            end
            ''')
            restore_monitors_workspaces(monitors)
            notify("Window Minimized", title[:30])
        else:
            target_ws = get_orig_workspace(addr, active_ws_id)
            eval_lua(f'''
            local wins = hl.get_windows()
            for _, w in ipairs(wins) do
                if w.address == "{addr}" then
                    hl.dispatch(hl.dsp.window.move({{ window = w, workspace = {target_ws} }}))
                    hl.dispatch(hl.dsp.focus({{ window = w }}))
                    break
                end
            end
            ''')
            notify("Window Restored", title[:30])
        sys.exit(0)

    # Otherwise open dropdown menu
    open_dropdown_menu(clients, active_addr, active_ws_id, monitors)

if __name__ == "__main__":
    main()
