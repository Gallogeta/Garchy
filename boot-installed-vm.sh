#!/usr/bin/env bash
set -e

# ==============================================================================
# Garchy Linux - Boot Installed System from Virtual Hard Drive (UEFI / Wayland native)
# ==============================================================================

VM_DISK="/tmp/garchy_test_disk.qcow2"

if [ ! -f "$VM_DISK" ]; then
    echo "No installed virtual disk found at $VM_DISK! Please run ./test-vm.sh first to install."
    exit 1
fi

echo "=========================================================="
echo "  🚀 Booting Installed Garchy OS from Virtual Hard Drive"
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

# Locate UEFI firmware
OVMF_BIOS="/usr/share/edk2/x64/OVMF.4m.fd"
BIOS_OPT=""
if [ -f "$OVMF_BIOS" ]; then
    BIOS_OPT="-bios $OVMF_BIOS"
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
    $BIOS_OPT \
    -drive file="$VM_DISK",format=qcow2,if=virtio \
    -boot c \
    -vga virtio \
    -net nic,model=virtio \
    -net user \
    -device virtio-tablet-pci \
    -device virtio-keyboard-pci \
    -device intel-hda \
    -device hda-duplex \
    $DISPLAY_OPT \
    -name "Garchy OS (Installed System)"
