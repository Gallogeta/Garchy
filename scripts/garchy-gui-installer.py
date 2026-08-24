#!/usr/bin/env python3
"""
Garchy OS - Modern Point-and-Click Graphical Installer (GUI)
Designed for beginners, children, and power users.
"""

import os
import sys
import subprocess
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox

# Theme Colors
BG_DARK = "#0a0f1d"
BG_CARD = "#131b2e"
FG_LIGHT = "#e0e6ed"
ACCENT_GOLD = "#d4af37"
ACCENT_CYAN = "#00d2ff"
BTN_SUCCESS = "#10b981"
BTN_DANGER = "#ef4444"
FONT_TITLE = ("Sans", 18, "bold")
FONT_HEADING = ("Sans", 13, "bold")
FONT_BODY = ("Sans", 10)
FONT_BTN = ("Sans", 11, "bold")

class GarchyInstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Garchy OS — Graphical System Installer")
        self.geometry("780x540")
        self.minsize(720, 480)
        self.configure(bg=BG_DARK)
        
        # State
        self.selected_disk = tk.StringVar(value="")
        self.username = tk.StringVar(value="gallo")
        self.fullname = tk.StringVar(value="Gallo User")
        self.password = tk.StringVar(value="")
        self.hostname = tk.StringVar(value="garchy-pc")
        self.install_hyprland = tk.BooleanVar(value=True)
        self.install_xfce = tk.BooleanVar(value=True)
        
        # Container for pages
        self.container = tk.Frame(self, bg=BG_DARK)
        self.container.pack(fill="both", expand=True, padx=25, pady=20)
        
        self.frames = {}
        for PageClass in (WelcomePage, DiskPage, UserPage, DesktopPage, SummaryPage, ProgressPage, DonePage):
            page_name = PageClass.__name__
            frame = PageClass(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        self.show_page("WelcomePage")

    def show_page(self, page_name):
        frame = self.frames[page_name]
        if hasattr(frame, "on_show"):
            frame.on_show()
        frame.tkraise()

def create_header(parent, title_text, subtitle_text):
    hdr = tk.Frame(parent, bg=BG_DARK)
    hdr.pack(fill="x", pady=(0, 15))
    lbl_title = tk.Label(hdr, text=f"🌌 {title_text}", font=FONT_TITLE, fg=ACCENT_GOLD, bg=BG_DARK)
    lbl_title.pack(anchor="w")
    lbl_sub = tk.Label(hdr, text=subtitle_text, font=FONT_BODY, fg=ACCENT_CYAN, bg=BG_DARK)
    lbl_sub.pack(anchor="w")
    sep = tk.Frame(hdr, height=2, bg=ACCENT_GOLD)
    sep.pack(fill="x", pady=(8, 0))
    return hdr

def create_nav_buttons(parent, back_cmd=None, next_cmd=None, next_text="Next  ▶", is_install=False):
    nav = tk.Frame(parent, bg=BG_DARK)
    nav.pack(fill="x", side="bottom", pady=(15, 0))
    if back_cmd:
        btn_back = tk.Button(nav, text="◀  Back", font=FONT_BTN, bg="#2d3748", fg=FG_LIGHT,
                             activebackground="#4a5568", activeforeground="#fff",
                             relief="flat", padx=18, pady=8, cursor="hand2", command=back_cmd)
        btn_back.pack(side="left")
    if next_cmd:
        btn_color = ACCENT_GOLD if not is_install else BTN_SUCCESS
        fg_color = "#000" if not is_install else "#fff"
        btn_next = tk.Button(nav, text=next_text, font=FONT_BTN, bg=btn_color, fg=fg_color,
                             activebackground=ACCENT_CYAN, activeforeground="#000",
                             relief="flat", padx=22, pady=8, cursor="hand2", command=next_cmd)
        btn_next.pack(side="right")
    return nav

class WelcomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        
        create_header(self, "Welcome to Garchy OS", "Minimal • Gaming & Dev Ready • Built-in AI Copilot")
        
        body = tk.Frame(self, bg=BG_CARD, padx=25, pady=25, relief="flat", highlightthickness=1, highlightbackground="#2d3748")
        body.pack(fill="both", expand=True, pady=10)
        
        msg = ("Welcome to the official Garchy OS setup wizard!\n\n"
               "This guided installer will help you install Garchy OS in a few simple clicks.\n\n"
               "✨ What will be configured for you:\n"
               "  • Btrfs High-Performance Filesystem with automatic snapshot rollbacks (Snapper)\n"
               "  • Modern Dual-Monitor Glassmorphic Hyprland Desktop Environment\n"
               "  • Full XFCE4 Fallback Desktop for guaranteed reliability\n"
               "  • Beautiful SDDM Graphical Login Screen with Garchy Branding\n"
               "  • Autonomous Garchy AI Copilot and Silent Background System Updater\n\n"
               "Click 'Next' to select your hard drive.")
        
        lbl = tk.Label(body, text=msg, font=FONT_BODY, fg=FG_LIGHT, bg=BG_CARD, justify="left", wraplength=650)
        lbl.pack(anchor="w")
        
        create_nav_buttons(self, next_cmd=lambda: controller.show_page("DiskPage"))

class DiskPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        create_header(self, "Step 1 of 4: Select Target Hard Drive", "Choose where Garchy OS will be installed")
        
        self.card = tk.Frame(self, bg=BG_CARD, padx=20, pady=20, relief="flat", highlightthickness=1, highlightbackground="#2d3748")
        self.card.pack(fill="both", expand=True, pady=10)
        
        self.list_frame = tk.Frame(self.card, bg=BG_CARD)
        self.list_frame.pack(fill="both", expand=True)
        
        create_nav_buttons(self, back_cmd=lambda: controller.show_page("WelcomePage"),
                           next_cmd=self.validate_and_next)

    def on_show(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
            
        disks = []
        try:
            res = subprocess.run(["lsblk", "-d", "-n", "-o", "NAME,SIZE,MODEL,TYPE"], stdout=subprocess.PIPE, text=True)
            for line in res.stdout.strip().splitlines():
                parts = line.split()
                if len(parts) >= 2 and parts[-1] == "disk" and not parts[0].startswith("loop") and not parts[0].startswith("airootfs"):
                    disks.append((f"/dev/{parts[0]}", parts[1], " ".join(parts[2:-1]) if len(parts) > 3 else "Storage Disk"))
        except Exception:
            pass

        if not disks:
            tk.Label(self.list_frame, text="⚠️ No suitable hard drives detected!", font=FONT_HEADING, fg=BTN_DANGER, bg=BG_CARD).pack(pady=20)
            return

        tk.Label(self.list_frame, text="Click to select target drive for installation:", font=FONT_HEADING, fg=FG_LIGHT, bg=BG_CARD).pack(anchor="w", pady=(0, 10))
        
        if not self.controller.selected_disk.get() and disks:
            self.controller.selected_disk.set(disks[0][0])
            
        for dev, size, model in disks:
            r = tk.Radiobutton(self.list_frame, text=f"  💾  {dev}   —   Size: {size}   ({model})",
                               variable=self.controller.selected_disk, value=dev,
                               font=FONT_HEADING, fg=ACCENT_GOLD, bg=BG_CARD, selectcolor=BG_DARK,
                               activebackground=BG_CARD, activeforeground=ACCENT_CYAN, cursor="hand2")
            r.pack(anchor="w", pady=6)
            
        warn = tk.Label(self.list_frame, text="⚠️ Note: The selected disk will be formatted automatically with modern Btrfs subvolumes.",
                        font=FONT_BODY, fg=BTN_DANGER, bg=BG_CARD)
        warn.pack(anchor="w", pady=(15, 0))

    def validate_and_next(self):
        if not self.controller.selected_disk.get():
            messagebox.showwarning("Selection Required", "Please select a target hard drive to continue.")
            return
        self.controller.show_page("UserPage")

class UserPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        create_header(self, "Step 2 of 4: Create User Profile", "Set up your computer login credentials")
        
        card = tk.Frame(self, bg=BG_CARD, padx=25, pady=25, relief="flat", highlightthickness=1, highlightbackground="#2d3748")
        card.pack(fill="both", expand=True, pady=10)
        
        fields = [
            ("Your Name / Display Name:", self.controller.fullname),
            ("Username (for terminal & login):", self.controller.username),
            ("Password:", self.controller.password, True),
            ("Computer Name (Hostname):", self.controller.hostname),
        ]
        
        for idx, item in enumerate(fields):
            lbl_text = item[0]
            var = item[1]
            is_pass = item[2] if len(item) > 2 else False
            
            f = tk.Frame(card, bg=BG_CARD)
            f.pack(fill="x", pady=6)
            
            lbl = tk.Label(f, text=lbl_text, font=FONT_HEADING, fg=FG_LIGHT, bg=BG_CARD, width=28, anchor="w")
            lbl.pack(side="left")
            
            entry = tk.Entry(f, textvariable=var, font=FONT_HEADING, bg=BG_DARK, fg=ACCENT_CYAN,
                             insertbackground=ACCENT_GOLD, relief="flat", highlightthickness=1, highlightbackground="#4a5568")
            if is_pass:
                entry.config(show="●")
            entry.pack(side="left", fill="x", expand=True, padx=(10, 0), ipady=4)
            
        create_nav_buttons(self, back_cmd=lambda: controller.show_page("DiskPage"),
                           next_cmd=self.validate_and_next)

    def validate_and_next(self):
        if not self.controller.username.get().strip():
            messagebox.showwarning("Required", "Username cannot be empty.")
            return
        if not self.controller.password.get():
            messagebox.showwarning("Required", "Please enter a password for your account.")
            return
        self.controller.show_page("DesktopPage")

class DesktopPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        create_header(self, "Step 3 of 4: Desktop Environments", "Choose which graphical sessions to install")
        
        card = tk.Frame(self, bg=BG_CARD, padx=25, pady=25, relief="flat", highlightthickness=1, highlightbackground="#2d3748")
        card.pack(fill="both", expand=True, pady=10)
        
        tk.Label(card, text="Select your desktop experiences (both can be switched at login screen):",
                 font=FONT_HEADING, fg=FG_LIGHT, bg=BG_CARD).pack(anchor="w", pady=(0, 15))
        
        cb1 = tk.Checkbutton(card, text="  🚀  Hyprland (Default) — Ultra-fast Wayland Glassmorphism, animations & AI Copilot",
                             variable=self.controller.install_hyprland, font=FONT_HEADING, fg=ACCENT_GOLD, bg=BG_CARD,
                             selectcolor=BG_DARK, activebackground=BG_CARD, activeforeground=ACCENT_CYAN, cursor="hand2")
        cb1.pack(anchor="w", pady=8)
        
        cb2 = tk.Checkbutton(card, text="  🛡️  XFCE4 (Fallback) — Classic, lightweight and foolproof desktop environment",
                             variable=self.controller.install_xfce, font=FONT_HEADING, fg=ACCENT_GOLD, bg=BG_CARD,
                             selectcolor=BG_DARK, activebackground=BG_CARD, activeforeground=ACCENT_CYAN, cursor="hand2")
        cb2.pack(anchor="w", pady=8)
        
        info = tk.Label(card, text="💡 Garchy OS will automatically install SDDM with a customized Garchy login screen.",
                        font=FONT_BODY, fg=ACCENT_CYAN, bg=BG_CARD)
        info.pack(anchor="w", pady=(20, 0))
        
        create_nav_buttons(self, back_cmd=lambda: controller.show_page("UserPage"),
                           next_cmd=lambda: controller.show_page("SummaryPage"))

class SummaryPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        create_header(self, "Step 4 of 4: Ready to Install", "Review your setup before installation starts")
        
        self.card = tk.Frame(self, bg=BG_CARD, padx=25, pady=20, relief="flat", highlightthickness=1, highlightbackground="#2d3748")
        self.card.pack(fill="both", expand=True, pady=10)
        
        self.lbl_info = tk.Label(self.card, text="", font=FONT_HEADING, fg=FG_LIGHT, bg=BG_CARD, justify="left", anchor="w")
        self.lbl_info.pack(fill="both", expand=True)
        
        create_nav_buttons(self, back_cmd=lambda: controller.show_page("DesktopPage"),
                           next_cmd=self.start_installation, next_text="✨  Install Garchy OS Now", is_install=True)

    def on_show(self):
        text = (f"Target Hard Drive:   {self.controller.selected_disk.get()}\n"
                f"Filesystem:          Btrfs Subvolumes (@, @home, @snapshots) with Snapper\n"
                f"Primary Desktop:     Hyprland Wayland Rice\n"
                f"Fallback Desktop:    XFCE4 Classic Session\n"
                f"Display Manager:     SDDM with Garchy Dark/Gold Theme\n"
                f"User Account:        {self.controller.username.get()} (Administrator/sudo)\n"
                f"Computer Hostname:   {self.controller.hostname.get()}\n"
                f"System AI Copilot:   Enabled (`garchy-ai` / `ai`)")
        self.lbl_info.config(text=text)

    def start_installation(self):
        confirm = messagebox.askyesno("Confirm Installation",
                                      f"Are you sure you want to format {self.controller.selected_disk.get()} and install Garchy OS?\n\nAll existing data on this drive will be replaced.")
        if confirm:
            self.controller.show_page("ProgressPage")

class ProgressPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        create_header(self, "Installing Garchy OS...", "Please relax while your new operating system is deployed")
        
        card = tk.Frame(self, bg=BG_CARD, padx=25, pady=30, relief="flat", highlightthickness=1, highlightbackground="#2d3748")
        card.pack(fill="both", expand=True, pady=10)
        
        self.lbl_status = tk.Label(card, text="Preparing installation...", font=FONT_HEADING, fg=ACCENT_CYAN, bg=BG_CARD)
        self.lbl_status.pack(anchor="w", pady=(10, 15))
        
        self.prog = ttk.Progressbar(card, orient="horizontal", length=600, mode="determinate")
        self.prog.pack(fill="x", pady=10, ipady=4)
        
        self.lbl_detail = tk.Label(card, text="Initializing...", font=FONT_BODY, fg=FG_LIGHT, bg=BG_CARD)
        self.lbl_detail.pack(anchor="w", pady=5)

    def on_show(self):
        threading.Thread(target=self.run_install_thread, daemon=True).start()

    def run_install_thread(self):
        disk = self.controller.selected_disk.get()
        username = self.controller.username.get()
        password = self.controller.password.get()
        hostname = self.controller.hostname.get()
        
        def update_ui(percent, status, detail=""):
            self.prog["value"] = percent
            self.lbl_status.config(text=status)
            self.lbl_detail.config(text=detail)
            self.update_idletasks()
            
        def exec_cmd(cmd):
            subprocess.run(cmd, shell=True, check=True)

        try:
            # 1. Partitioning (15%)
            update_ui(10, "Formatting & Partitioning Drive...", f"Creating GPT partitions on {disk}")
            exec_cmd(f"wipefs -af {disk}")
            exec_cmd(f"parted -s {disk} mklabel gpt")
            exec_cmd(f"parted -s {disk} mkpart ESP fat32 1MiB 513MiB")
            exec_cmd(f"parted -s {disk} set 1 esp on")
            exec_cmd(f"parted -s {disk} mkpart primary btrfs 513MiB 100%")
            
            p1 = f"{disk}p1" if "nvme" in disk or "mmcblk" in disk else f"{disk}1"
            p2 = f"{disk}p2" if "nvme" in disk or "mmcblk" in disk else f"{disk}2"
            
            update_ui(20, "Creating Btrfs Subvolumes...", "Formatting FAT32 EFI and Btrfs root")
            exec_cmd(f"mkfs.fat -F 32 {p1}")
            exec_cmd(f"mkfs.btrfs -f {p2}")
            
            exec_cmd(f"mount {p2} /mnt")
            exec_cmd("btrfs subvolume create /mnt/@")
            exec_cmd("btrfs subvolume create /mnt/@home")
            exec_cmd("btrfs subvolume create /mnt/@snapshots")
            exec_cmd("umount /mnt")
            
            exec_cmd(f"mount -o noatime,compress=zstd,subvol=@ {p2} /mnt")
            exec_cmd("mkdir -p /mnt/home /mnt/.snapshots /mnt/boot")
            exec_cmd(f"mount -o noatime,compress=zstd,subvol=@home {p2} /mnt/home")
            exec_cmd(f"mount -o noatime,compress=zstd,subvol=@snapshots {p2} /mnt/.snapshots")
            exec_cmd(f"mount {p1} /mnt/boot")
            
            # 2. Base Packages (50%)
            update_ui(35, "Installing Core OS Packages...", "Deploying Linux kernel, drivers, Hyprland, XFCE & SDDM")
            pkgs = ("base base-devel linux linux-headers linux-firmware sudo git zsh starship "
                    "hyprland waybar rofi dunst kitty thunar sddm xfce4 xfce4-goodies "
                    "pipewire pipewire-pulse wireplumber networkmanager ttf-jetbrains-mono-nerd noto-fonts-emoji "
                    "efibootmgr snapper btrfs-progs python jq fastfetch")
            exec_cmd(f"pacstrap -K /mnt {pkgs}")
            
            # 3. System Configuration (70%)
            update_ui(70, "Configuring User & Security...", f"Setting up user '{username}' and hostname '{hostname}'")
            exec_cmd("genfstab -U /mnt >> /mnt/etc/fstab")
            
            with open("/mnt/etc/hostname", "w") as f:
                f.write(f"{hostname}\n")
            with open("/mnt/etc/locale.gen", "w") as f:
                f.write("en_US.UTF-8 UTF-8\n")
            exec_cmd("arch-chroot /mnt locale-gen")
            with open("/mnt/etc/locale.conf", "w") as f:
                f.write("LANG=en_US.UTF-8\n")
                
            exec_cmd(f"arch-chroot /mnt useradd -m -G wheel -s /bin/zsh {username}")
            exec_cmd(f"echo '{username}:{password}' | arch-chroot /mnt chpasswd")
            exec_cmd(f"echo 'root:{password}' | arch-chroot /mnt chpasswd")
            exec_cmd("echo '%wheel ALL=(ALL:ALL) ALL' > /mnt/etc/sudoers.d/10-wheel")
            
            # 4. Dotfiles, SDDM Theme & Garchy AI (85%)
            update_ui(85, "Deploying Garchy Desktop Rice & SDDM Theme...", "Copying wallpapers, Hyprland configs and Garchy AI")
            user_home = f"/mnt/home/{username}"
            exec_cmd(f"mkdir -p {user_home}/.config {user_home}/Pictures/Wallpapers {user_home}/.local/bin")
            
            if os.path.exists("/etc/skel/.config"):
                exec_cmd(f"cp -r /etc/skel/.config/* {user_home}/.config/ 2>/dev/null || true")
            if os.path.exists("/etc/skel/Pictures/Wallpapers"):
                exec_cmd(f"cp -r /etc/skel/Pictures/Wallpapers/* {user_home}/Pictures/Wallpapers/ 2>/dev/null || true")
                
            exec_cmd("cp /usr/bin/garchy-ai /mnt/usr/bin/garchy-ai 2>/dev/null || true")
            exec_cmd("cp /usr/bin/garchy-update /mnt/usr/bin/garchy-update 2>/dev/null || true")
            exec_cmd("ln -sf /usr/bin/garchy-ai /mnt/usr/bin/ai")
            exec_cmd("chmod +x /mnt/usr/bin/garchy-ai /mnt/usr/bin/garchy-update 2>/dev/null || true")
            
            # Copy SDDM Theme
            if os.path.exists("/usr/share/sddm/themes/garchy"):
                exec_cmd("mkdir -p /mnt/usr/share/sddm/themes/")
                exec_cmd("cp -r /usr/share/sddm/themes/garchy /mnt/usr/share/sddm/themes/ 2>/dev/null || true")
            if os.path.exists("/etc/sddm.conf.d"):
                exec_cmd("mkdir -p /mnt/etc/sddm.conf.d")
                exec_cmd("cp -r /etc/sddm.conf.d/* /mnt/etc/sddm.conf.d/ 2>/dev/null || true")
                
            exec_cmd(f"chown -R 1000:1000 {user_home}")
            
            # 5. Bootloader & Services (95%)
            update_ui(95, "Configuring UEFI Bootloader & Services...", "Enabling SDDM, NetworkManager & systemd-boot")
            exec_cmd("arch-chroot /mnt bootctl install")
            with open("/mnt/boot/loader/loader.conf", "w") as f:
                f.write("default garchy.conf\ntimeout 3\nconsole-mode max\neditor no\n")
                
            p2_uuid = subprocess.check_output(f"blkid -s UUID -o value {p2}", shell=True).decode().strip()
            with open("/mnt/boot/loader/entries/garchy.conf", "w") as f:
                f.write(f"title   Garchy OS\nlinux   /vmlinuz-linux\ninitrd  /initramfs-linux.img\noptions root=UUID={p2_uuid} rootflags=subvol=@ rw quiet splash\n")
                
            exec_cmd("arch-chroot /mnt systemctl enable sddm NetworkManager")
            
            # 6. Complete (100%)
            update_ui(100, "Installation Complete!", "Garchy OS is ready to boot!")
            time.sleep(1)
            self.controller.show_page("DonePage")
            
        except Exception as e:
            messagebox.showerror("Installation Error", f"An error occurred during installation:\n\n{str(e)}")

class DonePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        create_header(self, "✨ Garchy OS Successfully Installed! ✨", "Your modern AI-powered Linux system is ready")
        
        card = tk.Frame(self, bg=BG_CARD, padx=25, pady=30, relief="flat", highlightthickness=1, highlightbackground="#2d3748")
        card.pack(fill="both", expand=True, pady=10)
        
        msg = ("🎉 Congratulations! Garchy OS has been installed successfully.\n\n"
               "What happens next:\n"
               "  1. Click 'Reboot Now' below to restart your computer.\n"
               "  2. You will be greeted by the custom Garchy login screen (SDDM).\n"
               "  3. Enter your password and log straight into Hyprland!\n"
               "  4. If you ever need it, select 'XFCE' from the login screen session menu.\n\n"
               "Enjoy your new system!")
        
        lbl = tk.Label(card, text=msg, font=FONT_HEADING, fg=FG_LIGHT, bg=BG_CARD, justify="left")
        lbl.pack(anchor="w")
        
        nav = tk.Frame(self, bg=BG_DARK)
        nav.pack(fill="x", side="bottom", pady=15)
        
        btn_reboot = tk.Button(nav, text="🔄  Reboot Now", font=FONT_TITLE, bg=BTN_SUCCESS, fg="#fff",
                               activebackground=ACCENT_CYAN, activeforeground="#000",
                               relief="flat", padx=30, pady=10, cursor="hand2", command=self.reboot_system)
        btn_reboot.pack(side="right")

    def reboot_system(self):
        subprocess.run(["systemctl", "reboot"])

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("Please run garchy-gui-installer as root (sudo garchy-gui-installer).")
        sys.exit(1)
    app = GarchyInstallerApp()
    app.mainloop()
