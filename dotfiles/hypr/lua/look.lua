-- ==============================================================================
-- 🌌 Garchy OS — Look & Feel, Input, Decoration, and Tiling Layout
-- ==============================================================================

hl.config({
    ecosystem = {
        no_update_news = true,
        no_donation_nag = true,
    },
    input = {
        kb_layout = "ee",
        kb_options = "",
        follow_mouse = 1,
        sensitivity = 0,
        accel_profile = "flat", -- 1:1 Raw mouse sensor tracking for competitive gaming
        touchpad = {
            natural_scroll = false,
        },
    },
    general = {
        gaps_in = 4,
        gaps_out = 8,
        border_size = 2,
        col = {
            active_border = { colors = { "rgba(38bdf8ee)", "rgba(3b82f6ee)" }, angle = 45 },
            inactive_border = "rgba(0a0f1d88)",
        },
        resize_on_border = true,
        allow_tearing = true, -- Enables zero-latency tearing for games
        layout = "dwindle",
    },
    decoration = {
        rounding = 6,
        active_opacity = 1.0,
        inactive_opacity = 1.0,
        fullscreen_opacity = 1.0,
        blur = {
            enabled = true,
            size = 10,
            passes = 4,
            new_optimizations = true,
            ignore_opacity = true,
            xray = false,
            vibrancy = 0.35,
            contrast = 1.0,
            brightness = 0.85,
        },
        shadow = {
            enabled = true,
            range = 18,
            render_power = 3,
            color = "rgba(05081166)",
        },
    },
    dwindle = {
        preserve_split = true,
        smart_split = false,
        smart_resizing = true,
    },
    master = {
        new_status = "master",
    },
    misc = {
        disable_hyprland_logo = true,
        disable_splash_rendering = true,
        vrr = 2, -- VRR / Adaptive-Sync / G-Sync enabled for fullscreen games only
        mouse_move_enables_dpms = true,
        key_press_enables_dpms = true,
        focus_on_activate = true,
        mouse_move_focuses_monitor = false,
    },
    cursor = {
        no_hardware_cursors = 2,
        enable_hyprcursor = true,
        sync_gsettings_theme = true,
        no_warps = false,
    },
    xwayland = {
        force_zero_scaling = true,
    },
    render = {
        direct_scanout = 1, -- Direct GPU plane scanout (bypasses compositor in games)
    },
})
