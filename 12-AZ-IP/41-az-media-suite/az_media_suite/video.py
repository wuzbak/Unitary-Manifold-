# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Lightweight video understanding (parsing) and creation.

Full codec-level video (H.264/VP9/...) decode/encode needs ffmpeg or a
similar native toolchain this repository does not bundle or depend on.
Instead, this module defines an honest, self-contained "AZ video
container" (`.azvid`, a zip of `manifest.json` + ordered PNG frames) that
this suite can both parse and create without new native dependencies.

When Pillow is installed (it already is for several other 12-AZ-IP
products, e.g. `12-AZ-IP/13-delphi/app/images/generator.py`), frame width
and height are read directly from each PNG; otherwise those fields are
reported as `None` and every other field (frame count, fps, duration,
per-frame byte sizes) is still returned.
"""

from __future__ import annotations

import json
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:  # pragma: no cover - exercised indirectly via optional-dependency tests
    from PIL import Image

    _PIL_AVAILABLE = True
except ImportError:  # pragma: no cover
    _PIL_AVAILABLE = False

_MANIFEST_NAME = "manifest.json"
_FRAME_SUFFIX = ".png"


@dataclass(frozen=True)
class VideoFrameInfo:
    index: int
    name: str
    size_bytes: int
    width: int | None = None
    height: int | None = None


@dataclass(frozen=True)
class VideoInspection:
    path: str
    fps: float
    frame_count: int
    duration_seconds: float
    frames: list[VideoFrameInfo] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


def _frame_dimensions(data: bytes) -> tuple[int | None, int | None]:
    if not _PIL_AVAILABLE:
        return None, None
    import io

    with Image.open(io.BytesIO(data)) as img:
        return img.width, img.height


def inspect_video_container(path: str | Path) -> VideoInspection:
    """Parse an AZ video container's manifest and ordered frame listing."""
    path = Path(path)
    with zipfile.ZipFile(path) as archive:
        if _MANIFEST_NAME not in archive.namelist():
            raise ValueError(f"{path} is missing {_MANIFEST_NAME}; not an AZ video container")
        manifest = json.loads(archive.read(_MANIFEST_NAME).decode("utf-8"))
        fps = float(manifest.get("fps", 0.0))
        frame_names = list(manifest.get("frames", []))

        frames = []
        for i, name in enumerate(frame_names):
            data = archive.read(name)
            width, height = _frame_dimensions(data)
            frames.append(
                VideoFrameInfo(
                    index=i,
                    name=name,
                    size_bytes=len(data),
                    width=width,
                    height=height,
                )
            )

    duration = (len(frames) / fps) if fps else 0.0
    metadata = {k: v for k, v in manifest.items() if k not in ("fps", "frames")}
    return VideoInspection(
        path=str(path),
        fps=fps,
        frame_count=len(frames),
        duration_seconds=duration,
        frames=frames,
        metadata=metadata,
    )


def create_video_container(
    output_path: str | Path,
    frames: list[bytes],
    fps: float = 24.0,
    metadata: dict[str, Any] | None = None,
) -> VideoInspection:
    """Create an AZ video container from an ordered list of PNG frame bytes."""
    if not frames:
        raise ValueError("at least one frame is required to create a video container")
    if fps <= 0:
        raise ValueError("fps must be positive")

    output_path = Path(output_path)
    frame_names = [f"frame_{i:05d}{_FRAME_SUFFIX}" for i in range(len(frames))]
    manifest: dict[str, Any] = {"fps": fps, "frames": frame_names}
    if metadata:
        manifest.update(metadata)

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(_MANIFEST_NAME, json.dumps(manifest, indent=2))
        for name, data in zip(frame_names, frames):
            archive.writestr(name, data)

    return inspect_video_container(output_path)
