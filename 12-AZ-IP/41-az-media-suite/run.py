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
from az_media_suite.audio import create_tone_sequence_wav, inspect_audio_file
from az_media_suite.video import inspect_video_container
from az_media_suite.feature_inspection import scan_app_features


def _print(data) -> None:
    print(json.dumps(data, indent=2, default=str))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AZ Media & Feature-Inspection Suite")
    subparsers = parser.add_subparsers(dest="command")
    serve_parser = subparsers.add_parser("serve", help="run the local web application")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8141)
    feature_parser = subparsers.add_parser("inspect-features", help="scan local source for feature evidence")
    feature_parser.add_argument("root", help="Directory of HTML/JS/TS source to scan")
    media_parser = subparsers.add_parser("inspect-media", help="inspect a local .cbz, .wav, or .azvid file")
    media_parser.add_argument("path", type=Path)
    tone_parser = subparsers.add_parser("create-tone", help="create a PCM16 WAV tone sequence")
    tone_parser.add_argument("output", type=Path)
    tone_parser.add_argument("--frequency", type=float, required=True, help="tone frequency in Hz")
    tone_parser.add_argument("--duration", type=float, required=True, help="tone duration in seconds")
    tone_parser.add_argument("--sample-rate", type=int, default=44100)
    tone_parser.add_argument("--amplitude", type=float, default=0.5)
    args = parser.parse_args(argv)

    if args.command == "serve":
        from az_media_suite.app.server import serve

        serve(host=args.host, port=args.port)
        return 0

    if args.command == "inspect-features":
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

    if args.command == "inspect-media":
        inspectors = {
            ".cbz": inspect_comic_archive,
            ".wav": inspect_audio_file,
            ".azvid": inspect_video_container,
        }
        inspector = inspectors.get(args.path.suffix.lower())
        if inspector is None:
            parser.error("inspect-media supports .cbz, .wav, and .azvid files")
        try:
            _print(asdict(inspector(args.path)))
        except (OSError, ValueError, IndexError) as exc:
            parser.error(str(exc))
        return 0

    if args.command == "create-tone":
        try:
            result = create_tone_sequence_wav(
                args.output,
                notes=[(args.frequency, args.duration)],
                framerate=args.sample_rate,
                amplitude=args.amplitude,
            )
        except (OSError, ValueError, OverflowError) as exc:
            parser.error(str(exc))
        _print(asdict(result))
        return 0

    print("Running demo comic / audio / video generation + inspection...")
    _print(asdict(inspect_comic_archive(_demo_comic_path())))
    _print(asdict(inspect_audio_file(_demo_audio_path())))
    _print(asdict(inspect_video_container(_demo_video_path())))
    print("Run `serve` to start the live HTTP product, or `inspect-features <dir>`.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
