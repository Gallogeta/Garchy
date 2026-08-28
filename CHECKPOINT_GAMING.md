# 🎮 Garchy OS — Gaming Mode & Gaming Compatibility Checkpoint

**Date**: August 28, 2026  
**System Profile**: Arch Linux / CachyOS Kernel (7.2.0-1-cachyos)  
**Hardware Topology**: AMD Ryzen 9 5900X (12C/24T) | NVIDIA GeForce RTX 3080 Ti | 32GB RAM | Dual 144Hz Displays (`DP-2`, `DP-0`)  

---

## ⚡ 1. Gaming Mode & System Compatibility Enhancements

### 🎯 Feral Interactive GameMode (`~/.config/gamemode.ini`)
* **CPU Tuning**: Sets governor to `performance` on game launch, disables core parking.
* **GPU Powerizer**: Automatically switches NVIDIA GeForce RTX 3080 Ti to `prefer-maximum-performance`.
* **Process Priority**: Renices game thread to high priority (`renice = 10`, `ioprio = 0`).
* **Desktop Notifications**: Dispatches animated notifications on game start/stop.
* **Screen Saver**: Automatically inhibits display sleep during active gameplay sessions.

### 🎨 Garchy OS MangoHud 144Hz Profile (`~/.config/MangoHud/MangoHud.conf`)
* **Visual Rice**: Styled using Garchy's strict 5-color palette:
  * Obsidian glass background (`#0a0f1d`, alpha `0.78`)
  * Cyber cyan GPU telemetry (`#38bdf8`) & Golden CPU metrics (`#fbbf24`)
  * Crisp silver/white typography (`#e2e8f0`)
* **Real-Time Telemetry**: Real-time FPS, frametime graph, VRAM, RAM, GPU Core Clock, and Temperatures.
* **144Hz Dynamics**: Dual FPS threshold indicators (`60`, `140`), `Shift_R + F12` instant toggle.

### 🚀 Universal Gaming Command (`~/.local/bin/garchy-game`)
* `garchy-game run <game>`: Wraps any executable with GameMode, DXVK async pipelines, and RTX 3080 Ti flags.
* `garchy-game status`: Live hardware telemetry, GPU power draw/temp, CPU governor, and 144Hz display links.
* `garchy-game fallout4`: One-click execution of Fallout 4 GOTY with F4SE and GameMode.
* `garchy-game hud on/off`: Toggle MangoHud session state.

---

## ☢️ 2. Fallout 4 GOTY 144Hz Modding Stack

### 📂 File Structure & Locations
* **Game Root**: `/run/media/gallo/GAME/Fallout4/Fallout 4 GOTY` (`/dev/sda1` ext4)
* **Proton Prefix**: `~/Games/Heroic/Prefixes/default/Fallout 4 Game of the Year Edition`
* **Mod Organizer 2**: `/run/media/gallo/GAME/Fallout4/ModOrganizer2`
* **F4SE Runtime**: v1.10.163 Pre-Next-Gen (Gold standard for F4SE mod compatibility)

### ⚙️ Engine & High FPS 144Hz Fixes
1. **High FPS Physics Fix (`Data/F4SE/Plugins/HighFPSPhysicsFix.ini`)**:
   * `UntieSpeedFromFPS = true` & `DisableiFPSClamp = true`
   * `DynamicUpdateBudget = true` & `BudgetMaxFPS = 144` (dynamically scales Papyrus script budget for smooth 144 FPS gameplay without script lag)
2. **Buffout 4**: Crash logging and memory address space fixes.
3. **X-Cell**: Multi-threaded cell loading, facegen bug prevention.
4. **Enhanced Launcher (`~/launch_fallout4.sh`)**:
   * Prioritizes `f4se_loader.exe` to run all F4SE mods smoothly.
   * Auto-detects and mounts `/dev/sda1` (`/run/media/gallo/GAME`) if unmounted.
   * Runner selection: `GE-Proton11-5` > `GE-Proton10-34` > `Proton 9.0 (Beta)`.
   * Passes `DXVK_ASYNC=1`, `PROTON_ENABLE_NVAPI=1`, and `gamemoderun`.

### 📦 Mod Auto-Ingestion Scripts
* `~/auto_install_fallout_mods.sh`: Scans `~/Downloads` for mod archives (.zip, .7z, .rar) and cleanly unpacks them directly into Mod Organizer 2's mods directory.
* `~/install_downloaded_mods.sh`: Automated extractor for batch downloads.

---

## 🪟 3. Desktop Compositor Gaming Integration

* **XFCE4 / Picom**: `unredir-if-possible = true` allows fullscreen games to completely bypass the X11 compositor, eliminating input latency.
* **Hyprland**: Dedicated gaming rules (`immediate = 1` for zero tearing latency, opacity overrides, workspace assignment to primary 144Hz display `DP-2`).
