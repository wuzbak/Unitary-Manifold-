# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Core constants for the standalone UM Reader / Educator."""

from __future__ import annotations

WINDING_NUMBER: int = 5
BRAID_PARTNER: int = 7
K_CS: int = 74
BRAIDED_SOUND_SPEED: float = 12 / 37
XI_C: float = 35 / 74

N_S: float = 0.9635
R_BRAIDED: float = 0.0315
BETA_LOW: float = 0.273
BETA_HIGH: float = 0.331

TOTAL_ENTRIES: int = 302
TOTAL_POSTS: int = 300
TOTAL_BOOKS: int = 2
TOPIC_CATEGORIES: int = 9
TOPIC_NAMES: tuple[str, ...] = (
    'cosmology',
    'particle physics',
    'consciousness',
    'governance',
    'geometry',
    'predictions',
    'experiments',
    'mathematics',
    'applications',
)

TTS_RATE: float = 0.95
TTS_PITCH: float = 1.05
TTS_MAX_CHARS: int = 500
DEFAULT_WPM: int = 180
DEFAULT_PORT: int = 8018
INDEX_FILENAME: str = 'reader-index.json'
