from __future__ import annotations

from pathlib import Path

from whisper_core import DEFAULTS, load_config, transcribe_options


def test_defaults_when_no_file() -> None:
    cfg = load_config(Path("/nonexistent/whisper-dictate-test.toml"))
    assert cfg["model"] == DEFAULTS["model"] == "small"
    assert cfg["live_mode"] == "off"
    assert cfg["copy_clipboard"] is True
    assert cfg["partial_interval"] == 3


def test_override_merges(tmp_path: Path) -> None:
    p = tmp_path / "c.toml"
    p.write_text('model = "small"\nlanguage = "en"\nlive_mode = "streaming"\n')
    cfg = load_config(p)
    assert cfg["model"] == "small"
    assert cfg["language"] == "en"
    assert cfg["live_mode"] == "streaming"
    # unknown keys are ignored, untouched defaults remain
    assert cfg["partial_interval"] == 3


def test_transcribe_options_resolves_auto() -> None:
    cfg = {"language": "auto", "multilingual": True}
    lang, ml = transcribe_options(cfg)
    assert lang is None
    assert ml is True


def test_transcribe_options_resolves_pinned() -> None:
    cfg = {"language": "pt", "multilingual": False}
    lang, ml = transcribe_options(cfg)
    assert lang == "pt"
    assert ml is False


def test_transcribe_options_resolves_empty_as_auto() -> None:
    cfg = {"language": "", "multilingual": True}
    lang, ml = transcribe_options(cfg)
    assert lang is None
    assert ml is True
