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
    property color colBg: "#F0181222"
    property color colBgAlt: "#281b36"
    property color colFg: "#fdf2f8"
    property color colFgMuted: "#d4b8e0"
    property color colAccent: "#f9a8d4"
    property color colAccentAlt: "#c084fc"
    property color colBorder: "#c084fc"
    property color colGold: "#fed7aa"
    property color colRed: "#fca5a5"
    property color colGreen: "#f9a8d4"
    property int themeRounding: 6
    property string layoutStyle: "garchy"
    property string activeThemeId: "garchy"
    property bool isFullSakura: root.layoutStyle === "full_sakura" || root.activeThemeId === "cyber_sakura"
    property bool isBottomBar: root.isFullSakura
    property int barHeight: root.isFullSakura ? 58 : 48
    property int pinnedDockCapacity: 5

    property int islandRadius: root.themeRounding
    property int cardRadius: Math.max(3, root.themeRounding - 2)
    property int buttonRadius: Math.max(2, root.themeRounding - 2)
    property int popupRadius: Math.max(4, root.themeRounding + 2)
    property var pinnedApps: []

    property var allAppsList: []

    FileView {
        id: appsCacheFile
        path: "/home/gallo/.cache/garchy_desktop_apps.json"
        watchChanges: true
        onLoaded: {
            try {
                root.allAppsList = JSON.parse(text());
            } catch(e) {}
        }
        onFileChanged: {
            reload();
            try {
                root.allAppsList = JSON.parse(text());
            } catch(e) {}
        }
    }

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

    function withAlpha(c, a) {
        return Qt.rgba(c.r, c.g, c.b, a);
    }

    function applyThemeJson(json) {
        if (!json) return;
        if (json.id) root.activeThemeId = json.id;
        if (json.bg) {
            var b = String(json.bg).trim();
            root.colBg = b.length === 7 ? ("#F0" + b.replace("#", "")) : b;
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
        interval: 800
        running: true
        repeat: true
        onTriggered: {
            activeThemeFile.reload();
            try {
                root.applyThemeJson(JSON.parse(activeThemeFile.text()));
            } catch(e) {}
            pinnedAppsFile.reload();
            appsCacheFile.reload();
            try {
                var p = JSON.parse(pinnedAppsFile.text());
                if (Array.isArray(p)) root.pinnedApps = p;
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
            top: !root.isBottomBar
            bottom: root.isBottomBar
            left: true
            right: true
        }
        implicitHeight: root.barHeight
        color: "transparent"

        WlrLayershell.layer: WlrLayer.Top
        WlrLayershell.namespace: "garchy-shell"
        WlrLayershell.keyboardFocus: (startMenuPopup.visible ? WlrKeyboardFocus.Exclusive : WlrKeyboardFocus.None)
        exclusionMode: ExclusionMode.Auto

        Item {
            anchors.fill: parent
            anchors.topMargin: root.isBottomBar ? 5 : 4
            anchors.bottomMargin: root.isBottomBar ? 5 : 4
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

            // 1. LEFT ISLAND: Launcher, Pinned Apps, Workspaces 1-4
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
                        width: 36
                        height: 36
                        radius: root.buttonRadius
                        color: launchArea.containsMouse ? root.withAlpha(root.colAccent, 0.20) : (root.isFullSakura ? "transparent" : root.colBgAlt)
                        border.color: launchArea.containsMouse ? root.colAccent : (root.isFullSakura ? "transparent" : root.colBorder)
                        border.width: 1

                        Text {
                            anchors.centerIn: parent
                            text: root.isFullSakura ? "🌸" : "󰣇"
                            font.pixelSize: root.isFullSakura ? 19 : 20
                            color: root.colAccent
                        }

                        MouseArea {
                            id: launchArea
                            anchors.fill: parent
                            hoverEnabled: true
                            acceptedButtons: Qt.LeftButton | Qt.RightButton
                            onClicked: mouse => {
                                if (mouse.button === Qt.LeftButton) {
                                    startMenuPopup.visible = !startMenuPopup.visible;
                                } else {
                                    root.runCmd(["bash", "-c", "~/.config/hypr/scripts/wallpaper-select.sh"]);
                                }
                            }
                        }
                    }

                    // 🌸 CYBER SAKURA PINNED QUICK-LAUNCH DOCK (With Emoticon Placeholders for Unpinned Slots)
                    Row {
                        id: pinnedRow
                        visible: root.isFullSakura
                        spacing: 5
                        Layout.alignment: Qt.AlignVCenter

                        Repeater {
                            model: Math.max(root.pinnedDockCapacity, (root.pinnedApps ? root.pinnedApps.length : 0))

                            Rectangle {
                                id: pinSlotItem
                                property int slotIndex: index
                                property bool isPinned: root.pinnedApps && slotIndex < root.pinnedApps.length
                                property var appData: isPinned ? root.pinnedApps[slotIndex] : null

                                property bool isRunning: {
                                    if (!isPinned || !appData || !root.taskbarState || !root.taskbarState.groups) return false;
                                    var pId = (appData.id || "").toLowerCase();
                                    var pCmd = (appData.cmd || "").toLowerCase();
                                    for (var i = 0; i < root.taskbarState.groups.length; i++) {
                                        var g = root.taskbarState.groups[i];
                                        var gId = (g.app_id || "").toLowerCase();
                                        var gClass = (g.wm_class || "").toLowerCase();
                                        if (gId.includes(pId) || gId.includes(pCmd) || gClass.includes(pId) || gClass.includes(pCmd)) return true;
                                    }
                                    return false;
                                }

                                width: 36
                                height: 36
                                radius: 10
                                color: isPinned 
                                    ? (pinSlotMouse.containsMouse ? (root.withAlpha(root.colAccent, 0.20)) : (isRunning ? (root.colBgAlt || "#281b36") : "transparent"))
                                    : (pinSlotMouse.containsMouse ? (root.withAlpha(root.colAccent, 0.15)) : (root.withAlpha(root.colBgAlt, 0.27)))
                                border.color: isPinned
                                    ? (isRunning ? (root.colAccent || "#f472b6") : (pinSlotMouse.containsMouse ? (root.colAccent || "#f472b6") : (root.withAlpha(root.colAccentAlt, 0.27))))
                                    : (pinSlotMouse.containsMouse ? (root.colAccent || "#f472b6") : (root.withAlpha(root.colBorder, 0.27)))
                                border.width: isPinned ? (isRunning ? 1.5 : 1) : 1

                                // 1. If Pinned: Application Desktop Icon
                                Image {
                                    id: pinSlotIcon
                                    visible: isPinned
                                    anchors.centerIn: parent
                                    width: 22
                                    height: 22
                                    source: isPinned && appData ? Quickshell.iconPath(appData.icon || appData.id) : ""
                                    fillMode: Image.PreserveAspectFit
                                }

                                // 2. If Pinned but icon failed to load: Pin Glyph
                                Text {
                                    visible: isPinned && pinSlotIcon.status !== Image.Ready
                                    anchors.centerIn: parent
                                    text: "󰤱"
                                    font.pixelSize: 16
                                    color: root.colAccent
                                }

                                // 3. If Unpinned Placeholder: Pastel Pin Glyph
                                Text {
                                    visible: !isPinned
                                    anchors.centerIn: parent
                                    text: "󰤱"
                                    font.pixelSize: 16
                                    color: root.colAccent
                                    opacity: pinSlotMouse.containsMouse ? 1.0 : 0.4
                                }

                                // Subtle Blossom Glow Dot when Running
                                Rectangle {
                                    visible: isPinned && isRunning
                                    width: 4
                                    height: 4
                                    radius: 2
                                    color: root.colAccent || "#f5bde6"
                                    anchors.bottom: parent.bottom
                                    anchors.bottomMargin: 2
                                    anchors.horizontalCenter: parent.horizontalCenter
                                }

                                MouseArea {
                                    id: pinSlotMouse
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    acceptedButtons: Qt.LeftButton | Qt.RightButton
                                    onClicked: mouse => {
                                        if (isPinned) {
                                            if (mouse.button === Qt.LeftButton) {
                                                var foundAddr = "";
                                                if (root.taskbarState && root.taskbarState.groups) {
                                                    var pId = (appData.id || "").toLowerCase();
                                                    var pCmd = (appData.cmd || "").toLowerCase();
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
                                                    root.runCmd(["bash", "-c", (appData.cmd || appData.id) + " & disown"]);
                                                }
                                            } else if (mouse.button === Qt.RightButton) {
                                                pinnedMenuPopup.targetApp = appData;
                                                pinnedMenuPopup.visible = true;
                                            }
                                        } else {
                                            // Unpinned placeholder slot: Open Launchpad
                                            startMenuPopup.visible = !startMenuPopup.visible;
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // Delicate Vertical Divider
                    Rectangle {
                        visible: root.isFullSakura
                        width: 1
                        height: 20
                        color: root.withAlpha(root.colAccentAlt, 0.27)
                        Layout.alignment: Qt.AlignVCenter
                    }

                    // 🔢 Workspaces (1 2 3 4)
                    Rectangle {
                        height: 36
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

                                    width: 26
                                    height: 26
                                    radius: root.buttonRadius
                                    color: isWsActive ? root.colAccent : (wsArea.containsMouse ? (root.withAlpha(root.colAccent, 0.20)) : "transparent")
                                    border.color: isWsActive ? root.colAccent : (wsArea.containsMouse ? root.colAccent : "transparent")
                                    border.width: 1

                                    Text {
                                        anchors.centerIn: parent
                                        text: modelData
                                        font.pixelSize: 13
                                        font.bold: true
                                        color: isWsActive ? "#181222" : (wsArea.containsMouse ? root.colAccent : root.colFgMuted)
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

                    // 🗔 WINDOWS 11 / KDE INTERACTIVE TASKBAR (When NOT Cyber Sakura)
                    Row {
                        id: taskbarRow
                        visible: !root.isFullSakura
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
                                    color: groupData.is_active ? root.withAlpha(root.colAccent, 0.20) : (appMouse.containsMouse ? (root.withAlpha(root.colAccent, 0.15)) : "transparent")
                                    border.color: groupData.is_active ? root.colAccent : (appMouse.containsMouse ? root.colAccent : "transparent")
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


            // ========================================================
            // 🪟 WINDOWS 10 STYLE START MENU POPUP (CYBER SAKURA)
            // ========================================================
            PopupWindow {
                id: startMenuPopup
                anchor.window: winMain
                anchor.rect.x: 8
                anchor.rect.y: root.isBottomBar ? 0 : 54
                anchor.rect.width: 720
                anchor.rect.height: 0
                anchor.edges: root.isBottomBar ? Edges.Top : Edges.Bottom
                anchor.gravity: root.isBottomBar ? Edges.Top : Edges.Bottom
                implicitWidth: 720
                implicitHeight: 560
                color: "transparent"
                visible: false

                Timer {
                    id: searchFocusTimer
                    interval: 60
                    repeat: false
                    onTriggered: {
                        searchField.forceActiveFocus();
                    }
                }

                onVisibleChanged: {
                    if (visible) {
                        searchField.text = "";
                        searchFocusTimer.restart();
                        Qt.callLater(function() { searchField.forceActiveFocus(); });
                    }
                }

                Rectangle {
                    focus: true
                    Keys.onEscapePressed: startMenuPopup.visible = false
                    anchors.fill: parent
                    radius: root.popupRadius
                    color: root.colBg
                    border.color: root.colAccent
                    border.width: 1.5
                    clip: true

                    RowLayout {
                        anchors.fill: parent
                        spacing: 0

                        // 1. LEFT NARROW RAIL (50px)
                        Rectangle {
                            Layout.fillHeight: true
                            Layout.preferredWidth: 50
                            color: root.withAlpha(root.colBgAlt, 0.4)
                            border.color: root.withAlpha(root.colBorder, 0.2)
                            border.width: 1

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 6
                                spacing: 8

                                // Top Hamburger Menu
                                Rectangle {
                                    Layout.preferredWidth: 38
                                    Layout.preferredHeight: 38
                                    radius: root.buttonRadius
                                    color: navHamMouse.containsMouse ? root.withAlpha(root.colAccent, 0.20) : "transparent"
                                    border.color: navHamMouse.containsMouse ? root.colAccent : "transparent"
                                    border.width: 1

                                    Text {
                                        anchors.centerIn: parent
                                        text: "󰍜"
                                        font.pixelSize: 18
                                        color: root.colAccent
                                    }

                                    MouseArea {
                                        id: navHamMouse
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                    }
                                }

                                Item { Layout.fillHeight: true }

                                // User Avatar
                                Rectangle {
                                    Layout.preferredWidth: 38
                                    Layout.preferredHeight: 38
                                    radius: root.buttonRadius
                                    color: navUserMouse.containsMouse ? root.withAlpha(root.colAccent, 0.20) : "transparent"
                                    border.color: navUserMouse.containsMouse ? root.colAccent : "transparent"
                                    border.width: 1

                                    Text {
                                        anchors.centerIn: parent
                                        text: "󰀉"
                                        font.pixelSize: 18
                                        color: root.colFg
                                    }

                                    MouseArea {
                                        id: navUserMouse
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                    }
                                }

                                // Files Shortcut (Thunar)
                                Rectangle {
                                    Layout.preferredWidth: 38
                                    Layout.preferredHeight: 38
                                    radius: root.buttonRadius
                                    color: navFilesMouse.containsMouse ? root.withAlpha(root.colAccent, 0.20) : "transparent"
                                    border.color: navFilesMouse.containsMouse ? root.colAccent : "transparent"
                                    border.width: 1

                                    Text {
                                        anchors.centerIn: parent
                                        text: "󰉋"
                                        font.pixelSize: 18
                                        color: root.colAccentAlt
                                    }

                                    MouseArea {
                                        id: navFilesMouse
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: {
                                            root.runCmd(["bash", "-c", "thunar & disown"]);
                                            startMenuPopup.visible = false;
                                        }
                                    }
                                }

                                // Settings Shortcut
                                Rectangle {
                                    Layout.preferredWidth: 38
                                    Layout.preferredHeight: 38
                                    radius: root.buttonRadius
                                    color: navSetMouse.containsMouse ? root.withAlpha(root.colAccent, 0.20) : "transparent"
                                    border.color: navSetMouse.containsMouse ? root.colAccent : "transparent"
                                    border.width: 1

                                    Text {
                                        anchors.centerIn: parent
                                        text: "󰒓"
                                        font.pixelSize: 18
                                        color: root.colGold
                                    }

                                    MouseArea {
                                        id: navSetMouse
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: {
                                            root.runCmd(["bash", "-c", "xfce4-settings-manager & disown"]);
                                            startMenuPopup.visible = false;
                                        }
                                    }
                                }

                                // Lock Screen
                                Rectangle {
                                    Layout.preferredWidth: 38
                                    Layout.preferredHeight: 38
                                    radius: root.buttonRadius
                                    color: navLockMouse.containsMouse ? root.withAlpha(root.colAccent, 0.20) : "transparent"
                                    border.color: navLockMouse.containsMouse ? root.colAccent : "transparent"
                                    border.width: 1

                                    Text {
                                        anchors.centerIn: parent
                                        text: "󰌾"
                                        font.pixelSize: 18
                                        color: root.colAccent
                                    }

                                    MouseArea {
                                        id: navLockMouse
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: {
                                            root.runCmd(["bash", "-c", "~/.config/hypr/scripts/dual-desktop.sh lock & disown"]);
                                            startMenuPopup.visible = false;
                                        }
                                    }
                                }

                                // Power Button
                                Rectangle {
                                    Layout.preferredWidth: 38
                                    Layout.preferredHeight: 38
                                    radius: root.buttonRadius
                                    color: navPwrMouse.containsMouse ? root.withAlpha(root.colRed, 0.25) : "transparent"
                                    border.color: navPwrMouse.containsMouse ? root.colRed : "transparent"
                                    border.width: 1

                                    Text {
                                        anchors.centerIn: parent
                                        text: "󰐥"
                                        font.pixelSize: 18
                                        color: navPwrMouse.containsMouse ? root.colRed : root.colFgMuted
                                    }

                                    MouseArea {
                                        id: navPwrMouse
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: {
                                            root.runCmd(["bash", "-c", "wlogout & disown"]);
                                            startMenuPopup.visible = false;
                                        }
                                    }
                                }
                            }
                        }

                        // 2. MIDDLE COLUMN: ALL APPS & REAL-TIME SEARCH (290px)
                        Rectangle {
                            Layout.fillHeight: true
                            Layout.preferredWidth: 290
                            color: "transparent"

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 14
                                spacing: 10

                                // Search Box
                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 38
                                    radius: 8
                                    color: root.colBgAlt
                                    border.color: searchField.activeFocus ? root.colAccent : root.withAlpha(root.colBorder, 0.4)
                                    border.width: searchField.activeFocus ? 1.5 : 1

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.margins: 8
                                        spacing: 8

                                        Text {
                                            text: "🔍"
                                            font.pixelSize: 13
                                            color: root.colAccent
                                        }

                                        TextInput {
                                            id: searchField
                                            Layout.fillWidth: true
                                            font.pixelSize: 12
                                            color: root.colFg
                                            clip: true
                                            selectByMouse: true
                                            focus: true
                                            property string placeholder: "Type here to search apps..."

                                            Keys.onEscapePressed: startMenuPopup.visible = false
                                            onAccepted: {
                                                if (appListView.count > 0 && appListView.model.length > 0) {
                                                    var topApp = appListView.model[0];
                                                    if (topApp && topApp.exec) {
                                                        root.runCmd(["bash", "-c", topApp.exec + " & disown"]);
                                                        startMenuPopup.visible = false;
                                                    }
                                                }
                                            }

                                            Text {
                                                visible: searchField.text === "" && !searchField.activeFocus
                                                text: searchField.placeholder
                                                font.pixelSize: 12
                                                color: root.colFgMuted
                                                anchors.fill: parent
                                                verticalAlignment: Text.AlignVCenter
                                            }
                                        }

                                        // Clear button
                                        Text {
                                            visible: searchField.text !== ""
                                            text: "✕"
                                            font.pixelSize: 11
                                            font.bold: true
                                            color: clearSearchMouse.containsMouse ? root.colRed : root.colFgMuted

                                            MouseArea {
                                                id: clearSearchMouse
                                                anchors.fill: parent
                                                hoverEnabled: true
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: {
                                                    searchField.text = "";
                                                    searchField.forceActiveFocus();
                                                }
                                            }
                                        }
                                    }
                                }

                                // Apps Header
                                RowLayout {
                                    Layout.fillWidth: true
                                    Text {
                                        text: searchField.text === "" ? "All Applications" : "Search Results"
                                        font.pixelSize: 11
                                        font.bold: true
                                        color: root.colAccent
                                    }
                                    Item { Layout.fillWidth: true }
                                    Text {
                                        text: appListView.count + " apps"
                                        font.pixelSize: 10
                                        color: root.colFgMuted
                                    }
                                }

                                // Scrollable App List
                                ListView {
                                    id: appListView
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    clip: true
                                    spacing: 4
                                    boundsBehavior: Flickable.StopAtBounds

                                    model: {
                                        var q = searchField.text.trim().toLowerCase();
                                        if (!q || q === "") return root.allAppsList;
                                        return (root.allAppsList || []).filter(function(a) {
                                            return (a.name && a.name.toLowerCase().includes(q)) ||
                                                   (a.comment && a.comment.toLowerCase().includes(q)) ||
                                                   (a.exec && a.exec.toLowerCase().includes(q));
                                        });
                                    }

                                    delegate: Rectangle {
                                        width: appListView.width
                                        height: 38
                                        radius: 6
                                        color: appItemMouse.containsMouse ? root.withAlpha(root.colAccent, 0.20) : "transparent"
                                        border.color: appItemMouse.containsMouse ? root.colAccent : "transparent"
                                        border.width: 1

                                        RowLayout {
                                            anchors.fill: parent
                                            anchors.margins: 6
                                            spacing: 10

                                            Image {
                                                id: appImg
                                                Layout.preferredWidth: 24
                                                Layout.preferredHeight: 24
                                                source: modelData.icon_path ? ("file://" + modelData.icon_path) : (Quickshell.iconPath(modelData.icon) || "")
                                                fillMode: Image.PreserveAspectFit
                                                visible: status === Image.Ready
                                            }

                                            Text {
                                                visible: !appImg.visible
                                                Layout.preferredWidth: 24
                                                Layout.preferredHeight: 24
                                                horizontalAlignment: Text.AlignHCenter
                                                verticalAlignment: Text.AlignVCenter
                                                text: modelData.glyph || "󰀻"
                                                font.pixelSize: 18
                                                color: root.colAccent
                                            }

                                            ColumnLayout {
                                                Layout.fillWidth: true
                                                spacing: 1

                                                Text {
                                                    Layout.fillWidth: true
                                                    text: modelData.name
                                                    font.pixelSize: 12
                                                    font.bold: true
                                                    color: root.colFg
                                                    elide: Text.ElideRight
                                                }

                                                Text {
                                                    visible: modelData.comment !== ""
                                                    Layout.fillWidth: true
                                                    text: modelData.comment || modelData.exec || ""
                                                    font.pixelSize: 9
                                                    color: root.colFgMuted
                                                    elide: Text.ElideRight
                                                }
                                            }
                                        }

                                        MouseArea {
                                            id: appItemMouse
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            acceptedButtons: Qt.LeftButton | Qt.RightButton
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: mouse => {
                                                if (mouse.button === Qt.LeftButton) {
                                                    root.runCmd(["bash", "-c", modelData.exec + " & disown"]);
                                                    startMenuPopup.visible = false;
                                                } else {
                                                    root.runCmd(["python3", "/home/gallo/.config/hypr/scripts/pin_app.py", "add", modelData.exec, modelData.name, modelData.icon]);
                                                    startMenuPopup.visible = false;
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }

                        // Divider
                        Rectangle {
                            Layout.fillHeight: true
                            Layout.preferredWidth: 1
                            color: root.withAlpha(root.colBorder, 0.3)
                        }

                        // 3. RIGHT COLUMN: WINDOWS 10 LIVE TILES / PINNED MATRIX (370px)
                        Rectangle {
                            Layout.fillHeight: true
                            Layout.fillWidth: true
                            color: "transparent"

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 14
                                spacing: 12

                                // Header
                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 8

                                    Text {
                                        text: root.isFullSakura ? "🌸 Cyber Sakura Hub" : "󰣇 Life at a glance"
                                        font.pixelSize: 14
                                        font.bold: true
                                        color: root.colFg
                                    }

                                    Item { Layout.fillWidth: true }

                                    Text {
                                        text: "Pinned Tiles"
                                        font.pixelSize: 11
                                        font.bold: true
                                        color: root.colAccent
                                    }
                                }

                                // 2x5 Grid of Windows 10 Live Tiles
                                GridLayout {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    columns: 2
                                    rowSpacing: 10
                                    columnSpacing: 10

                                    Repeater {
                                        model: [
                                            { name: "Brave Browser", sub: "Web Explorer", icon: "brave", icon_path: "/home/gallo/.local/share/icons/Papirus/24x24/apps/brave.svg", glyph: "󰖟", cmd: "brave", accent: root.colAccent },
                                            { name: "Kitty Terminal", sub: "144Hz CLI", icon: "kitty", icon_path: "/usr/share/icons/hicolor/scalable/apps/kitty.svg", glyph: "󰄛", cmd: "kitty", accent: root.colAccentAlt },
                                            { name: "Visual Studio Code", sub: "Code Editor", icon: "code", icon_path: "/home/gallo/.local/share/icons/Papirus/24x24/apps/code.svg", glyph: "󰨞", cmd: "code", accent: root.colAccent },
                                            { name: "Thunar Files", sub: "File System", icon: "thunar", icon_path: "/home/gallo/.local/share/icons/Papirus/24x24/apps/thunar.svg", glyph: "󰉋", cmd: "thunar", accent: root.colGold },
                                            { name: "Steam Games", sub: "Gaming Hub", icon: "steam", icon_path: "/usr/share/icons/hicolor/48x48/apps/steam.png", glyph: "󰓓", cmd: "steam", accent: root.colAccentAlt },
                                            { name: "Spotify Music", sub: "Audio Stream", icon: "spotify", icon_path: "/home/gallo/.local/share/icons/Papirus/24x24/apps/spotify.svg", glyph: "󰓇", cmd: "spotify", accent: root.colAccent },
                                            { name: "Gally AI Copilot", sub: "AI Assistant", icon: "help-browser", icon_path: "/usr/share/icons/AdwaitaLegacy/48x48/legacy/help-browser.png", glyph: "󰚩", cmd: "python3 ~/.config/hypr/scripts/gally-ai-hud.py", accent: root.colGold },
                                            { name: "Theme Gallery", sub: "Style Switcher", icon: "preferences-desktop-theme", icon_path: "/usr/share/icons/AdwaitaLegacy/48x48/legacy/preferences-desktop-theme.png", glyph: "󰏘", cmd: "~/.config/hypr/scripts/theme-switcher.sh", accent: root.colAccentAlt },
                                            { name: "Wallpapers", sub: "Backgrounds", icon: "preferences-desktop-wallpaper", icon_path: "/usr/share/icons/AdwaitaLegacy/48x48/legacy/preferences-desktop-wallpaper.png", glyph: "󰸉", cmd: "~/.config/hypr/scripts/wallpaper-select.sh", accent: root.colAccent },
                                            { name: "System Monitor", sub: "Hardware & BTOP", icon: "btop", icon_path: "/usr/share/icons/hicolor/scalable/apps/btop.svg", glyph: "󰍛", cmd: "kitty -e btop", accent: root.colAccentAlt }
                                        ]

                                        Rectangle {
                                            Layout.fillWidth: true
                                            Layout.fillHeight: true
                                            radius: 8
                                            color: tileMouse.containsMouse ? root.withAlpha(modelData.accent, 0.22) : root.colBgAlt
                                            border.color: tileMouse.containsMouse ? modelData.accent : root.withAlpha(root.colBorder, 0.35)
                                            border.width: tileMouse.containsMouse ? 1.5 : 1

                                            RowLayout {
                                                anchors.fill: parent
                                                anchors.margins: 10
                                                spacing: 10

                                                Image {
                                                    id: tileImg
                                                    Layout.preferredWidth: 32
                                                    Layout.preferredHeight: 32
                                                    source: modelData.icon_path ? ("file://" + modelData.icon_path) : (Quickshell.iconPath(modelData.icon) || "")
                                                    fillMode: Image.PreserveAspectFit
                                                    visible: status === Image.Ready
                                                }

                                                Text {
                                                    visible: !tileImg.visible
                                                    Layout.preferredWidth: 32
                                                    Layout.preferredHeight: 32
                                                    horizontalAlignment: Text.AlignHCenter
                                                    verticalAlignment: Text.AlignVCenter
                                                    text: modelData.glyph || "󰀻"
                                                    font.pixelSize: 24
                                                    color: modelData.accent
                                                }

                                                ColumnLayout {
                                                    Layout.fillWidth: true
                                                    spacing: 2

                                                    Text {
                                                        Layout.fillWidth: true
                                                        text: modelData.name
                                                        font.pixelSize: 11
                                                        font.bold: true
                                                        color: root.colFg
                                                        elide: Text.ElideRight
                                                    }

                                                    Text {
                                                        Layout.fillWidth: true
                                                        text: modelData.sub
                                                        font.pixelSize: 9
                                                        color: modelData.accent
                                                        elide: Text.ElideRight
                                                    }
                                                }
                                            }

                                            MouseArea {
                                                id: tileMouse
                                                anchors.fill: parent
                                                hoverEnabled: true
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: {
                                                    root.runCmd(["bash", "-c", modelData.cmd + " & disown"]);
                                                    startMenuPopup.visible = false;
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
                anchor.rect.y: root.isBottomBar ? 0 : 46
                anchor.rect.width: 320
                anchor.rect.height: 0
                anchor.edges: root.isBottomBar ? Edges.Top : Edges.Bottom
                anchor.gravity: root.isBottomBar ? Edges.Top : Edges.Bottom
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
                                        color: itemMouse.containsMouse ? root.colBgAlt : (modelData.is_active ? root.withAlpha(root.colAccent, 0.20) : root.colBgAlt)
                                        border.color: modelData.is_active ? root.colAccent : (modelData.is_minimized ? root.withAlpha(root.colGold, 0.55) : root.colBorder)
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
                            property bool isGroupPinned: {
                                if (!groupMenuPopup.currentGroup || !root.pinnedApps) return false;
                                var cls = (groupMenuPopup.currentGroup.class || "").toLowerCase();
                                return root.pinnedApps.some(p => p.id === cls || p.cmd === cls || (p.name && p.name.toLowerCase() === cls));
                            }

                            visible: root.isFullSakura && groupMenuPopup.currentGroup
                            Layout.fillWidth: true
                            height: 28
                            radius: root.buttonRadius
                            color: pinToggleMouse.containsMouse ? (isGroupPinned ? (root.withAlpha(root.colRed, 0.20)) : (root.withAlpha(root.colAccent, 0.20))) : root.colBgAlt
                            border.color: pinToggleMouse.containsMouse ? (isGroupPinned ? root.colRed : root.colAccent) : root.colBorder
                            border.width: 1

                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 6
                                spacing: 8

                                Text {
                                    text: parent.parent.isGroupPinned ? "󰤲" : "󰤱"
                                    font.pixelSize: 14
                                    color: parent.parent.isGroupPinned ? root.colRed : root.colAccent
                                }

                                Text {
                                    text: (parent.parent.isGroupPinned ? "Unpin " : "Pin ") + (groupMenuPopup.currentGroup ? groupMenuPopup.currentGroup.class : "App") + (parent.parent.isGroupPinned ? " from Sakura Dock" : " to Sakura Dock")
                                    font.pixelSize: 10
                                    font.bold: true
                                    color: parent.parent.isGroupPinned && pinToggleMouse.containsMouse ? root.colRed : root.colFg
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
                                        if (parent.isGroupPinned) {
                                            root.runCmd(["python3", "/home/gallo/.config/hypr/scripts/pin_app.py", "remove", g.class.toLowerCase()]);
                                        } else {
                                            root.runCmd(["python3", "/home/gallo/.config/hypr/scripts/pin_app.py", "add", g.class.toLowerCase(), g.class, g.icon || g.class.toLowerCase(), g.class.toLowerCase()]);
                                        }
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
                anchor.rect.y: root.isBottomBar ? 0 : 46
                anchor.rect.width: 220
                anchor.rect.height: 0
                anchor.edges: root.isBottomBar ? Edges.Top : Edges.Bottom
                anchor.gravity: root.isBottomBar ? Edges.Top : Edges.Bottom
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
                            color: launchPinMouse.containsMouse ? (root.withAlpha(root.colAccent, 0.20)) : "transparent"

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
                                        root.runCmd(["bash", "-c", (pinnedMenuPopup.targetApp.cmd || pinnedMenuPopup.targetApp.id) + " & disown"]);
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
                            color: unpinMouse.containsMouse ? (root.withAlpha(root.colRed, 0.20)) : "transparent"

                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: 8
                                spacing: 6

                                Text { text: "󰤲"; font.pixelSize: 14; color: unpinMouse.containsMouse ? root.colRed : root.colAccent }
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

            // 2. CENTER ISLAND: Centered Taskbar in Cyber Sakura, or Digital Clock in Garchy Signature
            Rectangle {
                id: centerIsland
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: root.isFullSakura ? (centerTaskRow.implicitWidth + 24) : (clockLayout.implicitWidth + 36)
                color: root.isFullSakura ? "transparent" : root.colBg
                border.color: root.isFullSakura ? "transparent" : (clockArea.containsMouse ? root.colAccent : root.colBorder)
                border.width: root.isFullSakura ? 0 : 1.5
                radius: root.islandRadius

                // A. Centered Taskbar (When Cyber Sakura is active)
                Row {
                    id: centerTaskRow
                    visible: root.isFullSakura
                    anchors.centerIn: parent
                    spacing: 8

                    Repeater {
                        model: root.taskbarState.groups || []

                        Item {
                            id: centerAppItem
                            property var groupData: modelData
                            width: 42
                            height: 36

                            Rectangle {
                                anchors.fill: parent
                                radius: root.buttonRadius
                                color: groupData.is_active ? root.withAlpha(root.colAccent, 0.20) : (centerAppMouse.containsMouse ? (root.withAlpha(root.colAccent, 0.15)) : "transparent")
                                border.color: groupData.is_active ? root.colAccent : (centerAppMouse.containsMouse ? root.colAccent : "transparent")
                                border.width: groupData.is_active ? 1.5 : 1

                                Image {
                                    id: centerAppIcon
                                    anchors.centerIn: parent
                                    width: 24
                                    height: 24
                                    source: Quickshell.iconPath(groupData.icon)
                                    fillMode: Image.PreserveAspectFit
                                    opacity: groupData.is_minimized ? 0.5 : 1.0
                                    visible: status === Image.Ready
                                }

                                Text {
                                    anchors.centerIn: parent
                                    visible: centerAppIcon.status !== Image.Ready
                                    text: "󰖯"
                                    font.pixelSize: 20
                                    color: groupData.is_active ? root.colAccent : root.colFg
                                }

                                // Active underline indicator
                                Rectangle {
                                    anchors.bottom: parent.bottom
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    anchors.bottomMargin: 2
                                    width: groupData.is_active ? 20 : 5
                                    height: 3
                                    radius: Math.max(1.5, root.buttonRadius / 4)
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
                                    id: centerAppMouse
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    acceptedButtons: Qt.LeftButton | Qt.RightButton | Qt.MiddleButton

                                    onClicked: mouse => {
                                        if (mouse.button === Qt.RightButton || (mouse.button === Qt.LeftButton && groupData.windows.length > 1 && groupData.is_minimized)) {
                                            groupMenuPopup.currentGroup = groupData;
                                            var p = centerAppItem.mapToItem(null, 0, 0);
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

                // B. Digital Clock (When NOT Cyber Sakura / Garchy Signature)
                RowLayout {
                    id: clockLayout
                    visible: !root.isFullSakura
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
                    visible: !root.isFullSakura
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: datePopup.visible = !datePopup.visible
                }
            }

            // 📅 Center Clock Dropdown: Date & Calendar Menu
            PopupWindow {
                id: datePopup
                anchor.window: winMain
                anchor.rect.x: root.isFullSakura ? (winMain.width - 320) : Math.round((winMain.width - 280) / 2)
                anchor.rect.y: root.isBottomBar ? 0 : 46
                anchor.rect.width: 280
                anchor.rect.height: 0
                anchor.edges: root.isBottomBar ? Edges.Top : Edges.Bottom
                anchor.gravity: root.isBottomBar ? Edges.Top : Edges.Bottom
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
                            color: calBtnArea.containsMouse ? root.withAlpha(root.colAccent, 0.20) : root.colBgAlt
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

            // 3. RIGHT ISLAND: Volume, Gally AI, Theme, Clock (in Cyber Sakura), Down Arrow Menu
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
                    spacing: 8

                    // 🔊 Volume Pill
                    Rectangle {
                        height: 34
                        width: volRow.implicitWidth + 16
                        radius: root.buttonRadius
                        color: root.colBgAlt

                        RowLayout {
                            id: volRow
                            anchors.centerIn: parent
                            spacing: 6

                            Text {
                                text: root.isMuted ? "󰝟" : (root.volPercent > 50 ? "󰕾" : "󰖀")
                                font.pixelSize: 15
                                color: root.isMuted ? root.colRed : root.colAccent
                            }

                            Text {
                                text: root.volPercent + "%"
                                font.pixelSize: 13
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
                        width: 34
                        height: 34
                        radius: root.buttonRadius
                        color: aiMouse.containsMouse ? root.withAlpha(root.colAccent, 0.20) : "transparent"

                        Text {
                            anchors.centerIn: parent
                            text: root.isFullSakura ? "✨" : "󰚩"
                            font.pixelSize: 18
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
                        width: 34
                        height: 34
                        radius: root.buttonRadius
                        color: thmMouse.containsMouse ? root.withAlpha(root.colAccentAlt, 0.20) : "transparent"

                        Text {
                            anchors.centerIn: parent
                            text: "󰏘"
                            font.pixelSize: 18
                            color: root.colAccentAlt
                        }

                        MouseArea {
                            id: thmMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: root.runCmd(["bash", "-c", "~/.config/hypr/scripts/theme-switcher.sh"])
                        }
                    }

                    // 🌸 Cyber Sakura Digital Clock (Placed next to tray menu on right side)
                    Rectangle {
                        id: sakuraClockBtn
                        visible: root.isFullSakura
                        height: 34
                        width: sakuraClockRow.implicitWidth + 20
                        radius: 14
                        color: sakuraClockMouse.containsMouse ? (root.withAlpha(root.colAccent, 0.20)) : (root.withAlpha(root.colBgAlt, 0.55))
                        border.color: "transparent"
                        border.width: 0

                        RowLayout {
                            id: sakuraClockRow
                            anchors.centerIn: parent
                            spacing: 6

                            Text {
                                text: "🌸"
                                font.pixelSize: 13
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
                            id: sakuraClockMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: datePopup.visible = !datePopup.visible
                        }
                    }

                    // 󰅀 Down Arrow / Minimized Tray Menu
                    Rectangle {
                        id: trayBtn
                        width: 34
                        height: 34
                        radius: root.buttonRadius
                        color: trayArea.containsMouse || trayMenuPopup.visible ? (root.withAlpha(root.colAccent, 0.20)) : "transparent"
                        border.color: trayArea.containsMouse || trayMenuPopup.visible ? root.colAccent : "transparent"
                        border.width: 1

                        Text {
                            anchors.centerIn: parent
                            text: "󰅀"
                            font.pixelSize: 16
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
                anchor.rect.y: root.isBottomBar ? 0 : 46
                anchor.rect.width: 350
                anchor.rect.height: 0
                anchor.edges: root.isBottomBar ? Edges.Top : Edges.Bottom
                anchor.gravity: root.isBottomBar ? Edges.Top : Edges.Bottom
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
                                color: root.withAlpha(root.colGreen, 0.15)
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
                                color: gmMouse.containsMouse ? root.withAlpha(root.colAccent, 0.20) : root.colBgAlt
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
                                color: pavuMouse.containsMouse ? root.withAlpha(root.colAccent, 0.20) : root.colBgAlt
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
                                color: thmQMouse.containsMouse ? root.withAlpha(root.colAccentAlt, 0.20) : root.colBgAlt
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
                                    color: lckMouse.containsMouse ? root.withAlpha(root.colAccent, 0.20) : "transparent"

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
                                    color: rbtMouse.containsMouse ? root.withAlpha(root.colGold, 0.20) : "transparent"

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
                                    color: pwrMenuMouse.containsMouse ? root.withAlpha(root.colRed, 0.20) : "transparent"

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
            top: !root.isBottomBar
            bottom: root.isBottomBar
            left: true
            right: true
        }
        implicitHeight: root.barHeight
        color: "transparent"

        WlrLayershell.layer: WlrLayer.Top
        WlrLayershell.namespace: "garchy-shell"
        WlrLayershell.keyboardFocus: (secStartMenuPopup.visible ? WlrKeyboardFocus.Exclusive : WlrKeyboardFocus.None)
        exclusionMode: ExclusionMode.Auto

        Item {
            anchors.fill: parent
            anchors.topMargin: root.isBottomBar ? 5 : 4
            anchors.bottomMargin: root.isBottomBar ? 5 : 4
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

            // 1. LEFT ISLAND: Launcher, Pinned Apps, Workspaces 1-4
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
                        width: 36
                        height: 36
                        radius: root.buttonRadius
                        color: secLaunchArea.containsMouse ? root.withAlpha(root.colAccent, 0.20) : (root.isFullSakura ? "transparent" : root.colBgAlt)
                        border.color: secLaunchArea.containsMouse ? root.colAccent : (root.isFullSakura ? "transparent" : root.colBorder)
                        border.width: 1

                        Text {
                            anchors.centerIn: parent
                            text: root.isFullSakura ? "🌸" : "󰣇"
                            font.pixelSize: root.isFullSakura ? 19 : 20
                            color: root.colAccent
                        }

                        MouseArea {
                            id: secLaunchArea
                            anchors.fill: parent
                            hoverEnabled: true
                            acceptedButtons: Qt.LeftButton | Qt.RightButton
                            onClicked: mouse => {
                                if (mouse.button === Qt.LeftButton) {
                                    startMenuPopup.visible = !startMenuPopup.visible;
                                } else {
                                    root.runCmd(["bash", "-c", "~/.config/hypr/scripts/wallpaper-select.sh"]);
                                }
                            }
                        }
                    }

                    // 🌸 CYBER SAKURA PINNED QUICK-LAUNCH DOCK (With Emoticon Placeholders for Unpinned Slots)
                    Row {
                        id: secPinnedRow
                        visible: root.isFullSakura
                        spacing: 5
                        Layout.alignment: Qt.AlignVCenter

                        Repeater {
                            model: Math.max(root.pinnedDockCapacity, (root.pinnedApps ? root.pinnedApps.length : 0))

                            Rectangle {
                                id: secPinSlotItem
                                property int slotIndex: index
                                property bool isPinned: root.pinnedApps && slotIndex < root.pinnedApps.length
                                property var appData: isPinned ? root.pinnedApps[slotIndex] : null

                                property bool isRunning: {
                                    if (!isPinned || !appData || !root.taskbarState || !root.taskbarState.groups) return false;
                                    var pId = (appData.id || "").toLowerCase();
                                    var pCmd = (appData.cmd || "").toLowerCase();
                                    for (var i = 0; i < root.taskbarState.groups.length; i++) {
                                        var g = root.taskbarState.groups[i];
                                        var gId = (g.app_id || "").toLowerCase();
                                        var gClass = (g.wm_class || "").toLowerCase();
                                        if (gId.includes(pId) || gId.includes(pCmd) || gClass.includes(pId) || gClass.includes(pCmd)) return true;
                                    }
                                    return false;
                                }

                                width: 36
                                height: 36
                                radius: 10
                                color: isPinned 
                                    ? (secPinSlotMouse.containsMouse ? (root.withAlpha(root.colAccent, 0.20)) : (isRunning ? (root.colBgAlt || "#281b36") : "transparent"))
                                    : (secPinSlotMouse.containsMouse ? (root.withAlpha(root.colAccent, 0.15)) : (root.withAlpha(root.colBgAlt, 0.27)))
                                border.color: isPinned
                                    ? (isRunning ? (root.colAccent || "#f472b6") : (secPinSlotMouse.containsMouse ? (root.colAccent || "#f472b6") : (root.withAlpha(root.colAccentAlt, 0.27))))
                                    : (secPinSlotMouse.containsMouse ? (root.colAccent || "#f472b6") : (root.withAlpha(root.colBorder, 0.27)))
                                border.width: isPinned ? (isRunning ? 1.5 : 1) : 1

                                // 1. If Pinned: Application Desktop Icon
                                Image {
                                    id: secPinSlotIcon
                                    visible: isPinned
                                    anchors.centerIn: parent
                                    width: 22
                                    height: 22
                                    source: isPinned ? Quickshell.iconPath(appData.icon || appData.id) : ""
                                    fillMode: Image.PreserveAspectFit
                                }

                                // 2. If Pinned but icon failed to load: Pin Glyph
                                Text {
                                    visible: isPinned && secPinSlotIcon.status !== Image.Ready
                                    anchors.centerIn: parent
                                    text: "󰤱"
                                    font.pixelSize: 16
                                    color: root.colAccent
                                }

                                // 3. If Unpinned Placeholder: Pastel Pin Glyph
                                Text {
                                    visible: !isPinned
                                    anchors.centerIn: parent
                                    text: "󰤱"
                                    font.pixelSize: 16
                                    color: root.colAccent
                                    opacity: secPinSlotMouse.containsMouse ? 1.0 : 0.4
                                }

                                // Subtle Blossom Glow Dot when Running
                                Rectangle {
                                    visible: isPinned && isRunning
                                    width: 4
                                    height: 4
                                    radius: 2
                                    color: root.colAccent || "#f5bde6"
                                    anchors.bottom: parent.bottom
                                    anchors.bottomMargin: 2
                                    anchors.horizontalCenter: parent.horizontalCenter
                                }

                                MouseArea {
                                    id: secPinSlotMouse
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    acceptedButtons: Qt.LeftButton | Qt.RightButton
                                    onClicked: mouse => {
                                        if (isPinned) {
                                            if (mouse.button === Qt.LeftButton) {
                                                var foundAddr = "";
                                                if (root.taskbarState && root.taskbarState.groups) {
                                                    var pId = (appData.id || "").toLowerCase();
                                                    var pCmd = (appData.cmd || "").toLowerCase();
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
                                                    root.runCmd(["bash", "-c", (appData.cmd || appData.id) + " & disown"]);
                                                }
                                            } else if (mouse.button === Qt.RightButton) {
                                                secPinnedMenuPopup.targetApp = appData;
                                                secPinnedMenuPopup.visible = true;
                                            }
                                        } else {
                                            // Unpinned placeholder slot: Open Launchpad
                                            startMenuPopup.visible = !startMenuPopup.visible;
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // Delicate Vertical Divider
                    Rectangle {
                        visible: root.isFullSakura
                        width: 1
                        height: 20
                        color: root.withAlpha(root.colAccentAlt, 0.27)
                        Layout.alignment: Qt.AlignVCenter
                    }

                    // 🔢 Workspaces (1 2 3 4) for Secondary Monitor
                    Rectangle {
                        height: 36
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

                                    width: 26
                                    height: 26
                                    radius: root.buttonRadius
                                    color: isWsActive ? root.colAccent : (secWsMouse.containsMouse ? (root.withAlpha(root.colAccent, 0.20)) : "transparent")
                                    border.color: isWsActive ? root.colAccent : (secWsMouse.containsMouse ? root.colAccent : "transparent")
                                    border.width: 1

                                    Text {
                                        anchors.centerIn: parent
                                        text: modelData
                                        font.pixelSize: 13
                                        font.bold: true
                                        color: isWsActive ? "#181222" : (secWsMouse.containsMouse ? root.colAccent : root.colFgMuted)
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

                    // 💻 Icon-Only Grouped Taskbar for Secondary Monitor (When NOT Cyber Sakura)
                    RowLayout {
                        visible: !root.isFullSakura
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
                                color: groupData.is_active ? root.withAlpha(root.colAccent, 0.15) : (secAppMouse.containsMouse ? (root.withAlpha(root.colAccent, 0.15)) : "transparent")
                                border.color: groupData.is_active ? root.colAccent : (secAppMouse.containsMouse ? root.colAccent : "transparent")
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


            // ========================================================
            // 🪟 WINDOWS 10 STYLE START MENU POPUP (CYBER SAKURA)
            // ========================================================
            PopupWindow {
                id: secStartMenuPopup
                anchor.window: winSec
                anchor.rect.x: 8
                anchor.rect.y: root.isBottomBar ? 0 : 54
                anchor.rect.width: 720
                anchor.rect.height: 0
                anchor.edges: root.isBottomBar ? Edges.Top : Edges.Bottom
                anchor.gravity: root.isBottomBar ? Edges.Top : Edges.Bottom
                implicitWidth: 720
                implicitHeight: 560
                color: "transparent"
                visible: false

                Timer {
                    id: secSearchFocusTimer
                    interval: 60
                    repeat: false
                    onTriggered: {
                        secSearchField.forceActiveFocus();
                    }
                }

                onVisibleChanged: {
                    if (visible) {
                        secSearchField.text = "";
                        secSearchFocusTimer.restart();
                        Qt.callLater(function() { secSearchField.forceActiveFocus(); });
                    }
                }

                Rectangle {
                    focus: true
                    Keys.onEscapePressed: secStartMenuPopup.visible = false
                    anchors.fill: parent
                    radius: root.popupRadius
                    color: root.colBg
                    border.color: root.colAccent
                    border.width: 1.5
                    clip: true

                    RowLayout {
                        anchors.fill: parent
                        spacing: 0

                        // 1. LEFT NARROW RAIL (50px)
                        Rectangle {
                            Layout.fillHeight: true
                            Layout.preferredWidth: 50
                            color: root.withAlpha(root.colBgAlt, 0.4)
                            border.color: root.withAlpha(root.colBorder, 0.2)
                            border.width: 1

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 6
                                spacing: 8

                                // Top Hamburger Menu
                                Rectangle {
                                    Layout.preferredWidth: 38
                                    Layout.preferredHeight: 38
                                    radius: root.buttonRadius
                                    color: secNavHamMouse.containsMouse ? root.withAlpha(root.colAccent, 0.20) : "transparent"
                                    border.color: secNavHamMouse.containsMouse ? root.colAccent : "transparent"
                                    border.width: 1

                                    Text {
                                        anchors.centerIn: parent
                                        text: "󰍜"
                                        font.pixelSize: 18
                                        color: root.colAccent
                                    }

                                    MouseArea {
                                        id: secNavHamMouse
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                    }
                                }

                                Item { Layout.fillHeight: true }

                                // User Avatar
                                Rectangle {
                                    Layout.preferredWidth: 38
                                    Layout.preferredHeight: 38
                                    radius: root.buttonRadius
                                    color: secNavUserMouse.containsMouse ? root.withAlpha(root.colAccent, 0.20) : "transparent"
                                    border.color: secNavUserMouse.containsMouse ? root.colAccent : "transparent"
                                    border.width: 1

                                    Text {
                                        anchors.centerIn: parent
                                        text: "󰀉"
                                        font.pixelSize: 18
                                        color: root.colFg
                                    }

                                    MouseArea {
                                        id: secNavUserMouse
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                    }
                                }

                                // Files Shortcut (Thunar)
                                Rectangle {
                                    Layout.preferredWidth: 38
                                    Layout.preferredHeight: 38
                                    radius: root.buttonRadius
                                    color: secNavFilesMouse.containsMouse ? root.withAlpha(root.colAccent, 0.20) : "transparent"
                                    border.color: secNavFilesMouse.containsMouse ? root.colAccent : "transparent"
                                    border.width: 1

                                    Text {
                                        anchors.centerIn: parent
                                        text: "󰉋"
                                        font.pixelSize: 18
                                        color: root.colAccentAlt
                                    }

                                    MouseArea {
                                        id: secNavFilesMouse
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: {
                                            root.runCmd(["bash", "-c", "thunar & disown"]);
                                            secStartMenuPopup.visible = false;
                                        }
                                    }
                                }

                                // Settings Shortcut
                                Rectangle {
                                    Layout.preferredWidth: 38
                                    Layout.preferredHeight: 38
                                    radius: root.buttonRadius
                                    color: secNavSetMouse.containsMouse ? root.withAlpha(root.colAccent, 0.20) : "transparent"
                                    border.color: secNavSetMouse.containsMouse ? root.colAccent : "transparent"
                                    border.width: 1

                                    Text {
                                        anchors.centerIn: parent
                                        text: "󰒓"
                                        font.pixelSize: 18
                                        color: root.colGold
                                    }

                                    MouseArea {
                                        id: secNavSetMouse
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: {
                                            root.runCmd(["bash", "-c", "xfce4-settings-manager & disown"]);
                                            secStartMenuPopup.visible = false;
                                        }
                                    }
                                }

                                // Lock Screen
                                Rectangle {
                                    Layout.preferredWidth: 38
                                    Layout.preferredHeight: 38
                                    radius: root.buttonRadius
                                    color: secNavLockMouse.containsMouse ? root.withAlpha(root.colAccent, 0.20) : "transparent"
                                    border.color: secNavLockMouse.containsMouse ? root.colAccent : "transparent"
                                    border.width: 1

                                    Text {
                                        anchors.centerIn: parent
                                        text: "󰌾"
                                        font.pixelSize: 18
                                        color: root.colAccent
                                    }

                                    MouseArea {
                                        id: secNavLockMouse
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: {
                                            root.runCmd(["bash", "-c", "~/.config/hypr/scripts/dual-desktop.sh lock & disown"]);
                                            secStartMenuPopup.visible = false;
                                        }
                                    }
                                }

                                // Power Button
                                Rectangle {
                                    Layout.preferredWidth: 38
                                    Layout.preferredHeight: 38
                                    radius: root.buttonRadius
                                    color: secNavPwrMouse.containsMouse ? root.withAlpha(root.colRed, 0.25) : "transparent"
                                    border.color: secNavPwrMouse.containsMouse ? root.colRed : "transparent"
                                    border.width: 1

                                    Text {
                                        anchors.centerIn: parent
                                        text: "󰐥"
                                        font.pixelSize: 18
                                        color: secNavPwrMouse.containsMouse ? root.colRed : root.colFgMuted
                                    }

                                    MouseArea {
                                        id: secNavPwrMouse
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: {
                                            root.runCmd(["bash", "-c", "wlogout & disown"]);
                                            secStartMenuPopup.visible = false;
                                        }
                                    }
                                }
                            }
                        }

                        // 2. MIDDLE COLUMN: ALL APPS & REAL-TIME SEARCH (290px)
                        Rectangle {
                            Layout.fillHeight: true
                            Layout.preferredWidth: 290
                            color: "transparent"

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 14
                                spacing: 10

                                // Search Box
                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 38
                                    radius: 8
                                    color: root.colBgAlt
                                    border.color: secSearchField.activeFocus ? root.colAccent : root.withAlpha(root.colBorder, 0.4)
                                    border.width: secSearchField.activeFocus ? 1.5 : 1

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.margins: 8
                                        spacing: 8

                                        Text {
                                            text: "🔍"
                                            font.pixelSize: 13
                                            color: root.colAccent
                                        }

                                        TextInput {
                                            id: secSearchField
                                            Layout.fillWidth: true
                                            font.pixelSize: 12
                                            color: root.colFg
                                            clip: true
                                            selectByMouse: true
                                            focus: true
                                            property string placeholder: "Type here to search apps..."

                                            Keys.onEscapePressed: secStartMenuPopup.visible = false
                                            onAccepted: {
                                                if (secAppListView.count > 0 && secAppListView.model.length > 0) {
                                                    var topApp = secAppListView.model[0];
                                                    if (topApp && topApp.exec) {
                                                        root.runCmd(["bash", "-c", topApp.exec + " & disown"]);
                                                        secStartMenuPopup.visible = false;
                                                    }
                                                }
                                            }

                                            Text {
                                                visible: secSearchField.text === "" && !secSearchField.activeFocus
                                                text: secSearchField.placeholder
                                                font.pixelSize: 12
                                                color: root.colFgMuted
                                                anchors.fill: parent
                                                verticalAlignment: Text.AlignVCenter
                                            }
                                        }

                                        // Clear button
                                        Text {
                                            visible: secSearchField.text !== ""
                                            text: "✕"
                                            font.pixelSize: 11
                                            font.bold: true
                                            color: secClearSearchMouse.containsMouse ? root.colRed : root.colFgMuted

                                            MouseArea {
                                                id: secClearSearchMouse
                                                anchors.fill: parent
                                                hoverEnabled: true
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: {
                                                    secSearchField.text = "";
                                                    secSearchField.forceActiveFocus();
                                                }
                                            }
                                        }
                                    }
                                }

                                // Apps Header
                                RowLayout {
                                    Layout.fillWidth: true
                                    Text {
                                        text: secSearchField.text === "" ? "All Applications" : "Search Results"
                                        font.pixelSize: 11
                                        font.bold: true
                                        color: root.colAccent
                                    }
                                    Item { Layout.fillWidth: true }
                                    Text {
                                        text: secAppListView.count + " apps"
                                        font.pixelSize: 10
                                        color: root.colFgMuted
                                    }
                                }

                                // Scrollable App List
                                ListView {
                                    id: secAppListView
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    clip: true
                                    spacing: 4
                                    boundsBehavior: Flickable.StopAtBounds

                                    model: {
                                        var q = secSearchField.text.trim().toLowerCase();
                                        if (!q || q === "") return root.allAppsList;
                                        return (root.allAppsList || []).filter(function(a) {
                                            return (a.name && a.name.toLowerCase().includes(q)) ||
                                                   (a.comment && a.comment.toLowerCase().includes(q)) ||
                                                   (a.exec && a.exec.toLowerCase().includes(q));
                                        });
                                    }

                                    delegate: Rectangle {
                                        width: secAppListView.width
                                        height: 38
                                        radius: 6
                                        color: secAppItemMouse.containsMouse ? root.withAlpha(root.colAccent, 0.20) : "transparent"
                                        border.color: secAppItemMouse.containsMouse ? root.colAccent : "transparent"
                                        border.width: 1

                                        RowLayout {
                                            anchors.fill: parent
                                            anchors.margins: 6
                                            spacing: 10

                                            Image {
                                                id: secAppImg
                                                Layout.preferredWidth: 24
                                                Layout.preferredHeight: 24
                                                source: modelData.icon_path ? ("file://" + modelData.icon_path) : (Quickshell.iconPath(modelData.icon) || "")
                                                fillMode: Image.PreserveAspectFit
                                                visible: status === Image.Ready
                                            }

                                            Text {
                                                visible: !secAppImg.visible
                                                Layout.preferredWidth: 24
                                                Layout.preferredHeight: 24
                                                horizontalAlignment: Text.AlignHCenter
                                                verticalAlignment: Text.AlignVCenter
                                                text: modelData.glyph || "󰀻"
                                                font.pixelSize: 18
                                                color: root.colAccent
                                            }

                                            ColumnLayout {
                                                Layout.fillWidth: true
                                                spacing: 1

                                                Text {
                                                    Layout.fillWidth: true
                                                    text: modelData.name
                                                    font.pixelSize: 12
                                                    font.bold: true
                                                    color: root.colFg
                                                    elide: Text.ElideRight
                                                }

                                                Text {
                                                    visible: modelData.comment !== ""
                                                    Layout.fillWidth: true
                                                    text: modelData.comment || modelData.exec || ""
                                                    font.pixelSize: 9
                                                    color: root.colFgMuted
                                                    elide: Text.ElideRight
                                                }
                                            }
                                        }

                                        MouseArea {
                                            id: secAppItemMouse
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            acceptedButtons: Qt.LeftButton | Qt.RightButton
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: mouse => {
                                                if (mouse.button === Qt.LeftButton) {
                                                    root.runCmd(["bash", "-c", modelData.exec + " & disown"]);
                                                    secStartMenuPopup.visible = false;
                                                } else {
                                                    root.runCmd(["python3", "/home/gallo/.config/hypr/scripts/pin_app.py", "add", modelData.exec, modelData.name, modelData.icon]);
                                                    secStartMenuPopup.visible = false;
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }

                        // Divider
                        Rectangle {
                            Layout.fillHeight: true
                            Layout.preferredWidth: 1
                            color: root.withAlpha(root.colBorder, 0.3)
                        }

                        // 3. RIGHT COLUMN: WINDOWS 10 LIVE TILES / PINNED MATRIX (370px)
                        Rectangle {
                            Layout.fillHeight: true
                            Layout.fillWidth: true
                            color: "transparent"

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 14
                                spacing: 12

                                // Header
                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 8

                                    Text {
                                        text: root.isFullSakura ? "🌸 Cyber Sakura Hub" : "󰣇 Life at a glance"
                                        font.pixelSize: 14
                                        font.bold: true
                                        color: root.colFg
                                    }

                                    Item { Layout.fillWidth: true }

                                    Text {
                                        text: "Pinned Tiles"
                                        font.pixelSize: 11
                                        font.bold: true
                                        color: root.colAccent
                                    }
                                }

                                // 2x5 Grid of Windows 10 Live Tiles
                                GridLayout {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    columns: 2
                                    rowSpacing: 10
                                    columnSpacing: 10

                                    Repeater {
                                        model: [
                                            { name: "Brave Browser", sub: "Web Explorer", icon: "brave", icon_path: "/home/gallo/.local/share/icons/Papirus/24x24/apps/brave.svg", glyph: "󰖟", cmd: "brave", accent: root.colAccent },
                                            { name: "Kitty Terminal", sub: "144Hz CLI", icon: "kitty", icon_path: "/usr/share/icons/hicolor/scalable/apps/kitty.svg", glyph: "󰄛", cmd: "kitty", accent: root.colAccentAlt },
                                            { name: "Visual Studio Code", sub: "Code Editor", icon: "code", icon_path: "/home/gallo/.local/share/icons/Papirus/24x24/apps/code.svg", glyph: "󰨞", cmd: "code", accent: root.colAccent },
                                            { name: "Thunar Files", sub: "File System", icon: "thunar", icon_path: "/home/gallo/.local/share/icons/Papirus/24x24/apps/thunar.svg", glyph: "󰉋", cmd: "thunar", accent: root.colGold },
                                            { name: "Steam Games", sub: "Gaming Hub", icon: "steam", icon_path: "/usr/share/icons/hicolor/48x48/apps/steam.png", glyph: "󰓓", cmd: "steam", accent: root.colAccentAlt },
                                            { name: "Spotify Music", sub: "Audio Stream", icon: "spotify", icon_path: "/home/gallo/.local/share/icons/Papirus/24x24/apps/spotify.svg", glyph: "󰓇", cmd: "spotify", accent: root.colAccent },
                                            { name: "Gally AI Copilot", sub: "AI Assistant", icon: "help-browser", icon_path: "/usr/share/icons/AdwaitaLegacy/48x48/legacy/help-browser.png", glyph: "󰚩", cmd: "python3 ~/.config/hypr/scripts/gally-ai-hud.py", accent: root.colGold },
                                            { name: "Theme Gallery", sub: "Style Switcher", icon: "preferences-desktop-theme", icon_path: "/usr/share/icons/AdwaitaLegacy/48x48/legacy/preferences-desktop-theme.png", glyph: "󰏘", cmd: "~/.config/hypr/scripts/theme-switcher.sh", accent: root.colAccentAlt },
                                            { name: "Wallpapers", sub: "Backgrounds", icon: "preferences-desktop-wallpaper", icon_path: "/usr/share/icons/AdwaitaLegacy/48x48/legacy/preferences-desktop-wallpaper.png", glyph: "󰸉", cmd: "~/.config/hypr/scripts/wallpaper-select.sh", accent: root.colAccent },
                                            { name: "System Monitor", sub: "Hardware & BTOP", icon: "btop", icon_path: "/usr/share/icons/hicolor/scalable/apps/btop.svg", glyph: "󰍛", cmd: "kitty -e btop", accent: root.colAccentAlt }
                                        ]

                                        Rectangle {
                                            Layout.fillWidth: true
                                            Layout.fillHeight: true
                                            radius: 8
                                            color: secTileMouse.containsMouse ? root.withAlpha(modelData.accent, 0.22) : root.colBgAlt
                                            border.color: secTileMouse.containsMouse ? modelData.accent : root.withAlpha(root.colBorder, 0.35)
                                            border.width: secTileMouse.containsMouse ? 1.5 : 1

                                            RowLayout {
                                                anchors.fill: parent
                                                anchors.margins: 10
                                                spacing: 10

                                                Image {
                                                    id: secTileImg
                                                    Layout.preferredWidth: 32
                                                    Layout.preferredHeight: 32
                                                    source: modelData.icon_path ? ("file://" + modelData.icon_path) : (Quickshell.iconPath(modelData.icon) || "")
                                                    fillMode: Image.PreserveAspectFit
                                                    visible: status === Image.Ready
                                                }

                                                Text {
                                                    visible: !secTileImg.visible
                                                    Layout.preferredWidth: 32
                                                    Layout.preferredHeight: 32
                                                    horizontalAlignment: Text.AlignHCenter
                                                    verticalAlignment: Text.AlignVCenter
                                                    text: modelData.glyph || "󰀻"
                                                    font.pixelSize: 24
                                                    color: modelData.accent
                                                }

                                                ColumnLayout {
                                                    Layout.fillWidth: true
                                                    spacing: 2

                                                    Text {
                                                        Layout.fillWidth: true
                                                        text: modelData.name
                                                        font.pixelSize: 11
                                                        font.bold: true
                                                        color: root.colFg
                                                        elide: Text.ElideRight
                                                    }

                                                    Text {
                                                        Layout.fillWidth: true
                                                        text: modelData.sub
                                                        font.pixelSize: 9
                                                        color: modelData.accent
                                                        elide: Text.ElideRight
                                                    }
                                                }
                                            }

                                            MouseArea {
                                                id: secTileMouse
                                                anchors.fill: parent
                                                hoverEnabled: true
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: {
                                                    root.runCmd(["bash", "-c", modelData.cmd + " & disown"]);
                                                    secStartMenuPopup.visible = false;
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

            // 📂 Secondary Screen Multi-Window Popup (Right-Click Selection)
            PopupWindow {
                id: secGroupMenuPopup
                property var currentGroup: null

                anchor.window: winSec
                anchor.rect.x: 120
                anchor.rect.y: root.isBottomBar ? 0 : 46
                anchor.rect.width: 320
                anchor.rect.height: 0
                anchor.edges: root.isBottomBar ? Edges.Top : Edges.Bottom
                anchor.gravity: root.isBottomBar ? Edges.Top : Edges.Bottom
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
                                        color: secItemMouse.containsMouse ? root.colBgAlt : (modelData.is_active ? root.withAlpha(root.colAccent, 0.20) : root.colBgAlt)
                                        border.color: modelData.is_active ? root.colAccent : (modelData.is_minimized ? root.withAlpha(root.colGold, 0.55) : root.colBorder)
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
                            property bool isGroupPinned: {
                                if (!secGroupMenuPopup.currentGroup || !root.pinnedApps) return false;
                                var cls = (secGroupMenuPopup.currentGroup.class || "").toLowerCase();
                                return root.pinnedApps.some(p => p.id === cls || p.cmd === cls || (p.name && p.name.toLowerCase() === cls));
                            }

                            visible: root.isFullSakura && secGroupMenuPopup.currentGroup
                            Layout.fillWidth: true
                            height: 28
                            radius: root.buttonRadius
                            color: secPinToggleMouse.containsMouse ? (isGroupPinned ? (root.withAlpha(root.colRed, 0.20)) : (root.withAlpha(root.colAccent, 0.20))) : root.colBgAlt
                            border.color: secPinToggleMouse.containsMouse ? (isGroupPinned ? root.colRed : root.colAccent) : root.colBorder
                            border.width: 1

                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 6
                                spacing: 8

                                Text {
                                    text: parent.parent.isGroupPinned ? "󰤲" : "󰤱"
                                    font.pixelSize: 14
                                    color: parent.parent.isGroupPinned ? root.colRed : root.colAccent
                                }

                                Text {
                                    text: (parent.parent.isGroupPinned ? "Unpin " : "Pin ") + (secGroupMenuPopup.currentGroup ? secGroupMenuPopup.currentGroup.class : "App") + (parent.parent.isGroupPinned ? " from Sakura Dock" : " to Sakura Dock")
                                    font.pixelSize: 10
                                    font.bold: true
                                    color: parent.parent.isGroupPinned && secPinToggleMouse.containsMouse ? root.colRed : root.colFg
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
                                        if (parent.isGroupPinned) {
                                            root.runCmd(["python3", "/home/gallo/.config/hypr/scripts/pin_app.py", "remove", g.class.toLowerCase()]);
                                        } else {
                                            root.runCmd(["python3", "/home/gallo/.config/hypr/scripts/pin_app.py", "add", g.class.toLowerCase(), g.class, g.icon || g.class.toLowerCase(), g.class.toLowerCase()]);
                                        }
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
                anchor.rect.y: root.isBottomBar ? 0 : 46
                anchor.rect.width: 220
                anchor.rect.height: 0
                anchor.edges: root.isBottomBar ? Edges.Top : Edges.Bottom
                anchor.gravity: root.isBottomBar ? Edges.Top : Edges.Bottom
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
                            color: secLaunchPinMouse.containsMouse ? (root.withAlpha(root.colAccent, 0.20)) : "transparent"

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
                                        root.runCmd(["bash", "-c", (secPinnedMenuPopup.targetApp.cmd || secPinnedMenuPopup.targetApp.id) + " & disown"]);
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
                            color: secUnpinMouse.containsMouse ? (root.withAlpha(root.colRed, 0.20)) : "transparent"

                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: 8
                                spacing: 6

                                Text { text: "󰤲"; font.pixelSize: 14; color: secUnpinMouse.containsMouse ? root.colRed : root.colAccent }
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

            // 2. CENTER ISLAND: Centered Taskbar in Cyber Sakura, or Digital Clock in Garchy Signature
            Rectangle {
                id: secCenterIsland
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: root.isFullSakura ? (secCenterTaskRow.implicitWidth + 24) : (secClockLayout.implicitWidth + 36)
                color: root.isFullSakura ? "transparent" : root.colBg
                border.color: root.isFullSakura ? "transparent" : (secClockArea.containsMouse ? root.colAccent : root.colBorder)
                border.width: root.isFullSakura ? 0 : 1.5
                radius: root.islandRadius

                // A. Centered Taskbar for Secondary Monitor (When Cyber Sakura is active)
                Row {
                    id: secCenterTaskRow
                    visible: root.isFullSakura
                    anchors.centerIn: parent
                    spacing: 8

                    Repeater {
                        model: root.taskbarState.groups || []

                        Item {
                            id: secCenterAppItem
                            property var groupData: modelData
                            width: 42
                            height: 36

                            Rectangle {
                                anchors.fill: parent
                                radius: root.buttonRadius
                                color: groupData.is_active ? root.withAlpha(root.colAccent, 0.20) : (secCenterAppMouse.containsMouse ? (root.withAlpha(root.colAccent, 0.15)) : "transparent")
                                border.color: groupData.is_active ? root.colAccent : (secCenterAppMouse.containsMouse ? root.colAccent : "transparent")
                                border.width: groupData.is_active ? 1.5 : 1

                                Image {
                                    id: secCenterAppIcon
                                    anchors.centerIn: parent
                                    width: 24
                                    height: 24
                                    source: Quickshell.iconPath(groupData.icon)
                                    fillMode: Image.PreserveAspectFit
                                    opacity: groupData.is_minimized ? 0.5 : 1.0
                                    visible: status === Image.Ready
                                }

                                Text {
                                    anchors.centerIn: parent
                                    visible: secCenterAppIcon.status !== Image.Ready
                                    text: "󰖯"
                                    font.pixelSize: 20
                                    color: groupData.is_active ? root.colAccent : root.colFg
                                }

                                // Active underline indicator
                                Rectangle {
                                    anchors.bottom: parent.bottom
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    anchors.bottomMargin: 2
                                    width: groupData.is_active ? 20 : 5
                                    height: 3
                                    radius: Math.max(1.5, root.buttonRadius / 4)
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
                                    id: secCenterAppMouse
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    acceptedButtons: Qt.LeftButton | Qt.RightButton | Qt.MiddleButton

                                    onClicked: mouse => {
                                        if (mouse.button === Qt.RightButton || (mouse.button === Qt.LeftButton && groupData.windows.length > 1 && groupData.is_minimized)) {
                                            secGroupMenuPopup.currentGroup = groupData;
                                            var p = secCenterAppItem.mapToItem(null, 0, 0);
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

                // B. Digital Clock (When NOT in Cyber Sakura / Garchy Signature)
                RowLayout {
                    id: secClockLayout
                    visible: !root.isFullSakura
                    anchors.centerIn: parent

                    Text {
                        text: root.timeStr
                        font.pixelSize: 14
                        font.bold: true
                        color: root.colFg
                    }
                }

                MouseArea {
                    id: secClockArea
                    visible: !root.isFullSakura
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: secDatePopup.visible = !secDatePopup.visible
                }
            }

            // 📅 Secondary Center Clock Dropdown: Date & Calendar Menu
            PopupWindow {
                id: secDatePopup
                anchor.window: winSec
                anchor.rect.x: root.isFullSakura ? (winSec.width - 320) : Math.round((winSec.width - 280) / 2)
                anchor.rect.y: root.isBottomBar ? 0 : 46
                anchor.rect.width: 280
                anchor.rect.height: 0
                anchor.edges: root.isBottomBar ? Edges.Top : Edges.Bottom
                anchor.gravity: root.isBottomBar ? Edges.Top : Edges.Bottom
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
                            color: secCalBtnArea.containsMouse ? root.withAlpha(root.colAccent, 0.20) : root.colBgAlt
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

            // 3. RIGHT ISLAND: Volume, Gally AI, Theme, Clock (in Cyber Sakura), Down Arrow Menu
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
                    spacing: 8

                    // 🔊 Volume Pill
                    Rectangle {
                        height: 34
                        width: secVolRow.implicitWidth + 16
                        radius: root.buttonRadius
                        color: root.colBgAlt

                        RowLayout {
                            id: secVolRow
                            anchors.centerIn: parent
                            spacing: 6

                            Text {
                                text: root.isMuted ? "󰝟" : (root.volPercent > 50 ? "󰕾" : "󰖀")
                                font.pixelSize: 15
                                color: root.isMuted ? root.colRed : root.colAccent
                            }

                            Text {
                                text: root.volPercent + "%"
                                font.pixelSize: 13
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
                        width: 34
                        height: 34
                        radius: root.buttonRadius
                        color: secAiMouse.containsMouse ? root.withAlpha(root.colAccent, 0.20) : "transparent"

                        Text {
                            anchors.centerIn: parent
                            text: root.isFullSakura ? "✨" : "󰚩"
                            font.pixelSize: 18
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
                        width: 34
                        height: 34
                        radius: root.buttonRadius
                        color: secThmMouse.containsMouse ? root.withAlpha(root.colAccentAlt, 0.20) : "transparent"

                        Text {
                            anchors.centerIn: parent
                            text: "󰏘"
                            font.pixelSize: 18
                            color: root.colAccentAlt
                        }

                        MouseArea {
                            id: secThmMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: root.runCmd(["bash", "-c", "~/.config/hypr/scripts/theme-switcher.sh"])
                        }
                    }

                    // 🌸 Cyber Sakura Digital Clock (Placed next to tray menu on right side)
                    Rectangle {
                        id: secSakuraClockBtn
                        visible: root.isFullSakura
                        height: 34
                        width: secSakuraClockRow.implicitWidth + 20
                        radius: 14
                        color: secSakuraClockMouse.containsMouse ? (root.withAlpha(root.colAccent, 0.20)) : (root.withAlpha(root.colBgAlt, 0.55))
                        border.color: "transparent"
                        border.width: 0

                        RowLayout {
                            id: secSakuraClockRow
                            anchors.centerIn: parent
                            spacing: 6

                            Text {
                                text: "🌸"
                                font.pixelSize: 13
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
                            id: secSakuraClockMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: secDatePopup.visible = !secDatePopup.visible
                        }
                    }

                    // 󰅀 Down Arrow / Minimized Tray Menu
                    Rectangle {
                        id: secTrayBtn
                        width: 34
                        height: 34
                        radius: root.buttonRadius
                        color: secTrayArea.containsMouse || secTrayMenuPopup.visible ? (root.withAlpha(root.colAccent, 0.20)) : "transparent"
                        border.color: secTrayArea.containsMouse || secTrayMenuPopup.visible ? root.colAccent : "transparent"
                        border.width: 1

                        Text {
                            anchors.centerIn: parent
                            text: "󰅀"
                            font.pixelSize: 16
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
                anchor.rect.y: root.isBottomBar ? 0 : 46
                anchor.rect.width: 350
                anchor.rect.height: 0
                anchor.edges: root.isBottomBar ? Edges.Top : Edges.Bottom
                anchor.gravity: root.isBottomBar ? Edges.Top : Edges.Bottom
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
                                color: root.withAlpha(root.colGreen, 0.15)
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
                                color: secGmMouse.containsMouse ? root.withAlpha(root.colAccent, 0.20) : root.colBgAlt
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
                                color: secPavuMouse.containsMouse ? root.withAlpha(root.colAccent, 0.20) : root.colBgAlt
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
                                color: secThmQMouse.containsMouse ? root.withAlpha(root.colAccentAlt, 0.20) : root.colBgAlt
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
                                    color: secLckMouse.containsMouse ? root.withAlpha(root.colAccent, 0.20) : "transparent"

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
                                    color: secRbtMouse.containsMouse ? root.withAlpha(root.colGold, 0.20) : "transparent"

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
                                    color: secPwrMenuMouse.containsMouse ? root.withAlpha(root.colRed, 0.20) : "transparent"

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
