# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
#!/usr/bin/env python3
"""Launch the standalone UM Reader / Educator as a local static web app."""

from __future__ import annotations

import argparse
import sys
import threading
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from um_reader.app.server import create_server
from um_reader.engine.constants import DEFAULT_PORT


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the standalone UM Reader / Educator server.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to bind (default: 8018).")
    parser.add_argument("--no-open", action="store_true", help="Do not open the default browser automatically.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    server = create_server(args.port)
    url = f"http://127.0.0.1:{args.port}/"

    print("UM Reader / Educator")
    print(f"Serving standalone UI from: {ROOT / 'ui'}")
    print(f"Open in browser: {url}")
    print("Press Ctrl+C to stop the local server.")

    if not args.no_open:
        threading.Timer(0.75, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down UM Reader server...")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
