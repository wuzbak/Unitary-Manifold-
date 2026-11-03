# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Static HTTP server for the Falsification Observatory UI and API."""

from __future__ import annotations

import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from falsification_observatory.engine.evidence_feed import (
    EvidenceFeedTracker,
    dispatch_evidence_request,
    get_default_tracker,
)
from falsification_observatory.engine.routing import dispatch_api_request

UI_DIR = Path(__file__).resolve().parents[2] / 'ui'
EVIDENCE_PREFIX = '/api/evidence'


class ObservatoryRequestHandler(SimpleHTTPRequestHandler):
    """Serve the standalone Product 19 UI directory and lightweight JSON API."""

    def __init__(self, *args, directory: str | None = None, **kwargs):
        super().__init__(*args, directory=directory or str(UI_DIR), **kwargs)

    def _evidence_tracker(self) -> EvidenceFeedTracker:
        return getattr(self.server, 'evidence_tracker', None) or get_default_tracker()

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, sort_keys=True).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def _handle_evidence(self, method: str, parsed) -> None:
        status, payload = dispatch_evidence_request(
            self._evidence_tracker(), method, parsed.path, parse_qs(parsed.query, keep_blank_values=True)
        )
        self._send_json(status, payload)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlsplit(self.path)
        if parsed.path == EVIDENCE_PREFIX or parsed.path.startswith(EVIDENCE_PREFIX + '/'):
            self._handle_evidence('GET', parsed)
            return
        if parsed.path.startswith('/api/'):
            try:
                payload = dispatch_api_request(parsed.path, parse_qs(parsed.query, keep_blank_values=True))
            except KeyError:
                self.send_error(404, 'Unknown API endpoint')
                return
            self._send_json(200, payload)
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlsplit(self.path)
        if parsed.path == EVIDENCE_PREFIX or parsed.path.startswith(EVIDENCE_PREFIX + '/'):
            self._handle_evidence('POST', parsed)
            return
        self.send_error(405, 'POST is only supported for /api/evidence/refresh')


def make_server(
    host: str = '127.0.0.1', port: int = 8019, tracker: EvidenceFeedTracker | None = None
) -> ThreadingHTTPServer:
    handler = partial(ObservatoryRequestHandler, directory=str(UI_DIR))
    server = ThreadingHTTPServer((host, port), handler)
    server.evidence_tracker = tracker or get_default_tracker()
    return server


def serve(host: str = '127.0.0.1', port: int = 8019, tracker: EvidenceFeedTracker | None = None) -> None:
    server = make_server(host, port, tracker)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
