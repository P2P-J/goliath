"""faster-whisper 기반 한국어 STT.

첫 호출 시 small 모델 (~460MB) 이 자동 다운로드된다. GPU 가 없으면 CPU 로 동작.
Phase 1 은 파일 기반 전사만 지원, 실시간 스트리밍은 Phase 2 에서 확장.
"""

from __future__ import annotations

from pathlib import Path

from faster_whisper import WhisperModel


class STT:
    def __init__(
        self,
        model_size: str = "small",
        device: str = "cpu",
        compute_type: str = "int8",
        language: str = "ko",
    ) -> None:
        # 기본은 CPU + int8 양자화. Phase 6 에서 CUDA 환경이면 `device="cuda"`·
        # `compute_type="float16"` 으로 교체 가능.
        self._model = WhisperModel(model_size, device=device, compute_type=compute_type)
        self._language = language

    def transcribe(self, wav_path: str | Path) -> str:
        """WAV 파일을 한국어 텍스트로 변환한다. 빈 오디오는 빈 문자열을 반환."""
        segments, _info = self._model.transcribe(
            str(wav_path),
            language=self._language,
            beam_size=5,
            vad_filter=True,
        )
        return " ".join(seg.text.strip() for seg in segments).strip()
