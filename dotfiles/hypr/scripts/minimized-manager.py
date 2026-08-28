#!/usr/bin/env python3
"""
Garchy OS — Selective Minimized Window Manager
Allows selecting, restoring, or closing any specific minimized window from 1 to 10+ windows.
"""

import sys
import json
import subprocess
import os

ICON_MAP = {
    "brave-browser": "brave-browser",
    "Brave-browser": "brave-browser",
    "code-oss": "code",
    "code": "code",
    "Code": "code",
    "kitty": "kitty",
    "firefox": "firefox",
    "steam": "steam",
    "heroic": "heroic",
    "thunar": "system-file-manager",
    "Thunar": "system-file-manager",
    "pavucontrol": "multimedia-volume-control",
    "org.pulseaudio.pavucontrol": "multimedia-volume-control",
    "discord": "discord",
    "Spotify": "spotify",
    "obsidian": "obsidian"
}

def notify(title, msg):
    try:
        subprocess.Popen(['notify-send', '-a', 'Window Manager', '-t', '1400', title, msg])
    except Exception:
        pass

def eval_lua(code):
    try:
        subprocess.run(['hyprctl', 'eval', code], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def get_minimized_windows():
    try:
        clients = json.loads(subprocess.check_output(['hyprctl', 'clients', '-j'], stderr=subprocess.DEVNULL))
        minimized = [
            c for c in clients
            if c.get('workspace', {}).get('name', '') == 'special:minimized'
        ]
        return minimized
    except Exception:
        return []

def get_active_workspace():
    try:
        ws_out = subprocess.check_output(['hyprctl', 'activeworkspace', '-j'], stderr=subprocess.DEVNULL)
        return json.loads(ws_out).get('id', 1)
    except Exception:
        return 1

def main():
    minimized = get_minimized_windows()
    if not minimized:
        notify("No Minimized Windows", "All application windows are currently visible.")
        sys.exit(0)

    active_ws_id = get_active_workspace()

    entries = []
    rofi_lines = []

    # 1. Option: Restore All
    if len(minimized) > 1:
        entries.append({
            'action': 'restore_all',
            'address': '',
            'title': f'All {len(minimized)} Windows'
        })
        rofi_lines.append(f"⚡ Restore All ({len(minimized)} Windows)\0icon\x1fview-restore")

    # 2. Individual Window Restore Options
    for win in minimized:
        addr = win.get('address', '')
        if not addr:
            continue
        c_class = win.get('class', 'App')
        title = win.get('title', 'Untitled')
        icon = ICON_MAP.get(c_class, c_class.lower())

        display_text = f"󰖯 {c_class} — {title[:48]}"
        entries.append({
            'action': 'restore_single',
            'address': addr,
            'title': f"{c_class} — {title[:30]}"
        })
        rofi_lines.append(f"{display_text}\0icon\x1f{icon}")

    # 3. Individual Window Close Options
    for win in minimized:
        addr = win.get('address', '')
        if not addr:
            continue
        c_class = win.get('class', 'App')
        title = win.get('title', 'Untitled')

        display_text = f"✕ Close: {c_class} — {title[:48]}"
        entries.append({
            'action': 'close_single',
            'address': addr,
            'title': f"{c_class} — {title[:30]}"
        })
        rofi_lines.append(f"{display_text}\0icon\x1fprocess-stop")

    rofi_input = "\n".join(rofi_lines)

    rofi_theme = os.path.expanduser("~/.config/rofi/window.rasi")
    if not os.path.exists(rofi_theme):
        rofi_theme = os.path.expanduser("~/.config/rofi/config.rasi")

    rofi_cmd = [
        "rofi",
        "-dmenu",
        "-i",
        "-format", "i",
        "-p", f"🗕 Minimized Windows ({len(minimized)})",
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
        for win in minimized:
            addr = win.get('address')
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
        notify("Restored All", f"Restored {len(minimized)} windows to Workspace {active_ws_id}")

    elif action == "restore_single":
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
        notify("Window Restored", f"Restored '{target_title}' to Workspace {active_ws_id}")

    elif action == "close_single":
        eval_lua(f'''
        local wins = hl.get_windows()
        for _, w in ipairs(wins) do
            if w.address == "{target_addr}" then
                hl.dispatch(hl.dsp.focus({{ window = w }}))
                hl.dispatch(hl.dsp.window.close())
                break
            end
        end
        ''')
        notify("Window Closed", f"Closed '{target_title}' without opening.")

if __name__ == "__main__":
    main()
