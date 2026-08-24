#!/usr/bin/env python3
"""
Cephalon Gally — Holographic AI System Core (Warframe Aesthetic)
High-Quality Neural Female Voice, 3D Glowing Particle Matrix, Live Audio Equalizer & Offline AI.
"""

import os
import sys
import math
import json
import time
import random
import asyncio
import subprocess
import threading
import urllib.request
import urllib.parse
import tkinter as tk
from tkinter import ttk, messagebox

CONFIG_PATH = os.path.expanduser("~/.config/gally/ai_config.json")

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
ACCENT_ROSE = "#f43f5e"
BORDER_CYAN = "#0369a1"
BORDER_GOLD = "#b45309"

DEFAULT_CONFIG = {
    "provider": "ollama",
    "ollama_model": "gally-cephalon-ai",
    "voice_enabled": True,
    "voice_name": "en-US-AriaNeural",
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

def speak_voice_neural_async(text, enabled=True, voice="en-US-AriaNeural"):
    if not enabled or not text.strip():
        return
        
    clean = text.replace("*", "").replace("#", "").replace("`", "").replace("[", "").replace("]", "")
    # Remove code blocks or long logs for speech
    clean = " ".join([line for line in clean.splitlines() if not line.strip().startswith("$") and not line.strip().startswith("sudo")])
    if len(clean) > 400:
        clean = clean[:400] + "..."

    def run_tts():
        out_file = f"/tmp/cephalon_speech_{int(time.time()*1000)}.mp3"
        try:
            # 1. Try High Quality Neural Voice (edge-tts)
            import edge_tts
            async def generate():
                comm = edge_tts.Communicate(clean, voice, rate="+4%", pitch="+2Hz")
                await comm.save(out_file)
            asyncio.run(generate())
            subprocess.run(["mpv", "--no-video", "--really-quiet", out_file], stderr=subprocess.DEVNULL)
            try: os.remove(out_file)
            except Exception: pass
        except Exception:
            # 2. Offline Fallback to female espeak-ng
            try:
                cmd = ["espeak-ng", "-v", "en-us+f3", "-p", "60", "-s", "145", clean]
                subprocess.run(cmd, stderr=subprocess.DEVNULL)
            except Exception:
                pass

    threading.Thread(target=run_tts, daemon=True).start()

class CephalonGlowingMatrix(tk.Canvas):
    """3D Glowing Geometric Cephalon Crystal + Orbiting Particle Swarm & Spectral Equalizer"""
    def __init__(self, parent, width=280, height=270):
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
        
        # 3D Outer Polyhedron Vertices
        self.outer_vertices = [
            (0, -75, 0),      # Top Apex
            (55, -20, 35),    # Upper Ring
            (0, -20, -65),
            (-55, -20, 35),
            (55, 20, -35),    # Lower Ring
            (0, 20, 65),
            (-55, 20, -35),
            (0, 75, 0)        # Bottom Apex
        ]
        
        self.outer_edges = [
            (0, 1), (0, 2), (0, 3),
            (1, 4), (2, 4), (2, 6), (3, 6), (3, 5), (1, 5),
            (7, 4), (7, 5), (7, 6),
            (1, 2), (2, 3), (3, 1), # Upper Triangle
            (4, 5), (5, 6), (6, 4)  # Lower Triangle
        ]

        # Inner Core Orokin Diamond Vertices
        self.inner_vertices = [
            (0, -35, 0),
            (25, 0, 0),
            (0, 0, 25),
            (-25, 0, 0),
            (0, 0, -25),
            (0, 35, 0)
        ]
        self.inner_edges = [
            (0, 1), (0, 2), (0, 3), (0, 4),
            (5, 1), (5, 2), (5, 3), (5, 4),
            (1, 2), (2, 3), (3, 4), (4, 1)
        ]

        # Orbiting Energy Particle Swarm (24 particles)
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

    def animate(self):
        self.delete("all")
        self.angle_x += 0.018
        self.angle_y += 0.024
        self.angle_z += 0.012
        self.pulse += 0.075
        
        # Audio / Energy Pulse scale factor
        amp = 0.28 if self.is_speaking else 0.08
        pulse_scale = 1.0 + amp * math.sin(self.pulse)
        
        # 1. Background Glowing Radial Rings (Aura)
        for r_offset, col, dash in [
            (95 * pulse_scale, "#0e2a47", (2, 4)),
            (115 * pulse_scale, "#091d33", (1, 5)),
            (130 * pulse_scale, "#061322", (2, 8))
        ]:
            self.create_oval(self.cx - r_offset, self.cy - r_offset,
                              self.cx + r_offset, self.cy + r_offset,
                              outline=col, width=1, dash=dash)
                              
        # 2. Kinetic Audio Equalizer Rays (Active When Speaking)
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
                ray_col = ACCENT_CYAN if i % 2 == 0 else ACCENT_GOLD
                self.create_line(x1, y1, x2, y2, fill=ray_col, width=2)

        # 3. Orbiting Particle Swarm
        for p in self.particles:
            p["angle"] += p["speed"]
            px = self.cx + p["radius"] * math.cos(p["angle"])
            py = self.cy + p["radius"] * math.sin(p["angle"]) * math.cos(p["tilt"]) + (10 * math.sin(self.pulse + p["angle"]))
            ps = p["size"] if not self.is_speaking else p["size"] * 1.5
            self.create_oval(px - ps, py - ps, px + ps, py + ps, fill=p["color"], outline="")

        # 4. Project & Render Outer Crystal Facets
        def project_3d(v_list, scale):
            proj = []
            for (x, y, z) in v_list:
                x, y, z = x * scale, y * scale, z * scale
                # Y Rotation
                x1 = x * math.cos(self.angle_y) + z * math.sin(self.angle_y)
                y1 = y
                z1 = -x * math.sin(self.angle_y) + z * math.cos(self.angle_y)
                # X Rotation
                x2 = x1
                y2 = y1 * math.cos(self.angle_x) - z1 * math.sin(self.angle_x)
                z2 = y1 * math.sin(self.angle_x) + z1 * math.cos(self.angle_x)
                # Perspective
                fov = 220
                dist = fov / (fov + z2 + 120)
                px = self.cx + x2 * dist * 1.4
                py = self.cy + y2 * dist * 1.4
                proj.append((px, py, z2))
            return proj

        outer_proj = project_3d(self.outer_vertices, pulse_scale)
        inner_proj = project_3d(self.inner_vertices, pulse_scale * 1.1)

        # Draw Outer Neon Cyan Facets
        for u, v in self.outer_edges:
            x1, y1, z1 = outer_proj[u]
            x2, y2, z2 = outer_proj[v]
            depth_col = ACCENT_CYAN if (z1 + z2) / 2 > -20 else "#0369a1"
            width = 2 if self.is_speaking else 1
            self.create_line(x1, y1, x2, y2, fill=depth_col, width=width)

        # Draw Inner Orokin Gold Core Facets (Glow Heart)
        for u, v in self.inner_edges:
            x1, y1, _ = inner_proj[u]
            x2, y2, _ = inner_proj[v]
            self.create_line(x1, y1, x2, y2, fill=ACCENT_GOLD, width=2)

        # 5. Glowing Vertex Energy Nodes
        for (px, py, _) in outer_proj:
            self.create_oval(px - 2, py - 2, px + 2, py + 2, fill=ACCENT_CYAN, outline="")

        # 6. Radiant Center Core Eye Node
        core_r = 7 if not self.is_speaking else 11 + 3 * math.sin(self.pulse * 2)
        self.create_oval(self.cx - core_r - 4, self.cy - core_r - 4,
                          self.cx + core_r + 4, self.cy + core_r + 4,
                          outline=ACCENT_PURPLE, width=1)
        self.create_oval(self.cx - core_r, self.cy - core_r,
                          self.cx + core_r, self.cy + core_r,
                          fill=ACCENT_GOLD, outline="#ffffff", width=2)
        
        self.after(22, self.animate)

class CephalonApp(tk.Tk):
    def __init__(self):
        super().__init__(className='gally_cephalon_hud')
        self.title("Cephalon Gally — Ship & System Core AI")
        self.geometry("980x700")
        self.configure(bg=BG_MAIN)
        self.minsize(860, 600)
        
        self.config_data = load_config()
        self.voice_enabled = self.config_data.get("voice_enabled", True)
        self.voice_name = self.config_data.get("voice_name", "en-US-AriaNeural")
        
        # 1. Top Cephalon Holographic Header Bar
        hdr = tk.Frame(self, bg=BG_MAIN, padx=22, pady=12)
        hdr.pack(fill="x")
        
        top_row = tk.Frame(hdr, bg=BG_MAIN)
        top_row.pack(fill="x")
        
        tk.Label(top_row, text="🌌 CEPHALON GALLY", font=("Sans", 16, "bold"), fg=ACCENT_CYAN, bg=BG_MAIN).pack(side="left")
        tk.Label(top_row, text=" [ OROKIN NEURAL SHIP CORE ] ", font=("Sans", 9, "bold"), fg=ACCENT_GOLD, bg=BG_MAIN).pack(side="left", padx=8)
        
        # Hardware Telemetry Badges
        self.lbl_telemetry = tk.Label(top_row, text="⚡ RYZEN 9 5900X (24T) | RTX GPU | DUAL 144Hz",
                                      font=("Sans", 9, "bold"), fg=ACCENT_CYAN, bg=BG_CARD, padx=12, pady=4,
                                      highlightthickness=1, highlightbackground=BORDER_CYAN)
        self.lbl_telemetry.pack(side="right")
        
        tk.Frame(hdr, height=2, bg=ACCENT_CYAN).pack(fill="x", pady=(8, 0))

        # 2. Main Content Frame
        main_content = tk.Frame(self, bg=BG_MAIN, padx=18, pady=6)
        main_content.pack(fill="both", expand=True)
        
        # Left Panel: Visual Matrix & Cephalon Voice Controls
        left_panel = tk.Frame(main_content, bg=BG_CARD, width=300, padx=14, pady=10,
                              highlightthickness=1, highlightbackground=BORDER_CYAN)
        left_panel.pack(side="left", fill="y", padx=(0, 12))
        left_panel.pack_propagate(False)
        
        tk.Label(left_panel, text="◈ NEURAL MATRIX ◈", font=("Sans", 9, "bold"), fg=ACCENT_GOLD, bg=BG_CARD).pack(pady=(0, 4))
        
        # 3D Glowing Visual Avatar
        self.matrix_canvas = CephalonGlowingMatrix(left_panel, width=270, height=250)
        self.matrix_canvas.pack()
        
        self.lbl_status = tk.Label(left_panel, text="● CEPHALON ONLINE", font=("Sans", 9, "bold"), fg="#22c55e", bg=BG_CARD)
        self.lbl_status.pack(pady=(4, 6))
        
        # Voice Toggle Button (Studio Neural Female)
        v_txt = "✨ Neural Voice: ON" if self.voice_enabled else "🔇 Voice: OFF"
        v_col = ACCENT_GOLD if self.voice_enabled else FG_MUTED
        self.btn_voice = tk.Button(left_panel, text=v_txt, font=("Sans", 9, "bold"),
                                   bg=BG_INPUT, fg=v_col, activebackground=ACCENT_CYAN, activeforeground="#000",
                                   relief="flat", padx=10, pady=6, cursor="hand2", command=self.toggle_voice)
        self.btn_voice.pack(fill="x", pady=4)
        
        # Cephalon Directives Header
        tk.Label(left_panel, text="─ CEPHALON DIRECTIVES ─", font=("Sans", 8, "bold"), fg=FG_MUTED, bg=BG_CARD).pack(pady=(10, 4))
        
        directives = [
            ("🛡️ Full System Diagnostics", "Operator, perform a full hardware and system journal health scan."),
            ("⚡ Boost Gaming FPS & Shaders", "Operator, boost gaming shaders and activate GameMode optimization."),
            ("🔊 Audio Subsystem Repair", "Operator, diagnose and re-initialize the PipeWire audio pipeline."),
            ("🧹 Purge Package & Disk Cache", "Operator, clear orphaned packages and reclaim disk storage.")
        ]
        
        for name, query in directives:
            btn = tk.Button(left_panel, text=name, font=("Sans", 8, "bold"),
                            bg=BG_INPUT, fg=FG_LIGHT, activebackground=ACCENT_CYAN, activeforeground="#000",
                            relief="flat", padx=6, pady=4, cursor="hand2", anchor="w",
                            command=lambda q=query: self.run_directive(q))
            btn.pack(fill="x", pady=2)
            
        # Right Panel: Chat & Holographic Console
        right_panel = tk.Frame(main_content, bg=BG_MAIN)
        right_panel.pack(side="right", fill="both", expand=True)
        
        chat_box_frame = tk.Frame(right_panel, bg=BG_CARD, highlightthickness=1, highlightbackground=BORDER_CYAN)
        chat_box_frame.pack(fill="both", expand=True, pady=(0, 8))
        
        self.txt_chat = tk.Text(chat_box_frame, bg=BG_CARD, fg=FG_LIGHT, font=("Sans", 10),
                                wrap="word", relief="flat", padx=16, pady=14, borderwidth=0)
        self.txt_chat.pack(side="left", fill="both", expand=True)
        
        scroll = ttk.Scrollbar(chat_box_frame, orient="vertical", command=self.txt_chat.yview)
        scroll.pack(side="right", fill="y")
        self.txt_chat.configure(yscrollcommand=scroll.set)
        
        # Text styling tags
        self.txt_chat.tag_configure("operator", foreground=ACCENT_CYAN, font=("Sans", 10, "bold"))
        self.txt_chat.tag_configure("cephalon", foreground=ACCENT_GOLD, font=("Sans", 10, "bold"))
        self.txt_chat.tag_configure("body", foreground=FG_LIGHT, font=("Sans", 10))
        
        # Welcome message
        welcome = (
            "Greetings, Operator. Cephalon Gally is online and synchronized with your Garchy Linux environment. "
            "All 24 threads on your Ryzen 9 5900X and Dual 144Hz displays are running nominal. How may I assist you?"
        )
        self.append_cephalon_response(welcome)
        speak_voice_neural_async(welcome, self.voice_enabled, self.voice_name)

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
                                  relief="flat", padx=18, pady=6, cursor="hand2", command=self.send_query)
        self.btn_send.pack(side="right")
        
        self.bind("<Escape>", lambda e: self.destroy())

    def toggle_voice(self):
        self.voice_enabled = not self.voice_enabled
        self.config_data["voice_enabled"] = self.voice_enabled
        save_config(self.config_data)
        txt = "✨ Neural Voice: ON" if self.voice_enabled else "🔇 Voice: OFF"
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
        self.matrix_canvas.set_speaking_state(True)
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
                response_text = data.get("response", "Operator, neural matrices returned an empty stream.")
        except Exception as e:
            response_text = f"Operator, local matrix encountered an anomaly: {e}\nEnsure local ollama daemon is running."
            
        self.after(0, self.on_query_complete, response_text)

    def on_query_complete(self, response_text):
        self.append_cephalon_response(response_text)
        self.lbl_status.config(text="● CEPHALON READY", fg="#22c55e")
        self.matrix_canvas.set_speaking_state(False)
        self.btn_send.config(state="normal")
        speak_voice_neural_async(response_text, self.voice_enabled, self.voice_name)

    def append_cephalon_response(self, text):
        self.txt_chat.insert(tk.END, "\n◈ CEPHALON GALLY: ", "cephalon")
        self.txt_chat.insert(tk.END, f"{text}\n", "body")
        self.txt_chat.see(tk.END)

if __name__ == "__main__":
    app = CephalonApp()
    app.mainloop()
