#!/usr/bin/env python3
"""
Garchy OS — Grouped Taskbar Icons Module for Waybar
Renders active and minimized app icons with multi-window count badges and hover tooltips.
Uses hidden background workspace 99 for 100% invisible minimization.
"""

import sys
import json
import subprocess

MINIMIZED_WS = 99

ICON_MAP = {
    "brave-browser": "󰖟",
    "Brave-browser": "󰖟",
    "firefox": "󰈹",
    "falkon": "󰈹",
    "kitty": "󰞷",
    "alacritty": "",
    "thunar": "󰉋",
    "Thunar": "󰉋",
    "code": "󰨞",
    "Code": "󰨞",
    "code-oss": "󰨞",
    "steam": "󰓓",
    "heroic": "󰓓",
    "discord": "󰙯",
    "vesktop": "󰙯",
    "spotify": "󰓇",
    "Spotify": "󰓇",
    "pavucontrol": "󰕾",
    "org.pulseaudio.pavucontrol": "󰕾",
    "haruna": "󰕼",
    "smplayer": "󰕼",
    "mpv": "󰕼",
    "gimp": "󰽉",
    "inkscape": "󰽉"
}

SUPERSCRIPTS = ["⁰", "¹", "²", "³", "⁴", "⁵", "⁶", "⁷", "⁸", "⁹"]

def get_superscript(n):
    if n <= 1:
        return ""
    return "".join(SUPERSCRIPTS[int(d)] for d in str(n))

def get_grouped_icons():
    try:
        clients = json.loads(subprocess.check_output(['hyprctl', 'clients', '-j'], stderr=subprocess.DEVNULL))
        active_win = json.loads(subprocess.check_output(['hyprctl', 'activewindow', '-j'], stderr=subprocess.DEVNULL))
    except Exception:
        return {"text": "", "tooltip": "", "class": "empty"}

    valid_clients = [c for c in clients if not c.get('workspace', {}).get('name', '').startswith('special')]
    if not valid_clients:
        return {"text": "", "tooltip": "No open applications", "class": "empty"}

    active_addr = active_win.get('address', '')

    # Group by application class
    groups = {}
    for c in valid_clients:
        cls = c.get('class', 'App')
        if not cls:
            cls = 'App'
        if cls not in groups:
            groups[cls] = []
        groups[cls].append(c)

    if not groups:
        return {"text": "", "tooltip": "No open applications", "class": "empty"}

    icon_elements = []
    tooltip_lines = ["<b>🗔 Running Applications</b>", "───────────────────────"]

    for cls, wins in groups.items():
        count = len(wins)
        icon_char = ICON_MAP.get(cls, ICON_MAP.get(cls.lower(), "🗔"))
        badge = get_superscript(count)

        is_active = any(w.get('address') == active_addr for w in wins)
        is_all_minimized = all(w.get('workspace', {}).get('id') == MINIMIZED_WS for w in wins)

        if is_active:
            # Highlight active application in electric cyan with underline
            pill = f"<span color='#38bdf8' font_weight='bold'><u>{icon_char}</u>{badge}</span>"
        elif is_all_minimized:
            # Dimmed with gold badge for minimized apps
            pill = f"<span color='#fbbf24'>{icon_char}{badge}</span>"
        else:
            # Normal grey for inactive open apps
            pill = f"<span color='#cbd5e1'>{icon_char}{badge}</span>"

        icon_elements.append(pill)

        # Tooltip details
        for w in wins:
            title = w.get('title', 'Untitled')[:40]
            ws_id = w.get('workspace', {}).get('id', 1)
            ws_name = w.get('workspace', {}).get('name', '1')

            if w.get('address') == active_addr:
                state_str = "<span color='#38bdf8'>[Active]</span>"
            elif ws_id == MINIMIZED_WS:
                state_str = "<span color='#fbbf24'>[🗕 Minimized]</span>"
            else:
                state_str = f"<span color='#94a3b8'>[WS {ws_name}]</span>"

            tooltip_lines.append(f"• <b>{cls}</b>: {title} {state_str}")

    tooltip_lines.append("───────────────────────")
    tooltip_lines.append("• <b>Left Click</b>: Toggle / Select Window")
    tooltip_lines.append("• <b>Right Click</b>: Open Dropdown Menu")

    output_text = "    ".join(icon_elements)
    tooltip_text = "\n".join(tooltip_lines)

    return {
        "text": output_text,
        "tooltip": tooltip_text,
        "class": "grouped-taskbar"
    }

if __name__ == "__main__":
    data = get_grouped_icons()
    print(json.dumps(data), flush=True)
