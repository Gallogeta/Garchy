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
    // DYNAMIC WALLUST / THEME GALLERY PALETTE & GEOMETRY
    // ========================================================
    property color colBg: "#070b12F2"
    property color colBgAlt: "#0f172a"
    property color colFg: "#f8fafc"
    property color colFgMuted: "#94a3b8"
    property color colAccent: "#38bdf8"
    property color colAccentAlt: "#2563eb"
    property color colBorder: "#1e293b"
    property color colGold: "#fbbf24"
    property color colRed: "#f43f5e"
    property color colGreen: "#10b981"
    property int themeRounding: 6
    property string layoutStyle: "garchy"
    property string activeThemeId: "garchy"
    property bool isFullSakura: root.layoutStyle === "full_sakura" || root.activeThemeId === "cyber_sakura"
    property int barHeight: 46

    property int islandRadius: root.themeRounding
    property int cardRadius: Math.max(3, root.themeRounding - 2)
    property int buttonRadius: Math.max(2, root.themeRounding - 2)
    property int popupRadius: Math.max(4, root.themeRounding + 2)
    property var pinnedApps: []

    FileView {
        id: pinnedAppsFile
        path: "/home/gallo/.config/gally/pinned_apps.json"
        watchChanges: true
        onLoaded: {
            try {
                root.pinnedApps = JSON.parse(text());
            } catch(e) {}
        }
        onFileChanged: {
            reload();
            try {
                root.pinnedApps = JSON.parse(text());
            } catch(e) {}
        }
    }

    function applyThemeJson(json) {
        if (!json) return;
        if (json.id) root.activeThemeId = json.id;
        if (json.bg) {
            var b = String(json.bg).trim();
            root.colBg = b.length === 7 ? b + "F0" : b;
        }
        if (json.bg_alt || json.bg_card) root.colBgAlt = json.bg_alt || json.bg_card;
        if (json.fg) root.colFg = json.fg;
        if (json.fg_muted) root.colFgMuted = json.fg_muted;
        if (json.accent) root.colAccent = json.accent;
        if (json.accent_alt) root.colAccentAlt = json.accent_alt;
        if (json.border || json.border_col) root.colBorder = json.border || json.border_col;
        else if (json.accent) root.colBorder = json.accent;
        if (json.gold) root.colGold = json.gold;
        if (json.rounding !== undefined) {
            var r = parseInt(json.rounding);
            root.themeRounding = r;
            root.islandRadius = r;
            root.cardRadius = Math.max(3, r - 2);
            root.buttonRadius = Math.max(2, r - 2);
            root.popupRadius = Math.max(4, r + 2);
        } else if (json.hypr_rounding !== undefined) {
            var r = parseInt(json.hypr_rounding);
            root.themeRounding = r;
            root.islandRadius = r;
            root.cardRadius = Math.max(3, r - 2);
            root.buttonRadius = Math.max(2, r - 2);
            root.popupRadius = Math.max(4, r + 2);
        }
        if (json.layout_style) root.layoutStyle = json.layout_style;
        if (json.bar_height) root.barHeight = parseInt(json.bar_height);
    }

    FileView {
        id: activeThemeFile
        path: "/home/gallo/.config/gally/active_theme.json"
        watchChanges: true
        onLoaded: {
            try {
                root.applyThemeJson(JSON.parse(text()));
            } catch(e) {}
        }
        onFileChanged: {
            reload();
            try {
                root.applyThemeJson(JSON.parse(text()));
            } catch(e) {}
        }
    }

    Timer {
        interval: 1000
        running: true
        repeat: true
        onTriggered: {
            activeThemeFile.reload();
            try {
                root.applyThemeJson(JSON.parse(activeThemeFile.text()));
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
        actionProc.exec(["python3", "/home/gallo/.config/quickshell/garchy-bar/taskbar_service.py", action, addr || ""]);
    }

    function runCmd(cmdList) {
        cmdProc.exec(cmdList);
    }

    Process {
        id: actionProc
        function exec(args) {
            running = false;
            command = args;
            running = true;
        }
    }

    Process {
        id: cmdProc
        function exec(args) {
            running = false;
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
        implicitHeight: root.barHeight
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

            // 🌸 CYBER SAKURA CONTINUOUS FULL BAR CONTAINER
            Rectangle {
                id: fullSakuraBar
                visible: root.isFullSakura
                anchors.fill: parent
                radius: 18
                color: root.colBg
                border.color: root.colBorder
                border.width: 1.5
            }

            // 1. LEFT ISLAND: Launcher, Pinned Apps, Workspaces 1-4, Grouped Taskbar
            Rectangle {
                id: leftIsland
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: leftLayout.implicitWidth + 20
                color: root.isFullSakura ? "transparent" : root.colBg
                border.color: root.isFullSakura ? "transparent" : root.colBorder
                border.width: root.isFullSakura ? 0 : 1.5
                radius: root.islandRadius

                RowLayout {
                    id: leftLayout
                    anchors.centerIn: parent
                    spacing: 8

                    // 🌌 / 🌸 Launcher Button
                    Rectangle {
                        width: 32
                        height: 32
                        radius: root.buttonRadius
                        color: launchArea.containsMouse ? root.colAccent + "33" : (root.isFullSakura ? "transparent" : root.colBgAlt)
                        border.color: launchArea.containsMouse ? root.colAccent : (root.isFullSakura ? "transparent" : root.colBorder)
                        border.width: 1

                        Text {
                            anchors.centerIn: parent
                            text: root.isFullSakura ? "🌸" : "󰣇"
                            font.pixelSize: root.isFullSakura ? 17 : 18
                            color: root.colAccent
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

                    // 🌸 CYBER SAKURA PINNED QUICK-LAUNCH DOCK
                    Row {
                        id: pinnedRow
                        visible: root.isFullSakura && root.pinnedApps && root.pinnedApps.length > 0
                        spacing: 4
                        Layout.alignment: Qt.AlignVCenter

                        Repeater {
                            model: root.pinnedApps

                            Rectangle {
                                width: 30
                                height: 30
                                radius: 8
                                property bool isRunning: {
                                    if (!root.taskbarState || !root.taskbarState.groups) return false;
                                    var pId = (modelData.id || "").toLowerCase();
                                    var pCmd = (modelData.cmd || "").toLowerCase();
                                    for (var i = 0; i < root.taskbarState.groups.length; i++) {
                                        var g = root.taskbarState.groups[i];
                                        var gId = (g.app_id || "").toLowerCase();
                                        var gClass = (g.wm_class || "").toLowerCase();
                                        if (gId.includes(pId) || gId.includes(pCmd) || gClass.includes(pId) || gClass.includes(pCmd)) return true;
                                    }
                                    return false;
                                }

                                color: pinMouse.containsMouse ? (root.colAccent + "33") : (isRunning ? (root.colBgAlt || "#242038") : "transparent")
                                border.color: isRunning ? (root.colAccent || "#f5bde6") : (pinMouse.containsMouse ? (root.colAccentAlt || "#c6a0f6") : "transparent")
                                border.width: isRunning ? 1.5 : 1

                                Image {
                                    anchors.centerIn: parent
                                    width: 18
                                    height: 18
                                    source: Quickshell.iconPath(modelData.icon || modelData.id)
                                    fillMode: Image.PreserveAspectFit
                                }

                                // Subtle Blossom Glow Dot when Running
                                Rectangle {
                                    visible: isRunning
                                    width: 4
                                    height: 4
                                    radius: 2
                                    color: root.colAccent || "#f5bde6"
                                    anchors.bottom: parent.bottom
                                    anchors.bottomMargin: 2
                                    anchors.horizontalCenter: parent.horizontalCenter
                                }

                                MouseArea {
                                    id: pinMouse
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    acceptedButtons: Qt.LeftButton | Qt.RightButton
                                    onClicked: mouse => {
                                        if (mouse.button === Qt.LeftButton) {
                                            var foundAddr = "";
                                            if (root.taskbarState && root.taskbarState.groups) {
                                                var pId = (modelData.id || "").toLowerCase();
                                                var pCmd = (modelData.cmd || "").toLowerCase();
                                                for (var i = 0; i < root.taskbarState.groups.length; i++) {
                                                    var g = root.taskbarState.groups[i];
                                                    var gId = (g.app_id || "").toLowerCase();
                                                    var gClass = (g.wm_class || "").toLowerCase();
                                                    if (gId.includes(pId) || gId.includes(pCmd) || gClass.includes(pId) || gClass.includes(pCmd)) {
                                                        if (g.windows && g.windows.length > 0) {
                                                            foundAddr = g.windows[0].address;
                                                            break;
                                                        }
                                                    }
                                                }
                                            }
                                            if (foundAddr) {
                                                root.dispatchAction("focus", foundAddr);
                                            } else {
                                                root.runCmd(["hyprctl", "dispatch", "exec", modelData.cmd || modelData.id]);
                                            }
                                        } else if (mouse.button === Qt.RightButton) {
                                            pinnedMenuPopup.targetApp = modelData;
                                            pinnedMenuPopup.visible = true;
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // Delicate Vertical Divider
                    Rectangle {
                        visible: root.isFullSakura && root.pinnedApps && root.pinnedApps.length > 0
                        width: 1
                        height: 16
                        color: root.colAccentAlt + "44"
                        Layout.alignment: Qt.AlignVCenter
                    }

                    // 🔢 Workspaces (1 2 3 4)
                    Rectangle {
                        height: 30
                        width: wsRow.implicitWidth + 10
                        radius: root.cardRadius
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
                                    radius: root.buttonRadius
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
                                id: appItem
                                property var groupData: modelData
                                width: 38
                                height: 32

                                Rectangle {
                                    id: appPill
                                    anchors.fill: parent
                                    radius: root.buttonRadius
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
                                        radius: Math.max(1, root.buttonRadius / 4)
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
                                        radius: Math.max(2, root.buttonRadius - 2)
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
                                            if (mouse.button === Qt.RightButton || (mouse.button === Qt.LeftButton && groupData.windows.length > 1 && groupData.is_minimized)) {
                                                groupMenuPopup.currentGroup = groupData;
                                                var p = appItem.mapToItem(null, 0, 0);
                                                groupMenuPopup.anchor.rect.x = Math.max(10, Math.min(winMain.width - 320, p.x - 20));
                                                groupMenuPopup.visible = !groupMenuPopup.visible;
                                            } else if (mouse.button === Qt.LeftButton) {
                                                if (groupData.windows.length === 1) {
                                                    root.dispatchAction("toggle", groupData.windows[0].address);
                                                } else {
                                                    var act = groupData.windows.find(w => w.is_active);
                                                    if (act) {
                                                        root.dispatchAction("toggle", act.address);
                                                    } else {
                                                        root.dispatchAction("focus", groupData.windows[0].address);
                                                    }
                                                }
                                            } else if (mouse.button === Qt.MiddleButton) {
                                                if (groupData.windows.length === 1) {
                                                    root.dispatchAction("close", groupData.windows[0].address);
                                                } else {
                                                    groupMenuPopup.currentGroup = groupData;
                                                    groupMenuPopup.visible = true;
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

            // 📂 Primary Screen Multi-Window Popup (Right-Click Selection)
            PopupWindow {
                id: groupMenuPopup
                property var currentGroup: null

                anchor.window: winMain
                anchor.rect.x: 120
                anchor.rect.y: 46
                anchor.rect.width: 320
                anchor.rect.height: 0
                anchor.edges: Edges.Bottom
                anchor.gravity: Edges.Bottom
                implicitWidth: 320
                implicitHeight: Math.min(380, menuCol.implicitHeight + 24)
                color: "transparent"
                visible: false

                Rectangle {
                    anchors.fill: parent
                    radius: root.popupRadius
                    color: "#0a0f1d"
                    border.color: root.colAccent
                    border.width: 1.5

                    ColumnLayout {
                        id: menuCol
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 8

                        // Header: Icon + Title + Window Count
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            Item {
                                width: 22
                                height: 22
                                Layout.alignment: Qt.AlignVCenter

                                Image {
                                    anchors.fill: parent
                                    source: Quickshell.iconPath(groupMenuPopup.currentGroup ? groupMenuPopup.currentGroup.icon : "")
                                    fillMode: Image.PreserveAspectFit
                                    visible: status === Image.Ready
                                }

                                Text {
                                    anchors.centerIn: parent
                                    visible: !parent.children[0].visible
                                    text: "󰖯"
                                    font.pixelSize: 16
                                    color: root.colAccent
                                }
                            }

                            Text {
                                text: (groupMenuPopup.currentGroup ? groupMenuPopup.currentGroup.class : "App") + " (" + (groupMenuPopup.currentGroup ? groupMenuPopup.currentGroup.count : 0) + " open)"
                                font.pixelSize: 12
                                font.bold: true
                                color: root.colFg
                            }

                            Item { Layout.fillWidth: true }

                            Rectangle {
                                width: 20
                                height: 20
                                radius: root.buttonRadius
                                color: closeGrpMouse.containsMouse ? root.colRed : root.colBgAlt

                                Text {
                                    anchors.centerIn: parent
                                    text: "✕"
                                    font.pixelSize: 9
                                    color: closeGrpMouse.containsMouse ? "#ffffff" : root.colFgMuted
                                }

                                MouseArea {
                                    id: closeGrpMouse
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    onClicked: groupMenuPopup.visible = false
                                }
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 1
                            color: root.colBorder
                        }

                        // Window List (Scrollable if more than 5 windows)
                        ScrollView {
                            Layout.fillWidth: true
                            Layout.preferredHeight: Math.min(260, winListCol.implicitHeight)
                            clip: true
                            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                            ScrollBar.vertical.policy: winListCol.implicitHeight > 260 ? ScrollBar.AlwaysOn : ScrollBar.AsNeeded

                            ColumnLayout {
                                id: winListCol
                                width: 296
                                spacing: 6

                                Repeater {
                                    model: groupMenuPopup.currentGroup ? groupMenuPopup.currentGroup.windows : []

                                    Rectangle {
                                        Layout.fillWidth: true
                                        Layout.preferredHeight: 38
                                        radius: root.cardRadius
                                        color: itemMouse.containsMouse ? root.colBgAlt : (modelData.is_active ? root.colAccent + "33" : root.colBgAlt)
                                        border.color: modelData.is_active ? root.colAccent : (modelData.is_minimized ? root.colGold + "88" : root.colBorder)
                                        border.width: 1

                                        RowLayout {
                                            anchors.fill: parent
                                            anchors.leftMargin: 10
                                            anchors.rightMargin: 8
                                            spacing: 8

                                            // Left area: Focus / Restore Window
                                            Item {
                                                Layout.fillWidth: true
                                                Layout.fillHeight: true

                                                RowLayout {
                                                    anchors.fill: parent
                                                    spacing: 8

                                                    Rectangle {
                                                        width: 8
                                                        height: 8
                                                        radius: 4
                                                        color: modelData.is_active ? root.colAccent : (modelData.is_minimized ? root.colGold : root.colFgMuted)
                                                    }

                                                    ColumnLayout {
                                                        Layout.fillWidth: true
                                                        spacing: 1

                                                        Text {
                                                            Layout.fillWidth: true
                                                            text: modelData.title || "Window"
                                                            font.pixelSize: 11
                                                            font.bold: modelData.is_active
                                                            elide: Text.ElideRight
                                                            color: modelData.is_active ? root.colAccent : root.colFg
                                                        }

                                                        Text {
                                                            Layout.fillWidth: true
                                                            text: modelData.is_minimized ? "🗕 Minimized (Click to Restore)" : (modelData.is_active ? "● Active Window" : "Workspace " + (modelData.workspace_name || modelData.workspace_id))
                                                            font.pixelSize: 9
                                                            color: modelData.is_minimized ? root.colGold : root.colFgMuted
                                                        }
                                                    }
                                                }

                                                MouseArea {
                                                    id: itemMouse
                                                    anchors.fill: parent
                                                    hoverEnabled: true
                                                    cursorShape: Qt.PointingHandCursor
                                                    onClicked: {
                                                        root.dispatchAction("focus", modelData.address);
                                                        groupMenuPopup.visible = false;
                                                    }
                                                }
                                            }

                                            // Right area: Close Specific Window
                                            Rectangle {
                                                width: 24
                                                height: 24
                                                radius: root.buttonRadius
                                                color: winCloseMouse.containsMouse ? root.colRed : root.colBgAlt
                                                border.color: winCloseMouse.containsMouse ? root.colRed : root.colBorder
                                                border.width: 1

                                                Text {
                                                    anchors.centerIn: parent
                                                    text: "✕"
                                                    font.pixelSize: 10
                                                    font.bold: true
                                                    color: winCloseMouse.containsMouse ? "#ffffff" : root.colFgMuted
                                                }

                                                MouseArea {
                                                    id: winCloseMouse
                                                    anchors.fill: parent
                                                    hoverEnabled: true
                                                    cursorShape: Qt.PointingHandCursor
                                                    onClicked: {
                                                        root.dispatchAction("close", modelData.address);
                                                        groupMenuPopup.visible = false;
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        // Pin/Unpin option for Cyber Sakura
                        Rectangle {
                            visible: root.isFullSakura && groupMenuPopup.currentGroup
                            Layout.fillWidth: true
                            height: 28
                            radius: root.buttonRadius
                            color: pinToggleMouse.containsMouse ? (root.colAccent + "33") : root.colBgAlt
                            border.color: pinToggleMouse.containsMouse ? root.colAccent : root.colBorder
                            border.width: 1

                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 6
                                spacing: 8

                                Text {
                                    text: "📌"
                                    font.pixelSize: 11
                                }

                                Text {
                                    text: "Pin " + (groupMenuPopup.currentGroup ? groupMenuPopup.currentGroup.class : "App") + " to Sakura Dock"
                                    font.pixelSize: 10
                                    font.bold: true
                                    color: root.colFg
                                }
                            }

                            MouseArea {
                                id: pinToggleMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    if (groupMenuPopup.currentGroup) {
                                        var g = groupMenuPopup.currentGroup;
                                        root.runCmd(["python3", "/home/gallo/.config/hypr/scripts/pin_app.py", "add", g.class.toLowerCase(), g.title || g.class, g.icon || g.class.toLowerCase(), g.class.toLowerCase()]);
                                    }
                                    groupMenuPopup.visible = false;
                                }
                            }
                        }
                    }
                }
            }

            // 📌 Primary Screen Pinned App Context Menu
            PopupWindow {
                id: pinnedMenuPopup
                property var targetApp: null

                anchor.window: winMain
                anchor.rect.x: 80
                anchor.rect.y: 46
                anchor.rect.width: 220
                anchor.rect.height: 0
                anchor.edges: Edges.Bottom
                anchor.gravity: Edges.Bottom
                implicitWidth: 220
                implicitHeight: pinMenuCol.implicitHeight + 20
                color: "transparent"
                visible: false

                Rectangle {
                    anchors.fill: parent
                    radius: root.popupRadius
                    color: root.colBgAlt
                    border.color: root.colAccent
                    border.width: 1.5

                    ColumnLayout {
                        id: pinMenuCol
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 6

                        // Header
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            Image {
                                width: 18
                                height: 18
                                source: Quickshell.iconPath(pinnedMenuPopup.targetApp ? (pinnedMenuPopup.targetApp.icon || pinnedMenuPopup.targetApp.id) : "application-x-executable")
                                fillMode: Image.PreserveAspectFit
                            }

                            Text {
                                text: pinnedMenuPopup.targetApp ? pinnedMenuPopup.targetApp.name : "Pinned App"
                                font.pixelSize: 12
                                font.bold: true
                                color: root.colFg
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 1
                            color: root.colBorder
                        }

                        // Launch
                        Rectangle {
                            Layout.fillWidth: true
                            height: 28
                            radius: 6
                            color: launchPinMouse.containsMouse ? (root.colAccent + "33") : "transparent"

                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: 8
                                spacing: 6

                                Text { text: "🚀"; font.pixelSize: 12 }
                                Text { text: "Launch Application"; font.pixelSize: 11; color: root.colFg }
                            }

                            MouseArea {
                                id: launchPinMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    if (pinnedMenuPopup.targetApp) {
                                        root.runCmd(["hyprctl", "dispatch", "exec", pinnedMenuPopup.targetApp.cmd || pinnedMenuPopup.targetApp.id]);
                                    }
                                    pinnedMenuPopup.visible = false;
                                }
                            }
                        }

                        // Unpin
                        Rectangle {
                            Layout.fillWidth: true
                            height: 28
                            radius: 6
                            color: unpinMouse.containsMouse ? (root.colRed + "33") : "transparent"

                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: 8
                                spacing: 6

                                Text { text: "📍"; font.pixelSize: 12 }
                                Text { text: "Unpin from Dock"; font.pixelSize: 11; color: unpinMouse.containsMouse ? root.colRed : root.colFg }
                            }

                            MouseArea {
                                id: unpinMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    if (pinnedMenuPopup.targetApp) {
                                        root.runCmd(["python3", "/home/gallo/.config/hypr/scripts/pin_app.py", "remove", pinnedMenuPopup.targetApp.id]);
                                    }
                                    pinnedMenuPopup.visible = false;
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
                width: clockLayout.implicitWidth + (root.isFullSakura ? 28 : 36)
                color: root.isFullSakura ? (root.colBgAlt + "88") : root.colBg
                border.color: root.isFullSakura ? "transparent" : (clockArea.containsMouse ? root.colAccent : root.colBorder)
                border.width: root.isFullSakura ? 0 : 1.5
                radius: root.isFullSakura ? 14 : root.islandRadius

                RowLayout {
                    id: clockLayout
                    anchors.centerIn: parent
                    spacing: 6

                    Text {
                        visible: root.isFullSakura
                        text: "🌸"
                        font.pixelSize: 12
                        color: root.colAccent
                    }

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
                    radius: root.popupRadius
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
                            radius: root.buttonRadius
                            color: calBtnArea.containsMouse ? root.colAccent + "33" : root.colBgAlt
                            border.color: calBtnArea.containsMouse ? root.colAccent : root.colBorder
                            border.width: 1

                            RowLayout {
                                anchors.centerIn: parent
                                spacing: 8

                                Text {
                                    text: "󰸗"
                                    font.pixelSize: 14
                                    color: root.colAccent
                                }

                                Text {
                                    text: "Open Calendar"
                                    font.pixelSize: 12
                                    font.bold: true
                                    color: root.colFg
                                }
                            }

                            MouseArea {
                                id: calBtnArea
                                anchors.fill: parent
                                hoverEnabled: true
                                onClicked: {
                                    root.runCmd(["bash", "-c", "gnome-calendar || korganizer || xfce4-calendar"]);
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
                color: root.isFullSakura ? "transparent" : root.colBg
                border.color: root.isFullSakura ? "transparent" : root.colBorder
                border.width: root.isFullSakura ? 0 : 1.5
                radius: root.islandRadius

                RowLayout {
                    id: rightLayout
                    anchors.centerIn: parent
                    spacing: 10

                    // 🔊 Volume Pill
                    Rectangle {
                        height: 28
                        width: volRow.implicitWidth + 16
                        radius: root.buttonRadius
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
                        radius: root.buttonRadius
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
                        radius: root.buttonRadius
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
                            onClicked: root.runCmd(["bash", "-c", "~/.config/hypr/scripts/theme-switcher.sh"])
                        }
                    }

                    // 󰅀 Down Arrow / Minimized Tray Menu
                    Rectangle {
                        id: trayBtn
                        width: 28
                        height: 28
                        radius: root.buttonRadius
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
                    radius: root.popupRadius
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
                                radius: root.buttonRadius
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
                                        radius: Math.max(1, root.buttonRadius / 2)
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
                                radius: root.buttonRadius
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

                        // 2. BACKGROUND & TRAY SERVICES SECTION (SCROLLABLE)
                        Text {
                            text: "BACKGROUND & TRAY SERVICES"
                            font.pixelSize: 9
                            font.bold: true
                            color: root.colAccent
                            Layout.topMargin: 2
                        }

                        ScrollView {
                            Layout.fillWidth: true
                            Layout.preferredHeight: Math.min(230, svcCol.implicitHeight)
                            clip: true
                            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                            ScrollBar.vertical.policy: svcCol.implicitHeight > 230 ? ScrollBar.AlwaysOn : ScrollBar.AsNeeded

                            ColumnLayout {
                                id: svcCol
                                width: 312
                                spacing: 6

                                Repeater {
                                    model: root.taskbarState.tray_services || []

                                    Rectangle {
                                        Layout.fillWidth: true
                                        Layout.preferredHeight: 38
                                        radius: root.cardRadius
                                        color: svcMouse.containsMouse ? root.colBgAlt : "#131c3188"
                                        border.color: modelData.is_running ? root.colBorder : "transparent"
                                        border.width: 1

                                        RowLayout {
                                            anchors.fill: parent
                                            anchors.leftMargin: 10
                                            anchors.rightMargin: 10
                                            spacing: 10

                                            // Fixed Icon Container (prevents overlap)
                                            Item {
                                                Layout.preferredWidth: 22
                                                Layout.preferredHeight: 22
                                                Layout.alignment: Qt.AlignVCenter

                                                Image {
                                                    anchors.fill: parent
                                                    source: Quickshell.iconPath(modelData.icon)
                                                    fillMode: Image.PreserveAspectFit
                                                    opacity: modelData.is_running ? 1.0 : 0.4
                                                    visible: status === Image.Ready
                                                }

                                                Text {
                                                    anchors.centerIn: parent
                                                    visible: !parent.children[0].visible
                                                    text: "󰖯"
                                                    font.pixelSize: 16
                                                    color: modelData.is_running ? root.colAccent : root.colFgMuted
                                                }
                                            }

                                            ColumnLayout {
                                                Layout.fillWidth: true
                                                Layout.alignment: Qt.AlignVCenter
                                                spacing: 1

                                                Text {
                                                    Layout.fillWidth: true
                                                    text: modelData.name
                                                    font.pixelSize: 11
                                                    font.bold: true
                                                    elide: Text.ElideRight
                                                    color: modelData.is_running ? root.colFg : root.colFgMuted
                                                }

                                                Text {
                                                    Layout.fillWidth: true
                                                    text: modelData.status_text
                                                    font.pixelSize: 10
                                                    elide: Text.ElideRight
                                                    color: modelData.is_running ? (modelData.is_minimized ? root.colGold : root.colAccent) : root.colFgMuted
                                                }
                                            }

                                            // Action Button (Restore / Open / Launch)
                                            Rectangle {
                                                Layout.preferredWidth: 62
                                                Layout.preferredHeight: 24
                                                Layout.alignment: Qt.AlignVCenter
                                                radius: root.buttonRadius
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
                                radius: root.buttonRadius
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
                                radius: root.buttonRadius
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
                                radius: root.buttonRadius
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
                                        root.runCmd(["bash", "-c", "~/.config/hypr/scripts/theme-switcher.sh"]);
                                        trayMenuPopup.visible = false;
                                    }
                                }
                            }
                        }

                        // 4. POWER & SESSION BAR
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 32
                            radius: root.cardRadius
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
                                    radius: root.buttonRadius
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
                                    radius: root.buttonRadius
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
                                    radius: root.buttonRadius
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
    // SECONDARY SCREEN (DP-1) - FULL SYNCED GARCHY SHELL
    // ========================================================
    PanelWindow {
        id: winSec
        screen: {
            for (var i = 0; i < Quickshell.screens.length; i++) {
                if (Quickshell.screens[i].name === "DP-1") return Quickshell.screens[i];
            }
            return Quickshell.screens.length > 1 ? Quickshell.screens[1] : Quickshell.screens[0];
        }

        anchors {
            top: true
            left: true
            right: true
        }
        implicitHeight: root.barHeight
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

            // 🌸 CYBER SAKURA CONTINUOUS FULL BAR CONTAINER
            Rectangle {
                id: fullSecSakuraBar
                visible: root.isFullSakura
                anchors.fill: parent
                radius: 18
                color: root.colBg
                border.color: root.colBorder
                border.width: 1.5
            }

            // 1. LEFT ISLAND: Launcher, Pinned Apps, Workspaces 1-4, Grouped Taskbar
            Rectangle {
                id: secLeftIsland
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: secLeftLayout.implicitWidth + 20
                color: root.isFullSakura ? "transparent" : root.colBg
                border.color: root.isFullSakura ? "transparent" : root.colBorder
                border.width: root.isFullSakura ? 0 : 1.5
                radius: root.islandRadius

                RowLayout {
                    id: secLeftLayout
                    anchors.centerIn: parent
                    spacing: 8

                    // 🌌 / 🌸 Launcher Button
                    Rectangle {
                        width: 32
                        height: 32
                        radius: root.buttonRadius
                        color: secLaunchArea.containsMouse ? root.colAccent + "33" : (root.isFullSakura ? "transparent" : root.colBgAlt)
                        border.color: secLaunchArea.containsMouse ? root.colAccent : (root.isFullSakura ? "transparent" : root.colBorder)
                        border.width: 1

                        Text {
                            anchors.centerIn: parent
                            text: root.isFullSakura ? "🌸" : "󰣇"
                            font.pixelSize: root.isFullSakura ? 17 : 18
                            color: root.colAccent
                        }

                        MouseArea {
                            id: secLaunchArea
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

                    // 🌸 CYBER SAKURA PINNED QUICK-LAUNCH DOCK
                    Row {
                        id: secPinnedRow
                        visible: root.isFullSakura && root.pinnedApps && root.pinnedApps.length > 0
                        spacing: 4
                        Layout.alignment: Qt.AlignVCenter

                        Repeater {
                            model: root.pinnedApps

                            Rectangle {
                                width: 30
                                height: 30
                                radius: 8
                                property bool isRunning: {
                                    if (!root.taskbarState || !root.taskbarState.groups) return false;
                                    var pId = (modelData.id || "").toLowerCase();
                                    var pCmd = (modelData.cmd || "").toLowerCase();
                                    for (var i = 0; i < root.taskbarState.groups.length; i++) {
                                        var g = root.taskbarState.groups[i];
                                        var gId = (g.app_id || "").toLowerCase();
                                        var gClass = (g.wm_class || "").toLowerCase();
                                        if (gId.includes(pId) || gId.includes(pCmd) || gClass.includes(pId) || gClass.includes(pCmd)) return true;
                                    }
                                    return false;
                                }

                                color: secPinMouse.containsMouse ? (root.colAccent + "33") : (isRunning ? (root.colBgAlt || "#242038") : "transparent")
                                border.color: isRunning ? (root.colAccent || "#f5bde6") : (secPinMouse.containsMouse ? (root.colAccentAlt || "#c6a0f6") : "transparent")
                                border.width: isRunning ? 1.5 : 1

                                Image {
                                    anchors.centerIn: parent
                                    width: 18
                                    height: 18
                                    source: Quickshell.iconPath(modelData.icon || modelData.id)
                                    fillMode: Image.PreserveAspectFit
                                }

                                // Subtle Blossom Glow Dot when Running
                                Rectangle {
                                    visible: isRunning
                                    width: 4
                                    height: 4
                                    radius: 2
                                    color: root.colAccent || "#f5bde6"
                                    anchors.bottom: parent.bottom
                                    anchors.bottomMargin: 2
                                    anchors.horizontalCenter: parent.horizontalCenter
                                }

                                MouseArea {
                                    id: secPinMouse
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    acceptedButtons: Qt.LeftButton | Qt.RightButton
                                    onClicked: mouse => {
                                        if (mouse.button === Qt.LeftButton) {
                                            var foundAddr = "";
                                            if (root.taskbarState && root.taskbarState.groups) {
                                                var pId = (modelData.id || "").toLowerCase();
                                                var pCmd = (modelData.cmd || "").toLowerCase();
                                                for (var i = 0; i < root.taskbarState.groups.length; i++) {
                                                    var g = root.taskbarState.groups[i];
                                                    var gId = (g.app_id || "").toLowerCase();
                                                    var gClass = (g.wm_class || "").toLowerCase();
                                                    if (gId.includes(pId) || gId.includes(pCmd) || gClass.includes(pId) || gClass.includes(pCmd)) {
                                                        if (g.windows && g.windows.length > 0) {
                                                            foundAddr = g.windows[0].address;
                                                            break;
                                                        }
                                                    }
                                                }
                                            }
                                            if (foundAddr) {
                                                root.dispatchAction("focus", foundAddr);
                                            } else {
                                                root.runCmd(["hyprctl", "dispatch", "exec", modelData.cmd || modelData.id]);
                                            }
                                        } else if (mouse.button === Qt.RightButton) {
                                            secPinnedMenuPopup.targetApp = modelData;
                                            secPinnedMenuPopup.visible = true;
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // Delicate Vertical Divider
                    Rectangle {
                        visible: root.isFullSakura && root.pinnedApps && root.pinnedApps.length > 0
                        width: 1
                        height: 16
                        color: root.colAccentAlt + "44"
                        Layout.alignment: Qt.AlignVCenter
                    }

                    // 🔢 Workspaces (1 2 3 4) for Secondary Monitor
                    Rectangle {
                        height: 30
                        width: secWsRow.implicitWidth + 10
                        radius: root.cardRadius
                        color: root.colBgAlt
                        border.color: root.colBorder
                        border.width: 1

                        Row {
                            id: secWsRow
                            anchors.centerIn: parent
                            spacing: 3

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
                                    radius: root.buttonRadius
                                    color: isWsActive ? root.colAccent : (secWsMouse.containsMouse ? root.colBorder : "transparent")

                                    Text {
                                        anchors.centerIn: parent
                                        text: modelData
                                        font.pixelSize: 12
                                        font.bold: true
                                        color: isWsActive ? "#0a0f1d" : (secWsMouse.containsMouse ? root.colFg : root.colFgMuted)
                                    }

                                    MouseArea {
                                        id: secWsMouse
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        onClicked: root.runCmd(["bash", "-c", "~/.config/hypr/scripts/dual-desktop.sh switch " + modelData])
                                    }
                                }
                            }
                        }
                    }

                    // Divider
                    Rectangle {
                        width: 1
                        height: 18
                        color: root.colBorder
                    }

                    // 💻 Icon-Only Grouped Taskbar for Secondary Monitor
                    RowLayout {
                        spacing: 4

                        Repeater {
                            id: secTaskbarRepeater
                            model: root.taskbarState.groups || []

                            Rectangle {
                                id: secAppItem
                                property var groupData: modelData

                                Layout.preferredWidth: groupData.is_active ? 40 : 34
                                Layout.preferredHeight: 32
                                radius: root.buttonRadius
                                color: groupData.is_active ? root.colAccent + "26" : (secAppMouse.containsMouse ? root.colBgAlt : "transparent")
                                border.color: groupData.is_active ? root.colAccent : (secAppMouse.containsMouse ? root.colBorder : "transparent")
                                border.width: groupData.is_active ? 1.5 : 1

                                Image {
                                    id: secAppIcon
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
                                    visible: secAppIcon.status !== Image.Ready
                                    text: "󰖯"
                                    font.pixelSize: 18
                                    color: groupData.is_active ? root.colAccent : root.colFg
                                }

                                Rectangle {
                                    anchors.bottom: parent.bottom
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    anchors.bottomMargin: 2
                                    width: groupData.is_active ? 18 : 4
                                    height: 2.5
                                    radius: Math.max(1, root.buttonRadius / 4)
                                    color: groupData.is_active ? root.colAccent : (groupData.is_minimized ? root.colGold : root.colFgMuted)
                                    Behavior on width { NumberAnimation { duration: 150 } }
                                }

                                Rectangle {
                                    visible: groupData.count > 1
                                    anchors.top: parent.top
                                    anchors.right: parent.right
                                    anchors.topMargin: 2
                                    anchors.rightMargin: 2
                                    width: 14
                                    height: 14
                                    radius: Math.max(2, root.buttonRadius - 2)
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
                                    id: secAppMouse
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    acceptedButtons: Qt.LeftButton | Qt.RightButton | Qt.MiddleButton

                                    onClicked: mouse => {
                                        if (mouse.button === Qt.RightButton || (mouse.button === Qt.LeftButton && groupData.windows.length > 1 && groupData.is_minimized)) {
                                            secGroupMenuPopup.currentGroup = groupData;
                                            var p = secAppItem.mapToItem(null, 0, 0);
                                            secGroupMenuPopup.anchor.rect.x = Math.max(10, Math.min(winSec.width - 320, p.x - 20));
                                            secGroupMenuPopup.visible = !secGroupMenuPopup.visible;
                                        } else if (mouse.button === Qt.LeftButton) {
                                            if (groupData.windows.length === 1) {
                                                root.dispatchAction("toggle", groupData.windows[0].address);
                                            } else {
                                                var act = groupData.windows.find(w => w.is_active);
                                                if (act) {
                                                    root.dispatchAction("toggle", act.address);
                                                } else {
                                                    root.dispatchAction("focus", groupData.windows[0].address);
                                                }
                                            }
                                        } else if (mouse.button === Qt.MiddleButton) {
                                            if (groupData.windows.length === 1) {
                                                root.dispatchAction("close", groupData.windows[0].address);
                                            } else {
                                                secGroupMenuPopup.currentGroup = groupData;
                                                secGroupMenuPopup.visible = true;
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // 📂 Secondary Screen Multi-Window Popup (Right-Click Selection)
            PopupWindow {
                id: secGroupMenuPopup
                property var currentGroup: null

                anchor.window: winSec
                anchor.rect.x: 120
                anchor.rect.y: 46
                anchor.rect.width: 320
                anchor.rect.height: 0
                anchor.edges: Edges.Bottom
                anchor.gravity: Edges.Bottom
                implicitWidth: 320
                implicitHeight: Math.min(380, secMenuCol.implicitHeight + 24)
                color: "transparent"
                visible: false

                Rectangle {
                    anchors.fill: parent
                    radius: root.popupRadius
                    color: "#0a0f1d"
                    border.color: root.colAccent
                    border.width: 1.5

                    ColumnLayout {
                        id: secMenuCol
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 8

                        // Header: Icon + Title + Window Count
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            Item {
                                width: 22
                                height: 22
                                Layout.alignment: Qt.AlignVCenter

                                Image {
                                    anchors.fill: parent
                                    source: Quickshell.iconPath(secGroupMenuPopup.currentGroup ? secGroupMenuPopup.currentGroup.icon : "")
                                    fillMode: Image.PreserveAspectFit
                                    visible: status === Image.Ready
                                }

                                Text {
                                    anchors.centerIn: parent
                                    visible: !parent.children[0].visible
                                    text: "󰖯"
                                    font.pixelSize: 16
                                    color: root.colAccent
                                }
                            }

                            Text {
                                text: (secGroupMenuPopup.currentGroup ? secGroupMenuPopup.currentGroup.class : "App") + " (" + (secGroupMenuPopup.currentGroup ? secGroupMenuPopup.currentGroup.count : 0) + " open)"
                                font.pixelSize: 12
                                font.bold: true
                                color: root.colFg
                            }

                            Item { Layout.fillWidth: true }

                            Rectangle {
                                width: 20
                                height: 20
                                radius: root.buttonRadius
                                color: secCloseGrpMouse.containsMouse ? root.colRed : root.colBgAlt

                                Text {
                                    anchors.centerIn: parent
                                    text: "✕"
                                    font.pixelSize: 9
                                    color: secCloseGrpMouse.containsMouse ? "#ffffff" : root.colFgMuted
                                }

                                MouseArea {
                                    id: secCloseGrpMouse
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    onClicked: secGroupMenuPopup.visible = false
                                }
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 1
                            color: root.colBorder
                        }

                        // Window List (Scrollable if more than 5 windows)
                        ScrollView {
                            Layout.fillWidth: true
                            Layout.preferredHeight: Math.min(260, secWinListCol.implicitHeight)
                            clip: true
                            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                            ScrollBar.vertical.policy: secWinListCol.implicitHeight > 260 ? ScrollBar.AlwaysOn : ScrollBar.AsNeeded

                            ColumnLayout {
                                id: secWinListCol
                                width: 296
                                spacing: 6

                                Repeater {
                                    model: secGroupMenuPopup.currentGroup ? secGroupMenuPopup.currentGroup.windows : []

                                    Rectangle {
                                        Layout.fillWidth: true
                                        Layout.preferredHeight: 38
                                        radius: root.cardRadius
                                        color: secItemMouse.containsMouse ? root.colBgAlt : (modelData.is_active ? root.colAccent + "33" : root.colBgAlt)
                                        border.color: modelData.is_active ? root.colAccent : (modelData.is_minimized ? root.colGold + "88" : root.colBorder)
                                        border.width: 1

                                        RowLayout {
                                            anchors.fill: parent
                                            anchors.leftMargin: 10
                                            anchors.rightMargin: 8
                                            spacing: 8

                                            // Left area: Focus / Restore Window
                                            Item {
                                                Layout.fillWidth: true
                                                Layout.fillHeight: true

                                                RowLayout {
                                                    anchors.fill: parent
                                                    spacing: 8

                                                    Rectangle {
                                                        width: 8
                                                        height: 8
                                                        radius: 4
                                                        color: modelData.is_active ? root.colAccent : (modelData.is_minimized ? root.colGold : root.colFgMuted)
                                                    }

                                                    ColumnLayout {
                                                        Layout.fillWidth: true
                                                        spacing: 1

                                                        Text {
                                                            Layout.fillWidth: true
                                                            text: modelData.title || "Window"
                                                            font.pixelSize: 11
                                                            font.bold: modelData.is_active
                                                            elide: Text.ElideRight
                                                            color: modelData.is_active ? root.colAccent : root.colFg
                                                        }

                                                        Text {
                                                            Layout.fillWidth: true
                                                            text: modelData.is_minimized ? "🗕 Minimized (Click to Restore)" : (modelData.is_active ? "● Active Window" : "Workspace " + (modelData.workspace_name || modelData.workspace_id))
                                                            font.pixelSize: 9
                                                            color: modelData.is_minimized ? root.colGold : root.colFgMuted
                                                        }
                                                    }
                                                }

                                                MouseArea {
                                                    id: secItemMouse
                                                    anchors.fill: parent
                                                    hoverEnabled: true
                                                    cursorShape: Qt.PointingHandCursor
                                                    onClicked: {
                                                        root.dispatchAction("focus", modelData.address);
                                                        secGroupMenuPopup.visible = false;
                                                    }
                                                }
                                            }

                                            // Right area: Close Specific Window
                                            Rectangle {
                                                width: 24
                                                height: 24
                                                radius: root.buttonRadius
                                                color: secWinCloseMouse.containsMouse ? root.colRed : root.colBgAlt
                                                border.color: secWinCloseMouse.containsMouse ? root.colRed : root.colBorder
                                                border.width: 1

                                                Text {
                                                    anchors.centerIn: parent
                                                    text: "✕"
                                                    font.pixelSize: 10
                                                    font.bold: true
                                                    color: secWinCloseMouse.containsMouse ? "#ffffff" : root.colFgMuted
                                                }

                                                MouseArea {
                                                    id: secWinCloseMouse
                                                    anchors.fill: parent
                                                    hoverEnabled: true
                                                    cursorShape: Qt.PointingHandCursor
                                                    onClicked: {
                                                        root.dispatchAction("close", modelData.address);
                                                        secGroupMenuPopup.visible = false;
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        // Pin/Unpin option for Cyber Sakura
                        Rectangle {
                            visible: root.isFullSakura && secGroupMenuPopup.currentGroup
                            Layout.fillWidth: true
                            height: 28
                            radius: root.buttonRadius
                            color: secPinToggleMouse.containsMouse ? (root.colAccent + "33") : root.colBgAlt
                            border.color: secPinToggleMouse.containsMouse ? root.colAccent : root.colBorder
                            border.width: 1

                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 6
                                spacing: 8

                                Text {
                                    text: "📌"
                                    font.pixelSize: 11
                                }

                                Text {
                                    text: "Pin " + (secGroupMenuPopup.currentGroup ? secGroupMenuPopup.currentGroup.class : "App") + " to Sakura Dock"
                                    font.pixelSize: 10
                                    font.bold: true
                                    color: root.colFg
                                }
                            }

                            MouseArea {
                                id: secPinToggleMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    if (secGroupMenuPopup.currentGroup) {
                                        var g = secGroupMenuPopup.currentGroup;
                                        root.runCmd(["python3", "/home/gallo/.config/hypr/scripts/pin_app.py", "add", g.class.toLowerCase(), g.title || g.class, g.icon || g.class.toLowerCase(), g.class.toLowerCase()]);
                                    }
                                    secGroupMenuPopup.visible = false;
                                }
                            }
                        }
                    }
                }
            }

            // 📌 Secondary Screen Pinned App Context Menu
            PopupWindow {
                id: secPinnedMenuPopup
                property var targetApp: null

                anchor.window: winSec
                anchor.rect.x: 80
                anchor.rect.y: 46
                anchor.rect.width: 220
                anchor.rect.height: 0
                anchor.edges: Edges.Bottom
                anchor.gravity: Edges.Bottom
                implicitWidth: 220
                implicitHeight: secPinMenuCol.implicitHeight + 20
                color: "transparent"
                visible: false

                Rectangle {
                    anchors.fill: parent
                    radius: root.popupRadius
                    color: root.colBgAlt
                    border.color: root.colAccent
                    border.width: 1.5

                    ColumnLayout {
                        id: secPinMenuCol
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 6

                        // Header
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            Image {
                                width: 18
                                height: 18
                                source: Quickshell.iconPath(secPinnedMenuPopup.targetApp ? (secPinnedMenuPopup.targetApp.icon || secPinnedMenuPopup.targetApp.id) : "application-x-executable")
                                fillMode: Image.PreserveAspectFit
                            }

                            Text {
                                text: secPinnedMenuPopup.targetApp ? secPinnedMenuPopup.targetApp.name : "Pinned App"
                                font.pixelSize: 12
                                font.bold: true
                                color: root.colFg
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 1
                            color: root.colBorder
                        }

                        // Launch
                        Rectangle {
                            Layout.fillWidth: true
                            height: 28
                            radius: 6
                            color: secLaunchPinMouse.containsMouse ? (root.colAccent + "33") : "transparent"

                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: 8
                                spacing: 6

                                Text { text: "🚀"; font.pixelSize: 12 }
                                Text { text: "Launch Application"; font.pixelSize: 11; color: root.colFg }
                            }

                            MouseArea {
                                id: secLaunchPinMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    if (secPinnedMenuPopup.targetApp) {
                                        root.runCmd(["hyprctl", "dispatch", "exec", secPinnedMenuPopup.targetApp.cmd || secPinnedMenuPopup.targetApp.id]);
                                    }
                                    secPinnedMenuPopup.visible = false;
                                }
                            }
                        }

                        // Unpin
                        Rectangle {
                            Layout.fillWidth: true
                            height: 28
                            radius: 6
                            color: secUnpinMouse.containsMouse ? (root.colRed + "33") : "transparent"

                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: 8
                                spacing: 6

                                Text { text: "📍"; font.pixelSize: 12 }
                                Text { text: "Unpin from Dock"; font.pixelSize: 11; color: secUnpinMouse.containsMouse ? root.colRed : root.colFg }
                            }

                            MouseArea {
                                id: secUnpinMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    if (secPinnedMenuPopup.targetApp) {
                                        root.runCmd(["python3", "/home/gallo/.config/hypr/scripts/pin_app.py", "remove", secPinnedMenuPopup.targetApp.id]);
                                    }
                                    secPinnedMenuPopup.visible = false;
                                }
                            }
                        }
                    }
                }
            }

            // 2. CENTER ISLAND: Digital Clock & Date Popup
            Rectangle {
                id: secCenterIsland
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: secClockLayout.implicitWidth + (root.isFullSakura ? 28 : 36)
                color: root.isFullSakura ? (root.colBgAlt + "88") : root.colBg
                border.color: root.isFullSakura ? "transparent" : (secClockArea.containsMouse ? root.colAccent : root.colBorder)
                border.width: root.isFullSakura ? 0 : 1.5
                radius: root.isFullSakura ? 14 : root.islandRadius

                RowLayout {
                    id: secClockLayout
                    anchors.centerIn: parent
                    spacing: 6

                    Text {
                        visible: root.isFullSakura
                        text: "🌸"
                        font.pixelSize: 12
                        color: root.colAccent
                    }

                    Text {
                        text: root.timeStr
                        font.pixelSize: 14
                        font.bold: true
                        color: root.colFg
                    }
                }

                MouseArea {
                    id: secClockArea
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: secDatePopup.visible = !secDatePopup.visible
                }
            }

            // 📅 Secondary Center Clock Dropdown: Date & Calendar Menu
            PopupWindow {
                id: secDatePopup
                anchor.window: winSec
                anchor.rect.x: Math.round((winSec.width - 280) / 2)
                anchor.rect.y: 46
                anchor.rect.width: 280
                anchor.rect.height: 0
                anchor.edges: Edges.Bottom
                anchor.gravity: Edges.Bottom
                implicitWidth: 280
                implicitHeight: secDateCol.implicitHeight + 28
                color: "transparent"
                visible: false

                Rectangle {
                    anchors.fill: parent
                    radius: root.popupRadius
                    color: root.colBg
                    border.color: root.colAccent
                    border.width: 1.5

                    ColumnLayout {
                        id: secDateCol
                        anchors.fill: parent
                        anchors.margins: 14
                        spacing: 10

                        Text {
                            text: root.timeStr
                            font.pixelSize: 22
                            font.bold: true
                            color: root.colFg
                            Layout.alignment: Qt.AlignHCenter
                        }

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

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 32
                            radius: root.buttonRadius
                            color: secCalBtnArea.containsMouse ? root.colAccent + "33" : root.colBgAlt
                            border.color: secCalBtnArea.containsMouse ? root.colAccent : root.colBorder
                            border.width: 1

                            RowLayout {
                                anchors.centerIn: parent
                                spacing: 8

                                Text {
                                    text: "󰸗"
                                    font.pixelSize: 14
                                    color: root.colAccent
                                }

                                Text {
                                    text: "Open Calendar"
                                    font.pixelSize: 12
                                    font.bold: true
                                    color: root.colFg
                                }
                            }

                            MouseArea {
                                id: secCalBtnArea
                                anchors.fill: parent
                                hoverEnabled: true
                                onClicked: {
                                    root.runCmd(["bash", "-c", "gnome-calendar || korganizer || xfce4-calendar"]);
                                    secDatePopup.visible = false;
                                }
                            }
                        }
                    }
                }
            }

            // 3. RIGHT ISLAND: Volume, Gally AI, Theme, Down Arrow Menu
            Rectangle {
                id: secRightIsland
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: secRightLayout.implicitWidth + 24
                color: root.isFullSakura ? "transparent" : root.colBg
                border.color: root.isFullSakura ? "transparent" : root.colBorder
                border.width: root.isFullSakura ? 0 : 1.5
                radius: root.islandRadius

                RowLayout {
                    id: secRightLayout
                    anchors.centerIn: parent
                    spacing: 10

                    // 🔊 Volume Pill
                    Rectangle {
                        height: 28
                        width: secVolRow.implicitWidth + 16
                        radius: root.buttonRadius
                        color: root.colBgAlt

                        RowLayout {
                            id: secVolRow
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
                        radius: root.buttonRadius
                        color: secAiMouse.containsMouse ? root.colAccent + "33" : "transparent"

                        Text {
                            anchors.centerIn: parent
                            text: "󰚩"
                            font.pixelSize: 16
                            color: root.colAccent
                        }

                        MouseArea {
                            id: secAiMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: root.runCmd(["bash", "-c", "python3 ~/.config/hypr/scripts/gally-ai-hud.py"])
                        }
                    }

                    // 🎨 Wallust Theme Switcher
                    Rectangle {
                        width: 30
                        height: 30
                        radius: root.buttonRadius
                        color: secThmMouse.containsMouse ? root.colAccentAlt + "33" : "transparent"

                        Text {
                            anchors.centerIn: parent
                            text: "󰏘"
                            font.pixelSize: 16
                            color: root.colAccentAlt
                        }

                        MouseArea {
                            id: secThmMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: root.runCmd(["bash", "-c", "~/.config/hypr/scripts/theme-switcher.sh"])
                        }
                    }

                    // 󰅀 Down Arrow / Minimized Tray Menu
                    Rectangle {
                        width: 28
                        height: 28
                        radius: root.buttonRadius
                        color: secTrayArea.containsMouse || secTrayMenuPopup.visible ? root.colBgAlt : "transparent"
                        border.color: secTrayArea.containsMouse || secTrayMenuPopup.visible ? root.colAccent : "transparent"
                        border.width: 1

                        Text {
                            anchors.centerIn: parent
                            text: "󰅀"
                            font.pixelSize: 15
                            color: root.taskbarState.minimized_windows && root.taskbarState.minimized_windows.length > 0 ? root.colGold : root.colFgMuted
                        }

                        MouseArea {
                            id: secTrayArea
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: secTrayMenuPopup.visible = !secTrayMenuPopup.visible
                        }
                    }
                }
            }

            // 🗕 Secondary Screen Luxury Tray & System Hub
            PopupWindow {
                id: secTrayMenuPopup
                anchor.window: winSec
                anchor.rect.x: winSec.width - 364
                anchor.rect.y: 46
                anchor.rect.width: 350
                anchor.rect.height: 0
                anchor.edges: Edges.Bottom
                anchor.gravity: Edges.Bottom
                implicitWidth: 350
                implicitHeight: secHubCol.implicitHeight + 28
                color: "transparent"
                visible: false

                Rectangle {
                    anchors.fill: parent
                    radius: root.popupRadius
                    color: root.colBg
                    border.color: root.colAccent
                    border.width: 1.5

                    ColumnLayout {
                        id: secHubCol
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

                            Rectangle {
                                width: secStatusRow.implicitWidth + 10
                                height: 20
                                radius: root.buttonRadius
                                color: root.colGreen + "22"
                                border.color: root.colGreen
                                border.width: 1

                                RowLayout {
                                    id: secStatusRow
                                    anchors.centerIn: parent
                                    spacing: 4

                                    Rectangle {
                                        width: 6
                                        height: 6
                                        radius: Math.max(1, root.buttonRadius / 2)
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

                            Rectangle {
                                width: 22
                                height: 22
                                radius: root.buttonRadius
                                color: secCloseHubMouse.containsMouse ? root.colRed : root.colBgAlt

                                Text {
                                    anchors.centerIn: parent
                                    text: "✕"
                                    font.pixelSize: 10
                                    color: secCloseHubMouse.containsMouse ? "#ffffff" : root.colFgMuted
                                }

                                MouseArea {
                                    id: secCloseHubMouse
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    onClicked: secTrayMenuPopup.visible = false
                                }
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 1
                            color: root.colBorder
                        }

                        // 2. BACKGROUND & TRAY SERVICES
                        Text {
                            text: "BACKGROUND & TRAY SERVICES"
                            font.pixelSize: 9
                            font.bold: true
                            color: root.colAccent
                            Layout.topMargin: 2
                        }

                        ScrollView {
                            Layout.fillWidth: true
                            Layout.preferredHeight: Math.min(230, secSvcCol.implicitHeight)
                            clip: true
                            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                            ScrollBar.vertical.policy: secSvcCol.implicitHeight > 230 ? ScrollBar.AlwaysOn : ScrollBar.AsNeeded

                            ColumnLayout {
                                id: secSvcCol
                                width: 312
                                spacing: 6

                                Repeater {
                                    model: root.taskbarState.tray_services || []

                                    Rectangle {
                                        Layout.fillWidth: true
                                        Layout.preferredHeight: 38
                                        radius: root.cardRadius
                                        color: secSvcMouse.containsMouse ? root.colBgAlt : "#131c3188"
                                        border.color: modelData.is_running ? root.colBorder : "transparent"
                                        border.width: 1

                                        RowLayout {
                                            anchors.fill: parent
                                            anchors.leftMargin: 10
                                            anchors.rightMargin: 10
                                            spacing: 10

                                            Item {
                                                Layout.preferredWidth: 22
                                                Layout.preferredHeight: 22
                                                Layout.alignment: Qt.AlignVCenter

                                                Image {
                                                    anchors.fill: parent
                                                    source: Quickshell.iconPath(modelData.icon)
                                                    fillMode: Image.PreserveAspectFit
                                                    opacity: modelData.is_running ? 1.0 : 0.4
                                                    visible: status === Image.Ready
                                                }

                                                Text {
                                                    anchors.centerIn: parent
                                                    visible: !parent.children[0].visible
                                                    text: "󰖯"
                                                    font.pixelSize: 16
                                                    color: modelData.is_running ? root.colAccent : root.colFgMuted
                                                }
                                            }

                                            ColumnLayout {
                                                Layout.fillWidth: true
                                                Layout.alignment: Qt.AlignVCenter
                                                spacing: 1

                                                Text {
                                                    Layout.fillWidth: true
                                                    text: modelData.name
                                                    font.pixelSize: 11
                                                    font.bold: true
                                                    elide: Text.ElideRight
                                                    color: modelData.is_running ? root.colFg : root.colFgMuted
                                                }

                                                Text {
                                                    Layout.fillWidth: true
                                                    text: modelData.status_text
                                                    font.pixelSize: 10
                                                    elide: Text.ElideRight
                                                    color: modelData.is_running ? (modelData.is_minimized ? root.colGold : root.colAccent) : root.colFgMuted
                                                }
                                            }

                                            Rectangle {
                                                Layout.preferredWidth: 62
                                                Layout.preferredHeight: 24
                                                Layout.alignment: Qt.AlignVCenter
                                                radius: root.buttonRadius
                                                color: secActArea.containsMouse ? root.colAccent : root.colBgAlt
                                                border.color: root.colAccent
                                                border.width: 1

                                                Text {
                                                    anchors.centerIn: parent
                                                    text: modelData.has_window ? (modelData.is_minimized ? "Restore" : "Focus") : (modelData.is_running ? "Open" : "Launch")
                                                    font.pixelSize: 10
                                                    font.bold: true
                                                    color: secActArea.containsMouse ? "#0a0f1d" : root.colAccent
                                                }

                                                MouseArea {
                                                    id: secActArea
                                                    anchors.fill: parent
                                                    hoverEnabled: true
                                                    onClicked: {
                                                        if (modelData.has_window) {
                                                            root.dispatchAction("toggle", modelData.address);
                                                        } else {
                                                            root.runCmd(["bash", "-c", modelData.cmd]);
                                                        }
                                                        secTrayMenuPopup.visible = false;
                                                    }
                                                }
                                            }
                                        }

                                        MouseArea {
                                            id: secSvcMouse
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            onClicked: {
                                                if (modelData.has_window) {
                                                    root.dispatchAction("toggle", modelData.address);
                                                } else {
                                                    root.runCmd(["bash", "-c", modelData.cmd]);
                                                }
                                                secTrayMenuPopup.visible = false;
                                            }
                                        }
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

                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 30
                                radius: root.buttonRadius
                                color: secGmMouse.containsMouse ? root.colAccent + "33" : root.colBgAlt
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
                                    id: secGmMouse
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    onClicked: {
                                        root.runCmd(["bash", "-c", "garchy-game status"]);
                                        secTrayMenuPopup.visible = false;
                                    }
                                }
                            }

                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 30
                                radius: root.buttonRadius
                                color: secPavuMouse.containsMouse ? root.colAccent + "33" : root.colBgAlt
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
                                    id: secPavuMouse
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    onClicked: {
                                        root.runCmd(["pavucontrol"]);
                                        secTrayMenuPopup.visible = false;
                                    }
                                }
                            }

                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 30
                                radius: root.buttonRadius
                                color: secThmQMouse.containsMouse ? root.colAccentAlt + "33" : root.colBgAlt
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
                                    id: secThmQMouse
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    onClicked: {
                                        root.runCmd(["bash", "-c", "~/.config/hypr/scripts/theme-switcher.sh"]);
                                        secTrayMenuPopup.visible = false;
                                    }
                                }
                            }
                        }

                        // 4. POWER & SESSION BAR
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 32
                            radius: root.cardRadius
                            color: root.colBgAlt
                            border.color: root.colBorder
                            border.width: 1

                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: 8
                                anchors.rightMargin: 8

                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    radius: root.buttonRadius
                                    color: secLckMouse.containsMouse ? root.colAccent + "33" : "transparent"

                                    Text {
                                        anchors.centerIn: parent
                                        text: " Lock"
                                        font.pixelSize: 10
                                        font.bold: true
                                        color: root.colFg
                                    }

                                    MouseArea {
                                        id: secLckMouse
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        onClicked: {
                                            root.runCmd(["hyprlock"]);
                                            secTrayMenuPopup.visible = false;
                                        }
                                    }
                                }

                                Rectangle {
                                    width: 1
                                    height: 16
                                    color: root.colBorder
                                }

                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    radius: root.buttonRadius
                                    color: secRbtMouse.containsMouse ? root.colGold + "33" : "transparent"

                                    Text {
                                        anchors.centerIn: parent
                                        text: "󰜉 Reboot"
                                        font.pixelSize: 10
                                        font.bold: true
                                        color: root.colGold
                                    }

                                    MouseArea {
                                        id: secRbtMouse
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        onClicked: {
                                            root.runCmd(["systemctl", "reboot"]);
                                            secTrayMenuPopup.visible = false;
                                        }
                                    }
                                }

                                Rectangle {
                                    width: 1
                                    height: 16
                                    color: root.colBorder
                                }

                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    radius: root.buttonRadius
                                    color: secPwrMenuMouse.containsMouse ? root.colRed + "33" : "transparent"

                                    Text {
                                        anchors.centerIn: parent
                                        text: " Power"
                                        font.pixelSize: 10
                                        font.bold: true
                                        color: root.colRed
                                    }

                                    MouseArea {
                                        id: secPwrMenuMouse
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        onClicked: {
                                            root.runCmd(["wlogout", "-b", "2", "-c", "20", "-r", "20"]);
                                            secTrayMenuPopup.visible = false;
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
}
