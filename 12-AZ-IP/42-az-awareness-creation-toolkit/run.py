#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""CLI entrypoint for the AZ Awareness & Creation Toolkit (Product 42)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from az_awareness_creation_toolkit.registry import load_product_registry, route_capability_request
from az_awareness_creation_toolkit.charts import create_bar_chart_svg
from az_awareness_creation_toolkit.cards import create_card_deck, review_card
from az_awareness_creation_toolkit.citations import verify_citation_string
from az_awareness_creation_toolkit.dashboard import build_home_health_snapshot


def _print(data) -> None:
    print(json.dumps(data, indent=2, default=str))


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    if argv and argv[0] == "serve":
        serve_parser = argparse.ArgumentParser(prog="run.py serve")
        serve_parser.add_argument("--host", default="127.0.0.1")
        serve_parser.add_argument("--port", type=int, default=8142)
        args = serve_parser.parse_args(argv[1:])

        from az_awareness_creation_toolkit.app.server import serve

        serve(host=args.host, port=args.port)
        return 0

    if argv and argv[0] == "route":
        parser = argparse.ArgumentParser(prog="run.py route")
        parser.add_argument("intent", help="Free-text intent, e.g. 'comic video audio media'")
        args = parser.parse_args(argv[1:])
        _print(route_capability_request(args.intent))
        return 0

    if argv and argv[0] == "verify-citation":
        parser = argparse.ArgumentParser(prog="run.py verify-citation")
        parser.add_argument("citation", help="e.g. 'src/core/metric.py:1-5'")
        args = parser.parse_args(argv[1:])
        _print([result.as_dict() for result in verify_citation_string(args.citation)])
        return 0

    print("Running demo: product registry + capability router + chart + card deck + dashboard...")
    records = load_product_registry()
    print(f"Product registry: {len(records)} products discovered from 12-AZ-IP/README.md")
    _print(route_capability_request("comic video audio media", limit=3))
    _print({"bar_chart_svg_bytes": len(create_bar_chart_svg(["a", "b", "c"], [1, 2, 3], title="Demo"))})
    deck = create_card_deck([("What is n_w?", "The winding number, n_w = 5.", "UM-core")])
    _print([review_card(card, 4).as_dict() for card in deck])
    _print(build_home_health_snapshot().as_dict())
    print("Run `serve` to start the live HTTP product, `route <intent>`, or `verify-citation <path:line>`.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
