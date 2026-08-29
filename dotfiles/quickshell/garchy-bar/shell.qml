import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import Quickshell
import Quickshell.Wayland
import Quickshell.Io

ShellRoot {
    id: root

        // =========================================================================
    // 🧠 GALLY AI CHAT STATE & HELPERS
    // =========================================================================
    property var chatHistory: []
    property string activeAiModel: "qwen2.5:0.5b"
    property bool isAiVoiceEnabled: true

    FileView {
        id: aiHistoryFile
        path: "/tmp/gally_chat_history.json"
        watchChanges: true
        onLoaded: {
            try { root.chatHistory = JSON.parse(text()); } catch(e){}
        }
        onFileChanged: {
            reload();
            try { root.chatHistory = JSON.parse(text()); } catch(e){}
        }
    }

    property int aiToggleCount: 0
    FileView {
        id: aiToggleWatcher
        path: "/tmp/garchy_ai_toggle.trigger"
        watchChanges: true
        onFileChanged: {
            reload();
            root.aiToggleCount += 1;
        }
    }

    function sendAiPrompt(p) {
        if (!p || !p.trim()) return;
        runCmd(["python3", "/home/gallo/.config/hypr/scripts/gally_chat_service.py", "send", p.trim()]);
    }

    function clearAiChat() {
        runCmd(["python3", "/home/gallo/.config/hypr/scripts/gally_chat_service.py", "clear"]);
    }

    function setAiModel(m) {
        root.activeAiModel = m;
        runCmd(["python3", "/home/gallo/.config/hypr/scripts/gally_chat_service.py", "set-model", m]);
    }

    function toggleAiVoice() {
        root.isAiVoiceEnabled = !root.isAiVoiceEnabled;
        runCmd(["python3", "/home/gallo/.config/hypr/scripts/gally_chat_service.py", "toggle-voice"]);
    }

// =========================================================================
    // 🎨 DYNAMIC THEME ENGINE & GARCHY 5-COLOR PALETTE
    // =========================================================================
    property string activeThemeId: "garchy_signature"
    property string layoutStyle: "garchy"
    property color colBg: "#C4080c16"
    property color colBgAlt: "#80121d33"
    property color colCard: "#660c1424"
    property color colFg: "#f1f5f9"
    property color colFgMuted: "#94a3b8"
    property color colAccent: "#38bdf8"
    property color colAccentAlt: "#3b82f6"
    property color colGold: "#fbbf24"
    property color colBorder: "#38bdf8"
    property color colRed: "#f43f5e"
    property color colGreen: "#10b981"

    property int themeRounding: 0
    property int islandWidth: 510
    property int islandRadius: 0
    property int buttonRadius: 0
    property int cardRadius: 0
    property int popupRadius: 0

    function withAlpha(c, a) {
        return Qt.rgba(c.r, c.g, c.b, a);
    }

    function applyTheme(t) {
        if (!t) return;
        if (t.id) activeThemeId = t.id;
        if (t.layout_style) layoutStyle = t.layout_style;
        if (t.bg) colBg = t.bg.length === 7 ? ("#C4" + t.bg.replace("#", "")) : t.bg;
        if (t.bg_alt || t.bg_card) colBgAlt = t.bg_alt || t.bg_card;
        if (t.bg_card) colCard = t.bg_card;
        if (t.fg) colFg = t.fg;
        if (t.fg_muted) colFgMuted = t.fg_muted;
        if (t.accent) colAccent = t.accent;
        if (t.accent_alt) colAccentAlt = t.accent_alt;
        if (t.gold) colGold = t.gold;
        if (t.border || t.border_col) colBorder = t.border || t.border_col;

        var r = (t.rounding !== undefined) ? parseInt(t.rounding) : 0;
        themeRounding = r;
        islandRadius = r;
        buttonRadius = r === 0 ? 0 : Math.max(2, r - 2);
        cardRadius = r === 0 ? 0 : Math.max(3, r - 2);
        popupRadius = r === 0 ? 0 : Math.max(4, r + 2);
    }

    FileView {
        id: themeFile
        path: "/home/gallo/.config/gally/active_theme.json"
        watchChanges: true
        onLoaded: { try { root.applyTheme(JSON.parse(text())); } catch(e){} }
        onFileChanged: { reload(); try { root.applyTheme(JSON.parse(text())); } catch(e){} }
    }

    // =========================================================================
    // ⏱️ TIME & DATE
    // =========================================================================
    property string timeStr: "00:00"
    property string secondsStr: "00"
    property string dateShortStr: "TODAY"
    property string fullDateStr: ""

    Timer {
        interval: 1000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: {
            var d = new Date();
            var h = String(d.getHours()).padStart(2, "0");
            var m = String(d.getMinutes()).padStart(2, "0");
            var s = String(d.getSeconds()).padStart(2, "0");
            root.timeStr = h + ":" + m;
            root.secondsStr = s;

            var days = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"];
            var months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];
            root.dateShortStr = days[d.getDay()] + ", " + months[d.getMonth()] + " " + d.getDate();

            var fullDays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
            var fullMonths = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
            root.fullDateStr = fullDays[d.getDay()] + ", " + fullMonths[d.getMonth()] + " " + d.getDate() + ", " + d.getFullYear();
        }
    }

    // =========================================================================
    // ⚡ HARDWARE TELEMETRY
    // =========================================================================
    property string cpuUsage: "0%"
    property string gpuUsage: "0%"
    property string ramUsage: "0%"
    property string gpuTemp: "45°C"

    FileView {
        id: telemetryFile
        path: "/tmp/garchy_telemetry.json"
        watchChanges: true
        onLoaded: {
            try {
                var d = JSON.parse(text());
                if (d.cpu) root.cpuUsage = d.cpu;
                if (d.gpu) root.gpuUsage = d.gpu;
                if (d.ram) root.ramUsage = d.ram;
                if (d.gpu_temp) root.gpuTemp = d.gpu_temp;
            } catch(e) {}
        }
        onFileChanged: { reload(); }
    }

    Timer {
        interval: 1200
        running: true
        repeat: true
        onTriggered: {
            telemetryFile.reload();
            try {
                var d = JSON.parse(telemetryFile.text());
                if (d.cpu) root.cpuUsage = d.cpu;
                if (d.gpu) root.gpuUsage = d.gpu;
                if (d.ram) root.ramUsage = d.ram;
                if (d.gpu_temp) root.gpuTemp = d.gpu_temp;
            } catch(e) {}
        }
    }

    // =========================================================================
    // 🎵 LIVE CAVA AUDIO SPECTRUM (PipeWire Streaming)
    // =========================================================================
    property var cavaBars: [3, 3, 3, 3, 3, 3, 3, 3, 3, 3]

    Process {
        id: cavaProc
        command: ["cava", "-p", "/home/gallo/.config/cava/garchy_bar.conf"]
        running: true
        stdout: SplitParser {
            onRead: data => {
                var p = data.trim().split(";");
                if (p.length >= 8) {
                    var arr = [];
                    for (var i = 0; i < Math.min(10, p.length); i++) {
                        var n = parseInt(p[i]);
                        arr.push(isNaN(n) ? 3 : Math.max(3, Math.min(22, n)));
                    }
                    root.cavaBars = arr;
                }
            }
        }
    }

    // =========================================================================
    // 🎛️ UNIFIED HUB STATE (MPRIS Media, Network, Bluetooth, Audio, Weather)
    // =========================================================================
    property var hubState: ({
        media: { available: false, player: "", status: "Stopped", title: "No Media", artist: "Offline", position: 0, length: 0, position_str: "0:00", length_str: "0:00", progress: 0.0 },
        network: { connected: true, type: "ethernet", name: "Wired", icon: "󰈀" },
        bluetooth: { powered: false, connected_device: "", icon: "󰂲" },
        audio: { volume: 50, muted: false, mic_volume: 100, mic_muted: false, default_sink: "", sinks: [] },
        toggles: { night_light: false, gamemode: false, dnd: false },
        weather: { temp: "+17°C", condition: "Overcast", icon: "🌤️", display: "🌤️ +17°C" }
    })

    FileView {
        id: hubFile
        path: "/tmp/garchy_hub_state.json"
        watchChanges: true
        onLoaded: { try { root.hubState = JSON.parse(text()); } catch(e){} }
        onFileChanged: { reload(); try { root.hubState = JSON.parse(text()); } catch(e){} }
    }

    Timer {
        interval: 1000
        running: true
        repeat: true
        onTriggered: {
            hubFile.reload();
            try { root.hubState = JSON.parse(hubFile.text()); } catch(e){}
        }
    }

    // =========================================================================
    // 🗔 HYPRLAND WINDOW STATE & APPLICATIONS
    // =========================================================================
    property var taskbarState: ({ groups: [], minimized_windows: [], active_addr: "", monitors: [] })
    property var allAppsList: []
    // Notification History State
    property var notifHistory: []

    FileView {
        id: notifHistoryFile
        path: "/tmp/garchy_notif_history.json"
        watchChanges: true
        onLoaded: { try { root.notifHistory = JSON.parse(text()); } catch(e){} }
        onFileChanged: { reload(); try { root.notifHistory = JSON.parse(text()); } catch(e){} }
    }

    property var pinnedApps: []

    Process {
        id: taskbarProc
        command: ["python3", "/home/gallo/.config/quickshell/garchy-bar/taskbar_service.py"]
        running: true
        stdout: SplitParser {
            onRead: data => {
                try {
                    var parsed = JSON.parse(data.trim());
                    if (parsed && parsed.groups !== undefined) root.taskbarState = parsed;
                } catch(e) {}
            }
        }
    }

    FileView {
        id: appsFile
        path: "/home/gallo/.cache/garchy_desktop_apps.json"
        watchChanges: true
        onLoaded: { try { root.allAppsList = JSON.parse(text()); } catch(e){} }
        onFileChanged: { reload(); try { root.allAppsList = JSON.parse(text()); } catch(e){} }
    }

    FileView {
        id: pinnedFile
        path: "/home/gallo/.config/gally/pinned_apps.json"
        watchChanges: true
        onLoaded: { try { root.pinnedApps = JSON.parse(text()); } catch(e){} }
        onFileChanged: { reload(); try { root.pinnedApps = JSON.parse(text()); } catch(e){} }
    }

    function runCmd(cmdList) {
        try {
            Qt.createQmlObject("import Quickshell; import Quickshell.Io; Process { running: true; command: " + JSON.stringify(cmdList) + "; onExited: destroy() }", root);
        } catch(e) {
            console.error("runCmd error:", e);
        }
    }

    function dispatchAction(action, addr) {
        runCmd(["python3", "/home/gallo/.config/quickshell/garchy-bar/taskbar_service.py", action, addr || ""]);
    }

    // =========================================================================
    // 🔊 FLOATING ON-SCREEN DISPLAY (OSD) EVENT LISTENER
    // =========================================================================
    property var osdEvent: ({ type: "volume", volume: 50, muted: false, timestamp: 0 })
    property bool osdVisible: false

    FileView {
        id: osdFile
        path: "/tmp/garchy_osd_event.json"
        watchChanges: true
        onLoaded: {
            try {
                root.osdEvent = JSON.parse(text());
                root.osdVisible = true;
                osdTimer.restart();
            } catch(e){}
        }
        onFileChanged: {
            reload();
            try {
                root.osdEvent = JSON.parse(text());
                root.osdVisible = true;
                osdTimer.restart();
            } catch(e){}
        }
    }

    Timer {
        id: osdTimer
        interval: 1800
        repeat: false
        onTriggered: root.osdVisible = false
    }

    // =========================================================================
    // 🖥️ MULTI-MONITOR TOP BARS (Variants for DP-2 & DP-1)
    // =========================================================================
    Variants {
        model: Quickshell.screens
        delegate: PanelWindow {
            id: barWin
            required property var modelData
            screen: modelData
            anchors {
                top: true
                left: true
                right: true
            }
            implicitHeight: 52
            color: "transparent"
            WlrLayershell.layer: WlrLayer.Top
            WlrLayershell.namespace: "garchy-bar"
            exclusionMode: ExclusionMode.Auto

            property bool isPrimary: modelData && (modelData.name === "DP-2")

            // Global Flyout Toggle Controller
            function toggleFlyout(target) {
                var wasVis = target.visible;
                if (typeof startMenuPopup !== "undefined") startMenuPopup.visible = false;
                if (typeof datePopup !== "undefined") datePopup.visible = false;
                if (typeof quickSettingsPopup !== "undefined") quickSettingsPopup.visible = false;
                if (typeof groupMenuPopup !== "undefined") groupMenuPopup.visible = false;
                if (typeof notifDrawerPopup !== "undefined") notifDrawerPopup.visible = false;
                if (typeof bentoOverlayPopup !== "undefined") bentoOverlayPopup.visible = false;
                if (typeof gallyAiPopup !== "undefined") gallyAiPopup.visible = false;
                target.visible = !wasVis;
            }

            Item {
                anchors.fill: parent

                // -------------------------------------------------------------
                // 1. LEFT ISLAND: Flagship Shield + Workspaces + Animated Taskbar (Equal Size)
                // -------------------------------------------------------------
                Rectangle {
                    id: leftIsland
                    anchors.left: parent.left
                    anchors.leftMargin: 20
                    anchors.verticalCenter: parent.verticalCenter
                    height: 42
                    width: root.islandWidth
                    radius: root.islandRadius
                    color: root.colBg
                    border.color: root.colBorder
                    border.width: 1.0

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 6
                        spacing: 8

                        // Flagship Shield Start Button (Toggles Caelestia Start Menu)
                        Rectangle {
                            width: 32
                            height: 30
                            radius: root.buttonRadius
                            color: startMenuPopup.visible ? root.colAccent : (startMouse.containsMouse ? root.withAlpha(root.colAccent, 0.25) : root.colBgAlt)
                            border.color: startMenuPopup.visible ? root.colAccent : (startMouse.containsMouse ? root.colAccent : root.withAlpha(root.colBorder, 0.4))
                            border.width: 1

                            Text {
                                anchors.centerIn: parent
                                text: "󰣇"
                                font.pixelSize: 18
                                color: startMenuPopup.visible ? "#080c16" : root.colAccent
                            }

                            MouseArea {
                                id: startMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    if (barWin.isPrimary) {
                                        barWin.toggleFlyout(startMenuPopup);
                                    } else {
                                        root.runCmd(["bash", "-c", "~/.config/hypr/scripts/launchpad.sh"]);
                                    }
                                }
                            }
                        }

                        // Sharp Square Workspaces [1] [2] [3] [4]
                        Row {
                            spacing: 3
                            Repeater {
                                model: [1, 2, 3, 4]
                                Rectangle {
                                    property int wsNum: modelData
                                    property bool isWsActive: {
                                        var mons = root.taskbarState.monitors || [];
                                        for (var i = 0; i < mons.length; i++) {
                                            if (mons[i].name === barWin.modelData.name) {
                                                var actId = mons[i].activeWorkspace ? mons[i].activeWorkspace.id : 1;
                                                return (Math.ceil(actId / 2) === wsNum) || (actId === wsNum);
                                            }
                                        }
                                        return wsNum === (barWin.isPrimary ? 1 : 2);
                                    }

                                    width: 25
                                    height: 28
                                    radius: root.buttonRadius
                                    color: isWsActive ? root.colAccent : (wsItemMouse.containsMouse ? root.withAlpha(root.colAccent, 0.20) : root.colBgAlt)
                                    border.color: isWsActive ? root.colAccent : (wsItemMouse.containsMouse ? root.colAccent : root.withAlpha(root.colBorder, 0.3))
                                    border.width: 1

                                    Text {
                                        anchors.centerIn: parent
                                        text: modelData
                                        font.family: "Orbitron"
                                        font.pixelSize: 11
                                        font.bold: true
                                        color: isWsActive ? "#080c16" : (wsItemMouse.containsMouse ? root.colAccent : root.colFgMuted)
                                    }

                                    MouseArea {
                                        id: wsItemMouse
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: root.runCmd(["bash", "-c", "~/.config/hypr/scripts/dual-desktop.sh switch " + modelData])
                                    }
                                }
                            }
                        }

                        // Divider
                        Rectangle {
                            width: 1
                            height: 16
                            color: root.withAlpha(root.colBorder, 0.35)
                        }

                        // Running Apps Taskbar with Fluid Minimize / Restore / Launch Animations
                        Item {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            clip: true

                            Row {
                                anchors.verticalCenter: parent.verticalCenter
                                spacing: 4

                                Repeater {
                                    model: barWin.isPrimary ? (root.taskbarState.groups || []) : []
                                    delegate: Rectangle {
                                        id: taskDelegate
                                        property var gData: modelData
                                        property bool isAct: gData.active
                                        property bool isPinned: gData.is_pinned
                                        property bool isRunning: gData.running

                                        height: 30
                                        width: Math.min(130, taskRow.implicitWidth + 14)
                                        radius: root.buttonRadius
                                        color: isAct ? root.withAlpha(root.colAccent, 0.22) : (taskM.containsMouse ? root.withAlpha(root.colAccent, 0.12) : root.colBgAlt)
                                        border.color: isAct ? root.colAccent : (taskM.containsMouse ? root.withAlpha(root.colBorder, 0.5) : root.withAlpha(root.colBorder, 0.25))
                                        border.width: 1
                                        clip: true

                                        RowLayout {
                                            id: taskRow
                                            anchors.centerIn: parent
                                            spacing: 5

                                            Image {
                                                Layout.preferredWidth: 16
                                                Layout.preferredHeight: 16
                                                sourceSize: Qt.size(16, 16)
                                                width: 16
                                                height: 16
                                                source: Quickshell.iconPath(gData.icon || gData.class || "application-default")
                                                fillMode: Image.PreserveAspectFit
                                                visible: status === Image.Ready
                                            }

                                            Text {
                                                text: gData.title || gData.class
                                                font.pixelSize: 11
                                                font.bold: isAct
                                                color: isAct ? root.colAccent : (taskM.containsMouse ? root.colFg : root.colFgMuted)
                                                elide: Text.ElideRight
                                                Layout.maximumWidth: 85
                                            }
                                        }

                                        MouseArea {
                                            id: taskM
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            acceptedButtons: Qt.LeftButton | Qt.RightButton
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: mouse => {
                                                if (mouse.button === Qt.RightButton || gData.count > 1) {
                                                    groupMenuPopup.currentGroup = gData;
                                                    barWin.toggleFlyout(groupMenuPopup);
                                                } else if (gData.count === 1) {
                                                    root.dispatchAction("toggle", gData.windows[0].address);
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                // -------------------------------------------------------------
                // 2. CENTER ISLAND: Dynamic Notch / Morphing Island (Equal Size)
                // -------------------------------------------------------------
                Rectangle {
                    id: centerIsland
                    property bool isMediaActive: barWin.isPrimary && root.hubState && root.hubState.media && (root.hubState.media.available || (root.hubState.media.title && root.hubState.media.title !== "No Media"))
                    property bool isGameActive: root.hubState && root.hubState.toggles && root.hubState.toggles.gamemode

                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    height: 42
                    width: root.islandWidth
                    radius: root.islandRadius
                    color: root.colBg
                    border.color: datePopup.visible ? root.colGold : (isGameActive ? root.colGold : (isMediaActive ? root.colAccentAlt : root.colBorder))
                    border.width: 1.0

                    // Background Click Area (Toggles Dynamic Notch Flyout)
                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            if (barWin.isPrimary) barWin.toggleFlyout(datePopup);
                        }
                    }

                    RowLayout {
                        id: centerLayout
                        anchors.centerIn: parent
                        spacing: 8

                        // Mode A: Dynamic Media Notch (Spinning Vinyl Disc + Track + Micro-Controls)
                        RowLayout {
                            visible: centerIsland.isMediaActive
                            spacing: 8

                            // 💿 Spinning Vinyl Record
                            Rectangle {
                                width: 24
                                height: 24
                                radius: 12
                                color: "#050811"
                                border.color: root.colGold
                                border.width: 1
                                clip: true

                                Text {
                                    anchors.centerIn: parent
                                    text: "💿"
                                    font.pixelSize: 15
                                    transformOrigin: Item.Center

                                    RotationAnimation on rotation {
                                        from: 0
                                        to: 360
                                        duration: 3000
                                        loops: Animation.Infinite
                                        running: root.hubState && root.hubState.media && root.hubState.media.status === "Playing"
                                    }
                                }
                            }

                            // Track & Artist Label
                            Text {
                                text: root.hubState && root.hubState.media ? (root.hubState.media.artist + " • " + root.hubState.media.title) : ""
                                font.pixelSize: 12
                                font.bold: true
                                color: root.colFg
                                elide: Text.ElideRight
                                Layout.maximumWidth: 150
                            }

                            // Micro Playback Controls
                            Row {
                                spacing: 4
                                z: 10

                                Rectangle {
                                    width: 20
                                    height: 20
                                    radius: 3
                                    color: prevM.containsMouse ? root.withAlpha(root.colAccent, 0.25) : "transparent"
                                    Text { anchors.centerIn: parent; text: "󰒮"; font.pixelSize: 13; color: prevM.containsMouse ? root.colAccent : root.colFgMuted }
                                    MouseArea {
                                        id: prevM
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: root.runCmd(["python3", "/home/gallo/.config/hypr/scripts/garchy_hub_service.py", "media-prev"])
                                    }
                                }

                                Rectangle {
                                    width: 20
                                    height: 20
                                    radius: 3
                                    color: playM.containsMouse ? root.withAlpha(root.colAccentAlt, 0.35) : root.withAlpha(root.colAccentAlt, 0.15)
                                    Text {
                                        anchors.centerIn: parent
                                        text: root.hubState && root.hubState.media && root.hubState.media.status === "Playing" ? "󰏤" : "󰐊"
                                        font.pixelSize: 13
                                        color: root.colAccentAlt
                                    }
                                    MouseArea {
                                        id: playM
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: root.runCmd(["python3", "/home/gallo/.config/hypr/scripts/garchy_hub_service.py", "media-play-pause"])
                                    }
                                }

                                Rectangle {
                                    width: 20
                                    height: 20
                                    radius: 3
                                    color: nextM.containsMouse ? root.withAlpha(root.colAccent, 0.25) : "transparent"
                                    Text { anchors.centerIn: parent; text: "󰒭"; font.pixelSize: 13; color: nextM.containsMouse ? root.colAccent : root.colFgMuted }
                                    MouseArea {
                                        id: nextM
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: root.runCmd(["python3", "/home/gallo/.config/hypr/scripts/garchy_hub_service.py", "media-next"])
                                    }
                                }
                            }

                            Rectangle {
                                width: 1
                                height: 16
                                color: root.withAlpha(root.colBorder, 0.4)
                            }
                        }

                        // Mode B: GameMode Alert Notch
                        RowLayout {
                            visible: centerIsland.isGameActive && !centerIsland.isMediaActive
                            spacing: 6
                            Text { text: "🎮"; font.pixelSize: 13 }
                            Text {
                                text: "GAMEMODE 144Hz"
                                font.family: "Orbitron"
                                font.pixelSize: 11
                                font.bold: true
                                color: root.colGold
                            }
                            Rectangle { width: 1; height: 16; color: root.withAlpha(root.colBorder, 0.4) }
                        }

                        // Time Display
                        Text {
                            text: root.timeStr
                            font.family: "Orbitron"
                            font.pixelSize: 14
                            font.bold: true
                            color: root.colAccent
                        }

                        // Divider
                        Rectangle {
                            width: 1
                            height: 16
                            color: root.withAlpha(root.colBorder, 0.4)
                        }

                        // Date
                        Text {
                            text: root.dateShortStr
                            font.family: "Orbitron"
                            font.pixelSize: 12
                            font.bold: true
                            color: root.colFg
                        }

                        // Divider
                        Rectangle {
                            width: 1
                            height: 16
                            color: root.withAlpha(root.colBorder, 0.4)
                        }

                        // Weather
                        Text {
                            text: root.hubState && root.hubState.weather ? root.hubState.weather.temp : "+17°C"
                            font.family: "Orbitron"
                            font.pixelSize: 12
                            font.bold: true
                            color: root.colGold
                        }
                    }
                }
                // -------------------------------------------------------------
                // 3. RIGHT ISLAND: Hardware Matrix + CAVA Spectrum + Control Center + Actions (Equal Size)
                // -------------------------------------------------------------
                Rectangle {
                    id: rightIsland
                    anchors.right: parent.right
                    anchors.rightMargin: 20
                    anchors.verticalCenter: parent.verticalCenter
                    height: 42
                    width: root.islandWidth
                    radius: root.islandRadius
                    color: root.colBg
                    border.color: root.colBorder
                    border.width: 1.0

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 6
                        spacing: 6

                        // Hardware Telemetry Matrix
                        Rectangle {
                            visible: barWin.isPrimary
                            Layout.fillWidth: true
                            height: 30
                            radius: root.buttonRadius
                            color: bentoOverlayPopup.visible ? root.colAccent : (hwM.containsMouse ? root.withAlpha(root.colAccent, 0.22) : root.colBgAlt)
                            border.color: bentoOverlayPopup.visible ? root.colAccent : (hwM.containsMouse ? root.colAccent : root.withAlpha(root.colBorder, 0.35))
                            border.width: 1.0

                            RowLayout {
                                anchors.centerIn: parent
                                spacing: 8

                                RowLayout {
                                    spacing: 3
                                    Text { text: "󰻠"; font.pixelSize: 13; color: bentoOverlayPopup.visible ? "#080c16" : root.colAccent }
                                    Text { text: root.cpuUsage; font.family: "Orbitron"; font.pixelSize: 11; font.bold: true; color: bentoOverlayPopup.visible ? "#080c16" : root.colFg }
                                }
                                RowLayout {
                                    spacing: 3
                                    Text { text: "󰢮"; font.pixelSize: 13; color: bentoOverlayPopup.visible ? "#080c16" : root.colGold }
                                    Text { text: root.gpuUsage + " " + root.gpuTemp; font.family: "Orbitron"; font.pixelSize: 11; font.bold: true; color: bentoOverlayPopup.visible ? "#080c16" : root.colFg }
                                }
                                RowLayout {
                                    spacing: 3
                                    Text { text: "󰍛"; font.pixelSize: 13; color: bentoOverlayPopup.visible ? "#080c16" : root.colAccentAlt }
                                    Text { text: root.ramUsage; font.family: "Orbitron"; font.pixelSize: 11; font.bold: true; color: bentoOverlayPopup.visible ? "#080c16" : root.colFg }
                                }
                            }

                            MouseArea {
                                id: hwM
                                anchors.fill: parent
                                hoverEnabled: true
                                acceptedButtons: Qt.LeftButton | Qt.RightButton
                                cursorShape: Qt.PointingHandCursor
                                onClicked: mouse => {
                                    if (mouse.button === Qt.RightButton) {
                                        root.runCmd(["bash", "/home/gallo/.config/hypr/scripts/garchy-toggle.sh", "btop"]);
                                    } else {
                                        barWin.toggleFlyout(bentoOverlayPopup);
                                    }
                                }
                            }
                        }

                        // PipeWire Audio Spectrum (CAVA Visualizer)
                        Rectangle {
                            visible: barWin.isPrimary
                            width: 80
                            height: 30
                            radius: root.buttonRadius
                            color: cavaM.containsMouse ? root.withAlpha(root.colAccentAlt, 0.25) : root.colBgAlt
                            border.color: cavaM.containsMouse ? root.colAccentAlt : root.withAlpha(root.colBorder, 0.3)
                            border.width: 1

                            Row {
                                id: cavaRow
                                anchors.centerIn: parent
                                spacing: 2

                                Repeater {
                                    model: 10
                                    Item {
                                        width: 3.5
                                        height: 18

                                        Rectangle {
                                            anchors.fill: parent
                                            radius: 1
                                            color: root.withAlpha(root.colBorder, 0.15)
                                        }

                                        Rectangle {
                                            anchors.bottom: parent.bottom
                                            anchors.horizontalCenter: parent.horizontalCenter
                                            width: parent.width
                                            height: (root.cavaBars && root.cavaBars[index] !== undefined) ? Math.max(3, Math.min(18, root.cavaBars[index])) : 3
                                            radius: 1
                                            color: height > 13 ? root.colGold : (height > 7 ? root.colAccent : root.colAccentAlt)
                                            opacity: Math.max(0.7, Math.min(1.0, height / 14.0))

                                            Behavior on height { NumberAnimation { duration: 40; easing.type: Easing.OutQuad } }
                                            Behavior on color { ColorAnimation { duration: 60 } }
                                        }
                                    }
                                }
                            }

                            MouseArea {
                                id: cavaM
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: root.runCmd(["bash", "/home/gallo/.config/hypr/scripts/garchy-toggle.sh", "pavucontrol"])
                            }
                        }

                        // Control Center Status Capsule
                        Rectangle {
                            visible: barWin.isPrimary
                            width: 90
                            height: 30
                            radius: root.buttonRadius
                            color: quickSettingsPopup.visible ? root.colAccent : (ctrlM.containsMouse ? root.withAlpha(root.colAccent, 0.25) : root.colBgAlt)
                            border.color: quickSettingsPopup.visible ? root.colAccent : (ctrlM.containsMouse ? root.colAccent : root.withAlpha(root.colBorder, 0.4))
                            border.width: 1

                            RowLayout {
                                id: ctrlRow
                                anchors.centerIn: parent
                                spacing: 5

                                Text {
                                    text: root.hubState && root.hubState.network ? root.hubState.network.icon : "󰈀"
                                    font.pixelSize: 13
                                    color: quickSettingsPopup.visible ? "#080c16" : (root.hubState && root.hubState.network && root.hubState.network.connected ? root.colAccent : root.colFgMuted)
                                }

                                Text {
                                    text: root.hubState && root.hubState.audio && root.hubState.audio.muted ? "󰝟" : "󰕾"
                                    font.pixelSize: 13
                                    color: quickSettingsPopup.visible ? "#080c16" : (root.hubState && root.hubState.audio && root.hubState.audio.muted ? root.colRed : root.colAccent)
                                }

                                Text {
                                    text: (root.hubState && root.hubState.audio ? root.hubState.audio.volume : 50) + "%"
                                    font.family: "Orbitron"
                                    font.pixelSize: 11
                                    font.bold: true
                                    color: quickSettingsPopup.visible ? "#080c16" : root.colFg
                                }
                            }

                            MouseArea {
                                id: ctrlM
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: barWin.toggleFlyout(quickSettingsPopup)
                            }
                        }

                        // Notification Bell
                        Rectangle {
                            visible: barWin.isPrimary
                            width: 30
                            height: 30
                            radius: root.buttonRadius
                            color: notifDrawerPopup.visible ? root.colAccent : (notifM.containsMouse ? root.withAlpha(root.colAccent, 0.25) : root.colBgAlt)
                            border.color: notifDrawerPopup.visible ? root.colAccent : (notifM.containsMouse ? root.colAccent : root.withAlpha(root.colBorder, 0.3))
                            border.width: 1.0

                            Text {
                                anchors.centerIn: parent
                                text: "󰂚"
                                font.pixelSize: 14
                                color: notifDrawerPopup.visible ? "#080c16" : root.colAccent
                            }

                            MouseArea {
                                id: notifM
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: barWin.toggleFlyout(notifDrawerPopup)
                            }
                        }

                        // Gally AI Copilot (Toggles Gally AI Studio Flyout)
                        Rectangle {
                            visible: barWin.isPrimary
                            width: 30
                            height: 30
                            radius: root.buttonRadius
                            color: (typeof gallyAiPopup !== "undefined" && gallyAiPopup.visible) ? root.colAccent : (aiM.containsMouse ? root.withAlpha(root.colAccent, 0.25) : root.colBgAlt)
                            border.color: (typeof gallyAiPopup !== "undefined" && gallyAiPopup.visible) ? root.colAccent : (aiM.containsMouse ? root.colAccent : root.withAlpha(root.colBorder, 0.3))
                            border.width: 1

                            Text {
                                anchors.centerIn: parent
                                text: "󰚩"
                                font.pixelSize: 14
                                color: (typeof gallyAiPopup !== "undefined" && gallyAiPopup.visible) ? "#080c16" : root.colAccent
                            }

                            MouseArea {
                                id: aiM
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    if (barWin.isPrimary) barWin.toggleFlyout(gallyAiPopup);
                                }
                            }
                        }

                        // Theme Switcher
                        Rectangle {
                            visible: barWin.isPrimary
                            width: 30
                            height: 30
                            radius: root.buttonRadius
                            color: thmM.containsMouse ? root.withAlpha(root.colAccentAlt, 0.25) : root.colBgAlt
                            border.color: thmM.containsMouse ? root.colAccentAlt : root.withAlpha(root.colBorder, 0.3)
                            border.width: 1

                            Text {
                                anchors.centerIn: parent
                                text: "󰏘"
                                font.pixelSize: 14
                                color: root.colAccentAlt
                            }

                            MouseArea {
                                id: thmM
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: root.runCmd(["bash", "/home/gallo/.config/hypr/scripts/garchy-toggle.sh", "theme"])
                            }
                        }

                        // Power Button
                        Rectangle {
                            width: 30
                            height: 30
                            radius: root.buttonRadius
                            color: pwrM.containsMouse ? root.withAlpha(root.colRed, 0.25) : root.colBgAlt
                            border.color: pwrM.containsMouse ? root.colRed : root.withAlpha(root.colBorder, 0.3)
                            border.width: 1

                            Text {
                                anchors.centerIn: parent
                                text: "󰐥"
                                font.pixelSize: 14
                                color: root.colRed
                            }

                            MouseArea {
                                id: pwrM
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: root.runCmd(["bash", "-c", "wlogout & disown"])
                            }
                        }
                    }
                }
                // =============================================================
                // 🎛️ POPUPS & FLYOUTS (Caelestia Bento Grid & Spring Animations)
                // =============================================================

                // 1. 🌌 Caelestia Bento Grid Start Menu
                PopupWindow {
                    id: startMenuPopup
                    visible: false
                    anchor.window: barWin
                    anchor.rect.x: 8
                    anchor.rect.y: 52
                    anchor.rect.width: 480
                    anchor.rect.height: 0
                    implicitWidth: 480
                    implicitHeight: 580
                    color: "transparent"

                    property string selectedCategory: "All"

                    Rectangle {
                        anchors.fill: parent
                        radius: root.popupRadius
                        color: root.colBg
                        border.color: root.colAccent
                        border.width: 1.0

                        scale: startMenuPopup.visible ? 1.0 : 0.94
                        opacity: startMenuPopup.visible ? 1.0 : 0.0
                        Behavior on scale { NumberAnimation { duration: 180; easing.type: Easing.OutBack } }
                        Behavior on opacity { NumberAnimation { duration: 150; easing.type: Easing.OutCubic } }

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 16
                            spacing: 12

                            // 1. Profile & OS Banner Header
                            Rectangle {
                                Layout.fillWidth: true
                                height: 54
                                radius: root.buttonRadius
                                color: root.colBgAlt
                                border.color: root.withAlpha(root.colBorder, 0.35)
                                border.width: 1.0

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 8
                                    spacing: 12

                                    // Avatar Badge
                                    Rectangle {
                                        width: 38
                                        height: 38
                                        radius: root.buttonRadius
                                        color: root.withAlpha(root.colAccent, 0.20)
                                        border.color: root.colAccent
                                        border.width: 1.0

                                        Text {
                                            anchors.centerIn: parent
                                            text: "󰣇"
                                            font.pixelSize: 22
                                            color: root.colAccent
                                        }
                                    }

                                    // User & OS Info
                                    ColumnLayout {
                                        Layout.fillWidth: true
                                        spacing: 2

                                        Text {
                                            text: "gallo"
                                            font.family: "Orbitron"
                                            font.pixelSize: 14
                                            font.bold: true
                                            color: root.colFg
                                        }

                                        Text {
                                            text: "Garchy OS • Arch Linux (144Hz Gaming Pipeline)"
                                            font.pixelSize: 10
                                            color: root.colFgMuted
                                        }
                                    }

                                    // Quick Terminal Launcher
                                    Rectangle {
                                        width: 32
                                        height: 32
                                        radius: root.buttonRadius
                                        color: termBtnM.containsMouse ? root.withAlpha(root.colAccent, 0.25) : root.colCard
                                        border.color: root.colBorder
                                        border.width: 1.0

                                        Text {
                                            anchors.centerIn: parent
                                            text: "󰞷"
                                            font.pixelSize: 16
                                            color: root.colAccent
                                        }

                                        MouseArea {
                                            id: termBtnM
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: {
                                                root.runCmd(["kitty"]);
                                                startMenuPopup.visible = false;
                                            }
                                        }
                                    }
                                }
                            }

                            // 2. Dynamic Search Bar
                            Rectangle {
                                Layout.fillWidth: true
                                height: 38
                                radius: root.buttonRadius
                                color: root.colBgAlt
                                border.color: searchInput.activeFocus ? root.colAccent : root.withAlpha(root.colBorder, 0.4)
                                border.width: searchInput.activeFocus ? 1.5 : 1.0

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
                                        id: searchInput
                                        Layout.fillWidth: true
                                        color: root.colFg
                                        font.pixelSize: 12
                                        focus: startMenuPopup.visible
                                        Keys.onEscapePressed: startMenuPopup.visible = false
                                    }

                                    Text {
                                        visible: !searchInput.text
                                        text: "Search apps, games & commands..."
                                        font.pixelSize: 11
                                        color: root.colFgMuted
                                    }

                                    Text {
                                        visible: !!searchInput.text
                                        text: "✕"
                                        font.pixelSize: 12
                                        color: root.colFgMuted
                                        MouseArea {
                                            anchors.fill: parent
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: searchInput.text = ""
                                        }
                                    }
                                }
                            }

                            // 3. Category Bento Filter Pills
                            Row {
                                Layout.fillWidth: true
                                spacing: 6

                                Repeater {
                                    model: ["All", "Games", "Dev", "Web", "System"]
                                    Rectangle {
                                        property bool isSel: startMenuPopup.selectedCategory === modelData
                                        height: 32
                                        width: catTxt.implicitWidth + 18
                                        radius: root.buttonRadius
                                        color: isSel ? (modelData === "Games" ? root.colGold : root.colAccent) : (catM.containsMouse ? root.withAlpha(root.colAccent, 0.20) : root.colBgAlt)
                                        border.color: isSel ? (modelData === "Games" ? root.colGold : root.colAccent) : root.withAlpha(root.colBorder, 0.3)
                                        border.width: 1.0

                                        RowLayout {
                                            id: catTxt
                                            anchors.centerIn: parent
                                            spacing: 5
                                            Text {
                                                text: modelData === "Games" ? "🎮" : (modelData === "Dev" ? "💻" : (modelData === "Web" ? "🌐" : (modelData === "System" ? "⚙️" : "✦")))
                                                font.pixelSize: 12
                                            }
                                            Text {
                                                text: modelData
                                                font.pixelSize: 13
                                                font.bold: isSel
                                                color: isSel ? "#080c16" : (catM.containsMouse ? root.colAccent : root.colFg)
                                            }
                                        }

                                        MouseArea {
                                            id: catM
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: startMenuPopup.selectedCategory = modelData
                                        }
                                    }
                                }
                            }

                            // 4A. GAMING PROFILE & FALLOUT 4 MODDING BENTO (When Games is active)
                            ScrollView {
                                visible: startMenuPopup.selectedCategory === "Games"
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                clip: true

                                ColumnLayout {
                                    width: 448
                                    spacing: 10

                                    // Fallout 4 GOTY Hero Bento Card
                                    Rectangle {
                                        Layout.fillWidth: true
                                        height: 116
                                        radius: root.cardRadius
                                        color: root.colBgAlt
                                        border.color: root.colGold
                                        border.width: 1.0

                                        ColumnLayout {
                                            anchors.fill: parent
                                            anchors.margins: 10
                                            spacing: 6

                                            RowLayout {
                                                Layout.fillWidth: true
                                                spacing: 8

                                                Rectangle {
                                                    width: 32
                                                    height: 32
                                                    radius: 4
                                                    color: root.withAlpha(root.colGold, 0.25)
                                                    border.color: root.colGold
                                                    border.width: 1
                                                    Text { anchors.centerIn: parent; text: "☢️"; font.pixelSize: 18 }
                                                }

                                                ColumnLayout {
                                                    Layout.fillWidth: true
                                                    spacing: 1
                                                    Text { text: "Fallout 4 GOTY (144Hz F4SE)"; font.family: "Orbitron"; font.pixelSize: 14; font.bold: true; color: root.colGold }
                                                    Text { text: "v1.10.163 Pre-Next-Gen • Dynamic Physics 144Hz • RTX 3080 Ti"; font.pixelSize: 11; color: root.colFgMuted }
                                                }
                                            }

                                            RowLayout {
                                                Layout.fillWidth: true
                                                spacing: 8

                                                Rectangle {
                                                    Layout.fillWidth: true
                                                    height: 34
                                                    radius: root.buttonRadius
                                                    color: fo4PlayM.containsMouse ? root.colGold : root.withAlpha(root.colGold, 0.25)
                                                    border.color: root.colGold
                                                    border.width: 1.0

                                                    RowLayout {
                                                        anchors.centerIn: parent
                                                        spacing: 6
                                                        Text { text: "🚀"; font.pixelSize: 13 }
                                                        Text { text: "Launch Fallout 4"; font.pixelSize: 13; font.bold: true; color: fo4PlayM.containsMouse ? "#080c16" : root.colFg }
                                                    }
                                                    MouseArea {
                                                        id: fo4PlayM
                                                        anchors.fill: parent
                                                        hoverEnabled: true
                                                        cursorShape: Qt.PointingHandCursor
                                                        onClicked: {
                                                            root.runCmd(["bash", "/home/gallo/launch_fallout4.sh"]);
                                                            startMenuPopup.visible = false;
                                                        }
                                                    }
                                                }

                                                Rectangle {
                                                    width: 110
                                                    height: 34
                                                    radius: root.buttonRadius
                                                    color: hudBtnM.containsMouse ? root.colAccent : root.colBgAlt
                                                    border.color: root.colAccent
                                                    border.width: 1.0

                                                    RowLayout {
                                                        anchors.centerIn: parent
                                                        spacing: 4
                                                        Text { text: "󰍹"; font.pixelSize: 13; color: hudBtnM.containsMouse ? "#080c16" : root.colAccent }
                                                        Text { text: "MangoHud"; font.pixelSize: 12; font.bold: true; color: hudBtnM.containsMouse ? "#080c16" : root.colFg }
                                                    }
                                                    MouseArea {
                                                        id: hudBtnM
                                                        anchors.fill: parent
                                                        hoverEnabled: true
                                                        cursorShape: Qt.PointingHandCursor
                                                        onClicked: {
                                                            root.runCmd(["bash", "/home/gallo/launch_fallout4.sh", "--hud"]);
                                                            startMenuPopup.visible = false;
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }

                                    // Modding Suite 2x2 Bento Grid
                                    Text { text: "🛠️ Fallout 4 Modding Suite"; font.family: "Orbitron"; font.pixelSize: 13; font.bold: true; color: root.colAccent }

                                    GridLayout {
                                        Layout.fillWidth: true
                                        columns: 2
                                        columnSpacing: 8
                                        rowSpacing: 8

                                        // Mod Organizer 2
                                        Rectangle {
                                            Layout.fillWidth: true
                                            height: 44
                                            radius: root.buttonRadius
                                            color: mo2M.containsMouse ? root.withAlpha(root.colAccent, 0.25) : root.colBgAlt
                                            border.color: mo2M.containsMouse ? root.colAccent : root.withAlpha(root.colBorder, 0.35)
                                            border.width: 1.0
                                            RowLayout {
                                                anchors.fill: parent
                                                anchors.margins: 8
                                                spacing: 8
                                                Text { text: "󰒓"; font.pixelSize: 16; color: root.colAccent }
                                                ColumnLayout {
                                                    spacing: 1
                                                    Text { text: "Mod Organizer 2"; font.pixelSize: 12; font.bold: true; color: root.colFg }
                                                    Text { text: "Mod Deployment"; font.pixelSize: 10; color: root.colFgMuted }
                                                }
                                            }
                                            MouseArea {
                                                id: mo2M
                                                anchors.fill: parent
                                                hoverEnabled: true
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: {
                                                    root.runCmd(["bash", "-c", "heroic || steam & disown"]);
                                                    startMenuPopup.visible = false;
                                                }
                                            }
                                        }

                                        // FO4Edit
                                        Rectangle {
                                            Layout.fillWidth: true
                                            height: 44
                                            radius: root.buttonRadius
                                            color: xeditM.containsMouse ? root.withAlpha(root.colAccentAlt, 0.25) : root.colBgAlt
                                            border.color: xeditM.containsMouse ? root.colAccentAlt : root.withAlpha(root.colBorder, 0.35)
                                            border.width: 1.0
                                            RowLayout {
                                                anchors.fill: parent
                                                anchors.margins: 8
                                                spacing: 8
                                                Text { text: "󰅩"; font.pixelSize: 16; color: root.colAccentAlt }
                                                ColumnLayout {
                                                    spacing: 1
                                                    Text { text: "FO4Edit (xEdit)"; font.pixelSize: 12; font.bold: true; color: root.colFg }
                                                    Text { text: "Plugin Conflict Resolver"; font.pixelSize: 10; color: root.colFgMuted }
                                                }
                                            }
                                            MouseArea {
                                                id: xeditM
                                                anchors.fill: parent
                                                hoverEnabled: true
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: {
                                                    root.runCmd(["bash", "-c", "notify-send FO4Edit Ready"]);
                                                    startMenuPopup.visible = false;
                                                }
                                            }
                                        }

                                        // LOOT Sorter
                                        Rectangle {
                                            Layout.fillWidth: true
                                            height: 44
                                            radius: root.buttonRadius
                                            color: lootM.containsMouse ? root.withAlpha(root.colGreen, 0.25) : root.colBgAlt
                                            border.color: lootM.containsMouse ? root.colGreen : root.withAlpha(root.colBorder, 0.35)
                                            border.width: 1.0
                                            RowLayout {
                                                anchors.fill: parent
                                                anchors.margins: 8
                                                spacing: 8
                                                Text { text: "󰑮"; font.pixelSize: 16; color: root.colGreen }
                                                ColumnLayout {
                                                    spacing: 1
                                                    Text { text: "LOOT Sorter"; font.pixelSize: 12; font.bold: true; color: root.colFg }
                                                    Text { text: "Load Order Optimizer"; font.pixelSize: 10; color: root.colFgMuted }
                                                }
                                            }
                                            MouseArea {
                                                id: lootM
                                                anchors.fill: parent
                                                hoverEnabled: true
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: {
                                                    root.runCmd(["loot"]);
                                                    startMenuPopup.visible = false;
                                                }
                                            }
                                        }

                                        // BodySlide Studio
                                        Rectangle {
                                            Layout.fillWidth: true
                                            height: 44
                                            radius: root.buttonRadius
                                            color: bsM.containsMouse ? root.withAlpha(root.colGold, 0.25) : root.colBgAlt
                                            border.color: bsM.containsMouse ? root.colGold : root.withAlpha(root.colBorder, 0.35)
                                            border.width: 1.0
                                            RowLayout {
                                                anchors.fill: parent
                                                anchors.margins: 8
                                                spacing: 8
                                                Text { text: "󰏘"; font.pixelSize: 16; color: root.colGold }
                                                ColumnLayout {
                                                    spacing: 1
                                                    Text { text: "BodySlide Studio"; font.pixelSize: 12; font.bold: true; color: root.colFg }
                                                    Text { text: "Mesh & Physics Generator"; font.pixelSize: 10; color: root.colFgMuted }
                                                }
                                            }
                                            MouseArea {
                                                id: bsM
                                                anchors.fill: parent
                                                hoverEnabled: true
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: {
                                                    root.runCmd(["bash", "-c", "notify-send BodySlide Ready"]);
                                                    startMenuPopup.visible = false;
                                                }
                                            }
                                        }
                                    }

                                    // Platform Launchers
                                    Text { text: "🎮 Platforms & Launchers"; font.family: "Orbitron"; font.pixelSize: 13; font.bold: true; color: root.colAccent }

                                    RowLayout {
                                        Layout.fillWidth: true
                                        spacing: 8

                                        Rectangle {
                                            Layout.fillWidth: true
                                            height: 36
                                            radius: root.buttonRadius
                                            color: stmM.containsMouse ? root.withAlpha(root.colAccent, 0.25) : root.colBgAlt
                                            border.color: root.colAccent
                                            border.width: 1.0
                                            RowLayout {
                                                anchors.centerIn: parent
                                                spacing: 6
                                                Text { text: "󰓓"; font.pixelSize: 14; color: root.colAccent }
                                                Text { text: "Steam (Native)"; font.pixelSize: 12; font.bold: true; color: root.colFg }
                                            }
                                            MouseArea {
                                                id: stmM
                                                anchors.fill: parent
                                                hoverEnabled: true
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: { root.runCmd(["steam"]); startMenuPopup.visible = false; }
                                            }
                                        }

                                        Rectangle {
                                            Layout.fillWidth: true
                                            height: 36
                                            radius: root.buttonRadius
                                            color: hrcM.containsMouse ? root.withAlpha(root.colAccentAlt, 0.25) : root.colBgAlt
                                            border.color: root.colAccentAlt
                                            border.width: 1.0
                                            RowLayout {
                                                anchors.centerIn: parent
                                                spacing: 6
                                                Text { text: "󰊴"; font.pixelSize: 14; color: root.colAccentAlt }
                                                Text { text: "Heroic Games"; font.pixelSize: 12; font.bold: true; color: root.colFg }
                                            }
                                            MouseArea {
                                                id: hrcM
                                                anchors.fill: parent
                                                hoverEnabled: true
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: { root.runCmd(["heroic"]); startMenuPopup.visible = false; }
                                            }
                                        }
                                    }
                                }
                            }

                            // 4B. Standard Applications List View (When not in Games)
                            ListView {
                                id: appListView
                                visible: startMenuPopup.selectedCategory !== "Games"
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                clip: true
                                spacing: 4

                                model: {
                                    var q = searchInput.text.toLowerCase().trim();
                                    var cat = startMenuPopup.selectedCategory;
                                    var list = root.allAppsList || [];

                                    if (cat !== "All") {
                                        list = list.filter(a => {
                                            var n = (a.name || "").toLowerCase();
                                            var c = (a.cmd || "").toLowerCase();
                                            if (cat === "Dev") return n.includes("code") || n.includes("terminal") || n.includes("kitty") || n.includes("git") || n.includes("gemini");
                                            if (cat === "Web") return n.includes("brave") || n.includes("firefox") || n.includes("browser") || n.includes("discord");
                                            if (cat === "System") return n.includes("setting") || n.includes("monitor") || n.includes("btop") || n.includes("thunar");
                                            return true;
                                        });
                                    }

                                    if (!q) return list.slice(0, 25);
                                    return list.filter(a => (a.name && a.name.toLowerCase().includes(q)) || (a.cmd && a.cmd.toLowerCase().includes(q))).slice(0, 25);
                                }

                                delegate: Rectangle {
                                    width: ListView.view.width
                                    height: 38
                                    radius: root.buttonRadius
                                    color: appItemM.containsMouse ? root.withAlpha(root.colAccent, 0.20) : "transparent"
                                    border.color: appItemM.containsMouse ? root.colAccent : "transparent"
                                    border.width: 1.0

                                    scale: appItemM.containsMouse ? 1.01 : 1.0
                                    Behavior on scale { NumberAnimation { duration: 80 } }

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.margins: 8
                                        spacing: 10

                                        Image {
                                            Layout.preferredWidth: 20
                                            Layout.preferredHeight: 20
                                            sourceSize: Qt.size(20, 20)
                                            width: 20
                                            height: 20
                                            source: Quickshell.iconPath(modelData.icon || modelData.id)
                                            fillMode: Image.PreserveAspectFit
                                            visible: status === Image.Ready
                                        }

                                        Text {
                                            visible: !parent.children[0].visible
                                            text: "󰖯"
                                            font.pixelSize: 16
                                            color: root.colAccent
                                        }

                                        ColumnLayout {
                                            Layout.fillWidth: true
                                            spacing: 1

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
                                                text: modelData.cmd || ""
                                                font.pixelSize: 8
                                                color: root.colFgMuted
                                                elide: Text.ElideRight
                                            }
                                        }
                                    }

                                    MouseArea {
                                        id: appItemM
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

                            // 5. Footer Quick Power Controls
                            Rectangle {
                                Layout.fillWidth: true
                                height: 38
                                radius: root.buttonRadius
                                color: root.colBgAlt
                                border.color: root.withAlpha(root.colBorder, 0.3)
                                border.width: 1.0

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 8
                                    spacing: 14

                                    Item { Layout.fillWidth: true }

                                    Text {
                                        text: "󰌾 Lock"
                                        font.pixelSize: 11
                                        font.bold: true
                                        color: lkM.containsMouse ? root.colAccent : root.colFgMuted
                                        MouseArea { id: lkM; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.runCmd(["bash", "-c", "hyprlock || swaylock"]) }
                                    }

                                    Text {
                                        text: "󰍃 Logout"
                                        font.pixelSize: 11
                                        font.bold: true
                                        color: loM.containsMouse ? root.colGold : root.colFgMuted
                                        MouseArea { id: loM; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.runCmd(["hyprctl", "dispatch", "exit"]) }
                                    }

                                    Text {
                                        text: "󰜉 Reboot"
                                        font.pixelSize: 11
                                        font.bold: true
                                        color: rbM.containsMouse ? root.colAccentAlt : root.colFgMuted
                                        MouseArea { id: rbM; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.runCmd(["systemctl", "reboot"]) }
                                    }

                                    Text {
                                        text: "󰐥 Shutdown"
                                        font.pixelSize: 11
                                        font.bold: true
                                        color: sdM.containsMouse ? root.colRed : root.colRed
                                        MouseArea { id: sdM; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.runCmd(["systemctl", "poweroff"]) }
                                    }
                                }
                            }
                        }
                    }
                }
                // 2. Control Center Popup
                PopupWindow {
                    id: quickSettingsPopup
                    visible: false
                    anchor.window: barWin
                    anchor.rect.x: Math.max(10, barWin.width - 380)
                    anchor.rect.y: 52
                    anchor.rect.width: 360
                    anchor.rect.height: 0
                    implicitWidth: 360
                    implicitHeight: qsCol.implicitHeight + 28
                    color: "transparent"

                    Rectangle {
                        anchors.fill: parent
                        radius: root.popupRadius
                        color: root.colBg
                        border.color: root.colAccent
                        border.width: 1.0

                        ColumnLayout {
                            id: qsCol
                            anchors.fill: parent
                            anchors.margins: 14
                            spacing: 12

                            // Header
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                Text {
                                    text: "🎛️ Control Center"
                                    font.family: "Orbitron"
                                    font.pixelSize: 13
                                    font.bold: true
                                    color: root.colAccent
                                }
                                Item { Layout.fillWidth: true }
                                Text {
                                    text: root.hubState && root.hubState.weather ? root.hubState.weather.display : "🌤️ +17°C"
                                    font.pixelSize: 11
                                    font.bold: true
                                    color: root.colGold
                                }
                            }

                            // Quick Tiles Grid (2x3)
                            GridLayout {
                                Layout.fillWidth: true
                                columns: 3
                                columnSpacing: 8
                                rowSpacing: 8

                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 40
                                    radius: root.buttonRadius
                                    color: root.hubState && root.hubState.network && root.hubState.network.connected ? root.withAlpha(root.colAccent, 0.25) : root.colBgAlt
                                    border.color: root.hubState && root.hubState.network && root.hubState.network.connected ? root.colAccent : root.colBorder
                                    border.width: 1
                                    RowLayout {
                                        anchors.centerIn: parent
                                        spacing: 6
                                        Text { text: "󰤨"; font.pixelSize: 15; color: root.colAccent }
                                        Text { text: "Network"; font.pixelSize: 10; font.bold: true; color: root.colFg }
                                    }
                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: root.runCmd(["python3", "/home/gallo/.config/hypr/scripts/garchy_hub_service.py", "toggle-wifi"])
                                    }
                                }

                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 40
                                    radius: root.buttonRadius
                                    color: root.hubState && root.hubState.bluetooth && root.hubState.bluetooth.powered ? root.withAlpha(root.colAccentAlt, 0.25) : root.colBgAlt
                                    border.color: root.hubState && root.hubState.bluetooth && root.hubState.bluetooth.powered ? root.colAccentAlt : root.colBorder
                                    border.width: 1
                                    RowLayout {
                                        anchors.centerIn: parent
                                        spacing: 6
                                        Text { text: "󰂯"; font.pixelSize: 15; color: root.colAccentAlt }
                                        Text { text: "Bluetooth"; font.pixelSize: 10; font.bold: true; color: root.colFg }
                                    }
                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: root.runCmd(["python3", "/home/gallo/.config/hypr/scripts/garchy_hub_service.py", "toggle-bt"])
                                    }
                                }

                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 40
                                    radius: root.buttonRadius
                                    color: root.hubState && root.hubState.toggles && root.hubState.toggles.night_light ? root.withAlpha(root.colGold, 0.25) : root.colBgAlt
                                    border.color: root.hubState && root.hubState.toggles && root.hubState.toggles.night_light ? root.colGold : root.colBorder
                                    border.width: 1
                                    RowLayout {
                                        anchors.centerIn: parent
                                        spacing: 6
                                        Text { text: "🌙"; font.pixelSize: 13 }
                                        Text { text: "Night Light"; font.pixelSize: 10; font.bold: true; color: root.colFg }
                                    }
                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: root.runCmd(["python3", "/home/gallo/.config/hypr/scripts/garchy_hub_service.py", "toggle-nightlight"])
                                    }
                                }

                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 40
                                    radius: root.buttonRadius
                                    color: root.hubState && root.hubState.toggles && root.hubState.toggles.gamemode ? root.withAlpha(root.colAccent, 0.25) : root.colBgAlt
                                    border.color: root.hubState && root.hubState.toggles && root.hubState.toggles.gamemode ? root.colAccent : root.colBorder
                                    border.width: 1
                                    RowLayout {
                                        anchors.centerIn: parent
                                        spacing: 6
                                        Text { text: "🎮"; font.pixelSize: 13 }
                                        Text { text: "GameMode"; font.pixelSize: 10; font.bold: true; color: root.colFg }
                                    }
                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: root.runCmd(["python3", "/home/gallo/.config/hypr/scripts/garchy_hub_service.py", "toggle-gamemode"])
                                    }
                                }

                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 40
                                    radius: root.buttonRadius
                                    color: root.hubState && root.hubState.audio && root.hubState.audio.mic_muted ? root.withAlpha(root.colRed, 0.25) : root.colBgAlt
                                    border.color: root.hubState && root.hubState.audio && root.hubState.audio.mic_muted ? root.colRed : root.colBorder
                                    border.width: 1
                                    RowLayout {
                                        anchors.centerIn: parent
                                        spacing: 6
                                        Text { text: root.hubState && root.hubState.audio && root.hubState.audio.mic_muted ? "󰍭" : "󰍬"; font.pixelSize: 15; color: root.hubState && root.hubState.audio && root.hubState.audio.mic_muted ? root.colRed : root.colAccent }
                                        Text { text: "Microphone"; font.pixelSize: 10; font.bold: true; color: root.colFg }
                                    }
                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: root.runCmd(["python3", "/home/gallo/.config/hypr/scripts/garchy_hub_service.py", "toggle-mic"])
                                    }
                                }

                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 40
                                    radius: root.buttonRadius
                                    color: root.colBgAlt
                                    border.color: root.colBorder
                                    border.width: 1
                                    RowLayout {
                                        anchors.centerIn: parent
                                        spacing: 6
                                        Text { text: "󰂛"; font.pixelSize: 15; color: root.colAccent }
                                        Text { text: "DND"; font.pixelSize: 10; font.bold: true; color: root.colFg }
                                    }
                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: root.runCmd(["dunstctl", "set-paused", "toggle"])
                                    }
                                }
                            }

                            // Master Volume Slider
                            Rectangle {
                                Layout.fillWidth: true
                                height: 36
                                radius: root.buttonRadius
                                color: root.colBgAlt
                                border.color: root.colBorder
                                border.width: 1

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 8
                                    spacing: 10
                                    Text { text: "󰕾"; font.pixelSize: 15; color: root.colAccent }
                                    Rectangle {
                                        Layout.fillWidth: true
                                        height: 6
                                        radius: root.buttonRadius
                                        color: root.withAlpha(root.colBorder, 0.4)
                                        Rectangle {
                                            anchors.left: parent.left
                                            anchors.top: parent.top
                                            anchors.bottom: parent.bottom
                                            width: parent.width * ((root.hubState && root.hubState.audio ? root.hubState.audio.volume : 50) / 100.0)
                                            radius: root.buttonRadius
                                            color: root.colAccent
                                        }
                                        MouseArea {
                                            anchors.fill: parent
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: mouse => {
                                                var pct = Math.max(0, Math.min(100, Math.round((mouse.x / width) * 100)));
                                                root.runCmd(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", (pct / 100.0).toFixed(2)]);
                                            }
                                        }
                                    }
                                    Text {
                                        text: (root.hubState && root.hubState.audio ? root.hubState.audio.volume : 50) + "%"
                                        font.family: "Orbitron"
                                        font.pixelSize: 10
                                        font.bold: true
                                        color: root.colFg
                                    }
                                }
                            }

                            // Audio Sinks Selector
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 4
                                Text { text: "🔊 Audio Output"; font.pixelSize: 10; font.bold: true; color: root.colFgMuted }
                                Repeater {
                                    model: root.hubState && root.hubState.audio && root.hubState.audio.sinks ? root.hubState.audio.sinks : []
                                    Rectangle {
                                        Layout.fillWidth: true
                                        height: 26
                                        radius: root.buttonRadius
                                        color: modelData.is_default ? root.withAlpha(root.colAccent, 0.20) : "transparent"
                                        border.color: modelData.is_default ? root.colAccent : "transparent"
                                        border.width: 1
                                        RowLayout {
                                            anchors.fill: parent
                                            anchors.margins: 6
                                            spacing: 8
                                            Text { text: modelData.is_default ? "●" : "○"; font.pixelSize: 9; color: modelData.is_default ? root.colAccent : root.colFgMuted }
                                            Text { Layout.fillWidth: true; text: modelData.desc; font.pixelSize: 10; font.bold: modelData.is_default; color: modelData.is_default ? root.colAccent : root.colFg; elide: Text.ElideRight }
                                        }
                                        MouseArea {
                                            anchors.fill: parent
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: root.runCmd(["python3", "/home/gallo/.config/hypr/scripts/garchy_hub_service.py", "set-sink", modelData.name])
                                        }
                                    }
                                }
                            }

                            // MPRIS Media Card
                            Rectangle {
                                Layout.fillWidth: true
                                height: 88
                                radius: root.cardRadius
                                color: root.colBgAlt
                                border.color: root.hubState && root.hubState.media && root.hubState.media.available ? root.colAccentAlt : root.colBorder
                                border.width: 1

                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: 8
                                    spacing: 4

                                    RowLayout {
                                        Layout.fillWidth: true
                                        spacing: 6
                                        Text { text: "🎵"; font.pixelSize: 14 }
                                        ColumnLayout {
                                            Layout.fillWidth: true
                                            spacing: 1
                                            Text { Layout.fillWidth: true; text: root.hubState && root.hubState.media ? root.hubState.media.title : "No Media Playing"; font.pixelSize: 10; font.bold: true; color: root.colFg; elide: Text.ElideRight }
                                            Text { Layout.fillWidth: true; text: root.hubState && root.hubState.media ? root.hubState.media.artist : "Offline"; font.pixelSize: 8; color: root.colFgMuted; elide: Text.ElideRight }
                                        }
                                    }

                                    RowLayout {
                                        Layout.fillWidth: true
                                        spacing: 6
                                        Text { text: root.hubState && root.hubState.media ? root.hubState.media.position_str : "0:00"; font.family: "Orbitron"; font.pixelSize: 8; color: root.colFgMuted }
                                        Rectangle {
                                            Layout.fillWidth: true
                                            height: 5
                                            radius: root.buttonRadius
                                            color: root.withAlpha(root.colBorder, 0.4)
                                            Rectangle {
                                                anchors.left: parent.left
                                                anchors.top: parent.top
                                                anchors.bottom: parent.bottom
                                                width: parent.width * (root.hubState && root.hubState.media ? root.hubState.media.progress : 0.0)
                                                radius: root.buttonRadius
                                                color: root.colGold
                                            }
                                            MouseArea {
                                                anchors.fill: parent
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: mouse => {
                                                    if (root.hubState && root.hubState.media && root.hubState.media.length > 0) {
                                                        var pos = Math.round((mouse.x / width) * root.hubState.media.length);
                                                        root.runCmd(["python3", "/home/gallo/.config/hypr/scripts/garchy_hub_service.py", "media-seek", String(pos)]);
                                                    }
                                                }
                                            }
                                        }
                                        Text { text: root.hubState && root.hubState.media ? root.hubState.media.length_str : "0:00"; font.family: "Orbitron"; font.pixelSize: 8; color: root.colFgMuted }
                                    }

                                    RowLayout {
                                        Layout.alignment: Qt.AlignHCenter
                                        spacing: 20
                                        Text {
                                            text: "󰒮"
                                            font.pixelSize: 16
                                            color: root.colFg
                                            MouseArea {
                                                anchors.fill: parent
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: root.runCmd(["python3", "/home/gallo/.config/hypr/scripts/garchy_hub_service.py", "media-prev"])
                                            }
                                        }
                                        Rectangle {
                                            width: 24
                                            height: 24
                                            radius: root.buttonRadius
                                            color: root.withAlpha(root.colAccent, 0.25)
                                            border.color: root.colAccent
                                            border.width: 1
                                            Text {
                                                anchors.centerIn: parent
                                                text: root.hubState && root.hubState.media && root.hubState.media.status === "Playing" ? "󰏤" : "󰐊"
                                                font.pixelSize: 12
                                                color: root.colAccent
                                            }
                                            MouseArea {
                                                anchors.fill: parent
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: root.runCmd(["python3", "/home/gallo/.config/hypr/scripts/garchy_hub_service.py", "media-play-pause"])
                                            }
                                        }
                                        Text {
                                            text: "󰒭"
                                            font.pixelSize: 16
                                            color: root.colFg
                                            MouseArea {
                                                anchors.fill: parent
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: root.runCmd(["python3", "/home/gallo/.config/hypr/scripts/garchy_hub_service.py", "media-next"])
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                // 3. 🌌 DYNAMIC NOTCH / ISLAND MORPHING FLYOUT (Dedicated Media & Gaming Turbo Hub)
                PopupWindow {
                    id: datePopup
                    visible: false
                    anchor.window: barWin
                    anchor.rect.x: Math.round((barWin.width - 380) / 2)
                    anchor.rect.y: 52
                    anchor.rect.width: 380
                    anchor.rect.height: 0
                    implicitWidth: 380
                    implicitHeight: notchFlyoutCol.implicitHeight + 28
                    color: "transparent"

                    Rectangle {
                        anchors.fill: parent
                        radius: root.popupRadius
                        color: root.colBg
                        border.color: root.hubState && root.hubState.toggles && root.hubState.toggles.gamemode ? root.colGold : root.colAccent
                        border.width: 1.0

                        scale: datePopup.visible ? 1.0 : 0.95
                        opacity: datePopup.visible ? 1.0 : 0.0
                        Behavior on scale { NumberAnimation { duration: 180; easing.type: Easing.OutBack } }
                        Behavior on opacity { NumberAnimation { duration: 150 } }

                        ColumnLayout {
                            id: notchFlyoutCol
                            anchors.fill: parent
                            anchors.margins: 14
                            spacing: 12

                            // 1. Dynamic Media Hub Hero Card
                            Rectangle {
                                Layout.fillWidth: true
                                height: 114
                                radius: root.cardRadius
                                color: root.colBgAlt
                                border.color: root.withAlpha(root.colAccentAlt, 0.4)
                                border.width: 1.0

                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: 10
                                    spacing: 8

                                    RowLayout {
                                        Layout.fillWidth: true
                                        spacing: 10

                                        // 3D Spinning Vinyl Album Core
                                        Rectangle {
                                            width: 42
                                            height: 42
                                            radius: 21
                                            color: "#000000"
                                            border.color: root.colGold
                                            border.width: 1.5

                                            Text {
                                                anchors.centerIn: parent
                                                text: "💿"
                                                font.pixelSize: 24
                                                transformOrigin: Item.Center
                                                RotationAnimation on rotation {
                                                    from: 0
                                                    to: 360
                                                    duration: 3000
                                                    loops: Animation.Infinite
                                                    running: root.hubState && root.hubState.media && root.hubState.media.status === "Playing"
                                                }
                                            }
                                        }

                                        ColumnLayout {
                                            Layout.fillWidth: true
                                            spacing: 2
                                            Text {
                                                Layout.fillWidth: true
                                                text: root.hubState && root.hubState.media && root.hubState.media.title ? root.hubState.media.title : "No Media Playing"
                                                font.family: "Orbitron"
                                                font.pixelSize: 12
                                                font.bold: true
                                                color: root.colFg
                                                elide: Text.ElideRight
                                            }
                                            Text {
                                                Layout.fillWidth: true
                                                text: root.hubState && root.hubState.media && root.hubState.media.artist ? (root.hubState.media.artist + " • " + (root.hubState.media.player || "MPRIS")) : "Media Control Ready"
                                                font.pixelSize: 10
                                                color: root.colAccentAlt
                                                elide: Text.ElideRight
                                            }
                                        }

                                        Rectangle {
                                            height: 20
                                            width: statusTxt.implicitWidth + 10
                                            radius: 3
                                            color: root.hubState && root.hubState.media && root.hubState.media.status === "Playing" ? root.withAlpha(root.colGreen, 0.2) : root.withAlpha(root.colFgMuted, 0.15)
                                            border.color: root.hubState && root.hubState.media && root.hubState.media.status === "Playing" ? root.colGreen : root.colFgMuted
                                            border.width: 1

                                            Text {
                                                id: statusTxt
                                                anchors.centerIn: parent
                                                text: root.hubState && root.hubState.media && root.hubState.media.status === "Playing" ? "● LIVE" : "○ IDLE"
                                                font.family: "Orbitron"
                                                font.pixelSize: 8
                                                font.bold: true
                                                color: root.hubState && root.hubState.media && root.hubState.media.status === "Playing" ? root.colGreen : root.colFgMuted
                                            }
                                        }
                                    }

                                    // Interactive Seek Bar
                                    RowLayout {
                                        Layout.fillWidth: true
                                        spacing: 8
                                        Text { text: root.hubState && root.hubState.media ? root.hubState.media.position_str : "0:00"; font.family: "Orbitron"; font.pixelSize: 9; color: root.colFgMuted }
                                        Rectangle {
                                            Layout.fillWidth: true
                                            height: 6
                                            radius: 3
                                            color: root.withAlpha(root.colBorder, 0.3)
                                            Rectangle {
                                                anchors.left: parent.left; anchors.top: parent.top; anchors.bottom: parent.bottom
                                                width: parent.width * (root.hubState && root.hubState.media ? root.hubState.media.progress : 0.0)
                                                radius: 3
                                                color: root.colGold
                                            }
                                            MouseArea {
                                                anchors.fill: parent
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: mouse => {
                                                    if (root.hubState && root.hubState.media && root.hubState.media.length > 0) {
                                                        var pos = Math.round((mouse.x / width) * root.hubState.media.length);
                                                        root.runCmd(["python3", "/home/gallo/.config/hypr/scripts/garchy_hub_service.py", "media-seek", String(pos)]);
                                                    }
                                                }
                                            }
                                        }
                                        Text { text: root.hubState && root.hubState.media ? root.hubState.media.length_str : "0:00"; font.family: "Orbitron"; font.pixelSize: 9; color: root.colFgMuted }
                                    }

                                    // Media Playback Action Buttons (Prev / Play-Pause / Next)
                                    RowLayout {
                                        Layout.alignment: Qt.AlignHCenter
                                        spacing: 20

                                        Rectangle {
                                            width: 32
                                            height: 32
                                            radius: root.buttonRadius
                                            color: prevBigM.containsMouse ? root.withAlpha(root.colAccent, 0.25) : root.colCard
                                            border.color: root.withAlpha(root.colBorder, 0.3)
                                            border.width: 1
                                            Text { anchors.centerIn: parent; text: "󰒮"; font.pixelSize: 16; color: prevBigM.containsMouse ? root.colAccent : root.colFg }
                                            MouseArea {
                                                id: prevBigM
                                                anchors.fill: parent
                                                hoverEnabled: true
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: root.runCmd(["python3", "/home/gallo/.config/hypr/scripts/garchy_hub_service.py", "media-prev"])
                                            }
                                        }

                                        Rectangle {
                                            width: 36
                                            height: 36
                                            radius: root.buttonRadius
                                            color: root.colAccentAlt
                                            Text {
                                                anchors.centerIn: parent
                                                text: root.hubState && root.hubState.media && root.hubState.media.status === "Playing" ? "󰏤" : "󰐊"
                                                font.pixelSize: 16
                                                color: "#ffffff"
                                            }
                                            MouseArea {
                                                anchors.fill: parent
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: root.runCmd(["python3", "/home/gallo/.config/hypr/scripts/garchy_hub_service.py", "media-play-pause"])
                                            }
                                        }

                                        Rectangle {
                                            width: 32
                                            height: 32
                                            radius: root.buttonRadius
                                            color: nextBigM.containsMouse ? root.withAlpha(root.colAccent, 0.25) : root.colCard
                                            border.color: root.withAlpha(root.colBorder, 0.3)
                                            border.width: 1
                                            Text { anchors.centerIn: parent; text: "󰒭"; font.pixelSize: 16; color: nextBigM.containsMouse ? root.colAccent : root.colFg }
                                            MouseArea {
                                                id: nextBigM
                                                anchors.fill: parent
                                                hoverEnabled: true
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: root.runCmd(["python3", "/home/gallo/.config/hypr/scripts/garchy_hub_service.py", "media-next"])
                                            }
                                        }
                                    }
                                }
                            }

                            // 2. Gaming Turbo & Hardware Performance Switcher (Click toggles ON/OFF)
                            Rectangle {
                                Layout.fillWidth: true
                                height: 46
                                radius: root.cardRadius
                                color: root.hubState && root.hubState.toggles && root.hubState.toggles.gamemode ? root.withAlpha(root.colGold, 0.25) : root.colBgAlt
                                border.color: root.hubState && root.hubState.toggles && root.hubState.toggles.gamemode ? root.colGold : root.withAlpha(root.colBorder, 0.3)
                                border.width: 1.0

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 10
                                    spacing: 10

                                    Rectangle {
                                        width: 28
                                        height: 28
                                        radius: 4
                                        color: root.hubState && root.hubState.toggles && root.hubState.toggles.gamemode ? root.colGold : root.withAlpha(root.colAccent, 0.20)
                                        Text {
                                            anchors.centerIn: parent
                                            text: "🎮"
                                            font.pixelSize: 14
                                        }
                                    }

                                    ColumnLayout {
                                        Layout.fillWidth: true
                                        spacing: 1

                                        Text {
                                            text: "GameMode Turbo (144Hz)"
                                            font.family: "Orbitron"
                                            font.pixelSize: 11
                                            font.bold: true
                                            color: root.hubState && root.hubState.toggles && root.hubState.toggles.gamemode ? root.colGold : root.colFg
                                        }

                                        Text {
                                            text: root.hubState && root.hubState.toggles && root.hubState.toggles.gamemode ? "RTX 3080 Ti Maximum Performance Active" : "Click to activate high performance governor"
                                            font.pixelSize: 9
                                            color: root.colFgMuted
                                        }
                                    }

                                    Rectangle {
                                        height: 24
                                        width: 48
                                        radius: 12
                                        color: root.hubState && root.hubState.toggles && root.hubState.toggles.gamemode ? root.colGold : root.colCard
                                        border.color: root.hubState && root.hubState.toggles && root.hubState.toggles.gamemode ? root.colGold : root.colBorder
                                        border.width: 1

                                        Text {
                                            anchors.centerIn: parent
                                            text: root.hubState && root.hubState.toggles && root.hubState.toggles.gamemode ? "ON" : "OFF"
                                            font.family: "Orbitron"
                                            font.pixelSize: 9
                                            font.bold: true
                                            color: root.hubState && root.hubState.toggles && root.hubState.toggles.gamemode ? "#080c16" : root.colFgMuted
                                        }
                                    }
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: root.runCmd(["python3", "/home/gallo/.config/hypr/scripts/garchy_hub_service.py", "toggle-gamemode"])
                                }
                            }
                        }
                    }
                }
                // 4. Window Group Popup
                PopupWindow {
                    id: groupMenuPopup
                    property var currentGroup: null
                    visible: false
                    anchor.window: barWin
                    anchor.rect.x: 80
                    anchor.rect.y: 52
                    anchor.rect.width: 260
                    anchor.rect.height: 0
                    implicitWidth: 260
                    implicitHeight: Math.min(300, (currentGroup ? currentGroup.windows.length * 36 : 0) + 40)
                    color: "transparent"

                    Rectangle {
                        anchors.fill: parent
                        radius: root.popupRadius
                        color: root.colBg
                        border.color: root.colAccent
                        border.width: 1.0

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 8
                            spacing: 4

                            Text {
                                text: (groupMenuPopup.currentGroup ? groupMenuPopup.currentGroup.class : "Windows") + " (" + (groupMenuPopup.currentGroup ? groupMenuPopup.currentGroup.count : 0) + ")"
                                font.pixelSize: 11
                                font.bold: true
                                color: root.colAccent
                            }

                            ListView {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                clip: true
                                model: groupMenuPopup.currentGroup ? groupMenuPopup.currentGroup.windows : []
                                delegate: Rectangle {
                                    width: ListView.view.width
                                    height: 32
                                    radius: root.buttonRadius
                                    color: winItemMouse.containsMouse ? root.withAlpha(root.colAccent, 0.20) : root.colBgAlt
                                    border.color: modelData.is_active ? root.colAccent : "transparent"
                                    border.width: 1

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.margins: 6
                                        spacing: 6

                                        Text {
                                            Layout.fillWidth: true
                                            text: modelData.title || "Window"
                                            font.pixelSize: 10
                                            color: modelData.is_active ? root.colAccent : root.colFg
                                            elide: Text.ElideRight
                                        }

                                        Text {
                                            text: "✕"
                                            font.pixelSize: 10
                                            color: winCloseMouse.containsMouse ? root.colRed : root.colFgMuted
                                            MouseArea {
                                                id: winCloseMouse
                                                anchors.fill: parent
                                                hoverEnabled: true
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: { root.dispatchAction("close", modelData.address); groupMenuPopup.visible = false; }
                                            }
                                        }
                                    }

                                    MouseArea {
                                        id: winItemMouse
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: { root.dispatchAction("focus", modelData.address); groupMenuPopup.visible = false; }
                                    }
                                }
                            }
                        }
                    }
                }
// 5. 📊 BENTO HARDWARE MONITOR OVERLAY (Sci-Fi Glass Dashboard)
                PopupWindow {
                    id: bentoOverlayPopup
                    visible: false
                    anchor.window: barWin
                    anchor.rect.x: Math.max(10, barWin.width - 560)
                    anchor.rect.y: 52
                    anchor.rect.width: 540
                    anchor.rect.height: 0
                    implicitWidth: 540
                    implicitHeight: bentoCol.implicitHeight + 28
                    color: "transparent"

                    Rectangle {
                        anchors.fill: parent
                        radius: root.popupRadius
                        color: root.colBg
                        border.color: root.colAccent
                        border.width: 1.0

                        scale: bentoOverlayPopup.visible ? 1.0 : 0.95
                        opacity: bentoOverlayPopup.visible ? 1.0 : 0.0
                        Behavior on scale { NumberAnimation { duration: 180; easing.type: Easing.OutBack } }
                        Behavior on opacity { NumberAnimation { duration: 150 } }

                        ColumnLayout {
                            id: bentoCol
                            anchors.fill: parent
                            anchors.margins: 14
                            spacing: 12

                            // Header
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8

                                Text {
                                    text: "📊 Garchy Bento System Telemetry"
                                    font.family: "Orbitron"
                                    font.pixelSize: 13
                                    font.bold: true
                                    color: root.colAccent
                                }

                                Item { Layout.fillWidth: true }

                                Rectangle {
                                    height: 24
                                    width: btopBtnTxt.implicitWidth + 14
                                    radius: root.buttonRadius
                                    color: root.colBgAlt
                                    border.color: root.colAccent
                                    border.width: 1.0

                                    Text {
                                        id: btopBtnTxt
                                        anchors.centerIn: parent
                                        text: "󰞷 Open btop"
                                        font.pixelSize: 10
                                        font.bold: true
                                        color: root.colAccent
                                    }

                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: {
                                            root.runCmd(["bash", "/home/gallo/.config/hypr/scripts/garchy-toggle.sh", "btop"]);
                                            bentoOverlayPopup.visible = false;
                                        }
                                    }
                                }
                            }

                            // 2x2 Bento Box Metrics Grid
                            GridLayout {
                                Layout.fillWidth: true
                                columns: 2
                                columnSpacing: 10
                                rowSpacing: 10

                                // 1. CPU Box: AMD Ryzen 9 5900X (12C/24T)
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 90
                                    radius: root.cardRadius
                                    color: root.colBgAlt
                                    border.color: root.withAlpha(root.colAccent, 0.4)
                                    border.width: 1.0

                                    ColumnLayout {
                                        anchors.fill: parent
                                        anchors.margins: 10
                                        spacing: 4

                                        RowLayout {
                                            Text { text: "󰻠 CPU LOAD"; font.family: "Orbitron"; font.pixelSize: 12; font.bold: true; color: root.colAccent }
                                            Item { Layout.fillWidth: true }
                                            Text { text: root.cpuUsage; font.family: "Orbitron"; font.pixelSize: 15; font.bold: true; color: root.colFg }
                                        }

                                        Text { text: "AMD Ryzen 9 5900X (12 Cores / 24 Threads)"; font.pixelSize: 11; color: root.colFgMuted }

                                        Rectangle {
                                            Layout.fillWidth: true
                                            height: 6
                                            radius: root.buttonRadius
                                            color: root.withAlpha(root.colBorder, 0.3)
                                            Rectangle {
                                                anchors.left: parent.left; anchors.top: parent.top; anchors.bottom: parent.bottom
                                                width: parent.width * (parseFloat(root.cpuUsage.replace("%", "")) / 100.0)
                                                radius: root.buttonRadius
                                                color: root.colAccent
                                            }
                                        }
                                    }
                                }

                                // 2. GPU Box: NVIDIA GeForce RTX 3080 Ti
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 90
                                    radius: root.cardRadius
                                    color: root.colBgAlt
                                    border.color: root.withAlpha(root.colGold, 0.4)
                                    border.width: 1.0

                                    ColumnLayout {
                                        anchors.fill: parent
                                        anchors.margins: 10
                                        spacing: 4

                                        RowLayout {
                                            Text { text: "󰢮 GPU & THERMALS"; font.family: "Orbitron"; font.pixelSize: 12; font.bold: true; color: root.colGold }
                                            Item { Layout.fillWidth: true }
                                            Text { text: root.gpuUsage + " • " + root.gpuTemp; font.family: "Orbitron"; font.pixelSize: 14; font.bold: true; color: root.colFg }
                                        }

                                        Text { text: "NVIDIA GeForce RTX 3080 Ti (12GB GDDR6X)"; font.pixelSize: 11; color: root.colFgMuted }

                                        Rectangle {
                                            Layout.fillWidth: true
                                            height: 6
                                            radius: root.buttonRadius
                                            color: root.withAlpha(root.colBorder, 0.3)
                                            Rectangle {
                                                anchors.left: parent.left; anchors.top: parent.top; anchors.bottom: parent.bottom
                                                width: parent.width * (parseFloat(root.gpuUsage.replace("%", "")) / 100.0)
                                                radius: root.buttonRadius
                                                color: root.colGold
                                            }
                                        }
                                    }
                                }

                                // 3. RAM Box: 32GB High-Speed Allocation
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 90
                                    radius: root.cardRadius
                                    color: root.colBgAlt
                                    border.color: root.withAlpha(root.colAccentAlt, 0.4)
                                    border.width: 1.0

                                    ColumnLayout {
                                        anchors.fill: parent
                                        anchors.margins: 10
                                        spacing: 4

                                        RowLayout {
                                            Text { text: "󰍛 MEMORY ALLOCATION"; font.family: "Orbitron"; font.pixelSize: 12; font.bold: true; color: root.colAccentAlt }
                                            Item { Layout.fillWidth: true }
                                            Text { text: root.ramUsage; font.family: "Orbitron"; font.pixelSize: 15; font.bold: true; color: root.colFg }
                                        }

                                        Text { text: "32GB High-Speed DDR4 Memory Pool"; font.pixelSize: 11; color: root.colFgMuted }

                                        Rectangle {
                                            Layout.fillWidth: true
                                            height: 6
                                            radius: root.buttonRadius
                                            color: root.withAlpha(root.colBorder, 0.3)
                                            Rectangle {
                                                anchors.left: parent.left; anchors.top: parent.top; anchors.bottom: parent.bottom
                                                width: parent.width * (parseFloat(root.ramUsage.replace("%", "")) / 100.0)
                                                radius: root.buttonRadius
                                                color: root.colAccentAlt
                                            }
                                        }
                                    }
                                }

                                // 4. Storage Box: NVMe & Disk Health
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 90
                                    radius: root.cardRadius
                                    color: root.colBgAlt
                                    border.color: root.withAlpha(root.colBorder, 0.4)
                                    border.width: 1.0

                                    ColumnLayout {
                                        anchors.fill: parent
                                        anchors.margins: 10
                                        spacing: 4

                                        RowLayout {
                                            Text { text: "󰋊 NVMe STORAGE"; font.family: "Orbitron"; font.pixelSize: 10; font.bold: true; color: root.colFg }
                                            Item { Layout.fillWidth: true }
                                            Text { text: (root.diskStatus ? root.diskStatus.avail_gb : "85") + " GB FREE"; font.family: "Orbitron"; font.pixelSize: 11; font.bold: true; color: root.colGreen }
                                        }

                                        Text { text: "Samsung NVMe System Root (/)"; font.pixelSize: 9; color: root.colFgMuted }

                                        Rectangle {
                                            Layout.fillWidth: true
                                            height: 6
                                            radius: root.buttonRadius
                                            color: root.withAlpha(root.colBorder, 0.3)
                                            Rectangle {
                                                anchors.left: parent.left; anchors.top: parent.top; anchors.bottom: parent.bottom
                                                width: parent.width * 0.82
                                                radius: root.buttonRadius
                                                color: root.colGreen
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                // 6. 🔔 NOTIFICATION HISTORY GLASS DRAWER
                PopupWindow {
                    id: notifDrawerPopup
                    visible: false
                    anchor.window: barWin
                    anchor.rect.x: Math.max(10, barWin.width - 380)
                    anchor.rect.y: 52
                    anchor.rect.width: 360
                    anchor.rect.height: 0
                    implicitWidth: 360
                    implicitHeight: 460
                    color: "transparent"

                    Rectangle {
                        anchors.fill: parent
                        radius: root.popupRadius
                        color: root.colBg
                        border.color: root.colAccent
                        border.width: 1.0

                        scale: notifDrawerPopup.visible ? 1.0 : 0.95
                        opacity: notifDrawerPopup.visible ? 1.0 : 0.0
                        Behavior on scale { NumberAnimation { duration: 180; easing.type: Easing.OutBack } }
                        Behavior on opacity { NumberAnimation { duration: 150 } }

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 14
                            spacing: 10

                            // Header: Title & Clear History Button
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8

                                Text {
                                    text: "🔔 Notification History"
                                    font.family: "Orbitron"
                                    font.pixelSize: 13
                                    font.bold: true
                                    color: root.colAccent
                                }

                                Item { Layout.fillWidth: true }

                                Rectangle {
                                    height: 24
                                    width: clearTxt.implicitWidth + 14
                                    radius: root.buttonRadius
                                    color: root.colBgAlt
                                    border.color: root.colRed
                                    border.width: 1.0

                                    Text {
                                        id: clearTxt
                                        anchors.centerIn: parent
                                        text: "✕ Clear All"
                                        font.pixelSize: 9
                                        font.bold: true
                                        color: root.colRed
                                    }

                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: {
                                            root.runCmd(["dunstctl", "history-clear"]);
                                            root.notifHistory = [];
                                        }
                                    }
                                }
                            }

                            // Notification List View
                            ListView {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                clip: true
                                spacing: 6

                                model: root.notifHistory && root.notifHistory.length > 0 ? root.notifHistory : []

                                delegate: Rectangle {
                                    width: ListView.view.width
                                    height: notifCardCol.implicitHeight + 16
                                    radius: root.cardRadius
                                    color: root.colBgAlt
                                    border.color: root.withAlpha(root.colBorder, 0.35)
                                    border.width: 1.0

                                    ColumnLayout {
                                        id: notifCardCol
                                        anchors.fill: parent
                                        anchors.margins: 8
                                        spacing: 3

                                        RowLayout {
                                            Layout.fillWidth: true
                                            spacing: 6

                                            Text {
                                                text: modelData.app || "System"
                                                font.pixelSize: 10
                                                font.bold: true
                                                color: root.colAccent
                                            }

                                            Item { Layout.fillWidth: true }

                                            Text {
                                                text: "✕"
                                                font.pixelSize: 10
                                                color: root.colFgMuted
                                                MouseArea {
                                                    anchors.fill: parent
                                                    cursorShape: Qt.PointingHandCursor
                                                    onClicked: root.runCmd(["dunstctl", "history-rm", String(modelData.id)])
                                                }
                                            }
                                        }

                                        Text {
                                            Layout.fillWidth: true
                                            text: modelData.summary || ""
                                            font.pixelSize: 11
                                            font.bold: true
                                            color: root.colFg
                                            elide: Text.ElideRight
                                        }

                                        Text {
                                            Layout.fillWidth: true
                                            text: modelData.body || ""
                                            font.pixelSize: 10
                                            color: root.colFgMuted
                                            wrapMode: Text.WordWrap
                                            maximumLineCount: 3
                                            elide: Text.ElideRight
                                        }
                                    }
                                }

                                                                // Empty State Placeholder
                                Item {
                                    anchors.centerIn: parent
                                    visible: !root.notifHistory || root.notifHistory.length === 0
                                    ColumnLayout {
                                        anchors.centerIn: parent
                                        spacing: 6
                                        Text { text: "󰂛"; font.pixelSize: 32; color: root.colFgMuted; Layout.alignment: Qt.AlignHCenter }
                                        Text { text: "No Notifications Yet"; font.pixelSize: 11; color: root.colFgMuted; Layout.alignment: Qt.AlignHCenter }
                                    }
                                }
                            }
                        }
                    }
                }

                // 7. 🧠 GALLY AI NEURAL STUDIO POPUP FLYOUT
                // -------------------------------------------------------------
                PopupWindow {
                    id: gallyAiPopup
                    visible: false
                    anchor.window: barWin
                    anchor.rect.x: Math.max(10, barWin.width - 560)
                    anchor.rect.y: 52
                    anchor.rect.width: 540
                    anchor.rect.height: 0
                    implicitWidth: 540
                    implicitHeight: 640
                    color: "transparent"

                    // Wire hotkey toggle trigger
                    Connections {
                        target: root
                        function onAiToggleCountChanged() {
                            if (barWin.isPrimary) barWin.toggleFlyout(gallyAiPopup);
                        }
                        function onChatHistoryChanged() {
                            if (chatView && chatView.count > 0) chatView.positionViewAtEnd();
                        }
                    }

                    Rectangle {
                        anchors.fill: parent
                        radius: root.popupRadius
                        color: root.colBg
                        border.color: root.colAccent
                        border.width: 1.0

                        scale: gallyAiPopup.visible ? 1.0 : 0.95
                        opacity: gallyAiPopup.visible ? 1.0 : 0.0
                        Behavior on scale { NumberAnimation { duration: 160; easing.type: Easing.OutBack } }
                        Behavior on opacity { NumberAnimation { duration: 130 } }

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 14
                            spacing: 10

                            // 1. Header (Emblem, Model Selector, Voice Toggle, Clear, Close)
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8

                                Rectangle {
                                    width: 34
                                    height: 34
                                    radius: 5
                                    color: root.withAlpha(root.colAccent, 0.22)
                                    border.color: root.colAccent
                                    border.width: 1.0
                                    Text { anchors.centerIn: parent; text: "󰚩"; font.pixelSize: 18; color: root.colAccent }
                                }

                                ColumnLayout {
                                    spacing: 1
                                    Text {
                                        text: "Gally AI Neural Studio"
                                        font.family: "Orbitron"
                                        font.pixelSize: 14
                                        font.bold: true
                                        color: root.colFg
                                    }
                                    Text {
                                        text: "Cephalon 3-Tier Multi-Provider Pipeline"
                                        font.pixelSize: 10
                                        color: root.colFgMuted
                                    }
                                }

                                Item { Layout.fillWidth: true }

                                // Voice Toggle
                                Rectangle {
                                    height: 28
                                    width: vTxt.implicitWidth + 14
                                    radius: 4
                                    color: root.isAiVoiceEnabled ? root.withAlpha(root.colAccent, 0.25) : root.colBgAlt
                                    border.color: root.isAiVoiceEnabled ? root.colAccent : root.withAlpha(root.colBorder, 0.35)
                                    border.width: 1.0
                                    RowLayout { id: vTxt; anchors.centerIn: parent; spacing: 4; Text { text: root.isAiVoiceEnabled ? "🔊" : "🔇"; font.pixelSize: 11 } Text { text: root.isAiVoiceEnabled ? "Voice ON" : "Mute"; font.pixelSize: 11; font.bold: true; color: root.isAiVoiceEnabled ? root.colAccent : root.colFgMuted } }
                                    MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: root.toggleAiVoice() }
                                }

                                // Clear Chat
                                Rectangle {
                                    height: 28
                                    width: 28
                                    radius: 4
                                    color: clrM.containsMouse ? root.withAlpha(root.colRed, 0.3) : root.colBgAlt
                                    border.color: clrM.containsMouse ? root.colRed : root.withAlpha(root.colBorder, 0.35)
                                    border.width: 1.0
                                    Text { anchors.centerIn: parent; text: "🗑️"; font.pixelSize: 12 }
                                    MouseArea { id: clrM; anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: root.clearAiChat() }
                                }

                                // Close Button
                                Rectangle {
                                    width: 28
                                    height: 28
                                    radius: 4
                                    color: clsM.containsMouse ? root.withAlpha(root.colRed, 0.3) : root.colBgAlt
                                    border.color: clsM.containsMouse ? root.colRed : root.withAlpha(root.colBorder, 0.35)
                                    border.width: 1.0
                                    Text { anchors.centerIn: parent; text: "✕"; font.pixelSize: 12; font.bold: true; color: clsM.containsMouse ? root.colRed : root.colFgMuted }
                                    MouseArea { id: clsM; anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: gallyAiPopup.visible = false }
                                }
                            }

                            // 2. 3-Tier Neural Model Chips
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 5

                                Repeater {
                                    model: [
                                        { id: "qwen2.5:0.5b", label: "⚡ Qwen (T1)" },
                                        { id: "gally-cephalon-ai", label: "🌌 Cephalon (T2)" },
                                        { id: "hermes3:8b", label: "🚀 Hermes (T3)" },
                                        { id: "gemini-1.5-flash", label: "✨ Gemini" }
                                    ]

                                    Rectangle {
                                        property bool isSel: root.activeAiModel === modelData.id
                                        Layout.fillWidth: true
                                        height: 26
                                        radius: 4
                                        color: isSel ? root.colGold : (mChipM.containsMouse ? root.withAlpha(root.colGold, 0.22) : root.colBgAlt)
                                        border.color: isSel ? root.colGold : root.withAlpha(root.colBorder, 0.3)
                                        border.width: 1.0

                                        Text {
                                            anchors.centerIn: parent
                                            text: modelData.label
                                            font.pixelSize: 10
                                            font.bold: isSel
                                            color: isSel ? "#080c16" : (mChipM.containsMouse ? root.colGold : root.colFg)
                                        }

                                        MouseArea {
                                            id: mChipM
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: root.setAiModel(modelData.id)
                                        }
                                    }
                                }
                            }

                            // 3. Live Chat History Viewport
                            Rectangle {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                radius: 6
                                color: root.colBgAlt
                                border.color: root.withAlpha(root.colBorder, 0.25)
                                border.width: 1.0
                                clip: true

                                ListView {
                                    id: chatView
                                    anchors.fill: parent
                                    anchors.margins: 10
                                    spacing: 8
                                    clip: true
                                    model: root.chatHistory || []

                                    ScrollBar.vertical: ScrollBar {
                                        policy: ScrollBar.AsNeeded
                                        contentItem: Rectangle { implicitWidth: 6; radius: 3; color: root.withAlpha(root.colAccent, 0.5) }
                                    }

                                    delegate: Item {
                                        width: chatView.width - 12
                                        height: bubbleCard.implicitHeight + 6
                                        property bool isUser: modelData.role === "user"

                                        Rectangle {
                                            id: bubbleCard
                                            anchors.right: isUser ? parent.right : undefined
                                            anchors.left: isUser ? undefined : parent.left
                                            width: Math.min(parent.width * 0.88, bubbleCol.implicitWidth + 20)
                                            height: bubbleCol.implicitHeight + 14
                                            radius: 6
                                            color: isUser ? root.withAlpha(root.colAccentAlt, 0.25) : root.colCard
                                            border.color: isUser ? root.colAccent : root.withAlpha(root.colGold, 0.35)
                                            border.width: 1.0

                                            ColumnLayout {
                                                id: bubbleCol
                                                anchors.fill: parent
                                                anchors.margins: 8
                                                spacing: 4

                                                RowLayout {
                                                    Layout.fillWidth: true
                                                    spacing: 6
                                                    Text { text: isUser ? "󰣇 gallo" : "󰚩 Cephalon Gally"; font.family: "Orbitron"; font.pixelSize: 10; font.bold: true; color: isUser ? root.colAccent : root.colGold }
                                                    Item { Layout.fillWidth: true }
                                                    Text { text: modelData.timestamp || ""; font.pixelSize: 9; color: root.colFgMuted }
                                                }

                                                TextEdit {
                                                    Layout.fillWidth: true
                                                    text: modelData.text || ""
                                                    font.pixelSize: 11
                                                    color: root.colFg
                                                    wrapMode: TextEdit.Wrap
                                                    readOnly: true
                                                    selectByMouse: true
                                                }
                                            }
                                        }
                                    }
                                }
                            }

                            // 4. Quick Action Chips
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 5

                                Repeater {
                                    model: [
                                        "🎮 144Hz Gaming Mode",
                                        "📊 System Diagnostics",
                                        "☢️ Fallout 4 Health"
                                    ]

                                    Rectangle {
                                        Layout.fillWidth: true
                                        height: 24
                                        radius: 4
                                        color: qM.containsMouse ? root.withAlpha(root.colAccent, 0.22) : root.colBgAlt
                                        border.color: qM.containsMouse ? root.colAccent : root.withAlpha(root.colBorder, 0.3)
                                        border.width: 1.0

                                        Text {
                                            anchors.centerIn: parent
                                            text: modelData
                                            font.pixelSize: 9
                                            font.bold: true
                                            color: qM.containsMouse ? root.colAccent : root.colFgMuted
                                        }

                                        MouseArea {
                                            id: qM
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: root.sendAiPrompt(modelData)
                                        }
                                    }
                                }
                            }

                            // 5. Prompt Input Bar
                            Rectangle {
                                Layout.fillWidth: true
                                height: 40
                                radius: 5
                                color: root.colBgAlt
                                border.color: flyoutPromptInput.activeFocus ? root.colAccent : root.withAlpha(root.colBorder, 0.35)
                                border.width: flyoutPromptInput.activeFocus ? 1.5 : 1.0

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 6
                                    spacing: 8

                                    Text { text: "💬"; font.pixelSize: 13 }

                                    TextInput {
                                        id: flyoutPromptInput
                                        Layout.fillWidth: true
                                        color: root.colFg
                                        font.pixelSize: 12
                                        selectByMouse: true

                                        Keys.onReturnPressed: {
                                            if (text.trim()) {
                                                root.sendAiPrompt(text.trim());
                                                text = "";
                                            }
                                        }
                                    }

                                    Text {
                                        visible: !flyoutPromptInput.text
                                        text: "Ask Gally AI or type system command..."
                                        font.pixelSize: 11
                                        color: root.colFgMuted
                                    }

                                    Rectangle {
                                        height: 28
                                        width: sndTxt.implicitWidth + 14
                                        radius: 4
                                        color: sndM.containsMouse ? root.colAccent : root.withAlpha(root.colAccent, 0.3)
                                        border.color: root.colAccent
                                        border.width: 1.0

                                        RowLayout {
                                            id: sndTxt
                                            anchors.centerIn: parent
                                            spacing: 4
                                            Text { text: "🚀"; font.pixelSize: 11 }
                                            Text { text: "Send"; font.pixelSize: 11; font.bold: true; color: sndM.containsMouse ? "#080c16" : root.colFg }
                                        }

                                        MouseArea {
                                            id: sndM
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: {
                                                if (flyoutPromptInput.text.trim()) {
                                                    root.sendAiPrompt(flyoutPromptInput.text.trim());
                                                    flyoutPromptInput.text = "";
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

    // =========================================================================
    // 🔊 FLOATING ON-SCREEN DISPLAY (OSD) OVERLAY
    // =========================================================================
    PanelWindow {
        id: winOSD
        visible: root.osdVisible
        screen: {
            for (var i = 0; i < Quickshell.screens.length; i++) {
                if (Quickshell.screens[i].name === "DP-2") return Quickshell.screens[i];
            }
            return Quickshell.screens[0];
        }
        anchors {
            bottom: true
        }
        implicitWidth: 260
        implicitHeight: 100
        color: "transparent"
        WlrLayershell.layer: WlrLayer.Overlay
        WlrLayershell.namespace: "garchy-osd"

        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 30
            width: 260
            height: 48
            radius: root.buttonRadius
            color: root.colBg
            border.color: root.colAccent
            border.width: 1.0

            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10

                Text {
                    text: root.osdEvent && root.osdEvent.muted ? "󰝟" : (root.osdEvent && root.osdEvent.volume > 50 ? "󰕾" : "󰖀")
                    font.pixelSize: 18
                    color: root.osdEvent && root.osdEvent.muted ? root.colRed : root.colAccent
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 6
                    radius: root.buttonRadius
                    color: root.withAlpha(root.colBorder, 0.4)

                    Rectangle {
                        anchors.left: parent.left
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        width: parent.width * ((root.osdEvent ? root.osdEvent.volume : 50) / 100.0)
                        radius: root.buttonRadius
                        color: root.osdEvent && root.osdEvent.muted ? root.colRed : root.colAccent
                    }
                }

                Text {
                    text: (root.osdEvent ? root.osdEvent.volume : 50) + "%"
                    font.family: "Orbitron"
                    font.pixelSize: 11
                    font.bold: true
                    color: root.colFg
                }
            }
        }
    }
}
