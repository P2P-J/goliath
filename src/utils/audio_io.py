"""마이크 입력 녹음 유틸 (pyaudio 기반).

Phase 1 은 버튼 토글(시작 클릭 → 종료 클릭) 방식으로 `stop_event` 를 세운다.
Phase 2 에서 VAD / 박수 감지 루프로 확장될 예정.
"""

from __future__ import annotations

import threading
import wave
from pathlib import Path

import pyaudio


FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
DEFAULT_MAX_SECONDS = 30.0


def record_until_stop(
    out_path: str | Path,
    stop_event: threading.Event,
    max_seconds: float = DEFAULT_MAX_SECONDS,
) -> Path:
    """`stop_event.set()` 혹은 `max_seconds` 경과까지 마이크를 녹음해 WAV 로 저장."""
    pa = pyaudio.PyAudio()
    sample_size = pa.get_sample_size(FORMAT)
    stream = pa.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
    )
    frames: list[bytes] = []
    total_chunks = int(RATE / CHUNK * max_seconds)
    try:
        for _ in range(total_chunks):
            if stop_event.is_set():
                break
            frames.append(stream.read(CHUNK, exception_on_overflow=False))
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out), "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(sample_size)
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))
    return out
