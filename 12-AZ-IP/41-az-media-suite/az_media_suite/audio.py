# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Audio understanding (parsing) and creation — stdlib-only (`wave`/`struct`).

"Understanding" here is deliberately narrow and honest: container metadata
(channels, sample rate, duration) plus simple, well-defined signal
statistics (peak amplitude, RMS loudness). It is not speech recognition,
music transcription, or a general audio-classification model.

"Creation" covers deterministic tone/tone-sequence synthesis to PCM16 WAV,
useful for notification sounds, test fixtures, and simple sonification of
other UM/PsiCat data.
"""

from __future__ import annotations

import math
import struct
import wave
from dataclasses import dataclass
from pathlib import Path

_PCM16_MAX = 32767


@dataclass(frozen=True)
class AudioInspection:
    path: str
    channels: int
    sample_width_bytes: int
    framerate: int
    frame_count: int
    duration_seconds: float
    peak_amplitude: float
    rms_amplitude: float


def _read_pcm16_samples(raw: bytes) -> list[int]:
    count = len(raw) // 2
    return list(struct.unpack(f"<{count}h", raw[: count * 2]))


def inspect_audio_file(path: str | Path) -> AudioInspection:
    """Parse a WAV file's container metadata and simple signal statistics."""
    path = Path(path)
    with wave.open(str(path), "rb") as handle:
        channels = handle.getnchannels()
        sample_width = handle.getsampwidth()
        framerate = handle.getframerate()
        frame_count = handle.getnframes()
        raw = handle.readframes(frame_count)

    duration = frame_count / framerate if framerate else 0.0
    peak = 0.0
    rms = 0.0
    if sample_width == 2 and raw:
        samples = _read_pcm16_samples(raw)
        if samples:
            peak = max(abs(s) for s in samples) / _PCM16_MAX
            rms = math.sqrt(sum(s * s for s in samples) / len(samples)) / _PCM16_MAX

    return AudioInspection(
        path=str(path),
        channels=channels,
        sample_width_bytes=sample_width,
        framerate=framerate,
        frame_count=frame_count,
        duration_seconds=duration,
        peak_amplitude=peak,
        rms_amplitude=rms,
    )


def synthesize_tone(
    frequency_hz: float,
    duration_seconds: float,
    framerate: int = 44100,
    amplitude: float = 0.5,
) -> bytes:
    """Return PCM16 mono samples for a sine tone (not yet wrapped in a WAV header)."""
    if frequency_hz <= 0:
        raise ValueError("frequency_hz must be positive")
    if duration_seconds <= 0:
        raise ValueError("duration_seconds must be positive")
    amplitude = max(0.0, min(1.0, amplitude))

    n_samples = int(framerate * duration_seconds)
    scale = amplitude * _PCM16_MAX
    samples = [
        int(scale * math.sin(2.0 * math.pi * frequency_hz * (i / framerate)))
        for i in range(n_samples)
    ]
    return struct.pack(f"<{len(samples)}h", *samples)


def write_wav(
    path: str | Path,
    pcm16_mono_samples: bytes,
    framerate: int = 44100,
) -> AudioInspection:
    """Write raw PCM16 mono samples to a WAV file and return its inspection."""
    path = Path(path)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(framerate)
        handle.writeframes(pcm16_mono_samples)
    return inspect_audio_file(path)


def create_tone_sequence_wav(
    path: str | Path,
    notes: list[tuple[float, float]],
    framerate: int = 44100,
    amplitude: float = 0.5,
) -> AudioInspection:
    """Create a WAV file from an ordered `(frequency_hz, duration_seconds)` sequence."""
    if not notes:
        raise ValueError("at least one note is required to create a tone sequence")
    chunks = [
        synthesize_tone(freq, dur, framerate=framerate, amplitude=amplitude)
        for freq, dur in notes
    ]
    return write_wav(path, b"".join(chunks), framerate=framerate)
