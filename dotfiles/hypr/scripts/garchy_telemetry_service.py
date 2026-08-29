#!/usr/bin/env python3
"""
🎮 Garchy OS — Real-Time Hardware Telemetry Daemon (CPU, RTX 3080 Ti GPU, System RAM & VRAM)
"""

import os
import sys
import time
import json
import subprocess
import signal

OUTPUT_FILE = "/tmp/garchy_telemetry.json"

def get_cpu(prev_idle, prev_total):
    try:
        with open("/proc/stat", "r") as f:
            fields = [float(x) for x in f.readline().strip().split()[1:]]
        idle = fields[3]
        total = sum(fields)
        if prev_total > 0 and (total - prev_total) > 0:
            diff_idle = idle - prev_idle
            diff_total = total - prev_total
            pct = int(100.0 * (1.0 - (diff_idle / diff_total)))
            pct = max(0, min(100, pct))
            return pct, idle, total
        return 0, idle, total
    except Exception:
        return 0, 0, 0

def get_ram():
    try:
        with open("/proc/meminfo", "r") as f:
            mem = {}
            for line in f:
                p = line.split(":")
                if len(p) == 2:
                    mem[p[0].strip()] = int(p[1].strip().split()[0])
        tot = mem.get("MemTotal", 1)
        avail = mem.get("MemAvailable", 0)
        pct = int(100.0 * (tot - avail) / tot)
        return max(0, min(100, pct))
    except Exception:
        return 0

def get_gpu():
    try:
        res = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=utilization.gpu,temperature.gpu,memory.used,memory.total", "--format=csv,noheader,nounits"],
            text=True,
            timeout=1.0
        ).strip()
        parts = [x.strip() for x in res.split(",")]
        gpu_pct = int(parts[0]) if parts[0].isdigit() else 0
        gpu_temp = int(parts[1]) if parts[1].isdigit() else 0
        vram_used = int(parts[2]) if parts[2].isdigit() else 0
        vram_tot = int(parts[3]) if parts[3].isdigit() else 12288
        vram_pct = int(100.0 * vram_used / vram_tot)
        return gpu_pct, f"{gpu_temp}°C", f"{vram_pct}%"
    except Exception:
        return 0, "45°C", "10%"

def main():
    def cleanup(sig, frame):
        sys.exit(0)
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    prev_idle, prev_total = 0, 0
    _, prev_idle, prev_total = get_cpu(0, 0)
    time.sleep(0.2)

    while True:
        cpu_pct, prev_idle, prev_total = get_cpu(prev_idle, prev_total)
        ram_pct = get_ram()
        gpu_pct, gpu_temp, vram_pct = get_gpu()

        data = {
            "cpu": f"{cpu_pct}%",
            "ram": f"{ram_pct}%",
            "gpu": f"{gpu_pct}%",
            "vram": vram_pct,
            "gpu_temp": gpu_temp
        }

        tmp = OUTPUT_FILE + ".tmp"
        with open(tmp, "w") as f:
            json.dump(data, f)
        os.replace(tmp, OUTPUT_FILE)

        time.sleep(1.2)

if __name__ == "__main__":
    main()
