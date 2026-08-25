#!/usr/bin/env python3
"""
Gally OS - Animated Glassmorphic Wallpaper Gallery & Chooser (GUI)
Features:
- Live on-the-fly theme observer (colors, border rounding, accents).
- Configurable auto-rotation timer (Minutes dropdown, Instant Enable/Disable button).
- Multi-directory wallpaper scanning (Add Folder button to include custom wallpaper directories).
- 144Hz smooth in-memory preview caching with adjacent prefetching.
- Auto-sliding filmstrip thumbnail carousel.
- Keyboard navigation (Arrow keys, Enter to apply, Space for random).
"""

import os
import sys
import glob
import json
import random
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageOps

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.expanduser("~/.config/hypr/scripts"))
import gally_theme_helper

CONFIG_FILE = os.path.expanduser("~/.config/gally/wallpaper_config.json")
DEFAULT_WALL_DIR = os.path.expanduser("~/Pictures/Wallpapers")
CURRENT_FILE = "/tmp/hypr_current_wallpaper.txt"

DEFAULT_CONFIG = {
    "timer_enabled": True,
    "interval_minutes": 10,
    "directories": [
        DEFAULT_WALL_DIR
    ]
}

def load_wallpaper_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                res = DEFAULT_CONFIG.copy()
                res.update(data)
                return res
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()

def save_wallpaper_config(cfg):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)

def restart_wallpaper_daemon(cfg):
    """Starts, updates, or stops the background wallpaper rotation daemon."""
    script_path = os.path.expanduser("~/.config/hypr/scripts/wallpaper-timer.sh")
    if not os.path.exists(script_path):
        return
    if cfg.get("timer_enabled", True):
        secs = max(30, int(cfg.get("interval_minutes", 10)) * 60)
        subprocess.Popen(["bash", script_path, "daemon", str(secs)],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        subprocess.run(["bash", script_path, "stop"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def get_all_wallpapers(dirs):
    exts = ("*.jpg", "*.jpeg", "*.png", "*.webp")
    files = []
    for d in dirs:
        exp_d = os.path.expanduser(d)
        if os.path.isdir(exp_d):
            for ext in exts:
                files.extend(glob.glob(os.path.join(exp_d, ext)))
                files.extend(glob.glob(os.path.join(exp_d, "**", ext), recursive=True))
    # Deduplicate and sort
    return sorted(list(set(files)))

class WallpaperGalleryApp(tk.Tk):
    def __init__(self):
        super().__init__(className='gally_wallpaper_gallery')
        
        self.wall_config = load_wallpaper_config()
        self.theme_mtime = gally_theme_helper.get_theme_mtime()
        self.load_theme_values()
        
        self.title("Gally OS — Wallpaper Gallery & Timer Controller")
        self.geometry("980x730")
        self.configure(bg=self.bg_main)
        self.minsize(860, 600)
        
        self.wallpapers = get_all_wallpapers(self.wall_config.get("directories", [DEFAULT_WALL_DIR]))
        self.current_index = 0
        self.thumb_boxes = []
        self.big_preview_img = None
        self.preview_cache = {}
        
        if os.path.exists(CURRENT_FILE):
            try:
                with open(CURRENT_FILE, "r") as f:
                    curr = f.read().strip()
                    if curr in self.wallpapers:
                        self.current_index = self.wallpapers.index(curr)
            except Exception:
                pass

        # 1. Header Bar
        self.hdr = tk.Frame(self, bg=self.bg_main, padx=22, pady=10)
        self.hdr.pack(fill="x")
        
        self.top_bar = tk.Frame(self.hdr, bg=self.bg_main)
        self.top_bar.pack(fill="x")
        
        self.lbl_title = tk.Label(self.top_bar, text="🌌 Gally Wallpaper Gallery", font=("Sans", 16, "bold"),
                                  fg=self.accent_primary, bg=self.bg_main)
        self.lbl_title.pack(side="left")
        
        self.lbl_count = tk.Label(self.top_bar, text=f"🖼️ {len(self.wallpapers)} Wallpapers Ready",
                                  font=("Sans", 10, "bold"), fg=self.accent_secondary, bg=self.bg_card, padx=12, pady=4,
                                  highlightthickness=1, highlightbackground=self.border_col)
        self.lbl_count.pack(side="right")
        
        # 2. Timer & Directory Toolbar
        self.toolbar = tk.Frame(self.hdr, bg=self.bg_card, padx=14, pady=8,
                                highlightthickness=1, highlightbackground=self.border_col)
        self.toolbar.pack(fill="x", pady=(8, 0))
        
        # Timer Toggle Button
        timer_text = "⏱️ Auto-Cycle: ON 🟢" if self.wall_config.get("timer_enabled", True) else "⏱️ Auto-Cycle: OFF ⛔"
        timer_fg = "#22c55e" if self.wall_config.get("timer_enabled", True) else self.fg_muted
        self.btn_timer_toggle = tk.Button(self.toolbar, text=timer_text, font=("Sans", 9, "bold"),
                                          bg=self.bg_input, fg=timer_fg, activebackground=self.accent_secondary, activeforeground="#000",
                                          relief="flat", padx=12, pady=4, cursor="hand2", command=self.toggle_timer)
        self.btn_timer_toggle.pack(side="left", padx=(0, 10))
        
        # Interval Dropdown
        self.lbl_interval = tk.Label(self.toolbar, text="Interval:", font=("Sans", 9, "bold"),
                                     fg=self.fg_light, bg=self.bg_card)
        self.lbl_interval.pack(side="left", padx=(0, 6))
        
        self.interval_var = tk.StringVar(value=f"{self.wall_config.get('interval_minutes', 10)} min")
        self.intervals_map = {
            "1 min": 1,
            "5 min": 5,
            "10 min": 10,
            "15 min": 15,
            "30 min": 30,
            "60 min": 60,
            "120 min": 120
        }
        self.opt_interval = ttk.Combobox(self.toolbar, textvariable=self.interval_var,
                                         values=list(self.intervals_map.keys()), state="readonly", width=8)
        self.opt_interval.pack(side="left", padx=(0, 15))
        self.opt_interval.bind("<<ComboboxSelected>>", self.on_interval_changed)
        
        # Add Directory Button
        self.btn_add_folder = tk.Button(self.toolbar, text="📂 ➕ Add Folder...", font=("Sans", 9, "bold"),
                                        bg=self.bg_input, fg=self.accent_secondary, activebackground=self.accent_secondary, activeforeground="#000",
                                        relief="flat", padx=12, pady=4, cursor="hand2", command=self.add_wallpaper_folder)
        self.btn_add_folder.pack(side="left", padx=(0, 6))
        
        # Reset Folders Button
        self.btn_reset_folders = tk.Button(self.toolbar, text="↺ Default Folder", font=("Sans", 9),
                                           bg=self.bg_input, fg=self.fg_muted, activebackground=self.border_col, activeforeground="#fff",
                                           relief="flat", padx=10, pady=4, cursor="hand2", command=self.reset_wallpaper_folders)
        self.btn_reset_folders.pack(side="left")

        # Subtitle
        self.lbl_sub = tk.Label(self.hdr, text="Browse via Arrow Keys or Filmstrip • Press [ Enter ] to Apply Wallpaper",
                                font=("Sans", 9), fg=self.fg_muted, bg=self.bg_main)
        self.lbl_sub.pack(anchor="w", pady=(6, 0))
        self.sep = tk.Frame(self.hdr, height=2, bg=self.accent_primary)
        self.sep.pack(fill="x", pady=(6, 0))

        # 3. Main Large Preview Canvas
        self.preview_frame = tk.Frame(self, bg=self.bg_card, padx=10, pady=8, relief="flat",
                                      highlightthickness=1, highlightbackground=self.border_col)
        self.preview_frame.pack(fill="both", expand=True, padx=22, pady=(2, 8))
        
        self.nav_row = tk.Frame(self.preview_frame, bg=self.bg_card)
        self.nav_row.pack(fill="x", pady=(0, 4))
        
        self.btn_prev = tk.Button(self.nav_row, text="◀  Prev", font=("Sans", 10, "bold"),
                                  bg=self.bg_input, fg=self.fg_light, activebackground=self.accent_secondary, activeforeground="#000",
                                  relief="flat", padx=14, pady=4, cursor="hand2", command=self.prev_wallpaper)
        self.btn_prev.pack(side="left")
        
        self.lbl_wall_name = tk.Label(self.nav_row, text="", font=("Sans", 11, "bold"), fg=self.accent_primary, bg=self.bg_card)
        self.lbl_wall_name.pack(side="left", padx=15)
        
        self.btn_next = tk.Button(self.nav_row, text="Next  ▶", font=("Sans", 10, "bold"),
                                  bg=self.bg_input, fg=self.fg_light, activebackground=self.accent_secondary, activeforeground="#000",
                                  relief="flat", padx=14, pady=4, cursor="hand2", command=self.next_wallpaper)
        self.btn_next.pack(side="right")
        
        # Big Preview Image Label
        self.lbl_preview_canvas = tk.Label(self.preview_frame, bg="#050811")
        self.lbl_preview_canvas.pack(fill="both", expand=True)

        # 4. Horizontal Auto-Sliding Thumbnail Filmstrip
        self.ribbon_outer = tk.Frame(self, bg=self.bg_main, padx=22, pady=2)
        self.ribbon_outer.pack(fill="x")
        
        self.lbl_filmstrip = tk.Label(self.ribbon_outer, text="Gallery Filmstrip (Auto-scrolls with selection):",
                                      font=("Sans", 9, "bold"), fg=self.fg_muted, bg=self.bg_main)
        self.lbl_filmstrip.pack(anchor="w", pady=(0, 2))
                 
        self.thumb_canvas = tk.Canvas(self.ribbon_outer, bg=self.bg_main, height=88, highlightthickness=0)
        self.thumb_scrollbar = ttk.Scrollbar(self.ribbon_outer, orient="horizontal", command=self.thumb_canvas.xview)
        
        self.thumb_container = tk.Frame(self.thumb_canvas, bg=self.bg_main)
        self.thumb_container.bind("<Configure>", lambda e: self.thumb_canvas.configure(scrollregion=self.thumb_canvas.bbox("all")))
        
        self.thumb_canvas.create_window((0, 0), window=self.thumb_container, anchor="nw")
        self.thumb_canvas.configure(xscrollcommand=self.thumb_scrollbar.set)
        
        self.thumb_canvas.pack(fill="x")
        self.thumb_scrollbar.pack(fill="x", pady=(2, 0))

        # 5. Action Buttons Footer
        self.footer = tk.Frame(self, bg=self.bg_main, padx=22, pady=10)
        self.footer.pack(fill="x", side="bottom")
        
        self.btn_random = tk.Button(self.footer, text="🎲  Random Wallpaper (Space)", font=("Sans", 10, "bold"),
                                    bg=self.bg_input, fg=self.accent_secondary, activebackground=self.accent_secondary, activeforeground="#000",
                                    relief="flat", padx=16, pady=6, cursor="hand2", command=self.apply_random)
        self.btn_random.pack(side="left")
        
        self.btn_close = tk.Button(self.footer, text="Close (Esc)", font=("Sans", 10),
                                   bg=self.bg_input, fg=self.fg_muted, activebackground=self.border_col, activeforeground="#fff",
                                   relief="flat", padx=16, pady=6, cursor="hand2", command=self.destroy)
        self.btn_close.pack(side="left", padx=(10, 0))
        
        self.btn_apply = tk.Button(self.footer, text="✨  Apply This Wallpaper (Enter)", font=("Sans", 11, "bold"),
                                   bg=self.accent_primary, fg="#000", activebackground=self.accent_secondary, activeforeground="#000",
                                   relief="flat", padx=22, pady=6, cursor="hand2", command=self.apply_current)
        self.btn_apply.pack(side="right")

        # Keyboard Bindings
        self.bind("<Left>", lambda e: self.prev_wallpaper())
        self.bind("<Right>", lambda e: self.next_wallpaper())
        self.bind("<Up>", lambda e: self.prev_wallpaper())
        self.bind("<Down>", lambda e: self.next_wallpaper())
        self.bind("<Return>", lambda e: self.apply_current())
        self.bind("<KP_Enter>", lambda e: self.apply_current())
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<space>", lambda e: self.apply_random())
        
        # Mouse Wheel on Strip
        self.thumb_canvas.bind_all("<Button-4>", lambda e: self.thumb_canvas.xview_scroll(-2, "units"))
        self.thumb_canvas.bind_all("<Button-5>", lambda e: self.thumb_canvas.xview_scroll(2, "units"))

        # Render first view and generate thumbnails in background
        self.update_preview()
        threading.Thread(target=self.generate_thumbnails_async, daemon=True).start()
        self.check_theme_update()

    def load_theme_values(self):
        self.theme = gally_theme_helper.get_active_theme()
        self.bg_main = self.theme.get("bg", "#070b14")
        self.bg_card = self.theme.get("bg_card", "#0f172a")
        self.bg_input = self.theme.get("bg_input", "#1e293b")
        self.fg_light = self.theme.get("fg", "#f1f5f9")
        self.fg_muted = self.theme.get("fg_muted", "#94a3b8")
        self.accent_primary = self.theme.get("accent", "#38bdf8")
        self.accent_secondary = self.theme.get("accent_alt", "#fbbf24")
        self.border_col = self.theme.get("border_col", self.accent_primary)
        self.rounding = int(self.theme.get("rounding", 14))

    def toggle_timer(self):
        cur = self.wall_config.get("timer_enabled", True)
        new_state = not cur
        self.wall_config["timer_enabled"] = new_state
        save_wallpaper_config(self.wall_config)
        restart_wallpaper_daemon(self.wall_config)
        
        if new_state:
            self.btn_timer_toggle.configure(text="⏱️ Auto-Cycle: ON 🟢", fg="#22c55e")
        else:
            self.btn_timer_toggle.configure(text="⏱️ Auto-Cycle: OFF ⛔", fg=self.fg_muted)

    def on_interval_changed(self, event=None):
        val_str = self.interval_var.get()
        mins = self.intervals_map.get(val_str, 10)
        self.wall_config["interval_minutes"] = mins
        save_wallpaper_config(self.wall_config)
        restart_wallpaper_daemon(self.wall_config)

    def add_wallpaper_folder(self):
        chosen = filedialog.askdirectory(title="Select Additional Wallpaper Folder")
        if chosen and os.path.isdir(chosen):
            dirs = self.wall_config.get("directories", [DEFAULT_WALL_DIR])
            if chosen not in dirs:
                dirs.append(chosen)
                self.wall_config["directories"] = dirs
                save_wallpaper_config(self.wall_config)
                self.refresh_wallpaper_list()

    def reset_wallpaper_folders(self):
        self.wall_config["directories"] = [DEFAULT_WALL_DIR]
        save_wallpaper_config(self.wall_config)
        self.refresh_wallpaper_list()

    def refresh_wallpaper_list(self):
        self.wallpapers = get_all_wallpapers(self.wall_config.get("directories", [DEFAULT_WALL_DIR]))
        self.lbl_count.configure(text=f"🖼️ {len(self.wallpapers)} Wallpapers Ready ({len(self.wall_config.get('directories', []))} Folders)")
        self.current_index = 0
        self.preview_cache.clear()
        self.update_preview()
        threading.Thread(target=self.generate_thumbnails_async, daemon=True).start()

    def check_theme_update(self):
        try:
            cur_mtime = gally_theme_helper.get_theme_mtime()
            if cur_mtime > self.theme_mtime:
                self.theme_mtime = cur_mtime
                self.load_theme_values()
                self.apply_theme_live()
        except Exception:
            pass
        self.after(300, self.check_theme_update)

    def apply_theme_live(self):
        self.configure(bg=self.bg_main)
        self.hdr.configure(bg=self.bg_main)
        self.top_bar.configure(bg=self.bg_main)
        self.lbl_title.configure(fg=self.accent_primary, bg=self.bg_main)
        self.lbl_count.configure(fg=self.accent_secondary, bg=self.bg_card, highlightbackground=self.border_col)
        self.toolbar.configure(bg=self.bg_card, highlightbackground=self.border_col)
        self.lbl_interval.configure(fg=self.fg_light, bg=self.bg_card)
        self.btn_add_folder.configure(bg=self.bg_input, fg=self.accent_secondary, activebackground=self.accent_secondary)
        self.btn_reset_folders.configure(bg=self.bg_input, fg=self.fg_muted, activebackground=self.border_col)
        self.lbl_sub.configure(fg=self.fg_muted, bg=self.bg_main)
        self.sep.configure(bg=self.accent_primary)
        self.preview_frame.configure(bg=self.bg_card, highlightbackground=self.border_col)
        self.nav_row.configure(bg=self.bg_card)
        self.lbl_wall_name.configure(fg=self.accent_primary, bg=self.bg_card)
        self.btn_prev.configure(bg=self.bg_input, fg=self.fg_light, activebackground=self.accent_secondary)
        self.btn_next.configure(bg=self.bg_input, fg=self.fg_light, activebackground=self.accent_secondary)
        self.ribbon_outer.configure(bg=self.bg_main)
        self.lbl_filmstrip.configure(fg=self.fg_muted, bg=self.bg_main)
        self.thumb_canvas.configure(bg=self.bg_main)
        self.thumb_container.configure(bg=self.bg_main)
        self.footer.configure(bg=self.bg_main)
        self.btn_random.configure(bg=self.bg_input, fg=self.accent_secondary, activebackground=self.accent_secondary)
        self.btn_close.configure(bg=self.bg_input, fg=self.fg_muted, activebackground=self.border_col)
        self.btn_apply.configure(bg=self.accent_primary, activebackground=self.accent_secondary)
        self.highlight_and_auto_scroll()

    def load_cached_preview(self, path):
        if path in self.preview_cache:
            return self.preview_cache[path]
        try:
            img = Image.open(path)
            pw, ph = 760, 320
            img.thumbnail((pw, ph), Image.Resampling.BILINEAR)
            tk_img = ImageTk.PhotoImage(img)
            self.preview_cache[path] = tk_img
            return tk_img
        except Exception:
            return None

    def prefetch_adjacent_previews(self):
        if not self.wallpapers:
            return
        total = len(self.wallpapers)
        prev_idx = (self.current_index - 1) % total
        next_idx = (self.current_index + 1) % total
        for idx in [next_idx, prev_idx]:
            p = self.wallpapers[idx]
            if p not in self.preview_cache:
                try:
                    img = Image.open(p)
                    pw, ph = 760, 320
                    img.thumbnail((pw, ph), Image.Resampling.BILINEAR)
                    self.preview_cache[p] = ImageTk.PhotoImage(img)
                except Exception:
                    pass

    def update_preview(self):
        if not self.wallpapers:
            self.lbl_wall_name.configure(text="No wallpapers found in configured directories!")
            return
            
        path = self.wallpapers[self.current_index]
        basename = os.path.basename(path)
        folder = os.path.basename(os.path.dirname(path))
        self.lbl_wall_name.configure(text=f"[{self.current_index + 1}/{len(self.wallpapers)}]  {folder} / {basename}")
        
        tk_img = self.load_cached_preview(path)
        if tk_img:
            self.big_preview_img = tk_img
            self.lbl_preview_canvas.configure(image=self.big_preview_img, text="")
        else:
            self.lbl_preview_canvas.configure(image="", text="Preview Unavailable", fg=self.fg_muted)
            
        self.highlight_and_auto_scroll()
        threading.Thread(target=self.prefetch_adjacent_previews, daemon=True).start()

    def prev_wallpaper(self):
        if not self.wallpapers:
            return
        self.current_index = (self.current_index - 1) % len(self.wallpapers)
        self.update_preview()

    def next_wallpaper(self):
        if not self.wallpapers:
            return
        self.current_index = (self.current_index + 1) % len(self.wallpapers)
        self.update_preview()

    def select_index(self, idx):
        if 0 <= idx < len(self.wallpapers):
            self.current_index = idx
            self.update_preview()

    def highlight_and_auto_scroll(self):
        for idx, box in enumerate(self.thumb_boxes):
            if idx == self.current_index:
                box.configure(highlightbackground=self.accent_primary, highlightthickness=3, bg=self.accent_primary)
            else:
                box.configure(highlightbackground=self.border_col, highlightthickness=1, bg=self.bg_card)
                
        # Auto-scroll thumbnail strip smoothly to keep selected item in center
        if self.wallpapers and len(self.thumb_boxes) == len(self.wallpapers):
            fraction = self.current_index / float(len(self.wallpapers))
            # Shift slightly to center
            adj_fraction = max(0.0, min(1.0, fraction - 0.08))
            self.thumb_canvas.xview_moveto(adj_fraction)

    def generate_thumbnails_async(self):
        for widget in self.thumb_container.winfo_children():
            widget.destroy()
        self.thumb_boxes = []

        cache_dir = os.path.expanduser("~/.cache/gally_wall_thumbs")
        os.makedirs(cache_dir, exist_ok=True)
        
        for idx, path in enumerate(self.wallpapers):
            box = tk.Frame(self.thumb_container, bg=self.bg_card, width=104, height=72,
                           highlightthickness=1, highlightbackground=self.border_col, cursor="hand2")
            box.pack(side="left", padx=4, pady=2)
            box.pack_propagate(False)
            
            lbl = tk.Label(box, bg="#000000", text="...", fg=self.fg_muted, cursor="hand2")
            lbl.pack(fill="both", expand=True)
            
            box.bind("<Button-1>", lambda e, i=idx: self.select_index(i))
            lbl.bind("<Button-1>", lambda e, i=idx: self.select_index(i))
            
            self.thumb_boxes.append(box)
            
            # Generate or load cached thumbnail
            try:
                fname = f"thumb_{abs(hash(path))}.png"
                cached_thumb_path = os.path.join(cache_dir, fname)
                
                if os.path.exists(cached_thumb_path):
                    thumb_img = Image.open(cached_thumb_path)
                else:
                    img = Image.open(path)
                    thumb_img = ImageOps.fit(img, (96, 64), Image.Resampling.BILINEAR)
                    thumb_img.save(cached_thumb_path, "PNG")
                    
                tk_thumb = ImageTk.PhotoImage(thumb_img)
                lbl.configure(image=tk_thumb, text="")
                lbl.image = tk_thumb  # Prevent garbage collection
            except Exception:
                lbl.configure(text="Err", fg="#ef4444")
                
        self.highlight_and_auto_scroll()

    def apply_current(self):
        if not self.wallpapers:
            return
        chosen = self.wallpapers[self.current_index]
        self.lbl_wall_name.configure(text=f"✨ Applying: {os.path.basename(chosen)}...")
        
        def run_apply():
            subprocess.run(["awww", "img", chosen, "--transition-type", "wipe", "--transition-step", "90", "--transition-fps", "144"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            with open(CURRENT_FILE, "w") as f:
                f.write(chosen)
            self.after(50, lambda: self.destroy())

        threading.Thread(target=run_apply, daemon=True).start()

    def apply_random(self):
        if not self.wallpapers:
            return
        self.current_index = random.randint(0, len(self.wallpapers) - 1)
        self.update_preview()
        self.apply_current()

if __name__ == "__main__":
    app = WallpaperGalleryApp()
    app.mainloop()
