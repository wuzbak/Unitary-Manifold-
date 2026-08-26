# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[2]
UI_ROOT = PRODUCT_ROOT / "ui"


class ImageGeneratorRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory: str | Path | None = None, **kwargs):
        resolved = Path(directory) if directory is not None else UI_ROOT
        super().__init__(*args, directory=str(resolved), **kwargs)


def create_server(port: int = 8017, host: str = "127.0.0.1") -> ThreadingHTTPServer:
    handler = partial(ImageGeneratorRequestHandler, directory=UI_ROOT)
    return ThreadingHTTPServer((host, port), handler)


__all__ = ["PRODUCT_ROOT", "UI_ROOT", "ImageGeneratorRequestHandler", "create_server"]
