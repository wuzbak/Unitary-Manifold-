# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Static file server for the standalone UI."""

from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class UIRequestHandler(SimpleHTTPRequestHandler):
    """Serve files from the product's ui/ directory."""



def ui_directory() -> Path:
    """Return the absolute path to the bundled UI directory."""
    return Path(__file__).resolve().parents[2] / "ui"



def serve_ui(port: int = 8021) -> None:
    """Serve the UI until interrupted."""
    directory = str(ui_directory())
    handler = partial(UIRequestHandler, directory=directory)
    with ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        print(f"Serving UM Geophysical Monitor at http://127.0.0.1:{port}")
        print(f"UI root: {directory}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down server.")
