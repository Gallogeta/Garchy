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
    property var taskbarState: ({ groups: [], minimized_windows: [], active_addr: "", monitors: [] })

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
    // TIME & AUDIO TELEMETRY
    // ========================================================
    property string timeStr: "00:00"
    property string fullDateStr: "Monday, 1 January 2026"
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

            var days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
            var months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
            root.fullDateStr = days[now.getDay()] + ", " + months[now.getMonth()] + " " + now.getDate() + ", " + now.getFullYear();
        }
    }

    Process {
        id: audioProc
        command: ["bash", "-c", "wpctl get-volume @DEFAULT_AUDIO_SINK@ | awk '{print int($2*100), ($3==\"[MUTED]\"?1:0)}' 2>/dev/null || echo '50 0'"]
        running: false
        stdout: SplitParser {
            onRead: data => {
                var p = data.trim().split(" ");
                if (p.length >= 2) {
                    root.volPercent = parseInt(p[0]) || 50;
                    root.isMuted = (p[1] === "1");
                }
            }
        }
    }

    Timer {
        interval: 2000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: audioProc.running = true
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
        implicitHeight: 46
        color: "transparent"

        WlrLayershell.layer: WlrLayer.Top
        WlrLayershell.namespace: "garchy-shell"
        WlrLayershell.keyboardFocus: WlrKeyboardFocus.None
        exclusionMode: ExclusionMode.Auto

        Item {
            anchors.fill: parent
            anchors.topMargin: 4
            anchors.bottomMargin: 4
            anchors.leftMargin: 10
            anchors.rightMargin: 10

            // 1. LEFT ISLAND: Launcher, Workspaces 1-4, Windows 11 Taskbar
            Rectangle {
                id: leftIsland
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: leftLayout.implicitWidth + 20
                color: root.colBg
                border.color: root.colBorder
                border.width: 1
                radius: 12

                RowLayout {
                    id: leftLayout
                    anchors.centerIn: parent
                    spacing: 10

                    // 🌌 Launcher Button
                    Rectangle {
                        width: 32
                        height: 32
                        radius: 9
                        color: launchArea.containsMouse ? root.colBgAlt : "transparent"
                        border.color: launchArea.containsMouse ? root.colAccent : "transparent"
                        border.width: 1

                        Text {
                            anchors.centerIn: parent
                            text: "󰣇"
                            font.pixelSize: 20
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
                        height: 30
                        width: wsRow.implicitWidth + 10
                        radius: 8
                        color: root.colBgAlt
                        border.color: root.colBorder
                        border.width: 1

                        Row {
                            id: wsRow
                            anchors.centerIn: parent
                            spacing: 3

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

                                    width: 24
                                    height: 24
                                    radius: 6
                                    color: isWsActive ? root.colAccent : (wsArea.containsMouse ? root.colBorder : "transparent")

                                    Text {
                                        anchors.centerIn: parent
                                        text: modelData
                                        font.pixelSize: 12
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
                        spacing: 8

                        Repeater {
                            model: root.taskbarState.groups || []

                            Item {
                                property var groupData: modelData
                                width: 38
                                height: 32

                                Rectangle {
                                    id: appPill
                                    anchors.fill: parent
                                    radius: 9
                                    color: groupData.is_active ? root.colAccent + "33" : (appMouse.containsMouse ? root.colBgAlt : "transparent")
                                    border.color: groupData.is_active ? root.colAccent : (appMouse.containsMouse ? root.colBorder : "transparent")
                                    border.width: groupData.is_active ? 1.5 : 1

                                    // App Desktop Icon
                                    Image {
                                        id: appIcon
                                        anchors.centerIn: parent
                                        width: 22
                                        height: 22
                                        source: Quickshell.iconPath(groupData.icon)
                                        fillMode: Image.PreserveAspectFit
                                        opacity: groupData.is_minimized ? 0.5 : 1.0
                                        visible: status === Image.Ready
                                    }

                                    Text {
                                        anchors.centerIn: parent
                                        visible: appIcon.status !== Image.Ready
                                        text: "󰖯"
                                        font.pixelSize: 18
                                        color: groupData.is_active ? root.colAccent : root.colFg
                                    }

                                    // Active underline indicator
                                    Rectangle {
                                        anchors.bottom: parent.bottom
                                        anchors.horizontalCenter: parent.horizontalCenter
                                        anchors.bottomMargin: 2
                                        width: groupData.is_active ? 18 : 4
                                        height: 2.5
                                        radius: 1.5
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
                                        width: 14
                                        height: 14
                                        radius: 7
                                        color: root.colAccentAlt

                                        Text {
                                            anchors.centerIn: parent
                                            text: groupData.count
                                            font.pixelSize: 9
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

            // 2. CENTER ISLAND: Single Digital Clock (Click opens Date & Calendar)
            Rectangle {
                id: centerIsland
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: clockLayout.implicitWidth + 36
                color: root.colBg
                border.color: clockArea.containsMouse ? root.colAccent : root.colBorder
                border.width: 1
                radius: 12

                RowLayout {
                    id: clockLayout
                    anchors.centerIn: parent

                    Text {
                        text: root.timeStr
                        font.pixelSize: 14
                        font.bold: true
                        color: root.colFg
                    }
                }

                MouseArea {
                    id: clockArea
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: datePopup.visible = !datePopup.visible
                }
            }

            // 📅 Center Clock Dropdown: Date & Calendar Menu
            PopupWindow {
                id: datePopup
                anchor.window: winMain
                anchor.rect.x: Math.round((winMain.width - 280) / 2)
                anchor.rect.y: 46
                anchor.rect.width: 280
                anchor.rect.height: 0
                anchor.edges: Edges.Bottom
                anchor.gravity: Edges.Bottom
                implicitWidth: 280
                implicitHeight: dateCol.implicitHeight + 28
                color: "transparent"
                visible: false

                Rectangle {
                    anchors.fill: parent
                    radius: 14
                    color: root.colBg
                    border.color: root.colAccent
                    border.width: 1.5

                    ColumnLayout {
                        id: dateCol
                        anchors.fill: parent
                        anchors.margins: 14
                        spacing: 10

                        // Full Date Header
                        Text {
                            text: root.fullDateStr
                            font.pixelSize: 13
                            font.bold: true
                            color: root.colAccent
                            Layout.alignment: Qt.AlignHCenter
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 1
                            color: root.colBorder
                        }

                        // Open Calendar Button
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 32
                            radius: 8
                            color: calBtnArea.containsMouse ? root.colAccent + "33" : root.colBgAlt
                            border.color: calBtnArea.containsMouse ? root.colAccent : root.colBorder
                            border.width: 1

                            Text {
                                anchors.centerIn: parent
                                text: "Open Full Calendar"
                                font.pixelSize: 12
                                font.bold: true
                                color: root.colFg
                            }

                            MouseArea {
                                id: calBtnArea
                                anchors.fill: parent
                                hoverEnabled: true
                                onClicked: {
                                    root.runCmd(["gnome-calendar"]);
                                    datePopup.visible = false;
                                }
                            }
                        }
                    }
                }
            }

            // 3. RIGHT ISLAND: Volume, Gally AI, Theme, Down Arrow Menu
            Rectangle {
                id: rightIsland
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: rightLayout.implicitWidth + 24
                color: root.colBg
                border.color: root.colBorder
                border.width: 1
                radius: 12

                RowLayout {
                    id: rightLayout
                    anchors.centerIn: parent
                    spacing: 10

                    // 🔊 Volume Pill
                    Rectangle {
                        height: 28
                        width: volRow.implicitWidth + 16
                        radius: 7
                        color: root.colBgAlt

                        RowLayout {
                            id: volRow
                            anchors.centerIn: parent
                            spacing: 6

                            Text {
                                text: root.isMuted ? "󰝟" : (root.volPercent > 50 ? "󰕾" : "󰖀")
                                font.pixelSize: 14
                                color: root.isMuted ? root.colRed : root.colAccent
                            }

                            Text {
                                text: root.volPercent + "%"
                                font.pixelSize: 12
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

                    // 🧠 Gally AI Hub
                    Rectangle {
                        width: 30
                        height: 30
                        radius: 8
                        color: aiMouse.containsMouse ? root.colAccent + "33" : "transparent"

                        Text {
                            anchors.centerIn: parent
                            text: "󰚩"
                            font.pixelSize: 16
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
                        width: 30
                        height: 30
                        radius: 8
                        color: thmMouse.containsMouse ? root.colAccentAlt + "33" : "transparent"

                        Text {
                            anchors.centerIn: parent
                            text: "󰏘"
                            font.pixelSize: 16
                            color: root.colAccentAlt
                        }

                        MouseArea {
                            id: thmMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: root.runCmd(["bash", "-c", "python3 ~/.config/hypr/scripts/theme-switcher-gui.py"])
                        }
                    }

                    // 󰅀 Down Arrow / Minimized Tray Menu
                    Rectangle {
                        id: trayBtn
                        width: 28
                        height: 28
                        radius: 7
                        color: trayArea.containsMouse || trayMenuPopup.visible ? root.colBgAlt : "transparent"
                        border.color: trayArea.containsMouse || trayMenuPopup.visible ? root.colAccent : "transparent"
                        border.width: 1

                        Text {
                            anchors.centerIn: parent
                            text: "󰅀"
                            font.pixelSize: 15
                            color: root.taskbarState.minimized_windows && root.taskbarState.minimized_windows.length > 0 ? root.colGold : root.colFgMuted
                        }

                        MouseArea {
                            id: trayArea
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: trayMenuPopup.visible = !trayMenuPopup.visible
                        }
                    }
                }
            }

            // 🗕 GARCHY SHELL LUXURY OBSIDIAN TRAY & SYSTEM HUB
            PopupWindow {
                id: trayMenuPopup
                anchor.window: winMain
                anchor.rect.x: winMain.width - 364
                anchor.rect.y: 46
                anchor.rect.width: 350
                anchor.rect.height: 0
                anchor.edges: Edges.Bottom
                anchor.gravity: Edges.Bottom
                implicitWidth: 350
                implicitHeight: hubCol.implicitHeight + 28
                color: "transparent"
                visible: false

                Rectangle {
                    anchors.fill: parent
                    radius: 16
                    color: root.colBg
                    border.color: root.colAccent
                    border.width: 1.5

                    ColumnLayout {
                        id: hubCol
                        anchors.fill: parent
                        anchors.margins: 14
                        spacing: 10

                        // 1. TOP HEADER
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            Text {
                                text: "󰣇"
                                font.pixelSize: 18
                                color: root.colAccent
                            }

                            Text {
                                text: "Garchy Shell Hub"
                                font.pixelSize: 13
                                font.bold: true
                                color: root.colFg
                            }

                            Item { Layout.fillWidth: true }

                            // Emerald Active Badge
                            Rectangle {
                                width: statusRow.implicitWidth + 10
                                height: 20
                                radius: 10
                                color: root.colGreen + "22"
                                border.color: root.colGreen
                                border.width: 1

                                RowLayout {
                                    id: statusRow
                                    anchors.centerIn: parent
                                    spacing: 4

                                    Rectangle {
                                        width: 6
                                        height: 6
                                        radius: 3
                                        color: root.colGreen
                                    }

                                    Text {
                                        text: "Active"
                                        font.pixelSize: 10
                                        font.bold: true
                                        color: root.colGreen
                                    }
                                }
                            }

                            // Close Button
                            Rectangle {
                                width: 22
                                height: 22
                                radius: 11
                                color: closeHubMouse.containsMouse ? root.colRed : root.colBgAlt

                                Text {
                                    anchors.centerIn: parent
                                    text: "✕"
                                    font.pixelSize: 10
                                    color: closeHubMouse.containsMouse ? "#ffffff" : root.colFgMuted
                                }

                                MouseArea {
                                    id: closeHubMouse
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    onClicked: trayMenuPopup.visible = false
                                }
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 1
                            color: root.colBorder
                        }

                        // 2. BACKGROUND & TRAY SERVICES SECTION
                        Text {
                            text: "BACKGROUND & TRAY SERVICES"
                            font.pixelSize: 9
                            font.bold: true
                            color: root.colAccent
                            Layout.topMargin: 2
                        }

                        Repeater {
                            model: root.taskbarState.tray_services || []

                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 38
                                radius: 8
                                color: svcMouse.containsMouse ? root.colBgAlt : "#131c3188"
                                border.color: modelData.is_running ? root.colBorder : "transparent"
                                border.width: 1

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: 10
                                    anchors.rightMargin: 10
                                    spacing: 10

                                    // App Desktop Vector Icon
                                    Image {
                                        width: 20
                                        height: 20
                                        source: Quickshell.iconPath(modelData.icon)
                                        fillMode: Image.PreserveAspectFit
                                        opacity: modelData.is_running ? 1.0 : 0.4
                                        visible: status === Image.Ready
                                    }

                                    ColumnLayout {
                                        Layout.fillWidth: true
                                        spacing: 1

                                        Text {
                                            text: modelData.name
                                            font.pixelSize: 12
                                            font.bold: true
                                            color: modelData.is_running ? root.colFg : root.colFgMuted
                                        }

                                        Text {
                                            text: modelData.status_text
                                            font.pixelSize: 10
                                            color: modelData.is_running ? (modelData.is_minimized ? root.colGold : root.colAccent) : root.colFgMuted
                                        }
                                    }

                                    // Action Button (Restore / Open / Launch)
                                    Rectangle {
                                        width: modelData.is_running ? 64 : 54
                                        height: 24
                                        radius: 6
                                        color: actArea.containsMouse ? root.colAccent : root.colBgAlt
                                        border.color: root.colAccent
                                        border.width: 1

                                        Text {
                                            anchors.centerIn: parent
                                            text: modelData.has_window ? (modelData.is_minimized ? "Restore" : "Focus") : (modelData.is_running ? "Open" : "Launch")
                                            font.pixelSize: 10
                                            font.bold: true
                                            color: actArea.containsMouse ? "#0a0f1d" : root.colAccent
                                        }

                                        MouseArea {
                                            id: actArea
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            onClicked: {
                                                if (modelData.has_window) {
                                                    root.dispatchAction("toggle", modelData.address);
                                                } else {
                                                    root.runCmd(["bash", "-c", modelData.cmd]);
                                                }
                                                trayMenuPopup.visible = false;
                                            }
                                        }
                                    }
                                }

                                MouseArea {
                                    id: svcMouse
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    onClicked: {
                                        if (modelData.has_window) {
                                            root.dispatchAction("toggle", modelData.address);
                                        } else {
                                            root.runCmd(["bash", "-c", modelData.cmd]);
                                        }
                                        trayMenuPopup.visible = false;
                                    }
                                }
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 1
                            color: root.colBorder
                            Layout.topMargin: 2
                        }

                        // 3. QUICK SYSTEM SHORTCUTS
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            // 🎮 GameMode
                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 30
                                radius: 6
                                color: gmMouse.containsMouse ? root.colAccent + "33" : root.colBgAlt
                                border.color: root.colBorder
                                border.width: 1

                                RowLayout {
                                    anchors.centerIn: parent
                                    spacing: 4

                                    Text {
                                        text: "🎮"
                                        font.pixelSize: 11
                                    }

                                    Text {
                                        text: "Gaming"
                                        font.pixelSize: 10
                                        font.bold: true
                                        color: root.colFg
                                    }
                                }

                                MouseArea {
                                    id: gmMouse
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    onClicked: {
                                        root.runCmd(["bash", "-c", "garchy-game status"]);
                                        trayMenuPopup.visible = false;
                                    }
                                }
                            }

                            // 🔊 Pavucontrol
                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 30
                                radius: 6
                                color: pavuMouse.containsMouse ? root.colAccent + "33" : root.colBgAlt
                                border.color: root.colBorder
                                border.width: 1

                                RowLayout {
                                    anchors.centerIn: parent
                                    spacing: 4

                                    Text {
                                        text: "󰕾"
                                        font.pixelSize: 11
                                        color: root.colAccent
                                    }

                                    Text {
                                        text: "Mixer"
                                        font.pixelSize: 10
                                        font.bold: true
                                        color: root.colFg
                                    }
                                }

                                MouseArea {
                                    id: pavuMouse
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    onClicked: {
                                        root.runCmd(["pavucontrol"]);
                                        trayMenuPopup.visible = false;
                                    }
                                }
                            }

                            // 🎨 Themes
                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 30
                                radius: 6
                                color: thmQMouse.containsMouse ? root.colAccentAlt + "33" : root.colBgAlt
                                border.color: root.colBorder
                                border.width: 1

                                RowLayout {
                                    anchors.centerIn: parent
                                    spacing: 4

                                    Text {
                                        text: "󰏘"
                                        font.pixelSize: 11
                                        color: root.colAccentAlt
                                    }

                                    Text {
                                        text: "Theme"
                                        font.pixelSize: 10
                                        font.bold: true
                                        color: root.colFg
                                    }
                                }

                                MouseArea {
                                    id: thmQMouse
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    onClicked: {
                                        root.runCmd(["bash", "-c", "python3 ~/.config/hypr/scripts/theme-switcher-gui.py"]);
                                        trayMenuPopup.visible = false;
                                    }
                                }
                            }
                        }

                        // 4. POWER & SESSION BAR
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 32
                            radius: 8
                            color: root.colBgAlt
                            border.color: root.colBorder
                            border.width: 1

                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: 8
                                anchors.rightMargin: 8

                                // Lock
                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    radius: 6
                                    color: lckMouse.containsMouse ? root.colAccent + "33" : "transparent"

                                    Text {
                                        anchors.centerIn: parent
                                        text: " Lock"
                                        font.pixelSize: 10
                                        font.bold: true
                                        color: root.colFg
                                    }

                                    MouseArea {
                                        id: lckMouse
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        onClicked: {
                                            root.runCmd(["hyprlock"]);
                                            trayMenuPopup.visible = false;
                                        }
                                    }
                                }

                                Rectangle {
                                    width: 1
                                    height: 16
                                    color: root.colBorder
                                }

                                // Restart
                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    radius: 6
                                    color: rbtMouse.containsMouse ? root.colGold + "33" : "transparent"

                                    Text {
                                        anchors.centerIn: parent
                                        text: "󰜉 Reboot"
                                        font.pixelSize: 10
                                        font.bold: true
                                        color: root.colGold
                                    }

                                    MouseArea {
                                        id: rbtMouse
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        onClicked: {
                                            root.runCmd(["systemctl", "reboot"]);
                                            trayMenuPopup.visible = false;
                                        }
                                    }
                                }

                                Rectangle {
                                    width: 1
                                    height: 16
                                    color: root.colBorder
                                }

                                // Power Menu
                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    radius: 6
                                    color: pwrMenuMouse.containsMouse ? root.colRed + "33" : "transparent"

                                    Text {
                                        anchors.centerIn: parent
                                        text: " Power"
                                        font.pixelSize: 10
                                        font.bold: true
                                        color: root.colRed
                                    }

                                    MouseArea {
                                        id: pwrMenuMouse
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        onClicked: {
                                            root.runCmd(["wlogout", "-b", "2", "-c", "20", "-r", "20"]);
                                            trayMenuPopup.visible = false;
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

    // ========================================================
    // SECONDARY SCREEN (DP-1) - COMPANION BAR
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
        implicitHeight: 46
        color: "transparent"

        WlrLayershell.layer: WlrLayer.Top
        WlrLayershell.namespace: "garchy-shell"
        WlrLayershell.keyboardFocus: WlrKeyboardFocus.None
        exclusionMode: ExclusionMode.Auto

        Item {
            anchors.fill: parent
            anchors.topMargin: 4
            anchors.bottomMargin: 4
            anchors.leftMargin: 10
            anchors.rightMargin: 10

            // Left: Workspaces for Right Screen
            Rectangle {
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: secWsRow.implicitWidth + 20
                color: root.colBg
                border.color: root.colBorder
                border.width: 1
                radius: 12

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

                            width: 26
                            height: 26
                            radius: 6
                            color: isWsActive ? root.colAccentAlt : "transparent"

                            Text {
                                anchors.centerIn: parent
                                text: modelData
                                font.pixelSize: 12
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

            // Center: Digital Clock
            Rectangle {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: 90
                color: root.colBg
                border.color: root.colBorder
                border.width: 1
                radius: 12

                Text {
                    anchors.centerIn: parent
                    text: root.timeStr
                    font.pixelSize: 14
                    font.bold: true
                    color: root.colFg
                }
            }
        }
    }
}
