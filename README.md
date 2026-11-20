# skills

AI 에이전트(Claude Code 등)용 스킬 모음입니다. 스킬 하나 = `skills/<이름>/` 폴더 하나이고, 폴더 안의 `SKILL.md`가 에이전트가 읽는 지침입니다.

## 스킬 목록

| 스킬 | 하는 일 | 필요한 것 |
|---|---|---|
| [review-pages](skills/review-pages/SKILL.md) | 사용자에게 고르게 하거나 검수받을 때 만드는 HTML 페이지 표준 — 고르기·전후 비교·계획·결과 보고 네 종류, 추천 표시, 버튼으로 고른 것 기록, 로컬 서버·점검 스크립트 | Python 3 (점검은 playwright) |

### review-pages 예시

채팅에 글로 늘어놓는 대신, 에이전트가 이런 페이지를 만들어 로컬 주소(`http://127.0.0.1:…`)로 줍니다. 누른 버튼은 기록되어 에이전트가 읽습니다.

**고르기** — 보기마다 카드, 좋은 점·걸리는 점에 무게 표시, 추천 하나와 추천 이유

![고르기 페이지 예시](docs/example_pick.png)

**바뀐 것 검수** — 고친 곳마다 전·후를 나란히, 색으로 종류(고침·새로·지움), 넣기/빼기 버튼

![바뀐 것 검수 페이지 예시](docs/example_diff.png)

예시 원본: [docs/example_pick.html](docs/example_pick.html) · [docs/example_diff.html](docs/example_diff.html) (내려받아 브라우저로 열면 버튼까지 눌러 볼 수 있습니다)

## 쓰는 법

1. 쓰고 싶은 스킬 폴더(`skills/<이름>`)를 에이전트의 스킬 폴더에 넣습니다. 예: Claude Code는 `~/.claude/skills/` 또는 프로젝트의 `.claude/skills/`.
2. 표의 「필요한 것」을 설치합니다.
3. 에이전트에게 평소처럼 일을 시키면, 스킬 설명(`SKILL.md` 머리말)에 맞는 요청일 때 에이전트가 알아서 그 스킬을 씁니다.

## review-pages 들어 있는 것

| 파일 | 하는 일 |
|---|---|
| [SKILL.md](skills/review-pages/SKILL.md) | 표준 본문 |
| [scripts/serve_pages.py](skills/review-pages/scripts/serve_pages.py) | 로컬 정적 서버 + 오디오·영상 위치 이동 + 고른 것 기록(`/_pick`) |
| [scripts/check_page.py](skills/review-pages/scripts/check_page.py) | 주기 전 점검 (열림·콘솔 오류·가로 넘침·첫 화면 스크린숏). `pip install playwright` 후 `playwright install chromium` |
| [scripts/pick_example.html](skills/review-pages/scripts/pick_example.html) | 고르는 버튼·추천·기록이 들어 있는 최소 틀 |
