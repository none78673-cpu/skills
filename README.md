# review-pages

AI 에이전트가 사용자에게 무엇을 고르게 하거나 검수받을 때 만드는 HTML 페이지의 표준입니다. 채팅에 글로 늘어놓는 대신, 보기·전후 비교·계획을 한 장의 페이지로 보여 주고 사용자가 그 자리에서 버튼으로 고르게 합니다.

- 페이지 종류 네 가지: 고르기 · 바뀐 것 검수(전·후) · 계획 · 결과 보고
- 모든 페이지 공통: 맨 위 「먼저 정해 주세요」, 번호 붙인 질문·보기, 추천 하나와 추천 이유, 실제 모양(그림·소리·영상)으로
- 고른 것 기록: 페이지에서 누른 버튼이 로컬 서버를 거쳐 `_picks.jsonl`에 남아 에이전트가 읽음

## 들어 있는 것

| 파일 | 하는 일 |
|---|---|
| [skills/review-pages/SKILL.md](skills/review-pages/SKILL.md) | 표준 본문 (에이전트가 읽는 지침) |
| [scripts/serve_pages.py](skills/review-pages/scripts/serve_pages.py) | 로컬 정적 서버 + 오디오·영상 위치 이동 + 고른 것 기록(`/_pick`) |
| [scripts/check_page.py](skills/review-pages/scripts/check_page.py) | 주기 전 점검 (열림·콘솔 오류·가로 넘침·첫 화면 스크린숏) |
| [scripts/pick_example.html](skills/review-pages/scripts/pick_example.html) | 고르는 버튼·추천·기록이 들어 있는 최소 틀 |

## 쓰는 법

1. `skills/review-pages` 폴더를 에이전트의 스킬 폴더에 넣습니다(예: Claude Code는 `~/.claude/skills/` 또는 프로젝트의 `.claude/skills/`).
2. 필요한 것: Python 3. 점검 스크립트는 `pip install playwright` 후 `playwright install chromium`.
3. 에이전트에게 「비교 페이지로 보여 줘」, 「바뀐 거 전후로 보여 줘」처럼 말하면 이 표준대로 페이지를 만들고 로컬 서버 주소를 줍니다.
