#!/usr/bin/env python3
"""
==============================================================================
🌌 Garchy OS — Wallpaper Indexer & Directory Management Engine
==============================================================================
"""

import os
import sys
import json
import subprocess
import shutil
from PIL import Image, ImageFilter, ImageEnhance

HOME = os.path.expanduser("~")
OUTPUT_JSON = "/tmp/garchy_wallpapers.json"
CACHE_DIR = "/tmp/garchy_wallpaper_cache"
DIRS_CONFIG_PATH = os.path.join(HOME, ".config", "gally", "wallpaper_directories.json")
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DIRS_CONFIG_PATH), exist_ok=True)

DEFAULT_DIRS = [
    os.path.join(HOME, "Pictures", "Wallpapers"),
    os.path.join(HOME, "Pictures"),
    "/usr/share/backgrounds",
]

def get_monitored_dirs():
    if os.path.exists(DIRS_CONFIG_PATH):
        try:
            with open(DIRS_CONFIG_PATH, "r") as f:
                dirs = json.load(f)
                if isinstance(dirs, list) and len(dirs) > 0:
                    return [os.path.expanduser(d) for d in dirs]
        except Exception:
            pass
    # Initialize defaults if file does not exist
    save_monitored_dirs(DEFAULT_DIRS)
    return DEFAULT_DIRS

def save_monitored_dirs(dirs):
    clean = []
    seen = set()
    for d in dirs:
        expanded = os.path.abspath(os.path.expanduser(d.strip()))
        if expanded and expanded not in seen:
            seen.add(expanded)
            clean.append(expanded)
    with open(DIRS_CONFIG_PATH, "w") as f:
        json.dump(clean, f, indent=2)
    return clean

def add_directory(new_dir):
    new_dir = os.path.abspath(os.path.expanduser(new_dir.strip()))
    if not os.path.isdir(new_dir):
        print(f"Directory {new_dir} does not exist", file=sys.stderr)
        return
    dirs = get_monitored_dirs()
    if new_dir not in dirs:
        dirs.append(new_dir)
        save_monitored_dirs(dirs)
        subprocess.run(["notify-send", "-a", "Garchy Wallpaper", "📁 Directory Added", new_dir], check=False)
    scan_wallpapers()

def remove_directory(target_dir):
    target_dir = os.path.abspath(os.path.expanduser(target_dir.strip()))
    dirs = get_monitored_dirs()
    dirs = [d for d in dirs if os.path.abspath(d) != target_dir]
    save_monitored_dirs(dirs)
    subprocess.run(["notify-send", "-a", "Garchy Wallpaper", "📁 Directory Removed", target_dir], check=False)
    scan_wallpapers()

def pick_and_add_dir():
    try:
        cmd = ["zenity", "--file-selection", "--directory", "--title=Select Wallpaper Directory"]
        res = subprocess.check_output(cmd, text=True).strip()
        if res and os.path.isdir(res):
            add_directory(res)
    except Exception:
        pass

def scan_wallpapers():
    valid_exts = (".png", ".jpg", ".jpeg", ".webp")
    wallpapers = []
    seen = set()
    dirs = get_monitored_dirs()

    for d in dirs:
        if not os.path.exists(d):
            continue
        for root, _, files in os.walk(d):
            for f in sorted(files):
                if f.lower().endswith(valid_exts):
                    full_path = os.path.join(root, f)
                    if full_path in seen:
                        continue
                    seen.add(full_path)
                    
                    folder_name = os.path.basename(os.path.normpath(d))
                    if "/usr/share" in full_path:
                        folder_tag = "System"
                    elif "Wallpapers" in full_path:
                        folder_tag = "Wallpapers"
                    elif "Pictures" in full_path:
                        folder_tag = "Pictures"
                    else:
                        folder_tag = folder_name or "Custom"

                    wallpapers.append({
                        "name": f,
                        "path": full_path,
                        "folder": folder_tag,
                        "dir": d,
                        "size_mb": round(os.path.getsize(full_path) / (1024 * 1024), 2),
                    })

    # Read current active wallpaper
    curr = ""
    curr_file = os.path.join(HOME, ".cache", "gally_current_wallpaper")
    if os.path.exists(curr_file):
        try:
            with open(curr_file, "r") as f:
                curr = f.read().strip()
        except Exception:
            pass

    data = {
        "current": curr,
        "total": len(wallpapers),
        "directories": dirs,
        "wallpapers": wallpapers
    }

    with open(OUTPUT_JSON, "w") as f:
        json.dump(data, f)
    return data

def apply_wallpaper(target_type, wall_path):
    if not os.path.exists(wall_path):
        print(f"Error: File {wall_path} does not exist", file=sys.stderr)
        return

    # 1. Update current wallpaper cache
    curr_file = os.path.join(HOME, ".cache", "gally_current_wallpaper")
    with open(curr_file, "w") as f:
        f.write(wall_path)

    if target_type in ("desktop", "both"):
        subprocess.run([
            "awww", "img",
            "--transition-type", "grow",
            "--transition-pos", "center",
            "--transition-duration", "1.0",
            "--transition-fps", "144",
            wall_path
        ], check=False)

        try:
            subprocess.run(["wallust", "run", wall_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        except Exception:
            pass

        try:
            img = Image.open(wall_path).convert("RGB")
            img.save(os.path.join(CACHE_DIR, "wall_clean.jpg"), "JPEG", quality=95)
            small = img.resize((img.width // 3, img.height // 3), Image.Resampling.BILINEAR)
            blurred = small.filter(ImageFilter.GaussianBlur(radius=6))
            full_blur = blurred.resize((img.width, img.height), Image.Resampling.BILINEAR)
            dimmed = ImageEnhance.Brightness(full_blur).enhance(0.68)
            dimmed.save(os.path.join(CACHE_DIR, "wall_blur.jpg"), "JPEG", quality=90)
        except Exception as e:
            print(f"Blur generation error: {e}", file=sys.stderr)

        subprocess.run(["notify-send", "-a", "Garchy Wallpaper", "🌌 Wallpaper Applied", os.path.basename(wall_path)], check=False)

    if target_type in ("sddm", "both"):
        sddm_bg = "/usr/share/sddm/themes/garchy/background.jpg"
        try:
            if os.access(os.path.dirname(sddm_bg), os.W_OK):
                shutil.copyfile(wall_path, sddm_bg)
                subprocess.run(["notify-send", "-a", "SDDM Theme", "🔒 SDDM Login Background Updated", os.path.basename(wall_path)], check=False)
            else:
                subprocess.run(["pkexec", "cp", wall_path, sddm_bg], check=False)
                subprocess.run(["notify-send", "-a", "SDDM Theme", "🔒 SDDM Login Background Updated", os.path.basename(wall_path)], check=False)
        except Exception as e:
            print(f"SDDM update error: {e}", file=sys.stderr)

    scan_wallpapers()

if __name__ == "__main__":
    if len(sys.argv) > 2:
        cmd = sys.argv[1]
        arg = sys.argv[2]
        if cmd == "add-dir":
            add_directory(arg)
        elif cmd == "remove-dir":
            remove_directory(arg)
        elif cmd in ("desktop", "sddm", "both"):
            apply_wallpaper(cmd, arg)
    elif len(sys.argv) > 1 and sys.argv[1] == "pick-add-dir":
        pick_and_add_dir()
    else:
        scan_wallpapers()
