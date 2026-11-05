# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Static HTTP server for the AZ UOS/AZ-KERNEL Bridge UI and JSON API."""

from __future__ import annotations

import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from az_uos_kernel_bridge.api import dispatch_api_request
from az_uos_kernel_bridge.ipc_message import decode_kernel_message_json

UI_DIR = Path(__file__).resolve().parents[2] / "ui"

DEFAULT_PORT = 8135
MAX_API_BODY_BYTES = 4096


class BridgeRequestHandler(SimpleHTTPRequestHandler):
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
        if parsed.path != "/api/ipc-message":
            self._send_json(404, {"error": f"unknown API endpoint: {parsed.path}"})
            return
        if self.headers.get_content_type() != "application/json":
            self._send_json(415, {"error": "Content-Type must be application/json"})
            return
        try:
            length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            self._send_json(400, {"error": "valid Content-Length is required"})
            return
        if length < 0:
            self._send_json(400, {"error": "Content-Length must be non-negative"})
            return
        if length > MAX_API_BODY_BYTES:
            self._send_json(413, {"error": "request body exceeds 4096 bytes"})
            return
        try:
            raw = self.rfile.read(length)
            if len(raw) != length:
                raise ValueError("request body ended before Content-Length")
            body = decode_kernel_message_json(raw).to_dict()
            payload = dispatch_api_request(
                parsed.path,
                parse_qs(parsed.query, keep_blank_values=True),
                method="POST",
                body=body,
            )
        except (ValueError, TypeError) as exc:
            self._send_json(400, {"error": str(exc)})
            return
        self._send_json(200, payload)

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def build_server(host: str = "127.0.0.1", port: int = DEFAULT_PORT) -> ThreadingHTTPServer:
    handler = partial(BridgeRequestHandler, directory=str(UI_DIR))
    return ThreadingHTTPServer((host, port), handler)


def serve(host: str = "127.0.0.1", port: int = DEFAULT_PORT) -> None:
    server = build_server(host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
