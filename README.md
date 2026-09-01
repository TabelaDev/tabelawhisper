<div align="center">

# Tabela Whisper

**English** · [Português](README.pt-BR.md)

[![Python](https://img.shields.io/badge/python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)](pyproject.toml)
[![uv](https://img.shields.io/badge/uv-astro-DEA584?style=flat-square&logo=astral&logoColor=white)](https://github.com/astral-sh/uv)
[![typos](https://img.shields.io/badge/typos-checked-1B1FCA?style=flat-square)](https://github.com/astral-sh/typos)
[![License: AGPL-3.0](https://img.shields.io/badge/license-AGPL--3.0-blue?style=flat-square)](LICENSE)

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/ianptkcs)

</div>

---

Voice dictation for [DankMaterialShell](https://github.com/TabelaDev/dankmaterialshell)
on niri (Wayland): press a key, speak, and the transcribed text lands on your
clipboard. Feedback lives in the **dank bar** as a small widget that appears
only while you are dictating, and a **silent, low-priority notification** shows
the result when you stop.

No floating windows, no always-on indicators: the widget collapses out of the
bar when idle, so it never reserves space.

## How it works

1. A niri keybind (default `Mod+E`) calls the toggler.
2. First press starts `pw-record` (PipeWire) capturing your microphone.
3. When you press again, recording stops and the audio is transcribed locally
   with [faster-whisper](https://github.com/SYSTRAN/faster-whisper).
4. The transcript is copied to the clipboard and a desktop notification is shown.

Everything runs locally; nothing is sent to the network.

## The dank bar widget

The `Tabela Whisper` widget (a dms plugin) reads the shared state file and
shows itself only while active:

- **Recording**: a red mic icon plus an `mm:ss` elapsed timer.
- **Transcribing**: an amber mic icon plus `Transcrevendo…`.
- **Idle / done**: hidden. The bar slot collapses, so no space is reserved.

When transcription finishes, the widget hides and a **silent, lowest-tier**
desktop notification (app name `Tabela Whisper`) shows the transcript.

## Requirements

- Linux with **PipeWire** (`pw-record`) and **WirePlumber**.
- **niri** (or any compositor that can run the toggle script).
- **DankMaterialShell** (quickshell) for the bar widget.
- `wl-clipboard` (`wl-copy`) for clipboard copy.
- `libnotify` (`notify-send`) for the completion notification.
- Python 3.12+ and [`uv`](https://github.com/astral-sh/uv).

## Install

```bash
git clone https://github.com/TabelaDev/tabelawhisper
cd tabelawhisper
./install.sh
```

`install.sh` will:

- sync the `uv` environment (downloads torch + faster-whisper on first run);
- drop a keybind helper at `~/.config/niri/scripts/whisper-dictate.sh`;
- symlink the dms plugin into `~/.config/DankMaterialShell/plugins/whisper-dictate`;
- create `~/.config/tabela/whisper-dictate/config.toml` from the example if absent.

Then:

1. Add the keybind in your niri config (the script path above):
   ```kdl
   bind Mod+E { spawn "~/.config/niri/scripts/whisper-dictate.sh"; }
   ```
2. Reload dms (restart quickshell) and **enable the `Tabela Whisper` widget**
   in the bar settings.
3. Press `Mod+E` and start talking.

## Configuration

Config lives at `~/.config/tabela/whisper-dictate/config.toml`. See
[`config/whisper-dictate.toml.example`](config/whisper-dictate.toml.example)
for all options. Highlights:

| Key | Default | Meaning |
| --- | --- | --- |
| `model` | `"small"` | faster-whisper model size (`tiny`…`large-v3`). |
| `language` | `"auto"` | `"auto"` detects pt/en per segment; or force e.g. `"pt"`. |
| `device` | `"cpu"` | `"cpu"` is safe on systems without CUDA. |
| `multilingual` | `true` | enable per-segment language detection. |
| `beam_size` | `5` | beam search width for better accuracy. |
| `live_mode` | `"off"` | `off` / `partial` / `streaming` (see below). |
| `copy_clipboard` | `true` | copy the transcript to the clipboard on finish. |
| `partial_interval` | `3` | seconds between re-transcriptions in `partial` mode. |

### Live modes

- **`off`** (default): record, then transcribe once when you stop. The bar
  widget shows the timer; the transcript appears on the notification.
- **`partial`**: re-transcribes the growing clip every `partial_interval`
  seconds (lighter than streaming).
- **`streaming`**: a continuous child process streams text live into the state
  file. Heavier on CPU; use when you want to watch the text grow.

## Debugging

- State file: `/tmp/whisper-dictate.json` (`state`, `elapsed`, `start`, `text`).
- Log: `/tmp/whisper-dictate.log`.
- Processes: the recorder is `pw-record`; the orchestrator renames itself to
  `twhisper` (via `prctl`) so it is easy to find:
  ```bash
  pkill -x pw-record     # force-stop a stuck recording
  pkill -x twhisper      # force-stop the orchestrator
  ```

## Development

```bash
uv sync --all-groups
uv run ruff format .
uv run ruff check .
uv run basedpyright bin
uv run pytest
```

## License

AGPL-3.0. See [LICENSE](LICENSE).
