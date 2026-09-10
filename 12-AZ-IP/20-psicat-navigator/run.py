# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Launch the standalone PsiCat Product 20 local server."""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from ox_navigator.app.server import serve


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Serve the standalone PsiCat Product 20 web app.')
    parser.add_argument('--port', type=int, default=8020, help='Port to bind the local server to.')
    parser.add_argument('--host', default='127.0.0.1', help='Host interface to bind.')
    parser.add_argument('--no-open', action='store_true', help='Accepted for parity; browser auto-open is disabled.')
    parser.add_argument(
        '--local-execution',
        choices=('on', 'off'),
        default='on',
        help='Enable or disable the protected local execution loop.',
    )
    parser.add_argument(
        '--local-execution-timeout',
        type=int,
        default=120,
        help='Max timeout (seconds) for /api/psicat/local-execution/run.',
    )
    parser.add_argument(
        '--local-execution-allowlist',
        default='',
        help='Optional comma-separated executable allowlist override for local execution.',
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    os.environ['MERLIN_LOCAL_EXECUTION_ENABLED'] = '1' if args.local_execution == 'on' else '0'
    os.environ['MERLIN_LOCAL_EXECUTION_MAX_TIMEOUT'] = str(max(5, args.local_execution_timeout))
    if str(args.local_execution_allowlist).strip():
        os.environ['MERLIN_LOCAL_EXECUTION_ALLOWED_COMMANDS'] = str(args.local_execution_allowlist).strip()
    print('PsiCat — Quantum Cat Interface (Product 20)')
    print(f'Local URL: http://{args.host}:{args.port}/ox-navigator.html')
    print('Included tools: /interrogator.html and /flashcard-trainer.html')
    print('Local execution loop endpoints: GET /api/psicat/local-execution/status, POST /api/psicat/local-execution/run')
    print('Set OPENROUTER_API_KEY before using live PsiCat queries against OpenRouter.')
    print('Example: export OPENROUTER_API_KEY=your_key_here')
    if not os.environ.get('OPENROUTER_API_KEY'):
        print('WARNING: OPENROUTER_API_KEY is not set. PsiCat will fall back to offline RAG responses.')
    httpd = serve(host=args.host, port=args.port, no_open=args.no_open)
    print('Serving static UI plus /api/psicat and hidden agent backend endpoints. Press Ctrl+C to stop.')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Shutting down PsiCat...')
    finally:
        httpd.server_close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
