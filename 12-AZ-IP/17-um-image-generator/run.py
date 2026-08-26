# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
from __future__ import annotations

import argparse
import sys
import webbrowser
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parent
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from image_generator.app.server import UI_ROOT, create_server


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Serve the UM Physics Image Generator as a local static web app.",
    )
    parser.add_argument("--port", type=int, default=8017, help="Port to bind (default: 8017).")
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not automatically open a browser window.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    with create_server(port=args.port) as server:
        host, port = server.server_address
        url = f"http://{host}:{port}/"
        print("UM Physics Image Generator")
        print(f"Serving standalone UI from: {UI_ROOT}")
        print(f"Open in browser: {url}")
        print("Press Ctrl+C to stop the server.")
        if not args.no_open:
            webbrowser.open(url, new=2)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
