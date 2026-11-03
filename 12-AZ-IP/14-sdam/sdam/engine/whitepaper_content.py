# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Whitepaper content helpers for SDAM."""
from __future__ import annotations

import math

WHITEPAPER_ABSTRACT = (
    "The current SDAM Android implementation sends text through ggwave's FSK acoustic codec, with AES-GCM payload encryption and authenticated SDAM1 frames. "
    "It does not use a five-symbol alphabet or a custom geometric modulation scheme, and its acoustic behavior has not been validated on target devices.\n\n"
    "The Unitary Manifold constants may be explored as a research hypothesis for future protocol design, but no validated derivation connects them to ggwave carrier frequencies, symbol timing, or error correction. "
    "They are not inputs to the current native audio path and are not presented as a demonstrated performance improvement.\n\n"
    "Information-theoretic calculations for a hypothetical five-symbol alphabet are illustrative only. "
    "They do not describe the current wire format or establish an advantage over conventional modulation."
)


def get_information_theory_grounding() -> dict:
    """Return illustrative Shannon-style values for a hypothetical 5-symbol alphabet."""
    entropy = math.log2(5)
    bits_per_char = 4 * entropy
    return {
        'alphabet_size': 5,
        'max_entropy_bits_per_symbol': round(entropy, 6),
        'symbols_per_ascii_character': 4,
        'payload_bits_per_ascii_character': round(bits_per_char, 6),
        'seven_bit_ascii_utilization': round(7 / bits_per_char, 6),
        'carrier_spacing_ratio': 7 / 5,
    }
