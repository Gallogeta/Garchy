#!/usr/bin/env bash

CYAN='\033[96m'
GREEN='\033[92m'
YELLOW='\033[93m'
MAGENTA='\033[95m'
BLUE='\033[94m'
BOLD='\033[1m'
RESET='\033[0m'

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
THEMES_DIR="$REPO_DIR/archiso/airootfs/usr/share/sddm/themes"

echo -e "${CYAN}${BOLD}"
echo "  ╔═══════════════════════════════════════════════════════╗"
echo "  ║        🌌 GARCHY OS SDDM THEME PREVIEW HUB          ║"
echo "  ╚═══════════════════════════════════════════════════════╝"
echo -e "${RESET}"

echo -e "Select a theme to preview in a live window:"
echo -e "  ${MAGENTA}[1]${RESET} ⚡ ${BOLD}Garchy Warframe${RESET} (3D Cephalon Hologram Core & Orokin HUD)"
echo -e "  ${CYAN}[2]${RESET} 🌌 ${BOLD}Garchy Signature${RESET} (Glassmorphic Hyprlock Design)"
echo -e "  ${GREEN}[3]${RESET} 🌟 ${BOLD}Garchy Junior${RESET} (Kids & Young Explorers Edition)"
echo -e "  ${MAGENTA}[4]${RESET} ⚡ ${BOLD}Garchy Cyber Neon${RESET} (Teens & Esports Gamers Edition)"
echo -e "  ${BLUE}[5]${RESET} 💻 ${BOLD}Garchy Dev Matrix${RESET} (Programmers & Terminal Hacker Edition)"
echo -e "  ${YELLOW}[6]${RESET} ✨ ${BOLD}Garchy Elegance${RESET} (Minimalist Obsidian Glass / Adults)"
echo -e "  ${RESET}[q] Quit\n"

read -p "Enter choice [1-6]: " choice

case "$choice" in
    1) THEME="garchy-warframe" ;;
    2) THEME="garchy" ;;
    3) THEME="garchy-kids" ;;
    4) THEME="garchy-cyber" ;;
    5) THEME="garchy-matrix" ;;
    6) THEME="garchy-elegance" ;;
    q|Q) exit 0 ;;
    *) echo -e "${YELLOW}Invalid option.${RESET}"; exit 1 ;;
esac

echo -e "\n${CYAN}Launching preview for: ${BOLD}$THEME${RESET}..."
echo -e "${YELLOW}(Close the preview window when done to return)${RESET}\n"

sddm-greeter-qt6 --test-mode --theme "$THEMES_DIR/$THEME"
