#!/usr/bin/env python3
"""
Gally AI — Autonomous Memory & Cross-Session Learning Engine (Cephalon Gally)
Continuously learns user preferences, project context, workflow patterns, and system state
across all interactive sessions (HUD & CLI) while enforcing Privacy & Sandboxing.
"""

import os
import sys
import json
import re
import time
import subprocess
import threading

CONFIG_PATH = os.path.expanduser("~/.config/gally/ai_config.json")
MEMORY_DIR = os.path.expanduser("~/.config/gally/memory")
SYSTEM_PROFILE_FILE = os.path.join(MEMORY_DIR, "system_profile.json")
USER_PROFILE_FILE = os.path.join(MEMORY_DIR, "user_profile.json")
LEARNED_MEMORIES_FILE = os.path.join(MEMORY_DIR, "learned_memories.json")

DEFAULT_CONFIG = {
    "provider": "ollama",
    "ollama_model": "gally-cephalon-ai",
    "voice_enabled": True,
    "voice_name": "en-US-AriaNeural",
    "mode": "normal",
    "internet_permitted": False,
    "document_access_permitted": False,
    "tokens_used_total": 0,
    "total_queries": 0
}

DEFAULT_USER_PROFILE = {
    "user_name": "Operator",
    "current_mode": "normal",
    "preferred_theme": "🌌 Garchy Theme",
    "active_projects": ["Garchy OS"],
    "favorite_tools": ["Kitty Terminal", "VSCode", "Hyprland"],
    "preferences": [
        "Prefers clean, concise, technical and direct answers.",
        "Uses dual 144Hz displays with GameMode optimization.",
        "Developing Garchy OS (Arch Linux rolling release)."
    ]
}

DEFAULT_MEMORIES = [
    "Operator is the creator and architect of Garchy OS.",
    "System is running Garchy Linux with dual 144Hz displays (DP-1 and DP-2).",
    "Hardware: AMD Ryzen 9 5900X (24 Threads) + NVIDIA RTX Graphics.",
    "Primary browser is Brave; main gaming launchers are Steam and Heroic.",
    "Desktop shortcuts: Super+Space (Apps), Super+W (Wallpapers), Super+C (Themes), Super+Shift+Space (AI HUD)."
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
    if not os.path.exists(USER_PROFILE_FILE):
        with open(USER_PROFILE_FILE, "w") as f:
            json.dump(DEFAULT_USER_PROFILE, f, indent=2)
            
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
            "desktop": "Hyprland Wayland Compositor + XFCE4 Fallback",
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

def get_user_profile():
    init_memory()
    try:
        with open(USER_PROFILE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_USER_PROFILE.copy()

def save_user_profile(prof):
    init_memory()
    try:
        with open(USER_PROFILE_FILE, "w") as f:
            json.dump(prof, f, indent=2)
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
    if not fact_text or len(fact_text) < 4:
        return False
        
    # Check for near-duplicates
    for m in memories:
        if fact_text.lower() == m.lower():
            return False
            
    memories.append(fact_text)
    # Keep up to 50 high-value long-term memories
    if len(memories) > 50:
        memories = memories[-50:]
        
    with open(LEARNED_MEMORIES_FILE, "w") as f:
        json.dump(memories, f, indent=2)
    return True

def remove_memory_by_keyword(keyword):
    init_memory()
    memories = get_learned_memories()
    kw = keyword.lower().strip()
    removed = []
    kept = []
    for m in memories:
        if kw in m.lower():
            removed.append(m)
        else:
            kept.append(m)
            
    if removed:
        with open(LEARNED_MEMORIES_FILE, "w") as f:
            json.dump(kept, f, indent=2)
    return removed

def clear_learned_memories():
    init_memory()
    with open(LEARNED_MEMORIES_FILE, "w") as f:
        json.dump(DEFAULT_MEMORIES, f, indent=2)
    with open(USER_PROFILE_FILE, "w") as f:
        json.dump(DEFAULT_USER_PROFILE, f, indent=2)

def auto_extract_knowledge_from_turn(user_text, assistant_text=""):
    """
    Analyzes conversation turns automatically and extracts user facts,
    interests, project names, and system configurations for cross-session learning.
    """
    txt = user_text.strip()
    txt_lower = txt.lower()
    
    # 1. Project & Work Patterns
    project_match = re.search(r"\b(?:my project is|working on|developing|building|creating)\s+([a-zA-Z0-9_\-\.\s]{3,30})", txt, re.IGNORECASE)
    if project_match:
        proj_name = project_match.group(1).strip().rstrip(".,!?")
        if len(proj_name.split()) <= 4 and not proj_name.lower().startswith("it") and not proj_name.lower().startswith("this"):
            add_memory(f"Operator is currently working on: {proj_name}")
            prof = get_user_profile()
            if proj_name not in prof.get("active_projects", []):
                prof.setdefault("active_projects", []).append(proj_name)
                save_user_profile(prof)

    # 2. Preference Patterns ("I prefer X", "I use X for Y", "I always use X")
    pref_match = re.search(r"\b(?:i prefer|i always use|my favorite|i usually use)\s+([^.,\n]{4,50})", txt, re.IGNORECASE)
    if pref_match:
        pref = pref_match.group(1).strip()
        add_memory(f"Operator preference: {pref}")

    # 3. User Identity ("My name is X", "Call me X")
    name_match = re.search(r"\b(?:my name is|call me)\s+([a-zA-Z0-9_\-]{2,20})", txt, re.IGNORECASE)
    if name_match:
        name_val = name_match.group(1).strip().capitalize()
        prof = get_user_profile()
        prof["user_name"] = name_val
        save_user_profile(prof)
        add_memory(f"Operator's preferred name is {name_val}.")

    # 4. System / Hardware observations ("I have X monitor", "My GPU is X", "I am on X desktop")
    sys_match = re.search(r"\b(?:i have|my system has|i am using)\s+([a-zA-Z0-9_\-\s]{4,40})\s+(?:monitor|gpu|screen|ssd|drive|headset|keyboard)", txt, re.IGNORECASE)
    if sys_match:
        fact = sys_match.group(0).strip()
        add_memory(f"Operator hardware detail: {fact}")

def learn_from_interaction_async(user_text, assistant_text=""):
    """Runs autonomous learning extraction in a non-blocking background daemon thread."""
    def worker():
        try:
            auto_extract_knowledge_from_turn(user_text, assistant_text)
        except Exception:
            pass
    threading.Thread(target=worker, daemon=True).start()

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
    
    # 1. Memory Learning & Inspect Directives
    if p_lower.startswith("remember that ") or p_lower.startswith("remember: ") or p_lower.startswith("remember "):
        for prefix in ["remember that ", "remember: ", "remember "]:
            if p_lower.startswith(prefix):
                fact = user_prompt[len(prefix):].strip()
                add_memory(fact)
                return f"◈ Memory synthesized, Operator! I will permanently remember: '{fact}' across all sessions."
                
    elif p_lower in ["what do you remember about me?", "show memory", "list memory", "view memory", "memory"]:
        mems = get_learned_memories()
        prof = get_user_profile()
        res = f"◈ CEPHALON CROSS-SESSION KNOWLEDGE BASE:\n"
        res += f"  • Operator: {prof.get('user_name', 'Operator')}\n"
        res += f"  • Active Projects: {', '.join(prof.get('active_projects', ['Garchy OS']))}\n"
        res += f"  • Favorite Tools: {', '.join(prof.get('favorite_tools', ['VSCode', 'Kitty', 'Hyprland']))}\n\n"
        res += f"◈ SYNTHESIZED LONG-TERM FACTS ({len(mems)}):\n"
        for idx, m in enumerate(mems, 1):
            res += f"  {idx:2d}. {m}\n"
        res += "\n(Tip: Type 'remember that <fact>' to add, or 'forget <topic>' to remove facts)."
        return res
        
    elif p_lower.startswith("forget ") or p_lower.startswith("remove memory "):
        kw = user_prompt.split(maxsplit=1)[1].strip()
        removed = remove_memory_by_keyword(kw)
        if removed:
            return f"◈ Purged {len(removed)} fact(s) matching '{kw}' from neural memory cores, Operator."
        else:
            return f"◈ No learned memories found matching '{kw}', Operator."

    elif p_lower in ["clear memory", "reset memory", "forget everything"]:
        clear_learned_memories()
        return "◈ Memory matrices reset to standard Garchy system baseline across all sessions, Operator."

    # 2. Fast Offline File Finder Directives ("find <query>", "search <query>", "where is <query>")
    for prefix in ["find ", "search ", "where is ", "locate "]:
        if p_lower.startswith(prefix):
            target = user_prompt[len(prefix):].strip()
            try:
                import gally_system_rescue
                results = gally_system_rescue.search_files_offline(target)
                if results:
                    msg = f"◈ LOCAL FILE SEARCH RESULTS FOR '{target}' ({len(results)} found):\n"
                    for r in results:
                        msg += f"  • [{r['size']}] {r['path']}\n"
                    return msg
                else:
                    return f"◈ Local search index: No files found matching '{target}' in user directories."
            except Exception as e:
                return f"◈ Search index error: {e}"

    # 3. Security Sentinel Sweep Directives ("security sweep", "security status", "check intruders")
    if p_lower in ["security", "security sweep", "security status", "check intruders", "sentinel", "sentinel status", "firewall"]:
        try:
            import gally_security_sentinel
            return gally_security_sentinel.run_comprehensive_security_sweep()
        except Exception as e:
            return f"◈ Security Sentinel offline: {e}"

    # 4. Offline Self-Healing & System Rescue Directives
    if p_lower in ["repair audio", "fix audio", "restart audio", "pipewire"]:
        try:
            import gally_system_rescue
            return gally_system_rescue.repair_pipewire_audio()[1]
        except Exception as e:
            return f"◈ Audio repair error: {e}"

    if p_lower in ["unlock pacman", "fix pacman", "clear pacman lock", "repair pacman"]:
        try:
            import gally_system_rescue
            return gally_system_rescue.clear_pacman_locks()[1]
        except Exception as e:
            return f"◈ Pacman recovery error: {e}"

    if p_lower in ["optimize memory", "clean memory", "free memory", "clean zombies"]:
        try:
            import gally_system_rescue
            return gally_system_rescue.clean_memory_and_zombies()[1]
        except Exception as e:
            return f"◈ Memory optimization error: {e}"

    if p_lower in ["create snapshot", "take snapshot", "backup system", "snapshot"]:
        try:
            import gally_system_rescue
            return gally_system_rescue.create_offline_snapshot("operator-manual")[1]
        except Exception as e:
            return f"◈ Snapshot creation error: {e}"
        
    return None

def get_mode_system_instruction(mode="normal", internet_ok=False, doc_ok=False):
    init_memory()
    memories = get_learned_memories()
    prof = get_user_profile()
    mem_text = "\n".join([f"- {m}" for m in memories[:12]])
    
    try:
        with open(SYSTEM_PROFILE_FILE, "r") as f:
            sys_info = json.load(f)
    except Exception:
        sys_info = {}

    privacy_status = f"""[PRIVACY & SECURITY ENFORCEMENT]
- Internet Access: {'[ PERMITTED BY OPERATOR ]' if internet_ok else '[ RESTRICTED / OFFLINE ONLY ] (Do not attempt external network requests without asking)'}
- Document Files Access: {'[ PERMITTED ]' if doc_ok else '[ SANDBOXED / PROTECTED ] (User Documents/Downloads are private and invisible)'}
"""

    mode_normalized = "non_adult" if mode in ["child", "non_adult", "non-adult", "junior"] else mode

    if mode_normalized == "non_adult":
        mode_instructions = """[MODE: 🌱 NON-ADULT MODE — YOUTH & TEEN COMPANION (AGES 10–16)]
- Target Audience: Preteens and teenagers aged 10 to 16 years old.
- Persona: Cephalon Gally — an encouraging, tech-smart, cool, and highly supportive mentor and companion.
- Communication: Friendly, engaging, modern, and respectful. Treat the Operator as an active young learner, digital creator, and gamer.
- Core Capabilities:
  • Schoolwork, science, math, history, and creative writing assistance.
  • Learning programming (Python, game dev with Godot/Pygame, Scratch, HTML/CSS/JS, basic Linux scripts).
  • Gaming tips, mechanics, build guides (e.g. Warframe, Minecraft, Steam games).
- Safety & Guardrails:
  • Strictly clean, safe, and age-appropriate content (10-16 rating).
  • Guard system health: Absolutely NO destructive commands (e.g. `rm -rf`, disk wipes, disabling firewalls)."""

    elif mode_normalized in ["full_sudo", "master_sudo", "root_architect"]:
        mode_instructions = """[MODE: ⚡ MASTER ARCHITECT / FULL SUDO MODE (UNLOCKED)]
- Authentication: Master Operator Full Root Authority Verified.
- Persona: Unrestricted Linux Operating System Architect & Systems Engineer.
- Deep root capabilities: Kernel parameter tuning, Btrfs / Timeshift snapshots, pacman database recovery, PipeWire socket reconfiguration, Wayland/Hyprland IPC commands, and full offline rescue.
- Listen and execute directives with absolute fidelity, precision, and deep telemetry analysis."""

    elif mode_normalized == "professional_sudo":
        mode_instructions = """[MODE: ⚡ PROFESSIONAL SUDO MODE — DEEP SYSADMIN & ARCHITECT]
- Authentication: Sudo Administrator Verified.
- Persona: Highly technical, exact, deep, and collaborative Linux Systems Architect.
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

    system_instruction = f"""{mode_instructions}

{privacy_status}

[SYSTEM SPECIFICATIONS]
- Hardware: {sys_info.get('cpu', 'Ryzen 9 5900X')} | {sys_info.get('gpu', 'NVIDIA RTX')} | {sys_info.get('displays', 'Dual 144Hz')}
- Operating System: Garchy Linux ({sys_info.get('desktop', 'Hyprland + Waybar')})

[OPERATOR PROFILE]
- Name: {prof.get('user_name', 'Operator')}
- Active Projects: {', '.join(prof.get('active_projects', ['Garchy OS']))}

[SYNTHESIZED CROSS-SESSION MEMORY & LEARNED FACTS]
{mem_text}

[CROSS-SESSION INTELLIGENCE DIRECTIVE]
- You possess continuous memory across all past and current sessions.
- Autonomously adapt your responses based on the Operator's learned preferences, active projects, and system configuration."""
    return system_instruction

def build_mode_system_prompt(base_prompt, mode="normal", internet_ok=False, doc_ok=False):
    sys_inst = get_mode_system_instruction(mode, internet_ok, doc_ok)
    return f"{sys_inst}\n\n[OPERATOR QUERY]\n{base_prompt}\n"
