# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
#!/usr/bin/env python3
"""Launch the Falsification Observatory static app."""

from __future__ import annotations

import argparse
import os
import sys
import webbrowser

sys.path.insert(0, os.path.dirname(__file__))

from falsification_observatory.app.server import serve


def main() -> None:
    parser = argparse.ArgumentParser(description='Serve the Falsification Observatory web app.')
    parser.add_argument('--port', type=int, default=8019, help='Port for the local server (default: 8019).')
    parser.add_argument('--host', default='127.0.0.1', help='Host interface to bind (default: 127.0.0.1).')
    parser.add_argument('--no-open', action='store_true', help='Do not open the browser automatically.')
    args = parser.parse_args()

    url = f'http://{args.host}:{args.port}/'
    if not args.no_open:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    print(f'Falsification Observatory serving at {url}')
    serve(host=args.host, port=args.port)


if __name__ == '__main__':
    main()
