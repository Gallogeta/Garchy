#!/usr/bin/env python3
"""
🌸 Garchy OS — Fast Desktop Application Indexer & Full Icon Path Resolver
Scans desktop entries and resolves exact icon filepaths (.svg / .png) from Papirus, hicolor, and system themes.
"""

import os
import sys
import glob
import json

CACHE_FILE = os.path.expanduser("~/.cache/garchy_desktop_apps.json")

def build_system_icon_index():
    """Builds a fast stem-to-filepath index for all available icon themes."""
    icon_index = {}
    
    active_icon_theme = "Tela-circle-pink-dark"
    try:
        with open(os.path.expanduser("~/.config/gally/active_theme.json"), "r") as f:
            t = json.load(f)
            active_icon_theme = t.get("icon_theme", "Tela-circle-pink-dark")
    except Exception:
        pass

    search_dirs = [
        f"/home/gallo/.local/share/icons/{active_icon_theme}",
        "/home/gallo/.local/share/icons/Tela-circle-pink-dark",
        "/home/gallo/.local/share/icons/Fluent-pink-dark",
        "/home/gallo/.local/share/icons/Candy",
        "/home/gallo/.local/share/icons/Papirus-Dark",
        "/home/gallo/.local/share/icons/Papirus",
        "/home/gallo/.local/share/icons",
        "/usr/share/icons/Papirus-Dark",
        "/usr/share/icons/Papirus",
        "/usr/share/icons/hicolor",
        "/usr/share/icons/Adwaita",
        "/usr/share/icons/AdwaitaLegacy",
        "/usr/share/pixmaps",
        "/var/lib/flatpak/exports/share/icons"
    ]

    for base in search_dirs:
        if not os.path.exists(base):
            continue
        for root, _, files in os.walk(base):
            for f in files:
                if f.endswith((".svg", ".png", ".xpm", ".webp")):
                    stem = os.path.splitext(f)[0].lower()
                    full = os.path.join(root, f)
                    # Prioritize scalable / 48x48 / SVGs
                    if stem not in icon_index or ("scalable" in full or "48" in full or full.endswith(".svg")):
                        icon_index[stem] = full
    return icon_index

def resolve_icon(icon_name, app_id, exec_cmd, icon_index):
    """Resolves an icon name or binary to an absolute file path."""
    if not icon_name:
        icon_name = app_id

    # If already an existing absolute path
    if os.path.isabs(icon_name) and os.path.exists(icon_name):
        return icon_name

    stem = os.path.splitext(os.path.basename(icon_name))[0].lower()
    
    # Try exact stem
    if stem in icon_index:
        return icon_index[stem]

    # Try app_id
    clean_id = app_id.lower()
    if clean_id in icon_index:
        return icon_index[clean_id]

    # Try binary name from exec_cmd
    if exec_cmd:
        bin_name = os.path.basename(exec_cmd.split()[0]).lower()
        if bin_name in icon_index:
            return icon_index[bin_name]

    # Try standard aliases
    aliases = {
        "code-oss": "code",
        "visual-studio-code": "code",
        "brave-browser": "brave",
        "thunar": "system-file-manager",
        "system-file-manager": "thunar",
        "xfce4-settings-manager": "preferences-desktop",
        "org.xfce.settings.manager": "preferences-desktop",
        "pavucontrol": "multimedia-volume-control",
        "spotify-client": "spotify",
        "discord": "discord",
        "vesktop": "discord",
        "btop": "utilities-system-monitor",
        "steam": "steam"
    }

    if stem in aliases and aliases[stem] in icon_index:
        return icon_index[aliases[stem]]

    return None

def determine_glyph(name, categories, exec_cmd):
    """Assigns an appropriate Nerd Font vector glyph based on application classification."""
    s = (name + " " + categories + " " + (exec_cmd or "")).lower()
    if any(k in s for k in ["terminal", "term", "kitty", "alacritty", "bash", "zsh", "console"]):
        return "󰄛"
    elif any(k in s for k in ["code", "editor", "ide", "develop", "studio", "nvim", "vim"]):
        return "󰨞"
    elif any(k in s for k in ["browser", "web", "internet", "chrome", "firefox", "brave"]):
        return "󰖟"
    elif any(k in s for k in ["file", "manager", "thunar", "folder", "nautilus", "dolphin"]):
        return "󰉋"
    elif any(k in s for k in ["game", "steam", "heroic", "lutris", "play", "retro"]):
        return "󰓓"
    elif any(k in s for k in ["music", "audio", "sound", "spotify", "player", "pavucontrol", "volume"]):
        return "󰓇"
    elif any(k in s for k in ["video", "media", "mpv", "vlc", "movie", "haruna"]):
        return "󰕼"
    elif any(k in s for k in ["image", "photo", "graphics", "gimp", "draw", "inkscape", "paint"]):
        return "󰋩"
    elif any(k in s for k in ["setting", "config", "control", "pref", "appearance"]):
        return "󰒓"
    elif any(k in s for k in ["monitor", "task", "system", "btop", "htop", "process"]):
        return "󰍛"
    elif any(k in s for k in ["chat", "message", "discord", "telegram", "vesktop", "talk"]):
        return "󰭹"
    return "󰀻"

def get_installed_apps(icon_index):
    dirs = [
        "/usr/share/applications",
        os.path.expanduser("~/.local/share/applications"),
        "/var/lib/flatpak/exports/share/applications",
        os.path.expanduser("~/.local/share/flatpak/exports/share/applications")
    ]
    apps = []
    seen = set()

    for d in dirs:
        if not os.path.exists(d):
            continue
        for f in glob.glob(os.path.join(d, "*.desktop")):
            try:
                name = None
                icon = None
                exec_cmd = None
                comment = ""
                categories = ""
                nodisplay = False

                with open(f, "r", encoding="utf-8", errors="ignore") as fp:
                    in_entry = False
                    for line in fp:
                        line = line.strip()
                        if line == "[Desktop Entry]":
                            in_entry = True
                        elif line.startswith("[") and in_entry:
                            break
                        if in_entry:
                            if line.startswith("Name=") and not name:
                                name = line.split("=", 1)[1].strip()
                            elif line.startswith("Icon=") and not icon:
                                icon = line.split("=", 1)[1].strip()
                            elif line.startswith("Exec=") and not exec_cmd:
                                raw_exec = line.split("=", 1)[1].strip()
                                parts = [p for p in raw_exec.split() if not p.startswith("%")]
                                exec_cmd = " ".join(parts)
                            elif line.startswith("Comment=") and not comment:
                                comment = line.split("=", 1)[1].strip()
                            elif line.startswith("Categories="):
                                categories = line.split("=", 1)[1].strip()
                            elif line.startswith("NoDisplay=true") or line.startswith("Hidden=true"):
                                nodisplay = True

                if name and exec_cmd and not nodisplay:
                    app_id = os.path.splitext(os.path.basename(f))[0]
                    if name.lower() not in seen:
                        seen.add(name.lower())
                        resolved_path = resolve_icon(icon, app_id, exec_cmd, icon_index)
                        glyph = determine_glyph(name, categories, exec_cmd)
                        apps.append({
                            "id": app_id,
                            "name": name,
                            "icon": icon or app_id,
                            "icon_path": resolved_path or "",
                            "glyph": glyph,
                            "exec": exec_cmd,
                            "comment": comment,
                            "categories": categories
                        })
            except Exception:
                continue

    apps.sort(key=lambda x: x["name"].lower())
    return apps

def update_cache():
    icon_index = build_system_icon_index()
    apps = get_installed_apps(icon_index)
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(apps, f, indent=2)
    return apps

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "json":
        apps = update_cache()
        print(json.dumps(apps))
    else:
        apps = update_cache()
        resolved_count = sum(1 for a in apps if a["icon_path"])
        print(f"Indexed {len(apps)} apps ({resolved_count} icons resolved) to {CACHE_FILE}")
