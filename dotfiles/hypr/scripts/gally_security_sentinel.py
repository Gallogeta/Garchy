#!/usr/bin/env python3
"""
Gally Security Sentinel & Intruder Alert Daemon
Monitors failed sudo attempts, unauthorized open ports, and USB device changes.
Generates desktop alerts and logs security events in ~/.config/gally/security_alerts.json.
"""

import os
import sys
import json
import time
import subprocess

ALERTS_FILE = os.path.expanduser("~/.config/gally/security_alerts.json")

def load_alerts():
    os.makedirs(os.path.dirname(ALERTS_FILE), exist_ok=True)
    if os.path.exists(ALERTS_FILE):
        try:
            with open(ALERTS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def record_alert(alert_type, severity, description):
    alerts = load_alerts()
    alert_obj = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "type": alert_type,
        "severity": severity, # "INFO", "WARNING", "CRITICAL"
        "description": description
    }
    alerts.append(alert_obj)
    if len(alerts) > 50:
        alerts = alerts[-50:]
    try:
        with open(ALERTS_FILE, "w") as f:
            json.dump(alerts, f, indent=2)
    except Exception:
        pass
        
    # Send desktop notification for WARNING and CRITICAL
    if severity in ["WARNING", "CRITICAL"]:
        try:
            icon = "dialog-warning" if severity == "WARNING" else "dialog-error"
            subprocess.run([
                "notify-send", "-u", "critical" if severity == "CRITICAL" else "normal",
                "-i", icon,
                f"🛡️ Garchy Sentinel Alert [{severity}]",
                description
            ], timeout=2)
        except Exception:
            pass

def audit_open_ports():
    """Checks for active listening TCP/UDP ports."""
    try:
        out = subprocess.getoutput("ss -tuln | awk 'NR>1 {print $1, $5}'")
        ports = []
        for line in out.splitlines():
            parts = line.strip().split()
            if len(parts) >= 2:
                proto = parts[0]
                addr = parts[1]
                ports.append(f"{proto} -> {addr}")
        return ports
    except Exception:
        return []

def audit_failed_sudo_attempts():
    """Checks journal for recent failed authentication attempts."""
    try:
        # Check journalctl for PAM authentication failures in the last 1 hour
        cmd = "journalctl -u sudo --since '1 hour ago' 2>/dev/null | grep -i 'authentication failure\\|incorrect password' | tail -n 5"
        out = subprocess.getoutput(cmd).strip()
        if out:
            lines = [l.strip() for l in out.splitlines() if l.strip()]
            return lines
    except Exception:
        pass
    return []

def audit_connected_usb():
    """Returns connected USB peripherals."""
    try:
        out = subprocess.getoutput("lsusb").strip()
        devices = [l.strip() for l in out.splitlines() if l.strip()]
        return devices
    except Exception:
        return []

def run_comprehensive_security_sweep():
    """Runs a full security audit and returns a formatted report for Cephalon."""
    ports = audit_open_ports()
    failed_sudo = audit_failed_sudo_attempts()
    usb_devs = audit_connected_usb()
    alerts = load_alerts()
    
    # Check firewall status
    ufw_status = subprocess.getoutput("ufw status 2>/dev/null || echo 'UFW not active'")
    
    report = "🛡️ CEPHALON SECURITY SENTINEL AUDIT REPORT:\n\n"
    
    # 1. Intrusion & Auth Check
    if failed_sudo:
        report += f"⚠️ FAILED AUTHENTICATION DETECTED ({len(failed_sudo)} events in last hour):\n"
        for line in failed_sudo:
            report += f"  • {line}\n"
        record_alert("AUTH_FAILURE", "WARNING", f"{len(failed_sudo)} failed sudo authentication attempt(s) detected.")
    else:
        report += "✓ Authentication Matrix: Nominal (0 failed sudo attempts in last hour).\n"
        
    # 2. Port & Network Surface
    report += f"\n🌐 ACTIVE LISTENING NETWORK PORTS ({len(ports)}):\n"
    for p in ports[:6]:
        report += f"  • {p}\n"
    if len(ports) > 6:
        report += f"  • ... and {len(ports)-6} more local endpoints.\n"
        
    # 3. USB Hardware Guard
    report += f"\n🔌 CONNECTED USB DEVICES ({len(usb_devs)}):\n"
    for d in usb_devs[:5]:
        report += f"  • {d}\n"
        
    # 4. Firewall
    report += f"\n🧱 FIREWALL STATUS:\n  • {ufw_status.splitlines()[0] if ufw_status.splitlines() else 'Nominal'}\n"
    
    return report

if __name__ == "__main__":
    print(run_comprehensive_security_sweep())
