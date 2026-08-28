#!/usr/bin/env bash
set -e

# ==============================================================================
# Garchy Linux - Dedicated VM Live Installer Test Launcher (Hyprland / Wayland native)
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT_DIR="$SCRIPT_DIR/out"

ISO_FILE=$(find "$OUT_DIR" -maxdepth 1 -name "garchy-*.iso" | sort -V | tail -n 1)

if [ -z "$ISO_FILE" ] || [ ! -f "$ISO_FILE" ]; then
    echo "No Garchy ISO found in $OUT_DIR! Run ./build-iso.sh first."
    exit 1
fi

echo "=========================================================="
echo "  🚀 Launching Garchy Linux Live ISO in QEMU / KVM"
echo "  💡 TIP: Mouse cursor moves freely into/out of window."
echo "  💡 TIP: If mouse is ever grabbed, press [Ctrl + Alt + G]"
echo "=========================================================="

export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
if [ -z "$WAYLAND_DISPLAY" ]; then
    WL_SOCKET=$(find "$XDG_RUNTIME_DIR" -maxdepth 1 -name "wayland-*" 2>/dev/null | head -n 1)
    if [ -n "$WL_SOCKET" ]; then
        export WAYLAND_DISPLAY="$(basename "$WL_SOCKET")"
    fi
fi

# Create temporary virtual drive for installer testing if not exists (20GB sparse)
VM_DISK="/tmp/garchy_test_disk.qcow2"
if [ ! -f "$VM_DISK" ]; then
    echo "Creating 20GB test virtual hard drive ($VM_DISK)..."
    qemu-img create -f qcow2 "$VM_DISK" 20G >/dev/null
fi

if qemu-system-x86_64 -display help 2>&1 | grep -q 'gtk'; then
    DISPLAY_OPT="-display gtk"
elif qemu-system-x86_64 -display help 2>&1 | grep -q 'sdl'; then
    DISPLAY_OPT="-display sdl,gl=off"
else
    DISPLAY_OPT="-display default"
fi

exec qemu-system-x86_64 \
    -enable-kvm \
    -m 4G \
    -smp 4 \
    -cpu host \
    -drive file="$VM_DISK",format=qcow2,if=virtio \
    -cdrom "$ISO_FILE" \
    -boot menu=on,order=dc \
    -vga virtio \
    -net nic,model=virtio \
    -net user \
    -device virtio-tablet-pci \
    -device virtio-keyboard-pci \
    -device intel-hda \
    -device hda-duplex \
    $DISPLAY_OPT \
    -name "Garchy Linux Live Installer Test"
