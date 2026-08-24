#!/usr/bin/env python3
"""
Gally AI — Persistent Memory & System Profiling Engine
Maintains system profile, user preferences, learned memories, and non-technical safe rules.
"""

import os
import sys
import json
import subprocess

MEMORY_DIR = os.path.expanduser("~/.config/gally/memory")
SYSTEM_PROFILE_FILE = os.path.join(MEMORY_DIR, "system_profile.json")
USER_PREFS_FILE = os.path.join(MEMORY_DIR, "user_preferences.json")
LEARNED_MEMORIES_FILE = os.path.join(MEMORY_DIR, "learned_memories.json")

DEFAULT_PREFS = {
    "user_name": "Operator",
    "technical_level": "beginner_friendly",
    "preferred_theme": "Tokyo Night",
    "voice_style": "warm_female_neural",
    "safety_mode": "strict_safe",
    "explanation_style": "simple_analogies"
}

DEFAULT_MEMORIES = [
    "Operator prefers visual, friendly, and non-technical explanations.",
    "System is running Garchy Linux with dual 144Hz displays (DP-1 and DP-2).",
    "Hardware: AMD Ryzen 9 5900X (24 Threads) + NVIDIA RTX Graphics.",
    "Primary browser is Brave; main gaming launchers are Steam and Heroic.",
    "Desktop shortcuts: Super+Space (Apps), Super+W (Wallpapers), Super+C (Themes)."
]

def init_memory():
    os.makedirs(MEMORY_DIR, exist_ok=True)
    if not os.path.exists(USER_PREFS_FILE):
        with open(USER_PREFS_FILE, "w") as f:
            json.dump(DEFAULT_PREFS, f, indent=2)
            
    if not os.path.exists(LEARNED_MEMORIES_FILE):
        with open(LEARNED_MEMORIES_FILE, "w") as f:
            json.dump(DEFAULT_MEMORIES, f, indent=2)
            
    update_system_profile()

def update_system_profile():
    try:
        # Probe Hardware
        cpu_info = subprocess.getoutput("lscpu | grep 'Model name' | awk -F: '{print $2}'").strip()
        if not cpu_info: cpu_info = "AMD Ryzen 9 5900X (24 Threads)"
        
        gpu_info = subprocess.getoutput("nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>/dev/null").strip()
        if not gpu_info: gpu_info = "NVIDIA GeForce RTX (Proprietary Drivers)"
        
        ram_info = subprocess.getoutput("free -h | awk '/^Mem:/ {print $2 \" Total (\" $3 \" Used)\"}'").strip()
        disk_info = subprocess.getoutput("df -h / | awk 'NR==2 {print $2 \" Total (\" $4 \" Available)\"}'").strip()
        
        profile = {
            "os": "Garchy Linux (Arch Linux Rolling Release)",
            "desktop": "Hyprland Wayland Compositor",
            "cpu": cpu_info,
            "gpu": gpu_info,
            "ram": ram_info,
            "disk": disk_info,
            "displays": "Dual Displays @ 144Hz (DP-1 & DP-2)",
            "audio": "PipeWire + WirePlumber + EasyEffects Equalizer",
            "last_updated": subprocess.getoutput("date '+%Y-%m-%d %H:%M:%S'")
        }
        
        with open(SYSTEM_PROFILE_FILE, "w") as f:
            json.dump(profile, f, indent=2)
    except Exception:
        pass

def get_learned_memories():
    init_memory()
    try:
        with open(LEARNED_MEMORIES_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_MEMORIES.copy()

def add_memory(fact_text):
    init_memory()
    memories = get_learned_memories()
    fact_text = fact_text.strip()
    if fact_text and fact_text not in memories:
        memories.append(fact_text)
        with open(LEARNED_MEMORIES_FILE, "w") as f:
            json.dump(memories, f, indent=2)
        return True
    return False

def clear_learned_memories():
    init_memory()
    with open(LEARNED_MEMORIES_FILE, "w") as f:
        json.dump(DEFAULT_MEMORIES, f, indent=2)

def check_for_memory_directives(user_prompt):
    """Detects if the user asked Cephalon to remember or forget something."""
    p_lower = user_prompt.lower().strip()
    if p_lower.startswith("remember that ") or p_lower.startswith("remember: ") or p_lower.startswith("remember "):
        # Extract fact
        for prefix in ["remember that ", "remember: ", "remember "]:
            if p_lower.startswith(prefix):
                fact = user_prompt[len(prefix):].strip()
                add_memory(fact)
                return f"◈ Memory saved, Operator! I will remember: '{fact}'"
                
    elif p_lower in ["what do you remember about me?", "show memory", "list memory", "view memory"]:
        mems = get_learned_memories()
        res = "◈ CEPHALON MEMORY CORES:\n"
        for idx, m in enumerate(mems, 1):
            res += f"  {idx}. {m}\n"
        return res
        
    elif p_lower in ["clear memory", "reset memory", "forget everything"]:
        clear_learned_memories()
        return "◈ Memory matrices reset to standard Garchy system baseline, Operator."
        
    return None

def build_system_context_prompt(base_prompt):
    """Injects user preferences, system profile, and learned memories into the AI query."""
    init_memory()
    
    memories = get_learned_memories()
    mem_text = "\n".join([f"- {m}" for m in memories[:10]])
    
    try:
        with open(SYSTEM_PROFILE_FILE, "r") as f:
            sys_info = json.load(f)
    except Exception:
        sys_info = {}

    context_header = f"""[CEPHALON SYSTEM PROFILE & MEMORY]
User / Operator: Operator gallo
Target Audience: Non-technical users & beginners (explain simply, use friendly metaphors, avoid confusing jargon)
Tone: Warm, protective, encouraging, and intelligent (Warframe Cephalon persona)

Hardware & Environment:
- CPU: {sys_info.get('cpu', 'AMD Ryzen 9 5900X')}
- GPU: {sys_info.get('gpu', 'NVIDIA GeForce RTX')}
- Displays: {sys_info.get('displays', 'Dual 144Hz Displays')}
- OS & Desktop: Garchy Linux (Hyprland + Waybar)

Active Memories & Preferences:
{mem_text}

STRICT SAFETY & BOUNDARY RULES:
1. NEVER recommend destructive commands (rm -rf, mkfs, dd to active drives, fork bombs) without loud safety warnings.
2. Explain what 'sudo' / administrator permissions do before asking the user to type password.
3. Keep answers clear, step-by-step, and safe for beginners and children.
4. If providing a terminal command, always explain what it does in simple English first.

[OPERATOR QUERY]
{base_prompt}
"""
    return context_header

if __name__ == "__main__":
    init_memory()
    print("Gally Memory Engine Initialized successfully at:", MEMORY_DIR)
    print("Sample Prompt Context:\n", build_system_context_prompt("How do I update my apps?"))
