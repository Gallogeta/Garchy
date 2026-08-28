#!/usr/bin/env python3
"""
Gally OS - Animated Glassmorphic Wallpaper Gallery & Chooser (CustomTkinter)
Visually rebuilt with native rounded theme borders, auto-cycling timer controls,
custom folder management, and 144Hz responsive preview caching.
"""

import os
import sys
import glob
import json
import random
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk, ImageOps
import customtkinter as ctk

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
    return sorted(list(set(files)))

class WallpaperGalleryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        ctk.set_appearance_mode("dark")
        self.wall_config = load_wallpaper_config()
        self.theme_mtime = gally_theme_helper.get_theme_mtime()
        self.load_theme_values()
        
        self.title("Gally OS — Wallpaper Gallery & Timer Controller")
        self.geometry("980x680")
        self.minsize(860, 580)
        self.configure(fg_color=self.bg_main)
        
        self.wallpapers = get_all_wallpapers(self.wall_config.get("directories", [DEFAULT_WALL_DIR]))
        self.current_index = 0
        self.thumb_boxes = []
        self.thumb_labels = []
        self.preview_cache = {}
        self.big_preview_img = None
        
        if os.path.exists(CURRENT_FILE):
            try:
                with open(CURRENT_FILE, "r") as f:
                    curr = f.read().strip()
                    if curr in self.wallpapers:
                        self.current_index = self.wallpapers.index(curr)
            except Exception:
                pass

        # --- 1. Top Glass Header & Toolbar Card ---
        self.hdr_card = ctk.CTkFrame(self, fg_color=self.bg_card, corner_radius=self.radius,
                                     border_width=1, border_color=self.accent_primary)
        self.hdr_card.pack(fill="x", padx=16, pady=(10, 6))
        
        hdr_top = ctk.CTkFrame(self.hdr_card, fg_color="transparent")
        hdr_top.pack(fill="x", padx=14, pady=(8, 4))
        
        self.lbl_title = ctk.CTkLabel(hdr_top, text="🌌 Gally Wallpaper Gallery",
                                      font=ctk.CTkFont(family="Sans", size=17, weight="bold"),
                                      text_color=self.accent_primary)
        self.lbl_title.pack(side="left")
        
        self.lbl_count = ctk.CTkLabel(hdr_top, text=f"🖼️ {len(self.wallpapers)} Wallpapers Ready",
                                      font=ctk.CTkFont(family="Sans", size=11, weight="bold"),
                                      text_color=self.accent_secondary, fg_color=self.bg_input,
                                      corner_radius=self.radius, padx=12, pady=3)
        self.lbl_count.pack(side="right")
        
        # Integrated Toolbar Row
        self.toolbar_row = ctk.CTkFrame(self.hdr_card, fg_color="transparent")
        self.toolbar_row.pack(fill="x", padx=14, pady=(0, 8))
        
        # Timer Toggle
        timer_on = self.wall_config.get("timer_enabled", True)
        timer_text = "⏱️ Auto-Cycle: ON 🟢" if timer_on else "⏱️ Auto-Cycle: OFF ⛔"
        timer_fg = "#22c55e" if timer_on else self.fg_muted
        self.btn_timer_toggle = ctk.CTkButton(self.toolbar_row, text=timer_text,
                                              font=ctk.CTkFont(family="Sans", size=11, weight="bold"),
                                              fg_color=self.bg_input, hover_color=self.bg_main,
                                              text_color=timer_fg, corner_radius=self.radius,
                                              border_width=1, border_color=self.border_col,
                                              height=28, command=self.toggle_timer)
        self.btn_timer_toggle.pack(side="left", padx=(0, 8))
        
        lbl_int = ctk.CTkLabel(self.toolbar_row, text="Interval:",
                               font=ctk.CTkFont(family="Sans", size=11), text_color=self.fg_muted)
        lbl_int.pack(side="left", padx=(0, 4))
        
        self.intervals_map = {
            "1 min": 1,
            "5 min": 5,
            "10 min": 10,
            "15 min": 15,
            "30 min": 30,
            "60 min": 60,
            "120 min": 120
        }
        curr_mins = self.wall_config.get("interval_minutes", 10)
        curr_choice = f"{curr_mins} min" if f"{curr_mins} min" in self.intervals_map else "10 min"
        
        self.opt_interval = ctk.CTkOptionMenu(self.toolbar_row, values=list(self.intervals_map.keys()),
                                              command=self.on_interval_changed,
                                              fg_color=self.bg_input, button_color=self.accent_primary,
                                              button_hover_color=self.accent_secondary,
                                              text_color=self.fg_light, corner_radius=self.radius,
                                              width=90, height=28)
        self.opt_interval.set(curr_choice)
        self.opt_interval.pack(side="left", padx=(0, 12))
        
        # Add Folder Button
        self.btn_add_folder = ctk.CTkButton(self.toolbar_row, text="📂 ➕ Add Folder...",
                                            font=ctk.CTkFont(family="Sans", size=11, weight="bold"),
                                            fg_color=self.bg_input, hover_color=self.bg_main,
                                            text_color=self.accent_secondary, corner_radius=self.radius,
                                            border_width=1, border_color=self.accent_secondary,
                                            height=28, command=self.add_wallpaper_folder)
        self.btn_add_folder.pack(side="left", padx=(0, 6))
        
        # Reset Folders Button
        self.btn_reset_folders = ctk.CTkButton(self.toolbar_row, text="↺ Reset",
                                               font=ctk.CTkFont(family="Sans", size=11),
                                               fg_color=self.bg_input, hover_color=self.bg_main,
                                               text_color=self.fg_muted, corner_radius=self.radius,
                                               width=65, height=28, command=self.reset_wallpaper_folders)
        self.btn_reset_folders.pack(side="left")

        # --- 2. Main Large Preview Canvas Frame ---
        self.preview_card = ctk.CTkFrame(self, fg_color=self.bg_card, corner_radius=self.radius,
                                         border_width=1, border_color=self.border_col)
        self.preview_card.pack(fill="both", expand=True, padx=16, pady=(0, 6))
        
        # Preview Nav Top Bar
        nav_top = ctk.CTkFrame(self.preview_card, fg_color="transparent")
        nav_top.pack(fill="x", padx=10, pady=(6, 2))
        
        self.btn_prev = ctk.CTkButton(nav_top, text="◀ Prev", width=75, height=26,
                                      font=ctk.CTkFont(family="Sans", size=11, weight="bold"),
                                      fg_color=self.bg_input, hover_color=self.bg_main,
                                      text_color=self.fg_light, corner_radius=self.radius,
                                      command=self.prev_wallpaper)
        self.btn_prev.pack(side="left")
        
        self.lbl_wall_name = ctk.CTkLabel(nav_top, text="",
                                          font=ctk.CTkFont(family="Sans", size=11, weight="bold"),
                                          text_color=self.accent_primary)
        self.lbl_wall_name.pack(side="left", padx=12, fill="x", expand=True)
        
        self.btn_next = ctk.CTkButton(nav_top, text="Next ▶", width=75, height=26,
                                      font=ctk.CTkFont(family="Sans", size=11, weight="bold"),
                                      fg_color=self.bg_input, hover_color=self.bg_main,
                                      text_color=self.fg_light, corner_radius=self.radius,
                                      command=self.next_wallpaper)
        self.btn_next.pack(side="right")
        
        # Big Preview Image Display
        self.lbl_preview_canvas = tk.Label(self.preview_card, bg="#050811", relief="flat", highlightthickness=0)
        self.lbl_preview_canvas.pack(fill="both", expand=True, padx=8, pady=(2, 6))

        # --- 3. Filmstrip Thumbnail Ribbon ---
        self.filmstrip_card = ctk.CTkFrame(self, fg_color=self.bg_card, corner_radius=self.radius,
                                           border_width=1, border_color=self.border_col)
        self.filmstrip_card.pack(fill="x", padx=16, pady=(0, 6))
        
        self.thumb_canvas = tk.Canvas(self.filmstrip_card, bg=self.bg_card, height=72, highlightthickness=0)
        self.thumb_scrollbar = ttk.Scrollbar(self.filmstrip_card, orient="horizontal", command=self.thumb_canvas.xview)
        
        self.thumb_container = tk.Frame(self.thumb_canvas, bg=self.bg_card)
        self.thumb_container.bind("<Configure>", lambda e: self.thumb_canvas.configure(scrollregion=self.thumb_canvas.bbox("all")))
        
        self.thumb_canvas.create_window((0, 0), window=self.thumb_container, anchor="nw")
        self.thumb_canvas.configure(xscrollcommand=self.thumb_scrollbar.set)
        
        self.thumb_canvas.pack(fill="x", padx=6, pady=(4, 2))
        self.thumb_scrollbar.pack(fill="x", padx=6, pady=(0, 4))

        # --- 4. Bottom Action Footer ---
        self.footer = ctk.CTkFrame(self, fg_color="transparent")
        self.footer.pack(fill="x", padx=16, pady=(0, 10))
        
        self.btn_random = ctk.CTkButton(self.footer, text="🎲 Random Wallpaper (Space)",
                                        font=ctk.CTkFont(family="Sans", size=11, weight="bold"),
                                        fg_color=self.bg_input, hover_color=self.bg_card,
                                        text_color=self.accent_secondary, corner_radius=self.radius,
                                        border_width=1, border_color=self.accent_secondary,
                                        height=32, command=self.apply_random)
        self.btn_random.pack(side="left")
        
        self.btn_close = ctk.CTkButton(self.footer, text="Close (Esc)",
                                       font=ctk.CTkFont(family="Sans", size=11),
                                       fg_color=self.bg_input, hover_color=self.bg_card,
                                       text_color=self.fg_muted, corner_radius=self.radius,
                                       width=95, height=32, command=self.destroy)
        self.btn_sddm = ctk.CTkButton(self.footer, text="🌌 Set as Login Screen",
                                      font=ctk.CTkFont(family="Sans", size=11, weight="bold"),
                                      fg_color=self.bg_input, hover_color=self.bg_card,
                                      text_color=self.accent_primary, corner_radius=self.radius,
                                      border_width=1, border_color=self.accent_primary,
                                      height=32, command=self.apply_sddm_current)
        self.btn_sddm.pack(side="left", padx=(8, 0))

        self.btn_apply = ctk.CTkButton(self.footer, text="✨ Apply Desktop (Enter)",
                                       font=ctk.CTkFont(family="Sans", size=12, weight="bold"),
                                       fg_color=self.accent_primary, hover_color=self.accent_secondary,
                                       text_color="#000000", corner_radius=self.radius,
                                       height=32, command=self.apply_current)
        self.btn_apply.pack(side="right")

        # Bindings
        self.bind("<Left>", lambda e: self.prev_wallpaper())
        self.bind("<Right>", lambda e: self.next_wallpaper())
        self.bind("<Up>", lambda e: self.prev_wallpaper())
        self.bind("<Down>", lambda e: self.next_wallpaper())
        self.bind("<Return>", lambda e: self.apply_current())
        self.bind("<KP_Enter>", lambda e: self.apply_current())
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<space>", lambda e: self.apply_random())
        
        self.thumb_canvas.bind_all("<Button-4>", lambda e: self.thumb_canvas.xview_scroll(-2, "units"))
        self.thumb_canvas.bind_all("<Button-5>", lambda e: self.thumb_canvas.xview_scroll(2, "units"))

        # Render initial image and thumbnails
        self.update_preview()
        threading.Thread(target=self.generate_thumbnails_async, daemon=True).start()
        self.check_theme_update()

    def load_theme_values(self):
        self.theme = gally_theme_helper.get_active_theme()
        self.bg_main = self.theme.get("bg", "#0a0f1d")
        self.bg_card = self.theme.get("bg_card", "#131c31")
        self.bg_input = self.theme.get("bg_input", "#1e293b")
        self.fg_light = self.theme.get("fg", "#f1f5f9")
        self.fg_muted = self.theme.get("fg_muted", "#94a3b8")
        self.accent_primary = self.theme.get("accent", "#38bdf8")
        self.accent_secondary = self.theme.get("accent_alt", "#fbbf24")
        self.border_col = self.theme.get("border_col", self.accent_primary)
        self.radius = max(8, int(self.theme.get("rounding", 14)))

    def toggle_timer(self):
        cur = self.wall_config.get("timer_enabled", True)
        new_state = not cur
        self.wall_config["timer_enabled"] = new_state
        save_wallpaper_config(self.wall_config)
        restart_wallpaper_daemon(self.wall_config)
        
        if new_state:
            self.btn_timer_toggle.configure(text="⏱️ Auto-Cycle: ON 🟢", text_color="#22c55e")
        else:
            self.btn_timer_toggle.configure(text="⏱️ Auto-Cycle: OFF ⛔", text_color=self.fg_muted)

    def on_interval_changed(self, val_str):
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
        self.configure(fg_color=self.bg_main)
        self.hdr_card.configure(fg_color=self.bg_card, border_color=self.accent_primary, corner_radius=self.radius)
        self.lbl_title.configure(text_color=self.accent_primary)
        self.lbl_count.configure(text_color=self.accent_secondary, fg_color=self.bg_input, corner_radius=self.radius)
        self.btn_timer_toggle.configure(fg_color=self.bg_input, border_color=self.border_col, corner_radius=self.radius)
        self.opt_interval.configure(fg_color=self.bg_input, button_color=self.accent_primary,
                                     button_hover_color=self.accent_secondary, text_color=self.fg_light, corner_radius=self.radius)
        self.btn_add_folder.configure(fg_color=self.bg_input, text_color=self.accent_secondary,
                                      border_color=self.accent_secondary, corner_radius=self.radius)
        self.btn_reset_folders.configure(fg_color=self.bg_input, text_color=self.fg_muted, corner_radius=self.radius)
        
        self.preview_card.configure(fg_color=self.bg_card, border_color=self.border_col, corner_radius=self.radius)
        self.lbl_wall_name.configure(text_color=self.accent_primary)
        self.btn_prev.configure(fg_color=self.bg_input, text_color=self.fg_light, corner_radius=self.radius)
        self.btn_next.configure(fg_color=self.bg_input, text_color=self.fg_light, corner_radius=self.radius)
        
        self.filmstrip_card.configure(fg_color=self.bg_card, border_color=self.border_col, corner_radius=self.radius)
        self.thumb_canvas.configure(bg=self.bg_card)
        self.thumb_container.configure(bg=self.bg_card)
        
        self.btn_random.configure(fg_color=self.bg_input, text_color=self.accent_secondary,
                                  border_color=self.accent_secondary, corner_radius=self.radius)
        self.btn_close.configure(fg_color=self.bg_input, text_color=self.fg_muted, corner_radius=self.radius)
        self.btn_sddm.configure(fg_color=self.bg_input, text_color=self.accent_primary,
                                border_color=self.accent_primary, corner_radius=self.radius)
        self.btn_apply.configure(fg_color=self.accent_primary, hover_color=self.accent_secondary, corner_radius=self.radius)
        self.highlight_and_auto_scroll()

    def load_cached_preview(self, path):
        if path in self.preview_cache:
            return self.preview_cache[path]
        try:
            img = Image.open(path)
            pw, ph = 740, 310
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
                    pw, ph = 740, 310
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
                box.configure(highlightbackground=self.border_col, highlightthickness=1, bg=self.bg_input)
                
        if self.wallpapers and len(self.thumb_boxes) == len(self.wallpapers):
            fraction = self.current_index / float(len(self.wallpapers))
            adj_fraction = max(0.0, min(1.0, fraction - 0.08))
            self.thumb_canvas.xview_moveto(adj_fraction)

    def generate_thumbnails_async(self):
        for widget in self.thumb_container.winfo_children():
            widget.destroy()
        self.thumb_boxes = []

        cache_dir = os.path.expanduser("~/.cache/gally_wall_thumbs")
        os.makedirs(cache_dir, exist_ok=True)
        
        for idx, path in enumerate(self.wallpapers):
            box = tk.Frame(self.thumb_container, bg=self.bg_input, width=96, height=60,
                           highlightthickness=1, highlightbackground=self.border_col, cursor="hand2")
            box.pack(side="left", padx=3, pady=2)
            box.pack_propagate(False)
            
            lbl = tk.Label(box, bg="#000000", text="...", fg=self.fg_muted, cursor="hand2")
            lbl.pack(fill="both", expand=True)
            
            box.bind("<Button-1>", lambda e, i=idx: self.select_index(i))
            lbl.bind("<Button-1>", lambda e, i=idx: self.select_index(i))
            
            self.thumb_boxes.append(box)
            
            try:
                fname = f"thumb_{abs(hash(path))}.png"
                cached_thumb_path = os.path.join(cache_dir, fname)
                
                if os.path.exists(cached_thumb_path):
                    thumb_img = Image.open(cached_thumb_path)
                else:
                    img = Image.open(path)
                    thumb_img = ImageOps.fit(img, (90, 54), Image.Resampling.BILINEAR)
                    thumb_img.save(cached_thumb_path, "PNG")
                    
                tk_thumb = ImageTk.PhotoImage(thumb_img)
                lbl.configure(image=tk_thumb, text="")
                lbl.image = tk_thumb
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

    def apply_sddm_current(self):
        if not self.wallpapers:
            return
        chosen = self.wallpapers[self.current_index]
        self.lbl_wall_name.configure(text=f"🌌 Setting SDDM Login Wallpaper: {os.path.basename(chosen)}...")
        
        def run_sddm():
            script = os.path.expanduser("~/.config/hypr/scripts/set-sddm-wallpaper.sh")
            subprocess.run(["bash", script, chosen])

        threading.Thread(target=run_sddm, daemon=True).start()

    def apply_random(self):
        if not self.wallpapers:
            return
        self.current_index = random.randint(0, len(self.wallpapers) - 1)
        self.update_preview()
        self.apply_current()

if __name__ == "__main__":
    app = WallpaperGalleryApp()
    app.mainloop()
