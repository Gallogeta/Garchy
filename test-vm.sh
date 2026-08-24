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

# Strictly prevent running as root/sudo
if [ "$EUID" -eq 0 ]; then
    echo -e "\033[91m\033[1m❌ ERROR: test-vm.sh must NOT be run with sudo.\033[0m"
    echo -e "👉 Please run as your normal user:\033[96m ./test-vm.sh\033[0m\n"
    exit 1
fi

# Ensure Wayland / XDG environment is loaded
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
if [ -z "$WAYLAND_DISPLAY" ]; then
    WL_SOCKET=$(find "$XDG_RUNTIME_DIR" -maxdepth 1 -name "wayland-*" 2>/dev/null | head -n 1)
    if [ -n "$WL_SOCKET" ]; then
        export WAYLAND_DISPLAY="$(basename "$WL_SOCKET")"
    fi
fi

# Try SDL display first (best for Wayland / Hyprland), fallback to GTK
if qemu-system-x86_64 -display help 2>&1 | grep -q 'sdl'; then
    DISPLAY_OPT="-display sdl,gl=off"
elif qemu-system-x86_64 -display help 2>&1 | grep -q 'gtk'; then
    DISPLAY_OPT="-display gtk"
else
    DISPLAY_OPT="-display default"
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
