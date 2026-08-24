#!/usr/bin/env bash
set -e

# ==============================================================================
#   GARCHY LINUX - Cleanup, ISO Compilation & VM Test Launcher
# ==============================================================================

CYAN='\033[96m'
GREEN='\033[92m'
YELLOW='\033[93m'
BOLD='\033[1m'
RESET='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="/tmp/garchy-archiso-work"
OUT_DIR="$SCRIPT_DIR/out"

echo -e "${CYAN}${BOLD}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║       🌌 GARCHY LINUX: CLEANUP, BUILD & VM TEST            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${RESET}"

# 1. Prune Bloat, Leftovers & Snapd
echo -e "${BOLD}[1/5] Removing Old Desktop Remnants, Surfshark & Snapd...${RESET}"
sudo pacman -Rns --noconfirm \
    xfce4-session plank parole galculator \
    gnome-tour gnome-logs baobab malcontent \
    cosmic-randr lightdm-gtk-greeter-settings \
    filelight plasma-firewall cervisia snapd 2>/dev/null || true

# 2. Prune Orphans
echo -e "\n${BOLD}[2/5] Cleaning Orphaned Packages...${RESET}"
ORPHANS=$(pacman -Qtdq 2>/dev/null || true)
if [ -n "$ORPHANS" ]; then
    sudo pacman -Rns --noconfirm $ORPHANS 2>/dev/null || true
    echo -e "  ${GREEN}✔${RESET} Orphan packages removed."
else
    echo -e "  ${GREEN}✔${RESET} No orphan packages found."
fi

# 3. Ensure archiso is installed
echo -e "\n${BOLD}[3/5] Installing Archiso build engine...${RESET}"
sudo pacman -S --needed --noconfirm archiso edk2-ovmf qemu-desktop

# 4. Sync Bootloader & Config Templates
echo -e "\n${BOLD}[4/5] Preparing Garchy ISO Profile...${RESET}"
mkdir -p "$SCRIPT_DIR/archiso" "$OUT_DIR"

if [ -d /usr/share/archiso/configs/releng ]; then
    [ ! -f "$SCRIPT_DIR/archiso/pacman.conf" ] && cp /usr/share/archiso/configs/releng/pacman.conf "$SCRIPT_DIR/archiso/"
    [ ! -d "$SCRIPT_DIR/archiso/efiboot" ] && cp -r /usr/share/archiso/configs/releng/efiboot "$SCRIPT_DIR/archiso/"
    [ ! -d "$SCRIPT_DIR/archiso/syslinux" ] && cp -r /usr/share/archiso/configs/releng/syslinux "$SCRIPT_DIR/archiso/"
    [ ! -d "$SCRIPT_DIR/archiso/grub" ] && cp -r /usr/share/archiso/configs/releng/grub "$SCRIPT_DIR/archiso/"
fi

# Ensure multilib is enabled in archiso/pacman.conf
sed -i 's/^#\[multilib\]/[multilib]/' "$SCRIPT_DIR/archiso/pacman.conf"
sed -i '/^\[multilib\]/{n;s/^#Include/Include/}' "$SCRIPT_DIR/archiso/pacman.conf"

# 5. Build the Bootable ISO
echo -e "\n${BOLD}[5/5] Compiling Garchy Linux Live ISO with mkarchiso...${RESET}"
sudo rm -rf "$WORK_DIR"
sudo mkarchiso -v -w "$WORK_DIR" -o "$OUT_DIR" "$SCRIPT_DIR/archiso"

ISO_FILE=$(find "$OUT_DIR" -maxdepth 1 -name "garchy-*.iso" | head -n 1)

echo -e "\n${GREEN}${BOLD}════════════════════════════════════════════════════════════${RESET}"
echo -e "${GREEN}${BOLD}       ✨ GARCHY ISO CREATED SUCCESSFULLY! ✨               ${RESET}"
echo -e "${GREEN}${BOLD}════════════════════════════════════════════════════════════${RESET}"
echo -e "ISO Path: ${CYAN}$ISO_FILE${RESET}"
echo -e "Size:     $(du -h "$ISO_FILE" | cut -f1)"

# 6. Launch in QEMU / KVM Virtual Machine
echo -e "\n${CYAN}${BOLD}🚀 Launching Garchy Linux in KVM Virtual Machine...${RESET}"
qemu-system-x86_64 \
    -enable-kvm \
    -m 4G \
    -smp 4 \
    -cpu host \
    -cdrom "$ISO_FILE" \
    -boot d \
    -vga virtio \
    -display gtk \
    -name "Garchy Linux Live Test"
