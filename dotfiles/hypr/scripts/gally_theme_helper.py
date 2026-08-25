#!/usr/bin/env python3
"""
Gally OS - Shared Desktop Theme State Controller
Synchronizes active theme colors, borders, corner rounding, icon sets,
and full 16-color ANSI terminal palettes across Gally GUI apps, Hyprland, Waybar, and Kitty.
"""

import os
import sys
import json
import subprocess

THEME_STATE_FILE = os.path.expanduser("~/.config/gally/active_theme.json")

DEFAULT_THEME = {
    "name": "🌌 Garchy Theme",
    "bg": "#0a0f1d",
    "bg_card": "#131c31",
    "bg_input": "#1e293b",
    "bg_alt": "#131c31",
    "fg": "#f1f5f9",
    "fg_muted": "#94a3b8",
    "accent": "#38bdf8",
    "accent_alt": "#fbbf24",
    "border_col": "#38bdf8",
    "rounding": 14,
    "border_width": 2,
    "icon_theme": "Tela-circle-dark"
}

THEME_PALETTES = {
    "🌌 Garchy Theme": {
        "c0": "#131c31", "c8": "#334155",
        "c1": "#f43f5e", "c9": "#fb7185",
        "c2": "#10b981", "c10": "#34d399",
        "c3": "#fbbf24", "c11": "#fde047",
        "c4": "#3b82f6", "c12": "#60a5fa",
        "c5": "#a855f7", "c13": "#c084fc",
        "c6": "#38bdf8", "c14": "#7dd3fc",
        "c7": "#e2e8f0", "c15": "#ffffff"
    },
    "🌸 Tokyo Night": {
        "c0": "#15161e", "c8": "#414868",
        "c1": "#f7768e", "c9": "#f7768e",
        "c2": "#9ece6a", "c10": "#9ece6a",
        "c3": "#e0af68", "c11": "#e0af68",
        "c4": "#7aa2f7", "c12": "#7aa2f7",
        "c5": "#bb9af7", "c13": "#bb9af7",
        "c6": "#7dcfff", "c14": "#7dcfff",
        "c7": "#a9b1d6", "c15": "#c0caf5"
    },
    "☕ Catppuccin Mocha": {
        "c0": "#45475a", "c8": "#585b70",
        "c1": "#f38ba8", "c9": "#f38ba8",
        "c2": "#a6e3a1", "c10": "#a6e3a1",
        "c3": "#f9e2af", "c11": "#f9e2af",
        "c4": "#89b4fa", "c12": "#89b4fa",
        "c5": "#f5c2e7", "c13": "#f5c2e7",
        "c6": "#94e2d5", "c14": "#94e2d5",
        "c7": "#bac2de", "c15": "#a6adc8"
    },
    "❄️ Nord Arctic": {
        "c0": "#3b4252", "c8": "#4c566a",
        "c1": "#bf616a", "c9": "#bf616a",
        "c2": "#a3be8c", "c10": "#a3be8c",
        "c3": "#ebcb8b", "c11": "#ebcb8b",
        "c4": "#81a1c1", "c12": "#81a1c1",
        "c5": "#b48ead", "c13": "#b48ead",
        "c6": "#88c0d0", "c14": "#8fbcbb",
        "c7": "#e5e9f0", "c15": "#eceff4"
    },
    "⚡ Cyberpunk 2077": {
        "c0": "#14141e", "c8": "#28283c",
        "c1": "#ff003c", "c9": "#ff0055",
        "c2": "#00ff66", "c10": "#33ff88",
        "c3": "#fcee0a", "c11": "#ffff33",
        "c4": "#00f0ff", "c12": "#33f3ff",
        "c5": "#ff00a0", "c13": "#ff33b3",
        "c6": "#00f0ff", "c14": "#70f7ff",
        "c7": "#eaeaf0", "c15": "#ffffff"
    },
    "🧛 Dracula": {
        "c0": "#21222c", "c8": "#6272a4",
        "c1": "#ff5555", "c9": "#ff6e6e",
        "c2": "#50fa7b", "c10": "#69ff94",
        "c3": "#f1fa8c", "c11": "#ffffa5",
        "c4": "#bd93f9", "c12": "#d6acff",
        "c5": "#ff79c6", "c13": "#ff92df",
        "c6": "#8be9fd", "c14": "#a4ffff",
        "c7": "#f8f8f2", "c15": "#ffffff"
    },
    "🌋 Volcanic Lava": {
        "c0": "#261414", "c8": "#4d2222",
        "c1": "#ff3333", "c9": "#ff5555",
        "c2": "#50fa7b", "c10": "#69ff94",
        "c3": "#ff9900", "c11": "#ffaa22",
        "c4": "#ff5533", "c12": "#ff7755",
        "c5": "#e056fd", "c13": "#f077ff",
        "c6": "#ff9966", "c14": "#ffbb88",
        "c7": "#ffddcc", "c15": "#ffffff"
    },
    "🌲 Emerald Forest": {
        "c0": "#12291e", "c8": "#234d3a",
        "c1": "#ff4757", "c9": "#ff6b81",
        "c2": "#2ed573", "c10": "#7bed9f",
        "c3": "#ffa502", "c11": "#eccc68",
        "c4": "#1e90ff", "c12": "#70a1ff",
        "c5": "#a55eea", "c13": "#d1a8ff",
        "c6": "#2ed573", "c14": "#7bed9f",
        "c7": "#e6ffed", "c15": "#ffffff"
    },
    "🖤 Deep Obsidian": {
        "c0": "#121212", "c8": "#2c2c2c",
        "c1": "#ff5252", "c9": "#ff7b7b",
        "c2": "#69f0ae", "c10": "#b9f6ca",
        "c3": "#ffd740", "c11": "#ffe57f",
        "c4": "#40c4ff", "c12": "#80d8ff",
        "c5": "#e040fb", "c13": "#ea80fc",
        "c6": "#00f0ff", "c14": "#84ffff",
        "c7": "#e0e0e0", "c15": "#ffffff"
    }
}

def generate_kitty_theme_config(theme_dict):
    """Generates the full 16-color ANSI theme configuration for Kitty."""
    name = theme_dict.get("name", "🌌 Garchy Theme")
    p = THEME_PALETTES.get(name, THEME_PALETTES["🌌 Garchy Theme"])
    
    bg = theme_dict.get("bg", "#0a0f1d")
    bg_alt = theme_dict.get("bg_alt", "#131c31")
    fg = theme_dict.get("fg", "#f1f5f9")
    fg_muted = theme_dict.get("fg_muted", "#94a3b8")
    accent = theme_dict.get("accent", "#38bdf8")
    accent_alt = theme_dict.get("accent_alt", "#fbbf24")

    content = f"""# ==============================================================================
# Garchy OS Kitty Theme: {name}
# ==============================================================================

# Core Colors
foreground            {fg}
background            {bg}
selection_foreground  {bg}
selection_background  {accent}

# Cursor
cursor                {accent}
cursor_text_color     {bg}

# Window Borders
active_border_color   {accent}
inactive_border_color {bg_alt}
bell_border_color     {accent_alt}

# URL Highlight
url_color             {accent_alt}

# Tab Bar Colors
active_tab_foreground   {bg}
active_tab_background   {accent}
inactive_tab_foreground {fg_muted}
inactive_tab_background {bg_alt}
tab_bar_background      {bg}

# --- Full 16-Color ANSI Spectrum ---
# Black / Dark Grey
color0                {p['c0']}
color8                {p['c8']}

# Red
color1                {p['c1']}
color9                {p['c9']}

# Green
color2                {p['c2']}
color10               {p['c10']}

# Yellow / Gold
color3                {p['c3']}
color11               {p['c11']}

# Blue / Sapphire
color4                {p['c4']}
color12               {p['c12']}

# Magenta / Purple
color5                {p['c5']}
color13               {p['c13']}

# Cyan / Electric Cyan
color6                {p['c6']}
color14               {p['c14']}

# White / Titanium
color7                {p['c7']}
color15               {p['c15']}
"""
    return content

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

CAVA_GRADIENTS = {
    "🌌 Garchy Theme": ["#131c31", "#1e3a8a", "#3b82f6", "#38bdf8", "#7dd3fc", "#fbbf24"],
    "🌸 Tokyo Night": ["#15161e", "#24283b", "#414868", "#7aa2f7", "#bb9af7", "#7dcfff"],
    "☕ Catppuccin Mocha": ["#1e1e2e", "#313244", "#585b70", "#89b4fa", "#cba6f7", "#f5c2e7"],
    "❄️ Nord Arctic": ["#2e3440", "#3b4252", "#4c566a", "#81a1c1", "#88c0d0", "#eceff4"],
    "⚡ Cyberpunk 2077": ["#0a0a0f", "#14141e", "#00f0ff", "#33ff88", "#fcee0a", "#ffff33"],
    "🧛 Dracula": ["#21222c", "#282a36", "#6272a4", "#bd93f9", "#ff79c6", "#8be9fd"],
    "🌋 Volcanic Lava": ["#1a0f0f", "#261414", "#ff3333", "#ff5533", "#ff9900", "#ffaa22"],
    "🌲 Emerald Forest": ["#0b1a13", "#12291e", "#1e90ff", "#2ed573", "#7bed9f", "#e6ffed"],
    "🖤 Deep Obsidian": ["#050505", "#121212", "#2c2c2c", "#40c4ff", "#00f0ff", "#ffffff"]
}

def update_cava_config(theme_dict):
    cava_conf_path = os.path.expanduser("~/.config/cava/config")
    name = theme_dict.get("name", "🌌 Garchy Theme")
    grad = CAVA_GRADIENTS.get(name, CAVA_GRADIENTS["🌌 Garchy Theme"])
    
    content = f"""## ==============================================================================
## 🌌 Garchy OS CAVA Configuration (Compact Frequency Spectrum: Bass ➔ Treble)
## ==============================================================================

[general]
mode = normal
framerate = 144
autosens = 1
overshoot = 10
sensitivity = 110
bars = 20
bar_width = 2
bar_spacing = 1
max_height = 6
lower_cutoff_freq = 30
higher_cutoff_freq = 14000
sleep_timer = 2

[input]
method = pipewire
source = auto

[output]
channels = mono
mono_option = average

[color]
gradient = 1
gradient_count = {len(grad)}

"""
    for i, col in enumerate(grad, 1):
        content += f"gradient_color_{i} = '{col}'\n"
        
    content += """
[smoothing]
integral = 70
monstercat = 1
waves = 0
gravity = 100
noise_reduction = 0.77
"""
    try:
        os.makedirs(os.path.dirname(cava_conf_path), exist_ok=True)
        with open(cava_conf_path, "w") as f:
            f.write(content)
        subprocess.run(["killall", "-SIGUSR2", "cava"], stderr=subprocess.DEVNULL)
        subprocess.run(["killall", "-SIGUSR1", "cava"], stderr=subprocess.DEVNULL)
    except Exception:
        pass

def save_active_theme(theme_dict):
    os.makedirs(os.path.dirname(THEME_STATE_FILE), exist_ok=True)
    with open(THEME_STATE_FILE, "w") as f:
        json.dump(theme_dict, f, indent=2)
    
    # 1. Update Kitty theme.conf
    kitty_theme_path = os.path.expanduser("~/.config/kitty/theme.conf")
    try:
        os.makedirs(os.path.dirname(kitty_theme_path), exist_ok=True)
        with open(kitty_theme_path, "w") as f:
            f.write(generate_kitty_theme_config(theme_dict))
        subprocess.run(["killall", "-SIGUSR1", "kitty"], stderr=subprocess.DEVNULL)
    except Exception:
        pass

    # 2. Update CAVA audio visualizer gradient colors
    update_cava_config(theme_dict)

    # 3. Sync GTK icon theme if specified
    icon_th = theme_dict.get("icon_theme", "Tela-circle-dark")
    if icon_th:
        try:
            subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "icon-theme", icon_th],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["xfconf-query", "-c", "xsettings", "-p", "/Net/IconThemeName", "-s", icon_th],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
