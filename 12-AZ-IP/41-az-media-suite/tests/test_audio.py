# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_media_suite.audio import (
    create_tone_sequence_wav,
    inspect_audio_file,
    synthesize_tone,
    write_wav,
)


def test_synthesize_tone_sample_count():
    samples = synthesize_tone(440.0, 0.5, framerate=8000)
    assert len(samples) == 8000  # 16-bit samples -> 2 bytes each


def test_synthesize_tone_rejects_bad_input():
    with pytest.raises(ValueError):
        synthesize_tone(0, 1.0)
    with pytest.raises(ValueError):
        synthesize_tone(440.0, 0.0)


def test_write_wav_and_inspect_round_trip(tmp_path):
    path = tmp_path / "tone.wav"
    samples = synthesize_tone(440.0, 0.25, framerate=8000, amplitude=0.8)
    inspection = write_wav(path, samples, framerate=8000)
    assert inspection.channels == 1
    assert inspection.sample_width_bytes == 2
    assert inspection.framerate == 8000
    assert inspection.frame_count == 2000
    assert inspection.duration_seconds == pytest.approx(0.25, rel=1e-6)
    assert 0.0 < inspection.peak_amplitude <= 1.0
    assert 0.0 < inspection.rms_amplitude <= inspection.peak_amplitude + 1e-9


def test_create_tone_sequence_wav(tmp_path):
    path = tmp_path / "sequence.wav"
    inspection = create_tone_sequence_wav(path, notes=[(440.0, 0.1), (523.25, 0.1)], framerate=8000)
    assert inspection.frame_count == 1600
    assert inspection.duration_seconds == pytest.approx(0.2, rel=1e-6)


def test_create_tone_sequence_wav_requires_notes(tmp_path):
    path = tmp_path / "sequence.wav"
    with pytest.raises(ValueError):
        create_tone_sequence_wav(path, notes=[])


def test_inspect_audio_file_matches_wav_header(tmp_path):
    path = tmp_path / "tone.wav"
    create_tone_sequence_wav(path, notes=[(220.0, 0.1)], framerate=16000)
    inspection = inspect_audio_file(path)
    assert inspection.framerate == 16000
    assert inspection.channels == 1
