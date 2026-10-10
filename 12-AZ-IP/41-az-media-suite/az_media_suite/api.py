# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""JSON API dispatch for the AZ Media & Feature-Inspection Suite.

Deliberately exposes no arbitrary-filesystem-path parameters: every
endpoint operates on a fixed, product-local `workspace/` directory (created
on first use) or this product's own bundled `ui/` directory. This avoids
path-traversal risk entirely rather than attempting to sanitize untrusted
path input.
"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Mapping

from .audio import create_tone_sequence_wav, inspect_audio_file
from .comic import create_comic_archive, inspect_comic_archive
from .feature_inspection import scan_app_features
from .video import create_video_container, inspect_video_container

API_ENDPOINTS = (
    "/api/status",
    "/api/comic/demo",
    "/api/audio/demo",
    "/api/video/demo",
    "/api/inspect/self",
)

_PRODUCT_ROOT = Path(__file__).resolve().parent.parent
_WORKSPACE_DIR = _PRODUCT_ROOT / "workspace"
_UI_DIR = _PRODUCT_ROOT / "ui"


def _ensure_workspace() -> Path:
    _WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    return _WORKSPACE_DIR


def _demo_comic_path() -> Path:
    workspace = _ensure_workspace()
    path = workspace / "demo.cbz"
    if not path.exists():
        pixel = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0"
            b"\x00\x00\x03\x01\x01\x00\x18\xdd\x8d\xb0\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        create_comic_archive(
            path,
            [("page_0001.png", pixel), ("page_0002.png", pixel)],
            metadata={"Title": "AZ Media Suite Demo Comic", "Writer": "AxiomZero"},
        )
    return path


def _demo_audio_path() -> Path:
    workspace = _ensure_workspace()
    path = workspace / "demo.wav"
    if not path.exists():
        create_tone_sequence_wav(path, notes=[(440.0, 0.1), (523.25, 0.1)])
    return path


def _demo_video_path() -> Path:
    workspace = _ensure_workspace()
    path = workspace / "demo.azvid"
    if not path.exists():
        pixel = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0"
            b"\x00\x00\x03\x01\x01\x00\x18\xdd\x8d\xb0\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        create_video_container(path, frames=[pixel, pixel, pixel], fps=12.0)
    return path


def dispatch_api_request(path: str, query: Mapping[str, List[str]]) -> Dict[str, Any]:
    if path == "/api/status":
        return {
            "product": "AZ Media & Feature-Inspection Suite",
            "endpoints": list(API_ENDPOINTS),
        }

    if path == "/api/comic/demo":
        inspection = inspect_comic_archive(_demo_comic_path())
        return {
            "page_count": inspection.page_count,
            "pages": [asdict(p) for p in inspection.pages],
            "metadata": inspection.metadata,
        }

    if path == "/api/audio/demo":
        inspection = inspect_audio_file(_demo_audio_path())
        return asdict(inspection)

    if path == "/api/video/demo":
        inspection = inspect_video_container(_demo_video_path())
        return {
            "fps": inspection.fps,
            "frame_count": inspection.frame_count,
            "duration_seconds": inspection.duration_seconds,
            "frames": [asdict(f) for f in inspection.frames],
            "metadata": inspection.metadata,
        }

    if path == "/api/inspect/self":
        report = scan_app_features(_UI_DIR)
        return {
            "root": report.root,
            "files_scanned": report.files_scanned,
            "features_present": report.features_present(),
            "findings": [asdict(f) for f in report.findings],
        }

    raise KeyError(f"unknown API endpoint: {path}")
