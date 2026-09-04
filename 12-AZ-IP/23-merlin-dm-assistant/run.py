# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Launch the Merlin DM Guide & Player Assistant local API."""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from merlin_dnd.server import serve


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Serve the Merlin D&D assistant product.")
    parser.add_argument("mode", nargs="?", default="serve", choices=["serve", "demo"])
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8033)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.mode == "demo":
        demo = {
            "service": "merlin-dm-assistant",
            "url": f"http://{args.host}:{args.port}/api/health",
            "features": [
                "separate DM and player dashboards",
                "invite-code campaign joins",
                "character import and player sync",
                "xp, treasure, gold, and inventory tracking",
                "map, npc, monster, and image interaction",
                "Merlin table assistant",
            ],
        }
        print(json.dumps(demo, indent=2))
        return 0

    print("Merlin DM Guide & Player Assistant (Product 23)")
    print(f"Local UI: http://{args.host}:{args.port}/")
    print(f"Local API: http://{args.host}:{args.port}/api/health")
    httpd = serve(host=args.host, port=args.port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
