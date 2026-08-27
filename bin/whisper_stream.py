#!/usr/bin/env python3
"""Streaming transcriber for tabela-whisper (live_mode = streaming).

Reads raw PCM16 mono 16 kHz from stdin (piped from ``pw-record``), keeps a
rolling buffer, and re-transcribes it every couple of seconds so the dms
indicator shows the transcript growing while you speak. On EOF it writes the
final ``done`` state.
"""

from __future__ import annotations

import sys
import time

import numpy as np

from whisper_core import get_model, load_config, transcribe_options, write_state

RETRANSCRIBE_EVERY = 2.0


def main() -> None:
    cfg = load_config()
    model = get_model(cfg["model"], cfg["language"], cfg.get("device", "cpu"))
    lang, multilingual = transcribe_options(cfg)
    beam_size = cfg.get("beam_size", 5)
    vad_parameters = {"threshold": 0.3, "min_speech_duration_ms": 150, "speech_pad_ms": 300}
    temperature = [0.0, 0.4, 0.6, 0.8]

    buf: list[np.ndarray] = []
    last = time.time()
    while True:
        data = sys.stdin.buffer.read(4096)
        if not data:
            break
        buf.append(np.frombuffer(data, dtype=np.int16))
        if time.time() - last >= RETRANSCRIBE_EVERY and buf:
            audio = np.concatenate(buf).astype(np.float32) / 32768.0
            segments, _ = model.transcribe(
                audio,
                language=lang,
                multilingual=multilingual,
                beam_size=beam_size,
                vad_filter=True,
                vad_parameters=vad_parameters,
                condition_on_previous_text=False,
                temperature=temperature,
            )
            text = "".join(s.text for s in segments).strip()
            write_state({"state": "recording", "text": text})
            last = time.time()

    if buf:
        audio = np.concatenate(buf).astype(np.float32) / 32768.0
        segments, _ = model.transcribe(
            audio,
            language=lang,
            multilingual=multilingual,
            beam_size=beam_size,
            vad_filter=True,
            vad_parameters=vad_parameters,
            condition_on_previous_text=False,
            temperature=temperature,
        )
        text = "".join(s.text for s in segments).strip()
        write_state({"state": "done", "text": text})


if __name__ == "__main__":
    main()
