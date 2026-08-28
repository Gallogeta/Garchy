#!/usr/bin/env python3
"""
==============================================================================
🌌 Garchy OS — Simple & Modern Guided TUI Installer
Step-by-Step wizard for installing Garchy Linux (Btrfs + GRUB UEFI/BIOS + Hyprland + AI)
==============================================================================
"""

import os
import sys
import subprocess
import time

CYAN = "\033[96m"
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

def clear_screen():
    os.system("clear")

def print_header(step_text=""):
    print(f"{CYAN}{BOLD}")
    print(" ╔══════════════════════════════════════════════════════════════╗")
    print(" ║                       🌌 GARCHY OS                           ║")
    print(" ║            Seamless Guided System Installer Matrix           ║")
    print(" ╚══════════════════════════════════════════════════════════════╝")
    print(f"{RESET}")
    if step_text:
        print(f" {YELLOW}{BOLD}▶ {step_text}{RESET}\n")

def run(cmd, check=True):
    print(f"{BLUE}>> {cmd}{RESET}")
    return subprocess.run(cmd, shell=True, check=check)

def get_disks():
    res = subprocess.run(["lsblk", "-d", "-n", "-o", "NAME,SIZE,MODEL,TYPE"], stdout=subprocess.PIPE, text=True)
    disks = []
    for line in res.stdout.strip().splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[-1] == "disk" and not parts[0].startswith("loop") and not parts[0].startswith("airootfs"):
            name = f"/dev/{parts[0]}"
            size = parts[1]
            model = " ".join(parts[2:-1]) if len(parts) > 3 else "Storage Device"
            disks.append((name, size, model))
    return disks

def step_welcome():
    clear_screen()
    print_header("Welcome to Garchy OS")
    print(" Garchy OS is a minimalist, high-performance Arch Linux distribution")
    print(" featuring a tuned Hyprland desktop, built-in Cephalon AI, and gaming/dev stack.\n")
    print(f" {GREEN}This installer will guide you through 4 easy steps:{RESET}")
    print("  1. Select target storage drive")
    print("  2. Set up your user account & password")
    print("  3. Review configuration summary")
    print("  4. Automatic partitioning, packages, dotfiles & universal bootloader deployment\n")
    input(f" Press {BOLD}[ Enter ]{RESET} to begin...")

def step_select_disk():
    clear_screen()
    print_header("Step 1 of 4: Select Target Storage Drive")
    disks = get_disks()
    if not disks:
        print(f"{RED}No suitable storage drives detected!{RESET}")
        sys.exit(1)
        
    print(f" {BOLD}Detected Storage Drives:{RESET}")
    for idx, (name, size, model) in enumerate(disks, 1):
        print(f"   [{CYAN}{idx}{RESET}] {BOLD}{name}{RESET}  —  Size: {YELLOW}{size}{RESET} ({model})")
        
    print(f"\n {RED}{BOLD}WARNING:{RESET} The selected disk will be formatted for Garchy OS.")
    while True:
        choice = input(f"\n Select drive number (1-{len(disks)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(disks):
            selected = disks[int(choice) - 1][0]
            confirm = input(f" Confirm installation to {BOLD}{selected}{RESET}? (yes/no): ").strip().lower()
            if confirm in ("yes", "y"):
                return selected

def step_user_account():
    clear_screen()
    print_header("Step 2 of 4: Create User Account")
    
    while True:
        username = input(f" Enter username [{CYAN}gallo{RESET}]: ").strip() or "gallo"
        if username.isalnum():
            break
        print(f"{RED}Username must be alphanumeric.{RESET}")
        
    while True:
        password = input(" Enter password for your account: ").strip()
        if not password:
            print(f"{RED}Password cannot be empty.{RESET}")
            continue
        confirm = input(" Confirm password: ").strip()
        if password == confirm:
            break
        print(f"{RED}Passwords do not match. Try again.{RESET}")
        
    hostname = input(f" Enter computer hostname [{CYAN}garchy-pc{RESET}]: ").strip() or "garchy-pc"
    return username, password, hostname

def step_confirm_summary(disk, username, hostname):
    clear_screen()
    print_header("Step 3 of 4: Review Installation Summary")
    print(f"  • Target Drive:         {BOLD}{CYAN}{disk}{RESET} (Universal GPT + BIOS + EFI + Btrfs)")
    print(f"  • Filesystem:           {BOLD}Btrfs with subvolumes (@, @home, @snapshots, @var_log){RESET}")
    print(f"  • Bootloader:           {BOLD}Universal GRUB (UEFI & BIOS fallback){RESET}")
    print(f"  • Primary Desktop:      {BOLD}Hyprland (144Hz Wayland){RESET}")
    print(f"  • Fallback Desktop:     {BOLD}XFCE4 (X11){RESET}")
    print(f"  • Login Greeter:        {BOLD}SDDM (3D Cephalon Matrix Theme){RESET}")
    print(f"  • Operator Account:     {BOLD}{username}{RESET} (wheel / sudo enabled)")
    print(f"  • Hostname:             {BOLD}{hostname}{RESET}\n")
    print(f" {RED}{BOLD}ALL DATA ON {disk} WILL BE ERASED.{RESET}\n")
    
    confirm = input(f" Are you ready to install Garchy OS? (type {BOLD}yes{RESET}): ").strip().lower()
    if confirm != "yes":
        print(f"\n{YELLOW}Installation cancelled.{RESET}")
        sys.exit(0)

def step_install(disk, username, password, hostname):
    clear_screen()
    print_header("Step 4 of 4: Installing Garchy OS")
    
    print(f"{BOLD}[1/7] Partitioning & Formatting Drive ({disk})...{RESET}")
    run(f"wipefs -af {disk}")
    run(f"parted -s {disk} mklabel gpt")
    run(f"parted -s {disk} mkpart bios_boot 1MiB 3MiB")
    run(f"parted -s {disk} set 1 bios_grub on")
    run(f"parted -s {disk} mkpart ESP fat32 3MiB 515MiB")
    run(f"parted -s {disk} set 2 esp on")
    run(f"parted -s {disk} mkpart primary btrfs 515MiB 100%")
    
    p1 = f"{disk}p1" if "nvme" in disk or "mmcblk" in disk else f"{disk}1"
    p2 = f"{disk}p2" if "nvme" in disk or "mmcblk" in disk else f"{disk}2"
    p3 = f"{disk}p3" if "nvme" in disk or "mmcblk" in disk else f"{disk}3"
    
    print(f"\n{BOLD}[2/7] Creating Btrfs Subvolumes & Mounting...{RESET}")
    run(f"mkfs.fat -F 32 {p2}")
    run(f"mkfs.btrfs -f {p3}")
    
    run(f"mount {p3} /mnt")
    run("btrfs subvolume create /mnt/@")
    run("btrfs subvolume create /mnt/@home")
    run("btrfs subvolume create /mnt/@snapshots")
    run("btrfs subvolume create /mnt/@var_log")
    run("umount /mnt")
    
    run(f"mount -o noatime,compress=zstd,subvol=@ {p3} /mnt")
    run("mkdir -p /mnt/home /mnt/.snapshots /mnt/var/log /mnt/boot/efi")
    run(f"mount -o noatime,compress=zstd,subvol=@home {p3} /mnt/home")
    run(f"mount -o noatime,compress=zstd,subvol=@snapshots {p3} /mnt/.snapshots")
    run(f"mount -o noatime,compress=zstd,subvol=@var_log {p3} /mnt/var/log")
    run(f"mount {p2} /mnt/boot/efi")
    
    print(f"\n{BOLD}[3/7] Copying Garchy OS Base System & Packages...{RESET}")
    pkgs = ("base base-devel linux linux-headers linux-firmware sudo git zsh starship "
            "grub efibootmgr dosfstools btrfs-progs "
            "hyprland waybar rofi dunst kitty thunar sddm qt6-declarative qt6-5compat xfce4 xfce4-goodies "
            "pipewire pipewire-pulse wireplumber networkmanager ttf-jetbrains-mono-nerd noto-fonts-emoji "
            "python python-pillow tk jq fastfetch awww")
    run(f"pacstrap -K /mnt {pkgs}")
    
    print(f"\n{BOLD}[4/7] Configuring System & User Account...{RESET}")
    run("genfstab -U /mnt >> /mnt/etc/fstab")
    
    with open("/mnt/etc/hostname", "w") as f:
        f.write(f"{hostname}\n")
        
    with open("/mnt/etc/locale.gen", "w") as f:
        f.write("en_US.UTF-8 UTF-8\n")
    run("arch-chroot /mnt locale-gen")
    
    with open("/mnt/etc/locale.conf", "w") as f:
        f.write("LANG=en_US.UTF-8\n")
        
    run(f"arch-chroot /mnt useradd -m -G wheel -s /bin/zsh {username}")
    run(f"echo '{username}:{password}' | arch-chroot /mnt chpasswd")
    run(f"echo 'root:{password}' | arch-chroot /mnt chpasswd")
    run("echo '%wheel ALL=(ALL:ALL) ALL' > /mnt/etc/sudoers.d/10-wheel")
    
    print(f"\n{BOLD}[5/7] Deploying Garchy Rice, Wallpapers & SDDM Themes...{RESET}")
    user_home = f"/mnt/home/{username}"
    run(f"mkdir -p {user_home}/.config {user_home}/Pictures/Wallpapers {user_home}/.local/bin")
    
    if os.path.exists("/etc/skel/.config"):
        run(f"cp -r /etc/skel/.config/* {user_home}/.config/ 2>/dev/null || true")
    if os.path.exists("/etc/skel/Pictures/Wallpapers"):
        run(f"cp -r /etc/skel/Pictures/Wallpapers/* {user_home}/Pictures/Wallpapers/ 2>/dev/null || true")
        
    run("cp /usr/bin/garchy-ai /mnt/usr/bin/garchy-ai 2>/dev/null || true")
    run("cp /usr/bin/garchy-update /mnt/usr/bin/garchy-update 2>/dev/null || true")
    run("cp /usr/bin/set-sddm-wallpaper /mnt/usr/bin/set-sddm-wallpaper 2>/dev/null || true")
    run("cp /usr/bin/install-sddm-theme /mnt/usr/bin/install-sddm-theme 2>/dev/null || true")
    run("ln -sf /usr/bin/garchy-ai /mnt/usr/bin/ai")
    run("chmod +x /mnt/usr/bin/garchy-ai /mnt/usr/bin/garchy-update /mnt/usr/bin/set-sddm-wallpaper /mnt/usr/bin/install-sddm-theme 2>/dev/null || true")
    
    if os.path.exists("/usr/share/sddm/themes"):
        run("mkdir -p /mnt/usr/share/sddm/themes/")
        run("cp -r /usr/share/sddm/themes/* /mnt/usr/share/sddm/themes/ 2>/dev/null || true")
    if os.path.exists("/etc/sddm.conf.d"):
        run("mkdir -p /mnt/etc/sddm.conf.d")
        run("cp -r /etc/sddm.conf.d/* /mnt/etc/sddm.conf.d/ 2>/dev/null || true")
        
    run(f"chown -R 1000:1000 {user_home}")
    
    print(f"\n{BOLD}[6/7] Configuring Initramfs & Universal GRUB Bootloader...{RESET}")
    run("sed -i 's/^HOOKS=(.*)/HOOKS=(base udev autodetect modconf kms keyboard keymap consolefont block btrfs filesystems fsck)/' /mnt/etc/mkinitcpio.conf")
    run("arch-chroot /mnt mkinitcpio -P")
    
    run("arch-chroot /mnt grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=GRUB --removable --recheck")
    run(f"arch-chroot /mnt grub-install --target=i386-pc --recheck {disk} || true")
    run("sed -i 's/^GRUB_TIMEOUT=.*/GRUB_TIMEOUT=3/' /mnt/etc/default/grub 2>/dev/null || true")
    run("arch-chroot /mnt grub-mkconfig -o /boot/grub/grub.cfg")
    
    print(f"\n{BOLD}[7/7] Enabling Core System Services...{RESET}")
    run("arch-chroot /mnt systemctl enable sddm NetworkManager")
    
    print(f"\n{GREEN}{BOLD}══════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{GREEN}{BOLD}   ✨ GARCHY OS INSTALLATION COMPLETED SUCCESSFULLY! ✨        ║{RESET}")
    print(f"{GREEN}{BOLD}══════════════════════════════════════════════════════════════╝{RESET}\n")
    
    print(f" Synchronizing disks and unmounting filesystems...")
    run("sync")
    run("umount -R /mnt 2>/dev/null || true")
    
    print(f"\n {CYAN}{BOLD}Restarting system in 5 seconds...{RESET}")
    for i in range(5, 0, -1):
        print(f" Rebooting in {i}...", end="\r", flush=True)
        time.sleep(1)
        
    print(f"\n {GREEN}Rebooting now!{RESET}")
    run("systemctl --force reboot || reboot -f")

def main():
    if os.geteuid() != 0:
        print(f"{RED}Please run garchy-installer as root (sudo garchy-installer).{RESET}")
        sys.exit(1)
        
    step_welcome()
    disk = step_select_disk()
    username, password, hostname = step_user_account()
    step_confirm_summary(disk, username, hostname)
    step_install(disk, username, password, hostname)

if __name__ == "__main__":
    main()
