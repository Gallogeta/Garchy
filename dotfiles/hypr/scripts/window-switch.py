#!/usr/bin/env python3
import sys
import json
import subprocess
import os

ICON_MAP = {
    "brave-browser": "brave-browser",
    "Brave-browser": "brave-browser",
    "code-oss": "code",
    "code": "code",
    "Code": "code",
    "codium": "vscodium",
    "kitty": "kitty",
    "firefox": "firefox",
    "steam": "steam",
    "heroic": "heroic",
    "kdenlive": "kdenlive",
    "thunar": "system-file-manager",
    "Thunar": "system-file-manager",
    "easyeffects": "easyeffects",
    "com.github.wwmm.easyeffects": "easyeffects",
    "org.gnome.Nautilus": "org.gnome.Nautilus",
    "pavucontrol": "multimedia-volume-control",
    "org.pulseaudio.pavucontrol": "multimedia-volume-control",
    "discord": "discord",
    "Spotify": "spotify",
    "obsidian": "obsidian"
}

def notify(title, msg):
    try:
        subprocess.Popen(['notify-send', '-a', 'Hyprland', '-t', '1500', title, msg])
    except Exception:
        pass

def get_clients():
    try:
        output = subprocess.check_output(['hyprctl', 'clients', '-j'], stderr=subprocess.DEVNULL)
        return json.loads(output)
    except Exception:
        return []

def main():
    clients = get_clients()
    if not clients:
        notify("Windows", "No open windows found")
        sys.exit(0)

    # Sort clients: visible first, then minimized
    clients.sort(key=lambda c: (1 if c.get('workspace', {}).get('name', '').startswith('special') else 0,
                                c.get('focusHistoryID', 999)))

    entries = []
    rofi_lines = []

    for c in clients:
        addr = c.get('address', '')
        if not addr:
            continue

        c_class = c.get('class', 'Unknown')
        title = c.get('title', 'Untitled')
        ws_name = c.get('workspace', {}).get('name', '')
        ws_id = c.get('workspace', {}).get('id', 1)

        icon = ICON_MAP.get(c_class, c_class.lower())

        if ws_name.startswith('special'):
            ws_badge = "󰖯 [Minimized]"
        else:
            ws_badge = f"󰍹 [WS {ws_id}]"

        # 1. Switch / Open Entry
        display_switch = f"{ws_badge}  ·  {c_class}  ·  {title}"
        entries.append({
            'action': 'switch',
            'address': addr,
            'title': title,
            'ws_name': ws_name
        })
        rofi_lines.append(f"{display_switch}\0icon\x1f{icon}")

        # 2. Close Entry
        display_close = f"󰅖  ✕ [Close Window]  ·  {c_class}  ·  {title}"
        entries.append({
            'action': 'close',
            'address': addr,
            'title': title,
            'ws_name': ws_name
        })
        rofi_lines.append(f"{display_close}\0icon\x1fprocess-stop")

    rofi_input = "\n".join(rofi_lines)

    rofi_cmd = [
        "rofi",
        "-dmenu",
        "-i",
        "-format", "i",
        "-p", "󰖯 Windows (Enter: Select | Alt+x / Shift+Del: ✕ Close)",
        "-kb-delete-entry", "",
        "-kb-custom-1", "Alt+x,Alt+c,Shift+Delete",
        "-config", os.path.expanduser("~/.config/rofi/window.rasi")
    ]

    proc = subprocess.Popen(rofi_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, _ = proc.communicate(input=rofi_input)
    exit_code = proc.returncode

    selected_str = stdout.strip()
    if not selected_str.isdigit():
        sys.exit(0)

    selected_idx = int(selected_str)
    if selected_idx < 0 or selected_idx >= len(entries):
        sys.exit(0)

    target = entries[selected_idx]
    target_addr = target['address']
    target_title = target['title']
    target_ws = target['ws_name']

    # If user pressed Alt+X / Shift+Del (exit code 10) OR clicked the Close entry:
    if exit_code == 10 or target['action'] == 'close':
        subprocess.run(['hyprctl', 'eval', f'local w = hl.get_window("{target_addr}"); if w then hl.dispatch(hl.dsp.focus({{ window = w }})); hl.dispatch(hl.dsp.window.close()) end'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        notify("✕ Window Closed", f"Closed '{target_title}' without opening")
        sys.exit(0)

    # Otherwise, switch / open the window
    if exit_code == 0 and target['action'] == 'switch':
        try:
            active_ws_out = subprocess.check_output(['hyprctl', 'activeworkspace', '-j'], stderr=subprocess.DEVNULL)
            active_ws_id = json.loads(active_ws_out).get('id', 1)
        except Exception:
            active_ws_id = 1

        if target_ws.startswith('special'):
            subprocess.run(['hyprctl', 'eval', f'local w = hl.get_window("{target_addr}"); if w then hl.dispatch(hl.dsp.focus({{ window = w }})); hl.dispatch(hl.dsp.window.move({{ workspace = {active_ws_id} }})) end'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        subprocess.run(['hyprctl', 'eval', f'local w = hl.get_window("{target_addr}"); if w then hl.dispatch(hl.dsp.focus({{ window = w }})) end'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    main()
