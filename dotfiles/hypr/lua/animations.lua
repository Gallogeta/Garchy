-- ==============================================================================
-- 🌌 Garchy OS — Caelestia Fluid Spring & 144Hz Snappy Bezier Animations
-- ==============================================================================

hl.config({
    animations = {
        enabled = true,
    },
})

-- Caelestia Fluid Bezier Curves
hl.curve("caelestia_fluid", { type = "bezier", points = { {0.05, 0.9}, {0.1, 1.05} } })
hl.curve("caelestia_popin", { type = "bezier", points = { {0.16, 1.0}, {0.3, 1.05} } })
hl.curve("caelestia_out", { type = "bezier", points = { {0.3, -0.2}, {0.1, 1.0} } })
hl.curve("smoothOut", { type = "bezier", points = { {0.25, 1.0}, {0.5, 1.0} } })
hl.curve("liner", { type = "bezier", points = { {1.0, 1.0}, {1.0, 1.0} } })

-- Animation Trees (Caelestia Spring Popin / Slide / Fade for Open, Restore, Minimize, Close)
hl.animation({ leaf = "windows", enabled = true, speed = 2.8, bezier = "caelestia_popin", style = "popin 85%" })
hl.animation({ leaf = "windowsIn", enabled = true, speed = 3.0, bezier = "caelestia_popin", style = "popin 85%" })
hl.animation({ leaf = "windowsOut", enabled = true, speed = 2.4, bezier = "caelestia_out", style = "popin 88%" })
hl.animation({ leaf = "windowsMove", enabled = true, speed = 2.8, bezier = "caelestia_fluid", style = "slide" })
hl.animation({ leaf = "border", enabled = false })
hl.animation({ leaf = "borderangle", enabled = false })
hl.animation({ leaf = "fade", enabled = true, speed = 2.0, bezier = "smoothOut" })
hl.animation({ leaf = "workspaces", enabled = true, speed = 2.6, bezier = "caelestia_fluid", style = "slidefade 25%" })
hl.animation({ leaf = "specialWorkspace", enabled = true, speed = 2.6, bezier = "caelestia_popin", style = "slidefadevert 20%" })
hl.animation({ leaf = "layers", enabled = true, speed = 2.8, bezier = "caelestia_popin", style = "popin 88%" })
hl.animation({ leaf = "layersIn", enabled = true, speed = 2.8, bezier = "caelestia_popin", style = "popin 88%" })
hl.animation({ leaf = "layersOut", enabled = true, speed = 2.0, bezier = "caelestia_out", style = "popin 88%" })
