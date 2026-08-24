#!/usr/bin/env python3
"""
Gally AI — Autonomous Cephalon System Copilot (Warframe Aesthetic)
3D Holographic Animated Core, Voice Synthesis, Live System Telemetry & 100% Offline AI.
"""

import os
import sys
import math
import json
import time
import subprocess
import threading
import urllib.request
import urllib.parse
import tkinter as tk
from tkinter import ttk, messagebox

CONFIG_PATH = os.path.expanduser("~/.config/gally/ai_config.json")

# Theme Palette (Cephalon Hologram & Orokin Gold)
BG_MAIN = "#040711"
BG_CARD = "#090e1d"
BG_INPUT = "#0f172a"
FG_LIGHT = "#e2e8f0"
FG_MUTED = "#64748b"
ACCENT_CYAN = "#00f0ff"
ACCENT_BLUE = "#38bdf8"
ACCENT_GOLD = "#fbbf24"
ACCENT_MAGENTA = "#f43f5e"
BORDER_CYAN = "#0284c7"
BORDER_GOLD = "#d97706"

DEFAULT_CONFIG = {
    "provider": "ollama",
    "ollama_model": "gally-cephalon-ai",
    "voice_enabled": True,
    "gemini_api_key": "",
    "openai_api_key": "",
    "claude_api_key": "",
    "tokens_used_total": 0,
    "total_queries": 0
}

def load_config():
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(cfg):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)

def speak_voice_async(text, enabled=True):
    if not enabled or not text.strip():
        return
    # Strip markdown symbols for clean speech
    clean = text.replace("*", "").replace("#", "").replace("`", "").replace("[", "").replace("]", "")
    def run_tts():
        try:
            cmd = ["espeak-ng", "-v", "en-us", "-p", "55", "-s", "150", clean[:300]]
            subprocess.run(cmd, stderr=subprocess.DEVNULL)
        except Exception:
            pass
    threading.Thread(target=run_tts, daemon=True).start()

class CephalonCoreCanvas(tk.Canvas):
    """3D Rotating Holographic Cephalon Crystal with Audio Oscillation"""
    def __init__(self, parent, width=220, height=220):
        super().__init__(parent, width=width, height=height, bg=BG_MAIN, highlightthickness=0)
        self.w = width
        self.h = height
        self.cx = width // 2
        self.cy = height // 2
        self.angle_x = 0.0
        self.angle_y = 0.0
        self.angle_z = 0.0
        self.is_speaking = False
        self.pulse = 0.0
        
        # 3D Octahedron / Crystal Vertices (X, Y, Z)
        self.base_vertices = [
            (0, -65, 0),    # Top Apex
            (50, 0, 0),     # Right
            (0, 0, 50),     # Front
            (-50, 0, 0),    # Left
            (0, 0, -50),    # Back
            (0, 65, 0)      # Bottom Apex
        ]
        
        # Facet Edges
        self.edges = [
            (0, 1), (0, 2), (0, 3), (0, 4), # Top Pyramids
            (5, 1), (5, 2), (5, 3), (5, 4), # Bottom Pyramids
            (1, 2), (2, 3), (3, 4), (4, 1)  # Equator Ring
        ]
        
        self.animate()

    def set_speaking_state(self, state: bool):
        self.is_speaking = state

    def animate(self):
        self.delete("all")
        self.angle_x += 0.02
        self.angle_y += 0.03
        self.angle_z += 0.01
        self.pulse += 0.08
        
        # Audio / Energy Pulse scale factor
        pulse_scale = 1.0 + (0.25 * math.sin(self.pulse) if self.is_speaking else 0.08 * math.sin(self.pulse))
        
        # 1. Holographic Radiance Rings
        ring_radius = 80 * pulse_scale
        glow_col = ACCENT_CYAN if not self.is_speaking else ACCENT_MAGENTA
        self.create_oval(self.cx - ring_radius, self.cy - ring_radius,
                          self.cx + ring_radius, self.cy + ring_radius,
                          outline=glow_col, width=1, dash=(3, 6))
                          
        if self.is_speaking:
            # Equalizer frequency ribbons around core
            for i in range(8):
                ang = i * (math.pi / 4) + self.pulse
                r_len = 88 + 16 * math.sin(self.pulse * 2 + i)
                x1 = self.cx + 70 * math.cos(ang)
                y1 = self.cy + 70 * math.sin(ang)
                x2 = self.cx + r_len * math.cos(ang)
                y2 = self.cy + r_len * math.sin(ang)
                self.create_line(x1, y1, x2, y2, fill=ACCENT_GOLD, width=2)
        
        # 2. 3D Matrix Projection
        projected = []
        for (x, y, z) in self.base_vertices:
            # Scale with pulse
            x, y, z = x * pulse_scale, y * pulse_scale, z * pulse_scale
            
            # Rotate Y
            rad_y = self.angle_y
            x1 = x * math.cos(rad_y) + z * math.sin(rad_y)
            y1 = y
            z1 = -x * math.sin(rad_y) + z * math.cos(rad_y)
            
            # Rotate X
            rad_x = self.angle_x
            x2 = x1
            y2 = y1 * math.cos(rad_x) - z1 * math.sin(rad_x)
            z2 = y1 * math.sin(rad_x) + z1 * math.cos(rad_x)
            
            # Perspective Projection
            fov = 180
            dist = fov / (fov + z2 + 100)
            px = self.cx + x2 * dist * 1.5
            py = self.cy + y2 * dist * 1.5
            projected.append((px, py))
            
        # 3. Draw Hologram Facets & Wireframes
        edge_col = ACCENT_CYAN if not self.is_speaking else ACCENT_GOLD
        for u, v in self.edges:
            x1, y1 = projected[u]
            x2, y2 = projected[v]
            self.create_line(x1, y1, x2, y2, fill=edge_col, width=2)
            
        # 4. Central Glowing Cephalon Eye Node
        core_r = 8 if not self.is_speaking else 12
        self.create_oval(self.cx - core_r, self.cy - core_r, self.cx + core_r, self.cy + core_r,
                          fill=ACCENT_GOLD, outline=ACCENT_CYAN, width=2)
        
        self.after(20, self.animate)

class GallyAiApp(tk.Tk):
    def __init__(self):
        super().__init__(className='gally_cephalon_hud')
        self.title("Cephalon Gally — Ship & System Core AI")
        self.geometry("960x680")
        self.configure(bg=BG_MAIN)
        self.minsize(840, 580)
        
        self.config_data = load_config()
        self.voice_enabled = self.config_data.get("voice_enabled", True)
        
        # 1. Top Cephalon Holographic Header
        hdr = tk.Frame(self, bg=BG_MAIN, padx=22, pady=12)
        hdr.pack(fill="x")
        
        top_row = tk.Frame(hdr, bg=BG_MAIN)
        top_row.pack(fill="x")
        
        tk.Label(top_row, text="🌌 CEPHALON GALLY", font=("Sans", 16, "bold"), fg=ACCENT_CYAN, bg=BG_MAIN).pack(side="left")
        tk.Label(top_row, text=" [ OROKIN SHIP-GRADE SYSTEM CORE ] ", font=("Sans", 9, "bold"), fg=ACCENT_GOLD, bg=BG_MAIN).pack(side="left", padx=8)
        
        # Hardware Telemetry Badges
        self.lbl_telemetry = tk.Label(top_row, text="⚡ RYZEN 9 5900X (24T) | RTX GPU | DUAL 144Hz",
                                      font=("Sans", 9, "bold"), fg=ACCENT_CYAN, bg=BG_CARD, padx=10, pady=3,
                                      highlightthickness=1, highlightbackground=BORDER_CYAN)
        self.lbl_telemetry.pack(side="right")
        
        tk.Frame(hdr, height=2, bg=ACCENT_CYAN).pack(fill="x", pady=(8, 0))

        # 2. Main Content: Left Avatar Core + Right Conversation Feed
        main_content = tk.Frame(self, bg=BG_MAIN, padx=18, pady=6)
        main_content.pack(fill="both", expand=True)
        
        # Left Cephalon Avatar Panel
        left_panel = tk.Frame(main_content, bg=BG_CARD, width=250, padx=14, pady=12,
                              highlightthickness=1, highlightbackground=BORDER_CYAN)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)
        
        tk.Label(left_panel, text="◈ VISUAL MATRIX ◈", font=("Sans", 9, "bold"), fg=ACCENT_GOLD, bg=BG_CARD).pack(pady=(0, 4))
        
        # 3D Animated Avatar
        self.avatar_canvas = CephalonCoreCanvas(left_panel, width=220, height=200)
        self.avatar_canvas.pack()
        
        # Status
        self.lbl_status = tk.Label(left_panel, text="● CEPHALON ONLINE", font=("Sans", 9, "bold"), fg="#22c55e", bg=BG_CARD)
        self.lbl_status.pack(pady=(6, 8))
        
        # Voice Toggle Button
        v_txt = "🔊 Voice: ON" if self.voice_enabled else "🔇 Voice: OFF"
        v_col = ACCENT_GOLD if self.voice_enabled else FG_MUTED
        self.btn_voice = tk.Button(left_panel, text=v_txt, font=("Sans", 9, "bold"),
                                   bg=BG_INPUT, fg=v_col, activebackground=ACCENT_CYAN, activeforeground="#000",
                                   relief="flat", padx=10, pady=5, cursor="hand2", command=self.toggle_voice)
        self.btn_voice.pack(fill="x", pady=4)
        
        # Cephalon Quick Directive Buttons
        tk.Label(left_panel, text="─ DIRECTIVES ─", font=("Sans", 8, "bold"), fg=FG_MUTED, bg=BG_CARD).pack(pady=(12, 4))
        
        directives = [
            ("🛡️ Full System Scan", "Operator, perform a full hardware and system journal health scan."),
            ("⚡ Boost Gaming FPS", "Operator, boost gaming shaders and activate GameMode optimization."),
            ("🔊 Audio Diagnostics", "Operator, diagnose and re-initialize the PipeWire audio pipeline."),
            ("🧹 Clean Package Cache", "Operator, clear orphaned packages and reclaim disk storage.")
        ]
        
        for name, query in directives:
            btn = tk.Button(left_panel, text=name, font=("Sans", 8, "bold"),
                            bg=BG_INPUT, fg=FG_LIGHT, activebackground=ACCENT_CYAN, activeforeground="#000",
                            relief="flat", padx=6, pady=4, cursor="hand2", anchor="w",
                            command=lambda q=query: self.run_directive(q))
            btn.pack(fill="x", pady=2)
            
        # Right Chat & Response Console
        right_panel = tk.Frame(main_content, bg=BG_MAIN)
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Conversation Transcript
        chat_box_frame = tk.Frame(right_panel, bg=BG_CARD, highlightthickness=1, highlightbackground=BORDER_CYAN)
        chat_box_frame.pack(fill="both", expand=True, pady=(0, 8))
        
        self.txt_chat = tk.Text(chat_box_frame, bg=BG_CARD, fg=FG_LIGHT, font=("Sans", 10),
                                wrap="word", relief="flat", padx=14, pady=12, borderwidth=0)
        self.txt_chat.pack(side="left", fill="both", expand=True)
        
        scroll = ttk.Scrollbar(chat_box_frame, orient="vertical", command=self.txt_chat.yview)
        scroll.pack(side="right", fill="y")
        self.txt_chat.configure(yscrollcommand=scroll.set)
        
        # Tags styling
        self.txt_chat.tag_configure("operator", foreground=ACCENT_CYAN, font=("Sans", 10, "bold"))
        self.txt_chat.tag_configure("cephalon", foreground=ACCENT_GOLD, font=("Sans", 10, "bold"))
        self.txt_chat.tag_configure("body", foreground=FG_LIGHT, font=("Sans", 10))
        self.txt_chat.tag_configure("cmd", foreground="#38bdf8", background="#0f172a", font=("Courier", 9, "bold"))
        
        # Welcome message
        self.append_cephalon_response(
            "Greetings, Operator. Cephalon Gally is online and synchronized with your Garchy Linux environment. "
            "All 24 threads on your Ryzen 9 5900X and Dual 144Hz displays are running nominal. How may I serve you?"
        )

        # 3. Input Query Box
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
        
        self.bind("<Escape>", lambda e: self.destroy())

    def toggle_voice(self):
        self.voice_enabled = not self.voice_enabled
        self.config_data["voice_enabled"] = self.voice_enabled
        save_config(self.config_data)
        txt = "🔊 Voice: ON" if self.voice_enabled else "🔇 Voice: OFF"
        col = ACCENT_GOLD if self.voice_enabled else FG_MUTED
        self.btn_voice.configure(text=txt, fg=col)

    def run_directive(self, query):
        self.ent_query.delete(0, tk.END)
        self.ent_query.insert(0, query)
        self.send_query()

    def send_query(self):
        prompt = self.ent_query.get().strip()
        if not prompt:
            return
            
        self.ent_query.delete(0, tk.END)
        self.txt_chat.insert(tk.END, "\n\n◈ OPERATOR: ", "operator")
        self.txt_chat.insert(tk.END, f"{prompt}\n", "body")
        self.txt_chat.see(tk.END)
        
        self.lbl_status.config(text="● COMPUTING MATRIX...", fg=ACCENT_GOLD)
        self.avatar_canvas.set_speaking_state(True)
        self.btn_send.config(state="disabled")
        
        threading.Thread(target=self.query_cephalon_thread, args=(prompt,), daemon=True).start()

    def query_cephalon_thread(self, prompt):
        try:
            url = "http://127.0.0.1:11434/api/generate"
            payload = json.dumps({
                "model": "gally-cephalon-ai",
                "prompt": prompt,
                "stream": False
            }).encode("utf-8")
            
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                response_text = data.get("response", "Operator, memory matrices returned an empty stream.")
        except Exception as e:
            response_text = f"Operator, local matrix encountered an anomaly: {e}\nEnsure local daemon is active."
            
        self.after(0, self.on_query_complete, response_text)

    def on_query_complete(self, response_text):
        self.append_cephalon_response(response_text)
        self.lbl_status.config(text="● CEPHALON READY", fg="#22c55e")
        self.avatar_canvas.set_speaking_state(False)
        self.btn_send.config(state="normal")
        speak_voice_async(response_text, self.voice_enabled)

    def append_cephalon_response(self, text):
        self.txt_chat.insert(tk.END, "\n◈ CEPHALON GALLY: ", "cephalon")
        self.txt_chat.insert(tk.END, f"{text}\n", "body")
        self.txt_chat.see(tk.END)

if __name__ == "__main__":
    app = GallyAiApp()
    app.mainloop()
