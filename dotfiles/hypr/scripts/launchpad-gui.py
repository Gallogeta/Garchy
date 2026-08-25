#!/usr/bin/env python3
"""
Gally OS - Native Modern App Grid & Launchpad (GUI)
Flicker-free static layout, instant cached loading, theme-synced colors & smooth hover.
"""

import os
import sys
import glob
import json
import subprocess
import threading
import tkinter as tk
from tkinter import ttk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.expanduser("~/.config/hypr/scripts"))
import gally_theme_helper

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
    in_desktop_entry = False
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line == '[Desktop Entry]':
                    in_desktop_entry = True
                    continue
                elif line.startswith('[') and line.endswith(']'):
                    in_desktop_entry = False
                    continue
                if in_desktop_entry and '=' in line:
                    key, val = line.split('=', 1)
                    key = key.strip()
                    val = val.strip()
                    if key in ['Name', 'Exec', 'Icon', 'Categories', 'NoDisplay', 'Terminal', 'Type', 'Comment']:
                        if key not in entry:
                            entry[key] = val
    except Exception:
        return None

    if entry.get('Type') != 'Application' or entry.get('NoDisplay') == 'true' or not entry.get('Name') or not entry.get('Exec'):
        return None

    exec_cmd = entry['Exec']
    for placeholder in ['%f', '%F', '%u', '%U', '%d', '%D', '%n', '%N', '%k', '%v', '%m']:
        exec_cmd = exec_cmd.replace(placeholder, '')
    exec_cmd = exec_cmd.strip()
    if not exec_cmd:
        return None

    emoji = "📦"
    cats = entry.get('Categories', '').lower()
    for cat_key, cat_emoji in CATEGORY_ICONS.items():
        if cat_key in cats:
            emoji = cat_emoji
            break

    name_lower = entry['Name'].lower()
    if "terminal" in name_lower or "kitty" in name_lower or "console" in name_lower:
        emoji = "💻"
    elif "browser" in name_lower or "brave" in name_lower or "firefox" in name_lower or "chrome" in name_lower:
        emoji = "🌐"
    elif "steam" in name_lower or "game" in name_lower or "heroic" in name_lower or "lutris" in name_lower:
        emoji = "🎮"
    elif "code" in name_lower or "editor" in name_lower:
        emoji = "⚡"
    elif "files" in name_lower or "thunar" in name_lower:
        emoji = "📁"

    return {
        "name": entry['Name'],
        "exec": exec_cmd,
        "comment": entry.get('Comment', ''),
        "emoji": emoji,
        "search_key": f"{entry['Name']} {entry.get('Comment', '')} {cats}".lower()
    }

def scan_apps_from_disk():
    dirs = [
        os.path.expanduser("~/.local/share/applications"),
        "/usr/local/share/applications",
        "/usr/share/applications"
    ]
    seen_execs = set()
    apps = []

    for d in dirs:
        if not os.path.exists(d):
            continue
        for root, _, files in os.walk(d):
            for file in files:
                if file.endswith('.desktop'):
                    full_path = os.path.join(root, file)
                    app = parse_desktop_file(full_path)
                    if app:
                        exec_base = app['exec'].split()[0]
                        if exec_base not in seen_execs:
                            seen_execs.add(exec_base)
                            apps.append(app)

    apps.sort(key=lambda x: x['name'].lower())
    return apps

def load_apps_cached():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    for app in data:
                        if "search_key" not in app:
                            app["search_key"] = f"{app.get('name', '')} {app.get('comment', '')}".lower()
                    return data
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
        
        # Load active theme dynamically
        self.theme = gally_theme_helper.get_active_theme()
        self.bg_main = self.theme.get("bg", "#070b14")
        self.bg_card = self.theme.get("bg_card", "#0f172a")
        self.bg_input = self.theme.get("bg_input", "#1e293b")
        self.bg_hover = "#1e293b" if self.bg_main != "#1e293b" else "#2a2b3d"
        self.fg_light = self.theme.get("fg", "#f1f5f9")
        self.accent_primary = self.theme.get("accent", "#38bdf8")
        self.accent_secondary = self.theme.get("accent_alt", "#fbbf24")
        self.border_col = self.theme.get("border_col", self.accent_primary)
        
        self.title("Gally OS — Application Launchpad")
        self.geometry("900x640")
        self.configure(bg=self.bg_main)
        self.minsize(760, 520)
        
        self.theme_mtime = gally_theme_helper.get_theme_mtime()

        # Style vertical scrollbar
        self.style = ttk.Style()
        self.apply_scrollbar_style()

        self.all_apps = load_apps_cached()
        self.filtered_apps = list(self.all_apps)
        
        # Header & Search Bar
        self.hdr = tk.Frame(self, bg=self.bg_main, padx=25, pady=14)
        self.hdr.pack(fill="x")
        
        self.top_bar = tk.Frame(self.hdr, bg=self.bg_main)
        self.top_bar.pack(fill="x")
        
        self.lbl_title = tk.Label(self.top_bar, text="🌌 Gally Launchpad", font=("Sans", 16, "bold"),
                                  fg=self.accent_primary, bg=self.bg_main)
        self.lbl_title.pack(side="left")
        
        # Search Box Container
        self.search_card = tk.Frame(self.top_bar, bg=self.bg_input, padx=12, pady=4, relief="flat",
                                    highlightthickness=1, highlightbackground=self.accent_secondary)
        self.search_card.pack(side="right", fill="x", expand=True, padx=(30, 0))
        
        self.lbl_search_ico = tk.Label(self.search_card, text="🔍", font=("Sans", 11),
                                       fg=self.accent_secondary, bg=self.bg_input)
        self.lbl_search_ico.pack(side="left", padx=(0, 6))
        
        self.ent_search = tk.Entry(self.search_card, font=("Sans", 11), bg=self.bg_input, fg="#ffffff",
                                   insertbackground=self.accent_primary, relief="flat", borderwidth=0)
        self.ent_search.pack(side="left", fill="x", expand=True)
        self.ent_search.bind("<KeyRelease>", self.on_search)
        self.ent_search.bind("<Return>", self.on_enter_press)
        self.ent_search.focus_set()
        
        self.sep_line = tk.Frame(self.hdr, height=2, bg=self.accent_primary)
        self.sep_line.pack(fill="x", pady=(10, 0))
        
        # Scrollable Canvas Grid
        self.canvas_frame = tk.Frame(self, bg=self.bg_main)
        self.canvas_frame.pack(fill="both", expand=True, padx=25, pady=(0, 10))
        
        self.canvas = tk.Canvas(self.canvas_frame, bg=self.bg_main, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        
        self.grid_container = tk.Frame(self.canvas, bg=self.bg_main)
        self.grid_container.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.grid_container, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.bind("<Configure>", self.on_resize)
        self.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-2, "units"))
        self.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(2, "units"))
        self.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        self.bind("<Escape>", lambda e: self.destroy())
        
        self.render_grid()
        
        threading.Thread(target=self.refresh_cache_async, daemon=True).start()
        self.check_theme_update()

    def apply_scrollbar_style(self):
        try:
            self.style.theme_use("clam")
            self.style.configure("Vertical.TScrollbar", gripcount=0,
                                background=self.bg_card, darkcolor=self.bg_main, lightcolor=self.bg_main,
                                troughcolor=self.bg_main, bordercolor=self.border_col, arrowcolor=self.accent_secondary)
        except Exception:
            pass

    def check_theme_update(self):
        try:
            cur_mtime = gally_theme_helper.get_theme_mtime()
            if cur_mtime > self.theme_mtime:
                self.theme_mtime = cur_mtime
                self.theme = gally_theme_helper.get_active_theme()
                self.bg_main = self.theme.get("bg", "#070b14")
                self.bg_card = self.theme.get("bg_card", "#0f172a")
                self.bg_input = self.theme.get("bg_input", "#1e293b")
                self.bg_hover = "#1e293b" if self.bg_main != "#1e293b" else "#2a2b3d"
                self.fg_light = self.theme.get("fg", "#f1f5f9")
                self.fg_muted = self.theme.get("fg_muted", "#94a3b8")
                self.accent_primary = self.theme.get("accent", "#38bdf8")
                self.accent_secondary = self.theme.get("accent_alt", "#fbbf24")
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
        self.search_card.configure(bg=self.bg_input, highlightbackground=self.accent_secondary)
        self.lbl_search_ico.configure(fg=self.accent_secondary, bg=self.bg_input)
        self.ent_search.configure(bg=self.bg_input, insertbackground=self.accent_primary)
        self.sep_line.configure(bg=self.accent_primary)
        self.canvas_frame.configure(bg=self.bg_main)
        self.canvas.configure(bg=self.bg_main)
        self.grid_container.configure(bg=self.bg_main)
        self.apply_scrollbar_style()
        self.render_grid()

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
            self.filtered_apps = [a for a in self.all_apps if q in a.get("search_key", "")]
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
            
            card = tk.Frame(self.grid_container, bg=self.bg_card, padx=10, pady=8, relief="flat",
                            highlightthickness=1, highlightbackground=self.border_col, cursor="hand2", width=195, height=72)
            card.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")
            card.pack_propagate(False)
            
            lbl_ico = tk.Label(card, text=app['emoji'], font=("Sans", 20),
                               bg=self.bg_card, fg=self.accent_primary, cursor="hand2")
            lbl_ico.pack(side="left", padx=(4, 8))
            
            info = tk.Frame(card, bg=self.bg_card, cursor="hand2")
            info.pack(side="left", fill="both", expand=True)
            
            lbl_nm = tk.Label(info, text=app['name'], font=("Sans", 10, "bold"),
                              fg=self.fg_light, bg=self.bg_card, anchor="w", justify="left", cursor="hand2")
            lbl_nm.pack(anchor="w")
            
            comment = app.get('comment', '')
            lbl_cm = None
            if comment:
                lbl_cm = tk.Label(info, text=comment[:22] + ("..." if len(comment) > 22 else ""),
                                  font=("Sans", 8), fg=self.fg_muted, bg=self.bg_card, anchor="w", cursor="hand2")
                lbl_cm.pack(anchor="w")

            widgets = [card, lbl_ico, info, lbl_nm]
            if lbl_cm:
                widgets.append(lbl_cm)

            def make_hover_handlers(cd, w_list, bg_normal, bg_hover, bd_normal, bd_hover):
                def on_enter(e):
                    cd.configure(bg=bg_hover, highlightbackground=bd_hover)
                    for w in w_list:
                        try:
                            w.configure(bg=bg_hover)
                        except Exception:
                            pass
                def on_leave(e):
                    cd.configure(bg=bg_normal, highlightbackground=bd_normal)
                    for w in w_list:
                        try:
                            w.configure(bg=bg_normal)
                        except Exception:
                            pass
                return on_enter, on_leave

            enter_fn, leave_fn = make_hover_handlers(card, widgets, self.bg_card, self.bg_hover, self.border_col, self.accent_secondary)

            for w in widgets:
                w.bind("<Enter>", enter_fn)
                w.bind("<Leave>", leave_fn)
                w.bind("<Button-1>", lambda e, ap=app: self.launch_app(ap))

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
