"""edge-tts 기반 한국어 TTS.

기본 보이스는 `ko-KR-InJoonNeural`(남성). 속도·피치는 약간 낮춰 차분한 톤.
Phase 6 에서 librosa 후처리로 J.A.R.V.I.S. 스타일에 더 근접하게 튜닝 예정.
"""

from __future__ import annotations

from pathlib import Path

import edge_tts

KO_MALE_VOICE = "ko-KR-InJoonNeural"


class TTS:
    def __init__(
        self,
        voice: str = KO_MALE_VOICE,
        rate: str = "-5%",
        pitch: str = "-3Hz",
    ) -> None:
        self._voice = voice
        self._rate = rate
        self._pitch = pitch

    async def speak_to_file(self, text: str, out_path: str | Path) -> Path:
        """텍스트를 mp3 파일로 합성해 저장한 뒤 Path 반환."""
        out = Path(out_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        communicate = edge_tts.Communicate(
            text,
            voice=self._voice,
            rate=self._rate,
            pitch=self._pitch,
        )
        await communicate.save(str(out))
        return out
