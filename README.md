# 🌌 Garchy Linux

<div align="center">

```
   ██████╗  █████╗ ██████╗  ██████╗██╗  ██╗██╗   ██╗
  ██╔════╝ ██╔══██╗██╔══██╗██╔════╝██║  ██║╚██╗ ██╔╝
  ██║  ███╗███████║██████╔╝██║     ███████║ ╚████╔╝ 
  ██║   ██║██╔══██║██╔══██╗██║     ██╔══██║  ╚██╔╝  
  ╚██████╔╝██║  ██║██║  ██║╚██████╗██║  ██║   ██║   
   ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝   ╚═╝   
```

**Minimalist, High-Performance Arch Linux + Hyprland Distribution with Built-in AI Copilot & Gaming/Dev Ready Stack.**

[![Arch Linux](https://img.shields.io/badge/Arch_Linux-1793D1?style=for-the-badge&logo=arch-linux&logoColor=white)](https://archlinux.org)
[![Hyprland](https://img.shields.io/badge/Hyprland-00AAFF?style=for-the-badge&logo=wayland&logoColor=white)](https://hyprland.org)
[![AI Powered](https://img.shields.io/badge/AI_Copilot-7AA2F7?style=for-the-badge&logo=openai&logoColor=white)](#-built-in-ai-copilot-garchy-ai)
[![Gaming Ready](https://img.shields.io/badge/Gaming-Ready-FF5555?style=for-the-badge&logo=steam&logoColor=white)](#-gaming--development-ready)

</div>

---

## ⚡ Highlights

* 🤖 **Built-in AI Copilot (`garchy-ai` / `ai`)**: Deep OS diagnostics, automated log analysis, configuration repairs, and hardware tuning out of the box.
* 🚀 **Zero-Bloat & Ultra-Minimal**: Boots under **800 MB RAM**, optimized kernel schedulers for low latency and high FPS.
* 🎮 **Gaming Ready**: Pre-configured with Steam, Proton-GE, Gamescope, MangoHud, and Hyprland zero-latency tearing rules.
* 💻 **Developer Ready**: Pre-packaged with Docker, Git, VSCode, Zsh + Starship prompt, and modern dev toolchains.
* 🛡️ **Silent Self-Healing Updates**: Unattended background updates guarded by automated **Btrfs + Snapper** snapshots for instant rollback.
* 🖥️ **Dual 144Hz Monitor Support**: Hardware-accelerated paired workspaces (left/right displays synchronized).
* 🎨 **Dynamic 10-Minute Wallpaper Rotation**: Built-in daemon (`awww`) with smooth animated transitions.

---

## 🚀 Quick Install (1-Line Bootstrap)

If you already have a clean Arch Linux install, you can deploy the full **Garchy** desktop, AI assistant, and gaming/dev environment with one command:

```bash
curl -sS https://raw.githubusercontent.com/Gallogeta/Garchy/main/install.sh | bash
```

---

## 💿 Live ISO Installation

1. Download the latest bootable ISO from the **[GitHub Releases](https://github.com/Gallogeta/Garchy/releases)** page.
2. Flash to a USB drive using **Ventoy**, **BalenaEtcher**, or `dd`:
   ```bash
   sudo dd if=garchy-x86_64.iso of=/dev/sdX bs=4M status=progress oflag=sync
   ```
3. Boot the USB and run the installer.

---

## 🤖 Built-in AI Copilot (`garchy-ai`)

Garchy comes with an autonomous system diagnostic and troubleshooting engine:

```bash
# Check full system telemetry (Kernel, RAM, GPU, Hyprland, Systemd units)
garchy-ai status

# Deep diagnostic scan (detects failed services, audio issues, config errors)
garchy-ai troubleshoot

# Apply performance optimizations (gaming, gpu, audio, storage)
garchy-ai optimize gaming

# Ask the AI copilot any Linux or administration question
garchy-ai ask "how do I configure isolated bridge networking for KVM?"
```

---

## ⌨️ Keybindings Cheatsheet

| Shortcut | Action |
| :--- | :--- |
| **`Super + Return`** / **`Super + T`** | Open Kitty Terminal |
| **`Super + D`** / **`Super + R`** | Open Rofi App Launcher |
| **`Super + B`** | Launch Browser (Brave) |
| **`Super + E`** | Open File Manager (Thunar) |
| **`Super + W`** | Interactive Wallpaper Selector (Rofi) |
| **`Super + Shift + W`** | Instantly Switch to Random Wallpaper |
| **`Super + Alt + W`** | Open Quickshell Wallpaper Gallery |
| **`Super + C`** | Open Desktop Theme Switcher |
| **`Super + V`** | Open Clipboard History (Cliphist) |
| **`Super + Shift + S`** | Region Screenshot (Slurp + Grim) |
| **`Print`** | Fullscreen Screenshot |
| **`Super + 1..10`** | Synchronized Dual-Monitor Desktop Switch |
| **`Super + N`** | Minimize Active Window |
| **`Super + Shift + N`** | Restore All Minimized Windows |
| **`Super + Q`** | Close Active Window |
| **`Super + Shift + Q`** | Force Kill Unresponsive App |
| **`Super + Escape`** | Power Menu (Wlogout) |

---

## 🛠️ Local ISO Build

To build your own customized ISO image locally:

```bash
git clone https://github.com/Gallogeta/Garchy.git
cd Garchy
./build-iso.sh
```

The output bootable `.iso` will be generated in `./out/`.

---

## 📄 License

Garchy Linux is open-source under the **MIT License**.
