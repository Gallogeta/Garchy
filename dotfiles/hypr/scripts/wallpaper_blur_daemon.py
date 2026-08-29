#!/usr/bin/env python3
"""
==============================================================================
🌌 Garchy OS — Wallpaper Canvas Dynamic Blur & Dim Engine (Caelestia Edition)
==============================================================================
Monitors active Hyprland workspaces and window states.
When windows are open: smoothly transitions to blurred/dimmed wallpaper.
When workspace is empty (Desktop Mode): smoothly transitions to clean wallpaper.
"""

import os
import sys
import time
import socket
import json
import subprocess
from PIL import Image, ImageFilter, ImageEnhance

HOME = os.path.expanduser("~")
CACHE_DIR = "/tmp/garchy_wallpaper_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

CLEAN_WALL_PATH = os.path.join(CACHE_DIR, "wall_clean.jpg")
BLUR_WALL_PATH = os.path.join(CACHE_DIR, "wall_blur.jpg")
CURRENT_STATE_FILE = os.path.join(CACHE_DIR, "current_state.txt")
WALL_TRACK_FILE = os.path.join(HOME, ".cache", "gally_current_wallpaper")

def get_current_wallpaper():
    if os.path.exists(WALL_TRACK_FILE):
        try:
            with open(WALL_TRACK_FILE, "r") as f:
                p = f.read().strip()
                if os.path.exists(p):
                    return p
        except Exception:
            pass
    
    # Fallback search in standard wallpaper folders
    defaults = [
        os.path.join(HOME, "Pictures", "Wallpapers"),
        "/usr/share/backgrounds",
    ]
    for d in defaults:
        if os.path.exists(d):
            for f in os.listdir(d):
                if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                    return os.path.join(d, f)
    return ""

def generate_blurred_wallpaper(src_path):
    if not os.path.exists(src_path):
        return False
    try:
        img = Image.open(src_path).convert("RGB")
        img.save(CLEAN_WALL_PATH, "JPEG", quality=95)
        
        # High-Speed Caelestia Box/Gaussian Blur + Obsidian Dim (<60ms)
        small = img.resize((img.width // 3, img.height // 3), Image.Resampling.BILINEAR)
        blurred = small.filter(ImageFilter.GaussianBlur(radius=6))
        full_blur = blurred.resize((img.width, img.height), Image.Resampling.BILINEAR)
        
        enhancer = ImageEnhance.Brightness(full_blur)
        dimmed = enhancer.enhance(0.68)
        dimmed.save(BLUR_WALL_PATH, "JPEG", quality=90)
        return True
    except Exception as e:
        print(f"[BlurEngine] Error generating blurred wallpaper: {e}", file=sys.stderr)
        return False

def set_wallpaper_mode(mode):
    # mode: 'clean' or 'blur'
    last_mode = ""
    if os.path.exists(CURRENT_STATE_FILE):
        try:
            with open(CURRENT_STATE_FILE, "r") as f:
                last_mode = f.read().strip()
        except Exception:
            pass
    
    if last_mode == mode:
        return

    target = BLUR_WALL_PATH if mode == "blur" else CLEAN_WALL_PATH
    if not os.path.exists(target):
        return

    try:
        subprocess.run([
            "awww", "img",
            "--transition-type", "fade",
            "--transition-duration", "0.4",
            "--transition-fps", "144",
            target
        ], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        with open(CURRENT_STATE_FILE, "w") as f:
            f.write(mode)
    except Exception as e:
        print(f"[BlurEngine] Transition error: {e}", file=sys.stderr)

def check_active_windows():
    try:
        out = subprocess.check_output(["hyprctl", "activeworkspace", "-j"], text=True)
        data = json.loads(out)
        windows = data.get("windows", 0)
        return windows > 0
    except Exception:
        return False

def listen_hyprland_events():
    his = os.getenv("HYPRLAND_INSTANCE_SIGNATURE")
    if not his:
        return

    sock_path = f"/tmp/hypr/{his}/.socket2.sock"
    if not os.path.exists(sock_path):
        # Alternative runtime dir path
        xdg_runtime = os.getenv("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
        sock_path = f"{xdg_runtime}/hypr/{his}/.socket2.sock"

    if not os.path.exists(sock_path):
        print(f"[BlurEngine] Hyprland socket not found at {sock_path}", file=sys.stderr)
        return

    wall = get_current_wallpaper()
    if wall:
        generate_blurred_wallpaper(wall)

    # Initial state
    has_win = check_active_windows()
    set_wallpaper_mode("blur" if has_win else "clean")

    last_wall_check = time.time()
    current_wall = wall

    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(sock_path)

    buf = ""
    while True:
        data = client.recv(4096).decode("utf-8", errors="ignore")
        if not data:
            break
        buf += data
        while "\n" in buf:
            line, buf = buf.split("\n", 1)
            line = line.strip()
            if not line:
                continue
            
            # Events that trigger window state change
            if any(line.startswith(ev) for ev in [
                "workspace>>", "focusedmon>>", "openwindow>>", "closewindow>>",
                "movewindow>>", "changefloatingmode>>", "fullscreen>>"
            ]):
                time.sleep(0.08) # Small debounce for window tiling settle
                has_win = check_active_windows()
                set_wallpaper_mode("blur" if has_win else "clean")
            
            # Check if wallpaper file was changed
            if time.time() - last_wall_check > 5.0:
                last_wall_check = time.time()
                new_wall = get_current_wallpaper()
                if new_wall and new_wall != current_wall:
                    current_wall = new_wall
                    generate_blurred_wallpaper(new_wall)
                    set_wallpaper_mode("blur" if check_active_windows() else "clean")

if __name__ == "__main__":
    try:
        listen_hyprland_events()
    except KeyboardInterrupt:
        pass
