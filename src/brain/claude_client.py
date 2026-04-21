"""Claude Agent SDK 비동기 래퍼.

Max 플랜 로그인(`claude` CLI)을 배경으로 사용한다.
Phase 1 은 단일 턴 호출만, Phase 4 에서 tools= 인자로 도구 등록 확장 예정.
"""

from __future__ import annotations

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    TextBlock,
    query,
)

from .prompts import SYSTEM_PROMPT


class ClaudeClient:
    """골리앗 페르소나로 단일 턴 질의응답을 수행하는 래퍼."""

    def __init__(self, system_prompt: str = SYSTEM_PROMPT) -> None:
        self._options = ClaudeAgentOptions(
            system_prompt=system_prompt,
            permission_mode="bypassPermissions",
        )

    async def ask(self, user_text: str) -> str:
        """사용자 발화를 받아 골리앗의 답변 텍스트를 반환한다."""
        chunks: list[str] = []
        async for message in query(prompt=user_text, options=self._options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        chunks.append(block.text)
        return "".join(chunks).strip()
