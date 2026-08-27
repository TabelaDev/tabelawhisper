import QtQuick
import QtQuick.Layouts
import Quickshell
import qs.Common
import qs.Services
import qs.Widgets
import qs.Modules.Plugins
import Quickshell.Io

PluginComponent {
    id: root
    pluginId: "whisper-dictate"

    property bool recording: false
    property bool transcribing: false
    property int startTime: 0
    property int elapsed: 0
    property var stateObj: ({})

    function fmt(sec) {
        sec = Math.max(0, sec | 0);
        const m = Math.floor(sec / 60);
        const s = sec % 60;
        return (m < 10 ? "0" : "") + m + ":" + (s < 10 ? "0" : "") + s;
    }

    FileView {
        id: stateFile
        path: "/tmp/whisper-dictate.json"
        onLoaded: {
            try {
                root.stateObj = JSON.parse(text());
            } catch (e) {
                root.stateObj = {};
            }
        }
        onLoadFailed: root.stateObj = {}
    }

    // FileView has no watch property here, so poll the state file.
    Timer {
        interval: 250
        running: true
        repeat: true
        onTriggered: stateFile.reload()
    }

    // Keep the elapsed timer ticking while recording. It is computed from the
    // recording start timestamp written by the orchestrator (the state file's
    // own elapsed field is not maintained during recording).
    Timer {
        interval: 1000
        running: root.recording
        repeat: true
        onTriggered: root.elapsed = Math.max(0, Math.floor(Date.now() / 1000 - root.startTime))
    }

    onStateObjChanged: {
        const st = (root.stateObj && root.stateObj.state) || "";
        root.recording = (st === "recording");
        root.transcribing = (st === "transcribing");
        root.startTime = (root.stateObj && root.stateObj.start) || 0;
        if (root.recording)
            root.elapsed = Math.max(0, Math.floor(Date.now() / 1000 - root.startTime));
        else if (!root.transcribing)
            root.elapsed = 0;
        // Collapse the bar slot while idle via the dms visibility API. Setting
        // the QML `visible` property only fades the pill; this actually frees
        // the space by animating the pill width to 0.
        root.setVisibilityOverride(root.recording || root.transcribing);
    }

    horizontalBarPill: Component {
        Row {
            spacing: 6

            DankIcon {
                name: "mic"
                size: Theme.fontSizeSmall
                color: root.transcribing ? Theme.warning : Theme.error
                anchors.verticalCenter: parent.verticalCenter
            }

            StyledText {
                text: root.transcribing ? "Transcrevendo…" : root.fmt(root.elapsed)
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.surfaceText
                anchors.verticalCenter: parent.verticalCenter
            }
        }
    }

    verticalBarPill: Component {
        Column {
            spacing: 2

            DankIcon {
                name: "mic"
                size: Theme.fontSizeSmall
                color: root.transcribing ? Theme.warning : Theme.error
                anchors.horizontalCenter: parent.horizontalCenter
            }

            StyledText {
                text: root.transcribing ? "…" : root.fmt(root.elapsed)
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.surfaceText
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }
    }
}
