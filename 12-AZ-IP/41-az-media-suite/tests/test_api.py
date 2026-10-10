# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
import shutil
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_media_suite import api


@pytest.fixture(autouse=True)
def _clean_workspace():
    workspace = PRODUCT_ROOT / "workspace"
    if workspace.exists():
        shutil.rmtree(workspace)
    yield
    if workspace.exists():
        shutil.rmtree(workspace)


def test_status_endpoint():
    result = api.dispatch_api_request("/api/status", {})
    assert result["product"] == "AZ Media & Feature-Inspection Suite"
    assert "/api/comic/demo" in result["endpoints"]


def test_comic_demo_endpoint_creates_workspace_archive():
    result = api.dispatch_api_request("/api/comic/demo", {})
    assert result["page_count"] == 2
    assert result["metadata"]["Title"] == "AZ Media Suite Demo Comic"
    assert (PRODUCT_ROOT / "workspace" / "demo.cbz").exists()


def test_audio_demo_endpoint_creates_workspace_wav():
    result = api.dispatch_api_request("/api/audio/demo", {})
    assert result["channels"] == 1
    assert result["framerate"] > 0
    assert (PRODUCT_ROOT / "workspace" / "demo.wav").exists()


def test_video_demo_endpoint_creates_workspace_container():
    result = api.dispatch_api_request("/api/video/demo", {})
    assert result["frame_count"] == 3
    assert result["fps"] == 12.0
    assert (PRODUCT_ROOT / "workspace" / "demo.azvid").exists()


def test_inspect_self_endpoint_scans_ui_dir():
    result = api.dispatch_api_request("/api/inspect/self", {})
    assert result["root"].endswith("ui")
    assert "fetch_network_call" in result["features_present"]


def test_dispatch_unknown_endpoint_raises_key_error():
    with pytest.raises(KeyError):
        api.dispatch_api_request("/api/unknown", {})
