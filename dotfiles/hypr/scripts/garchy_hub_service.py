#!/usr/bin/env python3
"""
==============================================================================
🌌 Garchy OS — Unified Hub State & Hardware Accelerator Service
==============================================================================
"""

import os
import sys
import json
import time
import subprocess
import threading

OUTPUT_FILE = "/tmp/garchy_hub_state.json"
GAMEMODE_STATE_FILE = "/tmp/garchy_gamemode.state"

state = {
    "media": {
        "available": False,
        "player": "",
        "status": "Stopped",
        "title": "No Media",
        "artist": "Offline",
        "album": "",
        "art_url": "",
        "position": 0,
        "length": 0,
        "position_str": "0:00",
        "length_str": "0:00",
        "progress": 0.0
    },
    "network": {
        "connected": True,
        "type": "ethernet",
        "name": "Wired",
        "icon": "󰈀"
    },
    "bluetooth": {
        "powered": False,
        "connected_device": "",
        "icon": "󰂲"
    },
    "audio": {
        "volume": 50,
        "muted": False,
        "mic_volume": 100,
        "mic_muted": False,
        "default_sink": "",
        "sinks": []
    },
    "toggles": {
        "night_light": False,
        "gamemode": False,
        "dnd": False
    },
    "weather": {
        "temp": "+17°C",
        "condition": "Overcast",
        "icon": "🌤️",
        "display": "🌤️ +17°C"
    }
}

def format_time(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins}:{secs:02d}"

last_media = {
    "title": "No Media",
    "artist": "Offline",
    "album": "",
    "art_url": "",
    "player": "",
    "status": "Stopped"
}

def update_media():
    global last_media
    try:
        # Check running players
        players_out = ""
        try:
            players_out = subprocess.check_output(["playerctl", "-l"], text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            pass
        has_players = bool(players_out)

        status = "Stopped"
        try:
            status_out = subprocess.check_output(["playerctl", "status"], text=True, stderr=subprocess.DEVNULL).strip()
            status = status_out.split("\n")[0] if status_out else ("Paused" if has_players else "Stopped")
        except Exception:
            status = "Paused" if has_players else "Stopped"

        meta_out = ""
        try:
            meta_out = subprocess.check_output(
                ["playerctl", "metadata", "--format", "{{playerName}}|||{{title}}|||{{artist}}|||{{album}}|||{{mpris:artUrl}}|||{{mpris:length}}"],
                text=True, stderr=subprocess.DEVNULL
            ).strip()
        except Exception:
            pass

        meta = meta_out.split("|||") if meta_out else []
        player = meta[0] if len(meta) > 0 and meta[0] else last_media["player"]
        title = meta[1] if len(meta) > 1 and meta[1] else last_media["title"]
        artist = meta[2] if len(meta) > 2 and meta[2] else last_media["artist"]
        album = meta[3] if len(meta) > 3 and meta[3] else last_media["album"]
        art_url = meta[4] if len(meta) > 4 and meta[4] else last_media["art_url"]

        if title and title != "No Media":
            last_media = {
                "title": title,
                "artist": artist,
                "album": album,
                "art_url": art_url,
                "player": player,
                "status": status
            }

        len_us = 0
        try:
            if len(meta) > 5 and meta[5].strip().isdigit():
                len_us = float(meta[5].strip())
        except Exception:
            pass

        pos_sec = 0
        try:
            pos_out = subprocess.check_output(["playerctl", "position"], text=True, stderr=subprocess.DEVNULL).strip()
            if pos_out:
                pos_sec = float(pos_out)
        except Exception:
            pass

        len_sec = len_us / 1000000.0 if len_us > 0 else 0
        progress = (pos_sec / len_sec) if len_sec > 0 else 0.0

        is_avail = bool(has_players or (status in ("Playing", "Paused")) or (title and title != "No Media"))

        state["media"] = {
            "available": is_avail,
            "player": player or "MPRIS",
            "status": status,
            "title": title or "No Media",
            "artist": artist or "Offline",
            "album": album,
            "art_url": art_url,
            "position": int(pos_sec),
            "length": int(len_sec),
            "position_str": format_time(pos_sec),
            "length_str": format_time(len_sec),
            "progress": min(1.0, max(0.0, progress))
        }
    except Exception:
        state["media"]["status"] = "Paused" if (last_media["title"] != "No Media") else "Stopped"
        state["media"]["available"] = (last_media["title"] != "No Media")
        state["media"]["title"] = last_media["title"]
        state["media"]["artist"] = last_media["artist"]

def update_audio():
    try:
        vol_out = subprocess.check_output(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"], text=True, stderr=subprocess.DEVNULL).strip()
        parts = vol_out.split()
        vol = int(float(parts[1]) * 100) if len(parts) > 1 else 50
        muted = "[MUTED]" in vol_out

        mic_out = subprocess.check_output(["wpctl", "get-volume", "@DEFAULT_AUDIO_SOURCE@"], text=True, stderr=subprocess.DEVNULL).strip()
        mic_parts = mic_out.split()
        mic_vol = int(float(mic_parts[1]) * 100) if len(mic_parts) > 1 else 100
        mic_muted = "[MUTED]" in mic_out

        sinks_raw = subprocess.check_output(["pactl", "list", "sinks", "short"], text=True, stderr=subprocess.DEVNULL).strip().split("\n")
        def_sink = subprocess.check_output(["pactl", "get-default-sink"], text=True, stderr=subprocess.DEVNULL).strip()

        sinks = []
        for line in sinks_raw:
            if not line.strip(): continue
            cols = line.split()
            if len(cols) >= 2:
                s_id = cols[0]
                s_name = cols[1]
                s_desc = "USB Headset / Audio" if "usb" in s_name.lower() else ("Digital / HDMI Audio" if "iec958" in s_name.lower() or "hdmi" in s_name.lower() else "Analog Speakers")
                sinks.append({
                    "id": s_id,
                    "name": s_name,
                    "desc": s_desc,
                    "is_default": (s_name == def_sink)
                })

        state["audio"] = {
            "volume": vol,
            "muted": muted,
            "mic_volume": mic_vol,
            "mic_muted": mic_muted,
            "default_sink": def_sink,
            "sinks": sinks
        }
    except Exception:
        pass

def update_network():
    try:
        out = subprocess.check_output(["nmcli", "-t", "-f", "TYPE,STATE,CONNECTION", "device"], text=True, stderr=subprocess.DEVNULL).strip().split("\n")
        conn_type = "ethernet"
        conn_name = "Wired"
        is_conn = False

        for line in out:
            parts = line.split(":")
            if len(parts) >= 3 and parts[1] == "connected":
                is_conn = True
                conn_type = parts[0]
                conn_name = parts[2]
                break

        state["network"] = {
            "connected": is_conn,
            "type": conn_type,
            "name": conn_name,
            "icon": "󰈀" if conn_type == "ethernet" else ("󰤨" if is_conn else "󰤭")
        }
    except Exception:
        pass

def update_bluetooth():
    try:
        sh = subprocess.check_output(["bluetoothctl", "show"], text=True, stderr=subprocess.DEVNULL)
        powered = "Powered: yes" in sh
        conn = subprocess.check_output(["bluetoothctl", "devices", "Connected"], text=True, stderr=subprocess.DEVNULL).strip()
        dev_name = conn.split(maxsplit=2)[2] if conn and len(conn.split()) >= 3 else ""

        state["bluetooth"] = {
            "powered": powered,
            "connected_device": dev_name,
            "icon": "󰂱" if dev_name else ("󰂯" if powered else "󰂲")
        }
    except Exception:
        pass

def update_toggles():
    try:
        # Check gamemode via state file or active process
        gm_active = os.path.exists(GAMEMODE_STATE_FILE)
        if not gm_active:
            try:
                out = subprocess.check_output(["gamemoded", "-s"], text=True, stderr=subprocess.DEVNULL).strip()
                gm_active = "is active" in out
            except Exception:
                pass
        state["toggles"]["gamemode"] = gm_active

        # Check Night Light (hyprsunset)
        hs_active = subprocess.call(["pgrep", "-x", "hyprsunset"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
        state["toggles"]["night_light"] = hs_active
    except Exception:
        pass

def update_weather():
    while True:
        try:
            w = subprocess.check_output(["curl", "-s", "--max-time", "3", "wttr.in/?format=%c+%t+%C"], text=True).strip()
            if w and "Unknown" not in w and "404" not in w:
                parts = w.split()
                icon = parts[0] if len(parts) > 0 else "🌤️"
                temp = parts[1] if len(parts) > 1 else "+17°C"
                cond = " ".join(parts[2:]) if len(parts) > 2 else "Clear"
                state["weather"] = {
                    "temp": temp,
                    "condition": cond,
                    "icon": icon,
                    "display": f"{icon} {temp} {cond}"
                }
        except Exception:
            pass
        time.sleep(900)

def flush_state():
    tmp = OUTPUT_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f)
    os.replace(tmp, OUTPUT_FILE)

def handle_cli_command(cmd, args):
    if cmd == "toggle-wifi":
        state_curr = subprocess.check_output(["nmcli", "radio", "wifi"], text=True).strip()
        new_s = "off" if state_curr == "enabled" else "on"
        subprocess.run(["nmcli", "radio", "wifi", new_s])
        update_network()
        flush_state()
    elif cmd == "toggle-bt":
        sh = subprocess.check_output(["bluetoothctl", "show"], text=True)
        new_p = "off" if "Powered: yes" in sh else "on"
        subprocess.run(["bluetoothctl", "power", new_p])
        update_bluetooth()
        flush_state()
    elif cmd == "toggle-mic":
        subprocess.run(["wpctl", "set-mute", "@DEFAULT_AUDIO_SOURCE@", "toggle"])
        update_audio()
        flush_state()
    elif cmd == "toggle-nightlight":
        if subprocess.call(["pgrep", "-x", "hyprsunset"], stdout=subprocess.DEVNULL) == 0:
            subprocess.run(["killall", "hyprsunset"])
        else:
            subprocess.Popen(["hyprsunset", "-t", "4200"])
        update_toggles()
        flush_state()
    elif cmd == "toggle-gamemode":
        if os.path.exists(GAMEMODE_STATE_FILE):
            try: os.remove(GAMEMODE_STATE_FILE)
            except Exception: pass
            state["toggles"]["gamemode"] = False
            subprocess.run(["nvidia-settings", "-a", "[gpu:0]/GPUPowerMizerMode=0"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            subprocess.run(["notify-send", "-a", "GameMode", "🎮 GameMode Deactivated", "Balanced Power Profile Restored"], check=False)
        else:
            with open(GAMEMODE_STATE_FILE, "w") as f:
                f.write("active")
            state["toggles"]["gamemode"] = True
            subprocess.run(["nvidia-settings", "-a", "[gpu:0]/GPUPowerMizerMode=1"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            subprocess.run(["notify-send", "-a", "GameMode", "🎮 GameMode Activated", "144Hz Maximum Performance Governor Locked"], check=False)
        flush_state()
    elif cmd == "set-sink" and len(args) > 0:
        subprocess.run(["pactl", "set-default-sink", args[0]])
        update_audio()
        flush_state()
    elif cmd == "media-play-pause":
        subprocess.run(["playerctl", "play-pause"])
        time.sleep(0.05)
        update_media()
        flush_state()
    elif cmd == "media-next":
        subprocess.run(["playerctl", "next"])
        time.sleep(0.05)
        update_media()
        flush_state()
    elif cmd == "media-prev":
        subprocess.run(["playerctl", "previous"])
        time.sleep(0.05)
        update_media()
        flush_state()
    elif cmd == "media-seek" and len(args) > 0:
        subprocess.run(["playerctl", "position", str(args[0])])
        time.sleep(0.05)
        update_media()
        flush_state()
    elif cmd == "vol-up":
        subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "5%+"])
        trigger_osd("volume")
    elif cmd == "vol-down":
        subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "5%-"])
        trigger_osd("volume")
    elif cmd == "vol-mute":
        subprocess.run(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"])
        trigger_osd("volume")

def trigger_osd(osd_type):
    try:
        update_audio()
        osd_data = {
            "type": osd_type,
            "volume": state["audio"]["volume"],
            "muted": state["audio"]["muted"],
            "mic_volume": state["audio"]["mic_volume"],
            "mic_muted": state["audio"]["mic_muted"],
            "timestamp": time.time()
        }
        with open("/tmp/garchy_osd_event.json", "w") as f:
            json.dump(osd_data, f)
    except Exception:
        pass

def update_notifs():
    try:
        out = subprocess.check_output(["dunstctl", "history"], text=True)
        raw = json.loads(out)
        items = []
        if "data" in raw and len(raw["data"]) > 0:
            for n in raw["data"][0][:15]:
                items.append({
                    "id": n.get("id", {}).get("data", 0),
                    "app": n.get("appname", {}).get("data", "System"),
                    "summary": n.get("summary", {}).get("data", ""),
                    "body": n.get("body", {}).get("data", ""),
                    "icon": n.get("icon_path", {}).get("data", "")
                })
        with open("/tmp/garchy_notif_history.json", "w") as f:
            json.dump(items, f)
    except Exception:
        pass

def main_loop():
    t = threading.Thread(target=update_weather, daemon=True)
    t.start()

    while True:
        update_media()
        update_audio()
        update_network()
        update_bluetooth()
        update_toggles()
        update_notifs()
        flush_state()
        time.sleep(0.8)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        handle_cli_command(sys.argv[1], sys.argv[2:])
        sys.exit(0)
    main_loop()
