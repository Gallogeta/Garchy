#!/usr/bin/env bash
set -e

# Garchy Linux ISO Local Build Script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="/tmp/garchy-archiso-work"
OUT_DIR="$SCRIPT_DIR/out"

echo "Building Garchy Linux ISO..."
mkdir -p "$OUT_DIR"

if ! command -v mkarchiso >/dev/null 2>&1; then
    echo "mkarchiso not found. Installing archiso..."
    sudo pacman -S --needed --noconfirm archiso
fi

sudo rm -rf "$WORK_DIR"
sudo mkarchiso -v -w "$WORK_DIR" -o "$OUT_DIR" "$SCRIPT_DIR/archiso"

echo "Build complete! ISO image is located at: $OUT_DIR"
