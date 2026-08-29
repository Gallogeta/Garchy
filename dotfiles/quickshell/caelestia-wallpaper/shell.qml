import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import Quickshell
import Quickshell.Wayland
import Quickshell.Io

ShellRoot {
    id: root

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

    function withAlpha(c, a) {
        return Qt.rgba(c.r, c.g, c.b, a);
    }

    // =========================================================================
    // 📂 WALLPAPER DATA & INDEXING
    // =========================================================================
    property var wallpaperData: ({ current: "", total: 0, directories: [], wallpapers: [] })
    property string selectedPath: ""
    property string selectedName: ""
    property string selectedFolder: ""
    property string activeCategory: "All"
    property string searchQuery: ""
    property bool showDirManager: false

    FileView {
        id: wallFile
        path: "/tmp/garchy_wallpapers.json"
        watchChanges: true
        onLoaded: {
            try {
                root.wallpaperData = JSON.parse(text());
                if (!root.selectedPath && root.wallpaperData.current) {
                    root.selectedPath = root.wallpaperData.current;
                    root.selectedName = root.selectedPath.split("/").pop();
                } else if (!root.selectedPath && root.wallpaperData.wallpapers.length > 0) {
                    root.selectedPath = root.wallpaperData.wallpapers[0].path;
                    root.selectedName = root.wallpaperData.wallpapers[0].name;
                }
            } catch(e){}
        }
        onFileChanged: {
            reload();
            try { root.wallpaperData = JSON.parse(text()); } catch(e){}
        }
    }

    function applyTarget(type) {
        if (!selectedPath) return;
        runProc(["python3", "/home/gallo/.config/hypr/scripts/wallpaper_indexer.py", type, selectedPath]);
    }

    function removeDir(dirPath) {
        runProc(["python3", "/home/gallo/.config/hypr/scripts/wallpaper_indexer.py", "remove-dir", dirPath]);
    }

    function pickAddDir() {
        runProc(["python3", "/home/gallo/.config/hypr/scripts/wallpaper_indexer.py", "pick-add-dir"]);
    }

    function selectRandom() {
        var list = filteredList();
        if (list.length > 0) {
            var rand = list[Math.floor(Math.random() * list.length)];
            root.selectedPath = rand.path;
            root.selectedName = rand.name;
            root.selectedFolder = rand.folder;
        }
    }

    function filteredList() {
        var list = root.wallpaperData && root.wallpaperData.wallpapers ? root.wallpaperData.wallpapers : [];
        var cat = root.activeCategory;
        var q = root.searchQuery.toLowerCase().trim();

        if (cat !== "All") {
            list = list.filter(w => w.folder === cat || w.dir === cat);
        }
        if (q) {
            list = list.filter(w => w.name.toLowerCase().includes(q));
        }
        return list;
    }

    function getCategoryList() {
        var dirs = root.wallpaperData && root.wallpaperData.directories ? root.wallpaperData.directories : [];
        var cats = ["All"];
        for (var i = 0; i < dirs.length; i++) {
            var p = dirs[i];
            var base = p.split("/").filter(Boolean).pop() || p;
            cats.push(base);
        }
        return cats;
    }

    function runProc(args) {
        try {
            Qt.createQmlObject("import Quickshell; import Quickshell.Io; Process { running: true; command: " + JSON.stringify(args) + "; onExited: destroy() }", root);
        } catch(e) {
            console.error("runProc error:", e);
        }
    }

    // =========================================================================
    // 🌌 FULL FLOATING CAELESTIA STUDIO WINDOW
    // =========================================================================
    PanelWindow {
        id: studioWin
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
        WlrLayershell.namespace: "garchy-wallpaper-studio"
        WlrLayershell.keyboardFocus: WlrKeyboardFocus.Exclusive

        // Dimmed backdrop
        Rectangle {
            anchors.fill: parent
            color: "#99000000"
            MouseArea {
                anchors.fill: parent
                onClicked: Qt.quit()
            }
        }

        // Center Floating Obsidian Studio Card
        Rectangle {
            id: mainCard
            anchors.centerIn: parent
            width: Math.min(1160, parent.width - 40)
            height: Math.min(740, parent.height - 40)
            radius: 8
            color: root.colBg
            border.color: root.colAccent
            border.width: 1.0

            focus: true
            Keys.onEscapePressed: Qt.quit()

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 18
                spacing: 14

                // -------------------------------------------------------------
                // 1. TOP HEADER (Title, Category Chips, Folders Toggle, Search & Close)
                // -------------------------------------------------------------
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12

                    // Title Badge
                    RowLayout {
                        spacing: 10
                        Text { text: "󰸉"; font.pixelSize: 26; color: root.colAccent }
                        ColumnLayout {
                            spacing: 2
                            Text {
                                text: "Caelestia Wallpaper Studio"
                                font.family: "Orbitron"
                                font.pixelSize: 17
                                font.bold: true
                                color: root.colFg
                            }
                            Text {
                                text: (root.wallpaperData.total || 0) + " High-Res Wallpapers • " + (root.wallpaperData.directories ? root.wallpaperData.directories.length : 0) + " Monitored Folders"
                                font.pixelSize: 11
                                color: root.colFgMuted
                            }
                        }
                    }

                    Item { Layout.fillWidth: true }

                    // Category Filter Pills
                    Row {
                        spacing: 5
                        Repeater {
                            model: root.getCategoryList()
                            Rectangle {
                                property bool isSel: root.activeCategory === modelData
                                height: 32
                                width: catTxt.implicitWidth + 18
                                radius: 5
                                color: isSel ? root.colAccent : (catM.containsMouse ? root.withAlpha(root.colAccent, 0.22) : root.colBgAlt)
                                border.color: isSel ? root.colAccent : root.withAlpha(root.colBorder, 0.35)
                                border.width: 1.0

                                Text {
                                    id: catTxt
                                    anchors.centerIn: parent
                                    text: modelData
                                    font.pixelSize: 12
                                    font.bold: isSel
                                    color: isSel ? "#080c16" : (catM.containsMouse ? root.colAccent : root.colFg)
                                }

                                MouseArea {
                                    id: catM
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: {
                                        root.activeCategory = modelData;
                                        root.showDirManager = false;
                                    }
                                }
                            }
                        }
                    }

                    // Directory Manager Toggle Button
                    Rectangle {
                        height: 32
                        width: dirBtnTxt.implicitWidth + 18
                        radius: 5
                        color: root.showDirManager ? root.colGold : (dirBtnM.containsMouse ? root.withAlpha(root.colGold, 0.25) : root.colBgAlt)
                        border.color: root.showDirManager ? root.colGold : root.withAlpha(root.colGold, 0.4)
                        border.width: 1.0

                        RowLayout {
                            id: dirBtnTxt
                            anchors.centerIn: parent
                            spacing: 6
                            Text { text: "📁"; font.pixelSize: 13 }
                            Text {
                                text: "Manage Folders"
                                font.pixelSize: 12
                                font.bold: true
                                color: root.showDirManager ? "#080c16" : (dirBtnM.containsMouse ? root.colGold : root.colFg)
                            }
                        }

                        MouseArea {
                            id: dirBtnM
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: root.showDirManager = !root.showDirManager
                        }
                    }

                    // Search Box
                    Rectangle {
                        width: 180
                        height: 32
                        radius: 5
                        color: root.colBgAlt
                        border.color: searchIn.activeFocus ? root.colAccent : root.withAlpha(root.colBorder, 0.4)
                        border.width: 1.0

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 8
                            spacing: 8
                            Text { text: "🔍"; font.pixelSize: 12; color: root.colAccent }
                            TextInput {
                                id: searchIn
                                Layout.fillWidth: true
                                color: root.colFg
                                font.pixelSize: 12
                                onTextChanged: root.searchQuery = text
                                Keys.onEscapePressed: Qt.quit()
                            }
                            Text {
                                visible: !searchIn.text
                                text: "Filter..."
                                font.pixelSize: 11
                                color: root.colFgMuted
                            }
                        }
                    }

                    // Close Button
                    Rectangle {
                        width: 32
                        height: 32
                        radius: 5
                        color: closeM.containsMouse ? root.withAlpha(root.colRed, 0.25) : root.colBgAlt
                        border.color: closeM.containsMouse ? root.colRed : root.withAlpha(root.colBorder, 0.35)
                        border.width: 1.0

                        Text {
                            anchors.centerIn: parent
                            text: "✕"
                            font.pixelSize: 14
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

                // Divider Line
                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: root.withAlpha(root.colBorder, 0.3)
                }

                // -------------------------------------------------------------
                // 📂 DIRECTORY MANAGEMENT DRAWER (Collapsible)
                // -------------------------------------------------------------
                Rectangle {
                    visible: root.showDirManager
                    Layout.fillWidth: true
                    height: dirCol.implicitHeight + 24
                    radius: 6
                    color: root.colBgAlt
                    border.color: root.colGold
                    border.width: 1.0

                    ColumnLayout {
                        id: dirCol
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 10

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8
                            Text { text: "📂 Monitored Wallpaper Directories"; font.family: "Orbitron"; font.pixelSize: 13; font.bold: true; color: root.colGold }
                            Item { Layout.fillWidth: true }
                            Rectangle {
                                height: 28
                                width: addDirTxt.implicitWidth + 16
                                radius: 4
                                color: root.colAccent
                                Text {
                                    id: addDirTxt
                                    anchors.centerIn: parent
                                    text: "➕ Add Directory"
                                    font.pixelSize: 11
                                    font.bold: true
                                    color: "#080c16"
                                }
                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: root.pickAddDir()
                                }
                            }
                        }

                        // Monitored Directories List
                        Repeater {
                            model: root.wallpaperData && root.wallpaperData.directories ? root.wallpaperData.directories : []
                            Rectangle {
                                Layout.fillWidth: true
                                height: 32
                                radius: 4
                                color: root.colCard
                                border.color: root.withAlpha(root.colBorder, 0.25)
                                border.width: 1.0

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 8
                                    spacing: 10

                                    Text { text: "📁"; font.pixelSize: 13 }
                                    Text {
                                        Layout.fillWidth: true
                                        text: modelData
                                        font.pixelSize: 12
                                        font.bold: true
                                        color: root.colFg
                                        elide: Text.ElideMiddle
                                    }

                                    Rectangle {
                                        width: 24
                                        height: 24
                                        radius: 4
                                        color: rmDirM.containsMouse ? root.withAlpha(root.colRed, 0.3) : "transparent"
                                        Text {
                                            anchors.centerIn: parent
                                            text: "✕"
                                            font.pixelSize: 12
                                            font.bold: true
                                            color: rmDirM.containsMouse ? root.colRed : root.colFgMuted
                                        }
                                        MouseArea {
                                            id: rmDirM
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: root.removeDir(modelData)
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                // -------------------------------------------------------------
                // 2. MAIN SPLIT VIEW (Gallery Grid + Styled Scroller + Live Preview)
                // -------------------------------------------------------------
                RowLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    spacing: 16

                    // LEFT: 3-Column Wallpaper Grid with Visible Garchy Scroller
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        radius: 6
                        color: root.colBgAlt
                        border.color: root.withAlpha(root.colBorder, 0.3)
                        border.width: 1.0
                        clip: true

                        GridView {
                            id: wallGrid
                            anchors.fill: parent
                            anchors.margins: 10
                            cellWidth: (width - 24) / 3
                            cellHeight: cellWidth * (9.0 / 16.0) + 40
                            clip: true

                            model: root.filteredList()

                            // GARCHY HARDWARE-STYLED SMOOTH SCROLLBAR
                            ScrollBar.vertical: ScrollBar {
                                id: wallScrollBar
                                policy: ScrollBar.AlwaysOn
                                active: true
                                width: 8

                                contentItem: Rectangle {
                                    implicitWidth: 8
                                    radius: 4
                                    color: wallScrollBar.pressed ? root.colGold : (wallScrollBar.hovered ? root.colAccent : root.withAlpha(root.colAccent, 0.6))
                                    Behavior on color { ColorAnimation { duration: 100 } }
                                }

                                background: Rectangle {
                                    implicitWidth: 8
                                    radius: 4
                                    color: root.withAlpha(root.colCard, 0.6)
                                }
                            }

                            delegate: Item {
                                id: delegateRoot
                                width: wallGrid.cellWidth
                                height: wallGrid.cellHeight
                                property bool isSelected: root.selectedPath === modelData.path
                                property bool isCurrentActive: root.wallpaperData.current === modelData.path

                                Rectangle {
                                    anchors.fill: parent
                                    anchors.margins: 5
                                    radius: 6

                                    color: delegateRoot.isSelected ? root.withAlpha(root.colAccent, 0.25) : (cardM.containsMouse ? root.withAlpha(root.colAccent, 0.14) : root.colCard)
                                    border.color: delegateRoot.isSelected ? root.colAccent : (cardM.containsMouse ? root.colAccent : root.withAlpha(root.colBorder, 0.25))
                                    border.width: delegateRoot.isSelected ? 1.5 : 1.0

                                    scale: cardM.containsMouse ? 1.02 : 1.0
                                    Behavior on scale { NumberAnimation { duration: 100 } }

                                    ColumnLayout {
                                        anchors.fill: parent
                                        anchors.margins: 5
                                        spacing: 5

                                        // Wallpaper Thumbnail
                                        Rectangle {
                                            Layout.fillWidth: true
                                            Layout.fillHeight: true
                                            radius: 4
                                            clip: true
                                            color: "#050811"

                                            Image {
                                                anchors.fill: parent
                                                source: modelData.path
                                                sourceSize: Qt.size(240, 135)
                                                fillMode: Image.PreserveAspectCrop
                                                asynchronous: true
                                                smooth: true
                                            }

                                            // Active Indicator Badge
                                            Rectangle {
                                                visible: delegateRoot.isCurrentActive
                                                anchors.top: parent.top
                                                anchors.left: parent.left
                                                anchors.margins: 5
                                                height: 18
                                                width: actTxt.implicitWidth + 10
                                                radius: 3
                                                color: root.colGreen

                                                Text {
                                                    id: actTxt
                                                    anchors.centerIn: parent
                                                    text: "✓ ACTIVE"
                                                    font.pixelSize: 9
                                                    font.bold: true
                                                    color: "#000000"
                                                }
                                            }
                                        }

                                        // Filename & Size footer
                                        RowLayout {
                                            Layout.fillWidth: true
                                            spacing: 6

                                            Text {
                                                Layout.fillWidth: true
                                                text: modelData.name
                                                font.pixelSize: 11
                                                font.bold: true
                                                color: delegateRoot.isSelected ? root.colAccent : root.colFg
                                                elide: Text.ElideRight
                                            }

                                            Text {
                                                text: modelData.size_mb + "M"
                                                font.pixelSize: 10
                                                font.bold: true
                                                color: root.colFgMuted
                                            }
                                        }
                                    }

                                    MouseArea {
                                        id: cardM
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: {
                                            root.selectedPath = modelData.path;
                                            root.selectedName = modelData.name;
                                            root.selectedFolder = modelData.folder;
                                        }
                                        onDoubleClicked: {
                                            root.selectedPath = modelData.path;
                                            root.applyTarget("desktop");
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // RIGHT: Cinema Preview & Control Panel (360px)
                    Rectangle {
                        Layout.preferredWidth: 360
                        Layout.fillHeight: true
                        radius: 6
                        color: root.colBgAlt
                        border.color: root.withAlpha(root.colBorder, 0.3)
                        border.width: 1.0

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 14
                            spacing: 12

                            Text {
                                text: "🎬 Cinema Preview"
                                font.family: "Orbitron"
                                font.pixelSize: 13
                                font.bold: true
                                color: root.colAccent
                            }

                            // Large 16:9 Hero Frame
                            Rectangle {
                                Layout.fillWidth: true
                                height: 195
                                radius: 6
                                clip: true
                                color: "#000000"
                                border.color: root.colAccent
                                border.width: 1.0

                                Image {
                                    anchors.fill: parent
                                    source: root.selectedPath
                                    fillMode: Image.PreserveAspectCrop
                                    asynchronous: true
                                    smooth: true
                                }
                            }

                            // Selected Metadata Card
                            Rectangle {
                                Layout.fillWidth: true
                                height: 56
                                radius: 5
                                color: root.colCard
                                border.color: root.withAlpha(root.colBorder, 0.25)
                                border.width: 1.0

                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: 8
                                    spacing: 3

                                    Text {
                                        Layout.fillWidth: true
                                        text: root.selectedName || "No Wallpaper Selected"
                                        font.pixelSize: 12
                                        font.bold: true
                                        color: root.colFg
                                        elide: Text.ElideRight
                                    }

                                    Text {
                                        Layout.fillWidth: true
                                        text: root.selectedPath || ""
                                        font.pixelSize: 10
                                        color: root.colFgMuted
                                        elide: Text.ElideMiddle
                                    }
                                }
                            }

                            Item { Layout.fillHeight: true }

                            // Action Buttons
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 8

                                // 1. Apply Desktop
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 40
                                    radius: 5
                                    color: dtBtnM.containsMouse ? root.colAccent : root.withAlpha(root.colAccent, 0.25)
                                    border.color: root.colAccent
                                    border.width: 1.0

                                    RowLayout {
                                        anchors.centerIn: parent
                                        spacing: 8
                                        Text { text: "🖼️"; font.pixelSize: 14 }
                                        Text {
                                            text: "Apply Desktop Wallpaper"
                                            font.pixelSize: 12
                                            font.bold: true
                                            color: dtBtnM.containsMouse ? "#080c16" : root.colFg
                                        }
                                    }

                                    MouseArea {
                                        id: dtBtnM
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: root.applyTarget("desktop")
                                    }
                                }

                                // 2. Apply SDDM Login
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 40
                                    radius: 5
                                    color: sddmBtnM.containsMouse ? root.colAccentAlt : root.withAlpha(root.colAccentAlt, 0.25)
                                    border.color: root.colAccentAlt
                                    border.width: 1.0

                                    RowLayout {
                                        anchors.centerIn: parent
                                        spacing: 8
                                        Text { text: "🔒"; font.pixelSize: 14 }
                                        Text {
                                            text: "Apply SDDM Login Background"
                                            font.pixelSize: 12
                                            font.bold: true
                                            color: sddmBtnM.containsMouse ? "#ffffff" : root.colFg
                                        }
                                    }

                                    MouseArea {
                                        id: sddmBtnM
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: root.applyTarget("sddm")
                                    }
                                }

                                // 3. Apply Both
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 40
                                    radius: 5
                                    color: bothBtnM.containsMouse ? root.colGold : root.withAlpha(root.colGold, 0.25)
                                    border.color: root.colGold
                                    border.width: 1.0

                                    RowLayout {
                                        anchors.centerIn: parent
                                        spacing: 8
                                        Text { text: "✨"; font.pixelSize: 14 }
                                        Text {
                                            text: "Apply to BOTH (Desktop + SDDM)"
                                            font.pixelSize: 12
                                            font.bold: true
                                            color: bothBtnM.containsMouse ? "#080c16" : root.colFg
                                        }
                                    }

                                    MouseArea {
                                        id: bothBtnM
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: root.applyTarget("both")
                                    }
                                }

                                // 4. Random Button
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 34
                                    radius: 5
                                    color: rndBtnM.containsMouse ? root.withAlpha(root.colAccent, 0.20) : root.colCard
                                    border.color: root.withAlpha(root.colBorder, 0.4)
                                    border.width: 1.0

                                    RowLayout {
                                        anchors.centerIn: parent
                                        spacing: 8
                                        Text { text: "🎲"; font.pixelSize: 13 }
                                        Text {
                                            text: "Random Wallpaper"
                                            font.pixelSize: 11
                                            font.bold: true
                                            color: root.colFg
                                        }
                                    }

                                    MouseArea {
                                        id: rndBtnM
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: root.selectRandom()
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
