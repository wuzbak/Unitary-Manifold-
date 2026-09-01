# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Static HTTP server for the Falsification Observatory UI and API."""

from __future__ import annotations

import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from falsification_observatory.engine.routing import dispatch_api_request

UI_DIR = Path(__file__).resolve().parents[2] / 'ui'


class ObservatoryRequestHandler(SimpleHTTPRequestHandler):
    """Serve the standalone Product 19 UI directory and lightweight JSON API."""

    def __init__(self, *args, directory: str | None = None, **kwargs):
        super().__init__(*args, directory=directory or str(UI_DIR), **kwargs)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlsplit(self.path)
        if parsed.path.startswith('/api/'):
            try:
                payload = dispatch_api_request(parsed.path, parse_qs(parsed.query, keep_blank_values=True))
            except KeyError:
                self.send_error(404, 'Unknown API endpoint')
                return
            body = json.dumps(payload, sort_keys=True).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()


def serve(host: str = '127.0.0.1', port: int = 8019) -> None:
    handler = partial(ObservatoryRequestHandler, directory=str(UI_DIR))
    server = ThreadingHTTPServer((host, port), handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
