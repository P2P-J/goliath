"""대화 싸이클 오케스트레이터 (Phase 1 버전).

한 턴의 흐름: 녹음된 WAV → STT → Claude → TTS mp3 → 재생 → 로그.
Phase 2 에서 상태 전이 이벤트 루프와 WAKING/CLAP 진입을 합쳐 확장한다.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import time

import pygame

from ..brain.claude_client import ClaudeClient
from ..utils.logger import log_turn
from ..utils.paths import TTS_OUTPUT_DIR, ensure_runtime_dirs
from ..voice.stt import STT
from ..voice.tts import TTS


@dataclass
class TurnResult:
    user_text: str
    assistant_text: str
    tts_path: Path
    took_ms: int


class Orchestrator:
    """Phase 1: 버튼 한 번 클릭 → 한 싸이클을 돌리는 단순 오케스트레이터."""

    def __init__(self) -> None:
        ensure_runtime_dirs()
        self._stt = STT()
        self._tts = TTS()
        self._claude = ClaudeClient()
        pygame.mixer.init()

    async def process_audio_turn(self, wav_path: Path) -> TurnResult:
        started = time()

        user_text = self._stt.transcribe(wav_path)
        if not user_text:
            user_text = "(무음 혹은 인식 실패)"
        log_turn("user", user_text, meta={"source_wav": wav_path.name})

        assistant_text = await self._claude.ask(user_text)
        if not assistant_text:
            assistant_text = "아엔님, 지금은 응답을 만들지 못했습니다."
        log_turn("assistant", assistant_text)

        tts_path = TTS_OUTPUT_DIR / f"reply_{int(time() * 1000)}.mp3"
        await self._tts.speak_to_file(assistant_text, tts_path)
        self._play_blocking(tts_path)

        took_ms = int((time() - started) * 1000)
        return TurnResult(
            user_text=user_text,
            assistant_text=assistant_text,
            tts_path=tts_path,
            took_ms=took_ms,
        )

    @staticmethod
    def _play_blocking(path: Path) -> None:
        pygame.mixer.music.load(str(path))
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.wait(50)

    def shutdown(self) -> None:
        pygame.mixer.quit()
