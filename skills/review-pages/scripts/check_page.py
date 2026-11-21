"""검수 페이지를 사용자에게 주기 전 점검. python check_page.py <주소> <스크린숏.png> (-I 없이 — 사용자 영역에 깐 playwright를 찾게, SKILL.md 3절)

- 주소가 열리나(200)
- 콘솔 오류·스크립트 오류·못 불러온 파일이 없나
- 가로로 넘치나(1280 폭 기준, 넘친 요소 몇 개를 알려 줌)
- 「먼저 정해 주세요」(답할 것이 없으면 「결론」 한 줄)가 첫 화면(1280x800) 안에 보이나 — 둘 다 없어도 문제
- 고르는 추천 버튼(넣기·빼기 말고)이 있으면 「추천 이유」 글이 있나
- 질문(data-q)마다 추천 버튼이 하나 이하인가
- 페이지 안 링크(#q1 등)가 실제로 있는 자리를 가리키나
- 페이지가 /_pick 으로 고른 것을 보내면, 이 서버가 기록을 받는 판인가(GET /_pick 200)
- 첫 화면 스크린숏을 남긴다 — 에이전트가 열어서 본다

종료 코드: 0 문제 없음 / 1 페이지 문제(고친 뒤 다시) / 2 점검 도구가 못 돎(playwright·브라우저 없음 등)
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
try:
    from playwright.sync_api import sync_playwright
except ImportError as e:
    print(f"점검 도구 못 돎: {e} (pip install playwright)"); sys.exit(2)

url, shot = sys.argv[1], sys.argv[2]
problems = []
try:
    with sync_playwright() as p:
        try:
            b = p.chromium.launch(channel="msedge")
        except Exception:
            b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1280, "height": 800})
        errors = []
        pg.on("console", lambda m: errors.append(m.text) if m.type == "error" and "Failed to load resource" not in m.text else None)
        pg.on("response", lambda r: errors.append(f"{r.status} {r.url}") if r.status >= 400 and not r.url.endswith("/favicon.ico") and not r.url.endswith("/_pick") else None)
        pg.on("pageerror", lambda e: errors.append(str(e)))
        r = pg.goto(url, wait_until="load")
        pg.wait_for_timeout(800)
        if not r or r.status != 200:
            problems.append(f"열기 실패: {r.status if r else '응답 없음'}")
        problems += [f"콘솔 오류: {e}" for e in errors]
        over = pg.evaluate("""() => {
          const W = document.documentElement.clientWidth;
          if (document.documentElement.scrollWidth <= W + 1) return [];
          return [...document.querySelectorAll('body *')]
            .filter(e => e.getBoundingClientRect().right > W + 1)
            .slice(0, 5).map(e => e.tagName.toLowerCase() + (e.className ? '.' + String(e.className).split(' ')[0] : ''));
        }""")
        if over:
            problems.append("가로 넘침: " + ", ".join(over))
        top_of = """(word) => {
          const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
          while (w.nextNode()) if (w.currentNode.textContent.includes(word))
            return w.currentNode.parentElement.getBoundingClientRect().top;
          return null;
        }"""
        ask = pg.evaluate(top_of, "먼저 정해 주세요")
        if ask is None:
            ask = pg.evaluate(top_of, "결론")
            if ask is None:
                problems.append("맨 위 「먼저 정해 주세요」도 「결론」 한 줄도 없음 — 답할 것이 없으면 그 자리에 결론 한 줄(2.1)")
        if ask is not None and ask > 800:
            problems.append(f"「먼저 정해 주세요」(또는 결론)가 첫 화면 밖(위에서 {int(ask)}px)")
        need_why = pg.evaluate("""() => [...document.querySelectorAll('button.rec')]
          .some(b => !['넣기', '빼기'].includes(b.dataset.v || ''))""")
        if need_why and '추천 이유' not in pg.inner_text('body'):
            problems.append("추천 버튼은 있는데 「추천 이유」 글이 없음 — 추천 아래에 이유 한두 문장")
        many = pg.evaluate("""() => [...document.querySelectorAll('.pick[data-q]')]
          .filter(b => b.querySelectorAll('button.rec').length > 1).map(b => b.dataset.q)""")
        if many:
            problems.append("추천이 둘 이상인 질문: " + ", ".join(many))
        broken = pg.evaluate("""() => [...document.querySelectorAll('a[href^="#"]')]
          .map(a => decodeURIComponent(a.getAttribute('href').slice(1)))
          .filter(id => id && !document.getElementById(id))""")
        if broken:
            problems.append("가리키는 자리가 없는 링크: #" + ", #".join(sorted(set(broken))))
        if "/_pick" in pg.content():
            ok = pg.evaluate("() => fetch('/_pick').then(r => r.status).catch(() => 0)")
            if ok != 200:
                problems.append(f"고른 것 기록이 안 되는 서버(GET /_pick → {ok}) — 새 serve_pages.py로 다시 띄우기")
        pg.screenshot(path=shot)
        b.close()
except Exception as e:
    print(f"점검 도구 못 돎: {e}"); sys.exit(2)
print("\n".join(problems) if problems else "문제 없음")
sys.exit(1 if problems else 0)
