# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Launch the standalone OX Navigator local server."""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from ox_navigator.app.server import serve


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Serve the standalone OX Navigator web app.')
    parser.add_argument('--port', type=int, default=8020, help='Port to bind the local server to.')
    parser.add_argument('--host', default='127.0.0.1', help='Host interface to bind.')
    parser.add_argument('--no-open', action='store_true', help='Accepted for parity; browser auto-open is disabled.')
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    print('OX Navigator (Product 20)')
    print(f'Local URL: http://{args.host}:{args.port}/ox-navigator.html')
    print('Included tools: /interrogator.html and /flashcard-trainer.html')
    print('Set OPENROUTER_API_KEY before using live OX queries against OpenRouter.')
    print('Example: export OPENROUTER_API_KEY=your_key_here')
    if not os.environ.get('OPENROUTER_API_KEY'):
        print('WARNING: OPENROUTER_API_KEY is not set. /api/ox will return a configuration error.')
    httpd = serve(host=args.host, port=args.port, no_open=args.no_open)
    print('Serving static UI and local /api/ox endpoints. Press Ctrl+C to stop.')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Shutting down OX Navigator...')
    finally:
        httpd.server_close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
