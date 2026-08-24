#!/usr/bin/env bash
set -e

# Garchy Linux - Dedicated VM Test Launcher (Hyprland / Wayland native)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT_DIR="$SCRIPT_DIR/out"

ISO_FILE=$(find "$OUT_DIR" -maxdepth 1 -name "garchy-*.iso" | sort -V | tail -n 1)

if [ -z "$ISO_FILE" ] || [ ! -f "$ISO_FILE" ]; then
    echo "No Garchy ISO found in $OUT_DIR! Run ./build-iso.sh first."
    exit 1
fi

echo "Found Garchy ISO: $ISO_FILE ($(du -h "$ISO_FILE" | cut -f1))"
echo "Launching QEMU / KVM Virtual Machine with hardware acceleration..."

# Do not run QEMU with sudo - drop to original user if invoked via sudo
if [ "$EUID" -eq 0 ] && [ -n "$SUDO_USER" ]; then
    echo "Re-launching as normal user ($SUDO_USER)..."
    exec su "$SUDO_USER" -c "$0"
fi

export SDL_VIDEODRIVER=wayland

# Authorize XWayland if needed
if command -v xhost >/dev/null 2>&1; then
    xhost +SI:localuser:$(whoami) 2>/dev/null || true
fi

# Try SDL display first (best for Wayland / Hyprland), fallback to GTK
if qemu-system-x86_64 -display help 2>&1 | grep -q 'sdl'; then
    DISPLAY_OPT="-display sdl,gl=off"
else
    DISPLAY_OPT="-display gtk"
fi

qemu-system-x86_64 \
    -enable-kvm \
    -m 4G \
    -smp 4 \
    -cpu host \
    -cdrom "$ISO_FILE" \
    -boot d \
    -vga virtio \
    $DISPLAY_OPT \
    -name "Garchy Linux Live Test"
