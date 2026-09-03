# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-08-27

### Added
- Voice dictation toggle (niri keybind `Mod+E`) that records via `pw-record` and
  transcribes locally with faster-whisper, copying the result to the clipboard.
- DankMaterialShell bar widget `TAbelha Whisper` that appears only while
  recording/transcribing (elapsed timer + `Transcrevendo…`), and collapses out
  of the bar when idle so it never reserves space.
- Silent, lowest-tier desktop notification (app `TAbelha Whisper`) with the
  transcript on completion.
- `config.toml` support (`~/.config/tabelha/whisper-dictate/config.toml`) with
  model, language, device, beam size, multilingual, and live modes
  (`off` / `partial` / `streaming`).
- Orchestrator renames itself to `twhisper` (via `prctl`) for easy process
  identification; stuck recordings can be killed with `pkill -x pw-record`.

## [Unreleased]
