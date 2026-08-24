#!/usr/bin/env bash
set -e

# ==============================================================================
#   GARCHY LINUX - Modern Arch + Hyprland + AI System Bootstrap Installer
#   Repository: https://github.com/Gallogeta/Garchy
# ==============================================================================

CYAN='\033[96m'
BLUE='\033[94m'
GREEN='\033[92m'
YELLOW='\033[93m'
RED='\033[91m'
BOLD='\033[1m'
RESET='\033[0m'

print_banner() {
    echo -e "${CYAN}${BOLD}"
    cat << "BANNER"
   ██████╗  █████╗ ██████╗  ██████╗██╗  ██╗██╗   ██╗
  ██╔════╝ ██╔══██╗██╔══██╗██╔════╝██║  ██║╚██╗ ██╔╝
  ██║  ███╗███████║██████╔╝██║     ███████║ ╚████╔╝ 
  ██║   ██║██╔══██║██╔══██╗██║     ██╔══██║  ╚██╔╝  
  ╚██████╔╝██║  ██║██║  ██║╚██████╗██║  ██║   ██║   
   ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝   ╚═╝   
BANNER
    echo -e "       ${BLUE}Modern Arch + Hyprland + AI Gaming/Dev OS${RESET}\n"
}

print_banner

# Check Arch Linux
if [ ! -f /etc/arch-release ]; then
    echo -e "${RED}Error: Garchy is designed for Arch Linux and its derivatives.${RESET}"
    exit 1
fi

echo -e "${BOLD}[1/5] Checking package manager & dependencies...${RESET}"
if command -v yay >/dev/null 2>&1; then
    AUR_HELPER="yay"
elif command -v paru >/dev/null 2>&1; then
    AUR_HELPER="paru"
else
    AUR_HELPER="sudo pacman"
fi
echo -e "  ${GREEN}✔${RESET} Using package manager: ${AUR_HELPER}"

# Install Core Desktop Packages
echo -e "\n${BOLD}[2/5] Installing Hyprland & Desktop Stack...${RESET}"
PACKAGES=(
    hyprland waybar rofi-wayland dunst kitty thunar
    wlogout wl-clipboard cliphist grim slurp swappy
    easyeffects pipewire pipewire-pulse wireplumber pavucontrol
    ttf-jetbrains-mono-nerd noto-fonts-emoji polkit-kde-agent
    jq python fastfetch
)

$AUR_HELPER -S --needed --noconfirm "${PACKAGES[@]}" || sudo pacman -S --needed --noconfirm "${PACKAGES[@]}"

# Backup existing configs
echo -e "\n${BOLD}[3/5] Backing up existing dotfiles...${RESET}"
BACKUP_DIR="$HOME/.config_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

for dir in hypr waybar rofi kitty dunst; do
    if [ -d "$HOME/.config/$dir" ]; then
        mv "$HOME/.config/$dir" "$BACKUP_DIR/"
        echo -e "  ${YELLOW}ℹ${RESET} Backed up ~/.config/$dir to $BACKUP_DIR/$dir"
    fi
done

# Install Garchy Dotfiles
echo -e "\n${BOLD}[4/5] Deploying Garchy Rice & Wallpapers...${RESET}"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "$HOME/.config" "$HOME/Pictures/Wallpapers" "$HOME/.local/bin"

cp -r "$REPO_DIR/dotfiles/"* "$HOME/.config/"
cp -r "$REPO_DIR/archiso/airootfs/etc/skel/Pictures/Wallpapers/"* "$HOME/Pictures/Wallpapers/" 2>/dev/null || true

# Install AI CLI & System Updater
cp "$REPO_DIR/scripts/garchy-ai.py" "$HOME/.local/bin/garchy-ai"
chmod +x "$HOME/.local/bin/garchy-ai"
ln -sf "$HOME/.local/bin/garchy-ai" "$HOME/.local/bin/ai"

cp "$REPO_DIR/scripts/garchy-update.sh" "$HOME/.local/bin/garchy-update"
chmod +x "$HOME/.local/bin/garchy-update"

# Make all Hyprland scripts executable
chmod +x "$HOME/.config/hypr/scripts/"*.sh "$HOME/.config/hypr/scripts/"*.py 2>/dev/null || true

echo -e "\n${BOLD}[5/5] Finalizing Environment...${RESET}"
# Ensure ~/.local/bin is in PATH in .bashrc and .zshrc
for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
    if [ -f "$rc" ] && ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$rc"; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$rc"
    fi
done

echo -e "\n${GREEN}${BOLD}════════════════════════════════════════════════════════════${RESET}"
echo -e "${GREEN}${BOLD}       ✨ GARCHY LINUX SETUP COMPLETED SUCCESSFULLY! ✨      ${RESET}"
echo -e "${GREEN}${BOLD}════════════════════════════════════════════════════════════${RESET}"
echo -e "• Launch Hyprland or log into your new session"
echo -e "• Try Garchy AI: ${CYAN}garchy-ai status${RESET} or ${CYAN}ai troubleshoot${RESET}"
echo -e "• Background Wallpaper Timer is set to rotate every 10 minutes"
echo -e "• Backups saved in: ${YELLOW}$BACKUP_DIR${RESET}\n"
