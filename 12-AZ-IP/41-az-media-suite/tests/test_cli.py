# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""CLI integration tests using actual input and generated WAV files."""

import json
import subprocess
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]


def _run(*args):
    return subprocess.run(
        [sys.executable, str(PRODUCT_ROOT / "run.py"), *map(str, args)],
        cwd=PRODUCT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_cli_creates_then_inspects_a_user_path_wav(tmp_path):
    audio_path = tmp_path / "tone.wav"
    created = _run("create-tone", audio_path, "--frequency", "440", "--duration", "0.1")
    assert created.returncode == 0, created.stderr
    assert audio_path.is_file()
    creation_report = json.loads(created.stdout)
    assert creation_report["frame_count"] == 4410
    assert creation_report["peak_amplitude"] > 0

    inspected = _run("inspect-media", audio_path)
    assert inspected.returncode == 0, inspected.stderr
    report = json.loads(inspected.stdout)
    assert report["framerate"] == 44100
    assert report["duration_seconds"] == 0.1
    assert report["rms_amplitude"] > 0


def test_cli_rejects_unsupported_media_suffix(tmp_path):
    result = _run("inspect-media", tmp_path / "input.mp3")
    assert result.returncode == 2
    assert "supports .cbz, .wav, and .azvid" in result.stderr
