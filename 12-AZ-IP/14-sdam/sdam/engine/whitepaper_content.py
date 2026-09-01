# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Whitepaper content helpers for SDAM."""
from __future__ import annotations

import math

WHITEPAPER_ABSTRACT = (
    "SDAM treats acoustic modulation as a constrained information geometry problem: a message is projected into a five-symbol alphabet tied to the repository's winding-number structure. "
    "That choice keeps the encoder simple, deterministic, and easy to audit in offline environments where radio stacks are disallowed.\n\n"
    "The five-symbol alphabet is not presented as a proof of new physics; it is an engineering metaphor grounded in the Unitary Manifold constants already used throughout the repository. "
    "The encoder therefore borrows the winding number and braid-resonance ratios as organizing parameters for near-ultrasonic carriers and symbol timing.\n\n"
    "Because each emitted symbol can be recovered with a finite-state decoder, the modulation layer stays compatible with Shannon-style analysis. "
    "This makes it possible to discuss entropy, redundancy, and carrier spacing without adding new dependencies or weakening the repository's plain epistemic status requirements."
)


def get_information_theory_grounding() -> dict:
    """Return a Shannon-style summary for the 5-symbol alphabet."""
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
