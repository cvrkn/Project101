#!/usr/bin/env python3
"""VectoStage dev server: static files, no-cache, and a /api/scenes listing.

Usage:  python server.py [port] [--no-open]
Then:   http://localhost:8000/index.html              (HUD on, click Play)
        http://localhost:8000/?scene=my_scene         (loads scenes/my_scene.json)
        http://localhost:8000/?autoplay&clean         (recording mode: no HUD, starts immediately)
"""
import functools
import http.server
import json
import pathlib
import sys
import webbrowser

ROOT = pathlib.Path(__file__).resolve().parent
for d in ("assets/characters", "assets/backgrounds", "assets/vfx", "assets/audio", "scenes", "modules"):
    (ROOT / d).mkdir(parents=True, exist_ok=True)


class Handler(http.server.SimpleHTTPRequestHandler):
    # Windows can map .js to text/plain, which breaks ES modules.
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      ".js": "text/javascript", ".mjs": "text/javascript", ".json": "application/json"}

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):
        if self.path.split("?")[0] == "/api/scenes":
            body = json.dumps(sorted(p.stem for p in (ROOT / "scenes").glob("*.json"))).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            super().do_GET()


if __name__ == "__main__":
    port = int(next((a for a in sys.argv[1:] if a.isdigit()), 8000))
    handler = functools.partial(Handler, directory=str(ROOT))
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as srv:
        url = f"http://localhost:{port}/index.html"
        print(f"VectoStage running at {url}  (Ctrl+C to stop)")
        if "--no-open" not in sys.argv:
            webbrowser.open(url)
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")
