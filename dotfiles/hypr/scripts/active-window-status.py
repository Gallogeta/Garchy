#!/usr/bin/env python3
"""
Gally OS - Active Window Status & Click Dispatcher for Waybar
Outputs active window title with 1-click minimize & close support.
"""

import sys
import json
import subprocess

def get_active_window_info():
    try:
        active = json.loads(subprocess.check_output(['hyprctl', 'activewindow', '-j'], stderr=subprocess.DEVNULL))
        title = active.get('title', '').strip()
        cls = active.get('class', '').strip()
        addr = active.get('address', '').strip()
        
        if not title or not addr:
            return {"text": "", "tooltip": "", "class": "empty"}
            
        icon = "🗖"
        cls_lower = cls.lower()
        if "brave" in cls_lower or "firefox" in cls_lower or "browser" in cls_lower:
            icon = "🌐"
        elif "kitty" in cls_lower or "terminal" in cls_lower:
            icon = ""
        elif "steam" in cls_lower or "game" in cls_lower:
            icon = "🎮"
        elif "code" in cls_lower:
            icon = "💻"
        elif "thunar" in cls_lower or "file" in cls_lower:
            icon = "📁"
            
        short_title = title if len(title) <= 24 else title[:22] + "..."
        display_text = f"{icon} {short_title}"
        tooltip = f"🗔 Active Window: {title}\n───────────────────────\n• Left Click: MINIMIZE this window\n• Right Click: CLOSE this window\n• Middle Click: Maximize / Restore"
        
        return {
            "text": display_text,
            "tooltip": tooltip,
            "class": "active-app"
        }
    except Exception:
        return {"text": "", "tooltip": "", "class": "empty"}

if __name__ == "__main__":
    data = get_active_window_info()
    print(json.dumps(data), flush=True)
