#!/usr/bin/env python3
import sys
import json
import subprocess

def get_hypr_data():
    try:
        cursor = json.loads(subprocess.check_output(['hyprctl', 'cursorpos', '-j'], stderr=subprocess.DEVNULL))
        monitors = json.loads(subprocess.check_output(['hyprctl', 'monitors', '-j'], stderr=subprocess.DEVNULL))
        clients = json.loads(subprocess.check_output(['hyprctl', 'clients', '-j'], stderr=subprocess.DEVNULL))
        active_win = json.loads(subprocess.check_output(['hyprctl', 'activewindow', '-j'], stderr=subprocess.DEVNULL))
        return cursor, monitors, clients, active_win
    except Exception as e:
        print(f"Error fetching hyprctl data: {e}", file=sys.stderr)
        return {}, [], [], {}

def ensure_special_workspace_hidden(monitors):
    for m in monitors:
        sw = m.get('specialWorkspace', {})
        sw_name = sw.get('name', '')
        if sw.get('id', 0) != 0 and sw_name:
            clean_name = sw_name.replace('special:', '')
            subprocess.run(['hyprctl', 'dispatch', f'hl.dsp.workspace.toggle_special("{clean_name}")'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def get_target_workspace_and_window():
    cursor, monitors, clients, active_win = get_hypr_data()
    ensure_special_workspace_hidden(monitors)

    if not monitors:
        return 1, None, [], clients, monitors

    cx = cursor.get('x', 0)
    cy = cursor.get('y', 0)

    target_mon = None
    for m in monitors:
        mx, my, mw, mh = m.get('x', 0), m.get('y', 0), m.get('width', 1920), m.get('height', 1080)
        if mx <= cx < mx + mw and my <= cy < my + mh:
            target_mon = m
            break

    if not target_mon:
        for m in monitors:
            if m.get('focused'):
                target_mon = m
                break

    if not target_mon and monitors:
        target_mon = monitors[0]

    target_ws_id = target_mon['activeWorkspace']['id']

    # Visible windows on this workspace (not in special)
    ws_clients = [
        c for c in clients
        if c.get('workspace', {}).get('id') == target_ws_id
        and not c.get('workspace', {}).get('name', '').startswith('special')
    ]

    target_win = None
    if active_win and active_win.get('address'):
        for c in ws_clients:
            if c.get('address') == active_win.get('address'):
                target_win = c
                break

    if not target_win and ws_clients:
        # Pick the most recently focused window
        ws_clients.sort(key=lambda c: c.get('focusHistoryID', 999))
        target_win = ws_clients[0]

    return target_ws_id, target_win, ws_clients, clients, monitors

def eval_lua(code):
    try:
        subprocess.run(['hyprctl', 'eval', code], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def notify(title, msg):
    try:
        subprocess.Popen(['notify-send', '-a', 'Hyprland', '-t', '1200', title, msg])
    except Exception:
        pass

def do_minimize():
    ws_id, target_win, ws_clients, clients, monitors = get_target_workspace_and_window()
    if target_win and target_win.get('address'):
        addr = target_win['address']
        title = target_win.get('title', 'Window')
        lua = f'''
        local wins = hl.get_windows()
        for _, w in ipairs(wins) do
            if w.address == "{addr}" then
                hl.dispatch(hl.dsp.focus({{ window = w }}))
                hl.dispatch(hl.dsp.window.move({{ workspace = "special:minimized", silent = true }}))
                break
            end
        end
        '''
        eval_lua(lua)
        notify("Window Minimized", title)
    else:
        notify("No Windows", f"Workspace {ws_id} has no windows to minimize.")

def do_minimize_all():
    ws_id, _, ws_clients, clients, monitors = get_target_workspace_and_window()
    if ws_clients:
        count = len(ws_clients)
        for win in ws_clients:
            addr = win.get('address')
            if addr:
                lua = f'''
                local wins = hl.get_windows()
                for _, w in ipairs(wins) do
                    if w.address == "{addr}" then
                        hl.dispatch(hl.dsp.focus({{ window = w }}))
                        hl.dispatch(hl.dsp.window.move({{ workspace = "special:minimized", silent = true }}))
                        break
                    end
                end
                '''
                eval_lua(lua)
        notify("Desktop Minimized", f"Minimized {count} window(s) on Workspace {ws_id}")
    else:
        notify("No Windows", f"Workspace {ws_id} has no windows to minimize.")

def do_restore_last():
    ws_id, _, _, all_clients, monitors = get_target_workspace_and_window()
    minimized_clients = [
        c for c in all_clients
        if c.get('workspace', {}).get('name', '') == 'special:minimized'
    ]

    if minimized_clients:
        last_win = minimized_clients[-1]
        addr = last_win['address']
        title = last_win.get('title', 'Window')
        lua = f'''
        local wins = hl.get_windows()
        for _, w in ipairs(wins) do
            if w.address == "{addr}" then
                hl.dispatch(hl.dsp.focus({{ window = w }}))
                hl.dispatch(hl.dsp.window.move({{ workspace = {ws_id} }}))
                break
            end
        end
        '''
        eval_lua(lua)
        notify("Window Restored", f"Restored '{title}' to Workspace {ws_id}")
    else:
        subprocess.Popen(['/home/gallo/.config/hypr/scripts/window-switch.sh'])

def do_restore_all():
    ws_id, _, _, all_clients, monitors = get_target_workspace_and_window()
    minimized_clients = [
        c for c in all_clients
        if c.get('workspace', {}).get('name', '') == 'special:minimized'
    ]
    if minimized_clients:
        for win in minimized_clients:
            addr = win.get('address')
            if addr:
                lua = f'''
                local wins = hl.get_windows()
                for _, w in ipairs(wins) do
                    if w.address == "{addr}" then
                        hl.dispatch(hl.dsp.focus({{ window = w }}))
                        hl.dispatch(hl.dsp.window.move({{ workspace = {ws_id} }}))
                        break
                    end
                end
                '''
                eval_lua(lua)
        notify("Restored All", f"Restored {len(minimized_clients)} window(s) to Workspace {ws_id}")

def do_toggle_all():
    ws_id, _, ws_clients, all_clients, monitors = get_target_workspace_and_window()
    if ws_clients:
        do_minimize_all()
    else:
        do_restore_all()

def do_toggle():
    ws_id, target_win, ws_clients, all_clients, monitors = get_target_workspace_and_window()
    if ws_clients:
        do_minimize()
    else:
        do_restore_last()

def do_maximize_toggle():
    ensure_special_workspace_hidden(get_hypr_data()[1])
    eval_lua('hl.dispatch(hl.dsp.window.fullscreen({ mode = 1 }))')

def do_close():
    ws_id, target_win, ws_clients, _, monitors = get_target_workspace_and_window()
    if target_win and target_win.get('address'):
        addr = target_win['address']
        eval_lua(f'''
        local wins = hl.get_windows()
        for _, w in ipairs(wins) do
            if w.address == "{addr}" then
                hl.dispatch(hl.dsp.focus({{ window = w }}))
                hl.dispatch(hl.dsp.window.close())
                break
            end
        end
        ''')

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "minimize"

    if action == "minimize":
        do_minimize()
    elif action in ("minimize-all", "minimize_all"):
        do_minimize_all()
    elif action in ("toggle-all", "toggle_all"):
        do_toggle_all()
    elif action in ("restore-last", "restore_last"):
        do_restore_last()
    elif action in ("restore-all", "restore_all"):
        do_restore_all()
    elif action == "toggle":
        do_toggle()
    elif action in ("maximize", "maximize-toggle"):
        do_maximize_toggle()
    elif action == "close-window":
        do_close()
    elif action == "menu":
        subprocess.Popen(['/home/gallo/.config/hypr/scripts/minimized-manager.py'])
    else:
        do_minimize()

if __name__ == "__main__":
    main()
