"""Local workspace backend. POST /api/draw → draw_yaml. Not required on GitHub Pages."""

from __future__ import annotations

import argparse
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from circuit.service import draw_yaml, explain_yaml

WEB = Path(__file__).resolve().parents[2] / "web"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB), **kwargs)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/draw":
            self.send_error(404)
            return
        n = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(n)
        try:
            payload = json.loads(raw.decode())
            text = payload.get("yaml") or ""
            out = draw_yaml(text)
            try:
                out["explain"] = json.dumps(explain_yaml(text), indent=2)
            except Exception:
                out["explain"] = ""
            # bytes values in pack_files are not JSON
            if "pack_files" in out:
                out["pack_files"] = {
                    k: ("<bytes>" if isinstance(v, (bytes, bytearray)) else v)
                    for k, v in (out["pack_files"] or {}).items()
                }
            body = json.dumps(out).encode()
        except Exception as exc:
            body = json.dumps({"ok": False, "sentence": str(exc), "sheets": {}}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        pass


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=8088)
    p.add_argument("--host", default="127.0.0.1")
    args = p.parse_args(argv)
    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"workspace http://{args.host}:{args.port}/", flush=True)
    httpd.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
