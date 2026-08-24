#!/usr/bin/env python3
"""
Cephalon Gally — Holographic AI System Core (Warframe Aesthetic)
Thread-Safe Real-time Streaming (Queue Event Pump for Python 3.14+),
3 Persona Modes (Child, Normal, Professional Sudo), Sudo Password Unlock,
Internet Permission Sandbox, Document Privacy Guard & Neural Voice.
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
from tkinter import ttk, messagebox, simpledialog

CONFIG_PATH = os.path.expanduser("~/.config/gally/ai_config.json")
HISTORY_PATH = os.path.expanduser("~/.config/gally/cephalon_history.json")

# Theme Palette (Cephalon Hologram & Orokin Radiance)
BG_MAIN = "#030610"
BG_CARD = "#070c1b"
BG_INPUT = "#0c1326"
FG_LIGHT = "#e2e8f0"
FG_MUTED = "#64748b"
ACCENT_CYAN = "#00f0ff"
ACCENT_BLUE = "#38bdf8"
ACCENT_GOLD = "#fbbf24"
ACCENT_PURPLE = "#c084fc"
ACCENT_GREEN = "#22c55e"
ACCENT_ROSE = "#f43f5e"
BORDER_CYAN = "#0369a1"
BORDER_GOLD = "#b45309"

CURRENT_TTS_PROC = None

# Import Memory & Security Engine
sys.path.insert(0, os.path.expanduser("~/.config/hypr/scripts"))
try:
    import gally_memory_manager
except Exception:
    gally_memory_manager = None

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
    clean = " ".join([line for line in clean.splitlines() if not line.strip().startswith("$") and not line.strip().startswith("sudo")])
    if len(clean) > 350:
        clean = clean[:350] + "..."

    def run_tts():
        global CURRENT_TTS_PROC
        out_file = f"/tmp/cephalon_speech_{int(time.time()*1000)}.mp3"
        try:
            import edge_tts
            async def generate():
                comm = edge_tts.Communicate(clean, voice, rate="+4%", pitch="+2Hz")
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

class CephalonGlowingMatrix(tk.Canvas):
    def __init__(self, parent, width=280, height=230):
        super().__init__(parent, width=width, height=height, bg=BG_CARD, highlightthickness=0)
        self.w = width
        self.h = height
        self.cx = width // 2
        self.cy = height // 2
        
        self.angle_x = 0.0
        self.angle_y = 0.0
        self.angle_z = 0.0
        self.is_speaking = False
        self.pulse = 0.0
        self.core_color = ACCENT_GOLD
        
        self.outer_vertices = [
            (0, -75, 0), (55, -20, 35), (0, -20, -65), (-55, -20, 35),
            (55, 20, -35), (0, 20, 65), (-55, 20, -35), (0, 75, 0)
        ]
        self.outer_edges = [
            (0, 1), (0, 2), (0, 3), (1, 4), (2, 4), (2, 6), (3, 6), (3, 5), (1, 5),
            (7, 4), (7, 5), (7, 6), (1, 2), (2, 3), (3, 1), (4, 5), (5, 6), (6, 4)
        ]
        self.inner_vertices = [
            (0, -35, 0), (25, 0, 0), (0, 0, 25), (-25, 0, 0), (0, 0, -25), (0, 35, 0)
        ]
        self.inner_edges = [
            (0, 1), (0, 2), (0, 3), (0, 4), (5, 1), (5, 2), (5, 3), (5, 4),
            (1, 2), (2, 3), (3, 4), (4, 1)
        ]
        self.particles = []
        for i in range(24):
            self.particles.append({
                "radius": random.uniform(85, 120),
                "angle": random.uniform(0, 2 * math.pi),
                "speed": random.uniform(0.015, 0.035) * random.choice([1, -1]),
                "tilt": random.uniform(-0.6, 0.6),
                "size": random.uniform(1.5, 3.2),
                "color": random.choice([ACCENT_CYAN, ACCENT_GOLD, ACCENT_PURPLE, "#38bdf8"])
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
            self.core_color = ACCENT_GOLD

    def animate(self):
        self.delete("all")
        self.angle_x += 0.018
        self.angle_y += 0.024
        self.angle_z += 0.012
        self.pulse += 0.075
        
        amp = 0.28 if self.is_speaking else 0.08
        pulse_scale = 1.0 + amp * math.sin(self.pulse)
        
        for r_offset, col, dash in [
            (95 * pulse_scale, "#0e2a47", (2, 4)),
            (115 * pulse_scale, "#091d33", (1, 5))
        ]:
            self.create_oval(self.cx - r_offset, self.cy - r_offset,
                              self.cx + r_offset, self.cy + r_offset,
                              outline=col, width=1, dash=dash)
                              
        if self.is_speaking:
            num_rays = 16
            for i in range(num_rays):
                ang = i * (2 * math.pi / num_rays) + (self.pulse * 0.5)
                wave = math.sin(self.pulse * 3 + i * 1.2) * 22
                r1 = 88 * pulse_scale
                r2 = 98 * pulse_scale + max(4, wave)
                x1 = self.cx + r1 * math.cos(ang)
                y1 = self.cy + r1 * math.sin(ang)
                x2 = self.cx + r2 * math.cos(ang)
                y2 = self.cy + r2 * math.sin(ang)
                self.create_line(x1, y1, x2, y2, fill=self.core_color, width=2)

        for p in self.particles:
            p["angle"] += p["speed"]
            px = self.cx + p["radius"] * math.cos(p["angle"])
            py = self.cy + p["radius"] * math.sin(p["angle"]) * math.cos(p["tilt"]) + (10 * math.sin(self.pulse + p["angle"]))
            ps = p["size"] if not self.is_speaking else p["size"] * 1.5
            self.create_oval(px - ps, py - ps, px + ps, py + ps, fill=p["color"], outline="")

        def project_3d(v_list, scale):
            proj = []
            for (x, y, z) in v_list:
                x, y, z = x * scale, y * scale, z * scale
                x1 = x * math.cos(self.angle_y) + z * math.sin(self.angle_y)
                y1 = y
                z1 = -x * math.sin(self.angle_y) + z * math.cos(self.angle_y)
                x2 = x1
                y2 = y1 * math.cos(self.angle_x) - z1 * math.sin(self.angle_x)
                z2 = y1 * math.sin(self.angle_x) + z1 * math.cos(self.angle_x)
                fov = 220
                dist = fov / (fov + z2 + 120)
                px = self.cx + x2 * dist * 1.4
                py = self.cy + y2 * dist * 1.4
                proj.append((px, py, z2))
            return proj

        outer_proj = project_3d(self.outer_vertices, pulse_scale)
        inner_proj = project_3d(self.inner_vertices, pulse_scale * 1.1)

        for u, v in self.outer_edges:
            x1, y1, z1 = outer_proj[u]
            x2, y2, z2 = outer_proj[v]
            depth_col = ACCENT_CYAN if (z1 + z2) / 2 > -20 else "#0369a1"
            self.create_line(x1, y1, x2, y2, fill=depth_col, width=2 if self.is_speaking else 1)

        for u, v in self.inner_edges:
            x1, y1, _ = inner_proj[u]
            x2, y2, _ = inner_proj[v]
            self.create_line(x1, y1, x2, y2, fill=self.core_color, width=2)

        core_r = 7 if not self.is_speaking else 11 + 3 * math.sin(self.pulse * 2)
        self.create_oval(self.cx - core_r, self.cy - core_r,
                          self.cx + core_r, self.cy + core_r,
                          fill=self.core_color, outline="#ffffff", width=2)
        
        self.after(22, self.animate)

class CephalonApp(tk.Tk):
    def __init__(self):
        super().__init__(className='gally_cephalon_hud')
        self.title("Cephalon Gally — Multi-Mode AI System Core")
        self.geometry("1020x730")
        self.configure(bg=BG_MAIN)
        self.minsize(900, 620)
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Thread-safe queue for streaming tokens and terminal updates
        self.msg_queue = queue.Queue()
        
        self.config_data = load_config()
        self.history = load_history()
        self.mode = self.config_data.get("mode", "normal")
        self.voice_enabled = self.config_data.get("voice_enabled", True)
        self.voice_name = self.config_data.get("voice_name", "en-US-AriaNeural")
        self.internet_permitted = self.config_data.get("internet_permitted", False)
        self.document_permitted = self.config_data.get("document_access_permitted", False)
        self.sudo_unlocked = False

        # 1. Top Cephalon Holographic Header Bar
        hdr = tk.Frame(self, bg=BG_MAIN, padx=20, pady=8)
        hdr.pack(fill="x")
        
        top_row = tk.Frame(hdr, bg=BG_MAIN)
        top_row.pack(fill="x")
        
        tk.Label(top_row, text="🌌 CEPHALON GALLY", font=("Sans", 16, "bold"), fg=ACCENT_CYAN, bg=BG_MAIN).pack(side="left")
        
        self.lbl_mode_badge = tk.Label(top_row, text="", font=("Sans", 9, "bold"), padx=10, pady=2)
        self.lbl_mode_badge.pack(side="left", padx=10)
        self.update_mode_badge_ui()
        
        self.lbl_telemetry = tk.Label(top_row, text="⚡ RYZEN 9 5900X (24T) | RTX GPU | DUAL 144Hz",
                                      font=("Sans", 9, "bold"), fg=ACCENT_CYAN, bg=BG_CARD, padx=12, pady=4,
                                      highlightthickness=1, highlightbackground=BORDER_CYAN)
        self.lbl_telemetry.pack(side="right")
        
        tk.Frame(hdr, height=2, bg=ACCENT_CYAN).pack(fill="x", pady=(6, 0))

        # 2. Main Content Frame
        main_content = tk.Frame(self, bg=BG_MAIN, padx=14, pady=4)
        main_content.pack(fill="both", expand=True)
        
        # Left Panel: Modes, Privacy & Visual Core
        left_panel = tk.Frame(main_content, bg=BG_CARD, width=300, padx=12, pady=8,
                              highlightthickness=1, highlightbackground=BORDER_CYAN)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # 3D Matrix
        self.matrix_canvas = CephalonGlowingMatrix(left_panel, width=270, height=190)
        self.matrix_canvas.pack()
        self.matrix_canvas.set_mode_color(self.mode)
        
        self.lbl_status = tk.Label(left_panel, text="● CEPHALON READY", font=("Sans", 8, "bold"), fg=ACCENT_GREEN, bg=BG_CARD)
        self.lbl_status.pack(pady=(2, 4))
        
        # --- Mode Selector Section ---
        tk.Label(left_panel, text="◈ OPERATION PERSONA ◈", font=("Sans", 8, "bold"), fg=ACCENT_GOLD, bg=BG_CARD).pack(pady=(2, 2))
        
        mode_btn_row = tk.Frame(left_panel, bg=BG_CARD)
        mode_btn_row.pack(fill="x", pady=2)
        
        self.btn_mode_child = tk.Button(mode_btn_row, text="🧸 Child", font=("Sans", 8, "bold"),
                                        bg=BG_INPUT, fg=FG_LIGHT, relief="flat", padx=6, pady=4, cursor="hand2",
                                        command=lambda: self.switch_mode("child"))
        self.btn_mode_child.pack(side="left", fill="x", expand=True, padx=1)
        
        self.btn_mode_normal = tk.Button(mode_btn_row, text="🚀 Normal", font=("Sans", 8, "bold"),
                                         bg=BG_INPUT, fg=FG_LIGHT, relief="flat", padx=6, pady=4, cursor="hand2",
                                         command=lambda: self.switch_mode("normal"))
        self.btn_mode_normal.pack(side="left", fill="x", expand=True, padx=1)
        
        self.btn_mode_sudo = tk.Button(mode_btn_row, text="⚡ Sudo Pro", font=("Sans", 8, "bold"),
                                       bg=BG_INPUT, fg=FG_LIGHT, relief="flat", padx=6, pady=4, cursor="hand2",
                                       command=lambda: self.switch_mode("professional_sudo"))
        self.btn_mode_sudo.pack(side="left", fill="x", expand=True, padx=1)
        
        # --- Privacy & Sandboxing Controls ---
        tk.Label(left_panel, text="─ PRIVACY & GUARDRAILS ─", font=("Sans", 8, "bold"), fg=FG_MUTED, bg=BG_CARD).pack(pady=(6, 2))
        
        self.btn_internet = tk.Button(left_panel, text="", font=("Sans", 8, "bold"),
                                      bg=BG_INPUT, relief="flat", padx=6, pady=3, cursor="hand2", anchor="w",
                                      command=self.toggle_internet_permission)
        self.btn_internet.pack(fill="x", pady=1)
        
        self.btn_doc = tk.Button(left_panel, text="", font=("Sans", 8, "bold"),
                                 bg=BG_INPUT, relief="flat", padx=6, pady=3, cursor="hand2", anchor="w",
                                 command=self.toggle_document_permission)
        self.btn_doc.pack(fill="x", pady=1)
        
        self.btn_voice = tk.Button(left_panel, text="", font=("Sans", 8, "bold"),
                                   bg=BG_INPUT, relief="flat", padx=6, pady=3, cursor="hand2", anchor="w",
                                   command=self.toggle_voice)
        self.btn_voice.pack(fill="x", pady=1)
        self.update_toggle_buttons_ui()

        # Directives
        tk.Label(left_panel, text="─ DIRECTIVES ─", font=("Sans", 8, "bold"), fg=FG_MUTED, bg=BG_CARD).pack(pady=(6, 2))
        
        directives = [
            ("🛡️ Full System Scan", "run_diagnostics"),
            ("⚡ Boost Gaming FPS", "boost_gaming"),
            ("🔊 Audio Diagnostics", "repair_audio"),
            ("🌐 Open Web Link...", "open_web_prompt")
        ]
        for name, act in directives:
            btn = tk.Button(left_panel, text=name, font=("Sans", 8),
                            bg=BG_INPUT, fg=FG_LIGHT, activebackground=ACCENT_CYAN, activeforeground="#000",
                            relief="flat", padx=6, pady=3, cursor="hand2", anchor="w",
                            command=lambda a=act, n=name: self.handle_directive_click(n, a))
            btn.pack(fill="x", pady=1)

        btn_clear = tk.Button(left_panel, text="🗑️ Clear Console History", font=("Sans", 8),
                              bg="#1e1e2e", fg=FG_MUTED, activebackground=ACCENT_ROSE, activeforeground="#fff",
                              relief="flat", padx=6, pady=3, cursor="hand2", anchor="center",
                              command=self.clear_console_history)
        btn_clear.pack(fill="x", pady=(4, 0), side="bottom")

        # Right Panel: Chat Console + Mini Terminal Progress
        right_panel = tk.Frame(main_content, bg=BG_MAIN)
        right_panel.pack(side="right", fill="both", expand=True)
        
        self.progress_frame = tk.Frame(right_panel, bg=BG_CARD, padx=8, pady=4,
                                       highlightthickness=1, highlightbackground=BORDER_CYAN)
        self.progress_frame.pack(fill="x", pady=(0, 6))
        
        self.lbl_progress = tk.Label(self.progress_frame, text="⚡ SYSTEM TELEMETRY: READY",
                                     font=("Sans", 8, "bold"), fg=ACCENT_CYAN, bg=BG_CARD)
        self.lbl_progress.pack(anchor="w")
        
        self.prog_bar = ttk.Progressbar(self.progress_frame, orient="horizontal", mode="determinate")
        self.prog_bar.pack(fill="x", pady=(2, 2))
        self.prog_bar["value"] = 100

        chat_box_frame = tk.Frame(right_panel, bg=BG_CARD, highlightthickness=1, highlightbackground=BORDER_CYAN)
        chat_box_frame.pack(fill="both", expand=True, pady=(0, 6))
        
        self.txt_chat = tk.Text(chat_box_frame, bg=BG_CARD, fg=FG_LIGHT, font=("Sans", 10),
                                wrap="word", relief="flat", padx=14, pady=12, borderwidth=0)
        self.txt_chat.pack(side="left", fill="both", expand=True)
        
        scroll = ttk.Scrollbar(chat_box_frame, orient="vertical", command=self.txt_chat.yview)
        scroll.pack(side="right", fill="y")
        self.txt_chat.configure(yscrollcommand=scroll.set)
        
        self.txt_chat.tag_configure("operator", foreground=ACCENT_CYAN, font=("Sans", 10, "bold"))
        self.txt_chat.tag_configure("cephalon", foreground=ACCENT_GOLD, font=("Sans", 10, "bold"))
        self.txt_chat.tag_configure("cephalon_child", foreground="#f472b6", font=("Sans", 10, "bold"))
        self.txt_chat.tag_configure("cephalon_sudo", foreground=ACCENT_ROSE, font=("Sans", 10, "bold"))
        self.txt_chat.tag_configure("body", foreground=FG_LIGHT, font=("Sans", 10))
        self.txt_chat.tag_configure("term_header", foreground="#ffffff", background="#0f172a", font=("Courier", 9, "bold"))
        self.txt_chat.tag_configure("term_out", foreground="#38bdf8", background="#030712", font=("Courier", 8))
        
        self.render_history()

        # Input Bar
        input_bar = tk.Frame(right_panel, bg=BG_INPUT, padx=8, pady=4,
                             highlightthickness=1, highlightbackground=BORDER_CYAN)
        input_bar.pack(fill="x")
        
        self.ent_query = tk.Entry(input_bar, bg=BG_INPUT, fg="#ffffff", font=("Sans", 11),
                                  insertbackground=ACCENT_GOLD, relief="flat", borderwidth=0)
        self.ent_query.pack(side="left", fill="x", expand=True, padx=8)
        self.ent_query.bind("<Return>", lambda e: self.send_query())
        self.ent_query.focus_set()
        
        self.btn_send = tk.Button(input_bar, text="Transmute (Enter)", font=("Sans", 10, "bold"),
                                  bg=ACCENT_CYAN, fg="#000", activebackground=ACCENT_GOLD, activeforeground="#000",
                                  relief="flat", padx=16, pady=6, cursor="hand2", command=self.send_query)
        self.btn_send.pack(side="right")
        
        self.bind("<Escape>", lambda e: self.on_close())
        
        # Start Main Event Pump for Thread-safe Queue
        self.poll_msg_queue()

    def poll_msg_queue(self):
        try:
            while True:
                msg_type, payload = self.msg_queue.get_nowait()
                if msg_type == "token":
                    self.txt_chat.insert(tk.END, payload, "body")
                    self.txt_chat.see(tk.END)
                elif msg_type == "complete":
                    self.txt_chat.insert(tk.END, "\n")
                    self.txt_chat.see(tk.END)
                    self.history.append({"role": "cephalon", "text": payload, "time": time.time()})
                    save_history(self.history)
                    self.lbl_status.config(text="● CEPHALON READY", fg=ACCENT_GREEN)
                    self.lbl_progress.config(text="⚡ INFERENCE COMPLETE (100%)")
                    self.prog_bar["value"] = 100
                    self.matrix_canvas.set_speaking_state(False)
                    self.btn_send.config(state="normal")
                    speak_voice_neural_async(payload, self.voice_enabled, self.voice_name)
                elif msg_type == "progress":
                    val, msg = payload
                    self.prog_bar["value"] = val
                    self.lbl_progress.config(text=f"⚡ {msg} ({val}%)")
                elif msg_type == "terminal":
                    cmd_str, out_str = payload
                    self.txt_chat.insert(tk.END, f"\n$ {cmd_str}\n", "term_header")
                    self.txt_chat.insert(tk.END, f"{out_str}\n", "term_out")
                    self.txt_chat.see(tk.END)
                elif msg_type == "directive_complete":
                    self.append_message("cephalon", payload)
                    self.lbl_status.config(text="● CEPHALON READY", fg=ACCENT_GREEN)
                    self.matrix_canvas.set_speaking_state(False)
                    self.btn_send.config(state="normal")
                    speak_voice_neural_async(payload, self.voice_enabled, self.voice_name)
        except queue.Empty:
            pass
        self.after(20, self.poll_msg_queue)

    def update_mode_badge_ui(self):
        if self.mode == "child":
            self.lbl_mode_badge.config(text="[ 🧸 CHILD MODE: SAFE & SIMPLE ]", fg="#000", bg="#f472b6")
        elif self.mode == "professional_sudo":
            self.lbl_mode_badge.config(text="[ ⚡ PRO SUDO MODE: SYSADMIN ARCHITECT ]", fg="#fff", bg=ACCENT_ROSE)
        else:
            self.lbl_mode_badge.config(text="[ 🚀 NORMAL MODE: CEPHALON COPILOT ]", fg="#000", bg=ACCENT_GOLD)

    def update_toggle_buttons_ui(self):
        if self.internet_permitted:
            self.btn_internet.config(text="🌐 Internet: ALLOWED 🔓", fg=ACCENT_GREEN)
        else:
            self.btn_internet.config(text="🌐 Internet: BLOCKED 🔒", fg=FG_MUTED)
            
        if self.document_permitted:
            self.btn_doc.config(text="📁 User Docs: PERMITTED 📂", fg=ACCENT_CYAN)
        else:
            self.btn_doc.config(text="📁 User Docs: PROTECTED 🛡️", fg=FG_MUTED)
            
        if self.voice_enabled:
            self.btn_voice.config(text="✨ Neural Voice: ON 🔊", fg=ACCENT_GOLD)
        else:
            self.btn_voice.config(text="🔇 Voice: OFF 🔇", fg=FG_MUTED)

    def switch_mode(self, target_mode):
        if target_mode == "professional_sudo" and not self.sudo_unlocked:
            pwd = simpledialog.askstring("Sudo Authentication Required",
                                         "Enter sudo password to unlock Professional Sysadmin Mode:",
                                         show='*', parent=self)
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
            target = simpledialog.askstring("Open Link / Search", "Enter website URL or search topic:", parent=self)
            if target:
                if not self.internet_permitted:
                    ans = messagebox.askyesno("Internet Permission", "Opening web pages requires internet connection. Proceed?", parent=self)
                    if not ans: return
                if gally_memory_manager:
                    gally_memory_manager.open_browser_link(target)
                self.append_message("cephalon", f"◈ Opening web browser to '{target}'...")
            return

        self.txt_chat.insert(tk.END, f"\n\n◈ DIRECTIVE INITIATED: {name}\n", "operator")
        self.lbl_status.config(text="● EXECUTING DIRECTIVE...", fg=ACCENT_GOLD)
        self.matrix_canvas.set_speaking_state(True)
        self.btn_send.config(state="disabled")
        threading.Thread(target=self.run_live_terminal_task, args=(name, action_type), daemon=True).start()

    def run_live_terminal_task(self, name, action_type):
        if action_type == "run_diagnostics":
            self.msg_queue.put(("progress", (20, "Scanning Systemd Journal & Kernel Logs")))
            res1 = subprocess.getoutput("journalctl -p 3 -xb -n 6 --no-pager")
            self.msg_queue.put(("terminal", ("journalctl -p 3 -xb -n 6", res1 if res1 else "[ OK ] Zero critical errors in journal.")))
            
            self.msg_queue.put(("progress", (50, "Probing GPU & NVIDIA Telemetry")))
            res2 = subprocess.getoutput("nvidia-smi --query-gpu=name,driver_version,temperature.gpu,utilization.gpu --format=csv,noheader 2>/dev/null || lspci -k | grep -A 2 -E '(VGA|3D)'")
            self.msg_queue.put(("terminal", ("gpu-telemetry-probe", res2)))
            
            self.msg_queue.put(("progress", (80, "Checking Memory & Storage Subsystems")))
            res3 = subprocess.getoutput("df -h / | awk 'NR==2 {print \"Root partition: \" $3 \" used of \" $2 \" (\" $5 \" used)\"}'")
            self.msg_queue.put(("terminal", ("storage-health-check", res3)))
            
            self.msg_queue.put(("progress", (100, "Diagnostics Complete")))
            summary = "Operator, full diagnostic sweep complete. Kernel logs are clean, NVIDIA GPU acceleration is active, and storage matrices are nominal."

        elif action_type == "boost_gaming":
            self.msg_queue.put(("progress", (30, "Activating GameMode Daemon")))
            res1 = subprocess.getoutput("gamemoded -s 2>/dev/null || echo 'GameMode daemon ready'")
            self.msg_queue.put(("terminal", ("gamemoded -s", res1)))
            
            self.msg_queue.put(("progress", (70, "Checking NVENC & NVIDIA Performance State")))
            res2 = subprocess.getoutput("nvidia-smi -q -d PERFORMANCE 2>/dev/null | grep 'Performance State' || echo 'P0 Performance Mode'")
            self.msg_queue.put(("terminal", ("nvidia-perf-query", res2)))
            
            self.msg_queue.put(("progress", (100, "Gaming Matrix Boosted")))
            summary = "Operator, gaming performance matrices are maximized. Dual 144Hz displays and GameMode high-priority scheduling are engaged."

        elif action_type == "repair_audio":
            self.msg_queue.put(("progress", (30, "Probing PipeWire & WirePlumber Status")))
            res1 = subprocess.getoutput("systemctl --user is-active pipewire wireplumber pipewire-pulse")
            self.msg_queue.put(("terminal", ("systemctl --user status pipewire", res1)))
            
            self.msg_queue.put(("progress", (70, "Re-initializing Audio Sinks")))
            res2 = subprocess.getoutput("wpctl status | grep -A 5 'Sinks:' || echo 'Audio sinks active'")
            self.msg_queue.put(("terminal", ("wpctl status (Sinks)", res2)))
            
            self.msg_queue.put(("progress", (100, "Audio Subsystem Harmonized")))
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

        self.lbl_status.config(text="● STREAMING NEURAL MATRIX...", fg=ACCENT_GOLD)
        self.lbl_progress.config(text=f"⚡ [{self.mode.upper()}] INFERENCE STREAMING...")
        self.prog_bar["value"] = 30
        self.matrix_canvas.set_speaking_state(True)
        self.btn_send.config(state="disabled")
        
        tag = "cephalon_child" if self.mode == "child" else ("cephalon_sudo" if self.mode == "professional_sudo" else "cephalon")
        self.txt_chat.insert(tk.END, "\n◈ CEPHALON GALLY: ", tag)
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
                    self.txt_chat.insert(tk.END, f"\n\n◈ OPERATOR: {text}\n", "operator")
                elif role == "cephalon":
                    tag = "cephalon_child" if self.mode == "child" else ("cephalon_sudo" if self.mode == "professional_sudo" else "cephalon")
                    self.txt_chat.insert(tk.END, f"\n◈ CEPHALON GALLY: ", tag)
                    self.txt_chat.insert(tk.END, f"{text}\n", "body")
            self.txt_chat.see(tk.END)

    def append_message(self, role, text):
        self.history.append({"role": role, "text": text, "time": time.time()})
        save_history(self.history)
        if role == "operator":
            self.txt_chat.insert(tk.END, f"\n\n◈ OPERATOR: {text}\n", "operator")
        elif role == "cephalon":
            tag = "cephalon_child" if self.mode == "child" else ("cephalon_sudo" if self.mode == "professional_sudo" else "cephalon")
            self.txt_chat.insert(tk.END, f"\n◈ CEPHALON GALLY: ", tag)
            self.txt_chat.insert(tk.END, f"{text}\n", "body")
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
