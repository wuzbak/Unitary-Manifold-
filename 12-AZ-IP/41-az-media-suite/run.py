#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""CLI entrypoint for the AZ Media & Feature-Inspection Suite (Product 41)."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from az_media_suite.api import _demo_audio_path, _demo_comic_path, _demo_video_path
from az_media_suite.comic import inspect_comic_archive
from az_media_suite.audio import inspect_audio_file
from az_media_suite.video import inspect_video_container
from az_media_suite.feature_inspection import scan_app_features


def _print(data) -> None:
    print(json.dumps(data, indent=2, default=str))


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    if argv and argv[0] == "serve":
        serve_parser = argparse.ArgumentParser(prog="run.py serve")
        serve_parser.add_argument("--host", default="127.0.0.1")
        serve_parser.add_argument("--port", type=int, default=8141)
        args = serve_parser.parse_args(argv[1:])

        from az_media_suite.app.server import serve

        serve(host=args.host, port=args.port)
        return 0

    if argv and argv[0] == "inspect-features":
        parser = argparse.ArgumentParser(prog="run.py inspect-features")
        parser.add_argument("root", help="Directory of HTML/JS/TS source to scan")
        args = parser.parse_args(argv[1:])
        report = scan_app_features(args.root)
        _print(
            {
                "root": report.root,
                "files_scanned": report.files_scanned,
                "features_present": report.features_present(),
                "findings": [asdict(f) for f in report.findings],
            }
        )
        return 0

    print("Running demo comic / audio / video generation + inspection...")
    _print(asdict(inspect_comic_archive(_demo_comic_path())))
    _print(asdict(inspect_audio_file(_demo_audio_path())))
    _print(asdict(inspect_video_container(_demo_video_path())))
    print("Run `serve` to start the live HTTP product, or `inspect-features <dir>`.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
