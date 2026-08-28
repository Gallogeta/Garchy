#!/usr/bin/env bash
set -e

CYAN='\033[96m'
GREEN='\033[92m'
YELLOW='\033[93m'
MAGENTA='\033[95m'
BOLD='\033[1m'
RESET='\033[0m'

CHOSEN_THEME="${1:-garchy-warframe}"

if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}Please run with sudo: ${CYAN}sudo $0 [theme-name]${RESET}"
    echo -e "Available themes: ${BOLD}garchy-warframe, garchy, garchy-kids, garchy-cyber, garchy-matrix, garchy-elegance${RESET}"
    exit 1
fi

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
THEMES_SRC="$REPO_DIR/archiso/airootfs/usr/share/sddm/themes"
THEMES_DEST="/usr/share/sddm/themes"

echo -e "${CYAN}${BOLD}🌌 Deploying Garchy SDDM Greeter Themes Suite...${RESET}"

mkdir -p "$THEMES_DEST"

# Deploy all themes
for theme in garchy-warframe garchy garchy-kids garchy-cyber garchy-matrix garchy-elegance; do
    if [ -d "$THEMES_SRC/$theme" ]; then
        rm -rf "$THEMES_DEST/$theme"
        cp -r "$THEMES_SRC/$theme" "$THEMES_DEST/"
        echo -e "  ${GREEN}✔${RESET} Deployed: ${CYAN}$theme${RESET}"
    fi
done

# Validate chosen theme
if [ ! -d "$THEMES_DEST/$CHOSEN_THEME" ]; then
    echo -e "${YELLOW}Warning: '$CHOSEN_THEME' not found. Defaulting to 'garchy-warframe'.${RESET}"
    CHOSEN_THEME="garchy-warframe"
fi

# Configure SDDM
mkdir -p /etc/sddm.conf.d
if [ -f /etc/sddm.conf.d/kde_settings.conf ]; then
    sed -i "s/^Current=.*/Current=$CHOSEN_THEME/" /etc/sddm.conf.d/kde_settings.conf
else
    cat << CONF > /etc/sddm.conf.d/garchy.conf
[Theme]
Current=$CHOSEN_THEME
CursorTheme=Adwaita
Font=JetBrainsMono Nerd Font

[General]
Numlock=on
InputMethod=
CONF
fi

echo -e "\n${GREEN}${BOLD}════════════════════════════════════════════════════════════${RESET}"
echo -e "  ${GREEN}✔${RESET} Active SDDM Theme set to: ${MAGENTA}${BOLD}$CHOSEN_THEME${RESET}"
echo -e "${GREEN}${BOLD}════════════════════════════════════════════════════════════${RESET}"
echo -e "\n${BOLD}Preview any theme with:${RESET}"
echo -e "  ${CYAN}sddm-greeter-qt6 --test-mode --theme /usr/share/sddm/themes/garchy-warframe${RESET}"
echo -e "  ${CYAN}sddm-greeter-qt6 --test-mode --theme /usr/share/sddm/themes/garchy${RESET}"
echo -e "  ${CYAN}sddm-greeter-qt6 --test-mode --theme /usr/share/sddm/themes/garchy-kids${RESET}"
echo -e "  ${CYAN}sddm-greeter-qt6 --test-mode --theme /usr/share/sddm/themes/garchy-cyber${RESET}"
echo -e "  ${CYAN}sddm-greeter-qt6 --test-mode --theme /usr/share/sddm/themes/garchy-matrix${RESET}"
echo -e "  ${CYAN}sddm-greeter-qt6 --test-mode --theme /usr/share/sddm/themes/garchy-elegance${RESET}\n"
