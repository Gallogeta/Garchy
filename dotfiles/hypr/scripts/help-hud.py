#!/usr/bin/env python3
"""
Garchy OS - On-Screen Visual Help & Shortcuts HUD
Clean, friendly cheatsheet for all users, synchronized with the active Gally theme.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.expanduser("~/.config/hypr/scripts"))
import gally_theme_helper

class HelpHudApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Load active theme
        self.theme = gally_theme_helper.get_active_theme()
        self.bg_main = self.theme.get("bg", "#0a0f1d")
        self.bg_card = self.theme.get("bg_card", "#131b2e")
        self.bg_input = self.theme.get("bg_input", "#1e293b")
        self.fg_light = self.theme.get("fg", "#e0e6ed")
        self.fg_muted = self.theme.get("fg_muted", "#94a3b8")
        self.accent_gold = self.theme.get("accent", "#d4af37")
        self.accent_cyan = self.theme.get("accent_alt", "#00d2ff")
        self.border_color = self.theme.get("border_col", "#2d3748")
        
        self.title("Garchy OS — Quick Help & Shortcuts")
        self.geometry("740x520")
        self.configure(bg=self.bg_main)
        self.resizable(False, False)
        
        # Header
        hdr = tk.Frame(self, bg=self.bg_main, padx=20, pady=15)
        hdr.pack(fill="x")
        
        tk.Label(hdr, text="🌌 Garchy OS — Quick Guide & Shortcuts", font=("Sans", 16, "bold"),
                 fg=self.accent_gold, bg=self.bg_main).pack(anchor="w")
        tk.Label(hdr, text="Everything you need to know to navigate your system easily", font=("Sans", 10),
                 fg=self.accent_cyan, bg=self.bg_main).pack(anchor="w")
        tk.Frame(hdr, height=2, bg=self.accent_gold).pack(fill="x", pady=(8, 0))
        
        # Cards Grid Container
        container = tk.Frame(self, bg=self.bg_main, padx=20, pady=10)
        container.pack(fill="both", expand=True)
        
        cards = [
            ("🚀 Opening Apps", "• Click any icon on the bottom Dock\n• Press [ Super ] or click 🌌 on top bar for Fullscreen Launchpad\n• Press [ Super + Return ] for Terminal"),
            ("🪟 Window Controls", "• Hold [ Super ] + Drag with Mouse to move\n• Hold [ Super ] + Right Click to resize\n• Press [ Super + Q ] to close window\n• Press [ Super + N ] to minimize window"),
            ("🖥️ Workspaces", "• Click workspace numbers on top bar (1-10)\n• Or press [ Super + 1, 2, 3... 10 ]\n• Left & Right monitors switch together!"),
            ("📸 Screenshots", "• Press [ Super + Shift + S ] to snip an area\n• Press [ Print ] for full screen\n• Saved directly to ~/Pictures/Screenshots"),
            ("🎨 Themes & Wallpapers", "• Click 🎨 on top bar for Theme Switcher\n• Press [ Super + W ] for Wallpaper Gallery\n• Press [ Super + Shift + W ] for Random Wallpaper"),
            ("🤖 Gally AI Copilot", "• Click 🤖 on top bar for AI Assistant\n• Press [ Super + Shift + Space ] for AI Hub\n• Homework, coding, gaming & system help!"),
        ]
        
        for idx, (title, desc) in enumerate(cards):
            row = idx // 2
            col = idx % 2
            
            card = tk.Frame(container, bg=self.bg_card, padx=15, pady=12, relief="flat",
                            highlightthickness=1, highlightbackground=self.border_color)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            
            tk.Label(card, text=title, font=("Sans", 11, "bold"), fg=self.accent_cyan, bg=self.bg_card).pack(anchor="w", pady=(0, 4))
            tk.Label(card, text=desc, font=("Sans", 9), fg=self.fg_light, bg=self.bg_card, justify="left").pack(anchor="w")
            
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)
        
        # Footer
        footer = tk.Frame(self, bg=self.bg_main, padx=20, pady=12)
        footer.pack(fill="x", side="bottom")
        
        tk.Label(footer, text="💡 Tip: Press [ F1 ] anytime to open or close this helper card.",
                 font=("Sans", 9, "italic"), fg=self.fg_muted, bg=self.bg_main).pack(side="left")
        
        btn_close = tk.Button(footer, text="Got it! (Close)", font=("Sans", 10, "bold"),
                              bg=self.bg_input, fg="#ffffff", activebackground=self.accent_cyan, activeforeground="#000",
                              relief="flat", padx=16, pady=6, cursor="hand2", command=self.destroy)
        btn_close.pack(side="right")
        
        # Close on Escape or F1
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<F1>", lambda e: self.destroy())

if __name__ == "__main__":
    app = HelpHudApp()
    app.mainloop()
