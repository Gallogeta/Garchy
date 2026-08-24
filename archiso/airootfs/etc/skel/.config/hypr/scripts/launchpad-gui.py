#!/usr/bin/env python3
"""
Gally OS - Native Modern App Grid & Launchpad (GUI)
Instant cached loading (<10ms), theme-synced colors & rounding, and mouse hover glow.
"""

import os
import sys
import glob
import json
import subprocess
import threading
import tkinter as tk
from tkinter import ttk

# Import Gally active theme state
try:
    import gally_theme_helper
    THEME = gally_theme_helper.get_active_theme()
except Exception:
    THEME = {
        "bg": "#070b14",
        "bg_card": "#0f172a",
        "bg_input": "#1e293b",
        "fg": "#f1f5f9",
        "fg_muted": "#94a3b8",
        "accent": "#fbbf24",
        "accent_alt": "#38bdf8",
        "border_col": "#334155",
        "rounding": 12
    }

BG_MAIN = THEME.get("bg", "#070b14")
BG_CARD = THEME.get("bg_card", "#0f172a")
BG_INPUT = THEME.get("bg_input", "#1e293b")
FG_LIGHT = THEME.get("fg", "#f1f5f9")
FG_MUTED = THEME.get("fg_muted", "#94a3b8")
ACCENT_PRIMARY = THEME.get("accent", "#fbbf24")
ACCENT_SECONDARY = THEME.get("accent_alt", "#38bdf8")
BORDER_COL = THEME.get("border_col", "#334155")
ROUNDING = THEME.get("rounding", 12)

CACHE_FILE = os.path.expanduser("~/.cache/gally_apps_cache.json")

CATEGORY_ICONS = {
    "game": "🎮",
    "audiovideo": "🎬",
    "audio": "🎵",
    "video": "🎥",
    "development": "💻",
    "graphics": "🎨",
    "network": "🌐",
    "webbrowser": "🌐",
    "office": "📄",
    "system": "⚙️",
    "utility": "🛠️",
    "settings": "🔧"
}

def parse_desktop_file(filepath):
    entry = {}
    is_desktop_entry = False
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if line.startswith('[') and line.endswith(']'):
                    is_desktop_entry = (line == '[Desktop Entry]')
                    continue
                if is_desktop_entry and '=' in line:
                    k, v = line.split('=', 1)
                    k = k.strip()
                    if k not in entry:
                        entry[k] = v.strip()
    except Exception:
        pass
    return entry

def scan_apps_from_disk():
    apps = []
    seen = set()
    dirs = [
        os.path.expanduser("~/.local/share/applications/*.desktop"),
        "/usr/share/applications/*.desktop"
    ]
    for d in dirs:
        for f in sorted(glob.glob(d)):
            e = parse_desktop_file(f)
            if not e or e.get('NoDisplay', '').lower() == 'true':
                continue
            name = e.get('Name', '').strip()
            exec_cmd = e.get('Exec', '').strip()
            if not name or not exec_cmd or name in seen:
                continue
            seen.add(name)
            
            clean_exec = " ".join([arg for arg in exec_cmd.split() if not arg.startswith('%')])
            categories = e.get('Categories', '').lower()
            
            icon_emoji = "📦"
            for cat, emoji in CATEGORY_ICONS.items():
                if cat in categories:
                    icon_emoji = emoji
                    break
                    
            name_lower = name.lower()
            if "terminal" in name_lower or "kitty" in name_lower:
                icon_emoji = ""
            elif "steam" in name_lower or "game" in name_lower:
                icon_emoji = "🎮"
            elif "brave" in name_lower or "firefox" in name_lower or "browser" in name_lower:
                icon_emoji = "🌐"
            elif "code" in name_lower or "codium" in name_lower:
                icon_emoji = "💻"
            elif "file" in name_lower or "thunar" in name_lower:
                icon_emoji = "📁"
            elif "gally" in name_lower or "ai" in name_lower:
                icon_emoji = "🤖"

            apps.append({
                "name": name,
                "exec": clean_exec,
                "emoji": icon_emoji,
                "comment": e.get('Comment', '')
            })
    apps.sort(key=lambda x: x['name'].lower())
    return apps

def load_apps_cached():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    apps = scan_apps_from_disk()
    save_apps_cache(apps)
    return apps

def save_apps_cache(apps):
    try:
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, "w") as f:
            json.dump(apps, f)
    except Exception:
        pass

class LaunchpadApp(tk.Tk):
    def __init__(self):
        super().__init__(className='gally_launchpad')
        self.title("Gally OS — Application Launchpad")
        self.geometry("900x640")
        self.configure(bg=BG_MAIN)
        self.minsize(760, 520)
        
        self.all_apps = load_apps_cached()
        self.filtered_apps = list(self.all_apps)
        
        # Header & Search Bar
        hdr = tk.Frame(self, bg=BG_MAIN, padx=25, pady=16)
        hdr.pack(fill="x")
        
        top_bar = tk.Frame(hdr, bg=BG_MAIN)
        top_bar.pack(fill="x")
        
        tk.Label(top_bar, text="🌌 Gally Launchpad", font=("Sans", 16, "bold"), fg=ACCENT_PRIMARY, bg=BG_MAIN).pack(side="left")
        
        # Search Box Container
        search_card = tk.Frame(top_bar, bg=BG_INPUT, padx=12, pady=4, relief="flat",
                               highlightthickness=1, highlightbackground=ACCENT_SECONDARY)
        search_card.pack(side="right", fill="x", expand=True, padx=(30, 0))
        
        tk.Label(search_card, text="🔍", font=("Sans", 11), fg=ACCENT_SECONDARY, bg=BG_INPUT).pack(side="left", padx=(0, 6))
        
        self.ent_search = tk.Entry(search_card, font=("Sans", 11), bg=BG_INPUT, fg="#ffffff",
                                   insertbackground=ACCENT_PRIMARY, relief="flat", borderwidth=0)
        self.ent_search.pack(side="left", fill="x", expand=True)
        self.ent_search.bind("<KeyRelease>", self.on_search)
        self.ent_search.bind("<Return>", self.on_enter_press)
        self.ent_search.focus_set()
        
        tk.Frame(hdr, height=2, bg=ACCENT_PRIMARY).pack(fill="x", pady=(12, 0))
        
        # Scrollable Canvas Grid
        self.canvas_frame = tk.Frame(self, bg=BG_MAIN)
        self.canvas_frame.pack(fill="both", expand=True, padx=25, pady=(0, 10))
        
        self.canvas = tk.Canvas(self.canvas_frame, bg=BG_MAIN, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        
        self.grid_container = tk.Frame(self.canvas, bg=BG_MAIN)
        self.grid_container.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.grid_container, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.bind("<Configure>", self.on_resize)
        self.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-2, "units"))
        self.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(2, "units"))
        self.bind("<Escape>", lambda e: self.destroy())
        
        self.render_grid()
        
        # Background refresh cache
        threading.Thread(target=self.refresh_cache_async, daemon=True).start()

    def refresh_cache_async(self):
        new_apps = scan_apps_from_disk()
        if len(new_apps) != len(self.all_apps):
            self.all_apps = new_apps
            save_apps_cache(new_apps)
            self.after(0, self.on_search)

    def on_resize(self, event):
        self.canvas.itemconfig(self.canvas_window, width=self.canvas.winfo_width())

    def on_search(self, event=None):
        q = self.ent_search.get().strip().lower()
        if not q:
            self.filtered_apps = list(self.all_apps)
        else:
            self.filtered_apps = [a for a in self.all_apps if q in a['name'].lower() or q in a['comment'].lower()]
        self.render_grid()

    def on_enter_press(self, event=None):
        if self.filtered_apps:
            self.launch_app(self.filtered_apps[0])

    def render_grid(self):
        for w in self.grid_container.winfo_children():
            w.destroy()
            
        columns = 4
        for idx, app in enumerate(self.filtered_apps):
            r = idx // columns
            c = idx % columns
            
            card = tk.Frame(self.grid_container, bg=BG_CARD, padx=10, pady=8, relief="flat",
                            highlightthickness=1, highlightbackground=BORDER_COL, cursor="hand2", width=195, height=72)
            card.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")
            card.grid_propagate(False)
            
            # Hover bindings
            card.bind("<Enter>", lambda e, cd=card: cd.configure(highlightbackground=ACCENT_SECONDARY, bg="#1e293b"))
            card.bind("<Leave>", lambda e, cd=card: cd.configure(highlightbackground=BORDER_COL, bg=BG_CARD))
            card.bind("<Button-1>", lambda e, ap=app: self.launch_app(ap))
            
            # Icon
            lbl_ico = tk.Label(card, text=app['emoji'], font=("Sans", 20), bg=BG_CARD, fg=ACCENT_PRIMARY, cursor="hand2")
            lbl_ico.pack(side="left", padx=(4, 8))
            lbl_ico.bind("<Button-1>", lambda e, ap=app: self.launch_app(ap))
            
            # Text info
            info = tk.Frame(card, bg=BG_CARD, cursor="hand2")
            info.pack(side="left", fill="both", expand=True)
            info.bind("<Button-1>", lambda e, ap=app: self.launch_app(ap))
            
            lbl_nm = tk.Label(info, text=app['name'], font=("Sans", 10, "bold"), fg=FG_LIGHT, bg=BG_CARD,
                              anchor="w", justify="left", cursor="hand2")
            lbl_nm.pack(anchor="w")
            lbl_nm.bind("<Button-1>", lambda e, ap=app: self.launch_app(ap))
            
            comment = app.get('comment', '')
            if comment:
                lbl_cm = tk.Label(info, text=comment[:22] + ("..." if len(comment) > 22 else ""),
                                  font=("Sans", 8), fg=FG_MUTED, bg=BG_CARD, anchor="w", cursor="hand2")
                lbl_cm.pack(anchor="w")
                lbl_cm.bind("<Button-1>", lambda e, ap=app: self.launch_app(ap))

        for i in range(columns):
            self.grid_container.grid_columnconfigure(i, weight=1)

    def launch_app(self, app):
        try:
            subprocess.Popen(app['exec'], shell=True)
        except Exception:
            pass
        self.destroy()

if __name__ == "__main__":
    app = LaunchpadApp()
    app.mainloop()
