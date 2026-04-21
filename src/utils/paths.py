"""프로젝트 경로 상수 및 런타임 디렉터리 준비 헬퍼."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
SRC_DIR: Path = PROJECT_ROOT / "src"
DATA_DIR: Path = PROJECT_ROOT / "data"
LOGS_DIR: Path = PROJECT_ROOT / "logs"
ASSETS_DIR: Path = PROJECT_ROOT / "assets"
DOCS_DIR: Path = PROJECT_ROOT / "docs"
PLAYLIST_DIR: Path = DATA_DIR / "playlists"
TODOS_PATH: Path = DATA_DIR / "todos.json"

# 런타임 중 생성되는 임시 오디오 (STT 입력 / TTS 출력) — gitignore 대상.
RUNTIME_DIR: Path = PROJECT_ROOT / ".runtime"
RECORDING_DIR: Path = RUNTIME_DIR / "recordings"
TTS_OUTPUT_DIR: Path = RUNTIME_DIR / "tts"


def ensure_runtime_dirs() -> None:
    """로그·임시 오디오 디렉터리를 보장. 앱 부팅 시 한 번만 호출하면 된다."""
    for d in (LOGS_DIR, RUNTIME_DIR, RECORDING_DIR, TTS_OUTPUT_DIR):
        d.mkdir(parents=True, exist_ok=True)
