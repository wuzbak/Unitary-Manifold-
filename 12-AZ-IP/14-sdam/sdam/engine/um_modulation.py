# Copyright (C) 2026  ThomasCory Walker-Pearson
"""UM-grounded modulation helpers for SDAM."""
from __future__ import annotations

import math

WINDING_NUMBER = 5
MODULATION_SYMBOLS = list(range(WINDING_NUMBER))
_CHAR_WIDTH = 4


def _to_base_five(value: int) -> list[int]:
    digits = [0] * _CHAR_WIDTH
    for index in range(_CHAR_WIDTH - 1, -1, -1):
        digits[index] = value % WINDING_NUMBER
        value //= WINDING_NUMBER
    return digits


def encode_message(text: str) -> list[int]:
    """Encode ASCII text into a fixed-width 5-symbol alphabet."""
    symbols: list[int] = []
    for char in text:
        code = ord(char)
        if code > 127:
            raise ValueError('encode_message only supports ASCII input')
        symbols.extend(_to_base_five(code))
    return symbols


def decode_symbols(symbols: list[int]) -> str:
    """Decode a fixed-width base-5 symbol stream back into ASCII."""
    if len(symbols) % _CHAR_WIDTH != 0:
        raise ValueError('symbol sequence length must be divisible by 4')
    chars = []
    for offset in range(0, len(symbols), _CHAR_WIDTH):
        value = 0
        for symbol in symbols[offset: offset + _CHAR_WIDTH]:
            if symbol not in MODULATION_SYMBOLS:
                raise ValueError('symbol out of range')
            value = value * WINDING_NUMBER + symbol
        if value > 127:
            raise ValueError('decoded value exceeds ASCII range')
        chars.append(chr(value))
    return ''.join(chars)


def get_braid_frequency(symbol: int, base_freq: float = 440.0) -> float:
    """Map a symbol onto a braid-resonant carrier frequency."""
    if symbol not in MODULATION_SYMBOLS:
        raise ValueError('symbol out of range')
    return round(base_freq * (7 / 5) ** (symbol / max(1, WINDING_NUMBER - 1)), 6)


def generate_audio_params(message: str) -> list[dict]:
    """Generate Web Audio API friendly modulation parameters."""
    params = []
    for index, symbol in enumerate(encode_message(message)):
        params.append({
            'symbol': symbol,
            'frequency': get_braid_frequency(symbol),
            'duration_ms': 90 + symbol * 15 + (index % WINDING_NUMBER) * 5,
        })
    return params
