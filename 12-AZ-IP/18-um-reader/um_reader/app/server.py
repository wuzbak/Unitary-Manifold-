# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Static server for the standalone UM Reader / Educator UI."""

from __future__ import annotations

import os
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

PRODUCT_ROOT = Path(__file__).resolve().parents[2]
UI_ROOT = PRODUCT_ROOT / 'ui'
REPO_ROOT = PRODUCT_ROOT.parents[1]


class UMReaderRequestHandler(SimpleHTTPRequestHandler):
    """Serve the standalone UI first, then fall back to repository content."""

    def __init__(self, *args, directory: str | None = None, **kwargs):
        super().__init__(*args, directory=str(UI_ROOT), **kwargs)

    @staticmethod
    def _contained(root: Path, relative: str) -> str | None:
        """Absolute path of ``relative`` under ``root`` if it exists and stays inside ``root``."""
        base = os.path.realpath(root)
        full = os.path.realpath(os.path.join(base, relative))
        if not full.startswith(base + os.sep):
            return None
        return full if os.path.exists(full) else None

    def translate_path(self, path: str) -> str:
        request_path = unquote(urlparse(path).path)
        if request_path in ('', '/'):
            return str(UI_ROOT / 'index.html')
        relative = request_path.lstrip('/')
        for root in (UI_ROOT, REPO_ROOT):
            found = self._contained(root, relative)
            if found is not None:
                return found
        # Not found, or outside both roots: a path that cannot exist yields a plain 404
        # instead of serving whatever ``..`` segments resolved to.
        return str(UI_ROOT / '__not_found__')

    def end_headers(self) -> None:
        self.send_header('Cache-Control', 'no-store, max-age=0')
        super().end_headers()

    def log_message(self, format: str, *args) -> None:
        print(f'UM Reader server — {self.address_string()} — ' + format % args)


def create_server(port: int = 8018) -> ThreadingHTTPServer:
    return ThreadingHTTPServer(('127.0.0.1', port), partial(UMReaderRequestHandler))
