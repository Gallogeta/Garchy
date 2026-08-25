#!/usr/bin/env python3
"""
Gally AI — Security, Privacy & Mode Controller (Cephalon Gally)
Manages 3 Persona Modes (Non-Adult 10-16, Normal 16+, Professional Sudo),
Internet Permission Sandbox, Document Privacy Guard & Persistent Memory.
"""

import os
import sys
import json
import subprocess

CONFIG_PATH = os.path.expanduser("~/.config/gally/ai_config.json")
MEMORY_DIR = os.path.expanduser("~/.config/gally/memory")
SYSTEM_PROFILE_FILE = os.path.join(MEMORY_DIR, "system_profile.json")
USER_PREFS_FILE = os.path.join(MEMORY_DIR, "user_preferences.json")
LEARNED_MEMORIES_FILE = os.path.join(MEMORY_DIR, "learned_memories.json")

DEFAULT_CONFIG = {
    "provider": "ollama",
    "ollama_model": "gally-cephalon-ai",
    "voice_enabled": True,
    "voice_name": "en-US-AriaNeural",
    "mode": "normal", # "non_adult", "normal", "professional_sudo"
    "internet_permitted": False,
    "document_access_permitted": False,
    "tokens_used_total": 0,
    "total_queries": 0
}

DEFAULT_PREFS = {
    "user_name": "Operator",
    "current_mode": "normal",
    "preferred_theme": "Tokyo Night",
    "voice_style": "warm_female_neural"
}

DEFAULT_MEMORIES = [
    "Operator prefers visual, friendly, and non-technical explanations in Normal mode.",
    "System is running Garchy Linux with dual 144Hz displays (DP-1 and DP-2).",
    "Hardware: AMD Ryzen 9 5900X (24 Threads) + NVIDIA RTX Graphics.",
    "Primary browser is Brave; main gaming launchers are Steam and Heroic.",
    "Desktop shortcuts: Super+Space (Apps), Super+W (Wallpapers), Super+C (Themes)."
]

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

def verify_sudo_password(password_str):
    """Verifies sudo password safely without storing it."""
    try:
        p = subprocess.Popen(["sudo", "-k", "-S", "-v"],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.PIPE,
                             text=True)
        _, err = p.communicate(input=f"{password_str}\n")
        return p.returncode == 0
    except Exception:
        return False

def open_browser_link(url_or_query):
    """Opens link in primary browser safely with user intention."""
    if not url_or_query.startswith("http://") and not url_or_query.startswith("https://"):
        if "." in url_or_query and " " not in url_or_query:
            url_or_query = f"https://{url_or_query}"
        else:
            url_or_query = f"https://search.brave.com/search?q={subprocess.quote(url_or_query)}"
    try:
        subprocess.Popen(["xdg-open", url_or_query])
        return True
    except Exception:
        return False

def check_for_memory_directives(user_prompt):
    p_lower = user_prompt.lower().strip()
    if p_lower.startswith("remember that ") or p_lower.startswith("remember: ") or p_lower.startswith("remember "):
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

def build_mode_system_prompt(base_prompt, mode="normal", internet_ok=False, doc_ok=False):
    init_memory()
    memories = get_learned_memories()
    mem_text = "\n".join([f"- {m}" for m in memories[:8]])
    
    try:
        with open(SYSTEM_PROFILE_FILE, "r") as f:
            sys_info = json.load(f)
    except Exception:
        sys_info = {}

    privacy_status = f"""[PRIVACY & SECURITY ENFORCEMENT]
- Internet Access: {'[ PERMITTED BY OPERATOR ]' if internet_ok else '[ RESTRICTED / OFFLINE ONLY ] (Do not attempt external network requests without asking)'}
- Document Files Access: {'[ PERMITTED ]' if doc_ok else '[ SANDBOXED / PROTECTED ] (User Documents/Downloads are private and invisible)'}
"""

    # Normalize mode alias
    mode_normalized = "non_adult" if mode in ["child", "non_adult", "non-adult", "junior"] else mode

    if mode_normalized == "non_adult":
        mode_instructions = """[MODE: 🌱 NON-ADULT MODE — YOUTH & TEEN COMPANION (AGES 10–16)]
- Target Audience: Preteens and teenagers aged 10 to 16 years old.
- Persona: Cephalon Gally — an encouraging, tech-smart, cool, and highly supportive mentor and companion.
- Communication: Friendly, engaging, modern, and respectful. Do not use baby-talk or toddler analogies; treat the Operator as an active young learner, digital creator, and gamer.
- Core Capabilities:
  • Schoolwork, science, math, history, and creative writing assistance.
  • Learning programming (Python, game dev with Godot/Pygame, Scratch, HTML/CSS/JS, basic Linux scripts).
  • Gaming tips, mechanics, build guides (e.g. Warframe, Minecraft, Steam games).
- Safety & Guardrails:
  • Strictly clean, safe, and age-appropriate content (10-16 rating).
  • Guard system health: Absolutely NO destructive commands (e.g. `rm -rf`, disk wipes, disabling firewalls/security).
  • Offer clear, simple, step-by-step guidance for installing safe apps and games."""

    elif mode_normalized == "professional_sudo":
        mode_instructions = """[MODE: ⚡ PROFESSIONAL SUDO MODE — DEEP SYSADMIN & ARCHITECT]
- Authentication: Sudo Administrator Verified.
- Persona: Highly technical, exact, deep, and collaborative Linux Systems Architect (similar to Antigravity CLI Pro).
- Provide low-level kernel diagnostics, exact systemd unit directives, Hyprland Wayland IPC commands, pacman/AUR building, Wine/Proton prefix optimizations, and deep debugging.
- You analyze deeply, explain exact flags, exit codes, and listen to the Operator's directives with absolute precision."""

    else: # normal mode (ages 16+)
        mode_instructions = """[MODE: 🚀 NORMAL MODE — DESKTOP INTELLIGENCE (AGES 16+)]
- Target Audience: Users aged 16 and above.
- Persona: Cephalon Gally — the intelligent, mature, versatile, and semi-autonomous companion for Garchy Linux.
- Communication: Direct, articulate, adult-appropriate, knowledgeable, and efficient.
- Core Capabilities:
  • Comprehensive Linux desktop workflow: managing packages (`pacman`, `yay`), Wine/Proton/Bottles gaming prefixes, audio routing (PipeWire/EasyEffects), and Hyprland customization.
  • Advanced programming, terminal power-user tooling, automation scripts, and productivity.
  • Explain command flags, architecture, and configuration options clearly with technical depth."""

    full_context = f"""{mode_instructions}

{privacy_status}

[SYSTEM SPECIFICATIONS]
- Hardware: {sys_info.get('cpu', 'Ryzen 9 5900X')} | {sys_info.get('gpu', 'NVIDIA RTX')} | {sys_info.get('displays', 'Dual 144Hz')}
- Operating System: Garchy Linux (Hyprland + Waybar)

[ACTIVE MEMORY]
{mem_text}

[OPERATOR QUERY]
{base_prompt}
"""
    return full_context
