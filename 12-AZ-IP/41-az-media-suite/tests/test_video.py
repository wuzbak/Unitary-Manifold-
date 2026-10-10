# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_media_suite.video import create_video_container, inspect_video_container

_PIXEL_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0"
    b"\x00\x00\x03\x01\x01\x00\x18\xdd\x8d\xb0\x00\x00\x00\x00IEND\xaeB`\x82"
)


def test_create_and_inspect_video_container(tmp_path):
    path = tmp_path / "clip.azvid"
    inspection = create_video_container(path, frames=[_PIXEL_PNG, _PIXEL_PNG, _PIXEL_PNG], fps=12.0)
    assert inspection.fps == 12.0
    assert inspection.frame_count == 3
    assert inspection.duration_seconds == pytest.approx(0.25, rel=1e-6)
    assert [f.name for f in inspection.frames] == ["frame_00000.png", "frame_00001.png", "frame_00002.png"]


def test_inspect_video_container_round_trip_with_metadata(tmp_path):
    path = tmp_path / "clip.azvid"
    create_video_container(path, frames=[_PIXEL_PNG], fps=24.0, metadata={"title": "Demo clip"})
    inspection = inspect_video_container(path)
    assert inspection.metadata.get("title") == "Demo clip"
    assert inspection.frames[0].size_bytes == len(_PIXEL_PNG)


def test_create_video_container_requires_frames(tmp_path):
    path = tmp_path / "clip.azvid"
    with pytest.raises(ValueError):
        create_video_container(path, frames=[], fps=24.0)


def test_create_video_container_requires_positive_fps(tmp_path):
    path = tmp_path / "clip.azvid"
    with pytest.raises(ValueError):
        create_video_container(path, frames=[_PIXEL_PNG], fps=0)


def test_inspect_video_container_rejects_missing_manifest(tmp_path):
    import zipfile

    path = tmp_path / "clip.azvid"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("not_a_manifest.txt", "hello")
    with pytest.raises(ValueError):
        inspect_video_container(path)
