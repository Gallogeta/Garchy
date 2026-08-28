import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Qt5Compat.GraphicalEffects

Item {
    id: root
    width: 1920
    height: 1080

    // Sci-Fi Orokin & Void Palette (Clean & Free of Third-Party Terms)
    readonly property color colAccent: config.accentColor || "#00f0ff"
    readonly property color colGold: config.goldColor || "#fbbf24"
    readonly property color colText: config.textColor || "#f1f5f9"
    readonly property color colSubtext: config.subtextColor || "#94a3b8"
    readonly property color colCardBg: config.cardBg || "#e6050914"
    readonly property color colInputBg: config.inputBg || "#f203060f"
    readonly property color colError: config.errorColor || "#f43f5e"
    readonly property color colSuccess: config.successColor || "#34d399"
    readonly property string fontFam: config.font || "JetBrainsMono Nerd Font"

    property bool isAuthenticating: false
    property bool showPassword: false
    property string statusText: ""
    property color statusColor: colSubtext

    // Connections to SDDM Greeter Events
    Connections {
        target: sddm

        function onLoginSucceeded() {
            root.isAuthenticating = false
            root.statusColor = root.colSuccess
            root.statusText = "[ AUTH_GRANTED // SPAWNING SESSION ]"
        }

        function onLoginFailed() {
            root.isAuthenticating = false
            passwordInput.text = ""
            root.statusColor = root.colError
            root.statusText = "[ CIPHER REJECTED // ACCESS DENIED ]"
            shakeAnimation.restart()
            passwordInput.forceActiveFocus()
        }

        function onInformationMessage(message) {
            root.statusColor = root.colAccent
            root.statusText = "[ CEPHALON ] " + message
        }
    }

    // ----------------------------------------------------
    // BASE WALLPAPER BACKGROUND
    // ----------------------------------------------------
    Image {
        id: bgImage
        anchors.fill: parent
        source: Qt.resolvedUrl(config.background || "background.jpg")
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
        smooth: true
    }

    // Left Half Subtle Vignette
    Rectangle {
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.right: rightPanel.left
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#b3020409" }
            GradientStop { position: 0.5; color: "#55050914" }
            GradientStop { position: 1.0; color: "#cc020409" }
        }
    }

    // Clock Timer
    Timer {
        id: clockTimer
        interval: 1000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: {
            var now = new Date()
            timeLabel.text = Qt.formatDateTime(now, config.timeFormat || "hh:mm:ss")
            dateLabel.text = Qt.formatDateTime(now, config.dateFormat || "dddd, d MMMM yyyy") + " // SYSTEM ONLINE"
        }
    }

    // ----------------------------------------------------
    // LEFT SIDE: CLOCK, DATE & 3D CEPHALON MATRIX
    // ----------------------------------------------------
    Item {
        id: leftPanel
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.right: rightPanel.left

        Column {
            anchors.centerIn: parent
            anchors.horizontalCenterOffset: -root.width * 0.05
            spacing: 12
            width: Math.min(parent.width - 60, 560)

            // Sci-Fi Header Tag
            Row {
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 10

                Text {
                    text: "⟨"
                    font.family: root.fontFam
                    font.bold: true
                    font.pixelSize: 18
                    color: root.colGold
                }

                Text {
                    text: config.headerText || "GARCHY OS // CEPHALON CORE"
                    font.family: root.fontFam
                    font.bold: true
                    font.pixelSize: 15
                    font.letterSpacing: 2
                    color: root.colAccent
                }

                Text {
                    text: "⟩"
                    font.family: root.fontFam
                    font.bold: true
                    font.pixelSize: 18
                    color: root.colGold
                }
            }

            // Big Crisp Clock
            Text {
                id: timeLabel
                anchors.horizontalCenter: parent.horizontalCenter
                font.family: root.fontFam
                font.bold: true
                font.pixelSize: 76
                font.letterSpacing: 2
                color: root.colText
                smooth: true
            }

            // Date & Status
            Text {
                id: dateLabel
                anchors.horizontalCenter: parent.horizontalCenter
                font.family: root.fontFam
                font.bold: true
                font.pixelSize: 14
                font.letterSpacing: 1
                color: root.colGold
                opacity: 0.95
            }

            // 3D Rotating Cephalon Canvas
            Canvas {
                id: cephalonCanvas
                width: 440
                height: 280
                anchors.horizontalCenter: parent.horizontalCenter

                property real rotX: 0.0
                property real rotY: 0.0
                property real rotZ: 0.0
                property real pulse: 0.0

                // 3D Octahedron Diamond Vertices
                readonly property var vertices: [
                    [0, -58, 0],   // Top Apex
                    [0, 58, 0],    // Bottom Apex
                    [52, 0, 0],    // Right
                    [-52, 0, 0],   // Left
                    [0, 0, 52],    // Front
                    [0, 0, -52]    // Back
                ]

                // Octahedron Edges
                readonly property var edges: [
                    [0, 2], [0, 3], [0, 4], [0, 5], // Top pyramid
                    [1, 2], [1, 3], [1, 4], [1, 5], // Bottom pyramid
                    [2, 4], [4, 3], [3, 5], [5, 2]  // Equator
                ]

                property var particles: []

                Component.onCompleted: {
                    var pts = []
                    for (var i = 0; i < 32; i++) {
                        var theta = Math.random() * Math.PI * 2
                        var phi = (Math.random() - 0.5) * Math.PI
                        var r = 70 + Math.random() * 26
                        pts.push({
                            x: r * Math.cos(phi) * Math.cos(theta),
                            y: r * Math.sin(phi),
                            z: r * Math.cos(phi) * Math.sin(theta),
                            size: 1.5 + Math.random() * 2.2,
                            speed: 0.4 + Math.random() * 0.8
                        })
                    }
                    particles = pts
                }

                function rotate3D(x, y, z, rx, ry, rz) {
                    var radX = rx * Math.PI / 180
                    var y1 = y * Math.cos(radX) - z * Math.sin(radX)
                    var z1 = y * Math.sin(radX) + z * Math.cos(radX)

                    var radY = ry * Math.PI / 180
                    var x2 = x * Math.cos(radY) + z1 * Math.sin(radY)
                    var z2 = -x * Math.sin(radY) + z1 * Math.cos(radY)

                    var radZ = rz * Math.PI / 180
                    var x3 = x2 * Math.cos(radZ) - y1 * Math.sin(radZ)
                    var y3 = x2 * Math.sin(radZ) + y1 * Math.cos(radZ)

                    return [x3, y3, z2]
                }

                onPaint: {
                    var ctx = getContext("2d")
                    ctx.clearRect(0, 0, width, height)

                    var cx = width / 2
                    var cy = height / 2
                    var fov = 220
                    var pulseScale = 1.0 + 0.05 * Math.sin(pulse)

                    // 1. Draw 3D Celestial Orbit Rings
                    for (var ringIdx = 0; ringIdx < 3; ringIdx++) {
                        var angleOffset = ringIdx * 60
                        var ringRadius = 82 * pulseScale
                        var ringPts = []
                        for (var deg = 0; deg <= 360; deg += 15) {
                            var rRad = deg * Math.PI / 180
                            var rx = ringRadius * Math.cos(rRad)
                            var ry = ringRadius * Math.sin(rRad)
                            var rz = 0
                            var rotP = rotate3D(rx, ry, rz, rotX + angleOffset, rotY + angleOffset, rotZ)
                            var scale = fov / (fov + rotP[2])
                            ringPts.push({ x: cx + rotP[0] * scale, y: cy + rotP[1] * scale, z: rotP[2] })
                        }
                        ctx.beginPath()
                        for (var k = 0; k < ringPts.length; k++) {
                            if (k === 0) ctx.moveTo(ringPts[k].x, ringPts[k].y)
                            else ctx.lineTo(ringPts[k].x, ringPts[k].y)
                        }
                        ctx.strokeStyle = (ringIdx === 1) ? "rgba(251, 191, 36, 0.45)" : "rgba(0, 240, 255, 0.4)"
                        ctx.lineWidth = 1.3
                        ctx.stroke()
                    }

                    // 2. Draw 3D Orbiting Data Motes
                    for (var p = 0; p < particles.length; p++) {
                        var part = particles[p]
                        var rotPart = rotate3D(part.x * pulseScale, part.y * pulseScale, part.z * pulseScale, rotX * part.speed, rotY * part.speed, rotZ)
                        var pScale = fov / (fov + rotPart[2])
                        var px = cx + rotPart[0] * pScale
                        var py = cy + rotPart[1] * pScale
                        var pAlpha = Math.max(0.12, (rotPart[2] + 90) / 180)

                        ctx.beginPath()
                        ctx.arc(px, py, part.size * pScale, 0, Math.PI * 2)
                        ctx.fillStyle = (p % 2 === 0) ? "rgba(0, 240, 255, " + pAlpha + ")" : "rgba(251, 191, 36, " + pAlpha + ")"
                        ctx.fill()
                    }

                    // 3. Project 3D Diamond Vertices
                    var projVerts = []
                    for (var v = 0; v < vertices.length; v++) {
                        var vert = vertices[v]
                        var rotV = rotate3D(vert[0] * pulseScale, vert[1] * pulseScale, vert[2] * pulseScale, rotX, rotY, rotZ)
                        var vScale = fov / (fov + rotV[2])
                        projVerts.push({
                            x: cx + rotV[0] * vScale,
                            y: cy + rotV[1] * vScale,
                            z: rotV[2]
                        })
                    }

                    // 4. Draw 3D Edges
                    for (var e = 0; e < edges.length; e++) {
                        var p1 = projVerts[edges[e][0]]
                        var p2 = projVerts[edges[e][1]]
                        var avgZ = (p1.z + p2.z) / 2
                        var edgeAlpha = Math.max(0.25, (avgZ + 70) / 140)

                        ctx.beginPath()
                        ctx.moveTo(p1.x, p1.y)
                        ctx.lineTo(p2.x, p2.y)
                        ctx.strokeStyle = (e < 8) ? "rgba(251, 191, 36, " + edgeAlpha + ")" : "rgba(0, 240, 255, " + edgeAlpha + ")"
                        ctx.lineWidth = (avgZ > 0) ? 2.2 : 1.3
                        ctx.stroke()
                    }

                    // 5. Draw Glowing Vertices
                    for (var vd = 0; vd < projVerts.length; vd++) {
                        var vp = projVerts[vd]
                        ctx.beginPath()
                        ctx.arc(vp.x, vp.y, (vd < 2 ? 4.0 : 3.0), 0, Math.PI * 2)
                        ctx.fillStyle = (vd < 2) ? "#fbbf24" : "#00f0ff"
                        ctx.fill()
                    }

                    // 6. Central Holographic Energy Core
                    var coreGlowRadius = (14 + 3 * Math.sin(pulse * 2)) * pulseScale
                    var grad = ctx.createRadialGradient(cx, cy, 2, cx, cy, coreGlowRadius)
                    grad.addColorStop(0.0, "rgba(255, 255, 255, 1.0)")
                    grad.addColorStop(0.3, "rgba(0, 240, 255, 0.85)")
                    grad.addColorStop(0.7, "rgba(251, 191, 36, 0.45)")
                    grad.addColorStop(1.0, "rgba(0, 240, 255, 0.0)")

                    ctx.beginPath()
                    ctx.arc(cx, cy, coreGlowRadius, 0, Math.PI * 2)
                    ctx.fillStyle = grad
                    ctx.fill()
                }

                Timer {
                    interval: 16
                    running: true
                    repeat: true
                    onTriggered: {
                        cephalonCanvas.rotX = (cephalonCanvas.rotX + 0.6) % 360
                        cephalonCanvas.rotY = (cephalonCanvas.rotY + 1.1) % 360
                        cephalonCanvas.rotZ = (cephalonCanvas.rotZ + 0.4) % 360
                        cephalonCanvas.pulse = (cephalonCanvas.pulse + 0.06) % (Math.PI * 2)
                        cephalonCanvas.requestPaint()
                    }
                }
            }

            // Bottom Left Telemetry
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "SYS_INTEGRITY: OPTIMAL // 144Hz DISPLAY MATRIX"
                font.family: root.fontFam
                font.bold: true
                font.pixelSize: 11
                font.letterSpacing: 1
                color: root.colSubtext
            }
        }
    }

    // ----------------------------------------------------
    // RIGHT SIDE: FROSTED GLASS LOGIN SIDEBAR
    // ----------------------------------------------------
    Item {
        id: rightPanel
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: Math.max(parent.width * 0.43, 490)
        clip: true

        // 1. Dark Glass Frost Overlay (Single background - zero duplicate image)
        Rectangle {
            anchors.fill: parent
            gradient: Gradient {
                GradientStop { position: 0.0; color: "#f5040711" }
                GradientStop { position: 0.5; color: "#eb080c18" }
                GradientStop { position: 1.0; color: "#f803050c" }
            }
        }

        // 3. Glowing Left Border Line
        Rectangle {
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            width: 2
            gradient: Gradient {
                GradientStop { position: 0.0; color: "#0000f0ff" }
                GradientStop { position: 0.2; color: "#8000f0ff" }
                GradientStop { position: 0.5; color: "#ccfbbf24" }
                GradientStop { position: 0.8; color: "#8000f0ff" }
                GradientStop { position: 1.0; color: "#0000f0ff" }
            }
        }

        // 4. Centered Right Login Form
        Rectangle {
            id: authCard
            width: Math.min(parent.width - 64, 400)
            height: 480
            anchors.centerIn: parent
            radius: 12
            color: "transparent"

            SequentialAnimation {
                id: shakeAnimation
                NumberAnimation { target: authCard; property: "anchors.horizontalCenterOffset"; from: 0; to: -16; duration: 40; easing.type: Easing.InOutQuad }
                NumberAnimation { target: authCard; property: "anchors.horizontalCenterOffset"; from: -16; to: 16; duration: 40; easing.type: Easing.InOutQuad }
                NumberAnimation { target: authCard; property: "anchors.horizontalCenterOffset"; from: 16; to: -10; duration: 35; easing.type: Easing.InOutQuad }
                NumberAnimation { target: authCard; property: "anchors.horizontalCenterOffset"; from: -10; to: 10; duration: 35; easing.type: Easing.InOutQuad }
                NumberAnimation { target: authCard; property: "anchors.horizontalCenterOffset"; from: 10; to: 0; duration: 30; easing.type: Easing.InOutQuad }
            }

            Column {
                anchors.centerIn: parent
                spacing: 20
                width: parent.width

                // User Profile Header
                Row {
                    anchors.horizontalCenter: parent.horizontalCenter
                    spacing: 14

                    Rectangle {
                        width: 56
                        height: 56
                        radius: 10
                        color: root.colInputBg
                        border.color: root.colGold
                        border.width: 1.5
                        anchors.verticalCenter: parent.verticalCenter

                        Text {
                            anchors.centerIn: parent
                            text: ""
                            font.family: root.fontFam
                            font.pixelSize: 26
                            color: root.colGold
                        }
                    }

                    Column {
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: 3

                        Text {
                            id: usernameText
                            text: (userModel && userModel.lastUser && userModel.lastUser !== "") ? "OPERATOR: " + userModel.lastUser.toUpperCase() : "OPERATOR: GALLO"
                            font.family: root.fontFam
                            font.bold: true
                            font.pixelSize: 16
                            font.letterSpacing: 1
                            color: root.colAccent
                        }

                        Text {
                            text: "[ SECURITY CLEARANCE: LEVEL 5 ]"
                            font.family: root.fontFam
                            font.bold: true
                            font.pixelSize: 10
                            font.letterSpacing: 1
                            color: root.colGold
                        }
                    }
                }

                // Password Input Field (Pill container)
                Rectangle {
                    id: inputPill
                    width: parent.width
                    height: 52
                    radius: 8
                    color: root.colInputBg
                    border.color: passwordInput.activeFocus ? root.colAccent : root.colGold
                    border.width: passwordInput.activeFocus ? 2 : 1.5

                    Behavior on border.color { ColorAnimation { duration: 150 } }

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 14
                        anchors.rightMargin: 8
                        spacing: 10

                        Text {
                            text: "󰌾"
                            font.family: root.fontFam
                            font.pixelSize: 16
                            color: passwordInput.activeFocus ? root.colAccent : root.colGold
                        }

                        TextField {
                            id: passwordInput
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            echoMode: root.showPassword ? TextInput.Normal : TextInput.Password
                            font.family: root.fontFam
                            font.pixelSize: 13
                            font.letterSpacing: 1
                            color: root.colText
                            focus: true
                            placeholderText: config.placeholderText || "[ ENTER ACCESS CIPHER ]"
                            placeholderTextColor: root.colSubtext
                            background: Rectangle { color: "transparent" }
                            verticalAlignment: TextInput.AlignVCenter
                            selectByMouse: true

                            onAccepted: root.startLogin()
                        }

                        // Reveal Eye
                        Rectangle {
                            width: 32
                            height: 32
                            radius: 6
                            color: eyeHover.containsMouse ? Qt.rgba(1, 1, 1, 0.15) : "transparent"

                            Text {
                                anchors.centerIn: parent
                                text: root.showPassword ? "󰈉" : "󰈈"
                                font.family: root.fontFam
                                font.pixelSize: 14
                                color: root.showPassword ? root.colAccent : root.colSubtext
                            }

                            MouseArea {
                                id: eyeHover
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: root.showPassword = !root.showPassword
                            }
                        }

                        // Submit Button
                        Rectangle {
                            id: submitBtn
                            width: 40
                            height: 40
                            radius: 6
                            color: submitHover.containsMouse ? root.colAccent : root.colGold

                            Behavior on color { ColorAnimation { duration: 120 } }

                            Text {
                                anchors.centerIn: parent
                                text: "󰅂"
                                font.family: root.fontFam
                                font.bold: true
                                font.pixelSize: 18
                                color: "#050914"
                            }

                            MouseArea {
                                id: submitHover
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: root.startLogin()
                            }
                        }
                    }
                }

                // Caps Lock Warning
                Text {
                    visible: (keyboard && keyboard.capsLock)
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: "⚠️ CIPHER WARNING: CAPS LOCK ACTIVE"
                    font.family: root.fontFam
                    font.bold: true
                    font.pixelSize: 11
                    color: root.colGold
                }

                // Status & Feedback Label
                Text {
                    id: feedbackLabel
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: root.statusText !== "" ? root.statusText : (config.sentinelStatus || "CEPHALON SECURITY MATRIX: ACTIVE [100%]")
                    font.family: root.fontFam
                    font.bold: true
                    font.pixelSize: 11
                    color: root.statusText !== "" ? root.statusColor : root.colSubtext
                    elide: Text.ElideRight
                }

                // Divider Line
                Rectangle {
                    width: parent.width
                    height: 1
                    color: Qt.rgba(0.22, 0.74, 0.97, 0.25)
                }

                // Session & Keyboard Controls Row
                RowLayout {
                    width: parent.width
                    spacing: 12

                    // Desktop Session Selector
                    ComboBox {
                        id: sessionSelector
                        Layout.fillWidth: true
                        Layout.preferredHeight: 38
                        model: sessionModel
                        textRole: "name"
                        currentIndex: (sessionModel && sessionModel.lastIndex >= 0) ? sessionModel.lastIndex : 0
                        font.family: root.fontFam
                        font.pixelSize: 11

                        background: Rectangle {
                            radius: 6
                            color: sessionSelector.hovered ? Qt.rgba(0, 240/255, 1, 0.2) : Qt.rgba(1, 1, 1, 0.06)
                            border.color: root.colAccent
                            border.width: 1
                        }

                        contentItem: Row {
                            spacing: 8
                            leftPadding: 10
                            rightPadding: 10
                            anchors.verticalCenter: parent.verticalCenter

                            Text {
                                text: "󰍹"
                                font.family: root.fontFam
                                font.pixelSize: 13
                                color: root.colAccent
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            Text {
                                text: "[ " + sessionSelector.displayText.toUpperCase() + " ]"
                                font.family: root.fontFam
                                font.bold: true
                                font.pixelSize: 11
                                color: root.colText
                                anchors.verticalCenter: parent.verticalCenter
                                elide: Text.ElideRight
                                width: 140
                            }
                        }

                        popup: Popup {
                            y: -implicitHeight - 6
                            width: sessionSelector.width
                            implicitHeight: Math.min(contentItem.implicitHeight + 16, 200)
                            padding: 6

                            background: Rectangle {
                                color: "#f2050914"
                                radius: 8
                                border.color: root.colGold
                                border.width: 1.5
                            }

                            contentItem: ListView {
                                clip: true
                                implicitHeight: contentHeight
                                model: sessionSelector.popup.visible ? sessionSelector.delegateModel : null
                                currentIndex: sessionSelector.highlightedIndex
                                ScrollIndicator.vertical: ScrollIndicator { }
                            }
                        }

                        delegate: ItemDelegate {
                            width: sessionSelector.width - 12
                            height: 34
                            highlighted: sessionSelector.highlightedIndex === index

                            background: Rectangle {
                                radius: 4
                                color: highlighted ? Qt.rgba(0, 240/255, 1, 0.25) : "transparent"
                            }

                            contentItem: Text {
                                text: model.name.toUpperCase()
                                font.family: root.fontFam
                                font.bold: true
                                font.pixelSize: 11
                                color: root.colText
                                verticalAlignment: Text.AlignVCenter
                                leftPadding: 8
                            }
                        }
                    }

                    // Keyboard Layout Button
                    Rectangle {
                        id: keyboardPill
                        Layout.preferredWidth: 80
                        Layout.preferredHeight: 38
                        radius: 6
                        color: keyboardHover.containsMouse ? Qt.rgba(0, 240/255, 1, 0.2) : Qt.rgba(1, 1, 1, 0.06)
                        border.color: root.colAccent
                        border.width: 1

                        Row {
                            anchors.centerIn: parent
                            spacing: 5

                            Text {
                                text: "🌐"
                                font.pixelSize: 12
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            Text {
                                text: (keyboard && keyboard.layouts && keyboard.layouts.length > 0 && keyboard.layouts[keyboard.currentLayout]) ? (keyboard.layouts[keyboard.currentLayout].shortName || keyboard.layouts[keyboard.currentLayout]).toUpperCase() : "EN"
                                font.family: root.fontFam
                                font.bold: true
                                font.pixelSize: 11
                                color: root.colGold
                                anchors.verticalCenter: parent.verticalCenter
                            }
                        }

                        MouseArea {
                            id: keyboardHover
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                if (keyboard && keyboard.layouts && keyboard.layouts.length > 1) {
                                    keyboard.currentLayout = (keyboard.currentLayout + 1) % keyboard.layouts.length
                                }
                            }
                        }
                    }
                }

                // Power Controls Matrix
                Row {
                    anchors.horizontalCenter: parent.horizontalCenter
                    spacing: 16

                    // Sleep / Suspend
                    Rectangle {
                        width: 40
                        height: 40
                        radius: 6
                        color: suspHover.containsMouse ? Qt.rgba(0, 240/255, 1, 0.3) : Qt.rgba(1, 1, 1, 0.06)
                        border.color: root.colAccent
                        border.width: 1

                        Text {
                            anchors.centerIn: parent
                            text: "⏾"
                            font.pixelSize: 15
                            color: root.colAccent
                        }

                        MouseArea {
                            id: suspHover
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: sddm.suspend()
                        }
                    }

                    // Reboot Matrix
                    Rectangle {
                        width: 40
                        height: 40
                        radius: 6
                        color: rebHover.containsMouse ? Qt.rgba(251/255, 191/255, 36/255, 0.3) : Qt.rgba(1, 1, 1, 0.06)
                        border.color: root.colGold
                        border.width: 1

                        Text {
                            anchors.centerIn: parent
                            text: "🗘"
                            font.pixelSize: 15
                            color: root.colGold
                        }

                        MouseArea {
                            id: rebHover
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: sddm.reboot()
                        }
                    }

                    // Power Off / Sever Session
                    Rectangle {
                        width: 40
                        height: 40
                        radius: 6
                        color: offHover.containsMouse ? Qt.rgba(244/255, 63/255, 94/255, 0.35) : Qt.rgba(1, 1, 1, 0.06)
                        border.color: root.colError
                        border.width: 1

                        Text {
                            anchors.centerIn: parent
                            text: "⏻"
                            font.pixelSize: 15
                            color: root.colError
                        }

                        MouseArea {
                            id: offHover
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: sddm.powerOff()
                        }
                    }
                }
            }
        }
    }

    // Login Function
    function startLogin() {
        if (root.isAuthenticating) return
        var rawUser = (userModel && userModel.lastUser && userModel.lastUser !== "") ? userModel.lastUser : "gallo"
        var password = passwordInput.text
        if (password.length === 0) {
            root.statusColor = root.colError
            root.statusText = "[ CIPHER REJECTED // PASSCODE REQUIRED ]"
            shakeAnimation.restart()
            return
        }
        root.isAuthenticating = true
        root.statusColor = root.colAccent
        root.statusText = "[ AUTHENTICATING CIPHER... ]"
        sddm.login(rawUser, password, sessionSelector.currentIndex)
    }

    Component.onCompleted: {
        passwordInput.forceActiveFocus()
    }
}
