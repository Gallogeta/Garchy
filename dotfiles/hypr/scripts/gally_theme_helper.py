#!/usr/bin/env python3
"""
Gally OS - Shared Desktop Theme State Reader
Reads active theme colors, borders, and corner rounding for all Gally GUI apps.
"""

import os
import json

THEME_STATE_FILE = os.path.expanduser("~/.config/gally/active_theme.json")

DEFAULT_THEME = {
    "name": "🌸 Tokyo Night",
    "bg": "#0a0f1d",
    "bg_card": "#0f172a",
    "bg_input": "#1e293b",
    "fg": "#f1f5f9",
    "fg_muted": "#94a3b8",
    "accent": "#7aa2f7",
    "accent_alt": "#bb9af7",
    "border_col": "#24283b",
    "rounding": 0,
    "border_width": 2
}

def get_active_theme():
    if os.path.exists(THEME_STATE_FILE):
        try:
            with open(THEME_STATE_FILE, "r") as f:
                data = json.load(f)
                return {**DEFAULT_THEME, **data}
        except Exception:
            pass
    return DEFAULT_THEME.copy()

def save_active_theme(theme_dict):
    os.makedirs(os.path.dirname(THEME_STATE_FILE), exist_ok=True)
    with open(THEME_STATE_FILE, "w") as f:
        json.dump(theme_dict, f, indent=2)
