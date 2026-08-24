#!/usr/bin/env python3
"""
Gally OS - Modern Visual Theme Switcher GUI
1-Click visual color palette selector with live preview.
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk

BG_MAIN = "#070b14"
BG_CARD = "#0f172a"
FG_LIGHT = "#f1f5f9"
ACCENT_GOLD = "#fbbf24"
ACCENT_CYAN = "#38bdf8"
BORDER_COL = "#334155"

THEMES = [
    {
        "name": "🌸 Tokyo Night",
        "desc": "Elegant dark navy blue with vibrant neon purple & cyan accents",
        "colors": ["#131622", "#7aa2f7", "#bb9af7", "#73daca", "#f7768e"],
        "hypr_border": "rgba(7aa2f7ee) rgba(bb9af7ee) 45deg",
        "hypr_inactive": "rgba(24283b88)",
        "hypr_rounding": 0,
        "waybar_radius": "0px",
        "accent": "#7aa2f7",
        "accent_alt": "#bb9af7",
        "bg": "#131622",
        "bg_alt": "#1a1d2e",
        "fg": "#c0caf5",
        "fg_muted": "#787c99"
    },
    {
        "name": "☕ Catppuccin Mocha",
        "desc": "Warm pastel aesthetics with lavender, mauve & smooth rounded corners",
        "colors": ["#1e1e2e", "#cba6f7", "#f5c2e7", "#a6e3a1", "#f38ba8"],
        "hypr_border": "rgba(cba6f7ee) rgba(f5c2e7ee) 45deg",
        "hypr_inactive": "rgba(1e1e2e88)",
        "hypr_rounding": 12,
        "waybar_radius": "12px",
        "accent": "#cba6f7",
        "accent_alt": "#f5c2e7",
        "bg": "#1e1e2e",
        "bg_alt": "#181825",
        "fg": "#cdd6f4",
        "fg_muted": "#6c7086"
    },
    {
        "name": "❄️ Nord Arctic",
        "desc": "Calm, icy blue tones inspired by Scandinavian winter landscapes",
        "colors": ["#2e3440", "#88c0d0", "#81a1c1", "#a3be8c", "#bf616a"],
        "hypr_border": "rgba(88c0d0ee) rgba(81a1c1ee) 45deg",
        "hypr_inactive": "rgba(2e344088)",
        "hypr_rounding": 8,
        "waybar_radius": "8px",
        "accent": "#88c0d0",
        "accent_alt": "#81a1c1",
        "bg": "#2e3440",
        "bg_alt": "#3b4252",
        "fg": "#eceff4",
        "fg_muted": "#7b88a1"
    },
    {
        "name": "⚡ Cyberpunk 2077",
        "desc": "High-contrast electric yellow, neon cyan and pure obsidian black",
        "colors": ["#0a0a0f", "#fcee0a", "#00f0ff", "#00ff66", "#ff003c"],
        "hypr_border": "rgba(fcee0aee) rgba(00f0ffee) 45deg",
        "hypr_inactive": "rgba(05050888)",
        "hypr_rounding": 0,
        "waybar_radius": "0px",
        "accent": "#fcee0a",
        "accent_alt": "#00f0ff",
        "bg": "#0a0a0f",
        "bg_alt": "#14141e",
        "fg": "#fcee0a",
        "fg_muted": "#71717a"
    },
    {
        "name": "🧛 Dracula",
        "desc": "Classic dark gothic purple, pink highlights and crisp contrast",
        "colors": ["#282a36", "#bd93f9", "#ff79c6", "#50fa7b", "#ff5555"],
        "hypr_border": "rgba(bd93f9ee) rgba(ff79c6ee) 45deg",
        "hypr_inactive": "rgba(282a3688)",
        "hypr_rounding": 10,
        "waybar_radius": "10px",
        "accent": "#bd93f9",
        "accent_alt": "#ff79c6",
        "bg": "#282a36",
        "bg_alt": "#1e1f29",
        "fg": "#f8f8f2",
        "fg_muted": "#6272a4"
    },
    {
        "name": "🌋 Volcanic Lava",
        "desc": "Deep magma crimson, fiery amber orange and warm charcoal",
        "colors": ["#1a0f0f", "#ff5533", "#ff9900", "#50fa7b", "#ff3333"],
        "hypr_border": "rgba(ff5533ee) rgba(ff9900ee) 45deg",
        "hypr_inactive": "rgba(1a0f0f88)",
        "hypr_rounding": 10,
        "waybar_radius": "10px",
        "accent": "#ff5533",
        "accent_alt": "#ff9900",
        "bg": "#1a0f0f",
        "bg_alt": "#261414",
        "fg": "#ffddcc",
        "fg_muted": "#885544"
    },
    {
        "name": "🌲 Emerald Forest",
        "desc": "Lush matrix green, deep forest jade and neon mint highlights",
        "colors": ["#0f1a14", "#50fa7b", "#8be9fd", "#f1fa8c", "#ff5555"],
        "hypr_border": "rgba(50fa7bee) rgba(8be9fdee) 45deg",
        "hypr_inactive": "rgba(0f1a1488)",
        "hypr_rounding": 10,
        "waybar_radius": "10px",
        "accent": "#50fa7b",
        "accent_alt": "#8be9fd",
        "bg": "#0f1a14",
        "bg_alt": "#14261c",
        "fg": "#e0f8e5",
        "fg_muted": "#4e7a5e"
    },
    {
        "name": "🖤 Monochrome Glass",
        "desc": "Minimalist luxury pure black, polished titanium silver & diamond white",
        "colors": ["#111116", "#ffffff", "#cbd5e1", "#e2e8f0", "#333340"],
        "hypr_border": "rgba(ffffffee) rgba(ccccccff) 45deg",
        "hypr_inactive": "rgba(1a1a1a88)",
        "hypr_rounding": 0,
        "waybar_radius": "0px",
        "accent": "#ffffff",
        "accent_alt": "#cbd5e1",
        "bg": "#111116",
        "bg_alt": "#1a1a22",
        "fg": "#ffffff",
        "fg_muted": "#888899"
    }
]

class ThemeSwitcherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gally OS — Visual Theme Gallery")
        self.geometry("780x560")
        self.configure(bg=BG_MAIN)
        self.resizable(False, False)
        
        # Header
        hdr = tk.Frame(self, bg=BG_MAIN, padx=22, pady=14)
        hdr.pack(fill="x")
        
        tk.Label(hdr, text="🎨 Desktop Theme Gallery", font=("Sans", 16, "bold"), fg=ACCENT_GOLD, bg=BG_MAIN).pack(anchor="w")
        tk.Label(hdr, text="Click any theme below to apply colors, borders, and bar styles instantly",
                 font=("Sans", 10), fg=ACCENT_CYAN, bg=BG_MAIN).pack(anchor="w", pady=(2, 0))
        tk.Frame(hdr, height=2, bg=ACCENT_GOLD).pack(fill="x", pady=(10, 0))
        
        # Scrollable Cards Grid Container
        container = tk.Frame(self, bg=BG_MAIN, padx=22, pady=10)
        container.pack(fill="both", expand=True)
        
        for idx, t in enumerate(THEMES):
            row = idx // 2
            col = idx % 2
            
            card = tk.Frame(container, bg=BG_CARD, padx=14, pady=12, relief="flat",
                            highlightthickness=1, highlightbackground=BORDER_COL, cursor="hand2")
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            card.bind("<Button-1>", lambda e, th=t: self.apply_theme(th))
            
            # Title & Desc
            lbl_title = tk.Label(card, text=t["name"], font=("Sans", 11, "bold"), fg=t["accent"], bg=BG_CARD, cursor="hand2")
            lbl_title.pack(anchor="w")
            lbl_title.bind("<Button-1>", lambda e, th=t: self.apply_theme(th))
            
            lbl_desc = tk.Label(card, text=t["desc"], font=("Sans", 9), fg=FG_LIGHT, bg=BG_CARD, wraplength=320, justify="left", cursor="hand2")
            lbl_desc.pack(anchor="w", pady=(2, 8))
            lbl_desc.bind("<Button-1>", lambda e, th=t: self.apply_theme(th))
            
            # Swatches Row
            swatch_row = tk.Frame(card, bg=BG_CARD, cursor="hand2")
            swatch_row.pack(anchor="w")
            swatch_row.bind("<Button-1>", lambda e, th=t: self.apply_theme(th))
            
            for c in t["colors"]:
                s = tk.Frame(swatch_row, bg=c, width=22, height=14, relief="flat", highlightthickness=1, highlightbackground="#000")
                s.pack(side="left", padx=2)
                s.bind("<Button-1>", lambda e, th=t: self.apply_theme(th))
                
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)
        
        # Footer
        footer = tk.Frame(self, bg=BG_MAIN, padx=22, pady=12)
        footer.pack(fill="x", side="bottom")
        
        tk.Label(footer, text="💡 Tip: Themes automatically sync across Hyprland, Waybar, Kitty, and Gally AI.",
                 font=("Sans", 9, "italic"), fg="#94a3b8", bg=BG_MAIN).pack(side="left")
        
        btn_close = tk.Button(footer, text="Close (Esc)", font=("Sans", 10, "bold"),
                              bg="#1e293b", fg="#ffffff", activebackground=ACCENT_CYAN, activeforeground="#000",
                              relief="flat", padx=16, pady=6, cursor="hand2", command=self.destroy)
        btn_close.pack(side="right")
        
        self.bind("<Escape>", lambda e: self.destroy())

    def apply_theme(self, t):
        waybar_theme = os.path.expanduser("~/.config/waybar/theme.css")
        kitty_theme = os.path.expanduser("~/.config/kitty/theme.conf")
        
        # 1. Write Waybar theme
        css_content = f"""@define-color bg {t['bg']};
@define-color bg-alt {t['bg_alt']};
@define-color border-col {BORDER_COL};
@define-color accent {t['accent']};
@define-color accent-alt {t['accent_alt']};
@define-color fg {t['fg']};
@define-color fg-muted {t['fg_muted']};
@define-color fg-active {t['bg']};
@define-color green #22c55e;
@define-color red #ef4444;
@define-color yellow #fbbf24;

.modules-left,
.modules-center,
.modules-right,
#workspaces button,
#custom-btn-minimize,
#custom-btn-maximize,
#custom-btn-close,
tooltip {{
    border-radius: {t['waybar_radius']};
}}
"""
        # 2. Update Hyprland Borders & Rounding Live
        subprocess.run(["hyprctl", "keyword", "general:col.active_border", t["hypr_border"]], stdout=subprocess.DEVNULL)
        subprocess.run(["hyprctl", "keyword", "general:col.inactive_border", t["hypr_inactive"]], stdout=subprocess.DEVNULL)
        subprocess.run(["hyprctl", "keyword", "decoration:rounding", str(t["hypr_rounding"])], stdout=subprocess.DEVNULL)
        
        # 3. Reload Waybar
        subprocess.run(["killall", "-SIGUSR2", "waybar"], stderr=subprocess.DEVNULL)

        # 4. Save to Gally active theme state
        try:
            import gally_theme_helper
            theme_state = {
                "name": t["name"],
                "bg": t["bg"],
                "bg_card": t["bg_alt"],
                "bg_input": t["bg_alt"],
                "fg": t["fg"],
                "fg_muted": t["fg_muted"],
                "accent": t["accent"],
                "accent_alt": t["accent_alt"],
                "border_col": BORDER_COL,
                "rounding": t["hypr_rounding"],
                "border_width": 2
            }
            gally_theme_helper.save_active_theme(theme_state)
        except Exception:
            pass

        # 5. Notify user
        subprocess.Popen(["notify-send", "-a", "Theme Switcher", "✨ Theme Applied", t["name"]])
        self.destroy()

if __name__ == "__main__":
    app = ThemeSwitcherApp()
    app.mainloop()
