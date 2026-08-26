# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Static HTTP server for the Falsification Observatory UI."""

from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

UI_DIR = Path(__file__).resolve().parents[2] / 'ui'


class ObservatoryRequestHandler(SimpleHTTPRequestHandler):
    """Serve the standalone Product 19 UI directory."""

    def __init__(self, *args, directory: str | None = None, **kwargs):
        super().__init__(*args, directory=directory or str(UI_DIR), **kwargs)


def serve(host: str = '127.0.0.1', port: int = 8019) -> None:
    handler = partial(ObservatoryRequestHandler, directory=str(UI_DIR))
    server = ThreadingHTTPServer((host, port), handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
