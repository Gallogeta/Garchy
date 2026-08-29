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

    // =========================================================================
    // 🧠 GALLY AI CHAT STATE & HISTORY
    // =========================================================================
    property var chatHistory: []
    property string activeModel: "qwen2.5:0.5b"
    property bool isVoiceEnabled: true

    FileView {
        id: historyFile
        path: "/tmp/gally_chat_history.json"
        watchChanges: true
        onLoaded: {
            try {
                root.chatHistory = JSON.parse(text());
                chatListView.positionViewAtEnd();
            } catch(e){}
        }
        onFileChanged: {
            reload();
            try {
                root.chatHistory = JSON.parse(text());
                chatListView.positionViewAtEnd();
            } catch(e){}
        }
    }

    function sendPrompt(p) {
        if (!p || !p.trim()) return;
        var text = p.trim();
        promptInput.text = "";
        runCmd(["python3", "/home/gallo/.config/hypr/scripts/gally_chat_service.py", "send", text]);
    }

    function clearChat() {
        runCmd(["python3", "/home/gallo/.config/hypr/scripts/gally_chat_service.py", "clear"]);
    }

    function setModel(m) {
        root.activeModel = m;
        runCmd(["python3", "/home/gallo/.config/hypr/scripts/gally_chat_service.py", "set-model", m]);
    }

    function toggleVoice() {
        root.isVoiceEnabled = !root.isVoiceEnabled;
        runCmd(["python3", "/home/gallo/.config/hypr/scripts/gally_chat_service.py", "toggle-voice"]);
    }

    // =========================================================================
    // 🌌 FULLSCREEN CAELESTIA GALLY AI STUDIO
    // =========================================================================
    PanelWindow {
        id: aiStudioWin
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
        WlrLayershell.namespace: "caelestia-ai"
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

        // Center Floating Obsidian Glass Studio Card
        Rectangle {
            id: mainCard
            anchors.centerIn: parent
            width: Math.min(1060, parent.width - 60)
            height: Math.min(760, parent.height - 60)
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
                // 1. TOP HEADER (Emblem, Neural Tier Selector, Actions, Close)
                // -------------------------------------------------------------
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 14

                    // Emblem & Identity
                    RowLayout {
                        spacing: 10
                        Rectangle {
                            width: 42
                            height: 42
                            radius: 6
                            color: root.withAlpha(root.colAccent, 0.22)
                            border.color: root.colAccent
                            border.width: 1.0
                            Text { anchors.centerIn: parent; text: "󰚩"; font.pixelSize: 24; color: root.colAccent }
                        }
                        ColumnLayout {
                            spacing: 1
                            Text {
                                text: "Gally AI Neural Studio"
                                font.family: "Orbitron"
                                font.pixelSize: 18
                                font.bold: true
                                color: root.colFg
                            }
                            Text {
                                text: "Cephalon 3-Tier Multi-Provider Neural Router"
                                font.pixelSize: 11
                                color: root.colFgMuted
                            }
                        }
                    }

                    Item { Layout.fillWidth: true }

                    // Neural Tier Selector Pills
                    Row {
                        spacing: 5
                        Repeater {
                            model: [
                                { id: "qwen2.5:0.5b", label: "⚡ Qwen (Tier 1)" },
                                { id: "gally-cephalon-ai", label: "🌌 Cephalon (Tier 2)" },
                                { id: "hermes3:8b", label: "🚀 Hermes (Tier 3)" },
                                { id: "gemini-1.5-flash", label: "✨ Gemini" }
                            ]
                            Rectangle {
                                property bool isSel: root.activeModel === modelData.id
                                height: 32
                                width: tierTxt.implicitWidth + 18
                                radius: 5
                                color: isSel ? root.colGold : (tierM.containsMouse ? root.withAlpha(root.colGold, 0.25) : root.colBgAlt)
                                border.color: isSel ? root.colGold : root.withAlpha(root.colBorder, 0.35)
                                border.width: 1.0

                                Text {
                                    id: tierTxt
                                    anchors.centerIn: parent
                                    text: modelData.label
                                    font.pixelSize: 12
                                    font.bold: isSel
                                    color: isSel ? "#080c16" : (tierM.containsMouse ? root.colGold : root.colFg)
                                }

                                MouseArea {
                                    id: tierM
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: root.setModel(modelData.id)
                                }
                            }
                        }
                    }

                    // Voice Synthesis Toggle
                    Rectangle {
                        height: 32
                        width: voiceTxt.implicitWidth + 18
                        radius: 5
                        color: root.isVoiceEnabled ? root.withAlpha(root.colAccent, 0.25) : root.colBgAlt
                        border.color: root.isVoiceEnabled ? root.colAccent : root.withAlpha(root.colBorder, 0.35)
                        border.width: 1.0

                        RowLayout {
                            id: voiceTxt
                            anchors.centerIn: parent
                            spacing: 5
                            Text { text: root.isVoiceEnabled ? "🔊" : "🔇"; font.pixelSize: 13 }
                            Text {
                                text: root.isVoiceEnabled ? "Voice ON" : "Voice OFF"
                                font.pixelSize: 12
                                font.bold: true
                                color: root.isVoiceEnabled ? root.colAccent : root.colFgMuted
                            }
                        }

                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: root.toggleVoice()
                        }
                    }

                    // Clear Buffer Button
                    Rectangle {
                        height: 32
                        width: clrTxt.implicitWidth + 16
                        radius: 5
                        color: clrM.containsMouse ? root.withAlpha(root.colRed, 0.3) : root.colBgAlt
                        border.color: clrM.containsMouse ? root.colRed : root.withAlpha(root.colBorder, 0.35)
                        border.width: 1.0

                        RowLayout {
                            id: clrTxt
                            anchors.centerIn: parent
                            spacing: 5
                            Text { text: "🗑️"; font.pixelSize: 12 }
                            Text { text: "Clear"; font.pixelSize: 12; font.bold: true; color: clrM.containsMouse ? root.colRed : root.colFgMuted }
                        }

                        MouseArea {
                            id: clrM
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: root.clearChat()
                        }
                    }

                    // Close Button
                    Rectangle {
                        width: 32
                        height: 32
                        radius: 5
                        color: closeM.containsMouse ? root.withAlpha(root.colRed, 0.3) : root.colBgAlt
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

                // Divider
                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: root.withAlpha(root.colBorder, 0.3)
                }

                // -------------------------------------------------------------
                // 2. CHAT CONVERSATION STREAMING SCROLLVIEW
                // -------------------------------------------------------------
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    radius: 6
                    color: root.colBgAlt
                    border.color: root.withAlpha(root.colBorder, 0.3)
                    border.width: 1.0
                    clip: true

                    ListView {
                        id: chatListView
                        anchors.fill: parent
                        anchors.margins: 14
                        spacing: 12
                        clip: true

                        model: root.chatHistory || []

                        ScrollBar.vertical: ScrollBar {
                            id: chatScrollBar
                            policy: ScrollBar.AlwaysOn
                            active: true
                            width: 8

                            contentItem: Rectangle {
                                implicitWidth: 8
                                radius: 4
                                color: chatScrollBar.pressed ? root.colGold : (chatScrollBar.hovered ? root.colAccent : root.withAlpha(root.colAccent, 0.6))
                            }

                            background: Rectangle {
                                implicitWidth: 8
                                radius: 4
                                color: root.withAlpha(root.colCard, 0.6)
                            }
                        }

                        delegate: Item {
                            width: chatListView.width - 24
                            height: msgBubble.implicitHeight + 10
                            property bool isUser: modelData.role === "user"

                            Rectangle {
                                id: msgBubble
                                anchors.right: isUser ? parent.right : undefined
                                anchors.left: isUser ? undefined : parent.left
                                width: Math.min(parent.width * 0.85, msgCol.implicitWidth + 28)
                                height: msgCol.implicitHeight + 20
                                radius: 6

                                color: isUser ? root.withAlpha(root.colAccentAlt, 0.25) : root.colCard
                                border.color: isUser ? root.colAccent : root.withAlpha(root.colGold, 0.4)
                                border.width: 1.0

                                ColumnLayout {
                                    id: msgCol
                                    anchors.fill: parent
                                    anchors.margins: 10
                                    spacing: 6

                                    // Header (Author + Timestamp)
                                    RowLayout {
                                        Layout.fillWidth: true
                                        spacing: 8

                                        Text {
                                            text: isUser ? "󰣇 gallo (Operator)" : "󰚩 Cephalon Gally"
                                            font.family: "Orbitron"
                                            font.pixelSize: 11
                                            font.bold: true
                                            color: isUser ? root.colAccent : root.colGold
                                        }

                                        Item { Layout.fillWidth: true }

                                        Text {
                                            text: modelData.timestamp || ""
                                            font.pixelSize: 10
                                            color: root.colFgMuted
                                        }
                                    }

                                    // Message Body
                                    TextEdit {
                                        Layout.fillWidth: true
                                        text: modelData.text || ""
                                        font.pixelSize: 13
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

                // -------------------------------------------------------------
                // 3. QUICK PROMPT CHIPS
                // -------------------------------------------------------------
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    Repeater {
                        model: [
                            "🎮 Optimize 144Hz Gaming Mode",
                            "📊 Run System Diagnostics",
                            "☢️ Check Fallout 4 Modding Health",
                            "🎨 Garchy Theme Palette Helper"
                        ]

                        Rectangle {
                            height: 28
                            width: chipTxt.implicitWidth + 16
                            radius: 4
                            color: chipM.containsMouse ? root.withAlpha(root.colAccent, 0.25) : root.colBgAlt
                            border.color: chipM.containsMouse ? root.colAccent : root.withAlpha(root.colBorder, 0.35)
                            border.width: 1.0

                            Text {
                                id: chipTxt
                                anchors.centerIn: parent
                                text: modelData
                                font.pixelSize: 11
                                font.bold: true
                                color: chipM.containsMouse ? root.colAccent : root.colFgMuted
                            }

                            MouseArea {
                                id: chipM
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: root.sendPrompt(modelData)
                            }
                        }
                    }
                }

                // -------------------------------------------------------------
                // 4. BOTTOM INTERACTIVE PROMPT INPUT BAR
                // -------------------------------------------------------------
                Rectangle {
                    Layout.fillWidth: true
                    height: 52
                    radius: 6
                    color: root.colBgAlt
                    border.color: promptInput.activeFocus ? root.colAccent : root.withAlpha(root.colBorder, 0.4)
                    border.width: promptInput.activeFocus ? 1.5 : 1.0

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 10

                        Text { text: "💬"; font.pixelSize: 16 }

                        TextInput {
                            id: promptInput
                            Layout.fillWidth: true
                            color: root.colFg
                            font.pixelSize: 14
                            focus: true
                            selectByMouse: true

                            Keys.onReturnPressed: {
                                root.sendPrompt(text);
                            }
                            Keys.onEscapePressed: Qt.quit()
                        }

                        Text {
                            visible: !promptInput.text
                            text: "Ask Gally AI anything, request system fixes, or query Cephalon matrix..."
                            font.pixelSize: 13
                            color: root.colFgMuted
                        }

                        // Send Button
                        Rectangle {
                            height: 34
                            width: sendTxt.implicitWidth + 18
                            radius: 5
                            color: sendM.containsMouse ? root.colAccent : root.withAlpha(root.colAccent, 0.3)
                            border.color: root.colAccent
                            border.width: 1.0

                            RowLayout {
                                id: sendTxt
                                anchors.centerIn: parent
                                spacing: 6
                                Text { text: "🚀"; font.pixelSize: 13 }
                                Text {
                                    text: "Send"
                                    font.pixelSize: 12
                                    font.bold: true
                                    color: sendM.containsMouse ? "#080c16" : root.colFg
                                }
                            }

                            MouseArea {
                                id: sendM
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: root.sendPrompt(promptInput.text)
                            }
                        }
                    }
                }
            }
        }
    }
}
