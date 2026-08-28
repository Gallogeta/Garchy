#!/usr/bin/env python3
"""
Gally OS — Modern Desktop Theme Gallery & Switcher
Obsidian Glass aesthetic with 1-click live synchronization across
Hyprland, Waybar, Kitty, Rofi, Quickshell, and Dunst.
"""

import os
import sys
import re
import json
import subprocess
import tkinter as tk
import customtkinter as ctk

# Ensure scripts dir in path
SCRIPTS_DIR = os.path.expanduser("~/.config/hypr/scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

import gally_theme_helper

THEMES = [
    {
        "id": "garchy",
        "name": "Garchy Signature",
        "desc": "Official Garchy aesthetic: Obsidian glass, sapphire blue, electric cyan, and Orokin gold.",
        "colors": ["#0a0f1d", "#38bdf8", "#3b82f6", "#e2e8f0", "#fbbf24"],
        "hypr_border": "rgba(38bdf8ee) rgba(3b82f6ee) rgba(fbbf24ee) 45deg",
        "hypr_inactive": "rgba(0a0f1d88)",
        "hypr_rounding": 14,
        "waybar_radius": "14px",
        "accent": "#38bdf8",
        "accent_alt": "#fbbf24",
        "bg": "#0a0f1d",
        "bg_card": "#131c31",
        "bg_alt": "#131c31",
        "fg": "#f1f5f9",
        "fg_muted": "#94a3b8",
        "icon_theme": "Papirus-Dark"
    },
    {
        "id": "tokyo_night",
        "name": "Tokyo Night",
        "desc": "Elegant dark navy blue with vibrant neon purple, cyan accents, and clean contrast.",
        "colors": ["#131622", "#7aa2f7", "#bb9af7", "#73daca", "#f7768e"],
        "hypr_border": "rgba(7aa2f7ee) rgba(bb9af7ee) 45deg",
        "hypr_inactive": "rgba(24283b88)",
        "hypr_rounding": 12,
        "waybar_radius": "12px",
        "accent": "#7aa2f7",
        "accent_alt": "#bb9af7",
        "bg": "#131622",
        "bg_card": "#1a1d2e",
        "bg_alt": "#1a1d2e",
        "fg": "#c0caf5",
        "fg_muted": "#787c99",
        "icon_theme": "Papirus-Dark"
    },
    {
        "id": "catppuccin",
        "name": "Catppuccin Mocha",
        "desc": "Warm pastel aesthetics with soothing lavender, mauve, and smooth rounded geometry.",
        "colors": ["#1e1e2e", "#cba6f7", "#f5c2e7", "#a6e3a1", "#f38ba8"],
        "hypr_border": "rgba(cba6f7ee) rgba(f5c2e7ee) 45deg",
        "hypr_inactive": "rgba(1e1e2e88)",
        "hypr_rounding": 16,
        "waybar_radius": "16px",
        "accent": "#cba6f7",
        "accent_alt": "#f5c2e7",
        "bg": "#1e1e2e",
        "bg_card": "#181825",
        "bg_alt": "#181825",
        "fg": "#cdd6f4",
        "fg_muted": "#6c7086",
        "icon_theme": "Papirus-Dark"
    },
    {
        "id": "nord",
        "name": "Nord Arctic",
        "desc": "Calm, arctic icy blue tones inspired by Scandinavian winter landscapes.",
        "colors": ["#2e3440", "#88c0d0", "#81a1c1", "#a3be8c", "#bf616a"],
        "hypr_border": "rgba(88c0d0ee) rgba(81a1c1ee) 45deg",
        "hypr_inactive": "rgba(2e344088)",
        "hypr_rounding": 12,
        "waybar_radius": "12px",
        "accent": "#88c0d0",
        "accent_alt": "#81a1c1",
        "bg": "#2e3440",
        "bg_card": "#3b4252",
        "bg_alt": "#3b4252",
        "fg": "#eceff4",
        "fg_muted": "#7b88a1",
        "icon_theme": "Papirus-Dark"
    },
    {
        "id": "cyberpunk",
        "name": "Cyberpunk 2077",
        "desc": "High-contrast electric yellow, neon cyan, zero-rounding sharp competitive edges.",
        "colors": ["#0a0a0f", "#fcee0a", "#00f0ff", "#00ff66", "#ff003c"],
        "hypr_border": "rgba(fcee0aee) rgba(00f0ffee) 45deg",
        "hypr_inactive": "rgba(05050888)",
        "hypr_rounding": 0,
        "waybar_radius": "0px",
        "accent": "#fcee0a",
        "accent_alt": "#00f0ff",
        "bg": "#0a0a0f",
        "bg_card": "#14141e",
        "bg_alt": "#14141e",
        "fg": "#fcee0a",
        "fg_muted": "#71717a",
        "icon_theme": "Papirus-Dark"
    },
    {
        "id": "dracula",
        "name": "Dracula",
        "desc": "Classic dark gothic purple with pink highlights and sharp contrast.",
        "colors": ["#282a36", "#bd93f9", "#ff79c6", "#50fa7b", "#ff5555"],
        "hypr_border": "rgba(bd93f9ee) rgba(ff79c6ee) 45deg",
        "hypr_inactive": "rgba(282a3688)",
        "hypr_rounding": 14,
        "waybar_radius": "14px",
        "accent": "#bd93f9",
        "accent_alt": "#ff79c6",
        "bg": "#282a36",
        "bg_card": "#1e1f29",
        "bg_alt": "#1e1f29",
        "fg": "#f8f8f2",
        "fg_muted": "#6272a4",
        "icon_theme": "Papirus-Dark"
    },
    {
        "id": "volcanic",
        "name": "Volcanic Magma",
        "desc": "Deep magma crimson, fiery amber orange, and warm obsidian charcoal.",
        "colors": ["#1a0f0f", "#ff5533", "#ff9900", "#50fa7b", "#ff3333"],
        "hypr_border": "rgba(ff5533ee) rgba(ff9900ee) 45deg",
        "hypr_inactive": "rgba(1a0f0f88)",
        "hypr_rounding": 12,
        "waybar_radius": "12px",
        "accent": "#ff5533",
        "accent_alt": "#ff9900",
        "bg": "#1a0f0f",
        "bg_card": "#261414",
        "bg_alt": "#261414",
        "fg": "#ffddcc",
        "fg_muted": "#885544",
        "icon_theme": "Papirus-Dark"
    },
    {
        "id": "emerald",
        "name": "Emerald Matrix",
        "desc": "Lush matrix green, deep forest jade, and neon mint highlights.",
        "colors": ["#0f1a14", "#50fa7b", "#8be9fd", "#f1fa8c", "#ff5555"],
        "hypr_border": "rgba(50fa7bee) rgba(8be9fdee) 45deg",
        "hypr_inactive": "rgba(0f1a1488)",
        "hypr_rounding": 12,
        "waybar_radius": "12px",
        "accent": "#50fa7b",
        "accent_alt": "#8be9fd",
        "bg": "#0f1a14",
        "bg_card": "#14261c",
        "bg_alt": "#14261c",
        "fg": "#e0f8e5",
        "fg_muted": "#4e7a5e",
        "icon_theme": "Papirus-Dark"
    },
    {
        "id": "obsidian",
        "name": "Monochrome Glass",
        "desc": "Minimalist luxury pure black, polished titanium silver, and diamond white.",
        "colors": ["#0a0f1d", "#ffffff", "#cbd5e1", "#e2e8f0", "#333340"],
        "hypr_border": "rgba(ffffffee) rgba(ccccccff) 45deg",
        "hypr_inactive": "rgba(1a1a1a88)",
        "hypr_rounding": 10,
        "waybar_radius": "10px",
        "accent": "#ffffff",
        "accent_alt": "#cbd5e1",
        "bg": "#0a0f1d",
        "bg_card": "#131c31",
        "bg_alt": "#131c31",
        "fg": "#ffffff",
        "fg_muted": "#888899",
        "icon_theme": "Papirus-Dark"
    }
]

CUSTOM_THEMES_DIR = os.path.expanduser("~/.config/gally/themes")
os.makedirs(CUSTOM_THEMES_DIR, exist_ok=True)

def load_all_themes():
    all_themes = list(THEMES)
    if os.path.exists(CUSTOM_THEMES_DIR):
        for fname in sorted(os.listdir(CUSTOM_THEMES_DIR)):
            if fname.endswith(".json"):
                try:
                    fpath = os.path.join(CUSTOM_THEMES_DIR, fname)
                    with open(fpath, "r") as f:
                        custom_data = json.load(f)
                    if isinstance(custom_data, dict) and "name" in custom_data:
                        custom_theme = {
                            "id": custom_data.get("id", fname.replace(".json", "")),
                            "name": custom_data.get("name", "Custom Theme"),
                            "desc": custom_data.get("desc", f"User custom theme from {fname}"),
                            "colors": custom_data.get("colors", [custom_data.get("bg", "#0a0f1d"), custom_data.get("accent", "#38bdf8"), custom_data.get("accent_alt", "#3b82f6"), custom_data.get("fg", "#e2e8f0"), "#fbbf24"]),
                            "hypr_border": custom_data.get("hypr_border", f"rgba({custom_data.get('accent', '#38bdf8').lstrip('#')}ee) 45deg"),
                            "hypr_inactive": custom_data.get("hypr_inactive", "rgba(0a0f1d88)"),
                            "hypr_rounding": custom_data.get("rounding", custom_data.get("hypr_rounding", 12)),
                            "rounding": custom_data.get("rounding", custom_data.get("hypr_rounding", 12)),
                            "bar_height": custom_data.get("bar_height", 46),
                            "layout_style": custom_data.get("layout_style", "garchy"),
                            "waybar_radius": f"{custom_data.get('rounding', 12)}px",
                            "accent": custom_data.get("accent", "#38bdf8"),
                            "accent_alt": custom_data.get("accent_alt", "#3b82f6"),
                            "bg": custom_data.get("bg", "#0a0f1d"),
                            "bg_card": custom_data.get("bg_card", "#131c31"),
                            "bg_alt": custom_data.get("bg_alt", "#131c31"),
                            "fg": custom_data.get("fg", "#e2e8f0"),
                            "fg_muted": custom_data.get("fg_muted", "#94a3b8"),
                            "icon_theme": custom_data.get("icon_theme", "Papirus-Dark")
                        }
                        all_themes.append(custom_theme)
                except Exception as err:
                    print(f"Error loading custom theme {fname}: {err}")
    return all_themes

class ModernThemeSwitcherApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        self.title("Gally OS — Visual Theme Gallery")
        self.geometry("900x660")
        self.minsize(800, 540)
        self.configure(fg_color="#0a0f1d")

        self.all_themes = load_all_themes()
        self.active_theme = gally_theme_helper.get_active_theme()
        self.active_name = self.active_theme.get("name", "Garchy Signature")

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.bind("<Escape>", lambda e: self.destroy())

        self.build_ui()

    def build_ui(self):
        # --- Top Header ---
        header = ctk.CTkFrame(self, fg_color="#131c31", corner_radius=14,
                              border_width=1, border_color="#1e293b")
        header.pack(fill="x", padx=16, pady=(14, 8))

        hdr_inner = ctk.CTkFrame(header, fg_color="transparent")
        hdr_inner.pack(fill="x", padx=16, pady=12)

        # Title & Active Badge
        left_box = ctk.CTkFrame(hdr_inner, fg_color="transparent")
        left_box.pack(side="left")

        lbl_title = ctk.CTkLabel(left_box, text="🎨 THEME GALLERY",
                                 font=ctk.CTkFont(family="Sans", size=16, weight="bold"),
                                 text_color="#38bdf8")
        lbl_title.pack(side="left", padx=(0, 10))

        self.lbl_active = ctk.CTkLabel(left_box, text=f"● ACTIVE: {self.active_name}",
                                       font=ctk.CTkFont(family="Sans", size=10, weight="bold"),
                                       text_color="#22c55e",
                                       fg_color="#0a0f1d", corner_radius=8, padx=8, pady=3)
        self.lbl_active.pack(side="left")

        # Right: Search Box
        self.ent_search = ctk.CTkEntry(hdr_inner, placeholder_text="Search themes...",
                                       font=ctk.CTkFont(family="Sans", size=11),
                                       fg_color="#0a0f1d", border_width=1, border_color="#1e293b",
                                       text_color="#e2e8f0", corner_radius=10, width=200, height=28)
        self.ent_search.pack(side="right", padx=(10, 0))
        self.ent_search.bind("<KeyRelease>", self.filter_themes)

        # --- Theme Cards Grid (Scrollable) ---
        self.grid_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.grid_scroll.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        self.render_cards(self.all_themes)

    def filter_themes(self, event=None):
        q = self.ent_search.get().strip().lower()
        if not q:
            self.render_cards(self.all_themes)
        else:
            filtered = [t for t in self.all_themes if q in t["name"].lower() or q in t["desc"].lower()]
            self.render_cards(filtered)

    def render_cards(self, theme_list):
        # Clear existing cards
        for widget in self.grid_scroll.winfo_children():
            widget.destroy()

        for idx, t in enumerate(theme_list):
            row = idx // 2
            col = idx % 2

            is_active = (t["name"].lower() in self.active_name.lower()) or (t["id"] in self.active_name.lower())

            card = ctk.CTkFrame(self.grid_scroll, fg_color="#131c31",
                                corner_radius=14,
                                border_width=2 if is_active else 1,
                                border_color=t["accent"] if is_active else "#1e293b")
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

            card_inner = ctk.CTkFrame(card, fg_color="transparent")
            card_inner.pack(fill="both", expand=True, padx=14, pady=12)

            # Card Header: Name + Badge
            hdr = ctk.CTkFrame(card_inner, fg_color="transparent")
            hdr.pack(fill="x")

            lbl_name = ctk.CTkLabel(hdr, text=t["name"],
                                    font=ctk.CTkFont(family="Sans", size=13, weight="bold"),
                                    text_color=t["accent"])
            lbl_name.pack(side="left")

            if is_active:
                lbl_badge = ctk.CTkLabel(hdr, text="ACTIVE ✓",
                                         font=ctk.CTkFont(size=9, weight="bold"),
                                         text_color="#22c55e", fg_color="#0a0f1d",
                                         corner_radius=6, padx=6, pady=1)
                lbl_badge.pack(side="right")

            # Description
            lbl_desc = ctk.CTkLabel(card_inner, text=t["desc"],
                                    font=ctk.CTkFont(family="Sans", size=10),
                                    text_color="#94a3b8", wraplength=340, justify="left")
            lbl_desc.pack(anchor="w", pady=(4, 8))

            # Color Palette Swatches Row
            swatch_row = ctk.CTkFrame(card_inner, fg_color="transparent")
            swatch_row.pack(anchor="w", pady=(0, 10))

            for color_hex in t["colors"]:
                s = ctk.CTkFrame(swatch_row, fg_color=color_hex, width=28, height=14,
                                 corner_radius=4, border_width=1, border_color="#000000")
                s.pack(side="left", padx=2)

            # Footer: Style Tag + Apply Button
            foot = ctk.CTkFrame(card_inner, fg_color="transparent")
            foot.pack(fill="x", pady=(2, 0))

            style_tag = f"Rounding: {t['hypr_rounding']}px"
            lbl_tag = ctk.CTkLabel(foot, text=style_tag,
                                   font=ctk.CTkFont(size=9),
                                   text_color="#64748b")
            lbl_tag.pack(side="left")

            btn_apply = ctk.CTkButton(foot, text="Apply Theme",
                                      font=ctk.CTkFont(size=10, weight="bold"),
                                      fg_color=t["accent"], text_color="#000000",
                                      hover_color=t["accent_alt"],
                                      corner_radius=8, width=95, height=26,
                                      command=lambda theme=t: self.apply_theme(theme))
            btn_apply.pack(side="right")

        self.grid_scroll.grid_columnconfigure(0, weight=1)
        self.grid_scroll.grid_columnconfigure(1, weight=1)

    def apply_theme(self, t):
        # 1. Update Hyprland Lua configuration and reload
        try:
            look_lua_path = os.path.expanduser("~/.config/hypr/lua/look.lua")
            if os.path.exists(look_lua_path):
                with open(look_lua_path, "r") as f:
                    content = f.read()

                rounding = t.get("hypr_rounding", t.get("rounding", 12))
                accent_clean = t.get("accent", "#38bdf8").lstrip("#")
                accent_alt_clean = t.get("accent_alt", t.get("accent", "#3b82f6")).lstrip("#")
                active_colors = [f'"rgba({accent_clean}ee)"', f'"rgba({accent_alt_clean}ee)"']
                inactive_col = f'"rgba({t.get("bg", "#0a0f1d").lstrip("#")}88)"'

                content = re.sub(r'rounding\s*=\s*\d+', f'rounding = {rounding}', content)
                content = re.sub(r'active_border\s*=\s*\{[\s\S]*?angle\s*=\s*\d+\s*\}(?:,\s*angle\s*=\s*\d+\s*\})?', f'active_border = {{ colors = {{ {", ".join(active_colors)} }}, angle = 45 }}', content)
                content = re.sub(r'inactive_border\s*=\s*"[^"]*"', f'inactive_border = {inactive_col}', content)

                with open(look_lua_path, "w") as f:
                    f.write(content)

                subprocess.run(["hyprctl", "reload"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as err:
            print("Error updating look.lua:", err)

        # 2. Write Rofi active theme
        try:
            rofi_theme = os.path.expanduser("~/.config/rofi/active-theme.rasi")
            os.makedirs(os.path.dirname(rofi_theme), exist_ok=True)
            rofi_content = f"""* {{
    bg: {t['bg']};
    bg-card: {t.get('bg_card', t['bg'])};
    accent: {t['accent']};
    accent-alt: {t.get('accent_alt', t['accent'])};
    fg: {t['fg']};
    fg-muted: {t.get('fg_muted', '#94a3b8')};
}}
"""
            with open(rofi_theme, "w") as f:
                f.write(rofi_content)
        except Exception:
            pass

        # 3. Save to Gally active theme state (triggers Kitty, GTK 3/4, Cava, Quickshell)
        theme_state = {
            "id": t.get("id", "custom"),
            "name": t["name"],
            "bg": t["bg"],
            "bg_card": t.get("bg_card", t["bg"]),
            "bg_input": t.get("bg_card", t["bg"]),
            "bg_alt": t.get("bg_alt", t["bg"]),
            "fg": t["fg"],
            "fg_muted": t.get("fg_muted", "#94a3b8"),
            "accent": t["accent"],
            "accent_alt": t.get("accent_alt", t["accent"]),
            "border_col": t.get("border", t.get("accent", "#38bdf8")),
            "border": t.get("border", t.get("accent", "#38bdf8")),
            "rounding": t.get("hypr_rounding", t.get("rounding", 12)),
            "bar_height": t.get("bar_height", 46),
            "layout_style": t.get("layout_style", "garchy"),
            "border_width": 2,
            "icon_theme": t.get("icon_theme", "Papirus-Dark")
        }
        gally_theme_helper.save_active_theme(theme_state)

        # 4. Sync to garchy_theme.json for immediate Quickshell FileView reactive reload
        try:
            cache_theme = {
                "bg": t["bg"],
                "bg_alt": t.get("bg_alt", t.get("bg_card", "#131c31")),
                "fg": t["fg"],
                "fg_muted": t.get("fg_muted", "#94a3b8"),
                "accent": t["accent"],
                "accent_alt": t.get("accent_alt", t["accent"]),
                "border": t.get("border", t.get("accent", "#38bdf8")),
                "border_col": t.get("border", t.get("accent", "#38bdf8")),
                "gold": t.get("colors", ["#fbbf24"])[-1] if len(t.get("colors", [])) > 4 else "#fbbf24",
                "rounding": t.get("hypr_rounding", t.get("rounding", 12)),
                "bar_height": t.get("bar_height", 46),
                "layout_style": t.get("layout_style", "garchy")
            }
            with open(os.path.expanduser("~/.cache/garchy_theme.json"), "w") as f:
                json.dump(cache_theme, f, indent=2)
        except Exception:
            pass

        # 5. Send Desktop Notification
        try:
            subprocess.Popen(["notify-send", "-a", "Theme Switcher", "✨ Theme Applied", t["name"]])
        except Exception:
            pass

        # 6. Refresh UI without dropping custom themes
        self.active_name = t["name"]
        self.lbl_active.configure(text=f"● ACTIVE: {self.active_name}")
        self.render_cards(self.all_themes)

def main():
    app = ModernThemeSwitcherApp()
    app.mainloop()

if __name__ == "__main__":
    main()
