#!/usr/bin/env python3
"""
Gally OS - Animated Glassmorphic Wallpaper Gallery & Chooser (GUI)
Theme-aware styling, auto-scrolling filmstrip carousel, in-memory preview caching & Enter-to-Apply.
"""

import os
import sys
import glob
import random
import subprocess
import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageOps

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.expanduser("~/.config/hypr/scripts"))
import gally_theme_helper

WALLPAPERS_DIR = os.path.expanduser("~/Pictures/Wallpapers")
CURRENT_FILE = "/tmp/hypr_current_wallpaper.txt"

def get_wallpaper_list():
    if not os.path.exists(WALLPAPERS_DIR):
        return []
    exts = ("*.jpg", "*.jpeg", "*.png", "*.webp")
    files = []
    for ext in exts:
        files.extend(glob.glob(os.path.join(WALLPAPERS_DIR, ext)))
        files.extend(glob.glob(os.path.join(WALLPAPERS_DIR, "**", ext), recursive=True))
    return sorted(list(set(files)))

class WallpaperGalleryApp(tk.Tk):
    def __init__(self):
        super().__init__(className='gally_wallpaper_gallery')
        
        # Dynamically load active theme
        self.theme = gally_theme_helper.get_active_theme()
        self.bg_main = self.theme.get("bg", "#070b14")
        self.bg_card = self.theme.get("bg_card", "#0f172a")
        self.bg_input = self.theme.get("bg_input", "#1e293b")
        self.fg_light = self.theme.get("fg", "#f1f5f9")
        self.fg_muted = self.theme.get("fg_muted", "#94a3b8")
        self.accent_primary = self.theme.get("accent", "#fbbf24")
        self.accent_secondary = self.theme.get("accent_alt", "#38bdf8")
        self.border_col = self.theme.get("border_col", "#334155")
        
        self.title("Gally OS — Visual Wallpaper Gallery")
        self.geometry("940x680")
        self.configure(bg=self.bg_main)
        self.minsize(800, 560)
        
        self.wallpapers = get_wallpaper_list()
        self.current_index = 0
        self.thumb_boxes = []
        self.big_preview_img = None
        self.preview_cache = {}  # In-memory LRU preview cache for instant switching
        
        # Determine currently active wallpaper if saved
        if os.path.exists(CURRENT_FILE):
            try:
                with open(CURRENT_FILE, "r") as f:
                    curr = f.read().strip()
                    if curr in self.wallpapers:
                        self.current_index = self.wallpapers.index(curr)
            except Exception:
                pass

        self.theme_mtime = gally_theme_helper.get_theme_mtime()

        # 1. Glassmorphic Header
        self.hdr = tk.Frame(self, bg=self.bg_main, padx=25, pady=12)
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
        
        self.lbl_sub = tk.Label(self.hdr, text="Browse via Arrow Keys or Filmstrip • Press [ Enter ] to Apply Wallpaper",
                                font=("Sans", 9), fg=self.fg_muted, bg=self.bg_main)
        self.lbl_sub.pack(anchor="w", pady=(2, 0))
        self.sep = tk.Frame(self.hdr, height=2, bg=self.accent_primary)
        self.sep.pack(fill="x", pady=(8, 0))

        # 2. Main Large Preview Canvas
        self.preview_frame = tk.Frame(self, bg=self.bg_card, padx=10, pady=10, relief="flat",
                                      highlightthickness=1, highlightbackground=self.border_col)
        self.preview_frame.pack(fill="both", expand=True, padx=25, pady=(5, 10))
        
        self.nav_row = tk.Frame(self.preview_frame, bg=self.bg_card)
        self.nav_row.pack(fill="x", pady=(0, 6))
        
        self.btn_prev = tk.Button(self.nav_row, text="◀  Prev", font=("Sans", 10, "bold"),
                                  bg=self.bg_input, fg=self.fg_light, activebackground=self.accent_secondary, activeforeground="#000",
                                  relief="flat", padx=14, pady=5, cursor="hand2", command=self.prev_wallpaper)
        self.btn_prev.pack(side="left")
        
        self.lbl_wall_name = tk.Label(self.nav_row, text="", font=("Sans", 11, "bold"), fg=self.accent_primary, bg=self.bg_card)
        self.lbl_wall_name.pack(side="left", padx=15)
        
        self.btn_next = tk.Button(self.nav_row, text="Next  ▶", font=("Sans", 10, "bold"),
                                  bg=self.bg_input, fg=self.fg_light, activebackground=self.accent_secondary, activeforeground="#000",
                                  relief="flat", padx=14, pady=5, cursor="hand2", command=self.next_wallpaper)
        self.btn_next.pack(side="right")
        
        # Big Preview Image Label
        self.lbl_preview_canvas = tk.Label(self.preview_frame, bg="#050811")
        self.lbl_preview_canvas.pack(fill="both", expand=True)

        # 3. Horizontal Auto-Sliding Thumbnail Filmstrip
        self.ribbon_outer = tk.Frame(self, bg=self.bg_main, padx=25, pady=4)
        self.ribbon_outer.pack(fill="x")
        
        self.lbl_filmstrip = tk.Label(self.ribbon_outer, text="Gallery Filmstrip (Auto-scrolls with selection):",
                                      font=("Sans", 9, "bold"), fg=self.fg_muted, bg=self.bg_main)
        self.lbl_filmstrip.pack(anchor="w", pady=(0, 4))
                 
        self.thumb_canvas = tk.Canvas(self.ribbon_outer, bg=self.bg_main, height=92, highlightthickness=0)
        self.thumb_scrollbar = ttk.Scrollbar(self.ribbon_outer, orient="horizontal", command=self.thumb_canvas.xview)
        
        self.thumb_container = tk.Frame(self.thumb_canvas, bg=self.bg_main)
        self.thumb_container.bind("<Configure>", lambda e: self.thumb_canvas.configure(scrollregion=self.thumb_canvas.bbox("all")))
        
        self.thumb_canvas.create_window((0, 0), window=self.thumb_container, anchor="nw")
        self.thumb_canvas.configure(xscrollcommand=self.thumb_scrollbar.set)
        
        self.thumb_canvas.pack(fill="x")
        self.thumb_scrollbar.pack(fill="x", pady=(3, 0))

        # 4. Action Buttons Footer
        self.footer = tk.Frame(self, bg=self.bg_main, padx=25, pady=12)
        self.footer.pack(fill="x", side="bottom")
        
        self.btn_random = tk.Button(self.footer, text="🎲  Random Wallpaper", font=("Sans", 10, "bold"),
                                    bg=self.bg_input, fg=self.accent_secondary, activebackground=self.accent_secondary, activeforeground="#000",
                                    relief="flat", padx=18, pady=8, cursor="hand2", command=self.apply_random)
        self.btn_random.pack(side="left")
        
        self.btn_close = tk.Button(self.footer, text="Close (Esc)", font=("Sans", 10),
                                   bg=self.bg_input, fg=self.fg_muted, activebackground=self.border_col, activeforeground="#fff",
                                   relief="flat", padx=16, pady=8, cursor="hand2", command=self.destroy)
        self.btn_close.pack(side="left", padx=(10, 0))
        
        self.btn_apply = tk.Button(self.footer, text="✨  Apply This Wallpaper (Enter)", font=("Sans", 11, "bold"),
                                   bg=self.accent_primary, fg="#000", activebackground=self.accent_secondary, activeforeground="#000",
                                   relief="flat", padx=24, pady=8, cursor="hand2", command=self.apply_current)
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

    def check_theme_update(self):
        try:
            cur_mtime = gally_theme_helper.get_theme_mtime()
            if cur_mtime > self.theme_mtime:
                self.theme_mtime = cur_mtime
                self.theme = gally_theme_helper.get_active_theme()
                self.bg_main = self.theme.get("bg", "#070b14")
                self.bg_card = self.theme.get("bg_card", "#0f172a")
                self.bg_input = self.theme.get("bg_input", "#1e293b")
                self.fg_light = self.theme.get("fg", "#f1f5f9")
                self.fg_muted = self.theme.get("fg_muted", "#94a3b8")
                self.accent_primary = self.theme.get("accent", "#fbbf24")
                self.accent_secondary = self.theme.get("accent_alt", "#38bdf8")
                self.border_col = self.theme.get("border_col", self.accent_primary)
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

    def update_preview(self):
        if not self.wallpapers:
            self.lbl_wall_name.config(text="No Wallpapers Found")
            return
            
        path = self.wallpapers[self.current_index]
        filename = os.path.basename(path)
        self.lbl_wall_name.config(text=f"[{self.current_index + 1}/{len(self.wallpapers)}]  {filename}")
        
        tk_img = self.load_cached_preview(path)
        if tk_img:
            self.big_preview_img = tk_img
            self.lbl_preview_canvas.config(image=self.big_preview_img)
            
        # Asynchronously prefetch next & prev
        threading.Thread(target=self.prefetch_adjacent_previews, daemon=True).start()

    def prefetch_adjacent_previews(self):
        total = len(self.wallpapers)
        if total <= 1:
            return
        for offset in [1, -1, 2, -2]:
            idx = (self.current_index + offset) % total
            p = self.wallpapers[idx]
            if p not in self.preview_cache:
                try:
                    img = Image.open(p)
                    img.thumbnail((760, 320), Image.Resampling.BILINEAR)
                    self.preview_cache[p] = ImageTk.PhotoImage(img)
                except Exception:
                    pass

    def next_wallpaper(self):
        if self.wallpapers:
            self.current_index = (self.current_index + 1) % len(self.wallpapers)
            self.update_preview()
            self.highlight_and_auto_scroll()

    def prev_wallpaper(self):
        if self.wallpapers:
            self.current_index = (self.current_index - 1 + len(self.wallpapers)) % len(self.wallpapers)
            self.update_preview()
            self.highlight_and_auto_scroll()

    def select_index(self, idx):
        self.current_index = idx
        self.update_preview()
        self.highlight_and_auto_scroll()

    def apply_current(self):
        if not self.wallpapers:
            return
        target = self.wallpapers[self.current_index]
        self.set_wallpaper_live(target)
        self.destroy()

    def apply_random(self):
        if not self.wallpapers:
            return
        self.current_index = random.randint(0, len(self.wallpapers) - 1)
        self.update_preview()
        self.highlight_and_auto_scroll()
        target = self.wallpapers[self.current_index]
        self.set_wallpaper_live(target)

    def set_wallpaper_live(self, target):
        try:
            if subprocess.run(["pgrep", "-x", "awww-daemon"], stdout=subprocess.DEVNULL).returncode != 0:
                subprocess.Popen(["awww-daemon"])
                
            cmd = ["awww", "img", target, "--transition-type", "outer", "--transition-step", "90", "--transition-fps", "144"]
            subprocess.Popen(cmd)
            
            with open(CURRENT_FILE, "w") as f:
                f.write(target)
                
            filename = os.path.basename(target)
            subprocess.Popen(["notify-send", "-a", "Wallpaper", "✨ Wallpaper Applied", filename, "-i", target])
        except Exception:
            pass

    def generate_thumbnails_async(self):
        for idx, path in enumerate(self.wallpapers):
            try:
                img = Image.open(path)
                thumb = ImageOps.fit(img, (110, 65), Image.Resampling.BILINEAR)
                tk_img = ImageTk.PhotoImage(thumb)
                self.after(0, self.add_thumb_widget, idx, tk_img, path)
            except Exception:
                continue

    def add_thumb_widget(self, idx, tk_img, path):
        box = tk.Frame(self.thumb_container, bg=self.bg_card, padx=2, pady=2, relief="flat",
                       highlightthickness=2, highlightbackground=self.border_col, cursor="hand2")
        box.pack(side="left", padx=4, pady=2)
        
        lbl = tk.Label(box, image=tk_img, bg=self.bg_card, cursor="hand2")
        lbl.image = tk_img
        lbl.pack()
        
        box.bind("<Button-1>", lambda e, i=idx: self.select_index(i))
        lbl.bind("<Button-1>", lambda e, i=idx: self.select_index(i))
        
        setattr(box, "thumb_idx", idx)
        self.thumb_boxes.append(box)
        
        if idx == self.current_index:
            box.configure(highlightbackground=self.accent_primary)
            self.auto_scroll_filmstrip()

    def highlight_and_auto_scroll(self):
        for box in self.thumb_container.winfo_children():
            idx = getattr(box, "thumb_idx", -1)
            if idx == self.current_index:
                box.configure(highlightbackground=self.accent_primary)
            else:
                box.configure(highlightbackground=self.border_col)
        self.auto_scroll_filmstrip()

    def auto_scroll_filmstrip(self):
        total = len(self.wallpapers)
        if total > 0:
            fraction = max(0.0, min(1.0, (self.current_index - 1) / float(total)))
            self.thumb_canvas.xview_moveto(fraction)

if __name__ == "__main__":
    app = WallpaperGalleryApp()
    app.mainloop()
