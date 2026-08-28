import Quickshell
import Quickshell.Wayland
import Quickshell.Widgets
import Quickshell.Io
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

ShellRoot {
    id: root

    // ========================================================
    // DYNAMIC WALLUST / GARCHY PALETTE
    // ========================================================
    property color colBg: "#0a0f1dE6"
    property color colBgAlt: "#131c31"
    property color colFg: "#e2e8f0"
    property color colFgMuted: "#94a3b8"
    property color colAccent: "#38bdf8"
    property color colAccentAlt: "#3b82f6"
    property color colBorder: "#1e293b"
    property color colGold: "#fbbf24"
    property color colRed: "#ef4444"
    property color colGreen: "#22c55e"

    FileView {
        path: "/home/gallo/.cache/garchy_theme.json"
        watchChanges: true
        onFileChanged: {
            try {
                var json = JSON.parse(text());
                if (json.bg) root.colBg = json.bg + "E6";
                if (json.bg_alt) root.colBgAlt = json.bg_alt;
                if (json.fg) root.colFg = json.fg;
                if (json.fg_muted) root.colFgMuted = json.fg_muted;
                if (json.accent) root.colAccent = json.accent;
                if (json.accent_alt) root.colAccentAlt = json.accent_alt;
                if (json.border) root.colBorder = json.border;
                if (json.gold) root.colGold = json.gold;
            } catch(e) {}
        }
    }

    // ========================================================
    // HYPRLAND REAL-TIME WINDOW STATE
    // ========================================================
    property var taskbarState: ({ groups: [], active_addr: "", monitors: [] })

    Process {
        id: taskbarProc
        command: ["python3", "/home/gallo/.config/quickshell/garchy-bar/taskbar_service.py"]
        running: true
        stdout: SplitParser {
            onRead: data => {
                try {
                    var parsed = JSON.parse(data.trim());
                    if (parsed && parsed.groups !== undefined) {
                        root.taskbarState = parsed;
                    }
                } catch(e) {}
            }
        }
    }

    function dispatchAction(action, addr) {
        cmdProc.exec(["python3", "/home/gallo/.config/quickshell/garchy-bar/taskbar_service.py", action, addr || ""]);
    }

    function runCmd(cmdList) {
        cmdProc.exec(cmdList);
    }

    Process {
        id: cmdProc
        function exec(args) {
            command = args;
            running = true;
        }
    }

    // ========================================================
    // SYSTEM TELEMETRY (CPU, RAM, AUDIO, TIME)
    // ========================================================
    property string timeStr: "00:00"
    property string dateStr: "Mon, 1 Jan"
    property int cpuPercent: 0
    property int ramPercent: 0
    property int volPercent: 50
    property bool isMuted: false

    Timer {
        interval: 1000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: {
            var now = new Date();
            var hours = String(now.getHours()).padStart(2, '0');
            var mins = String(now.getMinutes()).padStart(2, '0');
            root.timeStr = hours + ":" + mins;

            var days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
            var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
            root.dateStr = days[now.getDay()] + ", " + now.getDate() + " " + months[now.getMonth()];
        }
    }

    Process {
        id: statsProc
        command: ["bash", "-c", "echo $(grep 'cpu ' /proc/stat | awk '{u=$2+$4; t=$2+$4+$5; print int(u*100/t)}') $(free | grep Mem | awk '{print int($3*100/$2)}') $(wpctl get-volume @DEFAULT_AUDIO_SINK@ | awk '{print int($2*100), ($3==\"[MUTED]\"?1:0)}' 2>/dev/null || echo '50 0')"]
        running: false
        stdout: SplitParser {
            onRead: data => {
                var p = data.trim().split(" ");
                if (p.length >= 2) {
                    root.cpuPercent = parseInt(p[0]) || 0;
                    root.ramPercent = parseInt(p[1]) || 0;
                }
                if (p.length >= 4) {
                    root.volPercent = parseInt(p[2]) || 50;
                    root.isMuted = (p[3] === "1");
                }
            }
        }
    }

    Timer {
        interval: 2000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: statsProc.running = true
    }

    // ========================================================
    // PRIMARY SCREEN (DP-2) - 3 FLOATING ISLANDS
    // ========================================================
    PanelWindow {
        id: winMain
        screen: {
            for (var i = 0; i < Quickshell.screens.length; i++) {
                if (Quickshell.screens[i].name === "DP-2") return Quickshell.screens[i];
            }
            return Quickshell.screens[0];
        }

        anchors {
            top: true
            left: true
            right: true
        }
        implicitHeight: 44
        color: "transparent"

        WlrLayershell.layer: WlrLayer.Top
        WlrLayershell.namespace: "garchy-shell"
        WlrLayershell.keyboardFocus: WlrKeyboardFocus.None
        exclusionMode: ExclusionMode.Auto

        Item {
            anchors.fill: parent
            anchors.topMargin: 4
            anchors.leftMargin: 8
            anchors.rightMargin: 8
            anchors.bottomMargin: 2

            // 1. LEFT ISLAND: Launcher, Workspaces 1-4, Windows 11 Taskbar
            Rectangle {
                id: leftIsland
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: leftLayout.implicitWidth + 16
                color: root.colBg
                border.color: root.colBorder
                border.width: 1
                radius: 10

                RowLayout {
                    id: leftLayout
                    anchors.centerIn: parent
                    spacing: 8

                    // 🌌 Launcher Button
                    Rectangle {
                        width: 30
                        height: 30
                        radius: 8
                        color: launchArea.containsMouse ? root.colBgAlt : "transparent"
                        border.color: launchArea.containsMouse ? root.colAccent : "transparent"
                        border.width: 1

                        Text {
                            anchors.centerIn: parent
                            text: "󰣇"
                            font.pixelSize: 18
                            color: launchArea.containsMouse ? root.colAccent : root.colFg
                        }

                        MouseArea {
                            id: launchArea
                            anchors.fill: parent
                            hoverEnabled: true
                            acceptedButtons: Qt.LeftButton | Qt.RightButton
                            onClicked: mouse => {
                                if (mouse.button === Qt.LeftButton) {
                                    root.runCmd(["bash", "-c", "~/.config/hypr/scripts/launchpad.sh"]);
                                } else {
                                    root.runCmd(["bash", "-c", "~/.config/hypr/scripts/wallpaper-select.sh"]);
                                }
                            }
                        }
                    }

                    // 🔢 Workspaces (1 2 3 4)
                    Rectangle {
                        height: 28
                        width: wsRow.implicitWidth + 8
                        radius: 6
                        color: root.colBgAlt
                        border.color: root.colBorder
                        border.width: 1

                        Row {
                            id: wsRow
                            anchors.centerIn: parent
                            spacing: 2

                            Repeater {
                                model: [1, 2, 3, 4]
                                Rectangle {
                                    property int wsNum: modelData
                                    property bool isWsActive: {
                                        var mons = root.taskbarState.monitors || [];
                                        for (var i = 0; i < mons.length; i++) {
                                            if (mons[i].name === "DP-2") {
                                                var actId = mons[i].activeWorkspace ? mons[i].activeWorkspace.id : 1;
                                                return (Math.ceil(actId / 2) === wsNum) || (actId === wsNum);
                                            }
                                        }
                                        return wsNum === 1;
                                    }

                                    width: 22
                                    height: 22
                                    radius: 5
                                    color: isWsActive ? root.colAccent : (wsArea.containsMouse ? root.colBorder : "transparent")

                                    Text {
                                        anchors.centerIn: parent
                                        text: modelData
                                        font.pixelSize: 11
                                        font.bold: true
                                        color: isWsActive ? "#0a0f1d" : root.colFgMuted
                                    }

                                    MouseArea {
                                        id: wsArea
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        onClicked: root.runCmd(["bash", "-c", "~/.config/hypr/scripts/dual-desktop.sh switch " + modelData])
                                    }
                                }
                            }
                        }
                    }

                    // 🗔 WINDOWS 11 / KDE INTERACTIVE TASKBAR
                    Row {
                        id: taskbarRow
                        spacing: 6

                        Repeater {
                            model: root.taskbarState.groups || []

                            Item {
                                property var groupData: modelData
                                width: 36
                                height: 30

                                Rectangle {
                                    id: appPill
                                    anchors.fill: parent
                                    radius: 8
                                    color: groupData.is_active ? root.colAccent + "33" : (appMouse.containsMouse ? root.colBgAlt : "transparent")
                                    border.color: groupData.is_active ? root.colAccent : (appMouse.containsMouse ? root.colBorder : "transparent")
                                    border.width: groupData.is_active ? 1.5 : 1

                                    // App Desktop Icon
                                    Image {
                                        id: appIcon
                                        anchors.centerIn: parent
                                        width: 20
                                        height: 20
                                        source: Quickshell.iconPath(groupData.icon)
                                        fillMode: Image.PreserveAspectFit
                                        opacity: groupData.is_minimized ? 0.5 : 1.0
                                        visible: status === Image.Ready
                                    }

                                    Text {
                                        anchors.centerIn: parent
                                        visible: appIcon.status !== Image.Ready
                                        text: "󰖯"
                                        font.pixelSize: 16
                                        color: groupData.is_active ? root.colAccent : root.colFg
                                    }

                                    // Active underline indicator
                                    Rectangle {
                                        anchors.bottom: parent.bottom
                                        anchors.horizontalCenter: parent.horizontalCenter
                                        anchors.bottomMargin: 2
                                        width: groupData.is_active ? 16 : 4
                                        height: 2
                                        radius: 1
                                        color: groupData.is_active ? root.colAccent : (groupData.is_minimized ? root.colGold : root.colFgMuted)
                                        Behavior on width { NumberAnimation { duration: 150 } }
                                    }

                                    // Multi-window count badge (e.g. 2, 3)
                                    Rectangle {
                                        visible: groupData.count > 1
                                        anchors.top: parent.top
                                        anchors.right: parent.right
                                        anchors.topMargin: 2
                                        anchors.rightMargin: 2
                                        width: 13
                                        height: 13
                                        radius: 6.5
                                        color: root.colAccentAlt

                                        Text {
                                            anchors.centerIn: parent
                                            text: groupData.count
                                            font.pixelSize: 8
                                            font.bold: true
                                            color: "#ffffff"
                                        }
                                    }

                                    MouseArea {
                                        id: appMouse
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        acceptedButtons: Qt.LeftButton | Qt.RightButton | Qt.MiddleButton

                                        onClicked: mouse => {
                                            if (groupData.windows.length === 1) {
                                                var addr = groupData.windows[0].address;
                                                if (mouse.button === Qt.LeftButton) {
                                                    root.dispatchAction("toggle", addr);
                                                } else if (mouse.button === Qt.MiddleButton) {
                                                    root.dispatchAction("close", addr);
                                                }
                                            } else {
                                                // If multiple instances, toggle focus of latest or minimize all
                                                if (mouse.button === Qt.LeftButton) {
                                                    var act = groupData.windows.find(w => w.is_active);
                                                    if (act) {
                                                        root.dispatchAction("toggle", act.address);
                                                    } else {
                                                        root.dispatchAction("focus", groupData.windows[0].address);
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // 2. CENTER ISLAND: Clock & Calendar
            Rectangle {
                id: centerIsland
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: centerLayout.implicitWidth + 24
                color: root.colBg
                border.color: root.colBorder
                border.width: 1
                radius: 10

                RowLayout {
                    id: centerLayout
                    anchors.centerIn: parent
                    spacing: 8

                    Text {
                        text: " " + root.timeStr
                        font.pixelSize: 12
                        font.bold: true
                        color: root.colFg
                    }

                    Rectangle {
                        width: 1
                        height: 14
                        color: root.colBorder
                    }

                    Text {
                        text: " " + root.dateStr
                        font.pixelSize: 11
                        color: root.colFgMuted
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: root.runCmd(["gnome-calendar"])
                }
            }

            // 3. RIGHT ISLAND: Gally AI, Theme, Volume, Telemetry, Power
            Rectangle {
                id: rightIsland
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: rightLayout.implicitWidth + 20
                color: root.colBg
                border.color: root.colBorder
                border.width: 1
                radius: 10

                RowLayout {
                    id: rightLayout
                    anchors.centerIn: parent
                    spacing: 10

                    // 🧠 Gally AI Hub
                    Rectangle {
                        width: 26
                        height: 26
                        radius: 6
                        color: aiMouse.containsMouse ? root.colAccent + "33" : "transparent"

                        Text {
                            anchors.centerIn: parent
                            text: "󰚩"
                            font.pixelSize: 14
                            color: root.colAccent
                        }

                        MouseArea {
                            id: aiMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: root.runCmd(["bash", "-c", "python3 ~/.config/hypr/scripts/gally-ai-hud.py"])
                        }
                    }

                    // 🎨 Wallust Theme Switcher
                    Rectangle {
                        width: 26
                        height: 26
                        radius: 6
                        color: thmMouse.containsMouse ? root.colAccentAlt + "33" : "transparent"

                        Text {
                            anchors.centerIn: parent
                            text: "󰏘"
                            font.pixelSize: 14
                            color: root.colAccentAlt
                        }

                        MouseArea {
                            id: thmMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: root.runCmd(["bash", "-c", "python3 ~/.config/hypr/scripts/theme-switcher-gui.py"])
                        }
                    }

                    // 🔊 Volume Pill
                    Rectangle {
                        height: 24
                        width: volRow.implicitWidth + 12
                        radius: 6
                        color: root.colBgAlt

                        RowLayout {
                            id: volRow
                            anchors.centerIn: parent
                            spacing: 4

                            Text {
                                text: root.isMuted ? "󰝟" : (root.volPercent > 50 ? "󰕾" : "󰖀")
                                font.pixelSize: 12
                                color: root.isMuted ? root.colRed : root.colAccent
                            }

                            Text {
                                text: root.volPercent + "%"
                                font.pixelSize: 11
                                font.bold: true
                                color: root.colFg
                            }
                        }

                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: root.runCmd(["pavucontrol"])
                        }
                    }

                    // ⚡ CPU / RAM Telemetry
                    Rectangle {
                        height: 24
                        width: statRow.implicitWidth + 12
                        radius: 6
                        color: root.colBgAlt

                        RowLayout {
                            id: statRow
                            anchors.centerIn: parent
                            spacing: 6

                            Text {
                                text: " " + root.cpuPercent + "%"
                                font.pixelSize: 10
                                color: root.cpuPercent > 80 ? root.colRed : root.colFgMuted
                            }

                            Text {
                                text: " " + root.ramPercent + "%"
                                font.pixelSize: 10
                                color: root.ramPercent > 85 ? root.colGold : root.colFgMuted
                            }
                        }
                    }

                    // ⏻ Power Menu Button
                    Rectangle {
                        width: 26
                        height: 26
                        radius: 6
                        color: pwrMouse.containsMouse ? root.colRed + "33" : "transparent"

                        Text {
                            anchors.centerIn: parent
                            text: ""
                            font.pixelSize: 13
                            color: pwrMouse.containsMouse ? root.colRed : root.colFgMuted
                        }

                        MouseArea {
                            id: pwrMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: root.runCmd(["wlogout", "-b", "2", "-c", "20", "-r", "20"])
                        }
                    }
                }
            }
        }
    }

    // ========================================================
    // SECONDARY SCREEN (DP-1) - COMPANION STATUS BAR
    // ========================================================
    PanelWindow {
        id: winSec
        screen: {
            for (var i = 0; i < Quickshell.screens.length; i++) {
                if (Quickshell.screens[i].name === "DP-1") return Quickshell.screens[i];
            }
            return Quickshell.screens[0];
        }

        anchors {
            top: true
            left: true
            right: true
        }
        implicitHeight: 44
        color: "transparent"

        WlrLayershell.layer: WlrLayer.Top
        WlrLayershell.namespace: "garchy-shell"
        WlrLayershell.keyboardFocus: WlrKeyboardFocus.None
        exclusionMode: ExclusionMode.Auto

        Item {
            anchors.fill: parent
            anchors.topMargin: 4
            anchors.leftMargin: 8
            anchors.rightMargin: 8
            anchors.bottomMargin: 2

            // Left: Workspaces for Right Screen
            Rectangle {
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: secWsRow.implicitWidth + 16
                color: root.colBg
                border.color: root.colBorder
                border.width: 1
                radius: 10

                Row {
                    id: secWsRow
                    anchors.centerIn: parent
                    spacing: 4

                    Repeater {
                        model: [1, 2, 3, 4]
                        Rectangle {
                            property int wsNum: modelData
                            property bool isWsActive: {
                                var mons = root.taskbarState.monitors || [];
                                for (var i = 0; i < mons.length; i++) {
                                    if (mons[i].name === "DP-1") {
                                        var actId = mons[i].activeWorkspace ? mons[i].activeWorkspace.id : 2;
                                        return (Math.ceil(actId / 2) === wsNum) || (actId === wsNum);
                                    }
                                }
                                return wsNum === 1;
                            }

                            width: 24
                            height: 24
                            radius: 5
                            color: isWsActive ? root.colAccentAlt : "transparent"

                            Text {
                                anchors.centerIn: parent
                                text: modelData
                                font.pixelSize: 11
                                font.bold: true
                                color: isWsActive ? "#ffffff" : root.colFgMuted
                            }

                            MouseArea {
                                anchors.fill: parent
                                onClicked: root.runCmd(["bash", "-c", "~/.config/hypr/scripts/dual-desktop.sh switch " + modelData])
                            }
                        }
                    }
                }
            }

            // Center: Time
            Rectangle {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: 120
                color: root.colBg
                border.color: root.colBorder
                border.width: 1
                radius: 10

                Text {
                    anchors.centerIn: parent
                    text: " " + root.timeStr
                    font.pixelSize: 12
                    font.bold: true
                    color: root.colFg
                }
            }
        }
    }
}
