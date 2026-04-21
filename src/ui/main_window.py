"""Phase 1 MVP HUD 창.

버튼 한 개로 녹음 토글 → 오케스트레이터 싸이클 → 대화 로그 표시.
Phase 5 에서 반투명 오버레이·음파 애니메이션으로 교체 예정.
"""

from __future__ import annotations

import asyncio
import threading
from pathlib import Path
from time import time

from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..core.orchestrator import Orchestrator, TurnResult
from ..core.state import AssistantState
from ..utils.audio_io import record_until_stop
from ..utils.logger import log_turn
from ..utils.paths import RECORDING_DIR, ensure_runtime_dirs


class RecordingWorker(QThread):
    finished_ok = pyqtSignal(Path)
    failed = pyqtSignal(str)

    def __init__(self, out_path: Path, stop_event: threading.Event) -> None:
        super().__init__()
        self._out = out_path
        self._stop = stop_event

    def run(self) -> None:
        try:
            saved = record_until_stop(self._out, self._stop)
            self.finished_ok.emit(saved)
        except Exception as e:  # noqa: BLE001
            self.failed.emit(str(e))


class TurnWorker(QThread):
    finished_ok = pyqtSignal(object)
    failed = pyqtSignal(str)

    def __init__(self, orchestrator: Orchestrator, wav_path: Path) -> None:
        super().__init__()
        self._orch = orchestrator
        self._wav = wav_path

    def run(self) -> None:
        try:
            result = asyncio.run(self._orch.process_audio_turn(self._wav))
            self.finished_ok.emit(result)
        except Exception as e:  # noqa: BLE001
            self.failed.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        ensure_runtime_dirs()
        self.setWindowTitle("GOLIATH — Phase 1 MVP")
        self.resize(560, 640)

        self._state = AssistantState.IDLE
        self._stop_event: threading.Event | None = None
        self._recording_worker: RecordingWorker | None = None
        self._turn_worker: TurnWorker | None = None

        central = QWidget()
        layout = QVBoxLayout(central)

        self._state_label = QLabel(self._format_state())
        state_font = QFont()
        state_font.setPointSize(11)
        state_font.setBold(True)
        self._state_label.setFont(state_font)
        self._state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._state_label)

        self._transcript = QTextEdit()
        self._transcript.setReadOnly(True)
        self._transcript.setPlaceholderText("아직 대화가 없습니다. 아래 버튼을 눌러 대화를 시작하세요.")
        layout.addWidget(self._transcript, stretch=1)

        self._button = QPushButton("대화 시작")
        self._button.setMinimumHeight(48)
        self._button.clicked.connect(self._on_button_clicked)
        layout.addWidget(self._button)

        self.setCentralWidget(central)

        self._transcript.append("시스템: 골리앗 초기화 중입니다. 잠시만 기다려 주세요. (최초 실행 시 Whisper 모델 다운로드로 수십 초 소요)")
        self._orch: Orchestrator | None = None
        self._button.setEnabled(False)
        # 이벤트 루프가 창을 먼저 그린 뒤 초기화되도록 지연 호출.
        QTimer.singleShot(100, self._init_orchestrator)

    def _init_orchestrator(self) -> None:
        try:
            self._orch = Orchestrator()
            self._transcript.append("시스템: 초기화 완료. 대화를 시작할 수 있습니다.")
            log_turn("system", "Phase 1 MVP 부팅 완료")
            self._button.setEnabled(True)
        except Exception as e:  # noqa: BLE001
            self._transcript.append(f"시스템: 초기화 실패 — {e}")
            self._set_state(AssistantState.ERROR)
            self._button.setEnabled(False)

    def _format_state(self) -> str:
        return f"상태: {self._state.label()}"

    def _set_state(self, state: AssistantState) -> None:
        self._state = state
        self._state_label.setText(self._format_state())

    def _on_button_clicked(self) -> None:
        if self._orch is None:
            QMessageBox.warning(self, "오류", "오케스트레이터가 초기화되지 않았습니다.")
            return

        if self._state == AssistantState.IDLE:
            self._start_recording()
        elif self._state == AssistantState.LISTEN:
            self._stop_recording()

    def _start_recording(self) -> None:
        self._set_state(AssistantState.LISTEN)
        self._button.setText("녹음 중지 및 전송")

        self._stop_event = threading.Event()
        wav_path = RECORDING_DIR / f"rec_{int(time() * 1000)}.wav"
        self._recording_worker = RecordingWorker(wav_path, self._stop_event)
        self._recording_worker.finished_ok.connect(self._on_recording_done)
        self._recording_worker.failed.connect(self._on_worker_failed)
        self._recording_worker.start()

    def _stop_recording(self) -> None:
        if self._stop_event is not None:
            self._stop_event.set()
        self._button.setEnabled(False)
        self._button.setText("처리 중...")

    def _on_recording_done(self, wav_path: Path) -> None:
        self._set_state(AssistantState.THINK)
        self._transcript.append(f"시스템: 녹음 완료 ({wav_path.name}). 인식·응답 생성 중...")
        assert self._orch is not None
        self._turn_worker = TurnWorker(self._orch, wav_path)
        self._turn_worker.finished_ok.connect(self._on_turn_done)
        self._turn_worker.failed.connect(self._on_worker_failed)
        self._turn_worker.start()

    def _on_turn_done(self, result: object) -> None:
        assert isinstance(result, TurnResult)
        self._transcript.append(f"아엔님: {result.user_text}")
        self._transcript.append(f"골리앗: {result.assistant_text}")
        self._transcript.append(f"시스템: 소요 {result.took_ms} ms\n")
        self._set_state(AssistantState.IDLE)
        self._button.setEnabled(True)
        self._button.setText("대화 시작")

    def _on_worker_failed(self, message: str) -> None:
        self._transcript.append(f"시스템 오류: {message}")
        log_turn("system", f"오류: {message}")
        self._set_state(AssistantState.IDLE)
        self._button.setEnabled(True)
        self._button.setText("다시 시도")

    def closeEvent(self, event) -> None:  # noqa: N802 (Qt API)
        if self._orch is not None:
            self._orch.shutdown()
        super().closeEvent(event)
