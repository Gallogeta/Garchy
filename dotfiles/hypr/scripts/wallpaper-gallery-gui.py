#!/usr/bin/env python3
"""
Gally OS - Animated Wallpaper Gallery & Chooser (GUI)
Visual 16:9 thumbnails, large live preview, smooth sliding carousel & 1-click apply.
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

BG_MAIN = "#070b14"
BG_CARD = "#0f172a"
BG_INPUT = "#1e293b"
FG_LIGHT = "#f1f5f9"
FG_MUTED = "#94a3b8"
ACCENT_GOLD = "#fbbf24"
ACCENT_CYAN = "#38bdf8"
BORDER_COL = "#334155"

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
        self.title("Gally OS — Visual Wallpaper Gallery")
        self.geometry("940x680")
        self.configure(bg=BG_MAIN)
        self.minsize(800, 560)
        
        self.wallpapers = get_wallpaper_list()
        self.current_index = 0
        self.thumb_images = {}
        self.big_preview_img = None
        
        # Determine currently active wallpaper if saved
        if os.path.exists(CURRENT_FILE):
            try:
                with open(CURRENT_FILE, "r") as f:
                    curr = f.read().strip()
                    if curr in self.wallpapers:
                        self.current_index = self.wallpapers.index(curr)
            except Exception:
                pass

        # 1. Header
        hdr = tk.Frame(self, bg=BG_MAIN, padx=25, pady=12)
        hdr.pack(fill="x")
        
        top_bar = tk.Frame(hdr, bg=BG_MAIN)
        top_bar.pack(fill="x")
        
        tk.Label(top_bar, text="🌌 Gally Wallpaper Gallery", font=("Sans", 16, "bold"), fg=ACCENT_GOLD, bg=BG_MAIN).pack(side="left")
        
        self.lbl_count = tk.Label(top_bar, text=f"🖼️ {len(self.wallpapers)} Wallpapers Available",
                                  font=("Sans", 10, "bold"), fg=ACCENT_CYAN, bg=BG_CARD, padx=12, pady=4,
                                  highlightthickness=1, highlightbackground=BORDER_COL)
        self.lbl_count.pack(side="right")
        
        tk.Label(hdr, text="Slide, preview, and apply 144Hz dynamic wallpapers with one click",
                 font=("Sans", 9), fg=FG_MUTED, bg=BG_MAIN).pack(anchor="w", pady=(2, 0))
        tk.Frame(hdr, height=2, bg=ACCENT_GOLD).pack(fill="x", pady=(8, 0))

        # 2. Main Large Preview Canvas
        self.preview_frame = tk.Frame(self, bg=BG_CARD, padx=10, pady=10, relief="flat",
                                      highlightthickness=1, highlightbackground=BORDER_COL)
        self.preview_frame.pack(fill="both", expand=True, padx=25, pady=(5, 10))
        
        # Navigation Overlay Controls
        nav_row = tk.Frame(self.preview_frame, bg=BG_CARD)
        nav_row.pack(fill="x", pady=(0, 6))
        
        self.btn_prev = tk.Button(nav_row, text="◀  Previous", font=("Sans", 10, "bold"),
                                  bg=BG_INPUT, fg=FG_LIGHT, activebackground=ACCENT_CYAN, activeforeground="#000",
                                  relief="flat", padx=14, pady=5, cursor="hand2", command=self.prev_wallpaper)
        self.btn_prev.pack(side="left")
        
        self.lbl_wall_name = tk.Label(nav_row, text="", font=("Sans", 11, "bold"), fg=ACCENT_GOLD, bg=BG_CARD)
        self.lbl_wall_name.pack(side="left", padx=15)
        
        self.btn_next = tk.Button(nav_row, text="Next  ▶", font=("Sans", 10, "bold"),
                                  bg=BG_INPUT, fg=FG_LIGHT, activebackground=ACCENT_CYAN, activeforeground="#000",
                                  relief="flat", padx=14, pady=5, cursor="hand2", command=self.next_wallpaper)
        self.btn_next.pack(side="right")
        
        # Big Preview Image Label
        self.lbl_preview_canvas = tk.Label(self.preview_frame, bg="#050811")
        self.lbl_preview_canvas.pack(fill="both", expand=True)

        # 3. Horizontal Sliding Thumbnail Ribbon
        ribbon_outer = tk.Frame(self, bg=BG_MAIN, padx=25, pady=4)
        ribbon_outer.pack(fill="x")
        
        tk.Label(ribbon_outer, text="Gallery Filmstrip (Click any thumbnail or use Arrow Keys):",
                 font=("Sans", 9, "bold"), fg=FG_MUTED, bg=BG_MAIN).pack(anchor="w", pady=(0, 4))
                 
        self.thumb_canvas = tk.Canvas(ribbon_outer, bg=BG_MAIN, height=90, highlightthickness=0)
        self.thumb_scrollbar = ttk.Scrollbar(ribbon_outer, orient="horizontal", command=self.thumb_canvas.xview)
        
        self.thumb_container = tk.Frame(self.thumb_canvas, bg=BG_MAIN)
        self.thumb_container.bind("<Configure>", lambda e: self.thumb_canvas.configure(scrollregion=self.thumb_canvas.bbox("all")))
        
        self.thumb_canvas.create_window((0, 0), window=self.thumb_container, anchor="nw")
        self.thumb_canvas.configure(xscrollcommand=self.thumb_scrollbar.set)
        
        self.thumb_canvas.pack(fill="x")
        self.thumb_scrollbar.pack(fill="x", pady=(3, 0))

        # 4. Action Buttons Footer
        footer = tk.Frame(self, bg=BG_MAIN, padx=25, pady=12)
        footer.pack(fill="x", side="bottom")
        
        btn_random = tk.Button(footer, text="🎲  Random Wallpaper", font=("Sans", 10, "bold"),
                               bg=BG_INPUT, fg=ACCENT_CYAN, activebackground=ACCENT_CYAN, activeforeground="#000",
                               relief="flat", padx=18, pady=8, cursor="hand2", command=self.apply_random)
        btn_random.pack(side="left")
        
        btn_close = tk.Button(footer, text="Close (Esc)", font=("Sans", 10),
                              bg=BG_INPUT, fg=FG_MUTED, activebackground=BORDER_COL, activeforeground="#fff",
                              relief="flat", padx=16, pady=8, cursor="hand2", command=self.destroy)
        btn_close.pack(side="left", padx=(10, 0))
        
        self.btn_apply = tk.Button(footer, text="✨  Apply This Wallpaper", font=("Sans", 11, "bold"),
                                   bg=ACCENT_GOLD, fg="#000", activebackground=ACCENT_CYAN, activeforeground="#000",
                                   relief="flat", padx=24, pady=8, cursor="hand2", command=self.apply_current)
        self.btn_apply.pack(side="right")

        # Keyboard Bindings
        self.bind("<Left>", lambda e: self.prev_wallpaper())
        self.bind("<Right>", lambda e: self.next_wallpaper())
        self.bind("<Return>", lambda e: self.apply_current())
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<space>", lambda e: self.apply_random())
        
        # Mouse Wheel on Strip
        self.thumb_canvas.bind_all("<Button-4>", lambda e: self.thumb_canvas.xview_scroll(-2, "units"))
        self.thumb_canvas.bind_all("<Button-5>", lambda e: self.thumb_canvas.xview_scroll(2, "units"))

        # Render first view and generate thumbnails in background
        self.update_preview()
        threading.Thread(target=self.generate_thumbnails_async, daemon=True).start()

    def update_preview(self):
        if not self.wallpapers:
            self.lbl_wall_name.config(text="No Wallpapers Found")
            return
            
        path = self.wallpapers[self.current_index]
        filename = os.path.basename(path)
        self.lbl_wall_name.config(text=f"[{self.current_index + 1}/{len(self.wallpapers)}]  {filename}")
        
        try:
            img = Image.open(path)
            # Resize image to fit preview frame nicely (preserving aspect ratio)
            pw, ph = 760, 320
            img.thumbnail((pw, ph), Image.Resampling.LANCZOS)
            self.big_preview_img = ImageTk.PhotoImage(img)
            self.lbl_preview_canvas.config(image=self.big_preview_img)
        except Exception:
            pass

    def next_wallpaper(self):
        if self.wallpapers:
            self.current_index = (self.current_index + 1) % len(self.wallpapers)
            self.update_preview()
            self.highlight_thumbnail()

    def prev_wallpaper(self):
        if self.wallpapers:
            self.current_index = (self.current_index - 1 + len(self.wallpapers)) % len(self.wallpapers)
            self.update_preview()
            self.highlight_thumbnail()

    def select_index(self, idx):
        self.current_index = idx
        self.update_preview()
        self.highlight_thumbnail()

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
        self.highlight_thumbnail()
        target = self.wallpapers[self.current_index]
        self.set_wallpaper_live(target)

    def set_wallpaper_live(self, target):
        try:
            if not subprocess.run(["pgrep", "-x", "awww-daemon"], stdout=subprocess.DEVNULL).returncode == 0:
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
                self.thumb_images[idx] = tk_img
                self.after(0, self.add_thumb_widget, idx, tk_img, path)
            except Exception:
                continue

    def add_thumb_widget(self, idx, tk_img, path):
        box = tk.Frame(self.thumb_container, bg=BG_CARD, padx=2, pady=2, relief="flat",
                       highlightthickness=2, highlightbackground=BORDER_COL, cursor="hand2")
        box.pack(side="left", padx=4, pady=2)
        
        lbl = tk.Label(box, image=tk_img, bg=BG_CARD, cursor="hand2")
        lbl.pack()
        
        # Bindings
        box.bind("<Button-1>", lambda e, i=idx: self.select_index(i))
        lbl.bind("<Button-1>", lambda e, i=idx: self.select_index(i))
        
        setattr(box, "thumb_idx", idx)
        if idx == self.current_index:
            box.configure(highlightbackground=ACCENT_GOLD)

    def highlight_thumbnail(self):
        for box in self.thumb_container.winfo_children():
            idx = getattr(box, "thumb_idx", -1)
            if idx == self.current_index:
                box.configure(highlightbackground=ACCENT_GOLD)
            else:
                box.configure(highlightbackground=BORDER_COL)

if __name__ == "__main__":
    app = WallpaperGalleryApp()
    app.mainloop()
