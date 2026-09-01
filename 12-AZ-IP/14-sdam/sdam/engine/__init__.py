# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Engine exports for SDAM."""

from .um_modulation import (
    MODULATION_SYMBOLS,
    WINDING_NUMBER,
    decode_symbols,
    encode_message,
    generate_audio_params,
    get_braid_frequency,
)
from .whitepaper_content import WHITEPAPER_ABSTRACT, get_information_theory_grounding

__all__ = [
    'MODULATION_SYMBOLS',
    'WHITEPAPER_ABSTRACT',
    'WINDING_NUMBER',
    'decode_symbols',
    'encode_message',
    'generate_audio_params',
    'get_braid_frequency',
    'get_information_theory_grounding',
]
