#!/usr/bin/env python3
"""
Garchy OS - On-Screen Visual Help & Shortcuts HUD
Clean, friendly cheatsheet for children, beginners, and users.
"""

import tkinter as tk
from tkinter import ttk

BG_DARK = "#0a0f1d"
BG_CARD = "#131b2e"
FG_LIGHT = "#e0e6ed"
ACCENT_GOLD = "#d4af37"
ACCENT_CYAN = "#00d2ff"
BORDER_COLOR = "#2d3748"

class HelpHudApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Garchy OS — Quick Help & Shortcuts")
        self.geometry("740x520")
        self.configure(bg=BG_DARK)
        self.resizable(False, False)
        
        # Header
        hdr = tk.Frame(self, bg=BG_DARK, padx=20, pady=15)
        hdr.pack(fill="x")
        
        tk.Label(hdr, text="🌌 Garchy OS — Quick Guide & Shortcuts", font=("Sans", 16, "bold"), fg=ACCENT_GOLD, bg=BG_DARK).pack(anchor="w")
        tk.Label(hdr, text="Everything you need to know to navigate your system easily", font=("Sans", 10), fg=ACCENT_CYAN, bg=BG_DARK).pack(anchor="w")
        tk.Frame(hdr, height=2, bg=ACCENT_GOLD).pack(fill="x", pady=(8, 0))
        
        # Cards Grid Container
        container = tk.Frame(self, bg=BG_DARK, padx=20, pady=10)
        container.pack(fill="both", expand=True)
        
        cards = [
            ("🚀 Opening Apps", "• Click any icon on the bottom Dock\n• Press [ Super ] or click 🌌 on top bar for Fullscreen Launchpad\n• Press [ Super + Return ] for Terminal"),
            ("🪟 Window Controls", "• Hold [ Super ] + Drag with Mouse to move\n• Hold [ Super ] + Right Click to resize\n• Press [ Super + Q ] to close window\n• Press [ Super + N ] to minimize window"),
            ("🖥️ Workspaces", "• Click workspace numbers on top bar (1-10)\n• Or press [ Super + 1, 2, 3... 10 ]\n• Left & Right monitors switch together!"),
            ("📸 Screenshots", "• Press [ Super + Shift + S ] to snip an area\n• Press [ Print ] for full screen\n• Saved directly to ~/Pictures/Screenshots"),
            ("🎨 Themes & Wallpapers", "• Click 🎨 on top bar for Theme Switcher\n• Press [ Super + W ] for Wallpaper Gallery\n• Press [ Super + Shift + W ] for Random Wallpaper"),
            ("🤖 Garchy AI Copilot", "• Click 🤖 on top bar for AI Troubleshooter\n• Press [ Super + Shift + Space ] for AI Hub\n• One-click fixes for audio, gaming & system!"),
        ]
        
        for idx, (title, desc) in enumerate(cards):
            row = idx // 2
            col = idx % 2
            
            card = tk.Frame(container, bg=BG_CARD, padx=15, pady=12, relief="flat",
                            highlightthickness=1, highlightbackground=BORDER_COLOR)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            
            tk.Label(card, text=title, font=("Sans", 11, "bold"), fg=ACCENT_CYAN, bg=BG_CARD).pack(anchor="w", pady=(0, 4))
            tk.Label(card, text=desc, font=("Sans", 9), fg=FG_LIGHT, bg=BG_CARD, justify="left").pack(anchor="w")
            
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)
        
        # Footer
        footer = tk.Frame(self, bg=BG_DARK, padx=20, pady=12)
        footer.pack(fill="x", side="bottom")
        
        tk.Label(footer, text="💡 Tip: Press [ F1 ] anytime to open or close this helper card.",
                 font=("Sans", 9, "italic"), fg="#a0aec0", bg=BG_DARK).pack(side="left")
        
        btn_close = tk.Button(footer, text="Got it! (Close)", font=("Sans", 10, "bold"),
                              bg="#2d3748", fg="#ffffff", activebackground=ACCENT_CYAN, activeforeground="#000",
                              relief="flat", padx=16, pady=6, cursor="hand2", command=self.destroy)
        btn_close.pack(side="right")
        
        # Close on Escape or F1
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<F1>", lambda e: self.destroy())

if __name__ == "__main__":
    app = HelpHudApp()
    app.mainloop()
