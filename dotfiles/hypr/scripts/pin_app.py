#!/usr/bin/env python3
"""
Gally OS — Dynamic Application Pinning Service
Allows pinning/unpinning favorite applications to the taskbar.
"""

import os
import sys
import json

PINNED_FILE = os.path.expanduser("~/.config/gally/pinned_apps.json")

DEFAULT_PINNED = [
    {"id": "brave", "name": "Brave Browser", "icon": "brave-browser", "cmd": "brave"},
    {"id": "kitty", "name": "Garchy Terminal", "icon": "utilities-terminal", "cmd": "kitty"},
    {"id": "thunar", "name": "Files", "icon": "system-file-manager", "cmd": "thunar"},
    {"id": "code", "name": "VS Code", "icon": "code", "cmd": "code"}
]

def load_pinned():
    if os.path.exists(PINNED_FILE):
        try:
            with open(PINNED_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_PINNED.copy()

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
        app_id = sys.argv[2].lower()
        name = sys.argv[3] if len(sys.argv) > 3 else app_id.capitalize()
        icon = sys.argv[4] if len(sys.argv) > 4 else app_id
        exec_cmd = sys.argv[5] if len(sys.argv) > 5 else app_id

        # Check if already pinned
        for p in pinned:
            if p.get("id") == app_id:
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
        new_pinned = [p for p in pinned if p.get("id") != app_id and p.get("name").lower() != app_id]
        save_pinned(new_pinned)
        print(f"Unpinned '{app_id}' successfully.")

    elif cmd == "toggle":
        if len(sys.argv) < 3:
            print("Usage: pin_app.py toggle <id> [name] [icon] [cmd]", file=sys.stderr)
            sys.exit(1)
        app_id = sys.argv[2].lower()
        exists = any(p.get("id") == app_id for p in pinned)
        if exists:
            new_pinned = [p for p in pinned if p.get("id") != app_id]
            save_pinned(new_pinned)
            print(f"Unpinned '{app_id}'.")
        else:
            name = sys.argv[3] if len(sys.argv) > 3 else app_id.capitalize()
            icon = sys.argv[4] if len(sys.argv) > 4 else app_id
            exec_cmd = sys.argv[5] if len(sys.argv) > 5 else app_id
            pinned.append({"id": app_id, "name": name, "icon": icon, "cmd": exec_cmd})
            save_pinned(pinned)
            print(f"Pinned '{name}'.")

if __name__ == "__main__":
    main()
