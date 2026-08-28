-- ==============================================================================
-- 🌌 Garchy OS — NVIDIA RTX 3080 Ti & Wayland Gaming Environment Variables
-- ==============================================================================

-- Cursor Defaults
hl.env("XCURSOR_SIZE", "24")
hl.env("HYPRCURSOR_SIZE", "24")

-- NVIDIA Hardware Acceleration & Direct Backend
hl.env("LIBVA_DRIVER_NAME", "nvidia")
hl.env("__GLX_VENDOR_LIBRARY_NAME", "nvidia")
hl.env("NVD_BACKEND", "direct")
hl.env("AQ_DRM_DEVICES", "/dev/dri/card1")
hl.env("GBM_BACKEND", "nvidia-drm")
hl.env("XDG_SESSION_TYPE", "wayland")

-- NVIDIA G-Sync / VRR & Low Latency
hl.env("__GL_VRR_ALLOWED", "1")
hl.env("__GL_GSYNC_ALLOWED", "1")
hl.env("DISABLE_GAMESCOPE_WSI", "1") -- Prevents Gamescope layer error spam outside of gamescope sessions

-- Proton, DXVK & Wine Game Compatibility Flags
hl.env("DXVK_ASYNC", "1")
hl.env("DXVK_STATE_CACHE", "1")
hl.env("PROTON_ENABLE_NVAPI", "1")
hl.env("PROTON_HIDE_NVIDIA_GPU", "0")
hl.env("__GL_SHADER_DISK_CACHE", "1")
hl.env("__GL_SHADER_DISK_CACHE_SKIP_CLEANUP", "1")

-- Toolkit Hints (GTK, Qt, Electron, SDL)
hl.env("ELECTRON_OZONE_PLATFORM_HINT", "auto")
hl.env("QT_QPA_PLATFORM", "wayland;xcb")
hl.env("QT_WAYLAND_DISABLE_WINDOWDECORATION", "1")
hl.env("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
hl.env("MOZ_ENABLE_WAYLAND", "1")
hl.env("GDK_BACKEND", "wayland,x11,*")
hl.env("SDL_VIDEODRIVER", "wayland")
hl.env("CLUTTER_BACKEND", "wayland")
