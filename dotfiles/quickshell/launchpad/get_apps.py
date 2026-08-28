#!/usr/bin/env python3
import os
import sys
import json

CACHE_FILE = os.path.expanduser("~/.cache/quickshell_launchpad_apps.json")

def get_icon_score(path):
    score = 0
    lower = path.lower()
    if lower.endswith(".svg"):
        score += 1000
    if "scalable" in lower:
        score += 500
    elif "512x512" in lower:
        score += 400
    elif "256x256" in lower:
        score += 300
    elif "128x128" in lower:
        score += 200
    elif "64x64" in lower:
        score += 100
    elif "48x48" in lower:
        score += 50
    elif "32x32" in lower:
        score += 10
    elif "16x16" in lower or "22x22" in lower or "24x24" in lower:
        score += 1

    if "papirus-dark" in lower or "tela" in lower or "we10x" in lower:
        score += 50
    elif "papirus" in lower:
        score += 40
    return score

def build_icon_index():
    icon_map = {}
    base_dirs = [
        os.path.expanduser("~/.local/share/icons/Papirus-Dark"),
        os.path.expanduser("~/.local/share/icons"),
        "/usr/share/icons/Papirus-Dark",
        "/usr/share/icons/Papirus",
        "/usr/share/icons/hicolor",
        "/usr/share/pixmaps"
    ]
    for b in base_dirs:
        if not os.path.isdir(b):
            continue
        for root, _, files in os.walk(b):
            for f in files:
                if f.endswith(".svg") or f.endswith(".png"):
                    full_path = os.path.join(root, f)
                    if os.path.islink(full_path) and not os.path.exists(full_path):
                        continue # Skip broken symlinks
                    
                    stem = os.path.splitext(f)[0]
                    new_score = get_icon_score(full_path)
                    if stem not in icon_map or new_score > icon_map[stem][1]:
                        icon_map[stem] = (full_path, new_score)
    return icon_map

def resolve_app_icon(icon_val, name, exec_cmd, icon_map):
    default_icon = icon_map.get("application-x-executable", ("", 0))[0]

    if icon_val:
        # 1. Direct path
        if os.path.isabs(icon_val) and os.path.exists(icon_val):
            return "file://" + icon_val
        
        # 2. Exact match in icon index
        if icon_val in icon_map and os.path.exists(icon_map[icon_val][0]):
            return "file://" + icon_map[icon_val][0]
        
        # 3. Lowercase match
        if icon_val.lower() in icon_map and os.path.exists(icon_map[icon_val.lower()][0]):
            return "file://" + icon_map[icon_val.lower()][0]
        
        # 4. Reverse-DNS unprefixing (e.g. org.gnome.Papers -> papers, com.visualstudio.code -> code)
        short_stem = icon_val.split(".")[-1].lower()
        if short_stem in icon_map and os.path.exists(icon_map[short_stem][0]):
            return "file://" + icon_map[short_stem][0]

    # 5. Fallback via app name matching
    name_stem = name.lower().replace(" ", "-")
    if name_stem in icon_map and os.path.exists(icon_map[name_stem][0]):
        return "file://" + icon_map[name_stem][0]

    # 6. Fallback via executable binary name
    bin_stem = exec_cmd.split()[0].split("/")[-1].lower() if exec_cmd else ""
    if bin_stem in icon_map and os.path.exists(icon_map[bin_stem][0]):
        return "file://" + icon_map[bin_stem][0]

    # 7. Game / Steam specific fallback
    if "steam" in exec_cmd.lower() or "game" in name.lower():
        game_icon = icon_map.get("applications-games", icon_map.get("steam", ("", 0)))[0]
        if game_icon and os.path.exists(game_icon):
            return "file://" + game_icon

    return ("file://" + default_icon) if default_icon else ""

def is_ignored_app(name, exec_cmd, categories, only_show_in):
    # 1. Hide XFCE desktop settings applets when running in Hyprland
    if "XFCE" in only_show_in and "Hyprland" not in only_show_in:
        return True
    if any(c in categories for c in [
        "X-XFCE-SettingsDialog",
        "X-XFCE-PersonalSettings",
        "X-XFCE-HardwareSettings",
        "X-XFCE-SystemSettings"
    ]):
        return True
    
    exec_lower = exec_cmd.lower()
    name_lower = name.lower()

    # 2. XFCE control panels
    xfce_settings_execs = [
        "xfce4-appearance-settings", "xfce4-accessibility-settings", "xfce4-keyboard-settings",
        "xfce4-mouse-settings", "xfce4-display-settings", "xfce4-color-settings",
        "xfce4-mime-settings", "xfdesktop-settings", "xfce4-screensaver-preferences",
        "xfce4-session-settings", "xfce4-settings-editor", "xfce4-settings-manager",
        "xfce4-panel --preferences", "xfwm4-settings", "xfwm4-tweaks-settings",
        "xfwm4-workspace-settings", "xfce4-appfinder", "xfce4-session-logout",
        "exo-open --launch", "thunar-volman-settings", "thunar --bulk-rename",
        "xfce4-about", "xfce4-clipman-settings", "xfce4-power-manager-settings",
        "xfce4-notifyd-config", "xfce4-sensors", "xfce4-taskmanager", "xfce4-dict",
        "xfce4-notes"
    ]
    for x in xfce_settings_execs:
        if x in exec_lower:
            return True

    # 3. Diagnostic / Internal helper / Duplicate launchers
    ignored_patterns = [
        "torbrowser-launcher --settings",
        "octopi-cachecleaner",
        "octopi-notifier",
        "octopi-repoeditor",
        "scrcpy --pause-on-exit",
        "xdg-open http://localhost:631",
        "xgps",
        "xgpsspeed",
        "gcm-viewer",
        "malcontent-control",
        "plasmaengineexplorer",
        "lookandfeelexplorer",
        "plasmathemeexplorer",
        "iconexplorer",
        "kmenuedit",
        "plasma-emojier",
        "kwalletmanager5",
        "drkonqi-coredump-gui",
        "lightdm-gtk-greeter-settings",
        "rygel-preferences",
        "ibus-setup",
        "assistant6", "designer6", "linguist6", "qdbusviewer6", "qv4l2", "qvidcap",
        "/usr/lib/xfce4-screensaver"
    ]
    for p in ignored_patterns:
        if p in exec_lower:
            return True

    if name_lower in [
        "tor browser launcher settings", "octopi cachecleaner", "octopi notifier",
        "octopi repository editor", "scrcpy (console)", "manage printing",
        "xgps", "xgpsspeed", "color profile viewer", "parental controls",
        "menu editor", "kwalletmanager", "emoji selector", "plasma engine explorer",
        "plasma global theme explorer", "plasma theme explorer", "icon explorer",
        "crashed processes viewer", "ibus preferences", "rygel preferences",
        "lightdm gtk greeter settings", "floating xfce", "pop art squares", "slideshow"
    ]:
        return True

    return False

def scan_desktop_files(icon_map):
    search_dirs = [
        os.path.expanduser("~/.local/share/applications"),
        "/usr/local/share/applications",
        "/usr/share/applications"
    ]
    seen_filenames = set()
    seen_names = set()
    apps = []

    for d in search_dirs:
        if not os.path.isdir(d):
            continue
        for root, _, files in os.walk(d):
            for file in files:
                if not file.endswith(".desktop"):
                    continue
                
                # Check for duplicate desktop files across user & system dirs
                if file in seen_filenames:
                    continue
                seen_filenames.add(file)

                path = os.path.join(root, file)
                try:
                    name = None
                    exec_cmd = None
                    icon_val = ""
                    categories = ""
                    only_show_in = ""
                    no_display = False
                    terminal = False
                    is_app = False

                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            line = line.strip()
                            if line == "[Desktop Entry]":
                                is_app = True
                            elif line.startswith("[") and line != "[Desktop Entry]":
                                break
                            elif "=" in line:
                                k, v = line.split("=", 1)
                                k, v = k.strip(), v.strip()
                                if k == "Name" and not name:
                                    name = v
                                elif k == "Exec" and not exec_cmd:
                                    clean_exec = " ".join([arg for arg in v.split() if not arg.startswith("%")])
                                    exec_cmd = clean_exec
                                elif k == "Icon" and not icon_val:
                                    icon_val = v
                                elif k == "NoDisplay" and v.lower() == "true":
                                    no_display = True
                                elif k == "Terminal" and v.lower() == "true":
                                    terminal = True
                                elif k == "Type" and v != "Application":
                                    is_app = False
                                elif k == "Categories":
                                    categories = v
                                elif k == "OnlyShowIn":
                                    only_show_in = v

                    if is_app and name and exec_cmd and not no_display:
                        # Automatically filter ignored and internal tools
                        if is_ignored_app(name, exec_cmd, categories, only_show_in):
                            continue

                        if name.lower() not in seen_names:
                            seen_names.add(name.lower())
                            if terminal:
                                exec_cmd = f"kitty -e {exec_cmd}"
                            
                            resolved_icon = resolve_app_icon(icon_val, name, exec_cmd, icon_map)

                            apps.append({
                                "name": name,
                                "exec": exec_cmd,
                                "icon": resolved_icon
                            })
                except Exception:
                    continue

    apps.sort(key=lambda x: x["name"].lower())
    return apps

def main():
    force_refresh = "--refresh" in sys.argv
    if not force_refresh and os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                print(f.read())
                return
        except Exception:
            pass

    icon_map = build_icon_index()
    apps = scan_desktop_files(icon_map)
    out = json.dumps(apps, indent=2)
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        f.write(out)
    print(out)

if __name__ == "__main__":
    main()
