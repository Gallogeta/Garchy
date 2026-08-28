#!/usr/bin/env python3
"""
Garchy OS — Grouped Taskbar Click & Dropdown Handler
Provides instant single-window minimize/restore toggle, and multi-window dropdown selector.
Uses hidden background workspace 99 for 100% invisible minimization.
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

def open_dropdown_menu(clients, active_addr, active_ws_id):
    entries = []
    rofi_lines = []

    # Filter out special workspaces, only keep user apps + minimized (WS 99)
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
            badge = "[🗕 Minimized]"
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
            'is_minimized': is_min
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
            if addr:
                eval_lua(f'''
                local wins = hl.get_windows()
                for _, w in ipairs(wins) do
                    if w.address == "{addr}" then
                        hl.dispatch(hl.dsp.window.move({{ window = w, workspace = {active_ws_id} }}))
                        hl.dispatch(hl.dsp.focus({{ window = w }}))
                        break
                    end
                end
                ''')
        notify("Restored All", f"Restored {len(valid_clients)} windows to Workspace {active_ws_id}")

    elif action == "minimize_all":
        for c in valid_clients:
            addr = c.get('address')
            if addr:
                eval_lua(f'''
                local wins = hl.get_windows()
                for _, w in ipairs(wins) do
                    if w.address == "{addr}" then
                        hl.dispatch(hl.dsp.window.move({{ window = w, workspace = {MINIMIZED_WS}, silent = true }}))
                        break
                    end
                end
                ''')
        eval_lua(f'hl.dispatch(hl.dsp.focus({{ workspace = {active_ws_id} }}))')
        notify("Minimized All", f"Minimized {len(valid_clients)} windows")

    elif action == "select_window":
        if chosen.get('is_focused'):
            eval_lua(f'''
            local wins = hl.get_windows()
            for _, w in ipairs(wins) do
                if w.address == "{target_addr}" then
                    hl.dispatch(hl.dsp.window.move({{ window = w, workspace = {MINIMIZED_WS}, silent = true }}))
                    hl.dispatch(hl.dsp.focus({{ workspace = {active_ws_id} }}))
                    break
                end
            end
            ''')
            notify("Window Minimized", target_title)
        else:
            eval_lua(f'''
            local wins = hl.get_windows()
            for _, w in ipairs(wins) do
                if w.address == "{target_addr}" then
                    hl.dispatch(hl.dsp.window.move({{ window = w, workspace = {active_ws_id} }}))
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
        is_min = (only_win.get('workspace', {}).get('id') == MINIMIZED_WS)
        is_focused = (addr == active_addr)

        if is_focused and not is_min:
            eval_lua(f'''
            local wins = hl.get_windows()
            for _, w in ipairs(wins) do
                if w.address == "{addr}" then
                    hl.dispatch(hl.dsp.window.move({{ window = w, workspace = {MINIMIZED_WS}, silent = true }}))
                    hl.dispatch(hl.dsp.focus({{ workspace = {active_ws_id} }}))
                    break
                end
            end
            ''')
            notify("Window Minimized", title[:30])
        else:
            eval_lua(f'''
            local wins = hl.get_windows()
            for _, w in ipairs(wins) do
                if w.address == "{addr}" then
                    hl.dispatch(hl.dsp.window.move({{ window = w, workspace = {active_ws_id} }}))
                    hl.dispatch(hl.dsp.focus({{ window = w }}))
                    break
                end
            end
            ''')
            notify("Window Restored", title[:30])
        sys.exit(0)

    # Otherwise open dropdown menu
    open_dropdown_menu(clients, active_addr, active_ws_id)

if __name__ == "__main__":
    main()
