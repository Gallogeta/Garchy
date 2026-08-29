import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import Quickshell
import Quickshell.Wayland
import Quickshell.Io

ShellRoot {
    id: root

    property color colBg: "#C8080c16"
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

    function withAlpha(c, a) {
        return Qt.rgba(c.r, c.g, c.b, a);
    }

    function runCmd(cmdList) {
        try {
            Qt.createQmlObject("import Quickshell; import Quickshell.Io; Process { running: true; command: " + JSON.stringify(cmdList) + "; onExited: destroy() }", root);
        } catch(e) {
            console.error("runCmd error:", e);
        }
    }

    function launchApp(execCmd) {
        if (!execCmd) return;
        runCmd(["bash", "-c", execCmd + " & disown"]);
        Qt.quit();
    }

    // =========================================================================
    // 📂 DESKTOP APPLICATIONS & STATE
    // =========================================================================
    property var allAppsList: []
    property string activeCategory: "All"
    property string searchQuery: ""
    property string mathResult: ""

    FileView {
        id: appsFile
        path: "/home/gallo/.cache/garchy_desktop_apps.json"
        watchChanges: true
        onLoaded: {
            try { root.allAppsList = JSON.parse(text()); } catch(e){}
        }
        onFileChanged: {
            reload();
            try { root.allAppsList = JSON.parse(text()); } catch(e){}
        }
    }

    function evalMath(expr) {
        try {
            if (/^[0-9+\-*/().\s^%]+$/.test(expr.trim())) {
                var res = Function('"use strict"; return (' + expr + ')')();
                if (typeof res === "number" && !isNaN(res)) {
                    return String(res);
                }
            }
        } catch(e){}
        return "";
    }

    function filteredApps() {
        var list = root.allAppsList || [];
        var q = root.searchQuery.toLowerCase().trim();
        var cat = root.activeCategory;

        if (cat !== "All") {
            list = list.filter(a => {
                var c = (a.categories || "").toLowerCase();
                var n = (a.name || "").toLowerCase();
                var e = (a.exec || "").toLowerCase();

                if (cat === "Games") return c.includes("game") || n.includes("fallout") || n.includes("steam") || n.includes("heroic") || n.includes("mod") || e.includes("loot") || e.includes("fo4");
                if (cat === "Dev") return c.includes("development") || n.includes("code") || n.includes("kitty") || n.includes("terminal") || n.includes("gemini") || n.includes("git");
                if (cat === "Web") return c.includes("network") || c.includes("audio") || c.includes("video") || n.includes("brave") || n.includes("browser") || n.includes("discord") || n.includes("spotify");
                if (cat === "System") return c.includes("system") || c.includes("settings") || c.includes("utility") || n.includes("monitor") || n.includes("btop") || n.includes("thunar");
                return true;
            });
        }

        if (!q || q.startsWith(">")) return list;

        return list.filter(a => {
            var n = (a.name || "").toLowerCase();
            var e = (a.exec || "").toLowerCase();
            var c = (a.comment || "").toLowerCase();
            return n.includes(q) || e.includes(q) || c.includes(q);
        });
    }

    // =========================================================================
    // 🌌 FULLSCREEN CAELESTIA LAUNCHPAD WINDOW
    // =========================================================================
    PanelWindow {
        id: launchpadWin
        screen: {
            for (var i = 0; i < Quickshell.screens.length; i++) {
                if (Quickshell.screens[i].name === "DP-2") return Quickshell.screens[i];
            }
            return Quickshell.screens[0];
        }
        anchors {
            top: true
            bottom: true
            left: true
            right: true
        }
        color: "transparent"
        WlrLayershell.layer: WlrLayer.Overlay
        WlrLayershell.namespace: "caelestia-launchpad"
        WlrLayershell.keyboardFocus: WlrKeyboardFocus.Exclusive

        // Dimmed frosted backdrop
        Rectangle {
            anchors.fill: parent
            color: "#B3000000"
            MouseArea {
                anchors.fill: parent
                onClicked: Qt.quit()
            }
        }

        // Center Floating Obsidian Glass Launchpad Bento Card
        Rectangle {
            id: mainCard
            anchors.centerIn: parent
            width: Math.min(1240, parent.width - 60)
            height: Math.min(800, parent.height - 60)
            radius: 8
            color: root.colBg
            border.color: root.colAccent
            border.width: 1.0

            focus: true
            Keys.onEscapePressed: Qt.quit()

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 14

                // -------------------------------------------------------------
                // 1. TOP HEADER (OS Badge, Digital Clock, System Telemetry, Close)
                // -------------------------------------------------------------
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 14

                    // Left OS Badge
                    RowLayout {
                        spacing: 10
                        Rectangle {
                            width: 40
                            height: 40
                            radius: 6
                            color: root.withAlpha(root.colAccent, 0.22)
                            border.color: root.colAccent
                            border.width: 1.0
                            Text { anchors.centerIn: parent; text: "󰣇"; font.pixelSize: 24; color: root.colAccent }
                        }
                        ColumnLayout {
                            spacing: 1
                            Text {
                                text: "Caelestia Launchpad"
                                font.family: "Orbitron"
                                font.pixelSize: 18
                                font.bold: true
                                color: root.colFg
                            }
                            Text {
                                text: "Garchy OS • Arch Linux 144Hz Gaming Architecture"
                                font.pixelSize: 11
                                color: root.colFgMuted
                            }
                        }
                    }

                    Item { Layout.fillWidth: true }

                    // Hardware Telemetry Capsule
                    Rectangle {
                        height: 36
                        width: hwTelL.implicitWidth + 20
                        radius: 6
                        color: root.colBgAlt
                        border.color: root.withAlpha(root.colBorder, 0.35)
                        border.width: 1.0

                        RowLayout {
                            id: hwTelL
                            anchors.centerIn: parent
                            spacing: 12
                            RowLayout { spacing: 4; Text { text: "󰻠"; font.pixelSize: 14; color: root.colAccent } Text { text: "Ryzen 9 5900X"; font.family: "Orbitron"; font.pixelSize: 11; font.bold: true; color: root.colFg } }
                            RowLayout { spacing: 4; Text { text: "󰢮"; font.pixelSize: 14; color: root.colGold } Text { text: "RTX 3080 Ti"; font.family: "Orbitron"; font.pixelSize: 11; font.bold: true; color: root.colFg } }
                            RowLayout { spacing: 4; Text { text: "󰍛"; font.pixelSize: 14; color: root.colAccentAlt } Text { text: "32GB RAM"; font.family: "Orbitron"; font.pixelSize: 11; font.bold: true; color: root.colFg } }
                        }
                    }

                    // Close Button
                    Rectangle {
                        width: 36
                        height: 36
                        radius: 6
                        color: closeM.containsMouse ? root.withAlpha(root.colRed, 0.3) : root.colBgAlt
                        border.color: closeM.containsMouse ? root.colRed : root.withAlpha(root.colBorder, 0.35)
                        border.width: 1.0

                        Text {
                            anchors.centerIn: parent
                            text: "✕"
                            font.pixelSize: 15
                            font.bold: true
                            color: closeM.containsMouse ? root.colRed : root.colFgMuted
                        }

                        MouseArea {
                            id: closeM
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: Qt.quit()
                        }
                    }
                }

                // Divider
                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: root.withAlpha(root.colBorder, 0.3)
                }

                // -------------------------------------------------------------
                // 2. PINNED QUICK LAUNCH HERO CARDS (Top Ribbon)
                // -------------------------------------------------------------
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    // 1. Fallout 4 GOTY 144Hz Hero Card
                    Rectangle {
                        Layout.fillWidth: true
                        height: 48
                        radius: 6
                        color: fo4M.containsMouse ? root.colGold : root.withAlpha(root.colGold, 0.20)
                        border.color: root.colGold
                        border.width: 1.0

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 8
                            Text { text: "☢️"; font.pixelSize: 18 }
                            ColumnLayout {
                                spacing: 1
                                Text { text: "Fallout 4 GOTY"; font.family: "Orbitron"; font.pixelSize: 12; font.bold: true; color: fo4M.containsMouse ? "#080c16" : root.colGold }
                                Text { text: "144Hz F4SE • GameMode"; font.pixelSize: 9; color: fo4M.containsMouse ? "#080c16" : root.colFgMuted }
                            }
                        }
                        MouseArea {
                            id: fo4M
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: root.launchApp("/home/gallo/launch_fallout4.sh")
                        }
                    }

                    // 2. Mod Organizer 2
                    Rectangle {
                        Layout.fillWidth: true
                        height: 48
                        radius: 6
                        color: mo2M.containsMouse ? root.withAlpha(root.colAccent, 0.3) : root.colBgAlt
                        border.color: mo2M.containsMouse ? root.colAccent : root.withAlpha(root.colBorder, 0.3)
                        border.width: 1.0

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 8
                            Text { text: "󰒓"; font.pixelSize: 18; color: root.colAccent }
                            ColumnLayout {
                                spacing: 1
                                Text { text: "Mod Organizer 2"; font.pixelSize: 12; font.bold: true; color: root.colFg }
                                Text { text: "Mod Management"; font.pixelSize: 9; color: root.colFgMuted }
                            }
                        }
                        MouseArea {
                            id: mo2M
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: root.launchApp("heroic || steam")
                        }
                    }

                    // 3. Brave Browser
                    Rectangle {
                        Layout.fillWidth: true
                        height: 48
                        radius: 6
                        color: brvM.containsMouse ? root.withAlpha(root.colAccent, 0.3) : root.colBgAlt
                        border.color: brvM.containsMouse ? root.colAccent : root.withAlpha(root.colBorder, 0.3)
                        border.width: 1.0

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 8
                            Text { text: "🌐"; font.pixelSize: 18 }
                            ColumnLayout {
                                spacing: 1
                                Text { text: "Brave Browser"; font.pixelSize: 12; font.bold: true; color: root.colFg }
                                Text { text: "Web & YouTube"; font.pixelSize: 9; color: root.colFgMuted }
                            }
                        }
                        MouseArea {
                            id: brvM
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: root.launchApp("brave")
                        }
                    }

                    // 4. Kitty Terminal
                    Rectangle {
                        Layout.fillWidth: true
                        height: 48
                        radius: 6
                        color: ktM.containsMouse ? root.withAlpha(root.colAccent, 0.3) : root.colBgAlt
                        border.color: ktM.containsMouse ? root.colAccent : root.withAlpha(root.colBorder, 0.3)
                        border.width: 1.0

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 8
                            Text { text: "🐱"; font.pixelSize: 18 }
                            ColumnLayout {
                                spacing: 1
                                Text { text: "Kitty Terminal"; font.pixelSize: 12; font.bold: true; color: root.colFg }
                                Text { text: "Fish Shell (144Hz)"; font.pixelSize: 9; color: root.colFgMuted }
                            }
                        }
                        MouseArea {
                            id: ktM
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: root.launchApp("kitty")
                        }
                    }

                    // 5. Steam Native
                    Rectangle {
                        Layout.fillWidth: true
                        height: 48
                        radius: 6
                        color: stmM.containsMouse ? root.withAlpha(root.colAccentAlt, 0.3) : root.colBgAlt
                        border.color: stmM.containsMouse ? root.colAccentAlt : root.withAlpha(root.colBorder, 0.3)
                        border.width: 1.0

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 8
                            Text { text: "󰓓"; font.pixelSize: 18; color: root.colAccentAlt }
                            ColumnLayout {
                                spacing: 1
                                Text { text: "Steam Gaming"; font.pixelSize: 12; font.bold: true; color: root.colFg }
                                Text { text: "Games Library"; font.pixelSize: 9; color: root.colFgMuted }
                            }
                        }
                        MouseArea {
                            id: stmM
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: root.launchApp("steam")
                        }
                    }
                }

                // -------------------------------------------------------------
                // 3. SCI-FI SEARCH & COMMAND BAR (With Math & Shell Evaluation)
                // -------------------------------------------------------------
                Rectangle {
                    Layout.fillWidth: true
                    height: 48
                    radius: 6
                    color: root.colBgAlt
                    border.color: searchInput.activeFocus ? root.colAccent : root.withAlpha(root.colBorder, 0.4)
                    border.width: searchInput.activeFocus ? 1.5 : 1.0

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 10

                        Text {
                            text: searchInput.text.startsWith(">") ? "⚡" : "🔍"
                            font.pixelSize: 16
                            color: root.colAccent
                        }

                        TextInput {
                            id: searchInput
                            Layout.fillWidth: true
                            color: root.colFg
                            font.pixelSize: 14
                            font.bold: true
                            focus: true
                            selectByMouse: true

                            onTextChanged: {
                                root.searchQuery = text;
                                root.mathResult = root.evalMath(text);
                            }

                            Keys.onReturnPressed: {
                                var q = text.trim();
                                if (q.startsWith(">")) {
                                    root.launchApp(q.substring(1).trim());
                                } else {
                                    var list = root.filteredApps();
                                    if (list.length > 0) {
                                        root.launchApp(list[0].exec);
                                    }
                                }
                            }

                            Keys.onEscapePressed: Qt.quit()
                        }

                        // Math Evaluation Badge
                        Rectangle {
                            visible: !!root.mathResult
                            height: 28
                            width: mathTxt.implicitWidth + 16
                            radius: 4
                            color: root.colGold
                            Text {
                                id: mathTxt
                                anchors.centerIn: parent
                                text: "= " + root.mathResult
                                font.family: "Orbitron"
                                font.pixelSize: 12
                                font.bold: true
                                color: "#080c16"
                            }
                        }

                        // Shell Command Badge
                        Rectangle {
                            visible: searchInput.text.startsWith(">")
                            height: 28
                            width: cmdBadgeTxt.implicitWidth + 16
                            radius: 4
                            color: root.colAccent
                            Text {
                                id: cmdBadgeTxt
                                anchors.centerIn: parent
                                text: "⚡ Run Shell Command"
                                font.pixelSize: 11
                                font.bold: true
                                color: "#080c16"
                            }
                        }

                        Text {
                            visible: !searchInput.text
                            text: "Type to search apps, execute shell command (> cmd), or evaluate math..."
                            font.pixelSize: 13
                            color: root.colFgMuted
                        }

                        Text {
                            visible: !!searchInput.text
                            text: "✕"
                            font.pixelSize: 14
                            font.bold: true
                            color: root.colFgMuted
                            MouseArea {
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    searchInput.text = "";
                                    searchInput.focus = true;
                                }
                            }
                        }
                    }
                }

                // -------------------------------------------------------------
                // 4. CATEGORY FILTER PILLS
                // -------------------------------------------------------------
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    Repeater {
                        model: [
                            { id: "All", name: "✦ All Applications" },
                            { id: "Games", name: "🎮 Gaming & Modding" },
                            { id: "Dev", name: "💻 Development" },
                            { id: "Web", name: "🌐 Internet & Media" },
                            { id: "System", name: "⚙️ System & Settings" }
                        ]

                        Rectangle {
                            property bool isSel: root.activeCategory === modelData.id
                            height: 32
                            width: catPillTxt.implicitWidth + 20
                            radius: 5
                            color: isSel ? (modelData.id === "Games" ? root.colGold : root.colAccent) : (catPillM.containsMouse ? root.withAlpha(root.colAccent, 0.22) : root.colBgAlt)
                            border.color: isSel ? (modelData.id === "Games" ? root.colGold : root.colAccent) : root.withAlpha(root.colBorder, 0.35)
                            border.width: 1.0

                            Text {
                                id: catPillTxt
                                anchors.centerIn: parent
                                text: modelData.name
                                font.pixelSize: 12
                                font.bold: isSel
                                color: isSel ? "#080c16" : (catPillM.containsMouse ? root.colAccent : root.colFg)
                            }

                            MouseArea {
                                id: catPillM
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: root.activeCategory = modelData.id
                            }
                        }
                    }

                    Item { Layout.fillWidth: true }

                    Text {
                        text: root.filteredApps().length + " Apps Available"
                        font.pixelSize: 11
                        font.bold: true
                        color: root.colFgMuted
                    }
                }

                // -------------------------------------------------------------
                // 5. MAIN 6-COLUMN APPS GRID VIEW (With Garchy Smooth ScrollBar)
                // -------------------------------------------------------------
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    radius: 6
                    color: root.colBgAlt
                    border.color: root.withAlpha(root.colBorder, 0.3)
                    border.width: 1.0
                    clip: true

                    GridView {
                        id: appsGrid
                        anchors.fill: parent
                        anchors.margins: 12
                        cellWidth: (width - 24) / 6
                        cellHeight: 110
                        clip: true

                        model: root.filteredApps()

                        ScrollBar.vertical: ScrollBar {
                            id: appScrollBar
                            policy: ScrollBar.AlwaysOn
                            active: true
                            width: 8

                            contentItem: Rectangle {
                                implicitWidth: 8
                                radius: 4
                                color: appScrollBar.pressed ? root.colGold : (appScrollBar.hovered ? root.colAccent : root.withAlpha(root.colAccent, 0.6))
                            }

                            background: Rectangle {
                                implicitWidth: 8
                                radius: 4
                                color: root.withAlpha(root.colCard, 0.6)
                            }
                        }

                        delegate: Item {
                            width: appsGrid.cellWidth
                            height: appsGrid.cellHeight

                            Rectangle {
                                anchors.fill: parent
                                anchors.margins: 4
                                radius: 6
                                color: appCardM.containsMouse ? root.withAlpha(root.colAccent, 0.22) : root.colCard
                                border.color: appCardM.containsMouse ? root.colAccent : root.withAlpha(root.colBorder, 0.25)
                                border.width: 1.0

                                scale: appCardM.containsMouse ? 1.04 : 1.0
                                Behavior on scale { NumberAnimation { duration: 90 } }

                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: 8
                                    spacing: 4

                                    // App Icon
                                    Item {
                                        Layout.alignment: Qt.AlignHCenter
                                        Layout.preferredWidth: 44
                                        Layout.preferredHeight: 44

                                        Image {
                                            anchors.fill: parent
                                            sourceSize: Qt.size(44, 44)
                                            source: Quickshell.iconPath(modelData.icon || modelData.id || "application-default")
                                            fillMode: Image.PreserveAspectFit
                                            asynchronous: true
                                            visible: status === Image.Ready
                                        }

                                        Text {
                                            visible: !parent.children[0].visible
                                            anchors.centerIn: parent
                                            text: "󰖯"
                                            font.pixelSize: 32
                                            color: root.colAccent
                                        }
                                    }

                                    // App Name
                                    Text {
                                        Layout.fillWidth: true
                                        text: modelData.name
                                        font.pixelSize: 12
                                        font.bold: true
                                        color: appCardM.containsMouse ? root.colAccent : root.colFg
                                        horizontalAlignment: Text.AlignHCenter
                                        elide: Text.ElideRight
                                    }

                                    // Category / Exec Subtitle
                                    Text {
                                        Layout.fillWidth: true
                                        text: modelData.exec || ""
                                        font.pixelSize: 9
                                        color: root.colFgMuted
                                        horizontalAlignment: Text.AlignHCenter
                                        elide: Text.ElideRight
                                    }
                                }

                                MouseArea {
                                    id: appCardM
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: root.launchApp(modelData.exec)
                                }
                            }
                        }
                    }
                }

                // -------------------------------------------------------------
                // 6. FOOTER SESSION & SYSTEM ACTIONS BAR
                // -------------------------------------------------------------
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12

                    // Quick Help Tip
                    RowLayout {
                        spacing: 6
                        Text { text: "💡 Tip:"; font.pixelSize: 11; font.bold: true; color: root.colGold }
                        Text { text: "Press Esc to dismiss • Type > to run shell command • Double-click to launch"; font.pixelSize: 11; color: root.colFgMuted }
                    }

                    Item { Layout.fillWidth: true }

                    // Lock Button
                    Rectangle {
                        height: 32
                        width: lkTxt.implicitWidth + 18
                        radius: 5
                        color: lkM.containsMouse ? root.withAlpha(root.colAccent, 0.25) : root.colBgAlt
                        border.color: root.withAlpha(root.colBorder, 0.3)
                        border.width: 1.0
                        RowLayout { id: lkTxt; anchors.centerIn: parent; spacing: 5; Text { text: "󰌾"; font.pixelSize: 13; color: root.colAccent } Text { text: "Lock Screen"; font.pixelSize: 11; font.bold: true; color: root.colFg } }
                        MouseArea { id: lkM; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.launchApp("hyprlock || swaylock") }
                    }

                    // Logout Button
                    Rectangle {
                        height: 32
                        width: loTxt.implicitWidth + 18
                        radius: 5
                        color: loM.containsMouse ? root.withAlpha(root.colGold, 0.25) : root.colBgAlt
                        border.color: root.withAlpha(root.colGold, 0.4)
                        border.width: 1.0
                        RowLayout { id: loTxt; anchors.centerIn: parent; spacing: 5; Text { text: "󰍃"; font.pixelSize: 13; color: root.colGold } Text { text: "Logout"; font.pixelSize: 11; font.bold: true; color: root.colFg } }
                        MouseArea { id: loM; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.launchApp("hyprctl dispatch exit") }
                    }

                    // Reboot Button
                    Rectangle {
                        height: 32
                        width: rbTxt.implicitWidth + 18
                        radius: 5
                        color: rbM.containsMouse ? root.withAlpha(root.colAccentAlt, 0.25) : root.colBgAlt
                        border.color: root.withAlpha(root.colBorder, 0.3)
                        border.width: 1.0
                        RowLayout { id: rbTxt; anchors.centerIn: parent; spacing: 5; Text { text: "󰜉"; font.pixelSize: 13; color: root.colAccentAlt } Text { text: "Reboot"; font.pixelSize: 11; font.bold: true; color: root.colFg } }
                        MouseArea { id: rbM; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.launchApp("systemctl reboot") }
                    }

                    // Shutdown Button
                    Rectangle {
                        height: 32
                        width: sdTxt.implicitWidth + 18
                        radius: 5
                        color: sdM.containsMouse ? root.withAlpha(root.colRed, 0.35) : root.colBgAlt
                        border.color: root.withAlpha(root.colRed, 0.5)
                        border.width: 1.0
                        RowLayout { id: sdTxt; anchors.centerIn: parent; spacing: 5; Text { text: "󰐥"; font.pixelSize: 13; color: root.colRed } Text { text: "Shutdown"; font.pixelSize: 11; font.bold: true; color: root.colRed } }
                        MouseArea { id: sdM; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.launchApp("systemctl poweroff") }
                    }
                }
            }
        }
    }
}
