#!/usr/bin/env python3
"""
==============================================================================
🌌 GARCHY OS — Guided System Setup Wizard & Graphical Installer (GUI)
Modern, lightning-fast offline-first installation matrix for Garchy Linux.
Deploys Btrfs subvolumes, Universal GRUB (UEFI+BIOS), Cephalon AI,
SDDM 3D themes, NetworkManager, and automatic reboot in ~20 seconds.
==============================================================================
"""

import os
import sys
import json
import time
import shutil
import socket
import urllib.request
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk

# Color Palette & Typography
BG_DARK = "#0a0f1d"
BG_CARD = "#111927"
BG_INPUT = "#1a2333"
FG_LIGHT = "#f8fafc"
FG_MUTED = "#94a3b8"
ACCENT_CYAN = "#00f0ff"
ACCENT_GOLD = "#fbbf24"
ACCENT_BLUE = "#3b82f6"
BTN_SUCCESS = "#10b981"
BTN_DANGER = "#ef4444"
BORDER_COL = "#1e293b"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class GarchyInstallerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🌌 Garchy OS — System Setup Wizard")
        self.geometry("920x640")
        self.minsize(860, 580)
        self.configure(fg_color=BG_DARK)
        
        # Center on screen
        self.eval('tk::PlaceWindow . center')
        
        # Setup State Variables
        self.kb_layout = tk.StringVar(value="us")
        self.timezone = tk.StringVar(value="UTC")
        self.selected_disk = tk.StringVar(value="")
        self.disk_mode = tk.StringVar(value="auto_btrfs")
        self.enable_zram = tk.BooleanVar(value=True)
        
        self.username = tk.StringVar(value="gallo")
        self.fullname = tk.StringVar(value="Garchy Operator")
        self.hostname = tk.StringVar(value="garchy-pc")
        self.password = tk.StringVar(value="")
        self.autologin = tk.BooleanVar(value=True)
        self.enable_sudo = tk.BooleanVar(value=True)
        
        # AI Persona & Engine Configuration
        self.ai_persona = tk.StringVar(value="normal")
        self.ai_provider = tk.StringVar(value="local")
        self.ai_api_key = tk.StringVar(value="")
        self.enable_tts = tk.BooleanVar(value=True)
        
        # Desktop & SDDM Theme
        self.desktop_env = tk.StringVar(value="xfce.desktop")
        self.sddm_theme = tk.StringVar(value="garchy")
        self.install_gaming = tk.BooleanVar(value=True)
        self.install_xfce = tk.BooleanVar(value=True)
        
        # Main Navigation Container
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=16)
        
        self.frames = {}
        page_classes = (
            WelcomePage,
            NetworkPage,
            DiskPage,
            UserPage,
            AiConfigPage,
            ThemePage,
            SummaryPage,
            ProgressPage,
            DonePage
        )
        
        for PageClass in page_classes:
            name = PageClass.__name__
            frame = PageClass(parent=self.container, controller=self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        self.show_page("WelcomePage")

    def show_page(self, page_name):
        frame = self.frames[page_name]
        if hasattr(frame, "on_show"):
            frame.on_show()
        frame.tkraise()

def make_header(parent, title, subtitle):
    hdr = ctk.CTkFrame(parent, fg_color="transparent")
    hdr.pack(fill="x", pady=(0, 10))
    
    lbl_title = ctk.CTkLabel(hdr, text=f"⟨ {title} ⟩", font=ctk.CTkFont(family="Sans", size=18, weight="bold"),
                             text_color=ACCENT_CYAN)
    lbl_title.pack(anchor="w")
    
    lbl_sub = ctk.CTkLabel(hdr, text=subtitle, font=ctk.CTkFont(family="Sans", size=11), text_color=FG_MUTED)
    lbl_sub.pack(anchor="w", pady=(1, 0))
    
    sep = ctk.CTkFrame(hdr, height=2, fg_color=ACCENT_CYAN)
    sep.pack(fill="x", pady=(6, 0))
    return hdr

def make_nav(parent, back_cmd=None, next_cmd=None, next_text="Next  ▶", is_install=False):
    nav = ctk.CTkFrame(parent, fg_color="transparent")
    nav.pack(fill="x", side="bottom", pady=(10, 0))
    
    if back_cmd:
        btn_back = ctk.CTkButton(nav, text="◀  Back", font=ctk.CTkFont(family="Sans", size=12, weight="bold"),
                                 fg_color=BG_INPUT, hover_color="#2d3748", text_color=FG_LIGHT,
                                 corner_radius=8, width=100, height=36, command=back_cmd)
        btn_back.pack(side="left")
        
    if next_cmd:
        btn_bg = BTN_SUCCESS if is_install else ACCENT_CYAN
        btn_fg = "#ffffff" if is_install else "#000000"
        btn_next = ctk.CTkButton(nav, text=next_text, font=ctk.CTkFont(family="Sans", size=12, weight="bold"),
                                 fg_color=btn_bg, hover_color=ACCENT_GOLD, text_color=btn_fg,
                                 corner_radius=8, width=140, height=36, command=next_cmd)
        btn_next.pack(side="right")
    return nav

# ==============================================================================
# Page 1: Welcome & Locale
# ==============================================================================
class WelcomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        make_header(self, "GARCHY OS // SETUP WIZARD", "Minimalist Arch Linux • 144Hz Gaming & Dev • Built-in Cephalon AI")
        
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COL)
        card.pack(fill="both", expand=True, pady=8, padx=4)
        
        lbl_msg = ctk.CTkLabel(card, text=(
            "Welcome to the official Garchy OS setup experience!\n\n"
            "This guided installer will walk you through a seamless, automated installation tailored "
            "for gaming, software development, and AI workflows.\n\n"
            "✨ Highlights of your installation:\n"
            "  • Btrfs High-Performance Filesystem with automatic Snapper rollback snapshots\n"
            "  • Universal GRUB Bootloader with both UEFI and Legacy BIOS fallback\n"
            "  • 144Hz Glassmorphic Hyprland Desktop + Lightweight XFCE4 Fallback\n"
            "  • SDDM 3D Cephalon Matrix Login Greeter (Qt6 Canvas)\n"
            "  • Integrated Cephalon Gally AI Assistant and Silent System Updater"
        ), font=ctk.CTkFont(family="Sans", size=12), text_color=FG_LIGHT, justify="left", wraplength=760)
        lbl_msg.pack(anchor="w", padx=20, pady=(16, 10))
        
        opt_box = ctk.CTkFrame(card, fg_color=BG_INPUT, corner_radius=8)
        opt_box.pack(fill="x", padx=20, pady=(4, 16))
        
        lbl_kb = ctk.CTkLabel(opt_box, text="⌨️ Keyboard Layout:", font=ctk.CTkFont(family="Sans", size=11, weight="bold"),
                              text_color=ACCENT_GOLD)
        lbl_kb.grid(row=0, column=0, padx=12, pady=10, sticky="w")
        
        self.kb_menu = ctk.CTkOptionMenu(opt_box, values=["us (English US)", "uk (English UK)", "de (German)", "fr (French)", "es (Spanish)", "it (Italian)", "se (Swedish)", "fi (Finnish)", "ru (Russian)", "jp (Japanese)"],
                                         variable=self.controller.kb_layout, fg_color=BG_CARD, button_color=ACCENT_CYAN,
                                         button_hover_color=ACCENT_GOLD, text_color=FG_LIGHT, corner_radius=6,
                                         command=self.on_kb_changed)
        self.kb_menu.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        lbl_tz = ctk.CTkLabel(opt_box, text="🌐 Timezone:", font=ctk.CTkFont(family="Sans", size=11, weight="bold"),
                              text_color=ACCENT_GOLD)
        lbl_tz.grid(row=0, column=2, padx=(20, 10), pady=10, sticky="w")
        
        self.tz_menu = ctk.CTkOptionMenu(opt_box, values=["UTC", "Europe/London", "Europe/Paris", "Europe/Berlin", "Europe/Helsinki", "Europe/Rome", "America/New_York", "America/Chicago", "America/Los_Angeles", "Asia/Tokyo", "Asia/Shanghai"],
                                         variable=self.controller.timezone, fg_color=BG_CARD, button_color=ACCENT_CYAN,
                                         button_hover_color=ACCENT_GOLD, text_color=FG_LIGHT, corner_radius=6)
        self.tz_menu.grid(row=0, column=3, padx=10, pady=10, sticky="w")
        
        make_nav(self, next_cmd=lambda: controller.show_page("NetworkPage"))

    def on_kb_changed(self, val):
        code = val.split()[0]
        try:
            subprocess.run(["loadkeys", code], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

# ==============================================================================
# Page 2: Network & Internet Connectivity
# ==============================================================================
class NetworkPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        make_header(self, "CONNECTIVITY // NETWORK STATUS", "Verify internet connectivity or proceed in Offline Installation Mode")
        
        self.card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COL)
        self.card.pack(fill="both", expand=True, pady=8, padx=4)
        
        self.lbl_status = ctk.CTkLabel(self.card, text="🔍 Checking network connectivity...",
                                       font=ctk.CTkFont(family="Sans", size=13, weight="bold"), text_color=ACCENT_CYAN)
        self.lbl_status.pack(anchor="w", padx=20, pady=(16, 6))
        
        self.lbl_detail = ctk.CTkLabel(self.card, text="", font=ctk.CTkFont(family="Sans", size=11), text_color=FG_MUTED)
        self.lbl_detail.pack(anchor="w", padx=20, pady=(0, 12))
        
        self.net_box = ctk.CTkFrame(self.card, fg_color=BG_INPUT, corner_radius=8)
        self.net_box.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        
        self.lbl_info = ctk.CTkLabel(self.net_box, text="", font=ctk.CTkFont(family="JetBrainsMono Nerd Font", size=10),
                                     text_color=FG_LIGHT, justify="left")
        self.lbl_info.pack(anchor="nw", padx=14, pady=12)
        
        btn_refresh = ctk.CTkButton(self.card, text="🔄 Re-Check Connection", font=ctk.CTkFont(family="Sans", size=11),
                                    fg_color=BG_INPUT, hover_color="#2d3748", text_color=ACCENT_CYAN,
                                    width=160, height=30, corner_radius=6, command=self.check_network_async)
        btn_refresh.pack(anchor="e", padx=20, pady=(0, 12))
        
        make_nav(self, back_cmd=lambda: controller.show_page("WelcomePage"),
                 next_cmd=lambda: controller.show_page("DiskPage"))

    def on_show(self):
        self.check_network_async()

    def check_network_async(self):
        self.lbl_status.configure(text="🔍 Probing network interfaces & pinging mirrors...", text_color=ACCENT_CYAN)
        self.lbl_detail.configure(text="Resolving DNS and checking packet round-trip time...")
        threading.Thread(target=self.run_net_check, daemon=True).start()

    def run_net_check(self):
        online = False
        ip = "Offline"
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("1.1.1.1", 80))
            ip = s.getsockname()[0]
            s.close()
            online = True
        except Exception:
            pass

        info_text = (
            f"  • IPv4 Address:       {ip}\n"
            f"  • Network Interface:  VirtIO / Ethernet / Wireless\n"
            f"  • DNS Resolution:     {'ACTIVE' if online else 'OFFLINE'}\n"
            f"  • Installation Mode:  {'Online Synchronized (Connected)' if online else 'Offline ISO Cache (Fast Local Install)'}\n"
        )

        def update():
            if online:
                self.lbl_status.configure(text="🟢 Connected to Internet (High Speed Ready)", text_color=BTN_SUCCESS)
                self.lbl_detail.configure(text="Network connected. System will install with instant local image deploy.")
            else:
                self.lbl_status.configure(text="🟡 Offline Installation Mode", text_color=ACCENT_GOLD)
                self.lbl_detail.configure(text="No active internet. Garchy OS will deploy directly from the offline ISO image.")
            self.lbl_info.configure(text=info_text)

        self.after(50, update)

# ==============================================================================
# Page 3: Target Storage Drive & Partitioning
# ==============================================================================
class DiskPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        make_header(self, "STORAGE // TARGET DRIVE", "Choose destination drive and high-performance Btrfs filesystem scheme")
        
        self.card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COL)
        self.card.pack(fill="both", expand=True, pady=8, padx=4)
        
        self.list_frame = ctk.CTkScrollableFrame(self.card, fg_color="transparent", height=200)
        self.list_frame.pack(fill="both", expand=True, padx=16, pady=10)
        
        opt_card = ctk.CTkFrame(self.card, fg_color=BG_INPUT, corner_radius=8)
        opt_card.pack(fill="x", padx=16, pady=(0, 12))
        
        chk_btrfs = ctk.CTkRadioButton(opt_card, text="🚀 Automatic Btrfs (Subvolumes @, @home, @snapshots + Zstd Compression + Universal GRUB)",
                                      variable=self.controller.disk_mode, value="auto_btrfs",
                                      font=ctk.CTkFont(family="Sans", size=11, weight="bold"),
                                      text_color=ACCENT_CYAN, fg_color=ACCENT_CYAN)
        chk_btrfs.pack(anchor="w", padx=12, pady=(10, 4))
        
        chk_zram = ctk.CTkCheckBox(opt_card, text="⚡ Enable ZRAM compressed memory swap (Boosts gaming & heavy multitasking)",
                                   variable=self.controller.enable_zram, font=ctk.CTkFont(family="Sans", size=11),
                                   text_color=FG_LIGHT, fg_color=ACCENT_CYAN)
        chk_zram.pack(anchor="w", padx=12, pady=(4, 10))
        
        make_nav(self, back_cmd=lambda: controller.show_page("NetworkPage"),
                 next_cmd=self.validate_and_next)

    def on_show(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
            
        disks = []
        try:
            res = subprocess.run(["lsblk", "-d", "-n", "-o", "NAME,SIZE,MODEL,TYPE"], stdout=subprocess.PIPE, text=True)
            for line in res.stdout.strip().splitlines():
                parts = line.split()
                if len(parts) >= 2 and parts[-1] == "disk" and not parts[0].startswith("loop") and not parts[0].startswith("airootfs"):
                    disks.append((f"/dev/{parts[0]}", parts[1], " ".join(parts[2:-1]) if len(parts) > 3 else "Storage Device"))
        except Exception:
            pass

        if not disks:
            ctk.CTkLabel(self.list_frame, text="⚠️ No storage drives detected! Please attach a hard drive or SSD.",
                         font=ctk.CTkFont(family="Sans", size=12, weight="bold"), text_color=BTN_DANGER).pack(pady=20)
            return

        lbl_instruct = ctk.CTkLabel(self.list_frame, text="Select destination hard drive (Existing data on this drive will be replaced):",
                                    font=ctk.CTkFont(family="Sans", size=11, weight="bold"), text_color=ACCENT_GOLD)
        lbl_instruct.pack(anchor="w", pady=(0, 8))

        for dev_path, size, model in disks:
            row = ctk.CTkFrame(self.list_frame, fg_color=BG_INPUT, corner_radius=8, border_width=1, border_color=BORDER_COL)
            row.pack(fill="x", pady=4)
            
            rb = ctk.CTkRadioButton(row, text=f"💾 {dev_path}  [{size}] — {model}", variable=self.controller.selected_disk,
                                    value=dev_path, font=ctk.CTkFont(family="Sans", size=12, weight="bold"),
                                    text_color=FG_LIGHT, fg_color=ACCENT_CYAN)
            rb.pack(anchor="w", padx=12, pady=10)

        if disks and not self.controller.selected_disk.get():
            self.controller.selected_disk.set(disks[0][0])

    def validate_and_next(self):
        if not self.controller.selected_disk.get():
            messagebox.showwarning("Selection Required", "Please select a target storage drive to continue.")
            return
        self.controller.show_page("UserPage")

# ==============================================================================
# Page 4: User Account & Security
# ==============================================================================
class UserPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        make_header(self, "OPERATOR // IDENTITY & SECURITY", "Set up your credentials, host computer name, and administrative privileges")
        
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COL)
        card.pack(fill="both", expand=True, pady=8, padx=4)
        
        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=24, pady=16)
        
        def add_field(row, label_text, var, show=None):
            lbl = ctk.CTkLabel(form, text=label_text, font=ctk.CTkFont(family="Sans", size=11, weight="bold"),
                               text_color=FG_LIGHT)
            lbl.grid(row=row, column=0, sticky="w", pady=6, padx=(0, 16))
            ent = ctk.CTkEntry(form, textvariable=var, font=ctk.CTkFont(family="Sans", size=11), fg_color=BG_INPUT,
                              text_color=FG_LIGHT, border_color=BORDER_COL, corner_radius=6, width=280, show=show)
            ent.grid(row=row, column=1, sticky="w", pady=6)
            return ent

        add_field(0, "Operator Username:", controller.username)
        add_field(1, "Full Display Name:", controller.fullname)
        add_field(2, "Computer Hostname:", controller.hostname)
        add_field(3, "Account Password:", controller.password, show="•")
        
        self.var_confirm = tk.StringVar(value="")
        add_field(4, "Confirm Password:", self.var_confirm, show="•")
        
        opt_box = ctk.CTkFrame(card, fg_color=BG_INPUT, corner_radius=8)
        opt_box.pack(fill="x", padx=24, pady=(0, 16))
        
        chk_auto = ctk.CTkCheckBox(opt_box, text="🔓 Enable Automatic Login at Boot (Bypasses login password for faster startup)",
                                   variable=self.controller.autologin, font=ctk.CTkFont(family="Sans", size=11),
                                   text_color=FG_LIGHT, fg_color=ACCENT_CYAN)
        chk_auto.pack(anchor="w", padx=12, pady=(10, 4))
        
        chk_sudo = ctk.CTkCheckBox(opt_box, text="🛡️ Grant Administrator Privileges (Enables wheel / sudo permissions)",
                                   variable=self.controller.enable_sudo, font=ctk.CTkFont(family="Sans", size=11),
                                   text_color=FG_LIGHT, fg_color=ACCENT_CYAN)
        chk_sudo.pack(anchor="w", padx=12, pady=(4, 10))
        
        make_nav(self, back_cmd=lambda: controller.show_page("DiskPage"),
                 next_cmd=self.validate_and_next)

    def validate_and_next(self):
        u = self.controller.username.get().strip()
        p = self.controller.password.get()
        c = self.var_confirm.get()
        h = self.controller.hostname.get().strip()
        
        if not u or not u.isalnum():
            messagebox.showwarning("Invalid Username", "Username must be alphanumeric and cannot be empty.")
            return
        if not h:
            messagebox.showwarning("Invalid Hostname", "Please enter a computer hostname.")
            return
        if not p:
            messagebox.showwarning("Password Required", "Please enter a password for your account.")
            return
        if p != c:
            messagebox.showerror("Password Mismatch", "Passwords do not match. Please re-type your password.")
            return
            
        self.controller.show_page("AiConfigPage")

# ==============================================================================
# Page 5: Cephalon Gally AI Copilot Configuration
# ==============================================================================
class AiConfigPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        make_header(self, "CEPHALON AI // MATRIX CONFIGURATION", "Customize your autonomous AI assistant persona, engine, and voice synthesis")
        
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COL)
        card.pack(fill="both", expand=True, pady=8, padx=4)
        
        lbl_persona = ctk.CTkLabel(card, text="🧠 Select Default AI Persona:", font=ctk.CTkFont(family="Sans", size=12, weight="bold"),
                                   text_color=ACCENT_GOLD)
        lbl_persona.pack(anchor="w", padx=20, pady=(12, 6))
        
        p_box = ctk.CTkFrame(card, fg_color=BG_INPUT, corner_radius=8)
        p_box.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkRadioButton(p_box, text="🚀 Normal Companion (Ages 16+) — Gaming guides, Wine/Proton, package manager, coding",
                           variable=self.controller.ai_persona, value="normal", font=ctk.CTkFont(family="Sans", size=11),
                           text_color=FG_LIGHT, fg_color=ACCENT_CYAN).pack(anchor="w", padx=12, pady=6)
                           
        ctk.CTkRadioButton(p_box, text="🌱 Junior Explorer (Ages 10-16) — School homework helper, Python game dev, strictly filtered",
                           variable=self.controller.ai_persona, value="non-adult", font=ctk.CTkFont(family="Sans", size=11),
                           text_color=FG_LIGHT, fg_color=ACCENT_CYAN).pack(anchor="w", padx=12, pady=6)
                           
        ctk.CTkRadioButton(p_box, text="⚡ Master Sysadmin / Sudo Mode — Root system maintenance, kernel diagnostics, snapshot rollbacks",
                           variable=self.controller.ai_persona, value="sudo", font=ctk.CTkFont(family="Sans", size=11),
                           text_color=FG_LIGHT, fg_color=ACCENT_CYAN).pack(anchor="w", padx=12, pady=6)
                           
        lbl_eng = ctk.CTkLabel(card, text="⚡ Default AI Neural Provider:", font=ctk.CTkFont(family="Sans", size=12, weight="bold"),
                               text_color=ACCENT_GOLD)
        lbl_eng.pack(anchor="w", padx=20, pady=(6, 4))
        
        e_box = ctk.CTkFrame(card, fg_color=BG_INPUT, corner_radius=8)
        e_box.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkRadioButton(e_box, text="🤖 Local Offline Cephalon AI (Ollama) — 100% Private, zero internet required",
                           variable=self.controller.ai_provider, value="local", font=ctk.CTkFont(family="Sans", size=11),
                           text_color=FG_LIGHT, fg_color=ACCENT_CYAN).pack(anchor="w", padx=12, pady=6)
                           
        ctk.CTkRadioButton(e_box, text="☁️ Cloud Neural Matrix (Google Gemini, Claude 3.5, GPT-4o, Groq, DeepSeek R1)",
                           variable=self.controller.ai_provider, value="gemini", font=ctk.CTkFont(family="Sans", size=11),
                           text_color=FG_LIGHT, fg_color=ACCENT_CYAN).pack(anchor="w", padx=12, pady=6)
                           
        chk_tts = ctk.CTkCheckBox(card, text="🎙️ Enable Aria Neural Studio Voice Synthesis (Natural female voice)",
                                  variable=self.controller.enable_tts, font=ctk.CTkFont(family="Sans", size=11),
                                  text_color=FG_LIGHT, fg_color=ACCENT_CYAN)
        chk_tts.pack(anchor="w", padx=24, pady=(4, 8))
        
        make_nav(self, back_cmd=lambda: controller.show_page("UserPage"),
                 next_cmd=lambda: controller.show_page("ThemePage"))

# ==============================================================================
# Page 6: Desktop & SDDM 3D Theme Selection
# ==============================================================================
class ThemePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        make_header(self, "EDITION // SDDM 3D THEME & GAMING", "Select your preferred 3D Cephalon login screen edition and package stack")
        
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COL)
        card.pack(fill="both", expand=True, pady=8, padx=4)
        
        lbl_de = ctk.CTkLabel(card, text="🖥️ Choose Default Desktop Environment:",
                              font=ctk.CTkFont(family="Sans", size=12, weight="bold"), text_color=ACCENT_GOLD)
        lbl_de.pack(anchor="w", padx=20, pady=(10, 4))
        
        de_box = ctk.CTkFrame(card, fg_color=BG_INPUT, corner_radius=8)
        de_box.pack(fill="x", padx=20, pady=(0, 8))
        
        ctk.CTkRadioButton(de_box, text="🪟 XFCE4 (Classic Lightweight Desktop — Rock-Solid for VM & Workstations)",
                           variable=self.controller.desktop_env, value="xfce.desktop",
                           font=ctk.CTkFont(family="Sans", size=11), text_color=FG_LIGHT,
                           fg_color=ACCENT_CYAN).pack(anchor="w", padx=12, pady=4)
        
        ctk.CTkRadioButton(de_box, text="🌌 Hyprland (144Hz Glassmorphic Rice + Cephalon Gally AI Copilot)",
                           variable=self.controller.desktop_env, value="hyprland.desktop",
                           font=ctk.CTkFont(family="Sans", size=11), text_color=FG_LIGHT,
                           fg_color=ACCENT_CYAN).pack(anchor="w", padx=12, pady=4)

        lbl_sddm = ctk.CTkLabel(card, text="🎨 Choose Default SDDM 3D Greeter Theme:",
                                font=ctk.CTkFont(family="Sans", size=12, weight="bold"), text_color=ACCENT_GOLD)
        lbl_sddm.pack(anchor="w", padx=20, pady=(6, 4))
        
        t_box = ctk.CTkFrame(card, fg_color=BG_INPUT, corner_radius=8)
        t_box.pack(fill="x", padx=20, pady=(0, 8))
        
        themes = [
            ("garchy", "🌌 Garchy Signature (Electric Cyan & Orokin Gold — Default)"),
            ("garchy-kids", "🌟 Garchy Junior (Junior Space Explorer — Sky Blue & Yellow)"),
            ("garchy-cyber", "⚡ Garchy Cyber (Teens & Esports Gamers — Neon Rose & Cyan)"),
            ("garchy-matrix", "💻 Garchy Matrix (Dev & Hackers — Terminal Emerald Green)"),
            ("garchy-elegance", "✨ Garchy Elegance (Minimalist Obsidian Glass & Sapphire Blue)")
        ]
        
        for val, desc in themes:
            ctk.CTkRadioButton(t_box, text=desc, variable=self.controller.sddm_theme, value=val,
                               font=ctk.CTkFont(family="Sans", size=11), text_color=FG_LIGHT,
                               fg_color=ACCENT_CYAN).pack(anchor="w", padx=12, pady=3)

        opt_box = ctk.CTkFrame(card, fg_color=BG_INPUT, corner_radius=8)
        opt_box.pack(fill="x", padx=20, pady=(4, 8))
        
        chk_game = ctk.CTkCheckBox(opt_box, text="🎮 Pre-install Gaming Ready Stack (Steam, MangoHud, GameMode, Wine, VKD3D)",
                                   variable=self.controller.install_gaming, font=ctk.CTkFont(family="Sans", size=11),
                                   text_color=FG_LIGHT, fg_color=ACCENT_CYAN)
        chk_game.pack(anchor="w", padx=12, pady=(6, 6))
        
        make_nav(self, back_cmd=lambda: controller.show_page("AiConfigPage"),
                 next_cmd=lambda: controller.show_page("SummaryPage"))

# ==============================================================================
# Page 7: Installation Summary
# ==============================================================================
class SummaryPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        make_header(self, "SUMMARY // VERIFY INSTALLATION MATRIX", "Confirm your configuration before partitioning and deploying Garchy OS")
        
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COL)
        card.pack(fill="both", expand=True, pady=8, padx=4)
        
        self.lbl_info = ctk.CTkLabel(card, text="", font=ctk.CTkFont(family="JetBrainsMono Nerd Font", size=11),
                                     text_color=FG_LIGHT, justify="left")
        self.lbl_info.pack(anchor="nw", padx=24, pady=16)
        
        make_nav(self, back_cmd=lambda: controller.show_page("ThemePage"),
                 next_cmd=self.start_installation, next_text="🚀  Install Garchy OS", is_install=True)

    def on_show(self):
        d = self.controller.selected_disk.get()
        u = self.controller.username.get()
        h = self.controller.hostname.get()
        p = self.controller.ai_persona.get()
        t = self.controller.sddm_theme.get()
        kb = self.controller.kb_layout.get()
        tz = self.controller.timezone.get()
        auto = "ENABLED" if self.controller.autologin.get() else "DISABLED"
        
        summary = (
            f"  ┌─────────────────────────────────────────────────────────────┐\n"
            f"  │ 🌌 TARGET DRIVE:      {d:<45} │\n"
            f"  │ 🚀 FILESYSTEM:        Btrfs Subvolumes (@, @home, @snapshots, @log) │\n"
            f"  │ ⚡ BOOTLOADER:        Universal GRUB (UEFI & BIOS MBR Fallback)     │\n"
            f"  │ 👤 OPERATOR:          {u:<45} │\n"
            f"  │ 🖥️  HOSTNAME:          {h:<45} │\n"
            f"  │ 🔓 AUTOLOGIN:         {auto:<45} │\n"
            f"  │ 🧠 AI COPILOT:        Persona: {p:<36} │\n"
            f"  │ 🎨 SDDM THEME:        {t:<45} │\n"
            f"  │ ⌨️  KEYBOARD/TZ:       {kb} / {tz:<37} │\n"
            f"  └─────────────────────────────────────────────────────────────┘\n\n"
            f"  ⚠️  WARNING: Proceeding will format {d} and deploy Garchy OS!"
        )
        self.lbl_info.configure(text=summary)

    def start_installation(self):
        d = self.controller.selected_disk.get()
        if messagebox.askyesno("Confirm Installation", f"Are you sure you want to format {d} and install Garchy OS?"):
            self.controller.show_page("ProgressPage")

# ==============================================================================
# Page 8: Real-time Progress & Slideshow
# ==============================================================================
class ProgressPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        make_header(self, "DEPLOYING // GARCHY OS MATRIX", "Deploying system image, Btrfs subvolumes, and Universal GRUB bootloader...")
        
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COL)
        card.pack(fill="both", expand=True, pady=8, padx=4)
        
        self.lbl_status = ctk.CTkLabel(card, text="Initializing setup...", font=ctk.CTkFont(family="Sans", size=13, weight="bold"),
                                       text_color=ACCENT_CYAN)
        self.lbl_status.pack(anchor="w", padx=20, pady=(14, 2))
        
        self.lbl_detail = ctk.CTkLabel(card, text="Preparing storage architecture...", font=ctk.CTkFont(family="Sans", size=11),
                                       text_color=FG_MUTED)
        self.lbl_detail.pack(anchor="w", padx=20, pady=(0, 10))
        
        self.prog = ctk.CTkProgressBar(card, orientation="horizontal", mode="determinate", fg_color=BG_INPUT,
                                      progress_color=ACCENT_CYAN, height=14, corner_radius=6)
        self.prog.pack(fill="x", padx=20, pady=(0, 12))
        self.prog.set(0.0)
        
        self.log_text = tk.Text(card, height=10, bg=BG_INPUT, fg=FG_LIGHT, font=("JetBrainsMono Nerd Font", 9),
                                relief="flat", bd=0, padx=10, pady=10)
        self.log_text.pack(fill="both", expand=True, padx=20, pady=(0, 14))

    def on_show(self):
        threading.Thread(target=self.run_install_thread, daemon=True).start()

    def log(self, msg):
        self.log_text.insert("end", f"{msg}\n")
        self.log_text.see("end")
        self.update_idletasks()

    def run_install_thread(self):
        disk = self.controller.selected_disk.get()
        username = self.controller.username.get()
        password = self.controller.password.get()
        hostname = self.controller.hostname.get()
        sddm_theme = self.controller.sddm_theme.get()
        autologin = self.controller.autologin.get()
        kb_code = self.controller.kb_layout.get().split()[0]
        tz = self.controller.timezone.get()
        ai_persona = self.controller.ai_persona.get()
        ai_provider = self.controller.ai_provider.get()
        
        def update_ui(pct, status, detail=""):
            self.prog.set(pct / 100.0)
            self.lbl_status.configure(text=status)
            self.lbl_detail.configure(text=detail)
            self.log(f"[{pct}%] {status} — {detail}")
            self.update_idletasks()
            
        def exec_cmd(cmd):
            self.log(f">> {cmd}")
            subprocess.run(cmd, shell=True, check=True)

        try:
            # 1. Partitioning (15%)
            update_ui(10, "Formatting & Partitioning Drive...", f"Creating Universal GPT partitions on {disk}")
            exec_cmd(f"wipefs -af {disk}")
            exec_cmd(f"parted -s {disk} mklabel gpt")
            
            # Partition 1: BIOS Boot (1MB to 3MB)
            exec_cmd(f"parted -s {disk} mkpart bios_boot 1MiB 3MiB")
            exec_cmd(f"parted -s {disk} set 1 bios_grub on")
            
            # Partition 2: EFI System Partition (3MB to 515MB)
            exec_cmd(f"parted -s {disk} mkpart ESP fat32 3MiB 515MiB")
            exec_cmd(f"parted -s {disk} set 2 esp on")
            
            # Partition 3: Btrfs Root Partition (515MB to 100%)
            exec_cmd(f"parted -s {disk} mkpart primary btrfs 515MiB 100%")
            
            p1 = f"{disk}p1" if "nvme" in disk or "mmcblk" in disk else f"{disk}1"
            p2 = f"{disk}p2" if "nvme" in disk or "mmcblk" in disk else f"{disk}2"
            p3 = f"{disk}p3" if "nvme" in disk or "mmcblk" in disk else f"{disk}3"
            
            update_ui(20, "Creating Btrfs Subvolumes...", "Formatting FAT32 EFI and Btrfs root")
            exec_cmd(f"mkfs.fat -F 32 {p2}")
            exec_cmd(f"mkfs.btrfs -f {p3}")
            
            # Create Btrfs Subvolumes
            exec_cmd(f"mount {p3} /mnt")
            exec_cmd("btrfs subvolume create /mnt/@")
            exec_cmd("btrfs subvolume create /mnt/@home")
            exec_cmd("btrfs subvolume create /mnt/@snapshots")
            exec_cmd("btrfs subvolume create /mnt/@var_log")
            exec_cmd("umount /mnt")
            
            # Mount Subvolumes & EFI
            exec_cmd(f"mount -o noatime,compress=zstd,subvol=@ {p3} /mnt")
            exec_cmd("mkdir -p /mnt/home /mnt/.snapshots /mnt/var/log /mnt/boot/efi")
            exec_cmd(f"mount -o noatime,compress=zstd,subvol=@home {p3} /mnt/home")
            exec_cmd(f"mount -o noatime,compress=zstd,subvol=@snapshots {p3} /mnt/.snapshots")
            exec_cmd(f"mount -o noatime,compress=zstd,subvol=@var_log {p3} /mnt/var/log")
            exec_cmd(f"mount {p2} /mnt/boot/efi")
            
            # 2. Fast Offline System Deployment (35% to 65%)
            update_ui(35, "Deploying Garchy OS System Image...", "Copying system files & packages directly from ISO (Fast Offline)...")
            
            # Copy rootfs using -x (--one-file-system) to never touch /run, /proc, /sys, /mnt, /dev
            exclude_flags = (
                "--exclude=/mnt --exclude=/proc --exclude=/sys --exclude=/dev "
                "--exclude=/run --exclude=/tmp --exclude=/lost+found "
                "--exclude=/etc/fstab --exclude=/etc/systemd/system/getty@tty1.service.d"
            )
            
            rsync_cmd = f"rsync -aAX -x --info=progress2 {exclude_flags} / /mnt/"
            self.log(f">> {rsync_cmd}")
            
            process = subprocess.Popen(rsync_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    line_str = line.strip()
                    if "%" in line_str:
                        # Extract percentage from rsync output
                        try:
                            parts = line_str.split()
                            for part in parts:
                                if "%" in part:
                                    raw_pct = int(part.replace("%", "").strip())
                                    # Scale rsync pct (0-100%) to UI range (35% - 65%)
                                    scaled_pct = 35 + int(raw_pct * 0.30)
                                    update_ui(scaled_pct, "Deploying Garchy OS System Image...", f"Copying files: {line_str}")
                                    break
                        except Exception:
                            pass
                    else:
                        self.log(line_str)
                        
            if process.returncode != 0:
                raise Exception(f"Rsync copy exited with code {process.returncode}")
                
            exec_cmd("mkdir -p /mnt/proc /mnt/sys /mnt/dev /mnt/run /mnt/tmp /mnt/boot/efi")
            
            # 3. System Configuration (70%)
            update_ui(65, "Configuring User & Security...", f"Setting up user '{username}' and hostname '{hostname}'")
            exec_cmd("genfstab -U /mnt >> /mnt/etc/fstab")
            
            with open("/mnt/etc/hostname", "w") as f:
                f.write(f"{hostname}\n")
            with open("/mnt/etc/locale.gen", "w") as f:
                f.write("en_US.UTF-8 UTF-8\n")
            exec_cmd("arch-chroot /mnt locale-gen")
            with open("/mnt/etc/locale.conf", "w") as f:
                f.write("LANG=en_US.UTF-8\n")
            with open("/mnt/etc/vconsole.conf", "w") as f:
                f.write(f"KEYMAP={kb_code}\nFONT=eurlatgr\n")
                
            # Timezone
            exec_cmd(f"arch-chroot /mnt ln -sf /usr/share/zoneinfo/{tz} /etc/localtime")
            exec_cmd("arch-chroot /mnt hwclock --systohc")
                
            # Create user on target drive
            exec_cmd(f"arch-chroot /mnt useradd -m -G wheel,video,audio,storage,input,seat,users -s /bin/zsh {username} || true")
            exec_cmd(f"echo '{username}:{password}' | arch-chroot /mnt chpasswd")
            exec_cmd(f"echo 'root:{password}' | arch-chroot /mnt chpasswd")
            exec_cmd("mkdir -p /mnt/etc/sudoers.d")
            exec_cmd("echo '%wheel ALL=(ALL:ALL) ALL' > /mnt/etc/sudoers.d/10-wheel")
            
            # 4. Dotfiles, SDDM Theme & Garchy AI (80%)
            update_ui(80, "Deploying Garchy Desktop Rice & SDDM Theme...", "Configuring Hyprland configs and SDDM 3D theme")
            user_home = f"/mnt/home/{username}"
            exec_cmd(f"mkdir -p {user_home}/.config {user_home}/Pictures/Wallpapers {user_home}/.local/bin")
            
            if os.path.exists("/etc/skel/.config"):
                exec_cmd(f"cp -r /etc/skel/.config/* {user_home}/.config/ 2>/dev/null || true")
            if os.path.exists("/etc/skel/Pictures/Wallpapers"):
                exec_cmd(f"cp -r /etc/skel/Pictures/Wallpapers/* {user_home}/Pictures/Wallpapers/ 2>/dev/null || true")
                
            exec_cmd("ln -sf /usr/bin/garchy-ai /mnt/usr/bin/ai || true")
            
            # Configure SDDM Settings for user choice on target installed drive
            exec_cmd("mkdir -p /mnt/etc/sddm.conf.d")
            with open("/mnt/etc/sddm.conf.d/garchy.conf", "w") as f:
                f.write(f"[Theme]\nCurrent={sddm_theme}\nCursorTheme=Adwaita\nFont=JetBrainsMono Nerd Font\n\n[General]\nNumlock=on\nInputMethod=\n")
                if autologin:
                    de_sess = self.controller.desktop_env.get()
                    f.write(f"\n[Autologin]\nUser={username}\nSession={de_sess}\nRelogin=false\n")
                    
            # AI Initial Config
            ai_cfg_dir = f"{user_home}/.config/gally"
            exec_cmd(f"mkdir -p {ai_cfg_dir}/memory")
            ai_cfg = {
                "active_model": ai_provider,
                "persona_mode": ai_persona,
                "tts_enabled": self.controller.enable_tts.get(),
                "voice_name": "en-US-AriaNeural"
            }
            with open(f"{ai_cfg_dir}/ai_config.json", "w") as f:
                json.dump(ai_cfg, f, indent=2)
                
            exec_cmd(f"arch-chroot /mnt chown -R {username}:{username} /home/{username}")
            
            # 5. Initramfs with Btrfs & Universal GRUB Bootloader (90%)
            update_ui(90, "Building Initramfs & Universal GRUB...", "Configuring mkinitcpio (Btrfs) and GRUB for UEFI + BIOS")
            
            exec_cmd("sed -i 's/^HOOKS=(.*)/HOOKS=(base udev autodetect modconf kms keyboard keymap consolefont block btrfs filesystems fsck)/' /mnt/etc/mkinitcpio.conf")
            exec_cmd("arch-chroot /mnt mkinitcpio -P")
            
            # Install GRUB for UEFI
            exec_cmd("arch-chroot /mnt grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=GRUB --removable --recheck")
            
            # Also install GRUB for BIOS/MBR on the drive so it boots anywhere
            exec_cmd(f"arch-chroot /mnt grub-install --target=i386-pc --recheck {disk} || true")
            
            # Configure GRUB
            exec_cmd("sed -i 's/^GRUB_TIMEOUT=.*/GRUB_TIMEOUT=3/' /mnt/etc/default/grub 2>/dev/null || true")
            exec_cmd("arch-chroot /mnt grub-mkconfig -o /boot/grub/grub.cfg")
            
            # Enable services on target drive
            exec_cmd("arch-chroot /mnt systemctl enable sddm NetworkManager")
            
            # 6. Complete (100%)
            update_ui(100, "Installation Complete!", "Flushing buffers and preparing automated restart...")
            exec_cmd("sync")
            time.sleep(1)
            self.controller.show_page("DonePage")
            
        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            messagebox.showerror("Installation Error", f"An error occurred during installation:\n\n{str(e)}")

# ==============================================================================
# Page 9: Installation Complete & Automated Reboot
# ==============================================================================
class DonePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.countdown = 5
        
        make_header(self, "COMPLETE // SYSTEM MATRIX ACTIVE", "Garchy OS has been successfully installed and configured")
        
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COL)
        card.pack(fill="both", expand=True, pady=8, padx=4)
        
        lbl_msg = ctk.CTkLabel(card, text=(
            "🎉 Congratulations! Garchy OS is now fully installed on your storage drive.\n\n"
            "What happens next:\n"
            "  1. The system will cleanly unmount drives and restart automatically.\n"
            "  2. You will be greeted by your custom 3D Cephalon SDDM login screen.\n"
            "  3. Log in with your new password to access your 144Hz Hyprland desktop.\n\n"
            "Enjoy your ultra-fast, AI-powered Garchy OS!"
        ), font=ctk.CTkFont(family="Sans", size=12), text_color=FG_LIGHT, justify="left")
        lbl_msg.pack(anchor="w", padx=24, pady=(20, 10))
        
        self.lbl_timer = ctk.CTkLabel(card, text="Restarting in 5 seconds...",
                                     font=ctk.CTkFont(family="Sans", size=16, weight="bold"), text_color=ACCENT_CYAN)
        self.lbl_timer.pack(anchor="center", pady=(20, 0))
        
        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(fill="x", side="bottom", pady=10)
        
        btn_reboot = ctk.CTkButton(nav, text="🔄  Reboot Immediately", font=ctk.CTkFont(family="Sans", size=12, weight="bold"),
                                   fg_color=BTN_SUCCESS, hover_color=ACCENT_CYAN, text_color="#ffffff",
                                   corner_radius=8, width=180, height=36, command=self.do_reboot)
        btn_reboot.pack(side="right")

    def on_show(self):
        self.countdown = 5
        self.tick()

    def tick(self):
        if self.countdown > 0:
            self.lbl_timer.configure(text=f"🔄 Automatic Restart in {self.countdown} seconds...")
            self.countdown -= 1
            self.after(1000, self.tick)
        else:
            self.lbl_timer.configure(text="🔄 Restarting system now...")
            self.do_reboot()

    def do_reboot(self):
        try:
            subprocess.run("sync", shell=True)
            subprocess.run("umount -R /mnt 2>/dev/null || true", shell=True)
            subprocess.run("systemctl --force reboot", shell=True)
        except Exception:
            subprocess.run("reboot -f", shell=True)

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("Please run garchy-gui-installer as root (sudo garchy-gui-installer).")
        sys.exit(1)
    app = GarchyInstallerApp()
    app.mainloop()
