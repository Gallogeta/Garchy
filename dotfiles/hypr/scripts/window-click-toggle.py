#!/usr/bin/env python3
"""
Garchy OS — Precision Window Click Toggle Dispatcher
Handles 1-click minimize/restore toggle, focus, and close operations for any window address.
Preserves exact monitor and workspace origin.
"""

import sys
import json
import subprocess
import os

STATE_FILE = os.path.expanduser("~/.cache/garchy_minimized_history.json")

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

def ensure_special_hidden():
    try:
        monitors = json.loads(subprocess.check_output(['hyprctl', 'monitors', '-j'], stderr=subprocess.DEVNULL))
        for m in monitors:
            sw = m.get('specialWorkspace', {})
            sw_id = sw.get('id', 0)
            sw_name = sw.get('name', '')
            if sw_id != 0 and sw_name:
                clean_name = sw_name.replace('special:', '')
                eval_lua(f'hl.dispatch(hl.dsp.workspace.toggle_special("{clean_name}"))')
    except Exception:
        pass

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
                    if saved_ws and not str(saved_ws).startswith("special"):
                        return saved_ws
    except Exception:
        pass
    return fallback_ws_id

def toggle_window(target_addr, btn=1):
    ensure_special_hidden()

    try:
        clients = json.loads(subprocess.check_output(['hyprctl', 'clients', '-j'], stderr=subprocess.DEVNULL))
        active_win = json.loads(subprocess.check_output(['hyprctl', 'activewindow', '-j'], stderr=subprocess.DEVNULL))
        monitors = json.loads(subprocess.check_output(['hyprctl', 'monitors', '-j'], stderr=subprocess.DEVNULL))
    except Exception:
        return

    active_addr = active_win.get('address', '')
    active_ws_id = 1
    for m in monitors:
        if m.get('focused'):
            active_ws_id = m['activeWorkspace']['id']
            break

    # Find the target window object
    target_win = None
    for c in clients:
        if c.get('address') == target_addr:
            target_win = c
            break

    if not target_win:
        # If no addr given, pick active window
        if not target_addr and active_win:
            target_win = active_win
            target_addr = active_win.get('address', '')
        else:
            return

    c_class = target_win.get('class', 'App')
    c_title = target_win.get('title', 'Window')
    ws_name = target_win.get('workspace', {}).get('name', '1')
    ws_id = target_win.get('workspace', {}).get('id', 1)
    is_minimized = ws_name.startswith('special')
    is_focused = (target_addr == active_addr)

    # Middle Click -> Close
    if btn == 2:
        lua = f'''
        local wins = hl.get_windows()
        for _, w in ipairs(wins) do
            if w.address == "{target_addr}" then
                hl.dispatch(hl.dsp.focus({{ window = w }}))
                hl.dispatch(hl.dsp.window.close())
                break
            end
        end
        '''
        eval_lua(lua)
        notify("Window Closed", f"Closed {c_class} — {c_title[:25]}")
        return

    # Right Click -> Maximize
    if btn == 3:
        lua = f'''
        local wins = hl.get_windows()
        for _, w in ipairs(wins) do
            if w.address == "{target_addr}" then
                hl.dispatch(hl.dsp.focus({{ window = w }}))
                hl.dispatch(hl.dsp.window.fullscreen({{ mode = 1 }}))
                break
            end
        end
        '''
        eval_lua(lua)
        return

    # Left Click -> Toggle Minimize / Restore / Focus
    if is_minimized:
        # Restore window to original workspace & monitor
        orig_ws = get_orig_workspace(target_addr, active_ws_id)
        lua = f'''
        local wins = hl.get_windows()
        for _, w in ipairs(wins) do
            if w.address == "{target_addr}" then
                hl.dispatch(hl.dsp.window.move({{ window = w, workspace = {orig_ws} }}))
                hl.dispatch(hl.dsp.focus({{ window = w }}))
                break
            end
        end
        '''
        eval_lua(lua)
        ensure_special_hidden()
        notify("Window Restored", f"{c_class} — {c_title[:30]}")

    elif is_focused:
        # Window is already active -> MINIMIZE IT
        save_minimized_history({
            "address": target_addr,
            "title": c_title,
            "class": c_class,
            "workspace_id": ws_id,
            "monitor": target_win.get('monitor')
        })
        lua = f'''
        local wins = hl.get_windows()
        for _, w in ipairs(wins) do
            if w.address == "{target_addr}" then
                hl.dispatch(hl.dsp.window.move({{ window = w, workspace = "special:minimized", silent = true }}))
                break
            end
        end
        '''
        eval_lua(lua)
        ensure_special_hidden()
        notify("Window Minimized", f"{c_class} — {c_title[:30]}")

    else:
        # Window is open but not focused -> Focus and raise it
        lua = f'''
        local wins = hl.get_windows()
        for _, w in ipairs(wins) do
            if w.address == "{target_addr}" then
                hl.dispatch(hl.dsp.focus({{ window = w }}))
                break
            end
        end
        '''
        eval_lua(lua)

def main():
    target_addr = sys.argv[1] if len(sys.argv) > 1 else ""
    btn_str = sys.argv[2] if len(sys.argv) > 2 else "1"
    btn = int(btn_str) if btn_str.isdigit() else 1

    toggle_window(target_addr, btn)

if __name__ == "__main__":
    main()
