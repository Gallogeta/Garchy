-- ==============================================================================
-- 🌌 Garchy OS — Monitors & Paired Dual-144Hz Workspaces
-- ==============================================================================

-- Display Topology: Left Monitor DP-2 (Primary @ 144Hz) | Right Monitor DP-1 (Secondary @ 144Hz)
hl.monitor({ output = "DP-2", mode = "1920x1080@144", position = "0x0", scale = 1 })
hl.monitor({ output = "DP-1", mode = "1920x1080@144", position = "1920x0", scale = 1 })
hl.monitor({ output = "", mode = "preferred", position = "auto", scale = 1 })

-- 20 Paired Dual-Monitor Workspaces (Odd on DP-2, Even on DP-1)
for i = 1, 20 do
    local target_monitor = (i % 2 == 1) and "DP-2" or "DP-1"
    local is_default = (i == 1 or i == 2)
    hl.workspace_rule({
        workspace = tostring(i),
        monitor = target_monitor,
        default = is_default,
    })
end
