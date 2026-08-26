# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Static server for the standalone UM Reader / Educator UI."""

from __future__ import annotations

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
    def _is_within(candidate: Path, root: Path) -> bool:
        try:
            candidate.resolve().relative_to(root.resolve())
            return True
        except ValueError:
            return False

    def translate_path(self, path: str) -> str:
        request_path = unquote(urlparse(path).path)
        if request_path in ('', '/'):
            return str(UI_ROOT / 'index.html')
        relative = Path(request_path.lstrip('/'))
        ui_candidate = (UI_ROOT / relative).resolve()
        if self._is_within(ui_candidate, UI_ROOT) and ui_candidate.exists():
            return str(ui_candidate)
        repo_candidate = (REPO_ROOT / relative).resolve()
        if self._is_within(repo_candidate, REPO_ROOT) and repo_candidate.exists():
            return str(repo_candidate)
        return str(ui_candidate)

    def end_headers(self) -> None:
        self.send_header('Cache-Control', 'no-store, max-age=0')
        super().end_headers()

    def log_message(self, format: str, *args) -> None:
        print(f'UM Reader server — {self.address_string()} — ' + format % args)


def create_server(port: int = 8018) -> ThreadingHTTPServer:
    return ThreadingHTTPServer(('127.0.0.1', port), partial(UMReaderRequestHandler))
