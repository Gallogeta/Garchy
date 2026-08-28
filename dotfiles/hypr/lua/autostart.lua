-- ==============================================================================
-- 🌌 Garchy OS — System Daemons & Rice Autostart Pipeline
-- ==============================================================================

local home = os.getenv("HOME")

hl.on("hyprland.start", function()
    -- D-Bus and Systemd environment synchronization
    hl.exec_cmd("dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP=Hyprland")
    hl.exec_cmd("systemctl --user import-environment WAYLAND_DISPLAY XDG_CURRENT_DESKTOP")

    -- Core System Authentication & Bar
    hl.exec_cmd("/usr/lib/polkit-kde-authentication-agent-1")
    hl.exec_cmd("waybar")
    hl.exec_cmd("dunst")
    hl.exec_cmd("nm-applet --indicator")
    hl.exec_cmd("easyeffects --service-mode")

    -- Clipboard Daemon
    hl.exec_cmd("wl-paste --type text --watch cliphist store")
    hl.exec_cmd("wl-paste --type image --watch cliphist store")

    -- Dynamic Wallpaper Engine & Automation
    hl.exec_cmd("awww-daemon")
    hl.exec_cmd(home .. "/.config/hypr/scripts/wallpaper-timer.sh daemon 600")
    hl.exec_cmd(home .. "/.config/hypr/scripts/gally-drive-automount.py")
    hl.exec_cmd("python3 " .. home .. "/.config/hypr/scripts/gally-wallpaper-bridge.py")
end)
