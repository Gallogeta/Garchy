#!/usr/bin/env python3
"""
Gally OS - Dedicated Minimized Window Manager
1-Click Restore of ONLY the selected window, and 1-Click Close without restoring.
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
    "codium": "vscodium",
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
        subprocess.Popen(['notify-send', '-a', 'Gally Windows', '-t', '1500', title, msg])
    except Exception:
        pass

def get_minimized_windows():
    try:
        clients = json.loads(subprocess.check_output(['hyprctl', 'clients', '-j'], stderr=subprocess.DEVNULL))
        minimized = [
            c for c in clients
            if c.get('workspace', {}).get('name', '').startswith('special')
        ]
        return minimized
    except Exception:
        return []

def main():
    minimized = get_minimized_windows()
    if not minimized:
        notify("No Minimized Windows", "All windows are currently open on your workspaces.")
        sys.exit(0)

    entries = []
    rofi_lines = []

    for win in minimized:
        addr = win.get('address', '')
        if not addr:
            continue
        c_class = win.get('class', 'App')
        title = win.get('title', 'Untitled')
        icon = ICON_MAP.get(c_class, c_class.lower())

        # 1. Option: Restore ONLY this window
        display_restore = f"󰖯  Restore: {c_class} — {title}"
        entries.append({
            'action': 'restore',
            'address': addr,
            'title': title
        })
        rofi_lines.append(f"{display_restore}\0icon\x1f{icon}")

        # 2. Option: Close window without opening
        display_close = f"󰅖  ✕ Close (Quit): {c_class} — {title}"
        entries.append({
            'action': 'close',
            'address': addr,
            'title': title
        })
        rofi_lines.append(f"{display_close}\0icon\x1fprocess-stop")

    rofi_input = "\n".join(rofi_lines)

    rofi_cmd = [
        "rofi",
        "-dmenu",
        "-i",
        "-format", "i",
        "-p", "󰖯 Minimized Apps (Click to Restore or Close)",
        "-config", os.path.expanduser("~/.config/rofi/window.rasi")
    ]

    proc = subprocess.Popen(rofi_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, _ = proc.communicate(input=rofi_input)

    selected_str = stdout.strip()
    if not selected_str.isdigit():
        sys.exit(0)

    idx = int(selected_str)
    if idx < 0 or idx >= len(entries):
        sys.exit(0)

    target = entries[idx]
    target_addr = target['address']
    target_title = target['title']
    action = target['action']

    if action == "close":
        subprocess.run(['hyprctl', 'dispatch', 'closewindow', f"address:{target_addr}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        notify("✕ Window Closed", f"Closed '{target_title}' without opening.")
    elif action == "restore":
        try:
            active_ws_out = subprocess.check_output(['hyprctl', 'activeworkspace', '-j'], stderr=subprocess.DEVNULL)
            active_ws_id = json.loads(active_ws_out).get('id', 1)
        except Exception:
            active_ws_id = 1

        # Restore ONLY this specific window to current workspace
        subprocess.run(['hyprctl', 'dispatch', 'movetoworkspace', f"{active_ws_id},address:{target_addr}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['hyprctl', 'dispatch', 'focuswindow', f"address:{target_addr}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        notify("Window Restored", f"Restored '{target_title}' to Workspace {active_ws_id}.")

if __name__ == "__main__":
    main()
