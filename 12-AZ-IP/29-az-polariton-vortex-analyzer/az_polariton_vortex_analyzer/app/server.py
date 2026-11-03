# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Static HTTP server for the AZ Polariton Vortex Analyzer UI and JSON API."""

from __future__ import annotations

import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from az_polariton_vortex_analyzer.api import dispatch_api_request
from az_polariton_vortex_analyzer.measurement import MAX_INPUT_BYTES

UI_DIR = Path(__file__).resolve().parents[2] / "ui"

DEFAULT_PORT = 8129


class AnalyzerRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory: str | None = None, **kwargs):
        super().__init__(*args, directory=directory or str(UI_DIR), **kwargs)

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        pass

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlsplit(self.path)
        if parsed.path == "/api/analyze":
            self._json_response(405, {"error": "measurement analysis requires POST"}, allow="POST")
            return
        if parsed.path.startswith("/api/"):
            try:
                payload = dispatch_api_request(parsed.path, parse_qs(parsed.query, keep_blank_values=True))
                status = 200
            except KeyError as exc:
                payload = {"error": str(exc)}
                status = 404
            except (ValueError, TypeError) as exc:
                payload = {"error": str(exc)}
                status = 400
            self._json_response(status, payload)
            return
        super().do_GET()

    def _json_response(self, status: int, payload: dict, *, allow: str | None = None) -> None:
        body = json.dumps(payload, sort_keys=True, allow_nan=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        if allow:
            self.send_header("Allow", allow)
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlsplit(self.path)
        if parsed.path != "/api/analyze":
            status = 405 if parsed.path in {"/api/status", "/api/prediction", "/api/demo-comparison"} else 404
            self._json_response(
                status, {"error": "POST supported only for /api/analyze"},
                allow="GET" if status == 405 else None,
            )
            return
        if self.headers.get("Transfer-Encoding"):
            self._json_response(400, {"error": "Transfer-Encoding is unsupported; supply Content-Length"})
            return
        if self.headers.get_content_type() != "application/json":
            self._json_response(415, {"error": "Content-Type must be application/json"})
            return
        lengths = self.headers.get_all("Content-Length", [])
        if len(lengths) != 1 or not lengths[0].isascii() or not lengths[0].isdigit():
            self._json_response(400, {"error": "one numeric Content-Length is required"})
            return
        if len(lengths[0]) > 10:
            self._json_response(413, {"error": "Content-Length exceeds the input limit"})
            return
        length = int(lengths[0])
        if not 0 < length <= MAX_INPUT_BYTES:
            self._json_response(413, {"error": f"body must contain 1..{MAX_INPUT_BYTES} bytes"})
            return
        self.connection.settimeout(10)
        try:
            body = self.rfile.read(length)
            if len(body) != length:
                raise ValueError("incomplete request body")
            payload = dispatch_api_request(
                parsed.path,
                parse_qs(parsed.query, keep_blank_values=True),
                method="POST",
                body=body,
            )
        except (ValueError, TypeError, TimeoutError) as exc:
            self._json_response(400, {"error": str(exc)})
            return
        self._json_response(200, payload)


def build_server(host: str = "127.0.0.1", port: int = DEFAULT_PORT) -> ThreadingHTTPServer:
    handler = partial(AnalyzerRequestHandler, directory=str(UI_DIR))
    return ThreadingHTTPServer((host, port), handler)


def serve(host: str = "127.0.0.1", port: int = DEFAULT_PORT) -> None:
    server = build_server(host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
