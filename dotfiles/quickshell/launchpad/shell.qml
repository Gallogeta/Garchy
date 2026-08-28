import Quickshell
import Quickshell.Wayland
import Quickshell.Io
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

PanelWindow {
    id: root

    // Target Left/Primary Monitor (DP-2) or primary focused screen
    screen: {
        for (var i = 0; i < Quickshell.screens.length; i++) {
            if (Quickshell.screens[i].name === "DP-2") {
                return Quickshell.screens[i];
            }
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
    WlrLayershell.namespace: "launchpad"
    WlrLayershell.keyboardFocus: WlrKeyboardFocus.Exclusive
    exclusionMode: "Ignore"

    // Garchy OS Strict 5-Color Palette
    readonly property color colLightBlue: "#38bdf8"
    readonly property color colBlue: "#3b82f6"
    readonly property color colGold: "#fbbf24"
    readonly property color colLightGrey: "#e2e8f0"
    readonly property color colDarkObsidian: "#0a0f1d99" // 60% translucent frosted glass obsidian
    readonly property color colCardBg: "#131c31B3"      // 70% glass card

    property var allApps: []
    property var filteredApps: []
    property string searchText: ""

    function closeLaunchpad() {
        Qt.quit();
    }

    function launchApp(execCmd) {
        if (!execCmd) return;
        Quickshell.execDetached(["sh", "-c", execCmd + " &"]);
        closeLaunchpad();
    }

    function filterApps() {
        if (!allApps || allApps.length === 0) {
            filteredApps = [];
            return;
        }
        var query = searchText.trim().toLowerCase();
        if (query === "") {
            filteredApps = allApps;
        } else {
            var res = [];
            for (var i = 0; i < allApps.length; i++) {
                var app = allApps[i];
                if (app.name.toLowerCase().indexOf(query) !== -1) {
                    res.push(app);
                }
            }
            filteredApps = res;
        }
    }

    FileView {
        id: appsFile
        path: "/home/gallo/.cache/quickshell_launchpad_apps.json"
        watchChanges: true
        onFileChanged: loadJson()
    }

    function loadJson() {
        try {
            var content = appsFile.text();
            if (content && content.length > 5) {
                allApps = JSON.parse(content);
                filterApps();
            } else {
                Quickshell.execDetached(["python3", "/home/gallo/.config/quickshell/launchpad/get_apps.py", "--refresh"]);
            }
        } catch (e) {
            console.log("Error loading apps JSON:", e);
            Quickshell.execDetached(["python3", "/home/gallo/.config/quickshell/launchpad/get_apps.py", "--refresh"]);
        }
    }

    Component.onCompleted: {
        loadJson();
        searchInput.forceActiveFocus();
    }

    // Background Clickable Overlay (Click outside to close)
    Rectangle {
        id: bgOverlay
        anchors.fill: parent
        color: colDarkObsidian

        MouseArea {
            anchors.fill: parent
            onClicked: closeLaunchpad()
        }

        // Main Container
        Item {
            id: mainContainer
            anchors.fill: parent
            anchors.margins: 40

            // Catch clicks inside main container so it doesn't close
            MouseArea {
                anchors.fill: parent
                onClicked: (mouse) => mouse.accepted = true
            }

            ColumnLayout {
                anchors.fill: parent
                spacing: 24

                // Top Search Bar
                Rectangle {
                    Layout.alignment: Qt.AlignHCenter
                    Layout.preferredWidth: Math.min(800, parent.width * 0.7)
                    Layout.preferredHeight: 56
                    radius: 28
                    color: "#131c31E6"
                    border.width: searchInput.activeFocus ? 2 : 1
                    border.color: searchInput.activeFocus ? colLightBlue : Qt.rgba(56/255, 189/255, 248/255, 0.3)

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 20
                        anchors.rightMargin: 20
                        spacing: 12

                        Text {
                            text: "🔍"
                            font.pixelSize: 18
                        }

                        TextInput {
                            id: searchInput
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            verticalAlignment: TextInput.AlignVCenter
                            font.family: "JetBrainsMono Nerd Font"
                            font.pixelSize: 15
                            font.bold: true
                            color: "#ffffff"
                            clip: true

                            Text {
                                text: "Type to filter applications..."
                                font: searchInput.font
                                color: Qt.rgba(226/255, 232/255, 240/255, 0.4)
                                visible: !searchInput.text && !searchInput.inputMethodComposing
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            onTextChanged: {
                                searchText = text;
                                filterApps();
                            }

                            Keys.onEscapePressed: closeLaunchpad()
                            Keys.onReturnPressed: {
                                if (filteredApps.length > 0) {
                                    launchApp(filteredApps[0].exec);
                                }
                            }
                        }

                        // App Counter Badge
                        Rectangle {
                            Layout.preferredHeight: 28
                            Layout.preferredWidth: countText.implicitWidth + 16
                            radius: 14
                            color: Qt.rgba(251/255, 191/255, 36/255, 0.15)
                            border.width: 1
                            border.color: colGold

                            Text {
                                id: countText
                                anchors.centerIn: parent
                                text: filteredApps.length + " Apps"
                                font.family: "JetBrainsMono Nerd Font"
                                font.pixelSize: 11
                                font.bold: true
                                color: colGold
                            }
                        }
                    }
                }

                // Grid + Grabbable Scrollbar Layout
                RowLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    spacing: 16

                    // App Cards GridView
                    GridView {
                        id: appGrid
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true

                        cellWidth: Math.floor(width / 6)
                        cellHeight: 140

                        model: filteredApps

                        interactive: true
                        boundsBehavior: Flickable.StopAtBounds

                        delegate: Item {
                            width: appGrid.cellWidth
                            height: appGrid.cellHeight

                            Rectangle {
                                id: card
                                anchors.fill: parent
                                anchors.margins: 6
                                radius: 16
                                color: cardMouse.containsMouse ? Qt.rgba(56/255, 189/255, 248/255, 0.25) : colCardBg
                                border.width: 1
                                border.color: cardMouse.containsMouse ? colLightBlue : Qt.rgba(56/255, 189/255, 248/255, 0.15)
                                scale: cardMouse.containsMouse ? 1.04 : 1.0

                                Behavior on scale {
                                    NumberAnimation { duration: 80; easing.type: Easing.OutQuad }
                                }
                                Behavior on color {
                                    ColorAnimation { duration: 80 }
                                }

                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: 12
                                    spacing: 8

                                    // App Icon
                                    Image {
                                        Layout.alignment: Qt.AlignHCenter
                                        Layout.preferredWidth: 54
                                        Layout.preferredHeight: 54
                                        source: modelData.icon || ""
                                        sourceSize.width: 128
                                        sourceSize.height: 128
                                        fillMode: Image.PreserveAspectFit
                                        smooth: true
                                        mipmap: true
                                        asynchronous: true

                                        // Fallback icon if error
                                        Text {
                                            anchors.centerIn: parent
                                            text: "🚀"
                                            font.pixelSize: 32
                                            visible: parent.status === Image.Error || parent.status === Image.Null
                                        }
                                    }

                                    // App Name
                                    Text {
                                        Layout.fillWidth: true
                                        Layout.alignment: Qt.AlignHCenter
                                        text: modelData.name
                                        font.family: "JetBrainsMono Nerd Font"
                                        font.pixelSize: 11
                                        font.bold: true
                                        color: cardMouse.containsMouse ? "#ffffff" : colLightGrey
                                        horizontalAlignment: Text.AlignHCenter
                                        elide: Text.ElideRight
                                        maximumLineCount: 2
                                        wrapMode: Text.Wrap
                                    }
                                }

                                MouseArea {
                                    id: cardMouse
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: launchApp(modelData.exec)
                                }
                            }
                        }
                    }

                    // 100% Grabbable & Interactive Scrollbar
                    Rectangle {
                        id: scrollTrack
                        Layout.preferredWidth: 14
                        Layout.fillHeight: true
                        radius: 7
                        color: Qt.rgba(30/255, 41/255, 59/255, 0.7)
                        border.width: 1
                        border.color: Qt.rgba(56/255, 189/255, 248/255, 0.25)
                        visible: appGrid.contentHeight > appGrid.height

                        // Calculate Scroll handle height proportionally
                        property real visibleRatio: Math.min(1.0, appGrid.height / Math.max(1, appGrid.contentHeight))
                        property real handleHeight: Math.max(40, scrollTrack.height * visibleRatio)
                        property real maxHandleY: scrollTrack.height - handleHeight
                        property real scrollProgress: appGrid.contentHeight > appGrid.height ? 
                                                      (appGrid.contentY / (appGrid.contentHeight - appGrid.height)) : 0

                        // Track Click to Jump
                        MouseArea {
                            anchors.fill: parent
                            onClicked: (mouse) => {
                                var ratio = Math.max(0, Math.min(1, (mouse.y - scrollTrack.handleHeight / 2) / scrollTrack.maxHandleY));
                                appGrid.contentY = ratio * (appGrid.contentHeight - appGrid.height);
                            }
                        }

                        // Grabbable Handle
                        Rectangle {
                            id: scrollHandle
                            width: parent.width
                            height: scrollTrack.handleHeight
                            radius: 7
                            y: Math.max(0, Math.min(scrollTrack.maxHandleY, scrollTrack.scrollProgress * scrollTrack.maxHandleY))
                            color: handleMouse.containsMouse || handleMouse.drag.active ? colLightBlue : Qt.rgba(56/255, 189/255, 248/255, 0.8)

                            Behavior on color {
                                ColorAnimation { duration: 100 }
                            }

                            // Interactive Drag Area
                            MouseArea {
                                id: handleMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor

                                drag.target: scrollHandle
                                drag.axis: Drag.YAxis
                                drag.minimumY: 0
                                drag.maximumY: scrollTrack.maxHandleY

                                onPositionChanged: {
                                    if (drag.active) {
                                        var ratio = scrollHandle.y / scrollTrack.maxHandleY;
                                        appGrid.contentY = ratio * (appGrid.contentHeight - appGrid.height);
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
