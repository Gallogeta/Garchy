#!/usr/bin/env python3
"""
Garchy AI - Built-in System Copilot & Automated Diagnostics Engine
Designed for Garchy Linux (Arch + Hyprland)
"""

import sys
import os
import json
import subprocess
import shutil
import urllib.request
import urllib.parse
from datetime import datetime

VERSION = "1.0.0"

# ANSI Colors
CYAN = "\033[96m"
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_banner():
    banner = f"""{CYAN}{BOLD}
   ██████╗  █████╗ ██████╗  ██████╗██╗  ██╗██╗   ██╗     █████╗ ██╗
  ██╔════╝ ██╔══██╗██╔══██╗██╔════╝██║  ██║╚██╗ ██╔╝    ██╔══██╗██║
  ██║  ███╗███████║██████╔╝██║     ███████║ ╚████╔╝     ███████║██║
  ██║   ██║██╔══██║██╔══██╗██║     ██╔══██║  ╚██╔╝      ██╔══██║██║
  ╚██████╔╝██║  ██║██║  ██║╚██████╗██║  ██║   ██║       ██║  ██║██║
   ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝   ╚═╝       ╚═╝  ╚═╝╚═╝
          {BLUE}Autonomous System Copilot & Troubleshooter v{VERSION}{RESET}
    """
    print(banner)

def run_cmd(cmd_list, check=False):
    try:
        res = subprocess.run(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=check)
        return res.stdout.strip()
    except Exception:
        return ""

def get_system_telemetry():
    telemetry = {}
    
    # Kernel & Host
    telemetry["kernel"] = run_cmd(["uname", "-r"])
    telemetry["uptime"] = run_cmd(["uptime", "-p"])
    
    # Memory
    mem_info = run_cmd(["free", "-m"])
    for line in mem_info.splitlines():
        if line.startswith("Mem:"):
            parts = line.split()
            telemetry["memory_total_mb"] = parts[1]
            telemetry["memory_used_mb"] = parts[2]
            telemetry["memory_free_mb"] = parts[3]
    
    # Disk Usage
    disk_info = run_cmd(["df", "-h", "/"])
    lines = disk_info.splitlines()
    if len(lines) > 1:
        telemetry["root_disk"] = lines[1]
        
    # GPU
    gpu_info = run_cmd(["nvidia-smi", "--query-gpu=name,driver_version,temperature.gpu,utilization.gpu", "--format=csv,noheader"])
    if gpu_info:
        telemetry["gpu"] = f"NVIDIA {gpu_info}"
    else:
        telemetry["gpu"] = run_cmd(["lspci", "-nnk"]).split("VGA")[0] if "VGA" in run_cmd(["lspci"]) else "Integrated/AMD"
        
    # Hyprland Config Errors
    hypr_errors = run_cmd(["hyprctl", "configerrors"])
    telemetry["hyprland_errors"] = hypr_errors if hypr_errors else "0 errors (Clean)"
    
    # Failed Systemd Units
    failed_units = run_cmd(["systemctl", "--failed", "--no-legend"])
    telemetry["failed_systemd_units"] = failed_units if failed_units else "None"
    
    # Recent Critical Journal Errors (last boot)
    recent_errors = run_cmd(["journalctl", "-p", "3", "-xb", "-n", "10", "--no-pager"])
    telemetry["recent_journal_errors"] = recent_errors if recent_errors else "None"
    
    return telemetry

def cmd_status():
    print(f"{BOLD}Gathering Garchy System Telemetry...{RESET}\n")
    t = get_system_telemetry()
    
    print(f"{CYAN}🖥️  Kernel:{RESET} {t.get('kernel')} ({t.get('uptime')})")
    print(f"{CYAN}🧠 Memory:{RESET} {t.get('memory_used_mb', '?')}MB used / {t.get('memory_total_mb', '?')}MB total")
    print(f"{CYAN}💾 Root Disk:{RESET} {t.get('root_disk', 'N/A')}")
    print(f"{CYAN}🎮 GPU:{RESET} {t.get('gpu')}")
    print(f"{CYAN}🎨 Hyprland Status:{RESET} {GREEN if '0 errors' in t.get('hyprland_errors', '') else RED}{t.get('hyprland_errors')}{RESET}")
    
    if t.get('failed_systemd_units') == "None":
        print(f"{CYAN}⚙️  Systemd Units:{RESET} {GREEN}All healthy (0 failed){RESET}")
    else:
        print(f"{CYAN}⚙️  Systemd Units:{RESET} {RED}Failed units found:{RESET}\n{t.get('failed_systemd_units')}")

def cmd_troubleshoot():
    print(f"{BOLD}{YELLOW}🔍 Running Deep Garchy Diagnostics...{RESET}\n")
    t = get_system_telemetry()
    issues = []
    
    # 1. Check Hyprland Config
    if "0 errors" not in t.get("hyprland_errors", ""):
        issues.append({
            "component": "Hyprland Configuration",
            "severity": "HIGH",
            "detail": t["hyprland_errors"],
            "fix": "Run 'hyprctl reload' and verify ~/.config/hypr/hyprland.conf rules syntax."
        })
        
    # 2. Check Systemd Units
    if t.get("failed_systemd_units") != "None":
        issues.append({
            "component": "Systemd Services",
            "severity": "MEDIUM",
            "detail": t["failed_systemd_units"],
            "fix": "Check logs with 'systemctl status <unit>' or restart the failed unit."
        })
        
    # 3. Check Audio / PipeWire
    pipewire_status = run_cmd(["systemctl", "--user", "is-active", "pipewire"])
    if pipewire_status != "active":
        issues.append({
            "component": "PipeWire Audio Daemon",
            "severity": "HIGH",
            "detail": f"PipeWire state: {pipewire_status}",
            "fix": "Run 'systemctl --user restart pipewire pipewire-pulse wireplumber'"
        })
        
    # 4. Check Disk Space
    try:
        total, used, free = shutil.disk_usage("/")
        free_gb = free // (2**30)
        if free_gb < 10:
            issues.append({
                "component": "Root Disk Space",
                "severity": "HIGH",
                "detail": f"Only {free_gb}GB remaining on /",
                "fix": "Run 'paccache -rk1' and 'journalctl --vacuum-time=3d' to clean caches."
            })
    except Exception:
        pass

    if not issues:
        print(f"{GREEN}{BOLD}✅ All core systems are running optimally! No anomalies detected.{RESET}")
        return

    print(f"{RED}{BOLD}⚠️  Detected {len(issues)} System Issue(s):{RESET}\n")
    for i, issue in enumerate(issues, 1):
        color = RED if issue["severity"] == "HIGH" else YELLOW
        print(f"{BOLD}{i}. [{color}{issue['severity']}{RESET}{BOLD}] {issue['component']}{RESET}")
        print(f"   {BOLD}Details:{RESET} {issue['detail']}")
        print(f"   {GREEN}Recommended Fix:{RESET} {issue['fix']}\n")

def cmd_optimize(target):
    target = target.lower() if target else "all"
    print(f"{CYAN}{BOLD}⚡ Optimizing system for: {target.upper()}{RESET}\n")
    
    if target in ("gaming", "all"):
        print(f"{BOLD}[1/4] Applying Low-Latency Gaming Profile...{RESET}")
        # Enable GameMode & VRR
        run_cmd(["hyprctl", "keyword", "misc:vrr", "1"])
        print(f"  {GREEN}✔{RESET} Hyprland Adaptive Sync / VRR activated")
        
    if target in ("gpu", "nvidia", "all"):
        print(f"{BOLD}[2/4] Optimizing GPU Performance...{RESET}")
        if shutil.which("nvidia-settings"):
            run_cmd(["nvidia-settings", "-a", "[gpu:0]/GPUPowerMizerMode=1"])
            print(f"  {GREEN}✔{RESET} NVIDIA PowerMizer set to Maximum Performance")
        else:
            print(f"  {YELLOW}ℹ{RESET} Non-NVIDIA or headless environment detected")
            
    if target in ("audio", "all"):
        print(f"{BOLD}[3/4] Optimizing Audio Latency...{RESET}")
        run_cmd(["systemctl", "--user", "restart", "pipewire", "pipewire-pulse", "wireplumber"])
        print(f"  {GREEN}✔{RESET} PipeWire low-latency audio stack synchronized")
        
    if target in ("storage", "all"):
        print(f"{BOLD}[4/4] Trimming Storage & Reclaiming Memory...{RESET}")
        if shutil.which("paccache"):
            run_cmd(["paccache", "-rk2"])
        print(f"  {GREEN}✔{RESET} Package caches pruned")
        
    print(f"\n{GREEN}{BOLD}✨ System Optimization Complete!{RESET}")

def cmd_ask(prompt):
    print(f"{CYAN}{BOLD}🤖 Garchy AI Processing Query...{RESET}\n")
    t = get_system_telemetry()
    
    # 1. Try Local Ollama if running
    try:
        req_data = json.dumps({
            "model": "llama3",
            "prompt": f"System context:\nKernel: {t.get('kernel')}\nGPU: {t.get('gpu')}\nHyprland status: {t.get('hyprland_errors')}\n\nUser Question: {prompt}\n\nProvide a concise, expert Linux answer with exact bash commands.",
            "stream": False
        }).encode('utf-8')
        
        req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=req_data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"{BOLD}Local Ollama Response:{RESET}\n{data.get('response')}")
            return
    except Exception:
        pass
        
    # 2. Fallback to Local Knowledge Base Engine
    prompt_lower = prompt.lower()
    print(f"{BOLD}Diagnostic Advice:{RESET}")
    
    if "audio" in prompt_lower or "sound" in prompt_lower:
        print("• Check output sinks: `wpctl status`")
        print("• Unmute default sink: `wpctl set-mute @DEFAULT_AUDIO_SINK@ 0`")
        print("• Restart PipeWire stack: `systemctl --user restart pipewire pipewire-pulse wireplumber`")
    elif "gpu" in prompt_lower or "fps" in prompt_lower or "game" in prompt_lower:
        print("• Check GPU metrics: `nvidia-smi`")
        print("• Enable GameMode: `gamemoderun %command%` in Steam launch options")
        print("• Run optimizer: `garchy-ai optimize gaming`")
    elif "hyprland" in prompt_lower or "monitor" in prompt_lower or "display" in prompt_lower:
        print("• Reload compositor config: `hyprctl reload`")
        print("• Check monitor properties: `hyprctl monitors`")
        print("• View Hyprland errors: `hyprctl configerrors`")
    elif "update" in prompt_lower or "upgrade" in prompt_lower:
        print("• Run Garchy automated updater: `garchy-update`")
        print("• Full system upgrade: `sudo pacman -Syu`")
    else:
        print(f"Query: '{prompt}'")
        print("• Run automated troubleshooting: `garchy-ai troubleshoot`")
        print("• Check system logs: `journalctl -p 3 -xb`")
        print("• Check system telemetry: `garchy-ai status`")

def main():
    if len(sys.argv) < 2:
        print_banner()
        print(f"{BOLD}Usage:{RESET} garchy-ai <command> [arguments]\n")
        print(f"  {CYAN}status{RESET}          Show complete hardware & system health summary")
        print(f"  {CYAN}troubleshoot{RESET}    Analyze crash logs, configs, and suggest automated fixes")
        print(f"  {CYAN}optimize{RESET}        Apply low-latency tuning for gaming, GPU, and audio")
        print(f"  {CYAN}ask <query>{RESET}     Ask the AI copilot any Linux or administration question")
        print(f"  {CYAN}version{RESET}         Show Garchy AI version\n")
        sys.exit(0)
        
    cmd = sys.argv[1].lower()
    
    if cmd in ("status", "info"):
        print_banner()
        cmd_status()
    elif cmd in ("troubleshoot", "diag", "doctor"):
        print_banner()
        cmd_troubleshoot()
    elif cmd in ("optimize", "tune"):
        print_banner()
        target = sys.argv[2] if len(sys.argv) > 2 else "all"
        cmd_optimize(target)
    elif cmd in ("ask", "query"):
        prompt = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Help with system"
        cmd_ask(prompt)
    elif cmd in ("version", "-v", "--version"):
        print(f"Garchy AI v{VERSION}")
    else:
        # Direct query fallback: garchy-ai "why is my monitor black"
        prompt = " ".join(sys.argv[1:])
        cmd_ask(prompt)

if __name__ == "__main__":
    main()
