"""상태 열거형.

설계 문서 §4.2 의 6 상태를 그대로 사용. Phase 1 에서는 WAKING 을 쓰지 않는다
(버튼 트리거 방식이므로) — Phase 2 웨이크워드 도입 시 활성화.
"""

from __future__ import annotations

from enum import Enum, auto


class AssistantState(Enum):
    IDLE = auto()
    WAKING = auto()
    LISTEN = auto()
    THINK = auto()
    SPEAK = auto()
    ERROR = auto()

    def label(self) -> str:
        return {
            AssistantState.IDLE: "대기 중",
            AssistantState.WAKING: "깨어나는 중",
            AssistantState.LISTEN: "듣는 중",
            AssistantState.THINK: "생각 중",
            AssistantState.SPEAK: "말하는 중",
            AssistantState.ERROR: "오류",
        }[self]
