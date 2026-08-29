#!/usr/bin/env python3
"""
Gally OS — Shared Desktop Theme State Controller
Synchronizes active theme colors, borders, corner rounding, icon sets,
and terminal palettes across Quickshell, Hyprland, GTK 3/4, Rofi, Cava, and Kitty.
"""

import os
import sys
import re
import json
import subprocess

THEME_STATE_FILE = os.path.expanduser("~/.config/gally/active_theme.json")
CACHE_THEME_FILE = os.path.expanduser("~/.cache/garchy_theme.json")
THEMES_DIR = os.path.expanduser("~/.config/gally/themes")

DEFAULT_THEME = {
    "id": "garchy",
    "name": "Garchy Signature",
    "desc": "Official Garchy aesthetic: Obsidian titanium glass, sapphire blue, electric cyan, and Orokin gold.",
    "bg": "#070b12",
    "bg_card": "#0f172a",
    "bg_input": "#0f172a",
    "bg_alt": "#141e33",
    "fg": "#f8fafc",
    "fg_muted": "#94a3b8",
    "accent": "#38bdf8",
    "accent_alt": "#2563eb",
    "gold": "#fbbf24",
    "border_col": "#38bdf8",
    "border": "#1e293b",
    "rounding": 6,
    "bar_height": 46,
    "layout_style": "garchy",
    "border_width": 1.5,
    "icon_theme": "Papirus-Dark"
}

def get_all_themes():
    """Loads all 6 themes from ~/.config/gally/themes/."""
    themes = []
    if os.path.exists(THEMES_DIR):
        for fname in sorted(os.listdir(THEMES_DIR)):
            if fname.endswith(".json"):
                fpath = os.path.join(THEMES_DIR, fname)
                try:
                    with open(fpath, "r") as f:
                        data = json.load(f)
                    if isinstance(data, dict) and "name" in data:
                        if "id" not in data:
                            data["id"] = fname.replace(".json", "")
                        themes.append(data)
                except Exception as err:
                    print(f"Error loading theme {fname}: {err}", file=sys.stderr)
    return themes

def get_active_theme():
    if os.path.exists(THEME_STATE_FILE):
        try:
            with open(THEME_STATE_FILE, "r") as f:
                data = json.load(f)
                res = DEFAULT_THEME.copy()
                res.update(data)
                return res
        except Exception:
            pass
    return DEFAULT_THEME.copy()

def get_theme_mtime():
    if os.path.exists(THEME_STATE_FILE):
        try:
            return os.path.getmtime(THEME_STATE_FILE)
        except Exception:
            pass
    return 0.0

def save_active_theme(theme_dict):
    apply_theme(theme_dict)

def update_hyprland_look_lua(theme_dict):
    """Updates active border colors and window rounding in look.lua and reloads Hyprland."""
    look_path = os.path.expanduser("~/.config/hypr/lua/look.lua")
    if not os.path.exists(look_path):
        return

    accent = theme_dict.get("accent", "#38bdf8").lstrip("#")
    accent_alt = theme_dict.get("accent_alt", "#2563eb").lstrip("#")
    bg = theme_dict.get("bg", "#070b12").lstrip("#")
    rounding = theme_dict.get("rounding", 6)

    active_colors_str = f'{{ colors = {{ "rgba({accent}ee)", "rgba({accent_alt}ee)" }}, angle = 45 }}'
    inactive_color_str = f'"rgba({bg}88)"'

    try:
        with open(look_path, "r") as f:
            content = f.read()

        # Update rounding
        content = re.sub(r'rounding\s*=\s*\d+', f'rounding = {rounding}', content)

        # Update active_border (match whole active_border line)
        content = re.sub(
            r'active_border\s*=\s*\{.+?\},?\s*\n',
            f'active_border = {active_colors_str},\n',
            content
        )

        # Update inactive_border
        content = re.sub(
            r'inactive_border\s*=\s*["\'][^"\']+["\']',
            f'inactive_border = {inactive_color_str}',
            content
        )

        with open(look_path, "w") as f:
            f.write(content)

        subprocess.run(["hyprctl", "reload"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as err:
        print(f"Error updating look.lua: {err}", file=sys.stderr)

def generate_kitty_theme_config(theme_dict):
    name = theme_dict.get("name", "Garchy Theme")
    bg = theme_dict.get("bg", "#070b12")
    bg_alt = theme_dict.get("bg_alt", "#141e33")
    fg = theme_dict.get("fg", "#f8fafc")
    fg_muted = theme_dict.get("fg_muted", "#94a3b8")
    accent = theme_dict.get("accent", "#38bdf8")
    accent_alt = theme_dict.get("accent_alt", "#2563eb")
    gold = theme_dict.get("gold", "#fbbf24")
    peach = theme_dict.get("peach", "#fca5a5" if "sakura" in theme_dict.get("id", "") else "#fb923c")

    return f"""# ==============================================================================
# Garchy OS Kitty Theme: {name}
# ==============================================================================
foreground            {fg}
background            {bg}
selection_foreground  {bg}
selection_background  {accent}

cursor                {accent}
cursor_text_color     {bg}

active_border_color   {accent}
inactive_border_color {bg_alt}
bell_border_color     {accent_alt}
url_color             {accent_alt}

active_tab_foreground   {bg}
active_tab_background   {accent}
inactive_tab_foreground {fg_muted}
inactive_tab_background {bg_alt}
tab_bar_background      {bg}

# ANSI Colors
color0                {bg}
color8                {bg_alt}
color1                #f472b6
color9                {peach}
color2                {"#fbcfe8" if "sakura" in theme_dict.get("id", "") else ("#a6e3a1" if "matcha" in theme_dict.get("id", "") else "#86efac")}
color10               {"#f9a8d4" if "sakura" in theme_dict.get("id", "") else ("#94e2d5" if "matcha" in theme_dict.get("id", "") else "#a5f3fc")}
color3                {gold}
color11               #fed7aa
color4                {accent_alt}
color12               {accent}
color5                #c084fc
color13               #e879f9
color6                {accent}
color14               #fbcfe8
color7                {fg}
color15               #ffffff
"""

def generate_gtk_css(theme_dict):
    bg = theme_dict.get("bg", "#070b12")
    bg_card = theme_dict.get("bg_card", "#0f172a")
    fg = theme_dict.get("fg", "#f8fafc")
    accent = theme_dict.get("accent", "#38bdf8")
    border = theme_dict.get("border_col", accent)

    return f"""/* Garchy OS System-wide Dynamic GTK Palette */
@define-color accent_color {accent};
@define-color accent_bg_color {accent};
@define-color accent_fg_color {bg};
@define-color window_bg_color {bg};
@define-color window_fg_color {fg};
@define-color view_bg_color {bg_card};
@define-color view_fg_color {fg};
@define-color headerbar_bg_color {bg_card};
@define-color headerbar_fg_color {fg};
@define-color card_bg_color {bg_card};
@define-color card_fg_color {fg};
@define-color popover_bg_color {bg};
@define-color popover_fg_color {fg};
@define-color borders {border};
"""

def update_rofi_theme(theme_dict):
    bg = theme_dict.get("bg", "#070b12")
    bg_card = theme_dict.get("bg_card", "#0f172a")
    fg = theme_dict.get("fg", "#f8fafc")
    accent = theme_dict.get("accent", "#38bdf8")
    rounding = theme_dict.get("rounding", 6)

    rofi_rasi = os.path.expanduser("~/.config/rofi/active-theme.rasi")
    content = f"""* {{
    bg-color: {bg}F2;
    bg-card: {bg_card};
    fg-color: {fg};
    accent-color: {accent};
    border-radius: {rounding}px;
}}
"""
    try:
        os.makedirs(os.path.dirname(rofi_rasi), exist_ok=True)
        with open(rofi_rasi, "w") as f:
            f.write(content)
    except Exception:
        pass

def update_cava_config(theme_dict):
    cava_conf_path = os.path.expanduser("~/.config/cava/config")
    bg = theme_dict.get("bg", "#070b12")
    accent = theme_dict.get("accent", "#38bdf8")
    accent_alt = theme_dict.get("accent_alt", "#2563eb")
    grad = [bg, accent_alt, accent, "#f8fafc"]

    content = f"""[general]
mode = normal
framerate = 144
autosens = 1
overshoot = 20
sensitivity = 100
bars = 0
bar_width = 2
bar_spacing = 1
max_height = 100
lower_cutoff_freq = 50
higher_cutoff_freq = 12000
sleep_timer = 3

[input]
method = pipewire
source = auto

[output]
channels = stereo
mono_option = average

[color]
gradient = 1
gradient_count = {len(grad)}
"""
    for i, col in enumerate(grad, 1):
        content += f"gradient_color_{i} = '{col}'\n"

    try:
        os.makedirs(os.path.dirname(cava_conf_path), exist_ok=True)
        with open(cava_conf_path, "w") as f:
            f.write(content)
        subprocess.run(["killall", "-SIGUSR2", "cava"], stderr=subprocess.DEVNULL)
        subprocess.run(["killall", "-SIGUSR1", "cava"], stderr=subprocess.DEVNULL)
    except Exception:
        pass

def apply_theme(theme_dict):
    """Applies a theme dictionary system-wide in real time."""
    # 1. Write active theme state files
    os.makedirs(os.path.dirname(THEME_STATE_FILE), exist_ok=True)
    with open(THEME_STATE_FILE, "w") as f:
        json.dump(theme_dict, f, indent=2)

    os.makedirs(os.path.dirname(CACHE_THEME_FILE), exist_ok=True)
    with open(CACHE_THEME_FILE, "w") as f:
        json.dump(theme_dict, f, indent=2)

    # 2. Update Hyprland window borders and rounding
    update_hyprland_look_lua(theme_dict)

    # 3. Update Kitty terminal
    kitty_theme_path = os.path.expanduser("~/.config/kitty/theme.conf")
    try:
        os.makedirs(os.path.dirname(kitty_theme_path), exist_ok=True)
        with open(kitty_theme_path, "w") as f:
            f.write(generate_kitty_theme_config(theme_dict))
        subprocess.run(["killall", "-SIGUSR1", "kitty"], stderr=subprocess.DEVNULL)
    except Exception:
        pass

    # 4. Update GTK 3 & GTK 4 CSS
    try:
        gtk_css = generate_gtk_css(theme_dict)
        for gtk_dir in ["~/.config/gtk-3.0", "~/.config/gtk-4.0"]:
            full_dir = os.path.expanduser(gtk_dir)
            os.makedirs(full_dir, exist_ok=True)
            with open(os.path.join(full_dir, "gtk.css"), "w") as f:
                f.write(gtk_css)
    except Exception:
        pass

    # 5. Update Rofi
    update_rofi_theme(theme_dict)

    # 6. Update Cava
    update_cava_config(theme_dict)

    # 7. Update Icon Theme
    icon_th = theme_dict.get("icon_theme", "Papirus-Dark")
    if icon_th:
        try:
            subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "icon-theme", icon_th],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["xfconf-query", "-c", "xsettings", "-p", "/Net/IconThemeName", "-s", icon_th],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

def main():
    if len(sys.argv) < 2:
        print(json.dumps(get_all_themes(), indent=2))
        return

    cmd = sys.argv[1]
    if cmd == "list":
        print(json.dumps(get_all_themes()))
    elif cmd == "active":
        print(json.dumps(get_active_theme()))
    elif cmd == "apply":
        target = sys.argv[2] if len(sys.argv) > 2 else ""
        if not target:
            print("Error: Target theme ID, name, or JSON file required.", file=sys.stderr)
            sys.exit(1)

        # Find theme
        themes = get_all_themes()
        matched = None
        for t in themes:
            if t.get("id") == target or t.get("name") == target or os.path.basename(target).replace(".json", "") == t.get("id"):
                matched = t
                break

        if not matched and os.path.exists(target):
            try:
                with open(target, "r") as f:
                    matched = json.load(f)
            except Exception as e:
                print(f"Error reading file {target}: {e}", file=sys.stderr)

        if matched:
            apply_theme(matched)
            print(f"Theme '{matched.get('name')}' applied successfully.")
        else:
            print(f"Error: Theme '{target}' not found.", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
