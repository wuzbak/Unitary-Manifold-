# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Static HTTP server for the AZ Awareness & Creation Toolkit UI and JSON API."""

from __future__ import annotations

import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from az_awareness_creation_toolkit.api import dispatch_api_request

UI_DIR = Path(__file__).resolve().parents[2] / "ui"

DEFAULT_PORT = 8142
MAX_POST_BYTES = 1024 * 1024


class ToolkitRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory: str | None = None, **kwargs):
        super().__init__(*args, directory=directory or str(UI_DIR), **kwargs)

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        pass

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlsplit(self.path)
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
            self._send_json(status, payload)
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlsplit(self.path)
        if parsed.path not in {"/api/cards/deck", "/api/cards/review"}:
            self._send_json(405, {"error": "POST is only supported for card creation and review"})
            return
        try:
            if parsed.query:
                raise ValueError("card operations accept a JSON body, not query parameters")
            if self.headers.get_content_type() != "application/json":
                raise ValueError("Content-Type must be application/json")
            length = int(self.headers.get("Content-Length", ""))
            if not 0 < length <= MAX_POST_BYTES:
                raise ValueError(f"request body must be 1..{MAX_POST_BYTES} bytes")
            raw_body = self.rfile.read(length)
            if len(raw_body) != length:
                raise ValueError("request body ended before Content-Length")
            payload = json.loads(raw_body.decode("utf-8"))
            result = dispatch_api_request(parsed.path, {}, payload)
            status = 200
        except (ValueError, TypeError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            result = {"error": str(exc)}
            status = 400
        self._send_json(status, result)

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, sort_keys=True, allow_nan=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def build_server(host: str = "127.0.0.1", port: int = DEFAULT_PORT) -> ThreadingHTTPServer:
    handler = partial(ToolkitRequestHandler, directory=str(UI_DIR))
    return ThreadingHTTPServer((host, port), handler)


def serve(host: str = "127.0.0.1", port: int = DEFAULT_PORT) -> None:
    server = build_server(host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
