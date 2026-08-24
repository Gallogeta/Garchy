#!/usr/bin/env bash
# Garchy Linux ISO Profile Definition

iso_name="garchy"
iso_label="GARCHY_$(date +%Y%m)"
iso_publisher="Gallo <https://github.com/Gallogeta/Garchy>"
iso_application="Garchy Linux Live & Install Medium (Arch + Hyprland + AI)"
iso_version="$(date +%Y.%m.%d)"
install_dir="arch"
buildmodes=('iso')
bootmodes=('bios.syslinux.mbr' 'bios.syslinux.eltorito' 'uefi-ia32.systemd-boot.esp' 'uefi-x64.systemd-boot.esp')
arch="x86_64"
pacman_conf="pacman.conf"
airootfs_image_type="squashfs"
airootfs_image_tool_options=('-comp' 'zstd' '-Xcompression-level' '15')
file_permissions=(
  ["/etc/shadow"]="0:0:400"
  ["/root"]="0:0:750"
  ["/root/.automated_script.sh"]="0:0:755"
  ["/usr/bin/garchy-ai"]="0:0:755"
  ["/usr/bin/garchy-update"]="0:0:755"
  ["/etc/skel/.config/hypr/scripts/wallpaper-timer.sh"]="0:0:755"
  ["/etc/skel/.config/hypr/scripts/wallpaper-select.sh"]="0:0:755"
  ["/etc/skel/.config/hypr/scripts/dual-desktop.sh"]="0:0:755"
  ["/etc/skel/.config/hypr/scripts/minimize-window.sh"]="0:0:755"
  ["/etc/skel/.config/hypr/scripts/window-switch.sh"]="0:0:755"
  ["/etc/skel/.config/hypr/scripts/theme-switcher.sh"]="0:0:755"
  ["/etc/skel/.config/hypr/scripts/screenshot.sh"]="0:0:755"
  ["/etc/skel/.config/hypr/scripts/rofi-launcher.sh"]="0:0:755"
  ["/etc/skel/.config/hypr/scripts/togglefloat.sh"]="0:0:755"
  ["/etc/skel/.config/hypr/scripts/force-kill.sh"]="0:0:755"
  ["/etc/skel/.config/hypr/scripts/media-control.sh"]="0:0:755"
)
