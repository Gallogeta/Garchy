-- ==============================================================================
-- 🌌 Garchy OS — Keybindings & Interaction Matrix
-- ==============================================================================

local home = os.getenv("HOME")
local mainMod = "SUPER"

-- Core Launchers & AI Copilot
hl.bind(mainMod .. " + Space", hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/launchpad.sh"))
hl.bind(mainMod .. " + SHIFT + Space", hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/gally-ai-hud.sh"))
hl.bind(mainMod .. " + I", hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/gally-ai-hud.sh"))
hl.bind("F1", hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/help-hud.sh"))
hl.bind(mainMod .. " + slash", hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/help-hud.sh"))

-- Terminals & Browsers
hl.bind(mainMod .. " + Return", hl.dsp.exec_cmd(home .. "/.local/bin/garchy-terminal"))
hl.bind(mainMod .. " + T", hl.dsp.exec_cmd(home .. "/.local/bin/garchy-terminal"))
hl.bind(mainMod .. " + ALT + T", hl.dsp.exec_cmd(home .. "/.local/bin/cockpit"))
hl.bind(mainMod .. " + D", hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/rofi-launcher.sh"))
hl.bind(mainMod .. " + R", hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/rofi-launcher.sh"))
hl.bind(mainMod .. " + equal", hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/rofi-launcher.sh calc"))
hl.bind(mainMod .. " + E", hl.dsp.exec_cmd("thunar"))
hl.bind(mainMod .. " + B", hl.dsp.exec_cmd("brave"))
hl.bind(mainMod .. " + Y", hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/youtube-pip.sh"))

-- Window Management & Session Controls
hl.bind(mainMod .. " + P", hl.dsp.window.pin())
hl.bind(mainMod .. " + Q", hl.dsp.window.close())
hl.bind(mainMod .. " + SHIFT + Q", hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/force-kill.sh"))
hl.bind(mainMod .. " + SHIFT + Escape", hl.dsp.exec_cmd("hyprctl kill"))

-- Quick Menus & Overlays
hl.bind("ALT + Tab", hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/window-switch.sh"))
hl.bind(mainMod .. " + Tab", hl.dsp.exec_cmd("hyprlock"))
hl.bind(mainMod .. " + Escape", hl.dsp.exec_cmd("wlogout -b 2 -c 20 -r 20"))
hl.bind(mainMod .. " + W", hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/wallpaper-select.sh"))
hl.bind(mainMod .. " + SHIFT + W", hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/wallpaper-timer.sh random"))
hl.bind(mainMod .. " + ALT + W", hl.dsp.exec_cmd("quickshell -c hyprquickpaper"))
hl.bind(mainMod .. " + CTRL + R", hl.dsp.exec_cmd("sh -c 'killall waybar; hyprctl dispatch exec waybar'"))
hl.bind(mainMod .. " + O", hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/opacity.sh"))
hl.bind(mainMod .. " + V", hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/clipboard-manager.sh"))
hl.bind(mainMod .. " + SHIFT + V", hl.dsp.exec_cmd("kitty --class=gally_visualizer -e cava"))
hl.bind(mainMod .. " + C", hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/theme-switcher.sh"))
hl.bind(mainMod .. " + A", hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/easyeffects-menu.sh"))
hl.bind(mainMod .. " + SHIFT + A", hl.dsp.exec_cmd("easyeffects"))

-- Window Layout, Float & Fullscreen
hl.bind(mainMod .. " + ALT + Space", hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/togglefloat.sh"))
hl.bind(mainMod .. " + M", hl.dsp.window.fullscreen({ mode = 1 }))
hl.bind(mainMod .. " + F", hl.dsp.window.fullscreen({ mode = 0 }))
hl.bind(mainMod .. " + SHIFT + F", hl.dsp.window.fullscreen({ mode = 1 }))
hl.bind(mainMod .. " + G", hl.dsp.exec_cmd("hyprctl dispatch togglegroup"))
hl.bind(mainMod .. " + bracketleft", hl.dsp.exec_cmd("hyprctl dispatch changegroupactive b"))
hl.bind(mainMod .. " + bracketright", hl.dsp.exec_cmd("hyprctl dispatch changegroupactive f"))

-- Window Minimizing & Restoring
hl.bind(mainMod .. " + Down", hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/minimize-window.sh minimize"))
hl.bind(mainMod .. " + N", hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/minimize-window.sh minimize"))
hl.bind(mainMod .. " + SHIFT + Down", hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/minimize-window.sh minimize-all"))
hl.bind(mainMod .. " + SHIFT + Up", hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/minimize-window.sh restore-last"))
hl.bind(mainMod .. " + SHIFT + M", hl.dsp.exec_cmd("python3 " .. home .. "/.config/hypr/scripts/minimized-manager.py"))
hl.bind(mainMod .. " + SHIFT + N", hl.dsp.exec_cmd("python3 " .. home .. "/.config/hypr/scripts/minimized-manager.py"))
hl.bind(mainMod .. " + Z", hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/window-switch.sh"))
hl.bind(mainMod .. " + S", hl.dsp.workspace.toggle_special("magic"))
hl.bind(mainMod .. " + CTRL + S", hl.dsp.window.move({ workspace = "special:magic" }))

-- Screenshots (Grim + Slurp)
hl.bind(mainMod .. " + SHIFT + S", hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/screenshot.sh region"))
hl.bind("Print", hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/screenshot.sh full"))
hl.bind(mainMod .. " + Print", hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/screenshot.sh window"))

-- Mouse Window Control
hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag(), { mouse = true })
hl.bind(mainMod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true })

-- Exit Session
hl.bind(mainMod .. " + SHIFT + E", hl.dsp.exit())

-- Window Focus Navigation (Vim HJKL + Arrows)
hl.bind(mainMod .. " + H", hl.dsp.focus({ direction = "left" }))
hl.bind(mainMod .. " + L", hl.dsp.focus({ direction = "right" }))
hl.bind(mainMod .. " + K", hl.dsp.focus({ direction = "up" }))
hl.bind(mainMod .. " + J", hl.dsp.focus({ direction = "down" }))
hl.bind(mainMod .. " + Left", hl.dsp.focus({ direction = "left" }))
hl.bind(mainMod .. " + Right", hl.dsp.focus({ direction = "right" }))
hl.bind(mainMod .. " + comma", hl.dsp.focus({ monitor = -1 }))
hl.bind(mainMod .. " + period", hl.dsp.focus({ monitor = 1 }))

-- Move Active Window across Tiling & Monitors
hl.bind(mainMod .. " + SHIFT + comma", hl.dsp.window.move({ monitor = -1 }))
hl.bind(mainMod .. " + SHIFT + period", hl.dsp.window.move({ monitor = 1 }))
hl.bind(mainMod .. " + SHIFT + H", hl.dsp.window.move({ direction = "left" }))
hl.bind(mainMod .. " + SHIFT + L", hl.dsp.window.move({ direction = "right" }))
hl.bind(mainMod .. " + SHIFT + K", hl.dsp.window.move({ direction = "up" }))
hl.bind(mainMod .. " + SHIFT + J", hl.dsp.window.move({ direction = "down" }))
hl.bind(mainMod .. " + SHIFT + Left", hl.dsp.window.move({ direction = "left" }))
hl.bind(mainMod .. " + SHIFT + Right", hl.dsp.window.move({ direction = "right" }))

-- Resize Active Window (Hold to repeat)
hl.bind(mainMod .. " + CTRL + H", hl.dsp.window.resize({ x = -40, y = 0 }), { repeating = true })
hl.bind(mainMod .. " + CTRL + L", hl.dsp.window.resize({ x = 40, y = 0 }), { repeating = true })
hl.bind(mainMod .. " + CTRL + K", hl.dsp.window.resize({ x = 0, y = -40 }), { repeating = true })
hl.bind(mainMod .. " + CTRL + J", hl.dsp.window.resize({ x = 0, y = 40 }), { repeating = true })
hl.bind(mainMod .. " + CTRL + Left", hl.dsp.window.resize({ x = -40, y = 0 }), { repeating = true })
hl.bind(mainMod .. " + CTRL + Right", hl.dsp.window.resize({ x = 40, y = 0 }), { repeating = true })
hl.bind(mainMod .. " + CTRL + Up", hl.dsp.window.resize({ x = 0, y = -40 }), { repeating = true })
hl.bind(mainMod .. " + CTRL + Down", hl.dsp.window.resize({ x = 0, y = 40 }), { repeating = true })

-- Dual-Monitor Synchronized Navigation (Desktops 1..10)
for i = 1, 10 do
    local key = tostring(i % 10)
    hl.bind(mainMod .. " + " .. key, hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/dual-desktop.sh switch " .. i))
    hl.bind(mainMod .. " + SHIFT + " .. key, hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/dual-desktop.sh move " .. i))
end

-- Media Keys & Audio (PipeWire wpctl + media-control)
hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd("wpctl set-volume -l 1.5 @DEFAULT_AUDIO_SINK@ 5%+"), { locked = true })
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-"), { locked = true })
hl.bind("XF86AudioMute", hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"), { locked = true })
hl.bind("XF86AudioMicMute", hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle"), { locked = true })
hl.bind("XF86AudioPlay", hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/media-control.sh play-pause"), { locked = true })
hl.bind("XF86AudioNext", hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/media-control.sh next"), { locked = true })
hl.bind("XF86AudioPrev", hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/media-control.sh previous"), { locked = true })
hl.bind("XF86AudioStop", hl.dsp.exec_cmd(home .. "/.config/hypr/scripts/media-control.sh stop"), { locked = true })
