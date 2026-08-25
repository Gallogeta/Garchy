#!/usr/bin/env bash
# ==============================================================================
# 🌌 Garchy OS — Install Plymouth Boot Splash Theme
# ==============================================================================

set -e

THEME_SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/garchy-minimal" && pwd)"
TARGET_DIR="/usr/share/plymouth/themes/garchy-minimal"

echo "🌌 [Garchy OS] Installing Plymouth Boot Splash Theme..."
echo "Source: $THEME_SRC"
echo "Target: $TARGET_DIR"

sudo mkdir -p "$TARGET_DIR"
sudo cp -rf "$THEME_SRC"/* "$TARGET_DIR/"

if which plymouth-set-default-theme >/dev/null 2>&1; then
    echo "Applying 'garchy-minimal' as default Plymouth theme..."
    sudo plymouth-set-default-theme -R garchy-minimal || true
    echo "✔ Plymouth theme configured."
fi

echo "========================================================="
echo "✔ Garchy Minimal Plymouth Theme installed successfully!"
echo "To test locally without rebooting, run:"
echo "  sudo plymouthd && sudo plymouth --show-splash && sleep 5 && sudo plymouth --quit"
