import Quickshell
import Quickshell.Wayland
import Quickshell.Io
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

PanelWindow {
    id: root

    // Target Right Screen (DP-1)
    screen: {
        for (var i = 0; i < Quickshell.screens.length; i++) {
            if (Quickshell.screens[i].name === "DP-1") {
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
    WlrLayershell.layer: WlrLayer.Bottom
    exclusionMode: "Ignore"

    // State Variables
    property string songTitle: "No Media Playing"
    property string songArtist: "Play music in Brave / Spotify / MPV"
    property string playStatus: "Paused"
    property string artUrl: ""

    // 40 Spectrum Bars & Peak Hold Physics
    property var spectrumData: []
    property var peakData: []

    // ========================================================
    // DYNAMIC GLOBAL THEME SYNCHRONIZATION
    // ========================================================
    property color themeBg: "#131622CC"
    property color themeBgAlt: "#1A1D2E"
    property color themeBorder: "#24283B"
    property color themeAccent: "#7AA2F7"
    property color themeAccentAlt: "#BB9AF7"
    property color themeFg: "#C0CAF5"
    property int themeRadius: 0

    property int currentThemeIndex: 3
    property int currentStyleIndex: 0

    // Watch global theme changes from theme-switcher.sh
    FileView {
        path: "/home/gallo/.config/quickshell/desktop-hub/active_theme.json"
        watchChanges: true
        onFileChanged: {
            try {
                var content = text();
                var parsed = JSON.parse(content);
                if (parsed.themeIndex !== undefined) {
                    root.currentThemeIndex = parsed.themeIndex;
                }
                if (parsed.bg) root.themeBg = parsed.bg;
                if (parsed.bgAlt) root.themeBgAlt = parsed.bgAlt;
                if (parsed.border) root.themeBorder = parsed.border;
                if (parsed.accent) root.themeAccent = parsed.accent;
                if (parsed.accentAlt) root.themeAccentAlt = parsed.accentAlt;
                if (parsed.fg) root.themeFg = parsed.fg;
                if (parsed.radius !== undefined) root.themeRadius = parsed.radius;
            } catch(e) {
                console.log("Error updating active theme:", e);
            }
        }
    }

    property var themeNames: [
        "1. Rainbow Chroma",
        "2. Cyberpunk 2077",
        "3. Synthwave Outrun",
        "4. Tokyo Night",
        "5. Nord Arctic",
        "6. Catppuccin Mocha",
        "7. Dracula Vampire",
        "8. Matrix Rain",
        "9. Volcanic Lava",
        "10. Deep Ocean",
        "11. Sakura Blossom",
        "12. Golden Sunset",
        "13. Toxic Acid",
        "14. Blood Moon",
        "15. Emerald Forest",
        "16. Electric Violet",
        "17. Autumn Amber",
        "18. Vaporwave Dream",
        "19. Monochrome Glass",
        "20. Hyperpop Neon"
    ]

    property var styleNames: [
        "Classic EQ",
        "Center Mirror",
        "Digital Blocks",
        "Pulse Pins"
    ]

    property var themePalettes: [
        ["#FF3B30", "#FF9500", "#FFCC00", "#34C759", "#00F5D4", "#0A84FF", "#5E5CE6", "#BF5AF2", "#FF2A6D"],
        ["#FFE600", "#FF0055", "#00F0FF", "#7000FF", "#FFE600", "#FF0055", "#00F0FF"],
        ["#FF2A85", "#FF7700", "#9A00FF", "#05D9E8", "#FF2A85", "#9A00FF"],
        ["#7AA2F7", "#7DCFFF", "#BB9AF7", "#9D7CD8", "#F7768E", "#7AA2F7"],
        ["#5E81AC", "#81A1C1", "#88C0D0", "#8FBCBB", "#A3BE8C", "#EBCB8B"],
        ["#CBA6F7", "#F38BA8", "#FAB387", "#A6E3A1", "#94E2D5", "#89B4FA"],
        ["#BD93F9", "#FF79C6", "#8BE9FD", "#50FA7B", "#F1FA8C", "#FF5555"],
        ["#003B00", "#008F11", "#00FF66", "#33FF33", "#00CC44", "#00FF66"],
        ["#7F0000", "#D00000", "#DC2F02", "#E85D04", "#F48C06", "#FFBA08"],
        ["#03045E", "#023E8A", "#0077B6", "#0096C7", "#00B4D8", "#48CAE4", "#90E0EF"],
        ["#590D22", "#800F2F", "#A4133C", "#C9184A", "#FF4D6D", "#FF758F", "#FFB3C1"],
        ["#480CA8", "#7209B7", "#B5179E", "#F72585", "#FF7900", "#FFB703", "#FFD000"],
        ["#1B5E20", "#388E3C", "#76FF03", "#CCFF00", "#00E676", "#1DE9B6"],
        ["#370617", "#6A040F", "#9D0208", "#D00000", "#DC2F02", "#E85D04"],
        ["#1B4332", "#2D6A4F", "#40916C", "#52B788", "#74C69D", "#95D5B2", "#D8F3DC"],
        ["#240046", "#3C096C", "#5A189A", "#7B2CBF", "#9D4EDD", "#C77DFF", "#E0AAFF"],
        ["#6F1D1B", "#99582A", "#BB9457", "#D4A373", "#E6CCB2", "#FFE6A7"],
        ["#FF99C8", "#FCF6BD", "#D0F4DE", "#A9DEF9", "#E4C1F9", "#FF99C8"],
        ["#475569", "#64748B", "#94A3B8", "#CBD5E1", "#E2E8F0", "#FFFFFF"],
        ["#FF007F", "#39FF14", "#00E5FF", "#FFDF00", "#FF007F", "#7928CA"]
    ]

    function getBarColor(index) {
        var pal = root.themePalettes[root.currentThemeIndex] || root.themePalettes[0];
        var pos = (index / 39) * (pal.length - 1);
        var baseIdx = Math.floor(pos);
        return pal[Math.min(pal.length - 1, baseIdx)];
    }

    function nextTheme() {
        root.currentThemeIndex = (root.currentThemeIndex + 1) % root.themeNames.length;
    }

    function prevTheme() {
        root.currentThemeIndex = (root.currentThemeIndex - 1 + root.themeNames.length) % root.themeNames.length;
    }

    function nextStyle() {
        root.currentStyleIndex = (root.currentStyleIndex + 1) % root.styleNames.length;
    }

    function prevStyle() {
        root.currentStyleIndex = (root.currentStyleIndex - 1 + root.styleNames.length) % root.styleNames.length;
    }

    property bool drawerOpen: false

    // System Time
    property string timeStr: ""
    property string dateStr: ""

    // Initialize 40 bars on startup
    Component.onCompleted: {
        var initial = [];
        var initialPeaks = [];
        for (var i = 0; i < 40; i++) {
            initial.push(6);
            initialPeaks.push(8);
        }
        root.spectrumData = initial;
        root.peakData = initialPeaks;
        loadFavorites();
    }

    Timer {
        interval: 1000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: {
            var now = new Date();
            root.timeStr = Qt.formatTime(now, "hh:mm:ss");
            root.dateStr = Qt.formatDate(now, "dddd, MMMM d, yyyy");
        }
    }

    property bool hasMpvInfo: false

    FileView {
        path: "/tmp/mpv_media_info.json"
        watchChanges: true
        onFileChanged: {
            try {
                var content = text();
                if (content && content.length > 5) {
                    var parsed = JSON.parse(content);
                    if (parsed.title) {
                        root.songTitle = parsed.title;
                        root.songArtist = parsed.artist || "MPV Video Player";
                        root.playStatus = parsed.status || "Playing";
                        root.artUrl = parsed.artUrl || "";
                        root.hasMpvInfo = true;
                        return;
                    }
                }
            } catch(e) {}
            root.hasMpvInfo = false;
        }
    }

    // Polling playerctl for music status & artUrl
    Process {
        id: playerProc
        command: ["playerctl", "metadata", "--format", "{{status}}:::{{title}}:::{{artist}}:::{{mpris:artUrl}}"]
        running: false
        stdout: SplitParser {
            onRead: data => {
                if (root.hasMpvInfo) return;
                var parts = data.trim().split(":::");
                if (parts.length >= 3) {
                    root.playStatus = parts[0] || "Paused";
                    root.songTitle = parts[1] || "No Media Playing";
                    root.songArtist = parts[2] || "Unknown Artist";
                    root.artUrl = parts[3] || "";
                }
            }
        }
    }

    Timer {
        interval: 1200
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: {
            if (!playerProc.running) {
                playerProc.running = true;
            }
        }
    }

    // High-Density 40-Bar Frequency Acoustic Simulation
    Timer {
        interval: 45
        running: root.playStatus === "Playing"
        repeat: true
        onTriggered: {
            var updated = [];
            var updatedPeaks = [];
            var time = Date.now() / 140;

            for (var i = 0; i < 40; i++) {
                var val = 6;
                if (i < 8) {
                    var bassWave = Math.sin(time * 0.9 + i * 0.3) * 42 + 48;
                    var bassThump = (Math.sin(time * 1.8) > 0.4 ? 25 : 0);
                    val = Math.min(100, Math.max(6, Math.floor(bassWave + bassThump + Math.random() * 12)));
                } else if (i < 22) {
                    var midWave1 = Math.sin(time * 2.2 + i * 0.45) * 32;
                    var midWave2 = Math.cos(time * 1.5 - i * 0.25) * 20;
                    val = Math.min(100, Math.max(6, Math.floor(40 + midWave1 + midWave2 + Math.random() * 18)));
                } else if (i < 34) {
                    var highWave = Math.sin(time * 3.1 - i * 0.5) * 26 + 32;
                    val = Math.min(100, Math.max(6, Math.floor(highWave + Math.random() * 15)));
                } else {
                    var trebleWave = Math.sin(time * 4.2 + i * 0.8) * 20 + 24;
                    val = Math.min(100, Math.max(6, Math.floor(trebleWave + Math.random() * 14)));
                }

                updated.push(val);

                var prevPeak = root.peakData[i] || 0;
                if (val >= prevPeak) {
                    updatedPeaks.push(val);
                } else {
                    updatedPeaks.push(Math.max(6, prevPeak - 3));
                }
            }

            root.spectrumData = updated;
            root.peakData = updatedPeaks;
        }
    }

    // ==========================================
    // FAVORITES MODEL & PERSISTENCE
    // ==========================================
    ListModel {
        id: favModel
    }

    property var defaultFavs: [
        { "name": "Home", "icon": "󰋜", "command": "thunar /home/gallo", "description": "File Manager" },
        { "name": "Terminal", "icon": "", "command": "kitty", "description": "Kitty Terminal" },
        { "name": "Brave", "icon": "󰖟", "command": "brave", "description": "Web Browser" },
        { "name": "Firefox", "icon": "󰈹", "command": "firefox", "description": "Mozilla Firefox" },
        { "name": "Steam", "icon": "󰓓", "command": "steam", "description": "Gaming Platform" },
        { "name": "Heroic", "icon": "󰊴", "command": "heroic", "description": "Heroic Games Launcher" },
        { "name": "Kdenlive", "icon": "󰕼", "command": "kdenlive", "description": "Video Editor" },
        { "name": "CODE", "icon": "󰨞", "command": "code", "description": "VS Code Editor" },
        { "name": "EasyEffects", "icon": "󰓃", "command": "easyeffects", "description": "Audio Equalizer" }
    ]

    FileView {
        id: favFileView
        path: "/home/gallo/.config/quickshell/desktop-hub/favorites.json"
        watchChanges: true
        onFileChanged: {
            loadFavoritesFromFile();
        }
    }

    function loadFavoritesFromFile() {
        try {
            var content = favFileView.text();
            if (content && content.length > 2) {
                var parsed = JSON.parse(content);
                if (parsed && Array.isArray(parsed) && parsed.length > 0) {
                    favModel.clear();
                    for (var i = 0; i < parsed.length; i++) {
                        favModel.append({
                            name: parsed[i].name || "App",
                            icon: parsed[i].icon || "󰀻",
                            command: parsed[i].command || "",
                            description: parsed[i].description || ""
                        });
                    }
                    return true;
                }
            }
        } catch(e) {
            console.log("Error loading favorites from FileView:", e);
        }
        return false;
    }

    function loadDefaults() {
        favModel.clear();
        for (var i = 0; i < root.defaultFavs.length; i++) {
            favModel.append(root.defaultFavs[i]);
        }
        saveFavorites();
    }

    function loadFavorites() {
        if (!loadFavoritesFromFile()) {
            loadDefaults();
        }
    }

    function saveFavorites() {
        if (favModel.count === 0) return;
        var arr = [];
        for (var i = 0; i < favModel.count; i++) {
            var item = favModel.get(i);
            arr.push({
                name: item.name,
                icon: item.icon,
                command: item.command,
                description: item.description
            });
        }
        var jsonStr = JSON.stringify(arr, null, 4);
        Quickshell.execDetached(["/home/gallo/.config/quickshell/desktop-hub/manage_favs.sh", "save", jsonStr]);
    }

    function moveItem(fromIndex, toIndex) {
        if (toIndex >= 0 && toIndex < favModel.count && fromIndex !== toIndex) {
            favModel.move(fromIndex, toIndex, 1);
            saveFavorites();
        }
    }

    function removeItem(index) {
        if (index >= 0 && index < favModel.count) {
            favModel.remove(index);
            saveFavorites();
        }
    }

    // ==========================================
    // 1. CLOCK WIDGET (Top Center of Right Screen)
    // ==========================================
    Rectangle {
        id: clockCard
        anchors {
            top: parent.top
            topMargin: 48
            horizontalCenter: parent.horizontalCenter
        }
        width: 380
        height: 95
        radius: root.themeRadius
        color: root.themeBg
        border.color: root.themeBorder
        border.width: 1

        ColumnLayout {
            anchors.centerIn: parent
            spacing: 2

            Text {
                text: root.timeStr
                font.family: "JetBrainsMono Nerd Font"
                font.pixelSize: 40
                font.bold: true
                color: root.themeAccent
                Layout.alignment: Qt.AlignHCenter
            }

            Text {
                text: root.dateStr
                font.family: "JetBrainsMono Nerd Font"
                font.pixelSize: 13
                color: root.themeFg
                Layout.alignment: Qt.AlignHCenter
            }
        }
    }


    // ==========================================
    // 2. SSH WIDGET (Left Center Vertical Column)
    // ==========================================
    Rectangle {
        id: sshCard
        anchors {
            left: parent.left
            leftMargin: 36
            verticalCenter: parent.verticalCenter
        }
        width: 210
        height: 290
        radius: root.themeRadius
        color: root.themeBg
        border.color: root.themeBorder
        border.width: 1

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 14
            spacing: 10

            RowLayout {
                spacing: 8
                Text {
                    text: "󰒋"
                    font.family: "JetBrainsMono Nerd Font"
                    font.pixelSize: 16
                    color: root.themeAccent
                }
                Text {
                    text: "SSH SERVERS"
                    font.family: "JetBrainsMono Nerd Font"
                    font.pixelSize: 12
                    font.bold: true
                    color: "#787C99"
                    font.letterSpacing: 1
                }
            }

            // Server 1: itsusi (gallo@192.168.1.100)
            Rectangle {
                Layout.fillWidth: true
                height: 64
                radius: Math.max(0, root.themeRadius - 2)
                color: itsusiBtn.containsMouse ? root.themeBorder : root.themeBgAlt
                border.color: itsusiBtn.containsMouse ? root.themeAccent : root.themeBorder
                border.width: 1

                ColumnLayout {
                    anchors.centerIn: parent
                    spacing: 2

                    Text {
                        text: "󰒋 itsusi"
                        font.family: "JetBrainsMono Nerd Font"
                        font.pixelSize: 13
                        font.bold: true
                        color: "#FFFFFF"
                        Layout.alignment: Qt.AlignHCenter
                    }
                    Text {
                        text: "gallo@192.168.1.100"
                        font.family: "JetBrainsMono Nerd Font"
                        font.pixelSize: 10
                        color: root.themeAccent
                        Layout.alignment: Qt.AlignHCenter
                    }
                }

                MouseArea {
                    id: itsusiBtn
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: Quickshell.execDetached(["/home/gallo/.config/hypr/scripts/quick-ssh.sh", "itsusi"])
                }
            }

            // Server 2: prox (root@192.168.1.106)
            Rectangle {
                Layout.fillWidth: true
                height: 64
                radius: Math.max(0, root.themeRadius - 2)
                color: proxBtn.containsMouse ? root.themeBorder : root.themeBgAlt
                border.color: proxBtn.containsMouse ? root.themeAccent : root.themeBorder
                border.width: 1

                ColumnLayout {
                    anchors.centerIn: parent
                    spacing: 2

                    Text {
                        text: "󰒋 prox"
                        font.family: "JetBrainsMono Nerd Font"
                        font.pixelSize: 13
                        font.bold: true
                        color: "#FFFFFF"
                        Layout.alignment: Qt.AlignHCenter
                    }
                    Text {
                        text: "root@192.168.1.106"
                        font.family: "JetBrainsMono Nerd Font"
                        font.pixelSize: 10
                        color: root.themeAccent
                        Layout.alignment: Qt.AlignHCenter
                    }
                }

                MouseArea {
                    id: proxBtn
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: Quickshell.execDetached(["/home/gallo/.config/hypr/scripts/quick-ssh.sh", "prox"])
                }
            }

            // Server 3: flix (tv@192.168.1.105)
            Rectangle {
                Layout.fillWidth: true
                height: 64
                radius: Math.max(0, root.themeRadius - 2)
                color: flixBtn.containsMouse ? root.themeBorder : root.themeBgAlt
                border.color: flixBtn.containsMouse ? root.themeAccent : root.themeBorder
                border.width: 1

                ColumnLayout {
                    anchors.centerIn: parent
                    spacing: 2

                    Text {
                        text: "󰒋 flix"
                        font.family: "JetBrainsMono Nerd Font"
                        font.pixelSize: 13
                        font.bold: true
                        color: "#FFFFFF"
                        Layout.alignment: Qt.AlignHCenter
                    }
                    Text {
                        text: "tv@192.168.1.105"
                        font.family: "JetBrainsMono Nerd Font"
                        font.pixelSize: 10
                        color: root.themeAccent
                        Layout.alignment: Qt.AlignHCenter
                    }
                }

                MouseArea {
                    id: flixBtn
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: Quickshell.execDetached(["/home/gallo/.config/hypr/scripts/quick-ssh.sh", "flix"])
                }
            }
        }
    }

    // ========================================================
    // 3. MUSIC & 20-THEME VISUALIZER (Bottom Center Expanded)
    // ========================================================
    Rectangle {
        id: musicCard
        anchors {
            bottom: parent.bottom
            bottomMargin: 32
            horizontalCenter: parent.horizontalCenter
        }
        width: 980
        height: 160
        radius: root.themeRadius
        color: root.themeBg
        border.color: root.themeBorder
        border.width: 1

        RowLayout {
            anchors.fill: parent
            anchors.margins: 12
            spacing: 16

            // A. HIGH-RES ALBUM ART / TRACK COVER WITH PiP LAUNCHER
            Rectangle {
                id: videoScreenContainer
                width: 136
                height: 136
                radius: Math.max(0, root.themeRadius - 2)
                color: root.themeBgAlt
                border.color: pipBtnArea.containsMouse ? root.themeAccent : root.themeBorder
                border.width: 1
                clip: true

                // Album Artwork Image
                Image {
                    id: albumCover
                    anchors.fill: parent
                    source: root.artUrl
                    fillMode: Image.PreserveAspectCrop
                    asynchronous: true
                    visible: status === Image.Ready && root.artUrl !== ""
                }

                // Fallback Music Icon if no artwork
                Text {
                    anchors.centerIn: parent
                    text: ""
                    font.family: "JetBrainsMono Nerd Font"
                    font.pixelSize: 48
                    color: root.getBarColor(0)
                    visible: !albumCover.visible
                }

                // Floating PiP Popout Button (Corner Badge)
                Rectangle {
                    anchors {
                        top: parent.top
                        right: parent.right
                        margins: 4
                    }
                    width: 52
                    height: 20
                    radius: Math.max(0, root.themeRadius - 4)
                    color: pipBtnArea.containsMouse ? root.themeAccent : root.themeBg
                    border.color: root.themeAccent
                    border.width: 1

                    RowLayout {
                        anchors.centerIn: parent
                        spacing: 2
                        Text {
                            text: "󰕼"
                            font.family: "JetBrainsMono Nerd Font"
                            font.pixelSize: 11
                            color: pipBtnArea.containsMouse ? "#131622" : root.themeAccent
                        }
                        Text {
                            text: "PiP"
                            font.family: "JetBrainsMono Nerd Font"
                            font.pixelSize: 9
                            font.bold: true
                            color: pipBtnArea.containsMouse ? "#131622" : "#FFFFFF"
                        }
                    }

                    MouseArea {
                        id: pipBtnArea
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: Quickshell.execDetached(["/home/gallo/.config/hypr/scripts/youtube-pip.sh"])
                    }
                }
            }

            // B. TRACK INFO, THEME PICKERS & FULLY TRANSPARENT VISUALIZER
            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 6

                // Top Header Row (Status + Track title + Theme & Style Selectors)
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    Rectangle {
                        width: 72
                        height: 20
                        radius: Math.max(0, root.themeRadius - 4)
                        color: root.playStatus === "Playing" ? "#73DACA20" : "#565F8920"
                        border.color: root.playStatus === "Playing" ? "#73DACA" : "#565F89"
                        border.width: 1

                        Text {
                            anchors.centerIn: parent
                            text: root.playStatus.toUpperCase()
                            font.family: "JetBrainsMono Nerd Font"
                            font.pixelSize: 10
                            font.bold: true
                            color: root.playStatus === "Playing" ? "#73DACA" : "#565F89"
                        }
                    }

                    Text {
                        text: root.songTitle
                        font.family: "JetBrainsMono Nerd Font"
                        font.pixelSize: 14
                        font.bold: true
                        color: "#FFFFFF"
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                    }

                    // Theme Cycler Pill
                    Rectangle {
                        width: 170
                        height: 22
                        radius: Math.max(0, root.themeRadius - 4)
                        color: root.themeBgAlt
                        border.color: root.themeBorder
                        border.width: 1

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 2
                            spacing: 2

                            Text {
                                text: "◀"
                                font.pixelSize: 10
                                color: prevThmArea.containsMouse ? root.themeAccent : "#565F89"
                                MouseArea {
                                    id: prevThmArea
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: root.prevTheme()
                                }
                            }

                            Text {
                                text: root.themeNames[root.currentThemeIndex]
                                font.family: "JetBrainsMono Nerd Font"
                                font.pixelSize: 10
                                font.bold: true
                                color: root.getBarColor(15)
                                Layout.fillWidth: true
                                horizontalAlignment: Text.AlignHCenter
                                elide: Text.ElideRight
                            }

                            Text {
                                text: "▶"
                                font.pixelSize: 10
                                color: nextThmArea.containsMouse ? root.themeAccent : "#565F89"
                                MouseArea {
                                    id: nextThmArea
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: root.nextTheme()
                                }
                            }
                        }
                    }

                    // Style Cycler Pill
                    Rectangle {
                        width: 120
                        height: 22
                        radius: Math.max(0, root.themeRadius - 4)
                        color: root.themeBgAlt
                        border.color: root.themeBorder
                        border.width: 1

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 2
                            spacing: 2

                            Text {
                                text: "◀"
                                font.pixelSize: 10
                                color: prevStyArea.containsMouse ? root.themeAccent : "#565F89"
                                MouseArea {
                                    id: prevStyArea
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: root.prevStyle()
                                }
                            }

                            Text {
                                text: root.styleNames[root.currentStyleIndex]
                                font.family: "JetBrainsMono Nerd Font"
                                font.pixelSize: 10
                                font.bold: true
                                color: root.themeFg
                                Layout.fillWidth: true
                                horizontalAlignment: Text.AlignHCenter
                                elide: Text.ElideRight
                            }

                            Text {
                                text: "▶"
                                font.pixelSize: 10
                                color: nextStyArea.containsMouse ? root.themeAccent : "#565F89"
                                MouseArea {
                                    id: nextStyArea
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: root.nextStyle()
                                }
                            }
                        }
                    }
                }

                // Subtitle Row
                RowLayout {
                    Layout.fillWidth: true
                    Text {
                        text: root.songArtist
                        font.family: "JetBrainsMono Nerd Font"
                        font.pixelSize: 12
                        color: root.themeAccent
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                    }
                }

                // 40 Spectrum Frequency Bars (Fully Transparent Glassy Container)
                Item {
                    Layout.fillWidth: true
                    height: 72

                    // Center baseline for mirror mode only
                    Rectangle {
                        visible: root.currentStyleIndex === 1
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.left: parent.left
                        anchors.right: parent.right
                        height: 1
                        color: root.themeBorder
                    }

                    Row {
                        anchors {
                            bottom: root.currentStyleIndex === 1 ? undefined : parent.bottom
                            verticalCenter: root.currentStyleIndex === 1 ? parent.verticalCenter : undefined
                            horizontalCenter: parent.horizontalCenter
                        }
                        height: 70
                        spacing: 4

                        Repeater {
                            model: 40
                            Item {
                                width: root.currentStyleIndex === 3 ? 4 : 11
                                height: 70

                                // Spectrum Bar (Glassy & Opaque)
                                Rectangle {
                                    id: barRect
                                    width: parent.width
                                    height: root.playStatus === "Playing" ? Math.floor(Math.max(4, (root.spectrumData[index] || 6) * 0.68)) : 4
                                    anchors.bottom: root.currentStyleIndex === 1 ? undefined : parent.bottom
                                    anchors.verticalCenter: root.currentStyleIndex === 1 ? parent.verticalCenter : undefined
                                    color: root.getBarColor(index)
                                    opacity: root.currentStyleIndex === 2 ? 0.95 : 0.90
                                    radius: root.themeRadius > 0 ? 2 : 0
                                    border.color: "#FFFFFF40"
                                    border.width: root.currentStyleIndex === 3 ? 0 : 1

                                    Behavior on height {
                                        NumberAnimation { duration: 50; easing.type: Easing.OutQuad }
                                    }
                                }

                                // Floating Peak Dot
                                Rectangle {
                                    width: parent.width
                                    height: 2
                                    anchors.bottom: parent.bottom
                                    anchors.bottomMargin: root.playStatus === "Playing" ? Math.floor(Math.max(6, (root.peakData[index] || 8) * 0.68 + 2)) : 6
                                    color: "#FFFFFF"
                                    radius: root.themeRadius > 0 ? 1 : 0
                                    opacity: root.playStatus === "Playing" && (root.currentStyleIndex === 0 || root.currentStyleIndex === 2) ? 0.95 : 0.0

                                    Behavior on anchors.bottomMargin {
                                        NumberAnimation { duration: 45 }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // C. PLAYBACK CONTROLS (Play/Pause, Stop/Close, Prev, Next)
            ColumnLayout {
                spacing: 8
                Layout.alignment: Qt.AlignVCenter

                RowLayout {
                    spacing: 6

                    // Play / Pause Button
                    Rectangle {
                        width: 76
                        height: 38
                        radius: Math.max(0, root.themeRadius - 4)
                        color: playBtn.containsMouse ? root.themeAccent : root.themeBgAlt
                        border.color: root.themeAccent
                        border.width: 1

                        RowLayout {
                            anchors.centerIn: parent
                            spacing: 4

                            Text {
                                text: root.playStatus === "Playing" ? "󰏤" : "󰐊"
                                font.family: "JetBrainsMono Nerd Font"
                                font.pixelSize: 15
                                color: playBtn.containsMouse ? "#131622" : root.themeAccent
                            }
                            Text {
                                text: root.playStatus === "Playing" ? "Pause" : "Play"
                                font.family: "JetBrainsMono Nerd Font"
                                font.pixelSize: 11
                                font.bold: true
                                color: playBtn.containsMouse ? "#131622" : "#FFFFFF"
                            }
                        }

                        MouseArea {
                            id: playBtn
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: Quickshell.execDetached(["/home/gallo/.config/hypr/scripts/media-control.sh", "play-pause"])
                        }
                    }

                    // Stop / Close Button
                    Rectangle {
                        width: 38
                        height: 38
                        radius: Math.max(0, root.themeRadius - 4)
                        color: stopBtn.containsMouse ? "#F7768E" : root.themeBgAlt
                        border.color: stopBtn.containsMouse ? "#F7768E" : root.themeBorder
                        border.width: 1

                        Text {
                            anchors.centerIn: parent
                            text: "󰅖"
                            font.family: "JetBrainsMono Nerd Font"
                            font.pixelSize: 15
                            color: stopBtn.containsMouse ? "#131622" : "#F7768E"
                        }

                        MouseArea {
                            id: stopBtn
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: Quickshell.execDetached(["/home/gallo/.config/hypr/scripts/media-control.sh", "stop"])
                        }
                    }
                }

                // Prev / Next Buttons Row
                RowLayout {
                    spacing: 6

                    // Previous Button
                    Rectangle {
                        width: 57
                        height: 30
                        radius: Math.max(0, root.themeRadius - 4)
                        color: prevBtn.containsMouse ? root.themeBorder : root.themeBgAlt
                        border.color: prevBtn.containsMouse ? root.themeAccent : root.themeBorder
                        border.width: 1

                        Text {
                            anchors.centerIn: parent
                            text: "󰒮"
                            font.family: "JetBrainsMono Nerd Font"
                            font.pixelSize: 13
                            color: root.themeFg
                        }

                        MouseArea {
                            id: prevBtn
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: Quickshell.execDetached(["/home/gallo/.config/hypr/scripts/media-control.sh", "previous"])
                        }
                    }

                    // Next Button
                    Rectangle {
                        width: 57
                        height: 30
                        radius: Math.max(0, root.themeRadius - 4)
                        color: nextBtn.containsMouse ? root.themeBorder : root.themeBgAlt
                        border.color: nextBtn.containsMouse ? root.themeAccent : root.themeBorder
                        border.width: 1

                        Text {
                            anchors.centerIn: parent
                            text: "󰒭"
                            font.family: "JetBrainsMono Nerd Font"
                            font.pixelSize: 13
                            color: root.themeFg
                        }

                        MouseArea {
                            id: nextBtn
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: Quickshell.execDetached(["/home/gallo/.config/hypr/scripts/media-control.sh", "next"])
                        }
                    }
                }
            }
        }
    }

    // ==========================================
    // 4. SLIDE-OUT FAVORITES DOCK (Right Screen Edge)
    // ==========================================
    Item {
        anchors {
            right: parent.right
            top: parent.top
            bottom: parent.bottom
        }
        width: root.drawerOpen ? 270 : 36

        Behavior on width {
            NumberAnimation { duration: 220; easing.type: Easing.OutCubic }
        }

        // Background Drawer Container
        Rectangle {
            anchors.fill: parent
            color: root.themeBg
            border.color: root.themeBorder
            border.width: 1

            // Edge Trigger Handle (when collapsed)
            Rectangle {
                anchors {
                    left: parent.left
                    top: parent.top
                    bottom: parent.bottom
                }
                width: 36
                color: drawerToggleArea.containsMouse ? root.themeBorder : "transparent"

                ColumnLayout {
                    anchors.centerIn: parent
                    spacing: 12

                    Text {
                        text: root.drawerOpen ? "󰅖" : "󰒓"
                        font.family: "JetBrainsMono Nerd Font"
                        font.pixelSize: 16
                        color: root.themeAccent
                        Layout.alignment: Qt.AlignHCenter
                    }

                    Text {
                        text: "F\nA\nV\nS"
                        font.family: "JetBrainsMono Nerd Font"
                        font.pixelSize: 11
                        font.bold: true
                        color: "#787C99"
                        lineHeight: 1.1
                        Layout.alignment: Qt.AlignHCenter
                    }
                }

                MouseArea {
                    id: drawerToggleArea
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        root.drawerOpen = !root.drawerOpen;
                        if (root.drawerOpen) {
                            loadFavorites();
                        }
                    }
                }
            }

            // Expanded Favorites List Container
            Item {
                anchors {
                    left: parent.left
                    leftMargin: 44
                    right: parent.right
                    rightMargin: 10
                    top: parent.top
                    topMargin: 16
                    bottom: parent.bottom
                    bottomMargin: 16
                }
                visible: root.drawerOpen
                opacity: root.drawerOpen ? 1.0 : 0.0

                Behavior on opacity {
                    NumberAnimation { duration: 180 }
                }

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 8

                    // Drawer Header
                    RowLayout {
                        Layout.fillWidth: true
                        Text {
                            text: "FAVORITES"
                            font.family: "JetBrainsMono Nerd Font"
                            font.pixelSize: 12
                            font.bold: true
                            color: "#787C99"
                            font.letterSpacing: 1
                        }

                        Item { Layout.fillWidth: true }

                        // Reset to Defaults Button
                        Text {
                            text: "󰑐"
                            font.family: "JetBrainsMono Nerd Font"
                            font.pixelSize: 14
                            color: reloadArea.containsMouse ? root.themeAccent : "#565F89"

                            MouseArea {
                                id: reloadArea
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: loadFavorites()
                            }
                        }
                    }

                    // Dynamic Reorderable & Deletable Favorites ListView
                    ListView {
                        id: favListView
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        model: favModel
                        spacing: 6

                        delegate: Rectangle {
                            id: itemRect
                            width: favListView.width
                            height: 42
                            radius: Math.max(0, root.themeRadius - 4)
                            color: rowHover.containsMouse ? root.themeBorder : root.themeBgAlt
                            border.color: rowHover.containsMouse ? root.themeAccent : root.themeBorder
                            border.width: 1

                            // Launch Button Area (Clickable name & icon, excluding delete and reorder buttons)
                            MouseArea {
                                id: rowHover
                                anchors {
                                    left: parent.left
                                    leftMargin: 24
                                    right: parent.right
                                    rightMargin: 30
                                    top: parent.top
                                    bottom: parent.bottom
                                }
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    if (model.command) {
                                        Quickshell.execDetached(["/home/gallo/.config/quickshell/desktop-hub/manage_favs.sh", "launch", model.command]);
                                    }
                                }
                            }

                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: 6
                                anchors.rightMargin: 6
                                spacing: 6

                                // Reorder Arrows (Up / Down)
                                Column {
                                    spacing: 1
                                    Layout.alignment: Qt.AlignVCenter

                                    Text {
                                        text: "󰁝"
                                        font.family: "JetBrainsMono Nerd Font"
                                        font.pixelSize: 11
                                        color: upArea.containsMouse ? root.themeAccent : "#565F89"
                                        opacity: index > 0 ? 1.0 : 0.2

                                        MouseArea {
                                            id: upArea
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: root.moveItem(index, index - 1)
                                        }
                                    }

                                    Text {
                                        text: "󰁅"
                                        font.family: "JetBrainsMono Nerd Font"
                                        font.pixelSize: 11
                                        color: downArea.containsMouse ? root.themeAccent : "#565F89"
                                        opacity: index < favModel.count - 1 ? 1.0 : 0.2

                                        MouseArea {
                                            id: downArea
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: root.moveItem(index, index + 1)
                                        }
                                    }
                                }

                                // App Icon
                                Text {
                                    text: model.icon
                                    font.family: "JetBrainsMono Nerd Font"
                                    font.pixelSize: 16
                                    color: root.themeAccentAlt
                                }

                                // App Name (Click to launch)
                                Text {
                                    text: model.name
                                    font.family: "JetBrainsMono Nerd Font"
                                    font.pixelSize: 12
                                    font.bold: true
                                    color: "#FFFFFF"
                                    Layout.fillWidth: true
                                    elide: Text.ElideRight
                                }

                                // Delete Button ('✕')
                                Rectangle {
                                    id: delBtn
                                    width: 22
                                    height: 22
                                    radius: Math.max(0, root.themeRadius - 6)
                                    color: delArea.containsMouse ? "#F7768E30" : "transparent"
                                    border.color: delArea.containsMouse ? "#F7768E" : "transparent"
                                    border.width: 1

                                    Text {
                                        anchors.centerIn: parent
                                        text: "✕"
                                        font.family: "JetBrainsMono Nerd Font"
                                        font.pixelSize: 10
                                        font.bold: true
                                        color: delArea.containsMouse ? "#F7768E" : "#565F89"
                                    }

                                    MouseArea {
                                        id: delArea
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: root.removeItem(index)
                                    }
                                }
                            }
                        }
                    }

                    // + Add Application Button
                    Rectangle {
                        Layout.fillWidth: true
                        height: 36
                        radius: Math.max(0, root.themeRadius - 4)
                        color: addArea.containsMouse ? root.themeBorder : root.themeBgAlt
                        border.color: addArea.containsMouse ? root.themeAccent : root.themeBorder
                        border.width: 1

                        RowLayout {
                            anchors.centerIn: parent
                            spacing: 6

                            Text {
                                text: "󰐕"
                                font.family: "JetBrainsMono Nerd Font"
                                font.pixelSize: 13
                                color: root.themeAccent
                            }

                            Text {
                                text: "Add App"
                                font.family: "JetBrainsMono Nerd Font"
                                font.pixelSize: 11
                                font.bold: true
                                color: root.themeFg
                            }
                        }

                        MouseArea {
                            id: addArea
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                Quickshell.execDetached(["/home/gallo/.config/quickshell/desktop-hub/manage_favs.sh", "add"]);
                                loadTimer.start();
                            }
                        }
                    }

                    Timer {
                        id: loadTimer
                        interval: 1000
                        running: false
                        repeat: false
                        onTriggered: loadFavorites()
                    }
                }
            }
        }
    }
}
