import Quickshell
import Quickshell.Wayland
import Quickshell.Widgets
import Quickshell.Io
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

ShellRoot {
    id: root

    // Active Theme State
    property var activeTheme: ({})
    property var themeList: []

    FileView {
        path: "/home/gallo/.config/gally/active_theme.json"
        watchChanges: true
        onLoaded: {
            try {
                root.activeTheme = JSON.parse(text());
            } catch(e) {}
        }
        onFileChanged: {
            try {
                root.activeTheme = JSON.parse(text());
            } catch(e) {}
        }
    }

    Process {
        id: listProc
        command: ["python3", "/home/gallo/.config/hypr/scripts/gally_theme_helper.py", "list"]
        running: true
        stdout: SplitParser {
            onRead: data => {
                try {
                    root.themeList = JSON.parse(data.trim());
                } catch(e) {}
            }
        }
    }

    Process {
        id: applyProc
        function apply(themeId) {
            running = false;
            command = ["python3", "/home/gallo/.config/hypr/scripts/gally_theme_helper.py", "apply", themeId];
            running = true;
        }
    }

    PanelWindow {
        id: themeWin
        anchors {
            top: true
            bottom: true
            left: true
            right: true
        }
        color: "#00000088"
        WlrLayershell.layer: WlrLayer.Overlay
        WlrLayershell.keyboardFocus: WlrKeyboardFocus.Exclusive
        WlrLayershell.namespace: "garchy-theme-switcher"

        // Backdrop click to close
        MouseArea {
            anchors.fill: parent
            onClicked: Qt.quit()
        }

        // Keyboard handler (ESC to quit)
        Item {
            focus: true
            Keys.onEscapePressed: Qt.quit()
            Keys.onBackPressed: Qt.quit()
        }

        // Center Modal Dialog
        Rectangle {
            anchors.centerIn: parent
            width: 880
            height: 580
            radius: Math.max(8, (root.activeTheme.rounding || 8) + 4)
            color: root.activeTheme.bg ? root.activeTheme.bg : "#070b12"
            border.color: root.activeTheme.accent || "#38bdf8"
            border.width: 1.5

            // Prevent backdrop click inside modal
            MouseArea {
                anchors.fill: parent
                onClicked: {}
            }

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 24
                spacing: 16

                // Header
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12

                    Text {
                        text: "󰏘"
                        font.pixelSize: 26
                        color: root.activeTheme.accent || "#38bdf8"
                    }

                    ColumnLayout {
                        spacing: 2
                        Text {
                            text: "Garchy OS Theme Gallery"
                            font.pixelSize: 18
                            font.bold: true
                            color: root.activeTheme.fg || "#f8fafc"
                        }
                        Text {
                            text: "Select a theme to instantly synchronize Hyprland, Quickshell, GTK, Rofi, and Kitty"
                            font.pixelSize: 11
                            color: root.activeTheme.fg_muted || "#94a3b8"
                        }
                    }

                    Item { Layout.fillWidth: true }

                    // Close Button
                    Rectangle {
                        width: 32
                        height: 32
                        radius: 6
                        color: closeMouse.containsMouse ? "#ef4444" : (root.activeTheme.bg_card || "#0f172a")
                        border.color: closeMouse.containsMouse ? "#ef4444" : (root.activeTheme.border || "#1e293b")
                        border.width: 1

                        Text {
                            anchors.centerIn: parent
                            text: "✕"
                            font.pixelSize: 12
                            font.bold: true
                            color: closeMouse.containsMouse ? "#ffffff" : (root.activeTheme.fg || "#f8fafc")
                        }

                        MouseArea {
                            id: closeMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: Qt.quit()
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: root.activeTheme.border || "#1e293b"
                }

                // 3x2 Grid of Theme Cards
                GridLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    columns: 3
                    rowSpacing: 14
                    columnSpacing: 14

                    Repeater {
                        model: root.themeList

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            property bool isCurrent: (root.activeTheme.id === modelData.id || root.activeTheme.name === modelData.name)
                            radius: Math.max(6, (modelData.rounding || 8))
                            color: cardMouse.containsMouse ? (modelData.bg_alt || "#141e33") : (modelData.bg_card || "#0f172a")
                            border.color: isCurrent ? (modelData.accent || "#38bdf8") : (cardMouse.containsMouse ? (modelData.accent_alt || "#2563eb") : (modelData.border || "#1e293b"))
                            border.width: isCurrent ? 2 : 1

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 14
                                spacing: 8

                                // Top row: Title + Active Badge
                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 6

                                    Text {
                                        Layout.fillWidth: true
                                        text: modelData.name
                                        font.pixelSize: 13
                                        font.bold: true
                                        elide: Text.ElideRight
                                        color: isCurrent ? (modelData.accent || "#38bdf8") : (modelData.fg || "#f8fafc")
                                    }

                                    Rectangle {
                                        visible: isCurrent
                                        width: 58
                                        height: 18
                                        radius: 4
                                        color: (modelData.accent || "#38bdf8") + "33"
                                        border.color: modelData.accent || "#38bdf8"
                                        border.width: 1

                                        Text {
                                            anchors.centerIn: parent
                                            text: "✓ ACTIVE"
                                            font.pixelSize: 8
                                            font.bold: true
                                            color: modelData.accent || "#38bdf8"
                                        }
                                    }
                                }

                                // Description
                                Text {
                                    Layout.fillWidth: true
                                    text: modelData.desc || ""
                                    font.pixelSize: 10
                                    color: modelData.fg_muted || "#94a3b8"
                                    wrapMode: Text.WordWrap
                                    maximumLineCount: 2
                                    elide: Text.ElideRight
                                }

                                Item { Layout.fillHeight: true }

                                // 5-Color Palette Swatches
                                Row {
                                    spacing: 6
                                    Layout.alignment: Qt.AlignLeft

                                    Repeater {
                                        model: modelData.colors || [modelData.bg, modelData.accent, modelData.accent_alt, modelData.fg, "#fbbf24"]

                                        Rectangle {
                                            width: 22
                                            height: 14
                                            radius: 3
                                            color: modelData
                                            border.color: "#ffffff22"
                                            border.width: 1
                                        }
                                    }
                                }

                                // Apply Action Bar / Rounding tag
                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 6

                                    Text {
                                        text: "Rounding: " + (modelData.rounding || 8) + "px"
                                        font.pixelSize: 9
                                        color: modelData.fg_muted || "#94a3b8"
                                    }

                                    Item { Layout.fillWidth: true }

                                    Rectangle {
                                        width: 72
                                        height: 22
                                        radius: 4
                                        color: isCurrent ? (modelData.accent || "#38bdf8") : (applyBtnMouse.containsMouse ? (modelData.accent || "#38bdf8") : (modelData.bg || "#070b12"))
                                        border.color: modelData.accent || "#38bdf8"
                                        border.width: 1

                                        Text {
                                            anchors.centerIn: parent
                                            text: isCurrent ? "Selected" : "Apply"
                                            font.pixelSize: 10
                                            font.bold: true
                                            color: isCurrent ? "#070b12" : (applyBtnMouse.containsMouse ? "#070b12" : (modelData.accent || "#38bdf8"))
                                        }

                                        MouseArea {
                                            id: applyBtnMouse
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: {
                                                applyProc.apply(modelData.id);
                                            }
                                        }
                                    }
                                }
                            }

                            MouseArea {
                                id: cardMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                z: -1
                                onClicked: {
                                    applyProc.apply(modelData.id);
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
