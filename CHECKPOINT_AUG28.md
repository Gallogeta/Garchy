# 🌌 Garchy OS Development Checkpoint & Memory Log
**Date**: August 28, 2026  
**Project**: Garchy OS (Arch Linux Distribution with Cephalon Gally AI Copilot & 144Hz Gaming/Dev Stack)

---

## 📋 Executive Summary of Work Accomplished

In this milestone, we performed comprehensive system-wide memory optimizations targeting 4GB RAM machines, tuned dual displays to native 144Hz, introduced the Cephalon Gally AI 3-Tier neural architecture (setting lightweight Qwen as default), and delivered a complete ricing redesign for the Garchy Start Menu and 100% borderless top bar floating islands.

---

## 🛠️ Key Milestones & Architectures Implemented

### 1. ⚡ 4GB RAM Optimization & Bloat Elimination
* **Elimination of Heavy Background Software**:
  * Purged `surfshark` snap package, stopping its background daemons and removing all leftover user configs.
  * Disabled `com.sindresorhus.Caprine.desktop` from autostarting on boot.
  * Terminated orphaned Node.js/Vite/esbuild dev processes and disabled `docker.service` / `containerd.service` from autostarting.
* **Masked Indexing Daemons**:
  * Masked GNOME Evolution background daemons (`evolution-addressbook-factory`, `evolution-calendar-factory`, `evolution-source-registry`) and disabled Tracker/Localsearch, saving ~250MB RAM.
* **Panel Plugin & Wrapper Consolidation (`wrapper-2.0`)**:
  * Converted external Screenshooter and Power action plugins into native internal launchers.
  * Completely removed the weather plugin (`libweather.so`), reducing `wrapper-2.0` processes from 6 down to just 3, saving ~140MB RAM.
* **Picom Low-End GPU Tuning**:
  * Optimized dual-kawase blur (strength 5) and enabled `unredir-if-possible = true` to bypass compositing during full-screen games, keeping memory and VRAM lean.

### 2. 🖥️ Dual 144Hz Display Topology
* Configured both displays to **144.00Hz**:
  * **Primary (Left)**: `DP-2` (1920×1080 @ 144.00Hz, `+0+0`).
  * **Secondary (Right)**: `DP-0` (1920×1080 @ 144.00Hz, `+1920+0`).
* Enforced persistence via `~/.config/xfce4/xfconf/xfce-perchannel-xml/displays.xml` and executable `~/.xprofile`.

### 3. 🤖 Cephalon Gally AI 3-Tier Architecture (Qwen Default)
* Upgraded `gally_ai_router.py`, `ai_config.json`, and terminal CLI `ai`:
  * **⚡ Tier 1 (Fast & Lightweight - Default)**: `qwen2.5:0.5b` (<500MB RAM, instant response on 4GB machines).
  * **🌌 Tier 2 (Current Matrix)**: `gally-cephalon-ai` (system diagnostics & ricing persona).
  * **🚀 Tier 3 (High-Performing Free Tier)**: `hermes3:8b` via Ollama or OpenRouter free tier.
* Supported commands: `ai model qwen`, `ai model gally`, `ai model hermes`, `ai models`, `ai status`.

### 4. 🎨 Start Menu & Borderless Panel Ricing Redesign
* **Redesigned Garchy Start Menu (Whisker Menu)**:
  * Obsidian glassmorphic surface (`rgba(10, 15, 29, 0.96)`) with 16px corner radius, cyber-cyan neon border (`#38bdf8`), and deep drop shadow.
  * Floating search header card with golden halo (`#fbbf24`) on focus.
  * Category sidebar featuring an Orokin gold active indicator (`border-left: 3px solid #fbbf24`) and glowing gradient fills.
  * 10px rounded application glass cards with smooth hover transitions.
  * Glassmorphic action buttons for Lock, Logout, Settings with amber hover glows.
* **100% Borderless Panel Icons**:
  * Targeted main panel and external `GtkPlug` wrapper windows.
  * Stripped all inner borders, frames, and box-shadows from Start Menu Garchy shield, Gally AI, Theme Switcher, PulseAudio Volume, Screenshooter, Power, and Systray applets (Bluetooth, Network, Steam).

---

## 💾 Core Files Updated & Versioned

1. `/home/gallo/Garchy/CHECKPOINT_AUG28.md` — This milestone checkpoint log.
2. `/home/gallo/Garchy/CHECKPOINT_MEMORY.md` — Updated master project memory.
3. `/home/gallo/.config/gtk-3.0/gtk.css` & `/home/gallo/Garchy/dotfiles/gtk-3.0/gtk.css` — Redesigned Start Menu and borderless panel GTK styling.
4. `/home/gallo/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml` & `/home/gallo/Garchy/dotfiles/xfce4/` — Consolidated panel plugin layout without weather widget.
5. `/home/gallo/.config/xfce4/xfconf/xfce-perchannel-xml/displays.xml` & `/home/gallo/.xprofile` — Dual 144Hz display configurations.
6. `/home/gallo/.config/hypr/scripts/gally_ai_router.py` & `/home/gallo/.local/bin/ai` — 3-Tier Gally AI routing engine.
7. `/home/gallo/.config/picom/picom.conf` & `/home/gallo/Garchy/dotfiles/picom/` — Tuned Picom compositor profile.
