# GOLIATH

영화 아이언맨의 J.A.R.V.I.S. 스타일을 오마주한 개인용 AI 음성 비서 데스크톱 애플리케이션.

## 컨셉

- 항상 대기 → 음성 명령 → 실제 행동(앱 실행·파일 검색·정보 조회 등) → 전 대화 기록
- 차분하고 절제된 존댓말 페르소나
- Windows 우선, macOS 2차 지원

## 기술 스택

| 영역 | 라이브러리 |
| --- | --- |
| LLM | Claude Agent SDK (Max 플랜) |
| STT | faster-whisper |
| TTS | edge-tts + librosa 후처리 |
| 웨이크업 | openWakeWord + 박수 2회(pyaudio) |
| 오디오 재생 | pygame.mixer |
| UI | PyQt6 (QFramelessWindow HUD 오버레이) |
| 외부 API | 기상청 단기예보, 한국환경공단 에어코리아 |

## 폴더 구조

```
goliath/
├── src/            # 애플리케이션 소스
│   ├── core/       # Orchestrator, 상태 머신, 설정
│   ├── voice/      # 웨이크업·박수·STT·TTS
│   ├── brain/      # Claude Agent SDK 래퍼, 프롬프트
│   ├── tools/      # 기상·미세먼지·앱·파일·TODO·음악·웹 검색
│   ├── ui/         # PyQt6 HUD
│   └── utils/      # 로거, 오디오 유틸, 경로
├── data/           # todos.json, playlists/
├── logs/           # 일일 대화 로그 (JSONL + MD)
├── assets/         # 부팅 효과음, 아이콘
├── docs/           # 설계 문서
└── tests/
```

## 설치 (Phase 0 기준)

```bash
git clone <repo-url>
cd goliath
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
copy .env.example .env    # 그리고 API 키를 채워넣으세요
```

필요한 외부 API 키:

- `KMA_API_KEY` — [data.go.kr 기상청 단기예보 조회 서비스](https://www.data.go.kr/)
- `AIRKOREA_API_KEY` — [data.go.kr 한국환경공단 에어코리아](https://www.data.go.kr/)

## 로드맵

| Phase | 내용 | 상태 |
| --- | --- | --- |
| 0 | 프로젝트 스켈레톤 | 진행 중 |
| 1 | MVP — 버튼 기반 대화 (STT → LLM → TTS) | 예정 |
| 2 | 웨이크업 (웨이크워드 + 박수 2회) | 예정 |
| 3 | 시작 브리핑 (부팅음·날씨·미세먼지·TODO) | 예정 |
| 4 | 명령 도구 5종 (apps·files·todos·music·web_search) | 예정 |
| 5 | HUD UI (PyQt6 반투명 오버레이) | 예정 |
| 6 | 튜닝·배포·확장 | 예정 |

상세 설계는 [`docs/골리앗_설계문서.docx`](docs/) 참고.
