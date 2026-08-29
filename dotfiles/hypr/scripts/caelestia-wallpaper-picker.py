#!/usr/bin/env python3
"""
==============================================================================
🌌 Garchy OS — Caelestia Wallpaper & SDDM Background Chooser
==============================================================================
"""

import os
import sys
import glob
import subprocess
import shutil

HOME = os.path.expanduser("~")
WALLPAPER_DIRS = [
    os.path.join(HOME, "Pictures", "Wallpapers"),
    os.path.join(HOME, "Pictures"),
    "/usr/share/backgrounds",
]

def get_wallpapers():
    valid_exts = (".png", ".jpg", ".jpeg", ".webp")
    walls = []
    for d in WALLPAPER_DIRS:
        if os.path.exists(d):
            for root, _, files in os.walk(d):
                for f in files:
                    if f.lower().endswith(valid_exts):
                        walls.append(os.path.join(root, f))
    return sorted(list(set(walls)))

def apply_desktop(wall_path):
    print(f"Applying desktop wallpaper: {wall_path}")
    # 1. Update cache
    os.makedirs(os.path.join(HOME, ".cache"), exist_ok=True)
    with open(os.path.join(HOME, ".cache", "gally_current_wallpaper"), "w") as f:
        f.write(wall_path)
    
    # 2. Apply via awww
    subprocess.run([
        "awww", "img",
        "--transition-type", "fade",
        "--transition-duration", "0.6",
        "--transition-fps", "144",
        wall_path
    ], check=False)

    # 3. Trigger Wallust dynamic color palette generation
    try:
        subprocess.run(["wallust", "run", wall_path], check=False)
    except Exception:
        pass

    # 4. Trigger blur regeneration
    try:
        from PIL import Image, ImageFilter, ImageEnhance
        cache_dir = "/tmp/garchy_wallpaper_cache"
        os.makedirs(cache_dir, exist_ok=True)
        img = Image.open(wall_path).convert("RGB")
        img.save(os.path.join(cache_dir, "wall_clean.png"), "PNG")
        blurred = img.filter(ImageFilter.GaussianBlur(radius=18))
        enhancer = ImageEnhance.Brightness(blurred)
        dimmed = enhancer.enhance(0.70)
        dimmed.save(os.path.join(cache_dir, "wall_blur.png"), "PNG")
    except Exception as e:
        print(f"Blur cache error: {e}")

    subprocess.run(["notify-send", "-a", "Garchy Wallpaper", "🌌 Wallpaper Applied", os.path.basename(wall_path)], check=False)

def apply_sddm(wall_path):
    print(f"Applying SDDM background: {wall_path}")
    sddm_garchy_bg = "/usr/share/sddm/themes/garchy/background.jpg"
    try:
        # Check write permission or use pkexec
        if os.access(os.path.dirname(sddm_garchy_bg), os.W_OK):
            shutil.copyfile(wall_path, sddm_garchy_bg)
            subprocess.run(["notify-send", "-a", "SDDM Theme", "🔒 SDDM Background Updated", os.path.basename(wall_path)], check=False)
        else:
            cmd = f"pkexec cp '{wall_path}' '{sddm_garchy_bg}'"
            res = subprocess.run(["bash", "-c", cmd])
            if res.returncode == 0:
                subprocess.run(["notify-send", "-a", "SDDM Theme", "🔒 SDDM Background Updated", os.path.basename(wall_path)], check=False)
    except Exception as e:
        subprocess.run(["notify-send", "-u", "critical", "SDDM Error", str(e)], check=False)

def main():
    wallpapers = get_wallpapers()
    if not wallpapers:
        subprocess.run(["notify-send", "No Wallpapers Found", "Place wallpapers in ~/Pictures/Wallpapers"], check=False)
        return

    # Build rofi menu with thumbnail formatting
    entries = []
    for w in wallpapers:
        name = os.path.basename(w)
        entries.append(f"{name}\0icon\x1f{w}\x1finfo\x1f{w}")

    rofi_input = "\n".join(entries)
    rofi_cmd = [
        "rofi", "-dmenu",
        "-p", "🌌 Choose Caelestia Wallpaper",
        "-theme-str", "window { width: 700px; } listview { lines: 8; }"
    ]

    try:
        proc = subprocess.Popen(rofi_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out, _ = proc.communicate(input="\n".join([os.path.basename(w) for w in wallpapers]))
        selected_name = out.strip()
        if not selected_name:
            return

        selected_path = None
        for w in wallpapers:
            if os.path.basename(w) == selected_name:
                selected_path = w
                break

        if not selected_path:
            return

        # Target Chooser (Desktop / SDDM / Both)
        action_menu = "1. 🖼️ Apply to Desktop Wallpaper\n2. 🔒 Apply to SDDM Login Screen\n3. ✨ Apply to BOTH (Desktop + SDDM)"
        action_proc = subprocess.Popen(["rofi", "-dmenu", "-p", "🎯 Select Target"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        act_out, _ = action_proc.communicate(input=action_menu)
        choice = act_out.strip()

        if "1." in choice or "Desktop" in choice:
            apply_desktop(selected_path)
        elif "2." in choice or "SDDM" in choice:
            apply_sddm(selected_path)
        elif "3." in choice or "BOTH" in choice:
            apply_desktop(selected_path)
            apply_sddm(selected_path)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        apply_desktop(sys.argv[1])
    else:
        main()
