#!/usr/bin/env python3
"""
==============================================================================
🌌 Garchy OS — Gally AI Chat Service & Streaming Backend
==============================================================================
"""

import os
import sys
import json
import time
import subprocess
import threading

SCRIPTS_DIR = os.path.expanduser("~/.config/hypr/scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

import gally_ai_router

HISTORY_FILE = "/tmp/gally_chat_history.json"
CONFIG_FILE = os.path.expanduser("~/.config/gally/ai_config.json")

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return [
        {
            "role": "assistant",
            "text": "◈ Cephalon Gally online. AMD Ryzen 9 5900X & NVIDIA RTX 3080 Ti neural matrix connected. How may I assist your operations?",
            "timestamp": time.strftime("%H:%M")
        }
    ]

def save_history(hist):
    tmp = HISTORY_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(hist, f)
    os.replace(tmp, HISTORY_FILE)

def ensure_ollama():
    try:
        subprocess.check_output(["ollama", "list"], stderr=subprocess.DEVNULL, timeout=1.5)
        return True
    except Exception:
        try:
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1.0)
            return True
        except Exception:
            return False

def handle_send(prompt):
    hist = load_history()
    user_time = time.strftime("%H:%M")
    hist.append({"role": "user", "text": prompt, "timestamp": user_time})
    
    # Placeholder assistant response
    hist.append({"role": "assistant", "text": "...", "timestamp": user_time, "is_streaming": True})
    save_history(hist)

    cfg = gally_ai_router.load_ai_config()
    
    # Check special quick commands
    cmd_handled, reply, new_cfg = gally_ai_router.handle_meta_command(prompt, cfg)
    if cmd_handled:
        hist[-1]["text"] = reply
        hist[-1]["is_streaming"] = False
        save_history(hist)
        return

    # Check if local ollama
    if cfg.get("active_provider") == "local_ollama":
        ensure_ollama()

    collected = []

    def on_token(t):
        collected.append(t)
        hist[-1]["text"] = "".join(collected)
        save_history(hist)

    def on_complete(full_text):
        hist[-1]["text"] = full_text or "".join(collected)
        hist[-1]["is_streaming"] = False
        save_history(hist)
        # Speak if voice enabled
        if cfg.get("voice_enabled", False):
            speak_text(hist[-1]["text"][:300])

    try:
        gally_ai_router.stream_query(
            prompt,
            cfg,
            token_callback=on_token,
            complete_callback=on_complete,
            history_messages=hist[:-2]
        )
        on_complete("".join(collected))
    except Exception as e:
        hist[-1]["text"] = f"◈ Cephalon Diagnostics: {str(e)}\n\n(Tip: If using Ollama, verify `ollama serve` is active or configure an API key via `/login`)."
        hist[-1]["is_streaming"] = False
        save_history(hist)

def speak_text(text):
    clean = text.replace("`", "").replace("*", "").replace("#", "")
    try:
        subprocess.Popen(["espeak-ng", clean], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def handle_clear():
    save_history([
        {
            "role": "assistant",
            "text": "◈ Memory buffer cleared. Cephalon Gally ready for new operations.",
            "timestamp": time.strftime("%H:%M")
        }
    ])

def handle_set_model(model_name):
    cfg = gally_ai_router.load_ai_config()
    for label, prov, mod in gally_ai_router.AVAILABLE_MODELS:
        if mod == model_name or label == model_name or mod in model_name:
            cfg["active_provider"] = prov
            cfg["active_model"] = mod
            gally_ai_router.save_ai_config(cfg)
            hist = load_history()
            hist.append({
                "role": "assistant",
                "text": f"◈ Switched active neural model to: [ {label} ]",
                "timestamp": time.strftime("%H:%M")
            })
            save_history(hist)
            return
    cfg["active_model"] = model_name
    gally_ai_router.save_ai_config(cfg)

def handle_toggle_voice():
    cfg = gally_ai_router.load_ai_config()
    cfg["voice_enabled"] = not cfg.get("voice_enabled", False)
    gally_ai_router.save_ai_config(cfg)
    hist = load_history()
    v_status = "ACTIVATED 🔊" if cfg["voice_enabled"] else "MUTED 🔇"
    hist.append({
        "role": "assistant",
        "text": f"◈ Neural Voice Synthesis {v_status}.",
        "timestamp": time.strftime("%H:%M")
    })
    save_history(hist)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "send" and len(sys.argv) > 2:
            prompt = " ".join(sys.argv[2:])
            handle_send(prompt)
        elif cmd == "clear":
            handle_clear()
        elif cmd == "set-model" and len(sys.argv) > 2:
            handle_set_model(sys.argv[2])
        elif cmd == "toggle-voice":
            handle_toggle_voice()
        elif cmd == "init":
            save_history(load_history())
