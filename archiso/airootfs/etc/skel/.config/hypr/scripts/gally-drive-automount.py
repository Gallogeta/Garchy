#!/usr/bin/env python3
"""
Gally OS — Universal Storage & Drive Automounter Daemon
Automatically detects and mounts all connected internal and external drives,
removable USBs, SD cards, and secondary SSDs/HDDs both at startup and dynamically
on hotplug/connection via UDisks2.
"""

import os
import sys
import time
import json
import fcntl
import select
import subprocess

LOCK_FILE = "/tmp/gally_drive_automount.lock"

def get_unmounted_partitions():
    """Returns list of unmounted block devices with valid filesystems."""
    try:
        res = subprocess.run(
            ['lsblk', '-J', '-o', 'NAME,PATH,FSTYPE,LABEL,MOUNTPOINT,TYPE,SIZE'],
            capture_output=True, text=True, timeout=5
        )
        if res.returncode != 0 or not res.stdout.strip():
            return []
        
        data = json.loads(res.stdout)
        unmounted = []

        def scan_dev(dev):
            fstype = dev.get('fstype')
            mountpoint = dev.get('mountpoint')
            name = dev.get('name', '')
            
            # Filter valid storage partitions
            if fstype and not mountpoint:
                if fstype not in ['swap', 'squashfs', 'crypto_LUKS'] and not name.startswith(('loop', 'zram')):
                    unmounted.append(dev)
            for child in dev.get('children', []):
                scan_dev(child)

        for dev in data.get('blockdevices', []):
            scan_dev(dev)

        return unmounted
    except Exception:
        return []

def notify_user(title, message, icon="drive-harddisk"):
    """Sends desktop notification via notify-send."""
    try:
        subprocess.Popen([
            'notify-send', '-a', 'Gally Storage',
            '-i', icon,
            title, message
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def mount_partition(dev_info):
    """Mounts a partition using udisksctl and sends a notification."""
    path = dev_info.get('path')
    if not path:
        return False
    
    label = dev_info.get('label') or dev_info.get('name')
    fstype = dev_info.get('fstype', 'storage')
    size = dev_info.get('size', '')
    
    try:
        res = subprocess.run(
            ['udisksctl', 'mount', '-b', path, '--no-user-interaction'],
            capture_output=True, text=True, timeout=10
        )
        output = res.stdout.strip() or res.stderr.strip()
        if res.returncode == 0 and "Mounted" in output:
            # Extract mountpoint from output: "Mounted /dev/sdX at /run/media/..."
            mountpoint = output.split(" at ")[-1].strip() if " at " in output else path
            notify_user("💾 Storage Connected", f"{label} ({size} {fstype})\nMounted at: {mountpoint}")
            return True
    except Exception:
        pass
    return False

def mount_all_unmounted():
    """Sweeps all unmounted partitions and mounts them."""
    unmounted = get_unmounted_partitions()
    mounted_count = 0
    for dev in unmounted:
        if mount_partition(dev):
            mounted_count += 1
    return mounted_count

def run_monitor_loop():
    """Monitors udisksctl events for live drive connection/hotplug."""
    # Ensure single instance
    try:
        lock_fd = open(LOCK_FILE, "w")
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except (IOError, BlockingIOError):
        # Another instance is already running
        sys.exit(0)

    # Initial sweep at startup
    mount_all_unmounted()

    # Start UDisks2 event monitor
    while True:
        try:
            proc = subprocess.Popen(
                ['udisksctl', 'monitor'],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True
            )

            debounce_time = 0
            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                
                # Check for block device additions or interface creations
                if "Added /org/freedesktop/UDisks2/block_devices/" in line or "org.freedesktop.UDisks2.Filesystem:" in line:
                    now = time.time()
                    if now - debounce_time > 0.8:
                        debounce_time = now
                        time.sleep(0.6)  # Allow udev to settle partition metadata
                        mount_all_unmounted()

        except Exception:
            time.sleep(3)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["--once", "mount", "scan"]:
        count = mount_all_unmounted()
        print(f"Mounted {count} drive(s).")
    else:
        run_monitor_loop()
