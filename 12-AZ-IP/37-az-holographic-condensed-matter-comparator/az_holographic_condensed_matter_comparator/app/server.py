# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Static HTTP server for the AZ Holographic Condensed-Matter Comparator UI and JSON API."""

from __future__ import annotations

import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from az_holographic_condensed_matter_comparator.api import (
    dispatch_api_request, dispatch_reference_comparison,
)

UI_DIR = Path(__file__).resolve().parents[2] / "ui"

DEFAULT_PORT = 8137
MAX_REQUEST_BYTES = 262144


class ComparatorRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory: str | None = None, **kwargs):
        super().__init__(*args, directory=directory or str(UI_DIR), **kwargs)

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        pass

    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, sort_keys=True, allow_nan=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802
        if urlsplit(self.path).path != "/api/compare-references":
            self._send_json({"error": "unknown POST endpoint"}, 404)
            return
        if self.headers.get("Content-Type", "").split(";")[0].strip().lower() != "application/json":
            self._send_json({"error": "Content-Type must be application/json"}, 415)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 1 <= length <= MAX_REQUEST_BYTES:
                self._send_json({"error": f"body must be 1..{MAX_REQUEST_BYTES} bytes"}, 413)
                return
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            report = dispatch_reference_comparison(payload)
        except (ValueError, TypeError, UnicodeError) as exc:
            self._send_json({"error": str(exc)}, 400)
            return
        self._send_json(report)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlsplit(self.path)
        if parsed.path.startswith("/api/"):
            try:
                payload = dispatch_api_request(parsed.path, parse_qs(parsed.query, keep_blank_values=True))
                status = 200
            except KeyError as exc:
                payload = {"error": str(exc)}
                status = 404
            except (ValueError, TypeError, IndexError) as exc:
                payload = {"error": str(exc)}
                status = 400
            self._send_json(payload, status)
            return
        super().do_GET()


def build_server(host: str = "127.0.0.1", port: int = DEFAULT_PORT) -> ThreadingHTTPServer:
    handler = partial(ComparatorRequestHandler, directory=str(UI_DIR))
    return ThreadingHTTPServer((host, port), handler)


def serve(host: str = "127.0.0.1", port: int = DEFAULT_PORT) -> None:
    server = build_server(host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
