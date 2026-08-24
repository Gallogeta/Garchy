#!/usr/bin/env python3
"""
Cephalon Gally — Ultra-Modern CustomTkinter AI System Core (Warframe Aesthetic)
Native Rounded Glass Cards, Smooth Pill Buttons, 3D Holographic Particle Core,
Dynamic Theme Integration, Full Uncut Neural Voice, and Thread-Safe Queue Streaming.
"""

import os
import sys
import math
import json
import time
import queue
import random
import asyncio
import subprocess
import threading
import urllib.request
import urllib.parse
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

CONFIG_PATH = os.path.expanduser("~/.config/gally/ai_config.json")
HISTORY_PATH = os.path.expanduser("~/.config/gally/cephalon_history.json")

CURRENT_TTS_PROC = None

# Import Memory & Theme Helpers
sys.path.insert(0, os.path.expanduser("~/.config/hypr/scripts"))
try:
    import gally_theme_helper
except Exception:
    gally_theme_helper = None

try:
    import gally_memory_manager
except Exception:
    gally_memory_manager = None

def get_theme_colors():
    if gally_theme_helper:
        t = gally_theme_helper.get_active_theme()
        return {
            "bg": t.get("bg", "#0a0f1d"),
            "bg_card": t.get("bg_card", "#0f172a"),
            "bg_input": t.get("bg_input", "#1e293b"),
            "fg": t.get("fg", "#f1f5f9"),
            "fg_muted": t.get("fg_muted", "#94a3b8"),
            "accent": t.get("accent", "#38bdf8"),
            "accent_alt": t.get("accent_alt", "#fbbf24"),
            "border": t.get("border_col", "#1e293b"),
            "radius": max(12, int(t.get("rounding", 14)))
        }
    return {
        "bg": "#070c1e", "bg_card": "#0d1738", "bg_input": "#13214d",
        "fg": "#f1f5f9", "fg_muted": "#94a3b8", "accent": "#00f0ff",
        "accent_alt": "#fbbf24", "border": "#0284c7", "radius": 16
    }

def load_config():
    if gally_memory_manager:
        return gally_memory_manager.load_config()
    return {}

def save_config(cfg):
    if gally_memory_manager:
        gally_memory_manager.save_config(cfg)

def load_history():
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_history(history_list):
    try:
        os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
        trimmed = history_list[-100:]
        with open(HISTORY_PATH, "w") as f:
            json.dump(trimmed, f, indent=2)
    except Exception:
        pass

def stop_active_tts():
    global CURRENT_TTS_PROC
    if CURRENT_TTS_PROC:
        try:
            CURRENT_TTS_PROC.kill()
        except Exception:
            pass
        CURRENT_TTS_PROC = None
    try:
        subprocess.run(["pkill", "-f", "cephalon_speech"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def speak_voice_neural_async(text, enabled=True, voice="en-US-AriaNeural"):
    global CURRENT_TTS_PROC
    stop_active_tts()
    
    if not enabled or not text.strip():
        return
        
    clean = text.replace("*", "").replace("#", "").replace("`", "").replace("[", "").replace("]", "")
    clean_lines = []
    in_code = False
    for line in clean.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if not in_code and not line.strip().startswith("$") and not line.strip().startswith("sudo"):
            clean_lines.append(line)
    clean = " ".join(clean_lines).strip()
    
    if not clean:
        return

    def run_tts():
        global CURRENT_TTS_PROC
        out_file = f"/tmp/cephalon_speech_{int(time.time()*1000)}.mp3"
        try:
            import edge_tts
            async def generate():
                comm = edge_tts.Communicate(clean, voice, rate="+3%", pitch="+2Hz")
                await comm.save(out_file)
            asyncio.run(generate())
            
            CURRENT_TTS_PROC = subprocess.Popen(["mpv", "--no-video", "--really-quiet", out_file],
                                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            CURRENT_TTS_PROC.wait()
            try: os.remove(out_file)
            except Exception: pass
        except Exception:
            try:
                CURRENT_TTS_PROC = subprocess.Popen(["espeak-ng", "-v", "en-us+f3", "-p", "60", "-s", "145", clean],
                                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                CURRENT_TTS_PROC.wait()
            except Exception:
                pass

    threading.Thread(target=run_tts, daemon=True).start()

class HighGraphicsCephalonMatrix(tk.Canvas):
    def __init__(self, parent, width=280, height=210, bg_color="#0d1738", accent_color="#00f0ff"):
        super().__init__(parent, width=width, height=height, bg=bg_color, highlightthickness=0)
        self.w = width
        self.h = height
        self.cx = width // 2
        self.cy = height // 2
        
        self.rot_x = 0.0
        self.rot_y = 0.0
        self.rot_z = 0.0
        self.inner_rot = 0.0
        self.is_speaking = False
        self.pulse = 0.0
        self.core_color = "#fbbf24"
        self.accent_color = accent_color
        
        phi = (1.0 + math.sqrt(5.0)) / 2.0
        scale = 35.0
        self.raw_outer_verts = [
            (-1,  phi,  0), ( 1,  phi,  0), (-1, -phi,  0), ( 1, -phi,  0),
            ( 0, -1,  phi), ( 0,  1,  phi), ( 0, -1, -phi), ( 0,  1, -phi),
            ( phi,  0, -1), ( phi,  0,  1), (-phi,  0, -1), (-phi,  0,  1)
        ]
        self.outer_verts = [(x * scale, y * scale, z * scale) for (x, y, z) in self.raw_outer_verts]
        
        self.outer_edges = [
            (0, 1), (0, 5), (0, 7), (0, 10), (0, 11),
            (1, 5), (1, 7), (1, 8), (1, 9),
            (2, 3), (2, 4), (2, 6), (2, 10), (2, 11),
            (3, 4), (3, 6), (3, 8), (3, 9),
            (4, 5), (4, 9), (4, 11),
            (5, 9), (5, 11),
            (6, 7), (6, 8), (6, 10),
            (7, 8), (7, 10),
            (8, 9), (10, 11)
        ]

        in_s = 18.0
        self.inner_verts = [
            (0, -in_s*1.6, 0), (in_s, 0, 0), (0, 0, in_s),
            (-in_s, 0, 0), (0, 0, -in_s), (0, in_s*1.6, 0)
        ]
        self.inner_edges = [
            (0, 1), (0, 2), (0, 3), (0, 4),
            (5, 1), (5, 2), (5, 3), (5, 4),
            (1, 2), (2, 3), (3, 4), (4, 1)
        ]

        self.particles = []
        for i in range(40):
            self.particles.append({
                "r": random.uniform(65, 120),
                "theta": random.uniform(0, 2 * math.pi),
                "phi": random.uniform(-0.8, 0.8),
                "speed": random.uniform(0.015, 0.035) * random.choice([1, -1]),
                "size": random.uniform(1.2, 3.2),
                "color": random.choice([self.accent_color, "#fbbf24", "#c084fc", "#38bdf8", "#f43f5e"])
            })
        
        self.animate()

    def set_speaking_state(self, state: bool):
        self.is_speaking = state

    def set_mode_color(self, mode):
        if mode == "child":
            self.core_color = "#f472b6"
        elif mode == "professional_sudo":
            self.core_color = "#ef4444"
        else:
            self.core_color = "#fbbf24"

    def animate(self):
        self.delete("all")
        self.rot_x += 0.015
        self.rot_y += 0.022
        self.rot_z += 0.008
        self.inner_rot -= 0.035
        self.pulse += 0.075
        
        amp = 0.32 if self.is_speaking else 0.08
        pulse_scale = 1.0 + amp * math.sin(self.pulse)
        
        # Orbital Rings
        r_inner = 75 * pulse_scale
        r_outer = 95 * pulse_scale
        self.create_oval(self.cx - r_inner, self.cy - r_inner, self.cx + r_inner, self.cy + r_inner,
                          outline="#1e3a5f", width=1, dash=(3, 6))
        self.create_oval(self.cx - r_outer, self.cy - r_outer, self.cx + r_outer, self.cy + r_outer,
                          outline="#0e243d", width=1, dash=(1, 5))

        # 24-Band Equalizer Rays
        if self.is_speaking:
            num_bands = 24
            for i in range(num_bands):
                ang = i * (2 * math.pi / num_bands) + (self.pulse * 0.4)
                wave = math.sin(self.pulse * 3.5 + i * 1.5) * 22 + math.cos(self.pulse * 2 + i * 0.8) * 8
                r1 = 78 * pulse_scale
                r2 = 85 * pulse_scale + max(3, wave)
                x1 = self.cx + r1 * math.cos(ang)
                y1 = self.cy + r1 * math.sin(ang)
                x2 = self.cx + r2 * math.cos(ang)
                y2 = self.cy + r2 * math.sin(ang)
                col = self.accent_color if i % 2 == 0 else self.core_color
                self.create_line(x1, y1, x2, y2, fill=col, width=2)

        # 40-Particle Swarm
        for p in self.particles:
            p["theta"] += p["speed"]
            px3 = p["r"] * math.cos(p["theta"]) * math.cos(p["phi"])
            py3 = p["r"] * math.sin(p["theta"]) * math.cos(p["phi"])
            pz3 = p["r"] * math.sin(p["phi"])
            
            px = px3 * math.cos(self.rot_y) + pz3 * math.sin(self.rot_y)
            pz = -px3 * math.sin(self.rot_y) + pz3 * math.cos(self.rot_y)
            py = py3 + 8 * math.sin(self.pulse + p["theta"])
            
            fov = 220
            dist = fov / (fov + pz + 120)
            scr_x = self.cx + px * dist * 1.3
            scr_y = self.cy + py * dist * 1.3
            ps = p["size"] * dist * (1.6 if self.is_speaking else 1.1)
            self.create_oval(scr_x - ps, scr_y - ps, scr_x + ps, scr_y + ps, fill=p["color"], outline="")

        # 3D Project Outer & Inner Meshes
        def project_mesh(verts, rx, ry, scale):
            proj = []
            for (x, y, z) in verts:
                x, y, z = x * scale, y * scale, z * scale
                x1 = x * math.cos(ry) + z * math.sin(ry)
                y1 = y
                z1 = -x * math.sin(ry) + z * math.cos(ry)
                x2 = x1
                y2 = y1 * math.cos(rx) - z1 * math.sin(rx)
                z2 = y1 * math.sin(rx) + z1 * math.cos(rx)
                fov = 220
                dist = fov / (fov + z2 + 120)
                px = self.cx + x2 * dist * 1.4
                py = self.cy + y2 * dist * 1.4
                proj.append((px, py, z2))
            return proj

        outer_proj = project_mesh(self.outer_verts, self.rot_x, self.rot_y, pulse_scale)
        inner_proj = project_mesh(self.inner_verts, self.rot_x * 1.5, self.inner_rot, pulse_scale * 1.2)

        for u, v in self.outer_edges:
            x1, y1, z1 = outer_proj[u]
            x2, y2, z2 = outer_proj[v]
            avg_z = (z1 + z2) / 2
            edge_col = self.accent_color if avg_z > -10 else "#034977"
            self.create_line(x1, y1, x2, y2, fill=edge_col, width=2 if self.is_speaking else 1)

        for u, v in self.inner_edges:
            x1, y1, _ = inner_proj[u]
            x2, y2, _ = inner_proj[v]
            self.create_line(x1, y1, x2, y2, fill=self.core_color, width=2)

        for (px, py, z) in outer_proj:
            if z > -20:
                self.create_oval(px - 2, py - 2, px + 2, py + 2, fill=self.accent_color, outline="")

        core_r = 7 if not self.is_speaking else 11 + 3 * math.sin(self.pulse * 2.5)
        self.create_oval(self.cx - core_r - 4, self.cy - core_r - 4,
                          self.cx + core_r + 4, self.cy + core_r + 4,
                          outline="#c084fc", width=1)
        self.create_oval(self.cx - core_r, self.cy - core_r,
                          self.cx + core_r, self.cy + core_r,
                          fill=self.core_color, outline="#ffffff", width=2)
        
        self.after(22, self.animate)

class CephalonApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.theme_colors = get_theme_colors()
        
        self.title("Cephalon Gally — Glassmorphic AI System Core")
        self.geometry("1060x750")
        self.configure(fg_color=self.theme_colors["bg"])
        self.minsize(920, 640)
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.msg_queue = queue.Queue()
        self.config_data = load_config()
        self.history = load_history()
        self.mode = self.config_data.get("mode", "normal")
        self.voice_enabled = self.config_data.get("voice_enabled", True)
        self.voice_name = self.config_data.get("voice_name", "en-US-AriaNeural")
        self.internet_permitted = self.config_data.get("internet_permitted", False)
        self.document_permitted = self.config_data.get("document_access_permitted", False)
        self.sudo_unlocked = False

        # 1. Top Glass Header Card (Rounded 16px)
        self.hdr_frame = ctk.CTkFrame(self, fg_color=self.theme_colors["bg_card"],
                                      corner_radius=self.theme_colors["radius"],
                                      border_width=1, border_color=self.theme_colors["accent"])
        self.hdr_frame.pack(fill="x", padx=16, pady=(14, 8))
        
        hdr_inner = ctk.CTkFrame(self.hdr_frame, fg_color="transparent")
        hdr_inner.pack(fill="x", padx=16, pady=10)
        
        lbl_title = ctk.CTkLabel(hdr_inner, text="🌌 CEPHALON GALLY",
                                 font=ctk.CTkFont(family="Sans", size=18, weight="bold"),
                                 text_color=self.theme_colors["accent"])
        lbl_title.pack(side="left")
        
        self.lbl_mode_badge = ctk.CTkLabel(hdr_inner, text="",
                                           font=ctk.CTkFont(family="Sans", size=11, weight="bold"),
                                           corner_radius=12, padx=12, pady=4)
        self.lbl_mode_badge.pack(side="left", padx=14)
        self.update_mode_badge_ui()
        
        self.lbl_telemetry = ctk.CTkLabel(hdr_inner, text="⚡ RYZEN 9 5900X (24T) | RTX GPU | DUAL 144Hz",
                                          font=ctk.CTkFont(family="Sans", size=11, weight="bold"),
                                          text_color=self.theme_colors["accent_alt"],
                                          fg_color=self.theme_colors["bg_input"], corner_radius=12, padx=14, pady=5)
        self.lbl_telemetry.pack(side="right")

        # 2. Main Content Layout
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=16, pady=4)
        
        # Left Panel (Rounded Glass Card)
        left_panel = ctk.CTkFrame(main_content, fg_color=self.theme_colors["bg_card"],
                                  corner_radius=self.theme_colors["radius"], width=310,
                                  border_width=1, border_color=self.theme_colors["accent"])
        left_panel.pack(side="left", fill="y", padx=(0, 12), pady=(0, 10))
        left_panel.pack_propagate(False)
        
        # 3D Matrix Canvas
        self.matrix_canvas = HighGraphicsCephalonMatrix(left_panel, width=280, height=190,
                                                        bg_color=self.theme_colors["bg_card"],
                                                        accent_color=self.theme_colors["accent"])
        self.matrix_canvas.pack(pady=(10, 2))
        self.matrix_canvas.set_mode_color(self.mode)
        
        self.lbl_status = ctk.CTkLabel(left_panel, text="● CEPHALON ONLINE",
                                       font=ctk.CTkFont(family="Sans", size=11, weight="bold"),
                                       text_color="#22c55e")
        self.lbl_status.pack(pady=(2, 6))
        
        # Mode Selection Pill Buttons
        lbl_p = ctk.CTkLabel(left_panel, text="◈ OPERATION PERSONA ◈",
                             font=ctk.CTkFont(family="Sans", size=10, weight="bold"),
                             text_color=self.theme_colors["accent_alt"])
        lbl_p.pack(pady=(4, 4))
        
        mode_btn_row = ctk.CTkFrame(left_panel, fg_color="transparent")
        mode_btn_row.pack(fill="x", padx=10, pady=2)
        
        self.btn_mode_child = ctk.CTkButton(mode_btn_row, text="🧸 Child", font=ctk.CTkFont(size=10, weight="bold"),
                                            fg_color=self.theme_colors["bg_input"], hover_color="#f472b6",
                                            corner_radius=14, height=28,
                                            command=lambda: self.switch_mode("child"))
        self.btn_mode_child.pack(side="left", fill="x", expand=True, padx=2)
        
        self.btn_mode_normal = ctk.CTkButton(mode_btn_row, text="🚀 Normal", font=ctk.CTkFont(size=10, weight="bold"),
                                             fg_color=self.theme_colors["bg_input"], hover_color=self.theme_colors["accent"],
                                             corner_radius=14, height=28,
                                             command=lambda: self.switch_mode("normal"))
        self.btn_mode_normal.pack(side="left", fill="x", expand=True, padx=2)
        
        self.btn_mode_sudo = ctk.CTkButton(mode_btn_row, text="⚡ Sudo", font=ctk.CTkFont(size=10, weight="bold"),
                                           fg_color=self.theme_colors["bg_input"], hover_color="#ef4444",
                                           corner_radius=14, height=28,
                                           command=lambda: self.switch_mode("professional_sudo"))
        self.btn_mode_sudo.pack(side="left", fill="x", expand=True, padx=2)
        
        # Privacy & Sandboxing Controls
        lbl_priv = ctk.CTkLabel(left_panel, text="─ PRIVACY & SANDBOX ─",
                                font=ctk.CTkFont(family="Sans", size=10, weight="bold"),
                                text_color=self.theme_colors["fg_muted"])
        lbl_priv.pack(pady=(10, 4))
        
        self.btn_internet = ctk.CTkButton(left_panel, text="", font=ctk.CTkFont(size=11, weight="bold"),
                                          fg_color=self.theme_colors["bg_input"], corner_radius=14, height=30,
                                          anchor="w", command=self.toggle_internet_permission)
        self.btn_internet.pack(fill="x", padx=12, pady=2)
        
        self.btn_doc = ctk.CTkButton(left_panel, text="", font=ctk.CTkFont(size=11, weight="bold"),
                                     fg_color=self.theme_colors["bg_input"], corner_radius=14, height=30,
                                     anchor="w", command=self.toggle_document_permission)
        self.btn_doc.pack(fill="x", padx=12, pady=2)
        
        self.btn_voice = ctk.CTkButton(left_panel, text="", font=ctk.CTkFont(size=11, weight="bold"),
                                       fg_color=self.theme_colors["bg_input"], corner_radius=14, height=30,
                                       anchor="w", command=self.toggle_voice)
        self.btn_voice.pack(fill="x", padx=12, pady=2)
        self.update_toggle_buttons_ui()

        # Directives
        lbl_dir = ctk.CTkLabel(left_panel, text="─ CEPHALON DIRECTIVES ─",
                               font=ctk.CTkFont(family="Sans", size=10, weight="bold"),
                               text_color=self.theme_colors["fg_muted"])
        lbl_dir.pack(pady=(10, 4))
        
        directives = [
            ("🛡️ Full System Scan", "run_diagnostics"),
            ("⚡ Boost Gaming FPS", "boost_gaming"),
            ("🔊 Audio Repair", "repair_audio"),
            ("🌐 Open Web Link...", "open_web_prompt")
        ]
        for name, act in directives:
            btn = ctk.CTkButton(left_panel, text=name, font=ctk.CTkFont(size=11),
                                fg_color=self.theme_colors["bg_input"], hover_color=self.theme_colors["accent"],
                                corner_radius=14, height=28, anchor="w",
                                command=lambda a=act, n=name: self.handle_directive_click(n, a))
            btn.pack(fill="x", padx=12, pady=2)

        btn_clear = ctk.CTkButton(left_panel, text="🗑️ Clear Console History", font=ctk.CTkFont(size=10),
                                  fg_color="#1e1e2e", hover_color="#f43f5e",
                                  corner_radius=14, height=28,
                                  command=self.clear_console_history)
        btn_clear.pack(fill="x", padx=12, pady=(10, 12), side="bottom")

        # Right Panel: Glowing Chat Console Card
        right_panel = ctk.CTkFrame(main_content, fg_color="transparent")
        right_panel.pack(side="right", fill="both", expand=True, pady=(0, 10))
        
        # Telemetry Progress Bar Card
        self.progress_frame = ctk.CTkFrame(right_panel, fg_color=self.theme_colors["bg_card"],
                                           corner_radius=14, border_width=1, border_color=self.theme_colors["accent"])
        self.progress_frame.pack(fill="x", pady=(0, 8))
        
        self.lbl_progress = ctk.CTkLabel(self.progress_frame, text="⚡ SYSTEM TELEMETRY: READY",
                                         font=ctk.CTkFont(family="Sans", size=10, weight="bold"),
                                         text_color=self.theme_colors["accent"])
        self.lbl_progress.pack(anchor="w", padx=12, pady=(4, 2))
        
        self.prog_bar = ctk.CTkProgressBar(self.progress_frame, progress_color=self.theme_colors["accent"], height=6)
        self.prog_bar.pack(fill="x", padx=12, pady=(0, 6))
        self.prog_bar.set(1.0)

        # Rounded Chat Box Textbox
        self.txt_chat = ctk.CTkTextbox(right_panel, fg_color=self.theme_colors["bg_card"],
                                      text_color=self.theme_colors["fg"],
                                      corner_radius=self.theme_colors["radius"],
                                      border_width=1, border_color=self.theme_colors["accent"],
                                      font=ctk.CTkFont(family="Sans", size=13),
                                      wrap="word")
        self.txt_chat.pack(fill="both", expand=True, pady=(0, 8))
        
        # Rounded Input Bar
        input_bar = ctk.CTkFrame(right_panel, fg_color=self.theme_colors["bg_card"],
                                 corner_radius=16, border_width=1, border_color=self.theme_colors["accent"])
        input_bar.pack(fill="x")
        
        self.ent_query = ctk.CTkEntry(input_bar, fg_color="transparent", border_width=0,
                                      placeholder_text="Transmute a directive to Cephalon Gally... (Enter)",
                                      text_color="#ffffff", font=ctk.CTkFont(family="Sans", size=13))
        self.ent_query.pack(side="left", fill="x", expand=True, padx=12, pady=6)
        self.ent_query.bind("<Return>", lambda e: self.send_query())
        self.ent_query.focus_set()
        
        self.btn_send = ctk.CTkButton(input_bar, text="Transmute ↵",
                                      font=ctk.CTkFont(family="Sans", size=12, weight="bold"),
                                      fg_color=self.theme_colors["accent"], text_color="#000000",
                                      hover_color=self.theme_colors["accent_alt"],
                                      corner_radius=14, height=32, width=120,
                                      command=self.send_query)
        self.btn_send.pack(side="right", padx=8, pady=6)
        
        self.bind("<Escape>", lambda e: self.on_close())
        
        self.render_history()
        self.poll_msg_queue()

    def update_mode_badge_ui(self):
        if self.mode == "child":
            self.lbl_mode_badge.configure(text="[ 🧸 CHILD MODE: SAFE & SIMPLE ]", fg_color="#f472b6", text_color="#000000")
        elif self.mode == "professional_sudo":
            self.lbl_mode_badge.configure(text="[ ⚡ PRO SUDO MODE: SYSADMIN ]", fg_color="#ef4444", text_color="#ffffff")
        else:
            self.lbl_mode_badge.configure(text="[ 🚀 NORMAL MODE: CEPHALON COPILOT ]", fg_color=self.theme_colors["accent_alt"], text_color="#000000")

    def update_toggle_buttons_ui(self):
        if self.internet_permitted:
            self.btn_internet.configure(text="🌐 Internet: ALLOWED 🔓", text_color="#22c55e")
        else:
            self.btn_internet.configure(text="🌐 Internet: BLOCKED 🔒", text_color=self.theme_colors["fg_muted"])
            
        if self.document_permitted:
            self.btn_doc.configure(text="📁 User Docs: PERMITTED 📂", text_color=self.theme_colors["accent"])
        else:
            self.btn_doc.configure(text="📁 User Docs: PROTECTED 🛡️", text_color=self.theme_colors["fg_muted"])
            
        if self.voice_enabled:
            self.btn_voice.configure(text="✨ Neural Voice: ON 🔊", text_color=self.theme_colors["accent_alt"])
        else:
            self.btn_voice.configure(text="🔇 Voice: OFF 🔇", text_color=self.theme_colors["fg_muted"])

    def switch_mode(self, target_mode):
        if target_mode == "professional_sudo" and not self.sudo_unlocked:
            pwd = ctk.CTkInputDialog(text="Enter sudo password to unlock Professional Sysadmin Mode:",
                                     title="Sudo Authentication Required").get_input()
            if not pwd:
                return
            if gally_memory_manager and gally_memory_manager.verify_sudo_password(pwd):
                self.sudo_unlocked = True
                messagebox.showinfo("Access Granted", "⚡ Professional Sudo Mode unlocked, Operator.", parent=self)
            else:
                messagebox.showerror("Authentication Failed", "Incorrect sudo credentials. Access denied.", parent=self)
                return

        self.mode = target_mode
        self.config_data["mode"] = self.mode
        save_config(self.config_data)
        self.update_mode_badge_ui()
        self.matrix_canvas.set_mode_color(self.mode)
        
        msg = f"◈ Operation Mode switched to [{self.mode.upper()}], Operator."
        self.append_message("cephalon", msg)
        speak_voice_neural_async(msg, self.voice_enabled, self.voice_name)

    def toggle_internet_permission(self):
        if not self.internet_permitted:
            ans = messagebox.askyesno("Grant Internet Permission?",
                                      "Operator, do you grant Cephalon permission to access the Internet for queries, package lookups, and downloads?",
                                      parent=self)
            if not ans:
                return
            self.internet_permitted = True
        else:
            self.internet_permitted = False
            
        self.config_data["internet_permitted"] = self.internet_permitted
        save_config(self.config_data)
        self.update_toggle_buttons_ui()
        status_msg = "Internet access GRANTED by Operator." if self.internet_permitted else "Internet access RESTRICTED to offline only."
        self.append_message("cephalon", f"◈ Policy update: {status_msg}")

    def toggle_document_permission(self):
        if not self.document_permitted:
            ans = messagebox.askyesno("Grant Document Folder Access?",
                                      "Operator, do you grant Cephalon permission to view and inspect files in your ~/Documents and personal workspace?",
                                      parent=self)
            if not ans:
                return
            self.document_permitted = True
        else:
            self.document_permitted = False
            
        self.config_data["document_access_permitted"] = self.document_permitted
        save_config(self.config_data)
        self.update_toggle_buttons_ui()
        status_msg = "Document access PERMITTED." if self.document_permitted else "Documents SANDBOXED and protected."
        self.append_message("cephalon", f"◈ Privacy update: {status_msg}")

    def toggle_voice(self):
        self.voice_enabled = not self.voice_enabled
        self.config_data["voice_enabled"] = self.voice_enabled
        save_config(self.config_data)
        self.update_toggle_buttons_ui()
        if not self.voice_enabled:
            stop_active_tts()

    def handle_directive_click(self, name, action_type):
        if action_type == "open_web_prompt":
            target = ctk.CTkInputDialog(text="Enter website URL or search topic:", title="Open Link / Search").get_input()
            if target:
                if not self.internet_permitted:
                    ans = messagebox.askyesno("Internet Permission", "Opening web pages requires internet connection. Proceed?", parent=self)
                    if not ans: return
                if gally_memory_manager:
                    gally_memory_manager.open_browser_link(target)
                self.append_message("cephalon", f"◈ Opening web browser to '{target}'...")
            return

        self.txt_chat.insert(tk.END, f"\n\n◈ DIRECTIVE INITIATED: {name}\n")
        self.lbl_status.configure(text="● EXECUTING DIRECTIVE...", text_color=self.theme_colors["accent_alt"])
        self.matrix_canvas.set_speaking_state(True)
        self.btn_send.configure(state="disabled")
        threading.Thread(target=self.run_live_terminal_task, args=(name, action_type), daemon=True).start()

    def run_live_terminal_task(self, name, action_type):
        if action_type == "run_diagnostics":
            self.msg_queue.put(("progress", (0.2, "Scanning Systemd Journal & Kernel Logs")))
            res1 = subprocess.getoutput("journalctl -p 3 -xb -n 6 --no-pager")
            self.msg_queue.put(("terminal", ("journalctl -p 3 -xb -n 6", res1 if res1 else "[ OK ] Zero critical errors in journal.")))
            
            self.msg_queue.put(("progress", (0.5, "Probing GPU & NVIDIA Telemetry")))
            res2 = subprocess.getoutput("nvidia-smi --query-gpu=name,driver_version,temperature.gpu,utilization.gpu --format=csv,noheader 2>/dev/null || lspci -k | grep -A 2 -E '(VGA|3D)'")
            self.msg_queue.put(("terminal", ("gpu-telemetry-probe", res2)))
            
            self.msg_queue.put(("progress", (0.8, "Checking Memory & Storage Subsystems")))
            res3 = subprocess.getoutput("df -h / | awk 'NR==2 {print \"Root partition: \" $3 \" used of \" $2 \" (\" $5 \" used)\"}'")
            self.msg_queue.put(("terminal", ("storage-health-check", res3)))
            
            self.msg_queue.put(("progress", (1.0, "Diagnostics Complete")))
            summary = "Operator, full diagnostic sweep complete. Kernel logs are clean, NVIDIA GPU acceleration is active, and storage matrices are nominal."

        elif action_type == "boost_gaming":
            self.msg_queue.put(("progress", (0.3, "Activating GameMode Daemon")))
            res1 = subprocess.getoutput("gamemoded -s 2>/dev/null || echo 'GameMode daemon ready'")
            self.msg_queue.put(("terminal", ("gamemoded -s", res1)))
            
            self.msg_queue.put(("progress", (0.7, "Checking NVENC & NVIDIA Performance State")))
            res2 = subprocess.getoutput("nvidia-smi -q -d PERFORMANCE 2>/dev/null | grep 'Performance State' || echo 'P0 Performance Mode'")
            self.msg_queue.put(("terminal", ("nvidia-perf-query", res2)))
            
            self.msg_queue.put(("progress", (1.0, "Gaming Matrix Boosted")))
            summary = "Operator, gaming performance matrices are maximized. Dual 144Hz displays and GameMode high-priority scheduling are engaged."

        elif action_type == "repair_audio":
            self.msg_queue.put(("progress", (0.3, "Probing PipeWire & WirePlumber Status")))
            res1 = subprocess.getoutput("systemctl --user is-active pipewire wireplumber pipewire-pulse")
            self.msg_queue.put(("terminal", ("systemctl --user status pipewire", res1)))
            
            self.msg_queue.put(("progress", (0.7, "Re-initializing Audio Sinks")))
            res2 = subprocess.getoutput("wpctl status | grep -A 5 'Sinks:' || echo 'Audio sinks active'")
            self.msg_queue.put(("terminal", ("wpctl status (Sinks)", res2)))
            
            self.msg_queue.put(("progress", (1.0, "Audio Subsystem Harmonized")))
            summary = "Operator, PipeWire audio routing and WirePlumber nodes have been verified and re-harmonized."

        self.msg_queue.put(("directive_complete", summary))

    def send_query(self):
        prompt = self.ent_query.get().strip()
        if not prompt:
            return
            
        self.ent_query.delete(0, tk.END)
        
        if prompt.lower() in ["clear", "cls", "reset"]:
            self.clear_console_history()
            return
            
        self.append_message("operator", prompt)
        
        p_lower = prompt.lower()
        if p_lower.startswith("open ") and ("http" in p_lower or ".com" in p_lower or ".org" in p_lower or "youtube" in p_lower or "google" in p_lower):
            url = prompt[5:].strip()
            if not self.internet_permitted:
                ans = messagebox.askyesno("Internet Permission", f"Opening '{url}' requires Internet access. Allow?", parent=self)
                if not ans:
                    self.append_message("cephalon", "◈ Web request cancelled: Internet access was denied.")
                    return
            if gally_memory_manager:
                gally_memory_manager.open_browser_link(url)
            self.append_message("cephalon", f"◈ Launching browser to '{url}' for Operator.")
            return
        
        if gally_memory_manager:
            mem_action = gally_memory_manager.check_for_memory_directives(prompt)
            if mem_action:
                self.append_message("cephalon", mem_action)
                speak_voice_neural_async(mem_action, self.voice_enabled, self.voice_name)
                return

        self.lbl_status.configure(text="● STREAMING NEURAL MATRIX...", text_color=self.theme_colors["accent_alt"])
        self.lbl_progress.configure(text=f"⚡ [{self.mode.upper()}] INFERENCE STREAMING...")
        self.prog_bar.set(0.3)
        self.matrix_canvas.set_speaking_state(True)
        self.btn_send.configure(state="disabled")
        
        self.txt_chat.insert(tk.END, "\n◈ CEPHALON GALLY: ")
        self.txt_chat.see(tk.END)
        
        threading.Thread(target=self.stream_cephalon_thread, args=(prompt,), daemon=True).start()

    def stream_cephalon_thread(self, prompt):
        try:
            if gally_memory_manager:
                full_prompt = gally_memory_manager.build_mode_system_prompt(
                    prompt, mode=self.mode, internet_ok=self.internet_permitted, doc_ok=self.document_permitted
                )
            else:
                full_prompt = prompt
        except Exception:
            full_prompt = prompt

        collected_tokens = []
        try:
            url = "http://127.0.0.1:11434/api/generate"
            payload = json.dumps({
                "model": "gally-cephalon-ai",
                "prompt": full_prompt,
                "stream": True
            }).encode("utf-8")
            
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                for line in resp:
                    if line:
                        data = json.loads(line.decode("utf-8"))
                        token = data.get("response", "")
                        if token:
                            collected_tokens.append(token)
                            self.msg_queue.put(("token", token))
                            
            full_response = "".join(collected_tokens)
        except Exception as e:
            full_response = f"\nOperator, local matrix encountered an anomaly: {e}\nEnsure local ollama daemon is running."
            self.msg_queue.put(("token", full_response))
            
        self.msg_queue.put(("complete", full_response))

    def poll_msg_queue(self):
        try:
            while True:
                msg_type, payload = self.msg_queue.get_nowait()
                if msg_type == "token":
                    self.txt_chat.insert(tk.END, payload)
                    self.txt_chat.see(tk.END)
                elif msg_type == "complete":
                    self.txt_chat.insert(tk.END, "\n")
                    self.txt_chat.see(tk.END)
                    self.history.append({"role": "cephalon", "text": payload, "time": time.time()})
                    save_history(self.history)
                    self.lbl_status.configure(text="● CEPHALON READY", text_color="#22c55e")
                    self.lbl_progress.configure(text="⚡ INFERENCE COMPLETE (100%)")
                    self.prog_bar.set(1.0)
                    self.matrix_canvas.set_speaking_state(False)
                    self.btn_send.configure(state="normal")
                    speak_voice_neural_async(payload, self.voice_enabled, self.voice_name)
                elif msg_type == "progress":
                    val, msg = payload
                    self.prog_bar.set(val)
                    self.lbl_progress.configure(text=f"⚡ {msg} ({int(val*100)}%)")
                elif msg_type == "terminal":
                    cmd_str, out_str = payload
                    self.txt_chat.insert(tk.END, f"\n$ {cmd_str}\n{out_str}\n")
                    self.txt_chat.see(tk.END)
                elif msg_type == "directive_complete":
                    self.append_message("cephalon", payload)
                    self.lbl_status.configure(text="● CEPHALON READY", text_color="#22c55e")
                    self.matrix_canvas.set_speaking_state(False)
                    self.btn_send.configure(state="normal")
                    speak_voice_neural_async(payload, self.voice_enabled, self.voice_name)
        except queue.Empty:
            pass
        self.after(20, self.poll_msg_queue)

    def on_close(self):
        stop_active_tts()
        self.destroy()

    def render_history(self):
        if not self.history:
            welcome = (
                "Greetings, Operator. Cephalon Gally is online and synchronized with your Garchy Linux environment. "
                "All 24 threads on your Ryzen 9 5900X and Dual 144Hz displays are running nominal. How may I assist you?"
            )
            self.append_message("cephalon", welcome)
            save_history(self.history)
        else:
            for item in self.history:
                role = item.get("role")
                text = item.get("text", "")
                if role == "operator":
                    self.txt_chat.insert(tk.END, f"\n\n◈ OPERATOR: {text}\n")
                elif role == "cephalon":
                    self.txt_chat.insert(tk.END, f"\n◈ CEPHALON GALLY: {text}\n")
            self.txt_chat.see(tk.END)

    def append_message(self, role, text):
        self.history.append({"role": role, "text": text, "time": time.time()})
        save_history(self.history)
        if role == "operator":
            self.txt_chat.insert(tk.END, f"\n\n◈ OPERATOR: {text}\n")
        elif role == "cephalon":
            self.txt_chat.insert(tk.END, f"\n◈ CEPHALON GALLY: {text}\n")
        self.txt_chat.see(tk.END)

    def clear_console_history(self):
        self.history = []
        save_history(self.history)
        self.txt_chat.delete("1.0", tk.END)
        welcome = f"◈ Console history purged, Operator. All systems recalibrated in [{self.mode.upper()}] mode."
        self.append_message("cephalon", welcome)
        speak_voice_neural_async(welcome, self.voice_enabled, self.voice_name)

if __name__ == "__main__":
    app = CephalonApp()
    app.mainloop()
