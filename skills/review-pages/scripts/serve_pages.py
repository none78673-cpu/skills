"""정적 파일 서버 + HTTP Range(오디오·영상 재생 위치 이동) + 고른 것 기록.
python -I serve_pages.py <폴더> <포트>

고른 것 기록: 페이지가 POST /_pick 에 JSON({"page","round","q","choice","note"})을 보내면
그 페이지가 있는 폴더의 _picks.jsonl 에 한 줄씩 덧붙인다(time은 서버가 채움).
GET /_pick 은 200 {"pick":1} — 이 서버가 기록을 받는 판인지 확인용(옛 판은 404).
같은 컴퓨터의 127.0.0.1 페이지에서 온 요청만 받는다(다른 사이트가 몰래 보내는 것 막기).
Host가 127.0.0.1·localhost가 아닌 요청은 모두 403 — 악성 사이트가 DNS rebinding으로 이 폴더 파일을 읽어 가는 것 막기.
"""
import json, os, re, sys, time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

class H(SimpleHTTPRequestHandler):
    def parse_request(self):
        if not super().parse_request():
            return False
        h = self.headers.get("Host") or ""
        host = h.split("]")[0] + "]" if h.startswith("[") else h.rsplit(":", 1)[0]
        if host not in ("127.0.0.1", "localhost", "[::1]"):
            self.send_error(403, "Host not allowed")
            return False
        return True

    def do_GET(self):
        if urlparse(self.path).path == "/_pick":
            body = b'{"pick":1}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers(); self.wfile.write(body); return
        super().do_GET()

    def do_POST(self):
        if urlparse(self.path).path != "/_pick":
            self.send_error(404); return
        origin = self.headers.get("Origin") or ""
        if origin and not re.match(r"^https?://(127\.0\.0\.1|localhost)(:\d+)?$", origin):
            self.send_error(403); return
        try:
            n = int(self.headers.get("Content-Length") or 0)
            if n > 100_000:
                self.send_error(413); return
            data = json.loads(self.rfile.read(n) or b"{}")
            page = str(data.get("page") or unquote(urlparse(self.headers.get("Referer") or "").path)).lstrip("/")
            data["page"] = page
            data["time"] = time.strftime("%Y-%m-%d %H:%M:%S")
            folder = os.path.dirname(self.translate_path("/" + page)) if page else self.directory
            with open(os.path.join(folder, "_picks.jsonl"), "a", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
        except (ValueError, OSError) as e:
            self.send_error(400, str(e)); return
        self.send_response(204); self.end_headers()

    def send_head(self):
        path = self.translate_path(self.path)
        rng = self.headers.get("Range")
        if os.path.isdir(path) or not rng or not os.path.isfile(path):
            return super().send_head()
        m = re.match(r"bytes=(\d*)-(\d*)", rng)
        size = os.path.getsize(path)
        if m and not m.group(1) and m.group(2):  # bytes=-N: 마지막 N바이트
            start, end = max(0, size - int(m.group(2))), size - 1
        else:
            start = int(m.group(1)) if m and m.group(1) else 0
            end = int(m.group(2)) if m and m.group(2) else size - 1
        end = min(end, size - 1)
        if start > end:
            self.send_error(416); return None
        f = open(path, "rb"); f.seek(start)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Accept-Ranges", "bytes")
        self.end_headers()
        self._remaining = end - start + 1
        return f
    def copyfile(self, src, dst):
        n = getattr(self, "_remaining", None)
        if n is None:
            return super().copyfile(src, dst)
        while n > 0:
            b = src.read(min(65536, n))
            if not b: break
            dst.write(b); n -= len(b)
        self._remaining = None
    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
        super().end_headers()

root, port = sys.argv[1], int(sys.argv[2])
ThreadingHTTPServer(("127.0.0.1", port), partial(H, directory=root)).serve_forever()
