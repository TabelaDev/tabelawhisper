"""Shared helpers for tabela-whisper: config, model, and the on-disk state file.

The state file at ``/tmp/whisper-dictate.json`` is the single source of truth
shared between the shell toggle (whisper_dictate), the streaming transcriber
(whisper_stream) and the dms indicator plugin. It always carries at least
``state`` (``recording`` | ``transcribing`` | ``done`` | ``idle``) and, while
recording, ``start`` (epoch seconds) so the indicator can show elapsed time.
"""

from __future__ import annotations

import json
import os
import tomllib
from pathlib import Path

STATE_PATH = Path("/tmp/whisper-dictate.json")
CONFIG_PATH = Path(
    os.environ.get("WHISPER_DICTATE_CONFIG", "~/.config/tabela/whisper-dictate/config.toml")
).expanduser()

DEFAULTS = {
    "model": "small",
    "language": "auto",  # auto | pt | en | ... (auto detects pt/en mixed per segment)
    "multilingual": True,  # detect language independently on every segment
    "live_mode": "off",  # off | partial | streaming
    "partial_interval": 3,  # seconds between re-transcriptions (partial)
    "copy_clipboard": True,
    "indicator": True,
    "engine": "faster-whisper",
    "device": "cpu",  # cpu | cuda (falls back to cpu if CUDA is unavailable)
    "beam_size": 5,  # higher = more accurate, slower
    "wav": "/tmp/whisper-dictate.wav",
    "state_file": str(STATE_PATH),
}


def load_config(path: Path | None = None) -> dict:
    cfg = dict(DEFAULTS)
    p = path or CONFIG_PATH
    if p and p.exists():
        with p.open("rb") as f:
            data = tomllib.load(f)
        cfg.update({k: v for k, v in data.items() if k in DEFAULTS})
    return cfg


def read_state() -> dict:
    try:
        return json.loads(STATE_PATH.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {"state": "idle"}


def write_state(patch: dict) -> dict:
    """Merge ``patch`` into the existing state (preserving ``start``) and write it."""
    state = read_state()
    state.update(patch)
    STATE_PATH.write_text(json.dumps(state))
    return state


_MODEL = None


def get_model(model_size: str, language: str | None = None, device: str = "cpu"):
    import faster_whisper

    global _MODEL
    if _MODEL is None:
        try:
            _MODEL = faster_whisper.WhisperModel(model_size, device=device)
        except Exception:
            if device != "cpu":
                _MODEL = faster_whisper.WhisperModel(model_size, device="cpu")
            else:
                raise
    return _MODEL


def transcribe_options(cfg: dict) -> tuple[str | None, bool]:
    """Resolve the kwargs for ``model.transcribe`` from config.

    ``language="auto"`` (or empty/``None``) becomes ``None`` so faster-whisper
    auto-detects; ``multilingual`` enables per-segment language detection so pt
    and en can be mixed within a single recording.
    """
    raw = cfg.get("language") or "auto"
    lang = None if raw in ("auto", "", None) else raw
    multilingual = bool(cfg.get("multilingual", True))
    return lang, multilingual


def transcribe_file(
    path: str,
    model_size: str,
    language: str | None,
    device: str = "cpu",
    multilingual: bool = True,
    beam_size: int = 5,
) -> str:
    model = get_model(model_size, language, device)
    lang, ml = transcribe_options({"language": language, "multilingual": multilingual})
    segments, _ = model.transcribe(
        path,
        language=lang,
        multilingual=ml,
        beam_size=beam_size,
        vad_filter=True,
        vad_parameters={
            "threshold": 0.3,
            "min_speech_duration_ms": 150,
            "speech_pad_ms": 300,
        },
        condition_on_previous_text=False,
        temperature=[0.0, 0.4, 0.6, 0.8],
    )
    return "".join(seg.text for seg in segments).strip()
