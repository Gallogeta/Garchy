#!/usr/bin/env python3
"""
🍵 Garchy OS — Real-Time CAVA Audio Visualizer Service
Streams live 12-band frequency spectrum directly from PipeWire/Pulse to /tmp/garchy_cava_bars.json.
"""

import os
import sys
import json
import time
import subprocess
import signal

OUTPUT_FILE = "/tmp/garchy_cava_bars.json"
CONFIG_FILE = "/tmp/garchy_cava_cfg"

def create_config():
    with open(CONFIG_FILE, "w") as f:
        f.write("""[general]
framerate = 60
bars = 12
autosens = 1
overshoot = 20
sensitivity = 100
lower_cutoff_freq = 50
higher_cutoff_freq = 12000

[input]
method = pulse
source = auto

[output]
method = raw
data_format = ascii
ascii_max_range = 22
bar_delimiter = 59
""")

def main():
    create_config()
    proc = subprocess.Popen(
        ["cava", "-p", CONFIG_FILE],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1
    )

    def cleanup(sig, frame):
        proc.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    last_write = 0
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        try:
            parts = [int(p) for p in line.strip().split(";") if p.strip().isdigit()]
            if len(parts) >= 12:
                # Smooth minimum floor of 3
                bars = [max(3, min(22, p)) for p in parts[:12]]
                now = time.time()
                if now - last_write >= 0.03:  # ~30fps update
                    last_write = now
                    # Atomic write
                    tmp_out = OUTPUT_FILE + ".tmp"
                    with open(tmp_out, "w") as f:
                        json.dump(bars, f)
                    os.replace(tmp_out, OUTPUT_FILE)
        except Exception:
            pass

if __name__ == "__main__":
    main()
