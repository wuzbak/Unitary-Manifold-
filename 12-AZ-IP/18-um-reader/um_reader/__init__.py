# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""UM Reader / Educator package."""

from .engine.constants import (
    BETA_HIGH,
    BETA_LOW,
    DEFAULT_PORT,
    N_S,
    K_CS,
    R_BRAIDED,
    TTS_PITCH,
    TTS_RATE,
    TOTAL_ENTRIES,
    TOPIC_CATEGORIES,
    TOPIC_NAMES,
    WINDING_NUMBER,
)
from .engine.index import (
    filter_by_category,
    get_categories,
    get_entry_by_id,
    get_stats,
    load_index,
    search_entries,
    validate_entry,
)
from .engine.tts import chunk_text, estimate_reading_time, preprocess_math

__all__ = [
    'BETA_HIGH',
    'BETA_LOW',
    'DEFAULT_PORT',
    'N_S',
    'K_CS',
    'R_BRAIDED',
    'TOTAL_ENTRIES',
    'TOPIC_CATEGORIES',
    'TOPIC_NAMES',
    'TTS_PITCH',
    'TTS_RATE',
    'WINDING_NUMBER',
    'chunk_text',
    'estimate_reading_time',
    'filter_by_category',
    'get_categories',
    'get_entry_by_id',
    'get_stats',
    'load_index',
    'preprocess_math',
    'search_entries',
    'validate_entry',
]
__version__ = '1.0.0'
