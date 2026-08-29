#!/usr/bin/env python3
"""
Gally OS — Dynamic Application Pinning Service
Allows pinning/unpinning favorite applications to the taskbar dock.
"""

import os
import sys
import json
import shutil

PINNED_FILE = os.path.expanduser("~/.config/gally/pinned_apps.json")

def resolve_cmd(app_id, cmd):
    if not cmd:
        cmd = app_id
    if shutil.which(cmd):
        return cmd
    mapping = {
        "brave-browser": "brave",
        "brave": "brave",
        "code-oss": "code",
        "code": "code",
        "visual-studio-code": "code",
        "xfce4-terminal": "kitty",
        "terminal": "kitty",
        "utilities-terminal": "kitty",
        "thunar": "thunar",
        "system-file-manager": "thunar",
    }
    alt = mapping.get(app_id.lower()) or mapping.get(cmd.lower())
    if alt and shutil.which(alt):
        return alt
    return cmd

def resolve_icon(app_id, icon):
    if not icon or icon == "app" or icon == "application-x-executable":
        icon = app_id
    icon_map = {
        "brave-browser": "brave-desktop",
        "brave": "brave-desktop",
        "code-oss": "code",
        "code": "code",
        "kitty": "kitty",
        "thunar": "system-file-manager",
        "discord": "discord",
        "vesktop": "vesktop",
        "steam": "steam",
        "heroic": "heroic",
        "spotify": "spotify",
        "pavucontrol": "org.pulseaudio.pavucontrol"
    }
    return icon_map.get(app_id.lower(), icon_map.get(icon.lower(), icon))

def load_pinned():
    if os.path.exists(PINNED_FILE):
        try:
            with open(PINNED_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception:
            pass
    return []

def save_pinned(pinned_list):
    os.makedirs(os.path.dirname(PINNED_FILE), exist_ok=True)
    with open(PINNED_FILE, "w") as f:
        json.dump(pinned_list, f, indent=2)

def main():
    if len(sys.argv) < 2:
        print(json.dumps(load_pinned(), indent=2))
        return

    cmd = sys.argv[1]
    pinned = load_pinned()

    if cmd == "list":
        print(json.dumps(pinned))
    elif cmd == "add":
        if len(sys.argv) < 3:
            print("Usage: pin_app.py add <id> [name] [icon] [cmd]", file=sys.stderr)
            sys.exit(1)
        raw_id = sys.argv[2].lower()
        app_id = "brave" if "brave" in raw_id else raw_id
        name = sys.argv[3] if len(sys.argv) > 3 else app_id.capitalize()
        raw_icon = sys.argv[4] if len(sys.argv) > 4 else app_id
        raw_cmd = sys.argv[5] if len(sys.argv) > 5 else app_id

        exec_cmd = resolve_cmd(app_id, raw_cmd)
        icon = resolve_icon(app_id, raw_icon)

        # Check if already pinned
        for p in pinned:
            if p.get("id") == app_id or p.get("cmd") == exec_cmd:
                print(f"App '{app_id}' already pinned.")
                return

        pinned.append({"id": app_id, "name": name, "icon": icon, "cmd": exec_cmd})
        save_pinned(pinned)
        print(f"Pinned '{name}' successfully.")

    elif cmd == "remove":
        if len(sys.argv) < 3:
            print("Usage: pin_app.py remove <id>", file=sys.stderr)
            sys.exit(1)
        app_id = sys.argv[2].lower()
        new_pinned = [p for p in pinned if p.get("id") != app_id and p.get("cmd") != app_id and p.get("name", "").lower() != app_id]
        save_pinned(new_pinned)
        print(f"Unpinned '{app_id}' successfully.")

    elif cmd == "clear":
        save_pinned([])
        print("Cleared all pinned apps.")

    elif cmd == "toggle":
        if len(sys.argv) < 3:
            print("Usage: pin_app.py toggle <id> [name] [icon] [cmd]", file=sys.stderr)
            sys.exit(1)
        raw_id = sys.argv[2].lower()
        app_id = "brave" if "brave" in raw_id else raw_id
        exists = any(p.get("id") == app_id or p.get("cmd") == app_id for p in pinned)
        if exists:
            new_pinned = [p for p in pinned if p.get("id") != app_id and p.get("cmd") != app_id]
            save_pinned(new_pinned)
            print(f"Unpinned '{app_id}'.")
        else:
            name = sys.argv[3] if len(sys.argv) > 3 else app_id.capitalize()
            raw_icon = sys.argv[4] if len(sys.argv) > 4 else app_id
            raw_cmd = sys.argv[5] if len(sys.argv) > 5 else app_id
            exec_cmd = resolve_cmd(app_id, raw_cmd)
            icon = resolve_icon(app_id, raw_icon)
            pinned.append({"id": app_id, "name": name, "icon": icon, "cmd": exec_cmd})
            save_pinned(pinned)
            print(f"Pinned '{name}'.")

if __name__ == "__main__":
    main()
