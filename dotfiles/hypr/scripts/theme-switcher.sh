#!/usr/bin/env bash

# Master Global Theme Switcher for Hyprland, Waybar, Kitty, Quickshell, and Rofi

THEMES=(
    "🌸 Tokyo Night"
    "☕ Catppuccin Mocha"
    "❄️ Nord Arctic"
    "⚡ Cyberpunk 2077"
    "🧛 Dracula"
    "🌋 Volcanic Lava"
    "🌲 Emerald Forest"
    "🖤 Monochrome Diamond"
)

SELECTED=$(printf "%s\n" "${THEMES[@]}" | rofi -dmenu -i -p "󰏘 Desktop Theme" -config ~/.config/rofi/theme-picker.rasi)

if [ -z "$SELECTED" ]; then
    exit 0
fi

WAYBAR_THEME="$HOME/.config/waybar/theme.css"
KITTY_THEME="$HOME/.config/kitty/theme.conf"
QS_THEME="$HOME/.config/quickshell/desktop-hub/active_theme.json"
ROFI_THEME="$HOME/.config/rofi/active-theme.rasi"

case "$SELECTED" in
    *"Tokyo Night"*)
        HYPR_BORDER="rgba(7aa2f7ee) rgba(bb9af7ee) 45deg"
        HYPR_INACTIVE="rgba(24283b88)"
        HYPR_ROUNDING="0"
        WAYBAR_RADIUS="0px"
        QS_RADIUS=0
        
        ROFI_BG="rgba(19, 22, 34, 0.94)"
        ROFI_BG_ALT="rgba(26, 29, 46, 0.85)"
        ROFI_HOVER="rgba(122, 162, 247, 0.15)"
        ROFI_SELECTED="rgba(122, 162, 247, 0.32)"
        ROFI_BORDER="rgba(36, 40, 59, 0.9)"
        ROFI_ACCENT="#7aa2f7"
        ROFI_ACCENT_ALT="#bb9af7"
        ROFI_FG="#c0caf5"
        ROFI_FG_MUTED="#787c99"
        ROFI_RADIUS="0px"

        cat << EOF > "$WAYBAR_THEME"
@define-color bg #131622;
@define-color bg-alt #1a1d2e;
@define-color border-col #24283b;
@define-color accent #7aa2f7;
@define-color accent-alt #bb9af7;
@define-color fg #c0caf5;
@define-color fg-muted #787c99;
@define-color fg-active #131622;
@define-color green #73daca;
@define-color red #f7768e;
@define-color yellow #e0af68;

.modules-left,
.modules-center,
.modules-right,
#workspaces button,
#custom-btn-minimize,
#custom-btn-maximize,
#custom-btn-close,
#custom-minimized,
tooltip {
    border-radius: ${WAYBAR_RADIUS};
}
EOF

        cat << 'EOF' > "$KITTY_THEME"
foreground   #c0caf5
background   #131622
selection_foreground #131622
selection_background #7aa2f7
url_color #7dcfff
cursor #7aa2f7
cursor_text_color #131622

active_tab_background   #1f2335
active_tab_foreground   #c0caf5
inactive_tab_background #131622
inactive_tab_foreground #565f89

color0  #15161e
color1  #f7768e
color2  #9ece6a
color3  #e0af68
color4  #7aa2f7
color5  #bb9af7
color6  #7dcfff
color7  #a9b1d6
color8  #414868
color9  #f7768e
color10 #9ece6a
color11 #e0af68
color12 #7aa2f7
color13 #bb9af7
color14 #7dcfff
color15 #c0caf5
EOF

        cat << EOF > "$QS_THEME"
{
    "themeIndex": 3,
    "themeName": "Tokyo Night",
    "bg": "#131622CC",
    "bgAlt": "#1A1D2E",
    "border": "#24283B",
    "accent": "#7AA2F7",
    "accentAlt": "#BB9AF7",
    "fg": "#C0CAF5",
    "radius": ${QS_RADIUS}
}
EOF
        ;;

    *"Catppuccin Mocha"*)
        HYPR_BORDER="rgba(cba6f7ee) rgba(f5c2e7ee) 45deg"
        HYPR_INACTIVE="rgba(1e1e2e88)"
        HYPR_ROUNDING="12"
        WAYBAR_RADIUS="12px"
        QS_RADIUS=12

        ROFI_BG="rgba(30, 30, 46, 0.94)"
        ROFI_BG_ALT="rgba(24, 24, 37, 0.85)"
        ROFI_HOVER="rgba(203, 166, 247, 0.15)"
        ROFI_SELECTED="rgba(203, 166, 247, 0.32)"
        ROFI_BORDER="rgba(49, 50, 68, 0.9)"
        ROFI_ACCENT="#cba6f7"
        ROFI_ACCENT_ALT="#f5c2e7"
        ROFI_FG="#cdd6f4"
        ROFI_FG_MUTED="#6c7086"
        ROFI_RADIUS="12px"

        cat << EOF > "$WAYBAR_THEME"
@define-color bg #1e1e2e;
@define-color bg-alt #181825;
@define-color border-col #313244;
@define-color accent #cba6f7;
@define-color accent-alt #f5c2e7;
@define-color fg #cdd6f4;
@define-color fg-muted #6c7086;
@define-color fg-active #11111b;
@define-color green #a6e3a1;
@define-color red #f38ba8;
@define-color yellow #f9e2af;

.modules-left,
.modules-center,
.modules-right,
#workspaces button,
#custom-btn-minimize,
#custom-btn-maximize,
#custom-btn-close,
#custom-minimized,
tooltip {
    border-radius: ${WAYBAR_RADIUS};
}
EOF

        cat << 'EOF' > "$KITTY_THEME"
foreground   #cdd6f4
background   #1e1e2e
selection_foreground #1e1e2e
selection_background #cba6f7
url_color #f5e0dc
cursor #cba6f7
cursor_text_color #11111b

active_tab_background   #313244
active_tab_foreground   #cdd6f4
inactive_tab_background #181825
inactive_tab_foreground #6c7086

color0  #45475a
color1  #f38ba8
color2  #a6e3a1
color3  #f9e2af
color4  #89b4fa
color5  #cba6f7
color6  #94e2d5
color7  #bac2de
color8  #585b70
color9  #f38ba8
color10 #a6e3a1
color11 #f9e2af
color12 #89b4fa
color13 #cba6f7
color14 #94e2d5
color15 #a6adc8
EOF

        cat << EOF > "$QS_THEME"
{
    "themeIndex": 0,
    "themeName": "Catppuccin Mocha",
    "bg": "#1E1E2ECC",
    "bgAlt": "#181825",
    "border": "#313244",
    "accent": "#CBA6F7",
    "accentAlt": "#F5C2E7",
    "fg": "#CDD6F4",
    "radius": ${QS_RADIUS}
}
EOF
        ;;

    *"Nord Arctic"*)
        HYPR_BORDER="rgba(88c0d0ee) rgba(81a1c1ee) 45deg"
        HYPR_INACTIVE="rgba(2e344088)"
        HYPR_ROUNDING="8"
        WAYBAR_RADIUS="8px"
        QS_RADIUS=8

        ROFI_BG="rgba(46, 52, 64, 0.94)"
        ROFI_BG_ALT="rgba(59, 66, 82, 0.85)"
        ROFI_HOVER="rgba(136, 192, 208, 0.15)"
        ROFI_SELECTED="rgba(136, 192, 208, 0.32)"
        ROFI_BORDER="rgba(76, 86, 106, 0.9)"
        ROFI_ACCENT="#88c0d0"
        ROFI_ACCENT_ALT="#81a1c1"
        ROFI_FG="#eceff4"
        ROFI_FG_MUTED="#7b88a1"
        ROFI_RADIUS="8px"

        cat << EOF > "$WAYBAR_THEME"
@define-color bg #2e3440;
@define-color bg-alt #3b4252;
@define-color border-col #4c566a;
@define-color accent #88c0d0;
@define-color accent-alt #81a1c1;
@define-color fg #eceff4;
@define-color fg-muted #7b88a1;
@define-color fg-active #2e3440;
@define-color green #a3be8c;
@define-color red #bf616a;
@define-color yellow #ebcb8b;

.modules-left,
.modules-center,
.modules-right,
#workspaces button,
#custom-btn-minimize,
#custom-btn-maximize,
#custom-btn-close,
#custom-minimized,
tooltip {
    border-radius: ${WAYBAR_RADIUS};
}
EOF

        cat << 'EOF' > "$KITTY_THEME"
foreground   #eceff4
background   #2e3440
selection_foreground #2e3440
selection_background #88c0d0
url_color #81a1c1
cursor #88c0d0
cursor_text_color #2e3440

active_tab_background   #3b4252
active_tab_foreground   #eceff4
inactive_tab_background #2e3440
inactive_tab_foreground #4c566a

color0  #3b4252
color1  #bf616a
color2  #a3be8c
color3  #ebcb8b
color4  #81a1c1
color5  #b48ead
color6  #88c0d0
color7  #e5e9f0
color8  #4c566a
color9  #bf616a
color10 #a3be8c
color11 #ebcb8b
color12 #81a1c1
color13 #b48ead
color14 #8fbcbb
color15 #eceff4
EOF

        cat << EOF > "$QS_THEME"
{
    "themeIndex": 4,
    "themeName": "Nord Arctic",
    "bg": "#2E3440CC",
    "bgAlt": "#3B4252",
    "border": "#4C566A",
    "accent": "#88C0D0",
    "accentAlt": "#81A1C1",
    "fg": "#ECEFF4",
    "radius": ${QS_RADIUS}
}
EOF
        ;;

    *"Cyberpunk 2077"*)
        HYPR_BORDER="rgba(fcee0aee) rgba(00f0ffee) 45deg"
        HYPR_INACTIVE="rgba(05050888)"
        HYPR_ROUNDING="0"
        WAYBAR_RADIUS="0px"
        QS_RADIUS=0

        ROFI_BG="rgba(10, 10, 15, 0.96)"
        ROFI_BG_ALT="rgba(25, 25, 35, 0.85)"
        ROFI_HOVER="rgba(252, 238, 10, 0.15)"
        ROFI_SELECTED="rgba(252, 238, 10, 0.32)"
        ROFI_BORDER="rgba(40, 40, 50, 0.9)"
        ROFI_ACCENT="#fcee0a"
        ROFI_ACCENT_ALT="#00f0ff"
        ROFI_FG="#fcee0a"
        ROFI_FG_MUTED="#71717a"
        ROFI_RADIUS="0px"

        cat << EOF > "$WAYBAR_THEME"
@define-color bg #0a0a0f;
@define-color bg-alt #14141e;
@define-color border-col #282832;
@define-color accent #fcee0a;
@define-color accent-alt #00f0ff;
@define-color fg #fcee0a;
@define-color fg-muted #71717a;
@define-color fg-active #000000;
@define-color green #00ff66;
@define-color red #ff003c;
@define-color yellow #fcee0a;

.modules-left,
.modules-center,
.modules-right,
#workspaces button,
#custom-btn-minimize,
#custom-btn-maximize,
#custom-btn-close,
#custom-minimized,
tooltip {
    border-radius: ${WAYBAR_RADIUS};
}
EOF

        cat << 'EOF' > "$KITTY_THEME"
foreground   #fcee0a
background   #0a0a0f
selection_foreground #000000
selection_background #fcee0a
url_color #00f0ff
cursor #fcee0a
cursor_text_color #000000

active_tab_background   #14141e
active_tab_foreground   #fcee0a
inactive_tab_background #0a0a0f
inactive_tab_foreground #71717a

color0  #14141e
color1  #ff003c
color2  #00ff66
color3  #fcee0a
color4  #00f0ff
color5  #ff007f
color6  #00e5ff
color7  #fcee0a
color8  #282832
color9  #ff003c
color10 #00ff66
color11 #fcee0a
color12 #00f0ff
color13 #ff007f
color14 #00e5ff
color15 #ffffff
EOF

        cat << EOF > "$QS_THEME"
{
    "themeIndex": 1,
    "themeName": "Cyberpunk Neon",
    "bg": "#0A0A0FCC",
    "bgAlt": "#14141E",
    "border": "#282832",
    "accent": "#FCEE0A",
    "accentAlt": "#00F0FF",
    "fg": "#FCEE0A",
    "radius": ${QS_RADIUS}
}
EOF
        ;;

    *"Dracula"*)
        HYPR_BORDER="rgba(bd93f9ee) rgba(ff79c6ee) 45deg"
        HYPR_INACTIVE="rgba(282a3688)"
        HYPR_ROUNDING="10"
        WAYBAR_RADIUS="10px"
        QS_RADIUS=10

        ROFI_BG="rgba(40, 42, 54, 0.94)"
        ROFI_BG_ALT="rgba(30, 31, 41, 0.85)"
        ROFI_HOVER="rgba(189, 147, 249, 0.15)"
        ROFI_SELECTED="rgba(189, 147, 249, 0.32)"
        ROFI_BORDER="rgba(68, 71, 90, 0.9)"
        ROFI_ACCENT="#bd93f9"
        ROFI_ACCENT_ALT="#ff79c6"
        ROFI_FG="#f8f8f2"
        ROFI_FG_MUTED="#6272a4"
        ROFI_RADIUS="10px"

        cat << EOF > "$WAYBAR_THEME"
@define-color bg #282a36;
@define-color bg-alt #1e1f29;
@define-color border-col #44475a;
@define-color accent #bd93f9;
@define-color accent-alt #ff79c6;
@define-color fg #f8f8f2;
@define-color fg-muted #6272a4;
@define-color fg-active #282a36;
@define-color green #50fa7b;
@define-color red #ff5555;
@define-color yellow #f1fa8c;

.modules-left,
.modules-center,
.modules-right,
#workspaces button,
#custom-btn-minimize,
#custom-btn-maximize,
#custom-btn-close,
#custom-minimized,
tooltip {
    border-radius: ${WAYBAR_RADIUS};
}
EOF

        cat << 'EOF' > "$KITTY_THEME"
foreground   #f8f8f2
background   #282a36
selection_foreground #282a36
selection_background #bd93f9
url_color #8be9fd
cursor #bd93f9
cursor_text_color #282a36

active_tab_background   #44475a
active_tab_foreground   #f8f8f2
inactive_tab_background #282a36
inactive_tab_foreground #6272a4

color0  #21222c
color1  #ff5555
color2  #50fa7b
color3  #f1fa8c
color4  #bd93f9
color5  #ff79c6
color6  #8be9fd
color7  #f8f8f2
color8  #6272a4
color9  #ff6e6e
color10 #69ff94
color11 #ffffa5
color12 #d6acff
color13 #ff92df
color14 #a4ffff
color15 #ffffff
EOF

        cat << EOF > "$QS_THEME"
{
    "themeIndex": 6,
    "themeName": "Dracula",
    "bg": "#282A36CC",
    "bgAlt": "#1E1F29",
    "border": "#44475A",
    "accent": "#BD93F9",
    "accentAlt": "#FF79C6",
    "fg": "#F8F8F2",
    "radius": ${QS_RADIUS}
}
EOF
        ;;

    *"Volcanic Lava"*)
        HYPR_BORDER="rgba(ff5533ee) rgba(ff9900ee) 45deg"
        HYPR_INACTIVE="rgba(1a0f0f88)"
        HYPR_ROUNDING="10"
        WAYBAR_RADIUS="10px"
        QS_RADIUS=10

        ROFI_BG="rgba(26, 15, 15, 0.94)"
        ROFI_BG_ALT="rgba(38, 20, 20, 0.85)"
        ROFI_HOVER="rgba(255, 85, 51, 0.15)"
        ROFI_SELECTED="rgba(255, 85, 51, 0.32)"
        ROFI_BORDER="rgba(70, 30, 30, 0.9)"
        ROFI_ACCENT="#ff5533"
        ROFI_ACCENT_ALT="#ff9900"
        ROFI_FG="#ffddcc"
        ROFI_FG_MUTED="#885544"
        ROFI_RADIUS="10px"

        cat << EOF > "$WAYBAR_THEME"
@define-color bg #1a0f0f;
@define-color bg-alt #261414;
@define-color border-col #461e1e;
@define-color accent #ff5533;
@define-color accent-alt #ff9900;
@define-color fg #ffddcc;
@define-color fg-muted #885544;
@define-color fg-active #1a0f0f;
@define-color green #73daca;
@define-color red #ff3333;
@define-color yellow #ffaa00;

.modules-left,
.modules-center,
.modules-right,
#workspaces button,
#custom-btn-minimize,
#custom-btn-maximize,
#custom-btn-close,
#custom-minimized,
tooltip {
    border-radius: ${WAYBAR_RADIUS};
}
EOF

        cat << 'EOF' > "$KITTY_THEME"
foreground   #ffddcc
background   #1a0f0f
selection_foreground #1a0f0f
selection_background #ff5533
url_color #ff9900
cursor #ff5533
cursor_text_color #1a0f0f

active_tab_background   #261414
active_tab_foreground   #ffddcc
inactive_tab_background #1a0f0f
inactive_tab_foreground #885544

color0  #140b0b
color1  #ff3333
color2  #50fa7b
color3  #ffaa00
color4  #ff5533
color5  #ff7755
color6  #ff9900
color7  #ffddcc
color8  #461e1e
color9  #ff4444
color10 #69ff94
color11 #ffbb33
color12 #ff6644
color13 #ff8866
color14 #ffaa33
color15 #ffffff
EOF

        cat << EOF > "$QS_THEME"
{
    "themeIndex": 8,
    "themeName": "Crimson Fire",
    "bg": "#1A0F0FCC",
    "bgAlt": "#261414",
    "border": "#461E1E",
    "accent": "#FF5533",
    "accentAlt": "#FF9900",
    "fg": "#FFDDCC",
    "radius": ${QS_RADIUS}
}
EOF
        ;;

    *"Emerald Forest"*)
        HYPR_BORDER="rgba(50fa7bee) rgba(8be9fdee) 45deg"
        HYPR_INACTIVE="rgba(0f1a1488)"
        HYPR_ROUNDING="10"
        WAYBAR_RADIUS="10px"
        QS_RADIUS=10

        ROFI_BG="rgba(15, 26, 20, 0.94)"
        ROFI_BG_ALT="rgba(20, 38, 28, 0.85)"
        ROFI_HOVER="rgba(80, 250, 123, 0.15)"
        ROFI_SELECTED="rgba(80, 250, 123, 0.32)"
        ROFI_BORDER="rgba(30, 60, 45, 0.9)"
        ROFI_ACCENT="#50fa7b"
        ROFI_ACCENT_ALT="#8be9fd"
        ROFI_FG="#e0f8e5"
        ROFI_FG_MUTED="#4e7a5e"
        ROFI_RADIUS="10px"

        cat << EOF > "$WAYBAR_THEME"
@define-color bg #0f1a14;
@define-color bg-alt #14261c;
@define-color border-col #1e3c2d;
@define-color accent #50fa7b;
@define-color accent-alt #8be9fd;
@define-color fg #e0f8e5;
@define-color fg-muted #4e7a5e;
@define-color fg-active #0f1a14;
@define-color green #50fa7b;
@define-color red #ff5555;
@define-color yellow #f1fa8c;

.modules-left,
.modules-center,
.modules-right,
#workspaces button,
#custom-btn-minimize,
#custom-btn-maximize,
#custom-btn-close,
#custom-minimized,
tooltip {
    border-radius: ${WAYBAR_RADIUS};
}
EOF

        cat << 'EOF' > "$KITTY_THEME"
foreground   #e0f8e5
background   #0f1a14
selection_foreground #0f1a14
selection_background #50fa7b
url_color #8be9fd
cursor #50fa7b
cursor_text_color #0f1a14

active_tab_background   #14261c
active_tab_foreground   #e0f8e5
inactive_tab_background #0f1a14
inactive_tab_foreground #4e7a5e

color0  #0a120e
color1  #ff5555
color2  #50fa7b
color3  #f1fa8c
color4  #50fa7b
color5  #ff79c6
color6  #8be9fd
color7  #e0f8e5
color8  #1e3c2d
color9  #ff6e6e
color10 #69ff94
color11 #ffffa5
color12 #50fa7b
color13 #ff92df
color14 #a4ffff
color15 #ffffff
EOF

        cat << EOF > "$QS_THEME"
{
    "themeIndex": 12,
    "themeName": "Emerald Matrix",
    "bg": "#0F1A14CC",
    "bgAlt": "#14261C",
    "border": "#1E3C2D",
    "accent": "#50FA7B",
    "accentAlt": "#8BE9FD",
    "fg": "#E0F8E5",
    "radius": ${QS_RADIUS}
}
EOF
        ;;

    *"Monochrome Diamond"*)
        HYPR_BORDER="rgba(ffffffee) rgba(ccccccff) 45deg"
        HYPR_INACTIVE="rgba(1a1a1a88)"
        HYPR_ROUNDING="0"
        WAYBAR_RADIUS="0px"
        QS_RADIUS=0

        ROFI_BG="rgba(18, 18, 18, 0.96)"
        ROFI_BG_ALT="rgba(28, 28, 28, 0.85)"
        ROFI_HOVER="rgba(255, 255, 255, 0.15)"
        ROFI_SELECTED="rgba(255, 255, 255, 0.30)"
        ROFI_BORDER="rgba(50, 50, 50, 0.9)"
        ROFI_ACCENT="#ffffff"
        ROFI_ACCENT_ALT="#cccccc"
        ROFI_FG="#ffffff"
        ROFI_FG_MUTED="#777777"
        ROFI_RADIUS="0px"

        cat << EOF > "$WAYBAR_THEME"
@define-color bg #111116;
@define-color bg-alt #1a1a22;
@define-color border-col #333340;
@define-color accent #ffffff;
@define-color accent-alt #cbd5e1;
@define-color fg #ffffff;
@define-color fg-muted #888899;
@define-color fg-active #111116;
@define-color green #ffffff;
@define-color red #f7768e;
@define-color yellow #e0af68;

.modules-left,
.modules-center,
.modules-right,
#workspaces button,
#custom-btn-minimize,
#custom-btn-maximize,
#custom-btn-close,
#custom-minimized,
tooltip {
    border-radius: ${WAYBAR_RADIUS};
}
EOF

        cat << 'EOF' > "$KITTY_THEME"
foreground   #ffffff
background   #111116
selection_foreground #111116
selection_background #ffffff
url_color #cbd5e1
cursor #ffffff
cursor_text_color #111116

active_tab_background   #1a1a22
active_tab_foreground   #ffffff
inactive_tab_background #111116
inactive_tab_foreground #555566

color0  #1a1a22
color1  #f7768e
color2  #e2e8f0
color3  #cbd5e1
color4  #ffffff
color5  #e2e8f0
color6  #ffffff
color7  #ffffff
color8  #333340
color9  #f7768e
color10 #e2e8f0
color11 #cbd5e1
color12 #ffffff
color13 #e2e8f0
color14 #ffffff
color15 #ffffff
EOF

        cat << EOF > "$QS_THEME"
{
    "themeIndex": 18,
    "themeName": "Monochrome Glass",
    "bg": "#111116CC",
    "bgAlt": "#1A1A22",
    "border": "#333340",
    "accent": "#FFFFFF",
    "accentAlt": "#CBD5E1",
    "fg": "#FFFFFF",
    "radius": ${QS_RADIUS}
}
EOF
        ;;
esac

# Update Rofi active theme variables
cat << EOF > "$ROFI_THEME"
* {
    bg: ${ROFI_BG};
    bg-alt: ${ROFI_BG_ALT};
    bg-hover: ${ROFI_HOVER};
    bg-selected: ${ROFI_SELECTED};
    border-col: ${ROFI_BORDER};
    border-accent: ${ROFI_ACCENT};
    accent: ${ROFI_ACCENT};
    accent-alt: ${ROFI_ACCENT_ALT};
    fg: ${ROFI_FG};
    fg-muted: ${ROFI_FG_MUTED};
    fg-selected: #ffffff;
    urgent: #f7768e;
    radius: ${ROFI_RADIUS};
}
EOF

# 1. Update Hyprland window borders & corner rounding live
hyprctl keyword general:col.active_border "$HYPR_BORDER" >/dev/null 2>&1
hyprctl keyword general:col.inactive_border "$HYPR_INACTIVE" >/dev/null 2>&1
hyprctl keyword decoration:rounding "$HYPR_ROUNDING" >/dev/null 2>&1

# 2. Reload Waybar styles live
killall -SIGUSR2 waybar 2>/dev/null || (killall waybar; hyprctl dispatch exec waybar)

# 3. Reload Kitty terminal color schemes across all open windows live
killall -SIGUSR1 kitty 2>/dev/null

notify-send -a "Theme Switcher" "Theme Applied" "$SELECTED"
