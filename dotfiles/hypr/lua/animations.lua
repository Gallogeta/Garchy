-- ==============================================================================
-- 🌌 Garchy OS — 144Hz Snappy & Fluid Bezier Animations
-- ==============================================================================

hl.config({
    animations = {
        enabled = true,
    },
})

-- Bezier Curves
hl.curve("wind", { type = "bezier", points = { {0.05, 0.9}, {0.1, 1.05} } })
hl.curve("winIn", { type = "bezier", points = { {0.1, 1.1}, {0.1, 1.05} } })
hl.curve("winOut", { type = "bezier", points = { {0.3, -0.3}, {0.0, 1.0} } })
hl.curve("liner", { type = "bezier", points = { {1.0, 1.0}, {1.0, 1.0} } })
hl.curve("smoothOut", { type = "bezier", points = { {0.25, 1.0}, {0.5, 1.0} } })

-- Animation Trees (Tuned for instantaneous 144Hz response)
hl.animation({ leaf = "windows", enabled = true, speed = 2.5, bezier = "wind", style = "popin 80%" })
hl.animation({ leaf = "windowsIn", enabled = true, speed = 2.5, bezier = "winIn", style = "popin 80%" })
hl.animation({ leaf = "windowsOut", enabled = true, speed = 2.2, bezier = "winOut", style = "popin 85%" })
hl.animation({ leaf = "windowsMove", enabled = true, speed = 2.2, bezier = "wind", style = "slide" })
hl.animation({ leaf = "border", enabled = false })
hl.animation({ leaf = "borderangle", enabled = false })
hl.animation({ leaf = "fade", enabled = true, speed = 2.0, bezier = "smoothOut" })
hl.animation({ leaf = "workspaces", enabled = true, speed = 2.4, bezier = "smoothOut", style = "slidefade 20%" })
hl.animation({ leaf = "specialWorkspace", enabled = true, speed = 2.4, bezier = "wind", style = "slidefadevert 20%" })
hl.animation({ leaf = "layers", enabled = true, speed = 2.5, bezier = "winIn", style = "popin 85%" })
hl.animation({ leaf = "layersIn", enabled = true, speed = 2.5, bezier = "winIn", style = "popin 85%" })
hl.animation({ leaf = "layersOut", enabled = true, speed = 2.0, bezier = "winOut", style = "popin 85%" })
