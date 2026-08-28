# Garchy Linux

<div align="center">

```
   ██████╗  █████╗ ██████╗  ██████╗██╗  ██╗██╗   ██╗
  ██╔════╝ ██╔══██╗██╔══██╗██╔════╝██║  ██║╚██╗ ██╔╝
  ██║  ███╗███████║██████╔╝██║     ███████║ ╚████╔╝ 
  ██║   ██║██╔══██║██╔══██╗██║     ██╔══██║  ╚██╔╝  
  ╚██████╔╝██║  ██║██║  ██║╚██████╗██║  ██║   ██║   
   ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝   ╚═╝   
```

**Minimalist, High-Performance Arch Linux and Hyprland Distribution with Built-in AI Copilot and Gaming/Dev Ready Stack.**

[![Arch Linux](https://img.shields.io/badge/Arch_Linux-1793D1?style=for-the-badge&logo=arch-linux&logoColor=white)](https://archlinux.org)
[![Hyprland](https://img.shields.io/badge/Hyprland-00AAFF?style=for-the-badge&logo=wayland&logoColor=white)](https://hyprland.org)
[![AI Powered](https://img.shields.io/badge/AI_Copilot-7AA2F7?style=for-the-badge&logo=openai&logoColor=white)](#gally-ai-3-tier-architecture)
[![Gaming Ready](https://img.shields.io/badge/Gaming-Ready-FF5555?style=for-the-badge&logo=steam&logoColor=white)](#gaming-and-high-performance-pipeline)

</div>

---

## Overview

Garchy Linux is a customized, ultra-responsive Arch Linux distribution built on a pure Lua Hyprland architecture. Engineered for competitive 144Hz gaming, software engineering, and local AI workflows, it delivers low latency, zero desktop stutter, and a clean frosted obsidian glass aesthetic.

---

## Architecture and Core Features

### 1. Quickshell GPU Launchpad
* **Hardware Acceleration**: Built with QtQuick and QML on Wayland layershell for high-framerate responsiveness.
* **Kinetic Momentum and Touch Drag**: Full physics-driven flickable scrolling with a 14px grabbable interactive scrollbar.
* **Vector Icon Engine**: Multi-tier icon indexer prioritizing Scalable Vector Graphics (SVG) and high-DPI assets with real-time fuzzy search.
* **GPU Frosted Blur**: Layered dual-kawase blur shader rendering over underlying windows and wallpapers.

### 2. Gaming and High-Performance Pipeline
* **Low-Latency Display Engine**: Configured with direct scanout (`direct_scanout = 1`), explicit tearing support (`allow_tearing = true`), and adaptive-sync (`vrr = 2`) for 144Hz gaming displays.
* **NVIDIA RTX 3000 Tuning**: Dedicated power management, shader caching, and isolated Vulkan WSI layer controls.
* **GameMode and MangoHud**: Automatic CPU governor switching, process renicing, and custom obsidian/gold 144Hz telemetry.
* **Modding Ready**: Pre-configured floating and rendering rules for Mod Organizer 2, FO4Edit, LOOT, BodySlide, and Proton prefixes.

### 3. Native Hyprland Lua Configuration
* **Modular Lua Layout**: Split across modular configurations in `~/.config/hypr/lua/` (`monitors`, `env`, `look`, `animations`, `autostart`, `keybinds`, `rules`).
* **Silent Window Minimization**: Direct Lua dispatchers sending windows to `special:minimized` without overlay capture, integrated with Waybar taskbar restore.
* **Dual 144Hz Monitor Sync**: Synchronized workspace switching across primary (DP-2) and secondary (DP-0) displays.

### 4. Gally AI 3-Tier Architecture
* **Tier 1 (Lightweight / Low-Latency)**: Qwen (`qwen2.5:0.5b`) for instant offline queries and command generation.
* **Tier 2 (Core System Copilot)**: Cephalon Gally (`gally-cephalon-ai`) for desktop control, log audits, and automation.
* **Tier 3 (Deep Reasoning)**: Hermes (`hermes3:8b` / OpenRouter Free Tier) for complex scripting and system diagnosis.

### 5. Desktop Environment Coexistence
* **Dual Desktop Support**: Seamlessly coexists with an XFCE4 secondary desktop environment while isolating XFCE internal settings applets from the Hyprland Launchpad.
* **Zero Indexer Background Policy**: GNOME Tracker and indexing daemons are masked to protect gaming frame pacing and CPU headroom.

---

## Keybindings Cheatsheet

| Shortcut | Action |
| :--- | :--- |
| **`Super + Space`** | Quickshell GPU App Launchpad |
| **`Super + Return`** / **`Super + T`** | Open Kitty Terminal |
| **`Super + D`** / **`Super + R`** | Open Rofi App Launcher |
| **`Super + B`** | Launch Browser (Brave) |
| **`Super + E`** | Open File Manager (Thunar) |
| **`Super + W`** | Interactive Wallpaper Selector |
| **`Super + Shift + W`** | Instantly Switch to Random Wallpaper |
| **`Super + C`** | Open Desktop Theme Switcher |
| **`Super + V`** | Open Clipboard History (Cliphist) |
| **`Super + Shift + S`** | Region Screenshot (Slurp + Grim) |
| **`Print`** | Fullscreen Screenshot |
| **`Super + 1..10`** | Synchronized Dual-Monitor Workspace Switch |
| **`Super + N`** | Minimize Active Window |
| **`Super + Shift + N`** | Restore All Minimized Windows |
| **`Super + Q`** | Close Active Window |
| **`Super + Shift + Q`** | Force Kill Unresponsive Application |
| **`Super + Escape`** | Power and Session Menu |

---

## Installation and Deployment

### Automated Dotfile Synchronization

To deploy the Garchy dotfiles to your user profile:

```bash
git clone https://github.com/Gallogeta/Garchy.git ~/Garchy
cd ~/Garchy
cp -r dotfiles/hypr dotfiles/quickshell dotfiles/waybar dotfiles/rofi dotfiles/kitty dotfiles/dunst ~/.config/
```

### Refreshing Application Index

After adding new software or updating desktop entries, rebuild the Launchpad vector cache:

```bash
python3 ~/.config/quickshell/launchpad/get_apps.py --refresh
```

---

## Strict 5-Color Obsidian Palette

* **Light Blue (`#38bdf8` / `#7dd3fc`)**: Active window borders, highlights, and primary icons.
* **Blue (`#3b82f6` / `#1d4ed8`)**: Button halos, gradients, and secondary accents.
* **Golden (`#fbbf24` / `#fde047`)**: Clock borders, window button cores, and AI launcher triggers.
* **Light Grey (`#e2e8f0` / `#cbd5e1`)**: Typography and active window labels.
* **Dark Grey (`#0a0f1d` / `#131c31` / `#1e293b`)**: Obsidian glass panels and background cards.

---

## License

Garchy Linux is open-source software licensed under the **MIT License**.
