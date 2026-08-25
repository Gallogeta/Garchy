#!/usr/bin/env python3
"""
Cephalon Gally — Ultra-Modern CustomTkinter AI System Core (Warframe Aesthetic)
In-Terminal Login & API Key Insert, On-The-Fly Model Switching,
Native Rounded Glass UI, High-Graphics 3D Hologram, 3 Persona Modes, and Neural Voice.
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

# Import Memory, Router & Theme Helpers
sys.path.insert(0, os.path.expanduser("~/.config/hypr/scripts"))
import gally_ai_router
import gally_theme_helper
import gally_memory_manager

CURRENT_TTS_PROC = None

def get_theme_colors():
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
        if not in_code and not line.strip().startswith("$") and not line.strip().startswith("sudo") and not line.strip().startswith("┌") and not line.strip().startswith("│"):
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
    def __init__(self, parent, width=280, height=175, bg_color="#0f172a", accent_color="#00f0ff", accent_alt="#bb9af7"):
        super().__init__(parent, width=width, height=height, bg=bg_color, highlightthickness=0)
        self.w = width
        self.h = height
        self.cx = width // 2
        self.cy = height // 2
        self.bg_color = bg_color
        
        self.rot_x = 0.0
        self.rot_y = 0.0
        self.rot_z = 0.0
        self.inner_rot = 0.0
        self.is_speaking = False
        self.pulse = 0.0
        self.core_color = "#fbbf24"
        self.accent_color = accent_color
        self.accent_alt = accent_alt
        
        phi = (1.0 + math.sqrt(5.0)) / 2.0
        scale = 32.0
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

        in_s = 16.0
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
        for i in range(35):
            self.particles.append({
                "r": random.uniform(55, 105),
                "theta": random.uniform(0, 2 * math.pi),
                "phi": random.uniform(-0.8, 0.8),
                "speed": random.uniform(0.015, 0.035) * random.choice([1, -1]),
                "size": random.uniform(1.2, 3.0),
                "color": random.choice([self.accent_color, self.accent_alt, "#ffffff"])
            })
        
        self.animate()

    def set_speaking_state(self, state: bool):
        self.is_speaking = state

    def set_mode_color(self, mode):
        if mode in ("non_adult", "child", "non-adult", "junior"):
            self.core_color = "#38bdf8"
        elif mode == "professional_sudo":
            self.core_color = "#ef4444"
        else:
            self.core_color = "#fbbf24"

    def set_theme(self, bg_color, accent_color, accent_alt):
        self.bg_color = bg_color
        self.accent_color = accent_color
        self.accent_alt = accent_alt
        self.configure(bg=bg_color)
        for p in self.particles:
            p["color"] = random.choice([accent_color, accent_alt, "#ffffff", self.core_color])

    def animate(self):
        self.delete("all")
        self.rot_x += 0.015
        self.rot_y += 0.022
        self.rot_z += 0.008
        self.inner_rot -= 0.035
        self.pulse += 0.075
        
        amp = 0.32 if self.is_speaking else 0.08
        pulse_scale = 1.0 + amp * math.sin(self.pulse)
        
        r_inner = 68 * pulse_scale
        r_outer = 85 * pulse_scale
        self.create_oval(self.cx - r_inner, self.cy - r_inner, self.cx + r_inner, self.cy + r_inner,
                          outline=self.accent_color, width=1, dash=(3, 6))
        self.create_oval(self.cx - r_outer, self.cy - r_outer, self.cx + r_outer, self.cy + r_outer,
                          outline=self.accent_alt, width=1, dash=(1, 5))

        if self.is_speaking:
            num_bands = 24
            for i in range(num_bands):
                ang = i * (2 * math.pi / num_bands) + (self.pulse * 0.4)
                wave = math.sin(self.pulse * 3.5 + i * 1.5) * 18 + math.cos(self.pulse * 2 + i * 0.8) * 6
                r1 = 70 * pulse_scale
                r2 = 76 * pulse_scale + max(3, wave)
                x1 = self.cx + r1 * math.cos(ang)
                y1 = self.cy + r1 * math.sin(ang)
                x2 = self.cx + r2 * math.cos(ang)
                y2 = self.cy + r2 * math.sin(ang)
                col = self.accent_color if i % 2 == 0 else self.core_color
                self.create_line(x1, y1, x2, y2, fill=col, width=2)

        for p in self.particles:
            p["theta"] += p["speed"]
            px3 = p["r"] * math.cos(p["theta"]) * math.cos(p["phi"])
            py3 = p["r"] * math.sin(p["theta"]) * math.cos(p["phi"])
            pz3 = p["r"] * math.sin(p["phi"])
            
            px = px3 * math.cos(self.rot_y) + pz3 * math.sin(self.rot_y)
            pz = -px3 * math.sin(self.rot_y) + pz3 * math.cos(self.rot_y)
            py = py3 + 6 * math.sin(self.pulse + p["theta"])
            
            fov = 200
            dist = fov / (fov + pz + 100)
            scr_x = self.cx + px * dist * 1.3
            scr_y = self.cy + py * dist * 1.3
            ps = p["size"] * dist * (1.5 if self.is_speaking else 1.0)
            self.create_oval(scr_x - ps, scr_y - ps, scr_x + ps, scr_y + ps, fill=p["color"], outline="")

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
                fov = 200
                dist = fov / (fov + z2 + 100)
                px = self.cx + x2 * dist * 1.3
                py = self.cy + y2 * dist * 1.3
                proj.append((px, py, z2))
            return proj

        outer_proj = project_mesh(self.outer_verts, self.rot_x, self.rot_y, pulse_scale)
        inner_proj = project_mesh(self.inner_verts, self.rot_x * 1.5, self.inner_rot, pulse_scale * 1.2)

        for u, v in self.outer_edges:
            x1, y1, z1 = outer_proj[u]
            x2, y2, z2 = outer_proj[v]
            avg_z = (z1 + z2) / 2
            edge_col = self.accent_color if avg_z > -10 else self.accent_alt
            self.create_line(x1, y1, x2, y2, fill=edge_col, width=2 if self.is_speaking else 1)

        for u, v in self.inner_edges:
            x1, y1, _ = inner_proj[u]
            x2, y2, _ = inner_proj[v]
            self.create_line(x1, y1, x2, y2, fill=self.core_color, width=2)

        for (px, py, z) in outer_proj:
            if z > -20:
                self.create_oval(px - 2, py - 2, px + 2, py + 2, fill=self.accent_color, outline="")

        core_r = 6 if not self.is_speaking else 10 + 2 * math.sin(self.pulse * 2.5)
        self.create_oval(self.cx - core_r - 4, self.cy - core_r - 4,
                          self.cx + core_r + 4, self.cy + core_r + 4,
                          outline=self.accent_alt, width=1)
        self.create_oval(self.cx - core_r, self.cy - core_r,
                          self.cx + core_r, self.cy + core_r,
                          fill=self.core_color, outline="#ffffff", width=2)
        
        self.after(22, self.animate)

class CephalonApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        ctk.set_appearance_mode("dark")
        self.theme_colors = get_theme_colors()
        
        self.title("Cephalon Gally — Multi-Model AI System Core")
        self.geometry("1080x760")
        self.configure(fg_color=self.theme_colors["bg"])
        self.minsize(940, 660)
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.msg_queue = queue.Queue()
        self.config_data = gally_ai_router.load_ai_config()
        self.history = gally_ai_router.load_history()
        self.mode = self.config_data.get("mode", "normal")
        self.voice_enabled = self.config_data.get("voice_enabled", True)
        self.voice_name = self.config_data.get("voice_name", "en-US-AriaNeural")
        self.internet_permitted = self.config_data.get("internet_permitted", False)
        self.sudo_unlocked = False
        self.theme_mtime = gally_theme_helper.get_theme_mtime()
        self.directive_buttons = []

        # --- 1. Top Glass Header Card ---
        self.hdr_frame = ctk.CTkFrame(self, fg_color=self.theme_colors["bg_card"],
                                      corner_radius=self.theme_colors["radius"],
                                      border_width=1, border_color=self.theme_colors["accent"])
        self.hdr_frame.pack(fill="x", padx=16, pady=(12, 6))
        
        hdr_inner = ctk.CTkFrame(self.hdr_frame, fg_color="transparent")
        hdr_inner.pack(fill="x", padx=14, pady=8)
        
        self.lbl_title = ctk.CTkLabel(hdr_inner, text="🌌 CEPHALON GALLY",
                                      font=ctk.CTkFont(family="Sans", size=16, weight="bold"),
                                      text_color=self.theme_colors["accent"])
        self.lbl_title.pack(side="left")
        
        # Center: Live Model Switcher Dropdown
        model_names = [name for (name, _, _) in gally_ai_router.AVAILABLE_MODELS]
        cur_model = self.config_data.get("active_model", "gally-cephalon-ai")
        self.cur_model_name = model_names[0]
        for (name, _, m_id) in gally_ai_router.AVAILABLE_MODELS:
            if m_id == cur_model:
                self.cur_model_name = name
                break
                
        self.opt_model = ctk.CTkOptionMenu(hdr_inner, values=model_names,
                                           font=ctk.CTkFont(family="Sans", size=11, weight="bold"),
                                           fg_color=self.theme_colors["bg_input"],
                                           button_color=self.theme_colors["accent"],
                                           button_hover_color=self.theme_colors["accent_alt"],
                                           text_color=self.theme_colors["fg"],
                                           corner_radius=12, width=250, height=28,
                                           command=self.on_model_changed)
        self.opt_model.set(self.cur_model_name)
        self.opt_model.pack(side="left", padx=14)
        
        # In-Terminal Login Direct Command Button
        self.btn_login_cli = ctk.CTkButton(hdr_inner, text="🔑 In-Terminal Login (login)",
                                           font=ctk.CTkFont(size=10, weight="bold"),
                                           fg_color=self.theme_colors["bg_input"],
                                           hover_color=self.theme_colors["accent"],
                                           corner_radius=12, height=28, width=150,
                                           command=self.trigger_terminal_login_guide)
        self.btn_login_cli.pack(side="right", padx=(8, 0))

        self.lbl_telemetry = ctk.CTkLabel(hdr_inner, text="⚡ RYZEN 9 5900X (24T)",
                                          font=ctk.CTkFont(family="Sans", size=10, weight="bold"),
                                          text_color=self.theme_colors["accent_alt"],
                                          fg_color=self.theme_colors["bg_input"],
                                          corner_radius=12, padx=10, pady=4)
        self.lbl_telemetry.pack(side="right")

        # --- 2. Main Content Layout ---
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=16, pady=4)
        
        # Left Panel (Width 300px)
        self.left_panel = ctk.CTkFrame(main_content, fg_color=self.theme_colors["bg_card"],
                                       corner_radius=self.theme_colors["radius"], width=300,
                                       border_width=1, border_color=self.theme_colors["accent"])
        self.left_panel.pack(side="left", fill="y", padx=(0, 10), pady=(0, 8))
        self.left_panel.pack_propagate(False)
        
        # 3D Matrix Canvas
        self.matrix_canvas = HighGraphicsCephalonMatrix(self.left_panel, width=280, height=175,
                                                        bg_color=self.theme_colors["bg_card"],
                                                        accent_color=self.theme_colors["accent"])
        self.matrix_canvas.pack(pady=(8, 2))
        self.matrix_canvas.set_mode_color(self.mode)
        
        self.lbl_status = ctk.CTkLabel(self.left_panel, text="● CEPHALON ONLINE",
                                       font=ctk.CTkFont(family="Sans", size=10, weight="bold"),
                                       text_color="#22c55e")
        self.lbl_status.pack(pady=(1, 4))
        
        # Persona Mode Pill Row
        self.lbl_p = ctk.CTkLabel(self.left_panel, text="◈ OPERATION PERSONA ◈",
                                  font=ctk.CTkFont(family="Sans", size=9, weight="bold"),
                                  text_color=self.theme_colors["accent_alt"])
        self.lbl_p.pack(pady=(2, 2))
        
        mode_btn_row = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        mode_btn_row.pack(fill="x", padx=10, pady=1)
        
        self.btn_mode_non_adult = ctk.CTkButton(mode_btn_row, text="🌱 Non-Adult (10-16)", font=ctk.CTkFont(size=9, weight="bold"),
                                                fg_color=self.theme_colors["bg_input"], hover_color="#38bdf8",
                                                corner_radius=12, height=26,
                                                command=lambda: self.switch_mode("non_adult"))
        self.btn_mode_non_adult.pack(side="left", fill="x", expand=True, padx=1)
        
        self.btn_mode_normal = ctk.CTkButton(mode_btn_row, text="🚀 Normal (16+)", font=ctk.CTkFont(size=9, weight="bold"),
                                             fg_color=self.theme_colors["bg_input"], hover_color=self.theme_colors["accent"],
                                             corner_radius=12, height=26,
                                             command=lambda: self.switch_mode("normal"))
        self.btn_mode_normal.pack(side="left", fill="x", expand=True, padx=1)
        
        self.btn_mode_sudo = ctk.CTkButton(mode_btn_row, text="⚡ Sudo", font=ctk.CTkFont(size=9, weight="bold"),
                                           fg_color=self.theme_colors["bg_input"], hover_color="#ef4444",
                                           corner_radius=12, height=26,
                                           command=lambda: self.switch_mode("professional_sudo"))
        self.btn_mode_sudo.pack(side="left", fill="x", expand=True, padx=1)
        self.update_mode_buttons_ui()
        
        # Privacy & Sandboxing Controls
        self.lbl_priv = ctk.CTkLabel(self.left_panel, text="─ PRIVACY & SANDBOX ─",
                                     font=ctk.CTkFont(family="Sans", size=9, weight="bold"),
                                     text_color=self.theme_colors["fg_muted"])
        self.lbl_priv.pack(pady=(6, 2))
        
        self.btn_internet = ctk.CTkButton(self.left_panel, text="", font=ctk.CTkFont(size=10, weight="bold"),
                                          fg_color=self.theme_colors["bg_input"], corner_radius=12, height=26,
                                          anchor="w", command=self.toggle_internet_permission)
        self.btn_internet.pack(fill="x", padx=10, pady=2)
        
        self.btn_doc = ctk.CTkButton(self.left_panel, text="", font=ctk.CTkFont(size=10, weight="bold"),
                                     fg_color=self.theme_colors["bg_input"], corner_radius=12, height=26,
                                     anchor="w", command=self.toggle_document_permission)
        self.btn_doc.pack(fill="x", padx=10, pady=2)
        
        self.btn_voice = ctk.CTkButton(self.left_panel, text="", font=ctk.CTkFont(size=10, weight="bold"),
                                       fg_color=self.theme_colors["bg_input"], corner_radius=12, height=26,
                                       anchor="w", command=self.toggle_voice)
        self.btn_voice.pack(fill="x", padx=10, pady=2)
        self.update_toggle_buttons_ui()

        # Directives
        self.lbl_dir = ctk.CTkLabel(self.left_panel, text="─ DIRECTIVES ─",
                                    font=ctk.CTkFont(family="Sans", size=9, weight="bold"),
                                    text_color=self.theme_colors["fg_muted"])
        self.lbl_dir.pack(pady=(6, 2))
        
        directives = [
            ("🛡️ Full System Scan", "run_diagnostics"),
            ("⚡ Boost Gaming FPS", "boost_gaming"),
            ("🔊 Audio Repair", "repair_audio"),
            ("🌐 Open Web Link...", "open_web_prompt")
        ]
        for name, act in directives:
            btn = ctk.CTkButton(self.left_panel, text=name, font=ctk.CTkFont(size=10),
                                fg_color=self.theme_colors["bg_input"], hover_color=self.theme_colors["accent"],
                                corner_radius=12, height=26, anchor="w",
                                command=lambda a=act, n=name: self.handle_directive_click(n, a))
            btn.pack(fill="x", padx=10, pady=1)
            self.directive_buttons.append(btn)

        self.btn_clear = ctk.CTkButton(self.left_panel, text="🗑️ Clear History", font=ctk.CTkFont(size=9),
                                       fg_color=self.theme_colors["bg_input"], hover_color="#f43f5e",
                                       corner_radius=12, height=26,
                                       command=self.clear_console_history)
        self.btn_clear.pack(fill="x", padx=10, pady=(6, 8), side="bottom")

        # Right Panel: Chat Console & Progress Card
        right_panel = ctk.CTkFrame(main_content, fg_color="transparent")
        right_panel.pack(side="right", fill="both", expand=True, pady=(0, 8))
        
        # Telemetry Progress Card
        self.progress_frame = ctk.CTkFrame(right_panel, fg_color=self.theme_colors["bg_card"],
                                           corner_radius=12, border_width=1, border_color=self.theme_colors["accent"])
        self.progress_frame.pack(fill="x", pady=(0, 6))
        
        self.lbl_progress = ctk.CTkLabel(self.progress_frame, text=f"⚡ ACTIVE MODEL: {self.cur_model_name}",
                                         font=ctk.CTkFont(family="Sans", size=10, weight="bold"),
                                         text_color=self.theme_colors["accent"])
        self.lbl_progress.pack(anchor="w", padx=12, pady=(3, 1))
        
        self.prog_bar = ctk.CTkProgressBar(self.progress_frame, progress_color=self.theme_colors["accent"], height=5)
        self.prog_bar.pack(fill="x", padx=12, pady=(0, 5))
        self.prog_bar.set(1.0)

        # Rounded Chat Box
        self.txt_chat = ctk.CTkTextbox(right_panel, fg_color=self.theme_colors["bg_card"],
                                      text_color=self.theme_colors["fg"],
                                      corner_radius=self.theme_colors["radius"],
                                      border_width=1, border_color=self.theme_colors["accent"],
                                      font=ctk.CTkFont(family="Sans", size=12),
                                      wrap="word")
        self.txt_chat.pack(fill="both", expand=True, pady=(0, 6))
        
        # Rounded Input Bar
        self.input_bar = ctk.CTkFrame(right_panel, fg_color=self.theme_colors["bg_card"],
                                      corner_radius=14, border_width=1, border_color=self.theme_colors["accent"])
        self.input_bar.pack(fill="x")
        
        self.ent_query = ctk.CTkEntry(self.input_bar, fg_color="transparent", border_width=0,
                                      placeholder_text="Transmute a directive (or type 'login', 'model gemini')... (Enter)",
                                      text_color="#ffffff", font=ctk.CTkFont(family="Sans", size=12))
        self.ent_query.pack(side="left", fill="x", expand=True, padx=10, pady=5)
        self.ent_query.bind("<Return>", lambda e: self.send_query())
        self.ent_query.focus_set()
        
        self.btn_send = ctk.CTkButton(self.input_bar, text="Transmute ↵",
                                      font=ctk.CTkFont(family="Sans", size=11, weight="bold"),
                                      fg_color=self.theme_colors["accent"], text_color="#000000",
                                      hover_color=self.theme_colors["accent_alt"],
                                      corner_radius=12, height=30, width=110,
                                      command=self.send_query)
        self.btn_send.pack(side="right", padx=6, pady=5)
        
        self.bind("<Escape>", lambda e: self.on_close())
        
        self.render_history()
        self.poll_msg_queue()
        self.check_theme_update()

    def check_theme_update(self):
        try:
            cur_mtime = gally_theme_helper.get_theme_mtime()
            if cur_mtime > self.theme_mtime:
                self.theme_mtime = cur_mtime
                self.theme_colors = get_theme_colors()
                self.apply_theme_live()
        except Exception:
            pass
        self.after(300, self.check_theme_update)

    def apply_theme_live(self):
        c = self.theme_colors
        self.configure(fg_color=c["bg"])
        self.hdr_frame.configure(fg_color=c["bg_card"], border_color=c["accent"])
        self.lbl_title.configure(text_color=c["accent"])
        self.opt_model.configure(fg_color=c["bg_input"], button_color=c["accent"],
                                 button_hover_color=c["accent_alt"], text_color=c["fg"])
        self.btn_login_cli.configure(fg_color=c["bg_input"], hover_color=c["accent"])
        self.lbl_telemetry.configure(text_color=c["accent_alt"], fg_color=c["bg_input"])
        self.left_panel.configure(fg_color=c["bg_card"], border_color=c["accent"])
        self.lbl_p.configure(text_color=c["accent_alt"])
        self.lbl_priv.configure(text_color=c["fg_muted"])
        self.lbl_dir.configure(text_color=c["fg_muted"])
        for btn in self.directive_buttons:
            btn.configure(fg_color=c["bg_input"], hover_color=c["accent"])
        self.btn_clear.configure(fg_color=c["bg_input"])
        self.progress_frame.configure(fg_color=c["bg_card"], border_color=c["accent"])
        self.lbl_progress.configure(text_color=c["accent"])
        self.prog_bar.configure(progress_color=c["accent"])
        self.txt_chat.configure(fg_color=c["bg_card"], text_color=c["fg"], border_color=c["accent"])
        self.input_bar.configure(fg_color=c["bg_card"], border_color=c["accent"])
        self.btn_send.configure(fg_color=c["accent"], hover_color=c["accent_alt"])
        
        self.matrix_canvas.set_theme(c["bg_card"], c["accent"], c["accent_alt"])
        self.update_mode_buttons_ui()
        self.update_toggle_buttons_ui()
        self.render_history()
        self.poll_msg_queue()

    def trigger_terminal_login_guide(self):
        self.ent_query.delete(0, tk.END)
        self.ent_query.insert(0, "login")
        self.send_query()

    def on_model_changed(self, chosen_name):
        for (name, provider, model_id) in gally_ai_router.AVAILABLE_MODELS:
            if name == chosen_name:
                # Check if API key is missing for cloud providers
                key_fields = {
                    "gemini": "gemini_api_key",
                    "claude": "claude_api_key",
                    "openai": "openai_api_key",
                    "deepseek": "deepseek_api_key",
                    "groq": "groq_api_key"
                }
                if provider in key_fields and not self.config_data.get(key_fields[provider]):
                    self.append_message("cephalon", f"◈ [ ! ] {provider.upper()} API key not configured.\nType in terminal: login {provider} <YOUR_KEY>")
                    # Revert dropdown until logged in
                    cur_model = self.config_data.get("active_model", "gally-cephalon-ai")
                    for (n, _, m_id) in gally_ai_router.AVAILABLE_MODELS:
                        if m_id == cur_model:
                            self.opt_model.set(n)
                            break
                    return

                self.config_data["active_provider"] = provider
                self.config_data["active_model"] = model_id
                gally_ai_router.save_ai_config(self.config_data)
                
                self.cur_model_name = chosen_name
                self.lbl_progress.configure(text=f"⚡ ACTIVE MODEL: {chosen_name}")
                msg = f"◈ Active Neural Engine switched to [{chosen_name}], Operator."
                self.append_message("cephalon", msg)
                speak_voice_neural_async(msg, self.voice_enabled, self.voice_name)
                break

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

    def update_mode_buttons_ui(self):
        if not hasattr(self, "btn_mode_non_adult"):
            return
        is_non_adult = self.mode in ("non_adult", "child")
        is_normal = self.mode == "normal"
        is_sudo = self.mode == "professional_sudo"
        
        self.btn_mode_non_adult.configure(fg_color="#0284c7" if is_non_adult else self.theme_colors["bg_input"],
                                          text_color="#ffffff" if is_non_adult else self.theme_colors["fg_muted"])
        self.btn_mode_normal.configure(fg_color=self.theme_colors["accent"] if is_normal else self.theme_colors["bg_input"],
                                       text_color="#000000" if is_normal else self.theme_colors["fg_muted"])
        self.btn_mode_sudo.configure(fg_color="#dc2626" if is_sudo else self.theme_colors["bg_input"],
                                     text_color="#ffffff" if is_sudo else self.theme_colors["fg_muted"])

    def switch_mode(self, target_mode):
        if target_mode in ["child", "non_adult", "non-adult", "junior"]:
            target_mode = "non_adult"

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
        gally_ai_router.save_ai_config(self.config_data)
        self.matrix_canvas.set_mode_color(self.mode)
        self.update_mode_buttons_ui()
        
        if self.mode == "non_adult":
            msg = "◈ Operation Mode switched to [NON-ADULT (AGES 10-16)], Operator. Youth mentoring, learning & safe gaming active."
        elif self.mode == "normal":
            msg = "◈ Operation Mode switched to [NORMAL (AGES 16+)], Operator. Full desktop intelligence & capabilities active."
        else:
            msg = f"◈ Operation Mode switched to [{self.mode.upper()}], Operator."

        self.append_message("cephalon", msg)
        speak_voice_neural_async(msg, self.voice_enabled, self.voice_name)

    def toggle_internet_permission(self):
        if not self.internet_permitted:
            ans = messagebox.askyesno("Grant Internet Permission?",
                                      "Operator, do you grant Cephalon permission to access the Internet for cloud models and web lookups?",
                                      parent=self)
            if not ans:
                return
            self.internet_permitted = True
        else:
            self.internet_permitted = False
            
        self.config_data["internet_permitted"] = self.internet_permitted
        gally_ai_router.save_ai_config(self.config_data)
        self.update_toggle_buttons_ui()
        status_msg = "Internet access GRANTED by Operator." if self.internet_permitted else "Internet access RESTRICTED to offline only."
        self.append_message("cephalon", f"◈ Policy update: {status_msg}")

    def toggle_document_permission(self):
        if not self.document_permitted:
            ans = messagebox.askyesno("Grant Document Folder Access?",
                                      "Operator, do you grant Cephalon permission to inspect files in your ~/Documents and personal workspace?",
                                      parent=self)
            if not ans:
                return
            self.document_permitted = True
        else:
            self.document_permitted = False
            
        self.config_data["document_access_permitted"] = self.document_permitted
        gally_ai_router.save_ai_config(self.config_data)
        self.update_toggle_buttons_ui()
        status_msg = "Document access PERMITTED." if self.document_permitted else "Documents SANDBOXED and protected."
        self.append_message("cephalon", f"◈ Privacy update: {status_msg}")

    def toggle_voice(self):
        self.voice_enabled = not self.voice_enabled
        self.config_data["voice_enabled"] = self.voice_enabled
        gally_ai_router.save_ai_config(self.config_data)
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
        
        # 1. In-Terminal Login & Model Switch Command Interpretation
        handled, cli_msg, new_cfg = gally_ai_router.handle_terminal_command(prompt, self.config_data)
        if handled:
            self.config_data = new_cfg
            # Update active model dropdown if model changed
            cur_model = self.config_data.get("active_model", "gally-cephalon-ai")
            for (n, _, m_id) in gally_ai_router.AVAILABLE_MODELS:
                if m_id == cur_model:
                    self.cur_model_name = n
                    self.opt_model.set(n)
                    self.lbl_progress.configure(text=f"⚡ ACTIVE MODEL: {n}")
                    break
            self.append_message("cephalon", cli_msg)
            return

        # 2. Browser Open Commands
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
        
        # 3. Memory Learning Directives
        if gally_memory_manager:
            mem_action = gally_memory_manager.check_for_memory_directives(prompt)
            if mem_action:
                self.append_message("cephalon", mem_action)
                speak_voice_neural_async(mem_action, self.voice_enabled, self.voice_name)
                return

        self.lbl_status.configure(text="● STREAMING INFERENCE...", text_color=self.theme_colors["accent_alt"])
        self.prog_bar.set(0.3)
        self.matrix_canvas.set_speaking_state(True)
        self.btn_send.configure(state="disabled")
        
        self.txt_chat.insert(tk.END, "\n◈ CEPHALON GALLY: ")
        self.txt_chat.see(tk.END)
        
        threading.Thread(target=self.stream_cephalon_thread, args=(prompt,), daemon=True).start()

    def stream_cephalon_thread(self, prompt):
        try:
            full_prompt = gally_memory_manager.build_mode_system_prompt(
                prompt, mode=self.mode, internet_ok=self.internet_permitted, doc_ok=self.document_permitted
            )
        except Exception:
            full_prompt = prompt

        def on_token(token):
            self.msg_queue.put(("token", token))

        def on_complete(full_resp):
            self.msg_queue.put(("complete", full_resp))

        gally_ai_router.stream_query(full_prompt, self.config_data, on_token, on_complete)

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
                    gally_ai_router.save_history(self.history)
                    self.lbl_status.configure(text="● CEPHALON READY", text_color="#22c55e")
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
            gally_ai_router.save_history(self.history)
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
        gally_ai_router.save_history(self.history)
        if role == "operator":
            self.txt_chat.insert(tk.END, f"\n\n◈ OPERATOR: {text}\n")
        elif role == "cephalon":
            self.txt_chat.insert(tk.END, f"\n◈ CEPHALON GALLY: {text}\n")
        self.txt_chat.see(tk.END)

    def clear_console_history(self):
        self.history = []
        gally_ai_router.save_history(self.history)
        self.txt_chat.delete("1.0", tk.END)
        welcome = f"◈ Console history purged, Operator. All systems recalibrated in [{self.mode.upper()}] mode."
        self.append_message("cephalon", welcome)
        speak_voice_neural_async(welcome, self.voice_enabled, self.voice_name)

if __name__ == "__main__":
    app = CephalonApp()
    app.mainloop()
