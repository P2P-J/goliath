"""대화 로그 이중 기록 (JSONL + Markdown).

매일 `logs/YYYY-MM-DD.jsonl` 과 `logs/YYYY-MM-DD.md` 두 파일에 append 한다.
JSONL 은 기계 파싱용, Markdown 은 사람이 바로 훑어보기 위함.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Literal

from .paths import LOGS_DIR, ensure_runtime_dirs

Role = Literal["user", "assistant", "system"]

_ROLE_LABEL: dict[Role, str] = {
    "user": "아엔님",
    "assistant": "골리앗",
    "system": "시스템",
}


def _today_stem() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def log_turn(role: Role, content: str, meta: dict[str, Any] | None = None) -> None:
    """한 턴의 발화를 두 파일에 기록한다."""
    ensure_runtime_dirs()
    ts = datetime.now().isoformat(timespec="seconds")
    stem = _today_stem()

    record: dict[str, Any] = {"ts": ts, "role": role, "content": content}
    if meta:
        record["meta"] = meta

    jsonl_path = LOGS_DIR / f"{stem}.jsonl"
    with jsonl_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    label = _ROLE_LABEL[role]
    md_path = LOGS_DIR / f"{stem}.md"
    with md_path.open("a", encoding="utf-8") as f:
        f.write(f"**{ts} · {label}:** {content}\n\n")
