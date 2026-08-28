#!/usr/bin/env bash
# ==============================================================================
# Garchy OS — SDDM Login Screen Wallpaper Changer (CLI & GUI & Thunar Action)
# ==============================================================================

CYAN='\033[96m'
GREEN='\033[92m'
YELLOW='\033[93m'
RED='\033[91m'
BOLD='\033[1m'
RESET='\033[0m'

TARGET_IMAGE="$1"
DEFAULT_WALLPAPER="~/Pictures/Wallpapers/garchy-minimal.jpg"
THEMES_DIR="/usr/share/sddm/themes"

# Detect Active SDDM Theme
ACTIVE_THEME="garchy"
if [ -f /etc/sddm.conf.d/kde_settings.conf ]; then
    DETECTED=$(grep "^Current=" /etc/sddm.conf.d/kde_settings.conf | cut -d'=' -f2 | tr -d ' ')
    [ -n "$DETECTED" ] && ACTIVE_THEME="$DETECTED"
elif [ -f /etc/sddm.conf.d/garchy.conf ]; then
    DETECTED=$(grep "^Current=" /etc/sddm.conf.d/garchy.conf | cut -d'=' -f2 | tr -d ' ')
    [ -n "$DETECTED" ] && ACTIVE_THEME="$DETECTED"
fi

# Reset flag
if [ "$TARGET_IMAGE" = "--reset" ] || [ "$TARGET_IMAGE" = "-r" ]; then
    TARGET_IMAGE="$DEFAULT_WALLPAPER"
fi

# GUI File Chooser if no argument supplied
if [ -z "$TARGET_IMAGE" ]; then
    if command -v zenity >/dev/null 2>&1; then
        TARGET_IMAGE=$(zenity --file-selection --title="🌌 Select SDDM Login Screen Wallpaper" \
            --filename="~/Pictures/Wallpapers/" \
            --file-filter="Images (*.jpg *.png *.jpeg *.webp) | *.jpg *.png *.jpeg *.webp *.JPG *.PNG *.JPEG *.WEBP" \
            2>/dev/null)
    elif command -v kdialog >/dev/null 2>&1; then
        TARGET_IMAGE=$(kdialog --getopenfilename "~/Pictures/Wallpapers/" "*.jpg *.png *.jpeg *.webp" \
            --title "Select SDDM Login Wallpaper" 2>/dev/null)
    fi
fi

# If still empty (user cancelled), exit quietly
if [ -z "$TARGET_IMAGE" ]; then
    echo -e "${YELLOW}No image selected. Operation cancelled.${RESET}"
    exit 0
fi

if [ ! -f "$TARGET_IMAGE" ]; then
    echo -e "${RED}Error: File not found: $TARGET_IMAGE${RESET}"
    if command -v notify-send >/dev/null 2>&1; then
        notify-send -u critical "SDDM Wallpaper" "File not found: $TARGET_IMAGE"
    fi
    exit 1
fi

echo -e "${CYAN}${BOLD}🌌 Updating SDDM Login Wallpaper for theme '${ACTIVE_THEME}'...${RESET}"
echo -e "Selected Image: ${BOLD}$TARGET_IMAGE${RESET}"

# Execute with root privileges
UPDATE_SCRIPT="/tmp/update_sddm_wall_$$.sh"
cat << ROOT_SCRIPT > "$UPDATE_SCRIPT"
#!/usr/bin/env bash
set -e

# Update in active theme and all garchy themes if available
for t in "$ACTIVE_THEME" garchy garchy-warframe garchy-kids garchy-cyber garchy-matrix garchy-elegance; do
    if [ -d "$THEMES_DIR/\$t" ]; then
        cp -f "$TARGET_IMAGE" "$THEMES_DIR/\$t/background.jpg"
        chmod 644 "$THEMES_DIR/\$t/background.jpg"
    fi
done
ROOT_SCRIPT

chmod +x "$UPDATE_SCRIPT"

if [ "$EUID" -eq 0 ]; then
    bash "$UPDATE_SCRIPT"
else
    if command -v pkexec >/dev/null 2>&1; then
        pkexec bash "$UPDATE_SCRIPT"
    else
        sudo bash "$UPDATE_SCRIPT"
    fi
fi

rm -f "$UPDATE_SCRIPT"

echo -e "${GREEN}${BOLD}✔ SDDM Login Wallpaper successfully updated!${RESET}"

if command -v notify-send >/dev/null 2>&1; then
    notify-send -i preferences-desktop-wallpaper "🌌 Garchy SDDM" "Login screen wallpaper updated to $(basename "$TARGET_IMAGE")"
fi
