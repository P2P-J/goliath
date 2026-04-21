"""Goliath 진입점. Phase 1 MVP — PyQt6 창 기동."""

from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from src.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
