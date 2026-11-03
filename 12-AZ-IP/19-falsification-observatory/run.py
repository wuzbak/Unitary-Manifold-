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
from falsification_observatory.engine.evidence_feed import DEFAULT_MAX_AGE_SECONDS, EvidenceFeedTracker


def main() -> None:
    parser = argparse.ArgumentParser(description='Serve the Falsification Observatory web app.')
    parser.add_argument('--port', type=int, default=8019, help='Port for the local server (default: 8019).')
    parser.add_argument('--host', default='127.0.0.1', help='Host interface to bind (default: 127.0.0.1).')
    parser.add_argument('--no-open', action='store_true', help='Do not open the browser automatically.')
    parser.add_argument(
        '--evidence-state',
        default=None,
        help='Optional JSON file for persisting arXiv evidence-feed tracking between runs (default: in-memory only).',
    )
    parser.add_argument(
        '--evidence-max-age-hours',
        type=float,
        default=DEFAULT_MAX_AGE_SECONDS / 3600,
        help='Hours after which a successfully fetched evidence feed is reported as stale (default: 24).',
    )
    args = parser.parse_args()
    tracker = EvidenceFeedTracker(state_path=args.evidence_state, max_age_seconds=args.evidence_max_age_hours * 3600)

    url = f'http://{args.host}:{args.port}/'
    if not args.no_open:
        try:
            webbrowser.open(url)
        except (webbrowser.Error, OSError) as exc:
            print(f'Could not open a browser automatically: {exc}', file=sys.stderr)

    print(f'Falsification Observatory serving at {url}')
    serve(host=args.host, port=args.port, tracker=tracker)


if __name__ == '__main__':
    main()
