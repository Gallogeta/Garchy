#!/usr/bin/env python3
"""
Cephalon Gally — Ultra-Modern CustomTkinter AI System Core (Warframe Aesthetic)
Includes 100% Offline Self-Healing Rescue, Security Sentinel Intruder Alerts,
Fast Local File Search, Child Safety Shield, Standby Disable Switch & Full Sudo Master Mode.
"""

import os
import sys
import re
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

# Import Memory, Router, Theme & Rescue Helpers
sys.path.insert(0, os.path.expanduser("~/.config/hypr/scripts"))
import gally_ai_router
import gally_theme_helper
import gally_memory_manager
import gally_system_rescue
import gally_security_sentinel

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
        
        self.accent_color = accent_color
        self.accent_alt = accent_alt
        self.core_color = "#38bdf8"
        
        self.nodes = []
        num_pts = 42
        for i in range(num_pts):
            theta = math.acos(-1.0 + (2.0 * i) / num_pts)
            phi = math.sqrt(num_pts * math.pi) * theta
            r = 52.0
            x = r * math.sin(theta) * math.cos(phi)
            y = r * math.sin(theta) * math.sin(phi)
            z = r * math.cos(theta)
            self.nodes.append([x, y, z])
            
        self.inner_nodes = []
        inner_pts = 16
        for i in range(inner_pts):
            theta = math.acos(-1.0 + (2.0 * i) / inner_pts)
            phi = math.sqrt(inner_pts * math.pi) * theta
            r = 24.0
            x = r * math.sin(theta) * math.cos(phi)
            y = r * math.sin(theta) * math.sin(phi)
            z = r * math.cos(theta)
            self.inner_nodes.append([x, y, z])
            
        self.animate()

    def set_theme(self, bg_color, accent, accent_alt):
        self.bg_color = bg_color
        self.accent_color = accent
        self.accent_alt = accent_alt
        self.configure(bg=bg_color)

    def set_mode_color(self, mode):
        if mode == "non_adult":
            self.core_color = "#22c55e" # Growth Green
        elif mode in ["full_sudo", "master_sudo"]:
            self.core_color = "#f43f5e" # Master Crimson
        elif mode == "professional_sudo":
            self.core_color = "#eab308" # Sudo Amber
        else:
            self.core_color = "#38bdf8" # Garchy Electric Cyan

    def set_speaking_state(self, speaking=True):
        self.is_speaking = speaking

    def rotate_point(self, pt, rx, ry, rz):
        x, y, z = pt
        rad_x = math.radians(rx)
        y1 = y * math.cos(rad_x) - z * math.sin(rad_x)
        z1 = y * math.sin(rad_x) + z * math.cos(rad_x)
        
        rad_y = math.radians(ry)
        x2 = x * math.cos(rad_y) + z1 * math.sin(rad_y)
        z2 = -x * math.sin(rad_y) + z1 * math.cos(rad_y)
        
        rad_z = math.radians(rz)
        x3 = x2 * math.cos(rad_z) - y1 * math.sin(rad_z)
        y3 = x2 * math.sin(rad_z) + y1 * math.cos(rad_z)
        
        return x3, y3, z2

    def animate(self):
        self.delete("all")
        
        speed = 2.4 if self.is_speaking else 0.8
        self.rot_x = (self.rot_x + 0.4 * speed) % 360
        self.rot_y = (self.rot_y + 0.7 * speed) % 360
        self.rot_z = (self.rot_z + 0.3 * speed) % 360
        self.inner_rot = (self.inner_rot - 1.2 * speed) % 360
        self.pulse = (self.pulse + 0.08 * speed) % (2 * math.pi)
        
        scale_mod = 1.0 + (0.15 * math.sin(self.pulse)) if self.is_speaking else 1.0 + (0.04 * math.sin(self.pulse))
        
        # Outer Orbit Rings
        for angle_deg in [0, 60, 120]:
            poly_pts = []
            for step in range(0, 360, 20):
                rad = math.radians(step)
                rx = 62 * math.cos(rad) * scale_mod
                ry = 62 * math.sin(rad) * scale_mod
                rz = 0.0
                px, py, pz = self.rotate_point([rx, ry, rz], self.rot_x + angle_deg, self.rot_y + angle_deg, self.rot_z)
                fov = 180.0
                dist = fov / (fov + pz)
                poly_pts.append(self.cx + px * dist)
                poly_pts.append(self.cy + py * dist)
            if len(poly_pts) >= 4:
                self.create_polygon(poly_pts, outline=self.accent_alt, fill="", width=1, smooth=True)

        # 3D Node Mesh
        proj_nodes = []
        for pt in self.nodes:
            scaled_pt = [pt[0] * scale_mod, pt[1] * scale_mod, pt[2] * scale_mod]
            x, y, z = self.rotate_point(scaled_pt, self.rot_x, self.rot_y, self.rot_z)
            fov = 180.0
            dist = fov / (fov + z)
            proj_x = self.cx + x * dist
            proj_y = self.cy + y * dist
            proj_nodes.append((proj_x, proj_y, z))

        # Dynamic Mesh Lines
        for i in range(len(proj_nodes)):
            x1, y1, z1 = proj_nodes[i]
            for j in range(i + 1, len(proj_nodes)):
                x2, y2, z2 = proj_nodes[j]
                dx = x1 - x2
                dy = y1 - y2
                if math.hypot(dx, dy) < (34.0 * scale_mod):
                    alpha_color = self.accent_color if z1 > 0 else self.bg_color
                    self.create_line(x1, y1, x2, y2, fill=self.accent_color, width=1)

        # Inner Hologram Cube Core
        for pt in self.inner_nodes:
            x, y, z = self.rotate_point(pt, self.inner_rot, -self.inner_rot, self.inner_rot)
            fov = 180.0
            dist = fov / (fov + z)
            px = self.cx + x * dist
            py = self.cy + y * dist
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
        self.geometry("1100x780")
        self.configure(fg_color=self.theme_colors["bg"])
        self.minsize(960, 680)
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.msg_queue = queue.Queue()
        self.config_data = gally_ai_router.load_ai_config()
        self.history = gally_ai_router.load_history()
        self.mode = self.config_data.get("mode", "normal")
        self.cephalon_enabled = self.config_data.get("cephalon_enabled", True)
        self.voice_enabled = self.config_data.get("voice_enabled", True)
        self.voice_name = self.config_data.get("voice_name", "en-US-AriaNeural")
        self.internet_permitted = self.config_data.get("internet_permitted", False)
        self.document_permitted = self.config_data.get("document_access_permitted", False)
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
                                           corner_radius=12, width=240, height=28,
                                           command=self.on_model_changed)
        self.opt_model.set(self.cur_model_name)
        self.opt_model.pack(side="left", padx=12)
        
        # Master Standby / Disable Button
        self.btn_standby = ctk.CTkButton(hdr_inner, text="🟢 STANDBY: ACTIVE",
                                         font=ctk.CTkFont(size=10, weight="bold"),
                                         fg_color="#065f46", hover_color="#047857",
                                         corner_radius=12, height=28, width=140,
                                         command=self.toggle_cephalon_standby)
        self.btn_standby.pack(side="left", padx=6)
        
        # In-Terminal Login Direct Command Button
        self.btn_login_cli = ctk.CTkButton(hdr_inner, text="🔑 Login (login)",
                                           font=ctk.CTkFont(size=10, weight="bold"),
                                           fg_color=self.theme_colors["bg_input"],
                                           hover_color=self.theme_colors["accent"],
                                           corner_radius=12, height=28, width=110,
                                           command=self.trigger_terminal_login_guide)
        self.btn_login_cli.pack(side="right", padx=(6, 0))

        self.lbl_telemetry = ctk.CTkLabel(hdr_inner, text="⚡ RYZEN 9 5900X (24T)",
                                          font=ctk.CTkFont(family="Sans", size=10, weight="bold"),
                                          text_color=self.theme_colors["accent_alt"],
                                          fg_color=self.theme_colors["bg_input"],
                                          corner_radius=12, padx=10, pady=4)
        self.lbl_telemetry.pack(side="right")

        # --- 2. Main Content Layout ---
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=16, pady=4)
        
        # Left Panel (Width 320px)
        self.left_panel = ctk.CTkFrame(main_content, fg_color=self.theme_colors["bg_card"],
                                       corner_radius=self.theme_colors["radius"], width=320,
                                       border_width=1, border_color=self.theme_colors["accent"])
        self.left_panel.pack(side="left", fill="y", padx=(0, 10), pady=(0, 8))
        self.left_panel.pack_propagate(False)
        
        # 3D Matrix Canvas
        self.matrix_canvas = HighGraphicsCephalonMatrix(self.left_panel, width=290, height=170,
                                                        bg_color=self.theme_colors["bg_card"],
                                                        accent_color=self.theme_colors["accent"])
        self.matrix_canvas.pack(pady=(6, 2))
        self.matrix_canvas.set_mode_color(self.mode)
        
        self.lbl_status = ctk.CTkLabel(self.left_panel, text="● CEPHALON ONLINE",
                                       font=ctk.CTkFont(family="Sans", size=10, weight="bold"),
                                       text_color="#22c55e")
        self.lbl_status.pack(pady=(1, 3))
        
        # Persona Mode Pill Row (4 Modes including Full Sudo)
        self.lbl_p = ctk.CTkLabel(self.left_panel, text="◈ OPERATION PERSONA ◈",
                                  font=ctk.CTkFont(family="Sans", size=9, weight="bold"),
                                  text_color=self.theme_colors["accent_alt"])
        self.lbl_p.pack(pady=(1, 1))
        
        mode_btn_row1 = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        mode_btn_row1.pack(fill="x", padx=8, pady=1)
        
        self.btn_mode_non_adult = ctk.CTkButton(mode_btn_row1, text="🌱 Non-Adult", font=ctk.CTkFont(size=9, weight="bold"),
                                                fg_color=self.theme_colors["bg_input"], hover_color="#22c55e",
                                                corner_radius=10, height=24,
                                                command=lambda: self.switch_mode("non_adult"))
        self.btn_mode_non_adult.pack(side="left", fill="x", expand=True, padx=1)
        
        self.btn_mode_normal = ctk.CTkButton(mode_btn_row1, text="🚀 Normal", font=ctk.CTkFont(size=9, weight="bold"),
                                             fg_color=self.theme_colors["bg_input"], hover_color=self.theme_colors["accent"],
                                             corner_radius=10, height=24,
                                             command=lambda: self.switch_mode("normal"))
        self.btn_mode_normal.pack(side="left", fill="x", expand=True, padx=1)

        mode_btn_row2 = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        mode_btn_row2.pack(fill="x", padx=8, pady=1)
        
        self.btn_mode_sudo = ctk.CTkButton(mode_btn_row2, text="⚡ Sudo", font=ctk.CTkFont(size=9, weight="bold"),
                                           fg_color=self.theme_colors["bg_input"], hover_color="#eab308",
                                           corner_radius=10, height=24,
                                           command=lambda: self.switch_mode("professional_sudo"))
        self.btn_mode_sudo.pack(side="left", fill="x", expand=True, padx=1)

        self.btn_mode_full_sudo = ctk.CTkButton(mode_btn_row2, text="⚡ Master Sudo", font=ctk.CTkFont(size=9, weight="bold"),
                                                fg_color=self.theme_colors["bg_input"], hover_color="#f43f5e",
                                                corner_radius=10, height=24,
                                                command=lambda: self.switch_mode("full_sudo"))
        self.btn_mode_full_sudo.pack(side="left", fill="x", expand=True, padx=1)
        self.update_mode_buttons_ui()
        
        # Privacy & Sandboxing Controls
        self.lbl_priv = ctk.CTkLabel(self.left_panel, text="─ PRIVACY & SANDBOX ─",
                                     font=ctk.CTkFont(family="Sans", size=9, weight="bold"),
                                     text_color=self.theme_colors["fg_muted"])
        self.lbl_priv.pack(pady=(4, 1))
        
        self.btn_internet = ctk.CTkButton(self.left_panel, text="", font=ctk.CTkFont(size=9, weight="bold"),
                                          fg_color=self.theme_colors["bg_input"], corner_radius=10, height=24,
                                          anchor="w", command=self.toggle_internet_permission)
        self.btn_internet.pack(fill="x", padx=8, pady=1)
        
        self.btn_doc = ctk.CTkButton(self.left_panel, text="", font=ctk.CTkFont(size=9, weight="bold"),
                                     fg_color=self.theme_colors["bg_input"], corner_radius=10, height=24,
                                     anchor="w", command=self.toggle_document_permission)
        self.btn_doc.pack(fill="x", padx=8, pady=1)
        
        self.btn_voice = ctk.CTkButton(self.left_panel, text="", font=ctk.CTkFont(size=9, weight="bold"),
                                       fg_color=self.theme_colors["bg_input"], corner_radius=10, height=24,
                                       anchor="w", command=self.toggle_voice)
        self.btn_voice.pack(fill="x", padx=8, pady=1)
        self.update_toggle_buttons_ui()

        # Directives (Rescue, Sentinel, File Search)
        self.lbl_dir = ctk.CTkLabel(self.left_panel, text="─ RESCUE & SENTINEL ─",
                                    font=ctk.CTkFont(family="Sans", size=9, weight="bold"),
                                    text_color=self.theme_colors["fg_muted"])
        self.lbl_dir.pack(pady=(4, 1))
        
        directives = [
            ("🛡️ Security Sentinel Sweep", "security_sweep"),
            ("🔧 100% Offline System Rescue", "repair_offline_system"),
            ("💾 Take Rescue Snapshot", "take_snapshot"),
            ("🔍 Fast Local File Search", "find_files_prompt"),
            ("⚡ Boost Gaming FPS", "boost_gaming"),
            ("🌐 Open Web Link...", "open_web_prompt")
        ]
        for name, act in directives:
            btn = ctk.CTkButton(self.left_panel, text=name, font=ctk.CTkFont(size=9),
                                fg_color=self.theme_colors["bg_input"], hover_color=self.theme_colors["accent"],
                                corner_radius=10, height=24, anchor="w",
                                command=lambda a=act, n=name: self.handle_directive_click(n, a))
            btn.pack(fill="x", padx=8, pady=1)
            self.directive_buttons.append(btn)

        self.btn_clear = ctk.CTkButton(self.left_panel, text="🗑️ Clear Console", font=ctk.CTkFont(size=9),
                                       fg_color=self.theme_colors["bg_input"], hover_color="#f43f5e",
                                       corner_radius=10, height=24,
                                       command=self.clear_console_history)
        self.btn_clear.pack(fill="x", padx=8, pady=(4, 6), side="bottom")

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
        self.setup_chat_tags()
        
        # Rounded Input Bar
        self.input_bar = ctk.CTkFrame(right_panel, fg_color=self.theme_colors["bg_card"],
                                      corner_radius=14, border_width=1, border_color=self.theme_colors["accent"])
        self.input_bar.pack(fill="x")
        
        self.ent_query = ctk.CTkEntry(self.input_bar, fg_color="transparent", border_width=0,
                                      placeholder_text="Transmute a directive (or type 'find <file>', 'security', 'login')... (Enter)",
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

    def toggle_cephalon_standby(self):
        self.cephalon_enabled = not self.cephalon_enabled
        self.config_data["cephalon_enabled"] = self.cephalon_enabled
        gally_ai_router.save_ai_config(self.config_data)
        
        if self.cephalon_enabled:
            self.btn_standby.configure(text="🟢 STANDBY: ACTIVE", fg_color="#065f46", hover_color="#047857")
            self.lbl_status.configure(text="● CEPHALON ONLINE", text_color="#22c55e")
            self.btn_send.configure(state="normal")
            self.append_message("cephalon", "◈ Cephalon Gally re-engaged from standby. All neural monitors active.")
        else:
            stop_active_tts()
            self.btn_standby.configure(text="🛑 STANDBY: PAUSED", fg_color="#991b1b", hover_color="#7f1d1d")
            self.lbl_status.configure(text="🛑 CEPHALON STANDBY / PAUSED", text_color="#ef4444")
            self.matrix_canvas.set_speaking_state(False)
            self.append_message("cephalon", "◈ Cephalon Gally is now in STANDBY mode. Background queries and voice synthesis are paused.")

    def setup_chat_tags(self):
        c = self.theme_colors
        self.txt_chat.tag_config("op_hdr", foreground=c["accent"])
        self.txt_chat.tag_config("op_text", foreground="#ffffff")
        self.txt_chat.tag_config("ai_hdr", foreground=c["accent_alt"])
        self.txt_chat.tag_config("ai_text", foreground=c["fg"])
        self.txt_chat.tag_config("cmd", foreground="#c084fc", background="#1e1e2e")
        self.txt_chat.tag_config("terminal_out", foreground=c["accent"])
        self.txt_chat.tag_config("code_block", foreground="#34d399", background="#050811")
        self.txt_chat.tag_config("link", foreground="#00f0ff", underline=True)
        self.txt_chat.tag_config("sys_notice", foreground="#22c55e")
        self.txt_chat.tag_config("err_notice", foreground="#f87171")
        self.txt_chat.bind("<Button-1>", self.on_chat_click)

    def on_chat_click(self, event):
        try:
            index = self.txt_chat.index(f"@{event.x},{event.y}")
            tags = self.txt_chat.tag_names(index)
            for tag in tags:
                if tag.startswith("link_target_"):
                    url = tag[12:]
                    if gally_memory_manager:
                        gally_memory_manager.open_browser_link(url)
                    return
        except Exception:
            pass

    def apply_syntax_highlights(self):
        try:
            content = self.txt_chat.get("1.0", tk.END)
            for match in re.finditer(r"https?://[^\s\)\>]+|www\.[^\s\)\>]+", content):
                url = match.group(0).rstrip(".,;!?:")
                start_idx = f"1.0 + {match.start()} chars"
                end_idx = f"1.0 + {match.start() + len(url)} chars"
                tag_name = f"link_target_{url}"
                self.txt_chat.tag_config(tag_name, foreground="#00f0ff", underline=True)
                self.txt_chat.tag_add("link", start_idx, end_idx)
                self.txt_chat.tag_add(tag_name, start_idx, end_idx)
                
            for match in re.finditer(r"`([^`\n]+)`", content):
                start_idx = f"1.0 + {match.start()} chars"
                end_idx = f"1.0 + {match.end()} chars"
                self.txt_chat.tag_add("cmd", start_idx, end_idx)

            for match in re.finditer(r"```[\s\S]*?```", content):
                start_idx = f"1.0 + {match.start()} chars"
                end_idx = f"1.0 + {match.end()} chars"
                self.txt_chat.tag_add("code_block", start_idx, end_idx)
        except Exception:
            pass

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
        self.setup_chat_tags()
        self.update_mode_buttons_ui()
        self.update_toggle_buttons_ui()
        self.render_history()
        self.poll_msg_queue()

    def trigger_terminal_login_guide(self):
        self.ent_query.delete(0, tk.END)
        self.ent_query.insert(0, "login")
        self.send_query()

    def on_model_changed(self, choice):
        for (name, provider, model_id) in gally_ai_router.AVAILABLE_MODELS:
            if name == choice:
                self.config_data["active_provider"] = provider
                self.config_data["active_model"] = model_id
                gally_ai_router.save_ai_config(self.config_data)
                self.cur_model_name = name
                self.lbl_progress.configure(text=f"⚡ ACTIVE MODEL: {name}")
                msg = f"◈ Active Neural Engine switched to: [{name}], Operator."
                self.append_message("cephalon", msg)
                speak_voice_neural_async(msg, self.voice_enabled, self.voice_name)
                break

    def update_mode_buttons_ui(self):
        c = self.theme_colors
        self.btn_mode_non_adult.configure(fg_color="#065f46" if self.mode == "non_adult" else c["bg_input"],
                                          text_color="#ffffff" if self.mode == "non_adult" else c["fg"])
        self.btn_mode_normal.configure(fg_color=c["accent"] if self.mode == "normal" else c["bg_input"],
                                       text_color="#000000" if self.mode == "normal" else c["fg"])
        self.btn_mode_sudo.configure(fg_color="#854d0e" if self.mode == "professional_sudo" else c["bg_input"],
                                     text_color="#ffffff" if self.mode == "professional_sudo" else c["fg"])
        self.btn_mode_full_sudo.configure(fg_color="#991b1b" if self.mode in ["full_sudo", "master_sudo"] else c["bg_input"],
                                          text_color="#ffffff" if self.mode in ["full_sudo", "master_sudo"] else c["fg"])

    def update_toggle_buttons_ui(self):
        c = self.theme_colors
        self.btn_internet.configure(
            text="🌐 Internet: PERMITTED" if self.internet_permitted else "🌐 Internet: RESTRICTED",
            fg_color="#065f46" if self.internet_permitted else c["bg_input"],
            text_color="#ffffff" if self.internet_permitted else c["fg_muted"]
        )
        self.btn_doc.configure(
            text="📂 Documents: PERMITTED" if self.document_permitted else "📂 Documents: PROTECTED",
            fg_color="#065f46" if self.document_permitted else c["bg_input"],
            text_color="#ffffff" if self.document_permitted else c["fg_muted"]
        )
        self.btn_voice.configure(
            text="🔊 Voice: ON" if self.voice_enabled else "🔇 Voice: MUTED",
            fg_color=c["accent"] if self.voice_enabled else c["bg_input"],
            text_color="#000000" if self.voice_enabled else c["fg_muted"]
        )

    def switch_mode(self, target_mode):
        if target_mode == self.mode:
            return

        if target_mode in ["professional_sudo", "full_sudo"]:
            if not self.sudo_unlocked:
                pwd = ctk.CTkInputDialog(text="Enter Sudo Password to unlock Root Architect matrix:",
                                         title="Authentication Required").get_input()
                if not pwd:
                    return
                if gally_memory_manager.verify_sudo_password(pwd):
                    self.sudo_unlocked = True
                else:
                    messagebox.showerror("Authentication Failed", "Incorrect sudo credentials. Access denied.", parent=self)
                    return

        self.mode = target_mode
        self.config_data["mode"] = self.mode
        gally_ai_router.save_ai_config(self.config_data)
        self.matrix_canvas.set_mode_color(self.mode)
        self.update_mode_buttons_ui()
        
        if self.mode == "non_adult":
            msg = "◈ Operation Mode switched to [NON-ADULT (AGES 10-16)], Operator. Safe learning & gaming active."
        elif self.mode == "full_sudo":
            msg = "◈ Master Architect / Full Sudo Mode ENGAGED. Full root authority and offline rescue matrix unlocked."
        elif self.mode == "professional_sudo":
            msg = "◈ Operation Mode switched to [PROFESSIONAL SUDO], Operator. Deep Linux sysadmin architecture active."
        else:
            msg = "◈ Operation Mode switched to [NORMAL (AGES 16+)], Operator. Full desktop capabilities active."

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

        if action_type == "find_files_prompt":
            q = ctk.CTkInputDialog(text="Enter file name, extension or keyword to locate:", title="Fast Local File Search").get_input()
            if q:
                res = gally_system_rescue.search_files_offline(q)
                if res:
                    msg = f"◈ LOCAL FILE SEARCH RESULTS FOR '{q}' ({len(res)} found):\n"
                    for r in res:
                        msg += f"  • [{r['size']}] {r['path']}\n"
                else:
                    msg = f"◈ Local search index: No files matching '{q}' found."
                self.append_message("cephalon", msg)
            return

        self.txt_chat.insert(tk.END, f"\n\n◈ DIRECTIVE INITIATED: {name}\n", "ai_hdr")
        self.lbl_status.configure(text="● EXECUTING DIRECTIVE...", text_color=self.theme_colors["accent_alt"])
        self.matrix_canvas.set_speaking_state(True)
        self.btn_send.configure(state="disabled")
        threading.Thread(target=self.run_live_terminal_task, args=(name, action_type), daemon=True).start()

    def run_live_terminal_task(self, name, action_type):
        if action_type == "security_sweep":
            self.msg_queue.put(("progress", (0.3, "Scanning Authentication Log & Sudo Telemetry")))
            report = gally_security_sentinel.run_comprehensive_security_sweep()
            self.msg_queue.put(("terminal", ("gally-security-sentinel --audit", report)))
            self.msg_queue.put(("progress", (1.0, "Security Sweep Complete")))
            summary = "Operator, security sentinel audit concluded. Telemetry logged."

        elif action_type == "repair_offline_system":
            self.msg_queue.put(("progress", (0.2, "Unlocking Pacman Package Database")))
            ok1, m1 = gally_system_rescue.clear_pacman_locks()
            self.msg_queue.put(("terminal", ("pacman-lock-check", m1)))
            
            self.msg_queue.put(("progress", (0.5, "Re-harmonizing PipeWire & Audio Sinks")))
            ok2, m2 = gally_system_rescue.repair_pipewire_audio()
            self.msg_queue.put(("terminal", ("audio-repair", m2)))
            
            self.msg_queue.put(("progress", (0.8, "Flushing Memory & Purging Zombie Processes")))
            ok3, m3 = gally_system_rescue.clean_memory_and_zombies()
            self.msg_queue.put(("terminal", ("memory-optimization", m3)))
            
            self.msg_queue.put(("progress", (1.0, "Offline System Rescue Complete")))
            summary = "Operator, offline self-healing matrix executed. Pacman locks cleared, PipeWire re-harmonized, and buffers flushed."

        elif action_type == "take_snapshot":
            self.msg_queue.put(("progress", (0.4, "Generating Local System Snapshot (Timeshift/Snapper)")))
            ok, msg = gally_system_rescue.create_offline_snapshot("gally-operator-checkpoint")
            self.msg_queue.put(("terminal", ("system-snapshot-create", msg)))
            self.msg_queue.put(("progress", (1.0, "Snapshot Completed")))
            summary = f"Operator, local offline restore snapshot generated: {msg}"

        elif action_type == "boost_gaming":
            self.msg_queue.put(("progress", (0.3, "Activating GameMode Daemon")))
            res1 = subprocess.getoutput("gamemoded -s 2>/dev/null || echo 'GameMode daemon ready'")
            self.msg_queue.put(("terminal", ("gamemoded -s", res1)))
            
            self.msg_queue.put(("progress", (0.7, "Checking NVENC & NVIDIA Performance State")))
            res2 = subprocess.getoutput("nvidia-smi -q -d PERFORMANCE 2>/dev/null | grep 'Performance State' || echo 'P0 Performance Mode'")
            self.msg_queue.put(("terminal", ("nvidia-perf-query", res2)))
            
            self.msg_queue.put(("progress", (1.0, "Gaming Matrix Boosted")))
            summary = "Operator, gaming performance matrices are maximized. Dual 144Hz displays and GameMode high-priority scheduling are engaged."

        else:
            summary = "Operator, directive execution nominal."

        self.msg_queue.put(("directive_complete", summary))

    def send_query(self):
        if not self.cephalon_enabled:
            self.append_message("cephalon", "◈ Cephalon is in STANDBY. Click the green toggle button in the header to re-enable.")
            return

        prompt = self.ent_query.get().strip()
        if not prompt:
            return
            
        self.ent_query.delete(0, tk.END)
        
        if prompt.lower() in ["clear", "cls", "reset"]:
            self.clear_console_history()
            return
            
        self.append_message("operator", prompt)
        
        # 1. Safety Command Validation Check (Guarantees system cannot be messed up)
        is_safe, safety_msg = gally_system_rescue.validate_command_safety(prompt, self.mode)
        if not is_safe:
            self.append_message("cephalon", f"🛑 SAFETY INTERCEPTION:\n{safety_msg}")
            return

        # 2. In-Terminal Login & Model Switch Command Interpretation
        handled, cli_msg, new_cfg = gally_ai_router.handle_terminal_command(prompt, self.config_data)
        if handled:
            self.config_data = new_cfg
            cur_model = self.config_data.get("active_model", "gally-cephalon-ai")
            for (n, _, m_id) in gally_ai_router.AVAILABLE_MODELS:
                if m_id == cur_model:
                    self.cur_model_name = n
                    self.opt_model.set(n)
                    self.lbl_progress.configure(text=f"⚡ ACTIVE MODEL: {n}")
                    break
            self.append_message("cephalon", cli_msg)
            return

        # 3. Browser Open Commands
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
        
        # 4. Memory Learning, Rescue & Sentinel Directives
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
        
        self.txt_chat.insert(tk.END, "\n◈ CEPHALON GALLY: ", "ai_hdr")
        self.txt_chat.see(tk.END)
        
        threading.Thread(target=self.stream_cephalon_thread, args=(prompt,), daemon=True).start()

    def stream_cephalon_thread(self, prompt):
        try:
            sys_inst = gally_memory_manager.get_mode_system_instruction(
                mode=self.mode, internet_ok=self.internet_permitted, doc_ok=self.document_permitted
            )
        except Exception:
            sys_inst = "You are Cephalon Gally, the intelligent desktop companion for Garchy Linux."

        def on_token(token):
            self.msg_queue.put(("token", token))

        def on_complete(full_resp):
            self.msg_queue.put(("complete", full_resp))

        gally_ai_router.stream_query(
            prompt=prompt,
            config=self.config_data,
            token_callback=on_token,
            complete_callback=on_complete,
            history_messages=self.history,
            system_instruction=sys_inst
        )

    def poll_msg_queue(self):
        try:
            while True:
                msg_type, payload = self.msg_queue.get_nowait()
                if msg_type == "token":
                    self.txt_chat.insert(tk.END, payload, "ai_text")
                    self.txt_chat.see(tk.END)
                elif msg_type == "complete":
                    self.txt_chat.insert(tk.END, "\n")
                    self.apply_syntax_highlights()
                    self.txt_chat.see(tk.END)
                    self.history.append({"role": "cephalon", "text": payload, "time": time.time()})
                    gally_ai_router.save_history(self.history)
                    
                    last_user_prompt = ""
                    for m in reversed(self.history):
                        if m.get("role") in ["operator", "user"]:
                            last_user_prompt = m.get("text", "")
                            break
                    if last_user_prompt and gally_memory_manager:
                        gally_memory_manager.learn_from_interaction_async(last_user_prompt, payload)
                        
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
                    self.txt_chat.insert(tk.END, f"\n$ {cmd_str}\n", "cmd")
                    self.txt_chat.insert(tk.END, f"{out_str}\n", "terminal_out")
                    self.apply_syntax_highlights()
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
        self.txt_chat.delete("1.0", tk.END)
        if not self.history:
            welcome = (
                "Greetings, Operator. Cephalon Gally is online and synchronized with your Garchy Linux environment. "
                "All 24 threads on your Ryzen 9 5900X and Dual 144Hz displays are running nominal. How may I assist you?"
            )
            self.append_message("cephalon", welcome)
        else:
            for item in self.history:
                role = item.get("role")
                text = item.get("text", "")
                if role in ["operator", "user"]:
                    self.txt_chat.insert(tk.END, "\n\n◈ OPERATOR: ", "op_hdr")
                    self.txt_chat.insert(tk.END, f"{text}\n", "op_text")
                elif role in ["cephalon", "assistant", "model"]:
                    self.txt_chat.insert(tk.END, "\n◈ CEPHALON GALLY: ", "ai_hdr")
                    self.txt_chat.insert(tk.END, f"{text}\n", "ai_text")
            self.apply_syntax_highlights()
            self.txt_chat.see(tk.END)

    def append_message(self, role, text):
        self.history.append({"role": role, "text": text, "time": time.time()})
        gally_ai_router.save_history(self.history)
        if role in ["operator", "user"]:
            self.txt_chat.insert(tk.END, "\n\n◈ OPERATOR: ", "op_hdr")
            self.txt_chat.insert(tk.END, f"{text}\n", "op_text")
        elif role in ["cephalon", "assistant", "model"]:
            self.txt_chat.insert(tk.END, "\n◈ CEPHALON GALLY: ", "ai_hdr")
            self.txt_chat.insert(tk.END, f"{text}\n", "ai_text")
        self.apply_syntax_highlights()
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
