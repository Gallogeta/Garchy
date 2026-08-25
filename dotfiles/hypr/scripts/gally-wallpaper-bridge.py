#!/usr/bin/env python3
"""
🌌 Garchy OS — XFCE / Thunar Wallpaper Bridge
Listens to Thunar's native "Set as wallpaper" xfconf events and applies them seamlessly to Hyprland with awww at 144Hz.
"""

import os
import sys
import subprocess
import time

def start_bridge():
    cmd = ["xfconf-query", "-c", "xfce4-desktop", "-m"]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1)
        for line in iter(proc.stdout.readline, ""):
            line = line.strip()
            # Look for property change with image path
            if "last-image" in line:
                parts = line.split("value: ")
                if len(parts) > 1:
                    img_path = parts[1].strip()
                    if os.path.exists(img_path):
                        # Apply to awww
                        subprocess.run(["awww", "img", img_path, "--transition-type", "wave", "--transition-fps", "144"], stderr=subprocess.DEVNULL)
                        filename = os.path.basename(img_path)
                        subprocess.run(["notify-send", "-a", "Wallpaper", "🖼️ Wallpaper Applied", filename], stderr=subprocess.DEVNULL)
    except Exception as e:
        pass

if __name__ == "__main__":
    start_bridge()
