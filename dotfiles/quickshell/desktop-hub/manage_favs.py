#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import re
import shlex

FAV_FILE = os.path.expanduser("~/.config/quickshell/desktop-hub/favorites.json")
ROFI_CONFIG = os.path.expanduser("~/.config/rofi/config.rasi")

def clean_exec(exec_str):
    # Remove desktop field codes: %u, %U, %f, %F, %i, %c, %k, %d, %D, %n, %N, %v, %m, %%
    cleaned = re.sub(r'%[a-zA-Z%]', '', exec_str).strip()
    return cleaned

def get_icon(name, exec_cmd, categories, icon_name, file_path=''):
    txt = f"{name} {exec_cmd} {categories} {icon_name} {file_path}".lower()
    if any(k in txt for k in ['steam', 'rungameid']):
        return '󰓓'
    if any(k in txt for k in ['game', 'lutris', 'heroic', 'wine', 'soulframe', 'proton', 'retroarch', 'emulator', 'play', 'hitman', 'fallout', 'morrowind', 'subnautica', 'poe', 'exile', 'dyson', 'dawn of man', 'deep rock', 'backrooms', 'huniecam', 'red lantern']):
        return '󰊴'
    if any(k in txt for k in ['code', 'nvim', 'vim', 'editor', 'studio', 'sublime', 'text', 'ide', 'develop']):
        return '󰨞'
    if any(k in txt for k in ['firefox', 'browser', 'chrome', 'brave', 'opera', 'edge', 'chromium', 'web', 'zen', 'vivaldi']):
        return '󰖟'
    if any(k in txt for k in ['term', 'kitty', 'alacritty', 'foot', 'console', 'bash', 'zsh', 'wezterm']):
        return ''
    if any(k in txt for k in ['file', 'thunar', 'nautilus', 'dolphin', 'nemo', 'pcmanfm', 'folder']):
        return '󰋜'
    if any(k in txt for k in ['video', 'player', 'mpv', 'vlc', 'kdenlive', 'obs', 'movie', 'davinci', 'handbrake']):
        return '󰕼'
    if any(k in txt for k in ['audio', 'music', 'spotify', 'easyeffects', 'sound', 'mix', 'cava', 'audacity']):
        return '󰓃'
    if any(k in txt for k in ['discord', 'signal', 'telegram', 'chat', 'slack', 'messenger', 'vesktop', 'element']):
        return '󰭹'
    if any(k in txt for k in ['image', 'gimp', 'inkscape', 'krita', 'draw', 'paint', 'photo', 'blender', 'viewer', 'viewnior']):
        return '󰋩'
    if any(k in txt for k in ['settings', 'config', 'control', 'manager', 'tweak']):
        return '󰒓'
    return '󰀻'

def get_file_icon(path):
    if os.path.isdir(path):
        return '󰋜'
    lower = path.lower()
    if any(lower.endswith(ext) for ext in ['.mp4', '.mkv', '.avi', '.webm', '.mov', '.flv', '.wmv']):
        return '󰕼'
    if any(lower.endswith(ext) for ext in ['.mp3', '.flac', '.wav', '.ogg', '.m4a', '.opus', '.aac']):
        return '󰎆'
    if any(lower.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg', '.bmp', '.ico']):
        return '󰋩'
    if any(lower.endswith(ext) for ext in ['.pdf']):
        return '󰈦'
    if any(lower.endswith(ext) for ext in ['.zip', '.tar', '.gz', '.xz', '.7z', '.rar', '.bz2', '.iso']):
        return '󰛫'
    if any(lower.endswith(ext) for ext in ['.sh', '.py', '.bin', '.appimage', '.exe', '.bat', '.lnk']) or os.access(path, os.X_OK):
        if any(k in lower for k in ['game', 'proton', 'wine', 'soulframe', 'steam', 'play']):
            return '󰊴'
        return '󱕵'
    if any(lower.endswith(ext) for ext in ['.txt', '.md', '.doc', '.docx', '.odt', '.rtf', '.csv', '.xlsx']):
        return '󰈔'
    if any(lower.endswith(ext) for ext in ['.json', '.yml', '.yaml', '.toml', '.conf', '.ini', '.rasi', '.qml']):
        return '󰨞'
    return '󰈔'

def load_favorites():
    if os.path.exists(FAV_FILE):
        try:
            with open(FAV_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception as e:
            print(f"Error loading favorites: {e}", file=sys.stderr)
    return []

def save_favorites_list(favs):
    try:
        tmp_file = FAV_FILE + ".tmp"
        with open(tmp_file, 'w', encoding='utf-8') as f:
            json.dump(favs, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.replace(tmp_file, FAV_FILE)
        return True
    except Exception as e:
        print(f"Error saving favorites: {e}", file=sys.stderr)
        return False

def add_favorite(name, command, icon="󰀻", description=""):
    favs = load_favorites()
    # Avoid duplicate commands
    for item in favs:
        if item.get("command") == command:
            item["name"] = name
            item["icon"] = icon
            item["description"] = description or name
            save_favorites_list(favs)
            subprocess.run(["notify-send", "-a", "Desktop Hub", "Favorite Updated", f"Updated '{name}' in Favorites!"])
            return
    
    favs.append({
        "name": name,
        "icon": icon,
        "command": command,
        "description": description or name
    })
    save_favorites_list(favs)
    subprocess.run(["notify-send", "-a", "Desktop Hub", "Favorite Added", f"Added '{name}' to Favorites!"])

def scan_desktop_files():
    search_dirs = [
        os.path.expanduser('~/Desktop'),
        os.path.expanduser('~/Desktop/Desktop'),
        os.path.expanduser('~/.local/share/applications'),
        os.path.expanduser('~/.local/share/flatpak/exports/share/applications'),
        '/usr/share/applications',
        '/usr/local/share/applications',
        '/var/lib/flatpak/exports/share/applications',
        '/var/lib/snapd/desktop/applications'
    ]

    apps = {}
    for d in search_dirs:
        if not os.path.exists(d):
            continue
        for root, _, files in os.walk(d):
            for f in files:
                if f.endswith('.desktop'):
                    path = os.path.join(root, f)
                    try:
                        with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                            content = fp.read()

                        lines = content.splitlines()
                        entry_dict = {}
                        in_entry = False
                        for line in lines:
                            line = line.strip()
                            if line.startswith('[') and line.endswith(']'):
                                in_entry = (line == '[Desktop Entry]')
                                continue
                            if in_entry and '=' in line and not line.startswith('#'):
                                k, v = line.split('=', 1)
                                if k not in entry_dict:
                                    entry_dict[k] = v

                        if entry_dict.get('NoDisplay') == 'true' or entry_dict.get('Hidden') == 'true':
                            continue
                        if entry_dict.get('Type') and entry_dict.get('Type') != 'Application':
                            continue

                        name = entry_dict.get('Name')
                        exec_line = entry_dict.get('Exec')
                        if name and exec_line:
                            clean_cmd = clean_exec(exec_line)
                            icon = get_icon(name, clean_cmd, entry_dict.get('Categories', ''), entry_dict.get('Icon', ''), path)
                            desc = entry_dict.get('Comment', name)
                            key = f"{name} ({clean_cmd})".lower()
                            if key not in apps:
                                apps[key] = {
                                    'name': name,
                                    'command': clean_cmd,
                                    'icon': icon,
                                    'description': desc,
                                    'path': path
                                }
                    except Exception:
                        pass
    return list(apps.values())

def run_rofi(prompt, options_list):
    try:
        input_data = "\n".join(options_list)
        res = subprocess.run(
            ["rofi", "-dmenu", "-i", "-p", prompt, "-config", ROFI_CONFIG],
            input=input_data,
            text=True,
            capture_output=True
        )
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception as e:
        print(f"Error running rofi: {e}", file=sys.stderr)
    return None

def browse_file():
    # Try zenity first, then kdialog
    selected_path = None
    try:
        res = subprocess.run(
            ["zenity", "--file-selection", "--title=Select Application, Game, Script, or File to Add"],
            text=True,
            capture_output=True
        )
        if res.returncode == 0 and res.stdout.strip():
            selected_path = res.stdout.strip()
    except Exception:
        pass

    if not selected_path:
        try:
            res = subprocess.run(
                ["kdialog", "--getopenfilename", os.path.expanduser("~"), "All Files (*.*)"],
                text=True,
                capture_output=True
            )
            if res.returncode == 0 and res.stdout.strip():
                selected_path = res.stdout.strip()
        except Exception:
            pass

    if not selected_path:
        return

    # Check if the chosen file is a .desktop file
    if selected_path.endswith(".desktop") and os.path.isfile(selected_path):
        try:
            with open(selected_path, 'r', encoding='utf-8', errors='ignore') as fp:
                content = fp.read()
            entry_dict = {}
            in_entry = False
            for line in content.splitlines():
                line = line.strip()
                if line.startswith('[') and line.endswith(']'):
                    in_entry = (line == '[Desktop Entry]')
                    continue
                if in_entry and '=' in line and not line.startswith('#'):
                    k, v = line.split('=', 1)
                    if k not in entry_dict:
                        entry_dict[k] = v
            name = entry_dict.get('Name', os.path.basename(selected_path).replace('.desktop', ''))
            exec_line = clean_exec(entry_dict.get('Exec', selected_path))
            icon = get_icon(name, exec_line, entry_dict.get('Categories', ''), entry_dict.get('Icon', ''), selected_path)
            desc = entry_dict.get('Comment', name)
            add_favorite(name, exec_line, icon, desc)
            return
        except Exception:
            pass

    # Generic file / script / binary / directory
    base_name = os.path.basename(selected_path)
    if '.' in base_name and not base_name.startswith('.'):
        suggested_name = base_name.rsplit('.', 1)[0]
    else:
        suggested_name = base_name

    # Ask for clean display name
    name_input = None
    try:
        res = subprocess.run(
            ["zenity", "--entry", "--title=Display Name", f"--text=Enter name for '{base_name}':", f"--entry-text={suggested_name}"],
            text=True,
            capture_output=True
        )
        if res.returncode == 0 and res.stdout.strip():
            name_input = res.stdout.strip()
    except Exception:
        pass

    if not name_input:
        name_input = suggested_name

    icon = get_file_icon(selected_path)

    # Determine command
    if os.path.isdir(selected_path):
        cmd = f"thunar '{selected_path}'"
    elif os.access(selected_path, os.X_OK) or selected_path.endswith(('.sh', '.bin', '.AppImage', '.py')):
        cmd = f"'{selected_path}'"
    else:
        cmd = f"xdg-open '{selected_path}'"

    add_favorite(name_input, cmd, icon, f"File: {base_name}")

def add_custom_command():
    cmd_prompt = run_rofi("󰐕 Enter Command / Executable Path:", [])
    if not cmd_prompt:
        return
    
    suggested_name = cmd_prompt.split()[0] if cmd_prompt.split() else "Custom App"
    suggested_name = os.path.basename(suggested_name).capitalize()
    
    name_prompt = run_rofi(f"󰐕 Enter Display Name [{suggested_name}]:", [])
    display_name = name_prompt if name_prompt else suggested_name
    
    icon = get_icon(display_name, cmd_prompt, '', '', cmd_prompt)
    add_favorite(display_name, cmd_prompt, icon, display_name)

def handle_add():
    apps = scan_desktop_files()
    apps.sort(key=lambda x: x['name'].lower())

    action_browse = "📂  [Browse File / Program / Script / Game / Media...]"
    action_custom = "⌨️   [Enter Custom Command or Path...]"

    rofi_lines = [action_browse, action_custom]
    app_map = {}

    for app in apps:
        line = f"{app['icon']}  {app['name']}  ·  {app['command']}"
        rofi_lines.append(line)
        app_map[line] = app

    selected = run_rofi("󰐕 Add to Favorites", rofi_lines)
    if not selected:
        return

    if selected == action_browse:
        browse_file()
    elif selected == action_custom:
        add_custom_command()
    elif selected in app_map:
        app = app_map[selected]
        add_favorite(app['name'], app['command'], app['icon'], app['description'])
    else:
        # User typed something custom and pressed Enter
        typed = selected.strip()
        if os.path.exists(typed):
            # It is a real path on disk
            icon = get_file_icon(typed)
            name = os.path.basename(typed)
            if os.path.isdir(typed):
                cmd = f"thunar '{typed}'"
            elif os.access(typed, os.X_OK):
                cmd = f"'{typed}'"
            else:
                cmd = f"xdg-open '{typed}'"
            add_favorite(name, cmd, icon, name)
        else:
            # Custom command
            name = os.path.basename(typed.split()[0]).capitalize()
            icon = get_icon(name, typed, '', '')
            add_favorite(name, typed, icon, name)

def handle_launch(args):
    if not args:
        return
    full_cmd = " ".join(args).strip()
    if not full_cmd:
        return

    # Check if command is simply a file or folder path without a leading executable
    unquoted = full_cmd.strip("'\"")
    if os.path.exists(unquoted):
        if os.path.isdir(unquoted):
            full_cmd = f"thunar '{unquoted}'"
        elif not os.access(unquoted, os.X_OK) and not unquoted.endswith(('.sh', '.py', '.AppImage', '.bin')):
            full_cmd = f"xdg-open '{unquoted}'"

    # Launch detached in background with setsid bash
    subprocess.Popen(
        ["setsid", "bash", "-c", full_cmd],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True
    )

def handle_save(args):
    if not args:
        return
    raw_json = " ".join(args).strip()
    try:
        parsed = json.loads(raw_json)
        if isinstance(parsed, list) and len(parsed) > 0:
            save_favorites_list(parsed)
    except Exception as e:
        print(f"Error parsing json in save: {e}", file=sys.stderr)

def main():
    if len(sys.argv) < 2:
        print("Usage: manage_favs.py [add | save <json> | launch <command>]")
        sys.exit(1)

    action = sys.argv[1]
    if action == "add":
        handle_add()
    elif action == "launch":
        handle_launch(sys.argv[2:])
    elif action == "save":
        handle_save(sys.argv[2:])
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()
