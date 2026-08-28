-- ==============================================================================
-- 🌌 Garchy OS — Master Hyprland Lua Configuration (v0.55+ / v0.56+ Native Architecture)
-- Hardware Profile: AMD Ryzen 9 5900X | NVIDIA RTX 3080 Ti | Dual 144Hz Displays
-- ==============================================================================

local config_dir = os.getenv("HOME") .. "/.config/hypr"
package.path = config_dir .. "/lua/?.lua;" .. config_dir .. "/?.lua;" .. package.path

-- 1. Monitors & Workspaces Topology (Dual 144Hz DP-2 & DP-1)
require("monitors")

-- 2. NVIDIA Driver & Wayland Environment Variables
require("env")

-- 3. Look & Feel, Input, Decoration and Tiling
require("look")

-- 4. 144Hz Snappy Bezier Animations
require("animations")

-- 5. System Daemons & Rice Autostart Pipeline
require("autostart")

-- 6. Keybindings, Navigation & Media Matrix
require("keybinds")

-- 7. Window Rules, Layer Blur & Gaming Compatibility
require("rules")
