# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
#!/usr/bin/env python3
"""Launch the PsiCat Braided Brain static app."""

from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import webbrowser

PRODUCT_ROOT = Path(__file__).resolve().parent


def serve(host: str = '127.0.0.1', port: int = 8025) -> None:
    handler = partial(SimpleHTTPRequestHandler, directory=str(PRODUCT_ROOT))
    with ThreadingHTTPServer((host, port), handler) as server:
        print(f'PsiCat Braided Brain serving at http://{host}:{port}/ui/index.html')
        server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description='Serve the PsiCat Braided Brain web app.')
    parser.add_argument('--host', default='127.0.0.1', help='Host interface to bind (default: 127.0.0.1).')
    parser.add_argument('--port', type=int, default=8025, help='Port for the local server (default: 8025).')
    parser.add_argument('--no-open', action='store_true', help='Do not open the browser automatically.')
    args = parser.parse_args()
    url = f'http://{args.host}:{args.port}/ui/index.html'
    if not args.no_open:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    serve(host=args.host, port=args.port)


if __name__ == '__main__':
    main()
