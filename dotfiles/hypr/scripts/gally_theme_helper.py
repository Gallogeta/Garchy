#!/usr/bin/env python3
"""
Gally OS - Shared Desktop Theme State Controller
Synchronizes active theme colors, borders, corner rounding, and icon sets
across all Gally GUI applications, Hyprland, Waybar, and Kitty.
Provides real-time theme observer for live on-the-fly GUI updates.
"""

import os
import sys
import json
import subprocess

THEME_STATE_FILE = os.path.expanduser("~/.config/gally/active_theme.json")

DEFAULT_THEME = {
    "name": "🌸 Tokyo Night",
    "bg": "#131622",
    "bg_card": "#1a1d2e",
    "bg_input": "#1a1d2e",
    "fg": "#c0caf5",
    "fg_muted": "#787c99",
    "accent": "#7aa2f7",
    "accent_alt": "#bb9af7",
    "border_col": "#7aa2f7",
    "rounding": 12,
    "border_width": 2,
    "icon_theme": "Tela-circle-dark"
}

def get_active_theme():
    """Returns the latest active theme dictionary with safe fallbacks."""
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
    """Returns the last modified timestamp of the theme file."""
    if os.path.exists(THEME_STATE_FILE):
        try:
            return os.path.getmtime(THEME_STATE_FILE)
        except Exception:
            pass
    return 0.0

def save_active_theme(theme_dict):
    """Saves active theme dictionary and updates desktop environment settings."""
    os.makedirs(os.path.dirname(THEME_STATE_FILE), exist_ok=True)
    with open(THEME_STATE_FILE, "w") as f:
        json.dump(theme_dict, f, indent=2)
    
    # Sync GTK icon theme if specified
    icon_th = theme_dict.get("icon_theme", "Tela-circle-dark")
    if icon_th:
        try:
            subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "icon-theme", icon_th],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["xfconf-query", "-c", "xsettings", "-p", "/Net/IconThemeName", "-s", icon_th],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
