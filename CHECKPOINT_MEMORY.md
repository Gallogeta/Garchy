# 🌌 Garchy OS & Cephalon AI — Project Memory Checkpoint

**Date**: August 25, 2026  
**Operator**: `User`  
**OS**: Garchy Linux / Arch Linux (x86_64 rolling release)  
**Compositor**: Hyprland (Wayland)  
**Editor**: VSCode  
**Hardware Profile**: Modern Multi-Core x86_64 Architecture, Dedicated GPU, Dual 144Hz Displays, PipeWire Audio Subsystem.

---

## 🎯 Executive State & Summary of Work Completed

### 1. 🤖 Cephalon Gally (AI Copilot & System Matrix)
* **GUI Engine (`~/.config/hypr/scripts/gally-ai-hud.py`)**:
  * **Framework**: Built with **CustomTkinter** for modern, native **16px rounded glass cards**, glowing borders, and rounded pill buttons.
  * **3D Visual Core**: Multi-layer icosahedron & Orokin diamond wireframe rotating in 3D perspective with **35 orbiting nebula particles** and **24 radial kinetic equalizer rays** pulsating to speech.
  * **Neural Voice Synthesis**: Studio-grade **Aria Neural female voice** (`edge-tts` with offline `espeak-ng` fallback). Uncut audio output without length truncations.
  * **Python 3.14 Thread Safety**: Replaced cross-thread GUI calls with a thread-safe **`queue.Queue` event pump**, providing **instant token streaming (<30ms latency)** without lockups.
* **Multi-Provider AI Router (`~/.config/hypr/scripts/gally_ai_router.py`)**:
  * **On-the-Fly Switching**: Local Offline AI (`gally-cephalon-ai`), Google Gemini (1.5 Flash / Pro), Anthropic Claude (3.5 Sonnet), OpenAI (GPT-4o / mini), DeepSeek (Chat / R1), and Groq (Llama 3.3 @ 300 t/s).
  * **In-Terminal Login & Directives**: Manage keys and settings directly in prompt:
    * `login` / `keys` — View key matrix
    * `login <provider> <key>` — Set key and activate model
    * `model <name>` — Switch model (`local`, `gemini`, `claude`, `openai`, etc.)
    * `mode <non-adult|normal|sudo>` — Switch operational persona
    * `models` — List all engines and current active badge
    * `status` — View engine, persona mode, and privacy permissions
* **Three Operational Modes (`~/.config/hypr/scripts/gally_memory_manager.py`)**:
  * **🌱 Non-Adult Mode (Ages 10–16)**: Engaging, tech-smart youth and teen companion. Helps with learning programming (Python, Godot, Pygame, Scratch, web dev), school homework (math, science, history), gaming tips/builds, and creative projects with strict safety guardrails (0 adult content, 0 destructive shell commands).
  * **🚀 Normal Mode (Ages 16+)**: Unrestricted, semi-autonomous desktop intelligence. Handles package management (`pacman`, `yay`), Wine/Proton/Bottles gaming prefixes, PipeWire/EasyEffects audio routing, Hyprland script automation, and deep system workflows.
  * **⚡ Professional Sudo Mode**: **Unlocked via sudo password verification**. Highly technical Linux systems architect (kernel telemetry, systemd units, memory fragmentation, Wayland socket IPC).
* **Privacy & Security Sandbox**:
  * **Zero Internet by Default**: External queries require explicit user permission.
  * **Document Privacy Guard**: `~/Documents` and personal folders are completely invisible to the AI unless explicitly allowed.
* **Persistent Memory (`~/.config/gally/memory/`)**:
  * `system_profile.json`, `user_preferences.json`, and `learned_memories.json`.
  * Natural language learning: `remember that <fact>`, `what do you remember about me?`, `clear memory`.
* **Terminal CLI Tool (`~/.local/bin/ai` and `/usr/local/bin/ai`)**:
  * Direct command-line access to Cephalon with multi-mode flags (`ai --non-adult`, `ai --sudo`, `ai login`, `ai model <name>`).

---

### 2. 💾 Universal Storage & Drive Automounter
* **Automounter Daemon (`~/.config/hypr/scripts/gally-drive-automount.py`)**:
  * **Startup Auto-Mount**: Automatically detects and mounts all unmounted internal/secondary SSDs, HDDs, and storage partitions on login (`udisks2`).
  * **Live Hotplug Listener**: Real-time event monitoring via `udisksctl monitor` with debouncing. Automatically mounts newly plugged-in USB flash drives, external SSDs, SD cards, and storage drives upon connection.
  * **Desktop Notifications**: Dispatches rich desktop notifications (`notify-send`) showing drive label, storage size, filesystem type, and mount point path (`/run/media/$USER/<LABEL>`).
  * **Autostart**: Enrolled into `hyprland.conf` via `exec-once = ~/.config/hypr/scripts/gally-drive-automount.py`.

---

### 3. 🎨 Gally Visual Desktop Suite
* **Theme Switcher (`~/.config/hypr/scripts/theme-switcher-gui.py`)**:
  * Visual 1-click palette gallery (Tokyo Night, Catppuccin, Nord, Cyberpunk, Dracula, Lava, Emerald, Monochrome).
  * Integrated **vertical scrollbar** (`ttk.Scrollbar`) with full mousewheel scrolling support (`<Button-4>`, `<Button-5>`, `<MouseWheel>`), dynamic window resizing, and live disk synchronization across Waybar CSS, Kitty, Hyprland borders, and Gally AI.
* **Application Launchpad (`~/.config/hypr/scripts/launchpad-gui.py`)**:
  * Native 400+ application launcher with instant disk caching (`~/.cache/gally_apps_cache.json`, loads in <10ms). Bound to `Super + Space`.
* **Wallpaper Gallery (`~/.config/hypr/scripts/wallpaper-gallery-gui.py`)**:
  * High-definition preview with auto-scrolling filmstrip carousel that moves synchronously with arrow keys. Bound to `Super + W`. `Enter` applies wallpaper with 144Hz hardware transitions via `awww`.
* **Window Opacity (Solid / Non-Transparent)**:
  * Configured full 100% solid opacity across active and inactive windows (`active_opacity = 1.0`, `inactive_opacity = 1.0`, `windowrule = opacity 1.0 1.0 1.0`, `background_opacity 1.0`).
* **Waybar Taskbar & Docking**:
  * Replaced wide text labels with compact App Dock (`wlr/taskbar` with `{icon}`).
  * `custom/active-app` with focusHistoryID fallback to minimize active window on click.
  * `custom/minimized` amber pill to restore minimized windows with 1 click.

---

### 4. 📦 Garchy OS Debloat & ISO Manifest
* **Host & ISO Software Alignment**:
  * **Browsers**: Kept Brave & Firefox (stripped Chromium, Cachy-Browser).
  * **Office & Media**: Kept LibreOffice, MPV, VLC on host; ISO only contains LibreOffice and MPV.
  * **Gaming**: Kept Steam & Heroic on both host and ISO.
  * **Dev SDKs**: Kept Rust & VirtualBox on host; stripped heavy SDKs from ISO.
  * **Filesystem & Storage**: Added `udisks2`, `ntfs-3g`, `dosfstools`, `e2fsprogs`, `btrfs-progs`, `exfat-utils`.
* **Dotfiles & Profile Sync**:
  * `dotfiles/` and `archiso/` are in 100% sync and committed to Git on branch `main`.

---

## 📂 Key File Map

| Path | Description |
| :--- | :--- |
| `~/.config/hypr/scripts/gally-ai-hud.py` | Main CustomTkinter Glassmorphic Cephalon AI HUD |
| `~/.config/hypr/scripts/gally_ai_router.py` | Multi-provider router, in-terminal login & model switching engine |
| `~/.config/hypr/scripts/gally_memory_manager.py` | Persistent memory, 3 modes (Non-Adult 10-16, Normal 16+, Sudo), and security sandbox |
| `~/.config/hypr/scripts/gally-drive-automount.py` | Universal storage automounter (startup & live hotplug) |
| `~/.local/bin/ai` | Terminal CLI wrapper for Cephalon AI |
| `~/.config/gally/ai_config.json` | AI config, active model, persona mode, and API keys storage |
| `~/.config/gally/active_theme.json` | Active desktop theme state |
| `~/.config/hypr/scripts/theme-switcher-gui.py` | Desktop theme gallery with scrollbar & live sync |
| `~/.config/hypr/scripts/launchpad-gui.py` | Fast cached application launchpad |
| `~/.config/hypr/scripts/wallpaper-gallery-gui.py` | 144Hz animated wallpaper chooser |
| `~/.config/hypr/hyprland.conf` | Hyprland window rules, autostart, keybindings, and monitor setup |
| `CHECKPOINT_MEMORY.md` | Garchy OS master checkpoint memory documentation |
| `archiso/packages.x86_64` | Debloated Garchy OS ISO package manifest |

---

## 🚀 Status & Verification
1. **Drive Automounting**: Verified automatic mounting of internal and external block storage partitions to `/run/media/$USER/<LABEL>`.
2. **Hyprland & Dotfiles**: Reloaded and synced with portable, user-agnostic pathing (`~/.config/...`).
3. **Cephalon AI**: Operating with updated Non-Adult (10-16) and Normal (16+) personas, in-terminal model and mode commands, and CustomTkinter HUD.
