#!/usr/bin/env python3
"""
Gally OS - Active Window Status & Click Dispatcher for Waybar
Outputs active window title with fallback focus history & 1-click minimize.
"""

import sys
import json
import subprocess

def get_active_window_info():
    try:
        active = {}
        try:
            active = json.loads(subprocess.check_output(['hyprctl', 'activewindow', '-j'], stderr=subprocess.DEVNULL))
        except Exception:
            pass
            
        title = active.get('title', '').strip()
        cls = active.get('class', '').strip()
        addr = active.get('address', '').strip()
        
        # Fallback to focusHistoryID == 0 if activewindow is empty (e.g. during bar click)
        if not title or not addr:
            clients = json.loads(subprocess.check_output(['hyprctl', 'clients', '-j'], stderr=subprocess.DEVNULL))
            normal_clients = [c for c in clients if not c.get('workspace', {}).get('name', '').startswith('special')]
            if normal_clients:
                sorted_c = sorted(normal_clients, key=lambda x: x.get('focusHistoryID', 999))
                top = sorted_c[0]
                title = top.get('title', '').strip()
                cls = top.get('class', '').strip()
                addr = top.get('address', '').strip()
                
        if not title or not addr:
            return {"text": "", "tooltip": "", "class": "empty"}
            
        icon = "🗖"
        cls_lower = cls.lower()
        if "thunar" in cls_lower or "file" in cls_lower:
            icon = "📁"
        elif "brave" in cls_lower or "firefox" in cls_lower or "browser" in cls_lower:
            icon = "🌐"
        elif "kitty" in cls_lower or "terminal" in cls_lower:
            icon = ""
        elif "steam" in cls_lower or "game" in cls_lower:
            icon = "🎮"
        elif "code" in cls_lower:
            icon = "💻"
            
        short_title = title if len(title) <= 20 else title[:18] + "..."
        display_text = f"{icon} {short_title}"
        tooltip = f"🗔 Active: {title}\n───────────────────────\n• Left Click: MINIMIZE window\n• Right Click: CLOSE window\n• Middle Click: Maximize / Restore"
        
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
