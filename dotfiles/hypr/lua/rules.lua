-- ==============================================================================
-- 🌌 Garchy OS — Window Rules, Frosted Layer Rules & Gaming Compatibility
-- ==============================================================================

-- Layer Rules (Frosted Blur for Bars, Overlays & Quickshell Launchpad)
hl.layer_rule({ match = { namespace = "^(waybar|rofi|wlogout|dunst|quickshell|launchpad)$" }, blur = true, ignore_alpha = 0.1, xray = false })
hl.layer_rule({ match = { namespace = "launchpad" }, blur = true, ignore_alpha = 0.1, xray = false })

-- Global Maximize Suppression
hl.window_rule({ name = "suppress-maximize", match = { class = "^(.*)$" }, suppress_event = "maximize" })

-- Opacity Override for Primary Glassmorphic Applications
hl.window_rule({
    name = "app-opacity",
    match = {
        class = "^(kitty|xed|thunar|[bB]rave-browser|firefox|discord|vesktop|codium|Code|code-oss|GeForceNOW|obsidian|Spotify|spotify|org\\.pulseaudio\\.pavucontrol|com\\.github\\.johnfactotum\\.Foliate)$",
    },
    opacity = "1.0 1.0 1.0",
})

-- System Dialogs & Floating Windows
hl.window_rule({
    name = "float-system-dialogs",
    match = {
        class = "^(pavucontrol|nm-connection-editor|blueman-manager|org\\.pulseaudio\\.pavucontrol)$",
    },
    float = true,
    center = true,
    size = { 700, 500 },
})

hl.window_rule({
    name = "float-file-pickers",
    match = {
        title = "^(Open File|Save File|Authentication Required|Confirm to replace files|File Upload|All Files)$",
    },
    float = true,
    center = true,
})

-- Garchy OS HUDs & Visual Galleries
hl.window_rule({
    name = "garchy-help-hud",
    match = { title = "^(Garchy OS — Quick Help & Shortcuts)$" },
    float = true,
    center = true,
    size = { 740, 520 },
})

hl.window_rule({
    name = "gally-ai-hud",
    match = {
        class = "^(gally_cephalon_hud|Gally_cephalon_hud)$",
    },
    float = true,
    center = true,
    size = { 1040, 740 },
    rounding = 16,
    opacity = "1.0 1.0",
})

hl.window_rule({
    name = "gally-launchpad",
    match = {
        class = "^(gally_launchpad|Gally_launchpad)$",
    },
    float = true,
    center = true,
    size = { 900, 640 },
})

hl.window_rule({
    name = "gally-theme-gallery",
    match = { title = "^(Gally OS — Visual Theme Gallery)$" },
    float = true,
    center = true,
    size = { 820, 620 },
})

hl.window_rule({
    name = "gally-wallpaper-gallery",
    match = {
        class = "^(gally_wallpaper_gallery|Gally_wallpaper_gallery)$",
    },
    float = true,
    center = true,
    size = { 940, 680 },
})

hl.window_rule({
    name = "gally-visualizer",
    match = { class = "^(gally_visualizer)$" },
    float = true,
    center = true,
    size = { 860, 380 },
})

hl.window_rule({
    name = "garchy-installer",
    match = { title = "^(Garchy OS — Graphical System Installer)$" },
    float = true,
    center = true,
    size = { 780, 540 },
})

-- Modding Tools & Launchers (Mod Organizer 2, FO4Edit, LOOT, BodySlide, Heroic, Steam)
hl.window_rule({
    name = "modding-utilities-float",
    match = {
        class = "^(ModOrganizer\\.exe|FO4Edit\\.exe|xEdit\\.exe|BodySlide\\.exe|CreationKit\\.exe|LOOT\\.exe|LOOT)$",
    },
    float = true,
    center = true,
    opacity = "1.0 1.0",
})

hl.window_rule({
    name = "steam-friends-dialogs",
    match = {
        class = "^(Steam|steam)$",
        title = "^(Friends List|Special Offers|Steam Settings|Screenshot Uploader|Game Servers|Properties - .*)$",
    },
    float = true,
    center = true,
})

-- Gaming, Launchers & Emulators (Assigned to Left Monitor DP-2 @ 144Hz, Zero Latency Tearing)
hl.window_rule({
    name = "gaming-compatibility-monitor",
    match = {
        class = "^(steam_app_.*|gamescope|lutris|heroic|retroarch|net\\.pcsx2\\.PCSX2|net\\.rpcs3\\.RPCS3|org\\.DolphinEmu\\.dolphin-emu|org\\.ppsspp\\.PPSSPP|info\\.cemu\\.Cemu|duckstation|io\\.github\\.ryubing\\.Ryujinx|Soulframe.*|launcher\\.exe|Soulframe\\.x64\\.exe|wine|wine64|.*\\.exe)$",
    },
    monitor = "DP-2",
    workspace = 1,
    opacity = "1.0 override 1.0 override",
})

hl.window_rule({
    name = "gaming-immediate-tearing",
    match = {
        class = "^(steam_app_.*|gamescope|Soulframe.*|launcher\\.exe|Soulframe\\.x64\\.exe|.*\\.exe)$",
    },
    immediate = 1,
})

hl.window_rule({
    name = "gaming-idle-inhibit",
    match = {
        class = "^(steam_app_.*|gamescope|lutris|heroic|retroarch|net\\.pcsx2\\.PCSX2|net\\.rpcs3\\.RPCS3|org\\.DolphinEmu\\.dolphin-emu|org\\.ppsspp\\.PPSSPP|info\\.cemu\\.Cemu|duckstation|io\\.github\\.ryubing\\.Ryujinx|Soulframe.*|launcher\\.exe|Soulframe\\.x64\\.exe|wine|wine64|.*\\.exe)$",
    },
    idle_inhibit = "always",
})

-- Fallout 4 GOTY & F4SE Borderless 144Hz Rules
hl.window_rule({
    name = "fallout4-gameplay-rule",
    match = {
        class = "^([Ff]allout4\\.exe|[Ff]4se_loader\\.exe|steam_app_377160)$",
    },
    monitor = "DP-2",
    workspace = 1,
    immediate = 1,
    fullscreen = 0,
    idle_inhibit = "always",
    opacity = "1.0 override 1.0 override",
})

-- Picture-in-Picture & Floating Media (Always on Top)
hl.window_rule({
    name = "pip-video",
    match = {
        title = "^(Picture-in-Picture|Picture in picture|Picture in Picture|mpv-pip)$",
    },
    float = true,
    pin = true,
    size = { 720, 405 },
})
