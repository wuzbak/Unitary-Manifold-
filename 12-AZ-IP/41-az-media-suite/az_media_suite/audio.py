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
import sys
import wave
from array import array
from dataclasses import dataclass
from pathlib import Path

_PCM16_MAX = 32767
_MIN_FRAMERATE = 8000
_MAX_FRAMERATE = 192000
_MAX_SYNTHESIS_SAMPLES = 5_000_000


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
    try:
        frequency_hz = float(frequency_hz)
        duration_seconds = float(duration_seconds)
        amplitude = float(amplitude)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("frequency, duration, and amplitude must be finite numbers") from exc
    if not math.isfinite(frequency_hz) or frequency_hz <= 0:
        raise ValueError("frequency_hz must be finite and positive")
    if type(framerate) is not int or not _MIN_FRAMERATE <= framerate <= _MAX_FRAMERATE:
        raise ValueError(f"framerate must be an integer in {_MIN_FRAMERATE}..{_MAX_FRAMERATE}")
    if frequency_hz >= framerate / 2:
        raise ValueError("frequency_hz must be below the Nyquist frequency")
    if not math.isfinite(duration_seconds) or not 0 < duration_seconds <= 60:
        raise ValueError("duration_seconds must be finite and in (0, 60]")
    if not math.isfinite(amplitude) or not 0 <= amplitude <= 1:
        raise ValueError("amplitude must be finite and in 0..1")
    n_samples = int(framerate * duration_seconds)
    if not 1 <= n_samples <= _MAX_SYNTHESIS_SAMPLES:
        raise ValueError(f"tone length must be 1..{_MAX_SYNTHESIS_SAMPLES} samples")
    scale = amplitude * _PCM16_MAX
    samples = array(
        "h",
        (
            int(scale * math.sin(2.0 * math.pi * frequency_hz * (i / framerate)))
            for i in range(n_samples)
        ),
    )
    if samples.itemsize != 2:
        raise RuntimeError("native short width is not 16 bits")
    if sys.byteorder != "little":
        samples.byteswap()
    return samples.tobytes()


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
    if len(notes) > 1000:
        raise ValueError("tone sequences may contain at most 1000 notes")
    if type(framerate) is not int or not _MIN_FRAMERATE <= framerate <= _MAX_FRAMERATE:
        raise ValueError(f"framerate must be an integer in {_MIN_FRAMERATE}..{_MAX_FRAMERATE}")
    total_samples = 0
    for frequency, duration in notes:
        try:
            frequency = float(frequency)
            duration = float(duration)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("note frequencies and durations must be finite numbers") from exc
        if not math.isfinite(frequency) or not 0 < frequency < framerate / 2:
            raise ValueError("note frequency must be finite, positive, and below Nyquist")
        if not math.isfinite(duration) or duration <= 0:
            raise ValueError("note duration must be finite and positive")
        total_samples += int(framerate * duration)
        if total_samples > _MAX_SYNTHESIS_SAMPLES:
            raise ValueError(f"tone sequence may not exceed {_MAX_SYNTHESIS_SAMPLES} samples")
    chunks = [
        synthesize_tone(freq, dur, framerate=framerate, amplitude=amplitude)
        for freq, dur in notes
    ]
    return write_wav(path, b"".join(chunks), framerate=framerate)
