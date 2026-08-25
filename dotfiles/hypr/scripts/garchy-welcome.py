#!/usr/bin/env python3
"""
🌌 Garchy OS — Official Welcome & First-Boot Center (OOBE)
Interactive first-boot setup wizard, software installer, mirror optimizer,
theme customizer, and system diagnostics with garchy-minimal.jpg branding.
"""

import os
import sys
import json
import shutil
import platform
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gally_theme_helper

WELCOME_CONFIG = os.path.expanduser("~/.config/gally/welcome_config.json")
BANNER_IMG_PATH = os.path.expanduser("~/Pictures/Wallpapers/garchy-minimal.jpg")

def is_welcome_enabled():
    if os.path.exists(WELCOME_CONFIG):
        try:
            with open(WELCOME_CONFIG, "r") as f:
                data = json.load(f)
                return data.get("autostart", True)
        except Exception:
            pass
    return True

def set_welcome_enabled(val: bool):
    os.makedirs(os.path.dirname(WELCOME_CONFIG), exist_ok=True)
    with open(WELCOME_CONFIG, "w") as f:
        json.dump({"autostart": val}, f, indent=2)

class GarchyWelcomeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🌌 Garchy OS — Welcome & Setup Center")
        self.geometry("980x680")
        self.minsize(880, 580)
        self.configure(bg="#0a0f1d")

        # Active Theme Variables
        self.theme = gally_theme_helper.get_active_theme()
        self.bg_main = self.theme.get("bg", "#0a0f1d")
        self.bg_card = self.theme.get("bg_card", "#131c31")
        self.bg_input = self.theme.get("bg_input", "#1e293b")
        self.fg = self.theme.get("fg", "#f1f5f9")
        self.fg_muted = self.theme.get("fg_muted", "#94a3b8")
        self.accent = self.theme.get("accent", "#38bdf8")
        self.accent_alt = self.theme.get("accent_alt", "#fbbf24")

        self.autostart_var = tk.BooleanVar(value=is_welcome_enabled())

        self.build_ui()
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def build_ui(self):
        # Header with Banner Artwork
        header_frame = tk.Frame(self, bg=self.bg_main, height=130)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)

        if os.path.exists(BANNER_IMG_PATH):
            try:
                img = Image.open(BANNER_IMG_PATH)
                img = img.resize((980, 130), Image.Resampling.LANCZOS)
                self.banner_photo = ImageTk.PhotoImage(img)
                lbl_banner = tk.Label(header_frame, image=self.banner_photo, bg=self.bg_main)
                lbl_banner.pack(fill="both", expand=True)

                # Overlay title text
                overlay_frame = tk.Frame(lbl_banner, bg="#050914", padx=16, pady=8)
                overlay_frame.place(relx=0.04, rely=0.5, anchor="w")
                tk.Label(overlay_frame, text="🌌 GARCHY OS", font=("Sans", 18, "bold"), fg=self.accent, bg="#050914").pack(anchor="w")
                tk.Label(overlay_frame, text="Next-Gen Arch Rolling Performance Edition", font=("Sans", 10), fg="#e2e8f0", bg="#050914").pack(anchor="w")
            except Exception:
                self.fallback_header(header_frame)
        else:
            self.fallback_header(header_frame)

        # Main Navigation Bar (Sidebar or Top Tabs)
        nav_bar = tk.Frame(self, bg="#0d1527", padx=12, pady=6)
        nav_bar.pack(fill="x")

        self.tab_buttons = {}
        tabs = [
            ("🌟 Overview", self.show_overview),
            ("⚡ Fast Mirrors & Updates", self.show_mirrors),
            ("🎮 Gaming Suite", self.show_gaming),
            ("📦 Software & Browsers", self.show_apps),
            ("🎨 Personalize Rice", self.show_personalize),
            ("🛡️ System & Snapshots", self.show_system)
        ]

        for name, callback in tabs:
            btn = tk.Button(nav_bar, text=name, font=("Sans", 10, "bold"),
                            bg="#131c31", fg="#cbd5e1", activebackground=self.accent, activeforeground="#000",
                            relief="flat", padx=12, pady=6, cursor="hand2", command=callback)
            btn.pack(side="left", padx=4)
            self.tab_buttons[name] = btn

        # Content Container
        self.content_frame = tk.Frame(self, bg=self.bg_main, padx=20, pady=14)
        self.content_frame.pack(fill="both", expand=True)

        # Footer
        footer = tk.Frame(self, bg="#0d1527", padx=20, pady=10)
        footer.pack(fill="x", side="bottom")

        chk = tk.Checkbutton(footer, text="Launch Welcome Center on startup", variable=self.autostart_var,
                             font=("Sans", 9), fg=self.fg, bg="#0d1527", selectcolor="#1e293b",
                             activebackground="#0d1527", activeforeground=self.accent,
                             command=self.toggle_autostart)
        chk.pack(side="left")

        tk.Button(footer, text="Terminal (Super+Enter)", font=("Sans", 9, "bold"),
                  bg="#1e293b", fg=self.accent, relief="flat", padx=12, pady=4, cursor="hand2",
                  command=lambda: subprocess.Popen(["kitty"])).pack(side="right", padx=6)

        tk.Button(footer, text="Cephalon AI (Super+Shift+Space)", font=("Sans", 9, "bold"),
                  bg="#1e293b", fg=self.accent_alt, relief="flat", padx=12, pady=4, cursor="hand2",
                  command=lambda: subprocess.Popen([os.path.expanduser("~/.config/hypr/scripts/gally-ai-hud.sh")])).pack(side="right", padx=6)

        # Start on Overview Tab
        self.show_overview()

    def fallback_header(self, parent):
        tk.Label(parent, text="🌌 GARCHY OS", font=("Sans", 20, "bold"), fg=self.accent, bg=self.bg_main).pack(anchor="w", padx=20, pady=(15, 2))
        tk.Label(parent, text="Next-Generation Arch Rolling Linux Performance Rice", font=("Sans", 10), fg=self.fg_muted, bg=self.bg_main).pack(anchor="w", padx=20)

    def clear_content(self):
        for child in self.content_frame.winfo_children():
            child.destroy()

    def set_active_tab_btn(self, active_name):
        for name, btn in self.tab_buttons.items():
            if name == active_name:
                btn.configure(bg=self.accent, fg="#0a0f1d")
            else:
                btn.configure(bg="#131c31", fg="#cbd5e1")

    # ---------------- Tab 1: Overview ----------------
    def show_overview(self):
        self.clear_content()
        self.set_active_tab_btn("🌟 Overview")

        tk.Label(self.content_frame, text="Welcome to Garchy OS Linux", font=("Sans", 14, "bold"), fg=self.fg, bg=self.bg_main).pack(anchor="w", pady=(0, 4))
        tk.Label(self.content_frame, text="Engineered for ultra-low latency gaming, development, dynamic rice aesthetics, and Cephalon AI autonomy.",
                 font=("Sans", 9), fg=self.fg_muted, bg=self.bg_main).pack(anchor="w", pady=(0, 14))

        cards_row = tk.Frame(self.content_frame, bg=self.bg_main)
        cards_row.pack(fill="both", expand=True)

        # Left Column: System Status
        left_card = tk.Frame(cards_row, bg=self.bg_card, padx=16, pady=14, relief="flat", highlightthickness=1, highlightbackground="#1e293b")
        left_card.pack(side="left", fill="both", expand=True, padx=(0, 8))

        tk.Label(left_card, text="📊 System Telemetry", font=("Sans", 11, "bold"), fg=self.accent, bg=self.bg_card).pack(anchor="w", pady=(0, 10))

        # Hardware lines
        specs = [
            ("Kernel", platform.release()),
            ("Processor", "AMD Ryzen 9 5900X (24 Threads)"),
            ("Graphics", "NVIDIA GeForce RTX 3080 Ti"),
            ("Desktop", "Hyprland Wayland Compositor (Dual 144Hz)"),
            ("File System", "Btrfs with Automatic Subvolumes & Snapshots"),
            ("Active Rice", self.theme.get("name", "🌌 Garchy Theme")),
            ("Cephalon AI", "🟢 Active & Online (Autonomous Self-Healing)")
        ]
        for k, v in specs:
            row = tk.Frame(left_card, bg=self.bg_card)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"• {k}: ", font=("Sans", 9, "bold"), fg=self.fg, bg=self.bg_card).pack(side="left")
            tk.Label(row, text=v, font=("Sans", 9), fg=self.accent_alt if "Cephalon" in k else self.fg_muted, bg=self.bg_card).pack(side="left")

        # Right Column: Quick Shortcuts
        right_card = tk.Frame(cards_row, bg=self.bg_card, padx=16, pady=14, relief="flat", highlightthickness=1, highlightbackground="#1e293b")
        right_card.pack(side="right", fill="both", expand=True, padx=(8, 0))

        tk.Label(right_card, text="⚡ Quick Actions", font=("Sans", 11, "bold"), fg=self.accent_alt, bg=self.bg_card).pack(anchor="w", pady=(0, 10))

        actions = [
            ("🚀 Rank Fastest Mirrors", "Optimize pacman download speeds", lambda: self.run_in_terminal("rate-mirrors arch || cachyos-rate-mirrors || true")),
            ("🎮 Open Gaming Hub", "Manage Steam, Proton & GameMode", self.show_gaming),
            ("🎨 Open Theme Gallery (Super+C)", "Switch across 9 dynamic color themes", lambda: subprocess.Popen([os.path.expanduser("~/.config/hypr/scripts/theme-switcher.sh")])),
            ("🖼️ Wallpaper Gallery (Super+W)", "Browse wallpapers & set rotation timer", lambda: subprocess.Popen([os.path.expanduser("~/.config/hypr/scripts/wallpaper-select.sh")])),
            ("🛡️ Create Instant Snapshot", "Take an instant Btrfs backup checkpoint", lambda: self.create_snapshot_dialog())
        ]

        for title, desc, cmd in actions:
            btn_frame = tk.Frame(right_card, bg="#1a233a", padx=10, pady=6, cursor="hand2")
            btn_frame.pack(fill="x", pady=4)
            btn_frame.bind("<Button-1>", lambda e, c=cmd: c())
            
            lbl_t = tk.Label(btn_frame, text=title, font=("Sans", 9, "bold"), fg=self.fg, bg="#1a233a", cursor="hand2")
            lbl_t.pack(anchor="w")
            lbl_t.bind("<Button-1>", lambda e, c=cmd: c())

            lbl_d = tk.Label(btn_frame, text=desc, font=("Sans", 8), fg=self.fg_muted, bg="#1a233a", cursor="hand2")
            lbl_d.pack(anchor="w")
            lbl_d.bind("<Button-1>", lambda e, c=cmd: c())

    # ---------------- Tab 2: Mirrors & Updates ----------------
    def show_mirrors(self):
        self.clear_content()
        self.set_active_tab_btn("⚡ Fast Mirrors & Updates")

        tk.Label(self.content_frame, text="Package Mirrors & System Maintenance", font=("Sans", 14, "bold"), fg=self.fg, bg=self.bg_main).pack(anchor="w", pady=(0, 4))
        tk.Label(self.content_frame, text="Benchmarking mirrors ensures maximum download bandwidth and fastest system updates.",
                 font=("Sans", 9), fg=self.fg_muted, bg=self.bg_main).pack(anchor="w", pady=(0, 14))

        container = tk.Frame(self.content_frame, bg=self.bg_card, padx=18, pady=16, highlightthickness=1, highlightbackground="#1e293b")
        container.pack(fill="both", expand=True)

        items = [
            ("⚡ Benchmark & Rank Mirrors", "Automatically test 50+ Arch & CachyOS mirrors and apply the fastest top 5.",
             lambda: self.run_in_terminal("sudo cachyos-rate-mirrors || rate-mirrors arch")),
            ("🔄 Run Full System Update (pacman -Syu)", "Synchronize all repositories and upgrade installed packages.",
             lambda: self.run_in_terminal("sudo pacman -Syu")),
            ("🧹 Clean Package Cache", "Free disk space by removing obsolete cached pacman tarballs.",
             lambda: self.run_in_terminal("sudo pacman -Sc --noconfirm")),
            ("🔓 Unlock Package Database (Rescue)", "Clear stale /var/lib/pacman/db.lck lock file if update was interrupted.",
             lambda: self.run_in_terminal("python3 ~/.config/hypr/scripts/gally_system_rescue.py pacman"))
        ]

        for title, desc, action in items:
            row = tk.Frame(container, bg="#172138", padx=14, pady=10)
            row.pack(fill="x", pady=6)
            
            info = tk.Frame(row, bg="#172138")
            info.pack(side="left", fill="both", expand=True)
            tk.Label(info, text=title, font=("Sans", 10, "bold"), fg=self.fg, bg="#172138").pack(anchor="w")
            tk.Label(info, text=desc, font=("Sans", 9), fg=self.fg_muted, bg="#172138").pack(anchor="w")

            tk.Button(row, text="Execute", font=("Sans", 9, "bold"),
                      bg=self.accent, fg="#0a0f1d", activebackground=self.accent_alt, relief="flat",
                      padx=14, pady=6, cursor="hand2", command=action).pack(side="right")

    # ---------------- Tab 3: Gaming ----------------
    def show_gaming(self):
        self.clear_content()
        self.set_active_tab_btn("🎮 Gaming Suite")

        tk.Label(self.content_frame, text="Gaming & Compatibility Hub", font=("Sans", 14, "bold"), fg=self.fg, bg=self.bg_main).pack(anchor="w", pady=(0, 4))
        tk.Label(self.content_frame, text="1-Click installers for game launchers, Proton compatibility tools, Wine, and performance HUDs.",
                 font=("Sans", 9), fg=self.fg_muted, bg=self.bg_main).pack(anchor="w", pady=(0, 14))

        container = tk.Frame(self.content_frame, bg=self.bg_card, padx=18, pady=14, highlightthickness=1, highlightbackground="#1e293b")
        container.pack(fill="both", expand=True)

        gaming_apps = [
            ("Steam", "Valve's gaming platform with Proton Windows compatibility.", "steam"),
            ("Lutris", "Open gaming platform for GOG, Epic Games, EA, and Battle.net.", "lutris"),
            ("Heroic Games Launcher", "Native, fast client for Epic Games & GOG.", "heroic-games-launcher-bin"),
            ("GameMode", "Optimizes Linux CPU frequency, GPU clocks, and I/O priority for games.", "gamemode"),
            ("MangoHud", "On-screen overlay for FPS, temperatures, CPU/GPU load, and frame times.", "mangohud"),
            ("ProtonUp-Qt", "Graphical manager to download Proton-GE and Wine-GE compatibility tools.", "protonup-qt")
        ]

        for name, desc, pkg in gaming_apps:
            row = tk.Frame(container, bg="#172138", padx=12, pady=8)
            row.pack(fill="x", pady=4)

            info = tk.Frame(row, bg="#172138")
            info.pack(side="left", fill="both", expand=True)
            tk.Label(info, text=f"🎮 {name}", font=("Sans", 10, "bold"), fg=self.fg, bg="#172138").pack(anchor="w")
            tk.Label(info, text=desc, font=("Sans", 8), fg=self.fg_muted, bg="#172138").pack(anchor="w")

            installed = shutil.which(pkg.split("-")[0]) is not None
            btn_txt = "Installed ✔" if installed else "Install"
            btn_bg = "#1e293b" if installed else self.accent
            btn_fg = self.accent if installed else "#0a0f1d"

            tk.Button(row, text=btn_txt, font=("Sans", 9, "bold"),
                      bg=btn_bg, fg=btn_fg, relief="flat", padx=12, pady=4, cursor="hand2",
                      command=lambda p=pkg: self.run_in_terminal(f"sudo pacman -S --needed --noconfirm {p} || yay -S --needed {p}")).pack(side="right")

    # ---------------- Tab 4: Software & Browsers ----------------
    def show_apps(self):
        self.clear_content()
        self.set_active_tab_btn("📦 Software & Browsers")

        tk.Label(self.content_frame, text="Software & Browser Center", font=("Sans", 14, "bold"), fg=self.fg, bg=self.bg_main).pack(anchor="w", pady=(0, 4))
        tk.Label(self.content_frame, text="Install popular web browsers, developer tools, and communication apps with 1 click.",
                 font=("Sans", 9), fg=self.fg_muted, bg=self.bg_main).pack(anchor="w", pady=(0, 14))

        container = tk.Frame(self.content_frame, bg=self.bg_card, padx=18, pady=14, highlightthickness=1, highlightbackground="#1e293b")
        container.pack(fill="both", expand=True)

        apps = [
            ("Brave Browser", "Privacy-focused browser with built-in ad and tracker blocking.", "brave-bin"),
            ("Zen Browser", "Ultra-fast, beautiful Firefox-based browser with vertical tabs.", "zen-browser-bin"),
            ("Google Chrome", "Google Chrome web browser with sync.", "google-chrome"),
            ("Visual Studio Code", "Code editor with rich extension ecosystem.", "visual-studio-code-bin"),
            ("Discord / Vesktop", "Voice and text chat with Wayland screensharing support.", "vesktop"),
            ("Spotify", "Stream music and podcasts natively.", "spotify"),
            ("OBS Studio", "Live streaming and video recording studio.", "obs-studio")
        ]

        for name, desc, pkg in apps:
            row = tk.Frame(container, bg="#172138", padx=12, pady=8)
            row.pack(fill="x", pady=4)

            info = tk.Frame(row, bg="#172138")
            info.pack(side="left", fill="both", expand=True)
            tk.Label(info, text=name, font=("Sans", 10, "bold"), fg=self.fg, bg="#172138").pack(anchor="w")
            tk.Label(info, text=desc, font=("Sans", 8), fg=self.fg_muted, bg="#172138").pack(anchor="w")

            installed = shutil.which(pkg.split("-")[0]) is not None or shutil.which("code" if "code" in pkg else "") is not None
            btn_txt = "Installed ✔" if installed else "Install"
            btn_bg = "#1e293b" if installed else self.accent
            btn_fg = self.accent if installed else "#0a0f1d"

            tk.Button(row, text=btn_txt, font=("Sans", 9, "bold"),
                      bg=btn_bg, fg=btn_fg, relief="flat", padx=12, pady=4, cursor="hand2",
                      command=lambda p=pkg: self.run_in_terminal(f"sudo pacman -S --needed --noconfirm {p} || yay -S --needed {p}")).pack(side="right")

    # ---------------- Tab 5: Personalization ----------------
    def show_personalize(self):
        self.clear_content()
        self.set_active_tab_btn("🎨 Personalize Rice")

        tk.Label(self.content_frame, text="Personalization & Theming Hub", font=("Sans", 14, "bold"), fg=self.fg, bg=self.bg_main).pack(anchor="w", pady=(0, 4))
        tk.Label(self.content_frame, text="Customize color schemes, wallpapers, Waybar, Kitty, and window decorations across Garchy OS.",
                 font=("Sans", 9), fg=self.fg_muted, bg=self.bg_main).pack(anchor="w", pady=(0, 14))

        container = tk.Frame(self.content_frame, bg=self.bg_card, padx=18, pady=16, highlightthickness=1, highlightbackground="#1e293b")
        container.pack(fill="both", expand=True)

        cards = [
            ("🎨 Open Visual Theme Switcher (Super+C)", "Switch across 9 signature themes with real-time border, Waybar, and Kitty recoloring.",
             lambda: subprocess.Popen([os.path.expanduser("~/.config/hypr/scripts/theme-switcher.sh")])),
            ("🖼️ Open Wallpaper Gallery (Super+W)", "Browse HD wallpapers, add custom folders, and set auto-rotation timer intervals.",
             lambda: subprocess.Popen([os.path.expanduser("~/.config/hypr/scripts/wallpaper-select.sh")])),
            ("🪟 Toggle Window Opacity (Super+O)", "Switch between 100% solid opacity and glassmorphism translucent mode.",
             lambda: subprocess.Popen([os.path.expanduser("~/.config/hypr/scripts/opacity.sh")])),
            ("🎵 Floating Audio Visualizer (Super+Shift+V)", "Open CAVA 144Hz real-time frequency sound spectrum bar.",
             lambda: subprocess.Popen(["kitty", "--class=gally_visualizer", "-e", "cava"]))
        ]

        for title, desc, action in cards:
            row = tk.Frame(container, bg="#172138", padx=14, pady=10)
            row.pack(fill="x", pady=6)

            info = tk.Frame(row, bg="#172138")
            info.pack(side="left", fill="both", expand=True)
            tk.Label(info, text=title, font=("Sans", 10, "bold"), fg=self.fg, bg="#172138").pack(anchor="w")
            tk.Label(info, text=desc, font=("Sans", 9), fg=self.fg_muted, bg="#172138").pack(anchor="w")

            tk.Button(row, text="Open", font=("Sans", 9, "bold"),
                      bg=self.accent, fg="#0a0f1d", activebackground=self.accent_alt, relief="flat",
                      padx=14, pady=6, cursor="hand2", command=action).pack(side="right")

    # ---------------- Tab 6: System & Snapshots ----------------
    def show_system(self):
        self.clear_content()
        self.set_active_tab_btn("🛡️ System & Snapshots")

        tk.Label(self.content_frame, text="System Resilience, Snapshots & Diagnostics", font=("Sans", 14, "bold"), fg=self.fg, bg=self.bg_main).pack(anchor="w", pady=(0, 4))
        tk.Label(self.content_frame, text="Instant Btrfs snapshots, audio diagnostics, and self-healing repair tools.",
                 font=("Sans", 9), fg=self.fg_muted, bg=self.bg_main).pack(anchor="w", pady=(0, 14))

        container = tk.Frame(self.content_frame, bg=self.bg_card, padx=18, pady=16, highlightthickness=1, highlightbackground="#1e293b")
        container.pack(fill="both", expand=True)

        tools = [
            ("📸 Create Btrfs Snapshot Checkpoint", "Generate an instant local snapshot before updating or testing modifications.",
             self.create_snapshot_dialog),
            ("🔊 PipeWire Audio Re-Harmonize", "Restart and synchronize PipeWire, WirePlumber, and EasyEffects daemons.",
             lambda: self.run_in_terminal("python3 ~/.config/hypr/scripts/gally_system_rescue.py audio")),
            ("🛡️ Cephalon Security Sentinel Audit", "Check listening ports, failed sudo attempts, and firewall status.",
             lambda: self.run_in_terminal("python3 ~/.config/hypr/scripts/gally_security_sentinel.py")),
            ("📊 Launch BTOP Hardware Telemetry", "Inspect 24-thread CPU loads, GPU VRAM clocks, and NVMe I/O in real-time.",
             lambda: subprocess.Popen(["kitty", "-e", "btop"]))
        ]

        for title, desc, action in tools:
            row = tk.Frame(container, bg="#172138", padx=14, pady=10)
            row.pack(fill="x", pady=6)

            info = tk.Frame(row, bg="#172138")
            info.pack(side="left", fill="both", expand=True)
            tk.Label(info, text=title, font=("Sans", 10, "bold"), fg=self.fg, bg="#172138").pack(anchor="w")
            tk.Label(info, text=desc, font=("Sans", 9), fg=self.fg_muted, bg="#172138").pack(anchor="w")

            tk.Button(row, text="Run", font=("Sans", 9, "bold"),
                      bg=self.accent, fg="#0a0f1d", activebackground=self.accent_alt, relief="flat",
                      padx=14, pady=6, cursor="hand2", command=action).pack(side="right")

    # ---------------- Helpers ----------------
    def run_in_terminal(self, cmd_str):
        subprocess.Popen(["kitty", "sh", "-c", f"{cmd_str}; echo '\nPress Enter to close...'; read _"])

    def create_snapshot_dialog(self):
        self.run_in_terminal("python3 ~/.config/hypr/scripts/gally_system_rescue.py snapshot 'Manual checkpoint from Garchy Welcome Center'")

    def toggle_autostart(self):
        val = self.autostart_var.get()
        set_welcome_enabled(val)
        autostart_desktop = os.path.expanduser("~/.config/autostart/garchy-welcome.desktop")
        if val:
            os.makedirs(os.path.dirname(autostart_desktop), exist_ok=True)
            with open(autostart_desktop, "w") as f:
                f.write(f"""[Desktop Entry]
Type=Application
Name=Garchy OS Welcome Center
Exec=python3 {os.path.expanduser('~/.config/hypr/scripts/garchy-welcome.py')}
Icon=preferences-desktop
Terminal=false
Categories=System;Settings;
""")
        else:
            if os.path.exists(autostart_desktop):
                os.remove(autostart_desktop)

if __name__ == "__main__":
    app = GarchyWelcomeApp()
    app.mainloop()
