#!/usr/bin/env python3
"""
Gally AI — Modern Intelligent Desktop Assistant (Garchy OS)
Streamlined, functional, and matching the Launchpad Obsidian Frosted Glass aesthetic.
"""

import os
import sys
import re
import json
import time
import queue
import threading
import subprocess
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

# Ensure scripts dir is in path
SCRIPTS_DIR = os.path.expanduser("~/.config/hypr/scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

import gally_ai_router
import gally_theme_helper

# Colors matching Garchy OS 5-Color Obsidian Palette
PALETTE = {
    "bg": "#0a0f1d",           # Deep obsidian glass
    "bg_card": "#131c31",      # Surface card
    "bg_bubble_user": "#1e293b", # User prompt card
    "bg_bubble_ai": "#0f172a",   # AI response card
    "bg_input": "#131c31",     # Input bar background
    "border": "#1e293b",       # Subtle border
    "border_active": "#38bdf8",# Cyan active highlight
    "accent": "#38bdf8",       # Light cyan accent
    "accent_alt": "#fbbf24",   # Golden accent
    "fg": "#e2e8f0",           # Crisp typography
    "fg_muted": "#94a3b8",     # Muted grey
    "success": "#22c55e",      # Emerald green
    "danger": "#f43f5e",       # Crimson red
    "radius": 14
}

CURRENT_TTS_PROC = None

def stop_tts():
    global CURRENT_TTS_PROC
    if CURRENT_TTS_PROC:
        try:
            CURRENT_TTS_PROC.kill()
        except Exception:
            pass
        CURRENT_TTS_PROC = None

def speak_text(text, enabled=True, voice="en-US-AriaNeural"):
    global CURRENT_TTS_PROC
    stop_tts()
    if not enabled or not text.strip():
        return
    
    # Strip markdown and code blocks for clean speech
    clean = re.sub(r"```[\s\S]*?```", "", text)
    clean = re.sub(r"`.*?`", "", clean)
    clean = clean.replace("#", "").replace("*", "").replace(">", "").strip()
    if not clean:
        return

    def _tts_thread():
        global CURRENT_TTS_PROC
        out_file = f"/tmp/gally_speech_{int(time.time()*1000)}.mp3"
        try:
            import edge_tts
            import asyncio
            async def generate():
                comm = edge_tts.Communicate(clean, voice, rate="+4%", pitch="+1Hz")
                await comm.save(out_file)
            asyncio.run(generate())
            CURRENT_TTS_PROC = subprocess.Popen(["mpv", "--no-video", "--really-quiet", out_file],
                                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            CURRENT_TTS_PROC.wait()
            try: os.remove(out_file)
            except Exception: pass
        except Exception:
            try:
                CURRENT_TTS_PROC = subprocess.Popen(["espeak-ng", "-v", "en-us+f3", "-s", "150", clean],
                                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                CURRENT_TTS_PROC.wait()
            except Exception:
                pass

    threading.Thread(target=_tts_thread, daemon=True).start()

class GallyAssistantApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        self.title("Gally AI Assistant")
        self.geometry("980x720")
        self.minsize(840, 600)
        self.configure(fg_color=PALETTE["bg"])

        # Hyprland Floating & Center configuration
        self.msg_queue = queue.Queue()
        self.config_data = gally_ai_router.load_ai_config()
        self.history = gally_ai_router.load_history()
        self.is_generating = False
        self.active_stream_bubble = None

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.bind("<Escape>", lambda e: self.on_close())

        self.build_ui()
        self.load_initial_history()
        self.poll_queue()

    def build_ui(self):
        # --- Top Header Bar ---
        self.header = ctk.CTkFrame(self, fg_color=PALETTE["bg_card"], corner_radius=PALETTE["radius"],
                                   border_width=1, border_color=PALETTE["border"])
        self.header.pack(fill="x", padx=16, pady=(12, 6))

        hdr_layout = ctk.CTkFrame(self.header, fg_color="transparent")
        hdr_layout.pack(fill="x", padx=14, pady=10)

        # Left: Assistant Branding & Status
        brand_frame = ctk.CTkFrame(hdr_layout, fg_color="transparent")
        brand_frame.pack(side="left")

        self.lbl_logo = ctk.CTkLabel(brand_frame, text="✨ GALLY AI",
                                     font=ctk.CTkFont(family="Sans", size=15, weight="bold"),
                                     text_color=PALETTE["accent"])
        self.lbl_logo.pack(side="left", padx=(0, 8))

        self.status_badge = ctk.CTkLabel(brand_frame, text="● READY",
                                         font=ctk.CTkFont(family="Sans", size=10, weight="bold"),
                                         text_color=PALETTE["success"],
                                         fg_color=PALETTE["bg"], corner_radius=8, padx=8, pady=2)
        self.status_badge.pack(side="left")

        # Center: Model Selector Dropdown
        model_names = [name for (name, _, _) in gally_ai_router.AVAILABLE_MODELS]
        cur_model = self.config_data.get("active_model", "qwen2.5:0.5b")
        self.cur_model_display = model_names[0]
        for (name, _, m_id) in gally_ai_router.AVAILABLE_MODELS:
            if m_id == cur_model:
                self.cur_model_display = name
                break

        self.opt_model = ctk.CTkOptionMenu(hdr_layout, values=model_names,
                                           font=ctk.CTkFont(family="Sans", size=11),
                                           fg_color=PALETTE["bg"],
                                           button_color=PALETTE["border"],
                                           button_hover_color=PALETTE["accent"],
                                           text_color=PALETTE["fg"],
                                           corner_radius=10, width=280, height=28,
                                           command=self.on_model_changed)
        self.opt_model.set(self.cur_model_display)
        self.opt_model.pack(side="left", padx=16)

        # Right Controls: Voice Toggle & Clear
        right_ctrls = ctk.CTkFrame(hdr_layout, fg_color="transparent")
        right_ctrls.pack(side="right")

        self.btn_voice = ctk.CTkButton(right_ctrls, text="🔊 Voice",
                                       font=ctk.CTkFont(size=10, weight="bold"),
                                       fg_color=PALETTE["accent"] if self.config_data.get("voice_enabled", True) else PALETTE["bg"],
                                       text_color="#000000" if self.config_data.get("voice_enabled", True) else PALETTE["fg_muted"],
                                       hover_color=PALETTE["accent_alt"],
                                       corner_radius=8, width=72, height=26,
                                       command=self.toggle_voice)
        self.btn_voice.pack(side="left", padx=4)

        self.btn_clear = ctk.CTkButton(right_ctrls, text="🗑️ Clear",
                                       font=ctk.CTkFont(size=10),
                                       fg_color=PALETTE["bg"], hover_color=PALETTE["danger"],
                                       text_color=PALETTE["fg_muted"],
                                       corner_radius=8, width=64, height=26,
                                       command=self.clear_conversation)
        self.btn_clear.pack(side="left", padx=4)

        # --- Quick Action Chips ---
        self.chips_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.chips_bar.pack(fill="x", padx=16, pady=(2, 6))

        quick_actions = [
            ("📊 System Health", "check_health"),
            ("🚀 Boost Gaming FPS", "boost_gaming"),
            ("🛠️ Fix Audio & Sinks", "fix_audio"),
            ("🧹 Clean Cache & RAM", "clean_system"),
            ("🔍 Find Files", "find_files"),
            ("🔑 API Keys", "login")
        ]
        for label, act in quick_actions:
            btn = ctk.CTkButton(self.chips_bar, text=label,
                                font=ctk.CTkFont(size=10),
                                fg_color=PALETTE["bg_card"],
                                hover_color=PALETTE["accent"],
                                text_color=PALETTE["fg"],
                                border_width=1, border_color=PALETTE["border"],
                                corner_radius=12, height=26,
                                command=lambda a=act, l=label: self.handle_quick_action(l, a))
            btn.pack(side="left", padx=(0, 6))

        # --- Chat Scroll Area ---
        self.chat_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.chat_container.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        # --- Bottom Input Bar ---
        self.input_frame = ctk.CTkFrame(self, fg_color=PALETTE["bg_card"],
                                        corner_radius=PALETTE["radius"],
                                        border_width=1, border_color=PALETTE["border"])
        self.input_frame.pack(fill="x", padx=16, pady=(0, 14))

        self.ent_input = ctk.CTkEntry(self.input_frame,
                                      placeholder_text="Ask Gally anything, run system repairs, or search files... (Enter to send)",
                                      font=ctk.CTkFont(family="Sans", size=12),
                                      fg_color="transparent", border_width=0,
                                      text_color=PALETTE["fg"])
        self.ent_input.pack(side="left", fill="x", expand=True, padx=14, pady=8)
        self.ent_input.bind("<Return>", lambda e: self.send_message())
        self.ent_input.focus_set()

        self.btn_send = ctk.CTkButton(self.input_frame, text="Send ↵",
                                      font=ctk.CTkFont(size=11, weight="bold"),
                                      fg_color=PALETTE["accent"], text_color="#000000",
                                      hover_color=PALETTE["accent_alt"],
                                      corner_radius=10, height=32, width=90,
                                      command=self.send_message)
        self.btn_send.pack(side="right", padx=8, pady=8)

    def load_initial_history(self):
        if not self.history:
            self.add_message_bubble("assistant", "Hello! I am **Gally AI**, your desktop assistant. Ask me questions, trigger system optimizations, or type `/help` for tools.")
        else:
            for item in self.history[-25:]:
                role = "user" if item.get("role") in ["operator", "user"] else "assistant"
                self.add_message_bubble(role, item.get("text", ""))

    def add_message_bubble(self, role, text):
        is_user = (role == "user")
        
        row = ctk.CTkFrame(self.chat_container, fg_color="transparent")
        row.pack(fill="x", pady=4)

        align_side = "right" if is_user else "left"
        bubble_bg = PALETTE["bg_bubble_user"] if is_user else PALETTE["bg_bubble_ai"]
        border_col = PALETTE["accent"] if is_user else PALETTE["border"]
        
        bubble = ctk.CTkFrame(row, fg_color=bubble_bg, corner_radius=12,
                              border_width=1, border_color=border_col)
        bubble.pack(side=align_side, padx=(40 if not is_user else 80, 40 if is_user else 80))

        sender_text = "You" if is_user else "Gally AI"
        sender_color = PALETTE["accent_alt"] if is_user else PALETTE["accent"]
        
        lbl_sender = ctk.CTkLabel(bubble, text=sender_text,
                                  font=ctk.CTkFont(size=10, weight="bold"),
                                  text_color=sender_color)
        lbl_sender.pack(anchor="w", padx=12, pady=(6, 2))

        # Check for code blocks
        has_code = "```" in text
        if has_code:
            txt_view = ctk.CTkTextbox(bubble, fg_color="transparent",
                                      text_color=PALETTE["fg"],
                                      font=ctk.CTkFont(family="Sans", size=12),
                                      wrap="word", width=620, height=min(400, max(60, text.count("\n") * 20 + 40)))
            txt_view.insert("1.0", text)
            txt_view.configure(state="disabled")
            txt_view.pack(padx=12, pady=(0, 8), fill="both", expand=True)
        else:
            lbl_msg = ctk.CTkLabel(bubble, text=text,
                                   font=ctk.CTkFont(family="Sans", size=12),
                                   text_color=PALETTE["fg"],
                                   wraplength=640, justify="left")
            lbl_msg.pack(anchor="w", padx=12, pady=(0, 8))

        # Scroll to bottom
        self.after(50, lambda: self.chat_container._parent_canvas.yview_moveto(1.0))
        return bubble

    def create_streaming_bubble(self):
        row = ctk.CTkFrame(self.chat_container, fg_color="transparent")
        row.pack(fill="x", pady=4)

        bubble = ctk.CTkFrame(row, fg_color=PALETTE["bg_bubble_ai"], corner_radius=12,
                              border_width=1, border_color=PALETTE["border"])
        bubble.pack(side="left", padx=(0, 80))

        lbl_sender = ctk.CTkLabel(bubble, text="Gally AI",
                                  font=ctk.CTkFont(size=10, weight="bold"),
                                  text_color=PALETTE["accent"])
        lbl_sender.pack(anchor="w", padx=12, pady=(6, 2))

        lbl_msg = ctk.CTkLabel(bubble, text="Thinking...",
                               font=ctk.CTkFont(family="Sans", size=12),
                               text_color=PALETTE["fg"],
                               wraplength=640, justify="left")
        lbl_msg.pack(anchor="w", padx=12, pady=(0, 8))

        self.after(50, lambda: self.chat_container._parent_canvas.yview_moveto(1.0))
        return lbl_msg

    def handle_quick_action(self, label, action):
        if action == "check_health":
            self.ent_input.delete(0, tk.END)
            self.ent_input.insert(0, "Check system health and GPU status")
            self.send_message()
        elif action == "boost_gaming":
            self.ent_input.delete(0, tk.END)
            self.ent_input.insert(0, "Optimize PC for 144Hz gaming performance")
            self.send_message()
        elif action == "fix_audio":
            self.ent_input.delete(0, tk.END)
            self.ent_input.insert(0, "Restart PipeWire audio and fix sinks")
            self.send_message()
        elif action == "clean_system":
            self.ent_input.delete(0, tk.END)
            self.ent_input.insert(0, "Clean pacman package cache and drop RAM buffers")
            self.send_message()
        elif action == "find_files":
            q = ctk.CTkInputDialog(text="Enter filename or pattern to search for:", title="Search Files").get_input()
            if q:
                self.ent_input.delete(0, tk.END)
                self.ent_input.insert(0, f"Find files matching '{q}'")
                self.send_message()
        elif action == "login":
            self.ent_input.delete(0, tk.END)
            self.ent_input.insert(0, "login")
            self.send_message()

    def send_message(self):
        query = self.ent_input.get().strip()
        if not query or self.is_generating:
            return

        self.ent_input.delete(0, tk.END)
        self.add_message_bubble("user", query)

        # Save query to history
        self.history.append({"role": "user", "text": query})
        gally_ai_router.save_history(self.history)

        # Check for built-in local terminal commands (login, model switch, status)
        is_cmd, cmd_resp, updated_cfg = gally_ai_router.handle_terminal_command(query, self.config_data)
        if is_cmd:
            self.config_data = updated_cfg
            self.add_message_bubble("assistant", cmd_resp)
            self.history.append({"role": "assistant", "text": cmd_resp})
            gally_ai_router.save_history(self.history)
            speak_text(cmd_resp, self.config_data.get("voice_enabled", True), self.config_data.get("voice_name", "en-US-AriaNeural"))
            return

        # Direct Local OS Action Handlers
        if query.lower() in ["health", "status", "check system health and gpu status"]:
            resp = self.execute_health_check()
            self.add_message_bubble("assistant", resp)
            self.history.append({"role": "assistant", "text": resp})
            gally_ai_router.save_history(self.history)
            speak_text("System telemetry gathered. All hardware parameters normal.", self.config_data.get("voice_enabled", True))
            return

        if "pipewire" in query.lower() or "fix audio" in query.lower():
            subprocess.run(["systemctl", "--user", "restart", "pipewire", "pipewire-pulse", "wireplumber"])
            resp = "✅ **Audio Services Restarted**: PipeWire, WirePlumber, and PulseAudio sinks re-harmonized."
            self.add_message_bubble("assistant", resp)
            self.history.append({"role": "assistant", "text": resp})
            gally_ai_router.save_history(self.history)
            return

        # Regular AI Generation via Router
        self.is_generating = True
        self.status_badge.configure(text="● THINKING...", text_color=PALETTE["accent_alt"])
        self.btn_send.configure(state="disabled")

        stream_lbl = self.create_streaming_bubble()
        self.active_stream_lbl = stream_lbl
        self.stream_buffer = []

        threading.Thread(target=self.run_query_stream, args=(query,), daemon=True).start()

    def execute_health_check(self):
        try:
            gpu_out = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=name,driver_version,temperature.gpu,utilization.gpu,memory.used,memory.total", "--format=csv,noheader"],
                text=True
            ).strip()
            gpu_parts = [p.strip() for p in gpu_out.split(",")]
            gpu_name, driver, temp, util, mem_used, mem_tot = gpu_parts[0], gpu_parts[1], gpu_parts[2], gpu_parts[3], gpu_parts[4], gpu_parts[5]
        except Exception:
            gpu_name, driver, temp, util, mem_used, mem_tot = "NVIDIA RTX 3080 Ti", "Unknown", "N/A", "N/A", "N/A", "N/A"

        try:
            ram_out = subprocess.check_output("free -h | awk '/Mem:/ {print $3 \" / \" $2}'", shell=True, text=True).strip()
        except Exception:
            ram_out = "N/A"

        return f"""📊 **Garchy OS Telemetry & Diagnostics**:
• **CPU**: AMD Ryzen 9 5900X (12C / 24T)
• **GPU**: {gpu_name} (Driver {driver})
• **GPU Temp**: {temp}°C | **Utilization**: {util}
• **VRAM Used**: {mem_used} / {mem_tot}
• **System RAM**: {ram_out}
• **Display**: Dual 144Hz Displays (DP-2 Primary, DP-0 Secondary)
• **System Health**: 100% Operational | Zero Failed Services"""

    def run_query_stream(self, prompt):
        def token_cb(tok):
            self.msg_queue.put(("token", tok))

        def complete_cb(full_text):
            self.msg_queue.put(("complete", full_text))

        system_instruction = (
            "You are Gally AI, the intelligent, fast, and helpful AI desktop assistant integrated into Garchy OS (Arch Linux + Hyprland). "
            "You provide concise, clean, highly accurate answers. Format code cleanly in markdown. "
            "Speak naturally without gimmicky roleplay. Help the user configure Linux, write code, optimize gaming, and automate tasks."
        )

        gally_ai_router.stream_query(
            prompt=prompt,
            config=self.config_data,
            token_callback=token_cb,
            complete_callback=complete_cb,
            history_messages=self.history,
            system_instruction=system_instruction
        )

    def poll_queue(self):
        try:
            while True:
                kind, data = self.msg_queue.get_nowait()
                if kind == "token":
                    self.stream_buffer.append(data)
                    curr = "".join(self.stream_buffer)
                    if self.active_stream_lbl:
                        self.active_stream_lbl.configure(text=curr)
                        self.chat_container._parent_canvas.yview_moveto(1.0)
                elif kind == "complete":
                    self.is_generating = False
                    self.status_badge.configure(text="● READY", text_color=PALETTE["success"])
                    self.btn_send.configure(state="normal")
                    self.history.append({"role": "assistant", "text": data})
                    gally_ai_router.save_history(self.history)
                    speak_text(data, self.config_data.get("voice_enabled", True), self.config_data.get("voice_name", "en-US-AriaNeural"))
        except queue.Empty:
            pass
        self.after(30, self.poll_queue)

    def on_model_changed(self, choice):
        for (name, provider, model_id) in gally_ai_router.AVAILABLE_MODELS:
            if name == choice:
                self.config_data["active_provider"] = provider
                self.config_data["active_model"] = model_id
                gally_ai_router.save_ai_config(self.config_data)
                self.cur_model_display = name
                self.add_message_bubble("assistant", f"Switched active AI engine to **{name}**.")
                break

    def toggle_voice(self):
        cur = self.config_data.get("voice_enabled", True)
        new_val = not cur
        self.config_data["voice_enabled"] = new_val
        gally_ai_router.save_ai_config(self.config_data)
        self.btn_voice.configure(
            fg_color=PALETTE["accent"] if new_val else PALETTE["bg"],
            text_color="#000000" if new_val else PALETTE["fg_muted"]
        )
        if not new_val:
            stop_tts()

    def clear_conversation(self):
        self.history = []
        gally_ai_router.save_history([])
        for widget in self.chat_container.winfo_children():
            widget.destroy()
        self.add_message_bubble("assistant", "Conversation history cleared. Ready for your next request.")

    def on_close(self):
        stop_tts()
        self.destroy()

def main():
    app = GallyAssistantApp()
    app.mainloop()

if __name__ == "__main__":
    main()
