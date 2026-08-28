#!/usr/bin/env python3
"""
Garchy OS — Quickshell High-Performance Taskbar & Window State Service
Streams real-time window states, multi-instance groupings, and handles
Windows 11 / KDE style click-to-minimize and monitor-preserving restoration.
"""

import sys
import os
import json
import time
import socket
import subprocess

STATE_FILE = os.path.expanduser("~/.cache/garchy_minimized_history.json")
MINIMIZED_WS = 99

ICON_MAP = {
    "brave-browser": "brave-browser",
    "Brave-browser": "brave-browser",
    "firefox": "firefox",
    "falkon": "falkon",
    "kitty": "kitty",
    "alacritty": "alacritty",
    "thunar": "system-file-manager",
    "Thunar": "system-file-manager",
    "code": "code",
    "Code": "code",
    "code-oss": "code",
    "steam": "steam",
    "heroic": "heroic",
    "discord": "discord",
    "vesktop": "vesktop",
    "spotify": "spotify",
    "Spotify": "spotify",
    "pavucontrol": "org.pulseaudio.pavucontrol",
    "org.pulseaudio.pavucontrol": "org.pulseaudio.pavucontrol",
    "haruna": "haruna",
    "smplayer": "smplayer",
    "mpv": "mpv"
}

def eval_lua(code):
    try:
        subprocess.run(['hyprctl', 'eval', code], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
                    if saved_ws and not str(saved_ws).startswith("special") and saved_ws != MINIMIZED_WS:
                        return saved_ws
    except Exception:
        pass
    return fallback_ws_id

def get_windows_state():
    try:
        clients = json.loads(subprocess.check_output(['hyprctl', 'clients', '-j'], stderr=subprocess.DEVNULL))
        active_win = json.loads(subprocess.check_output(['hyprctl', 'activewindow', '-j'], stderr=subprocess.DEVNULL))
        monitors = json.loads(subprocess.check_output(['hyprctl', 'monitors', '-j'], stderr=subprocess.DEVNULL))
    except Exception:
        return {"groups": [], "active_addr": "", "monitors": []}

    active_addr = active_win.get('address', '')

    # Filter valid windows
    valid_clients = [c for c in clients if not c.get('class', '') in ('wlogout', 'rofi', 'quickshell')]

    # Group by App Class
    groups_dict = {}
    for c in valid_clients:
        cls = c.get('class', 'App') or 'App'
        if cls not in groups_dict:
            groups_dict[cls] = []
        
        ws_name = c.get('workspace', {}).get('name', '1')
        ws_id = c.get('workspace', {}).get('id', 1)
        addr = c.get('address', '')
        title = c.get('title', 'Window')
        is_min = ws_name.startswith('special') or ws_id == MINIMIZED_WS
        is_active = (addr == active_addr)

        groups_dict[cls].append({
            "address": addr,
            "title": title,
            "class": cls,
            "workspace_id": ws_id,
            "workspace_name": ws_name,
            "monitor": c.get('monitor', 0),
            "is_active": is_active,
            "is_minimized": is_min
        })

    groups_list = []
    for cls, win_list in groups_dict.items():
        is_group_active = any(w['is_active'] for w in win_list)
        is_all_min = all(w['is_minimized'] for w in win_list)
        icon = ICON_MAP.get(cls, ICON_MAP.get(cls.lower(), cls.lower()))

        groups_list.append({
            "class": cls,
            "icon": icon,
            "count": len(win_list),
            "is_active": is_group_active,
            "is_minimized": is_all_min,
            "windows": win_list
        })

    return {
        "groups": groups_list,
        "active_addr": active_addr,
        "monitors": monitors
    }

def handle_action(action, addr):
    ensure_special_hidden()
    if not addr:
        return

    try:
        clients = json.loads(subprocess.check_output(['hyprctl', 'clients', '-j'], stderr=subprocess.DEVNULL))
        active_win = json.loads(subprocess.check_output(['hyprctl', 'activewindow', '-j'], stderr=subprocess.DEVNULL))
    except Exception:
        return

    target_win = None
    for c in clients:
        if c.get('address') == addr:
            target_win = c
            break

    if not target_win:
        return

    ws_name = target_win.get('workspace', {}).get('name', '1')
    ws_id = target_win.get('workspace', {}).get('id', 1)
    is_min = ws_name.startswith('special') or ws_id == MINIMIZED_WS
    is_active = (addr == active_win.get('address', ''))

    if action == "toggle":
        if is_min:
            # Restore to original workspace
            orig_ws = get_orig_workspace(addr, 1)
            eval_lua(f'''
            local wins = hl.get_windows()
            for _, w in ipairs(wins) do
                if w.address == "{addr}" then
                    hl.dispatch(hl.dsp.window.move({{ window = w, workspace = {orig_ws} }}))
                    hl.dispatch(hl.dsp.focus({{ window = w }}))
                    break
                end
            end
            ''')
            ensure_special_hidden()
        elif is_active:
            # Minimize active window
            save_minimized_history({
                "address": addr,
                "title": target_win.get('title', 'Window'),
                "class": target_win.get('class', 'App'),
                "workspace_id": ws_id,
                "monitor": target_win.get('monitor')
            })
            eval_lua(f'''
            local wins = hl.get_windows()
            for _, w in ipairs(wins) do
                if w.address == "{addr}" then
                    hl.dispatch(hl.dsp.window.move({{ window = w, workspace = "special:minimized", silent = true }}))
                    break
                end
            end
            ''')
            ensure_special_hidden()
        else:
            # Inactive -> Focus
            eval_lua(f'''
            local wins = hl.get_windows()
            for _, w in ipairs(wins) do
                if w.address == "{addr}" then
                    hl.dispatch(hl.dsp.focus({{ window = w }}))
                    break
                end
            end
            ''')

    elif action == "close":
        eval_lua(f'''
        local wins = hl.get_windows()
        for _, w in ipairs(wins) do
            if w.address == "{addr}" then
                hl.dispatch(hl.dsp.focus({{ window = w }}))
                hl.dispatch(hl.dsp.window.close())
                break
            end
        end
        ''')

    elif action == "focus":
        if is_min:
            orig_ws = get_orig_workspace(addr, 1)
            eval_lua(f'''
            local wins = hl.get_windows()
            for _, w in ipairs(wins) do
                if w.address == "{addr}" then
                    hl.dispatch(hl.dsp.window.move({{ window = w, workspace = {orig_ws} }}))
                    hl.dispatch(hl.dsp.focus({{ window = w }}))
                    break
                end
            end
            ''')
            ensure_special_hidden()
        else:
            eval_lua(f'''
            local wins = hl.get_windows()
            for _, w in ipairs(wins) do
                if w.address == "{addr}" then
                    hl.dispatch(hl.dsp.focus({{ window = w }}))
                    break
                end
            end
            ''')

def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "dump":
            print(json.dumps(get_windows_state()))
            sys.exit(0)
        elif cmd in ("toggle", "close", "focus", "restore", "minimize"):
            addr = sys.argv[2] if len(sys.argv) > 2 else ""
            handle_action(cmd, addr)
            sys.exit(0)

    # Daemon mode: emit initial state and listen to Hyprland socket2
    print(json.dumps(get_windows_state()), flush=True)

    sig = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE", "")
    sock_path = f"/run/user/1000/hypr/{sig}/.socket2.sock"

    while True:
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.connect(sock_path)
            buf = ""
            while True:
                data = s.recv(4096).decode('utf-8', errors='ignore')
                if not data:
                    break
                buf += data
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    if any(line.startswith(ev) for ev in ("openwindow", "closewindow", "movewindow", "activewindow", "workspace", "focusedmon")):
                        time.sleep(0.04) # debounce slight state settles
                        print(json.dumps(get_windows_state()), flush=True)
        except Exception:
            time.sleep(1)

if __name__ == "__main__":
    main()
