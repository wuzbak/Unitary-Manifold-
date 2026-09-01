# Copyright (C) 2026  ThomasCory Walker-Pearson
import math
import sys
from pathlib import Path

import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from sdam.engine.um_modulation import (
    MODULATION_SYMBOLS,
    WINDING_NUMBER,
    decode_symbols,
    encode_message,
    generate_audio_params,
    get_braid_frequency,
)
from sdam.engine.whitepaper_content import (
    WHITEPAPER_ABSTRACT,
    get_information_theory_grounding,
)


def test_winding_number_is_five():
    assert WINDING_NUMBER == 5


def test_modulation_symbols_cover_zero_through_four():
    assert MODULATION_SYMBOLS == [0, 1, 2, 3, 4]


def test_encode_message_returns_symbol_list():
    encoded = encode_message('A')
    assert isinstance(encoded, list)
    assert len(encoded) == 4


def test_encode_message_round_trips_ascii_text():
    text = 'HELLO'
    assert decode_symbols(encode_message(text)) == text


def test_encode_message_rejects_non_ascii():
    with pytest.raises(ValueError):
        encode_message('φ')


def test_decode_symbols_rejects_bad_length():
    with pytest.raises(ValueError):
        decode_symbols([1, 2, 3])


def test_decode_symbols_rejects_out_of_range_symbol():
    with pytest.raises(ValueError):
        decode_symbols([0, 0, 0, 9])


def test_get_braid_frequency_uses_base_for_zero_symbol():
    assert get_braid_frequency(0) == 440.0


def test_get_braid_frequency_increases_with_symbol():
    assert get_braid_frequency(4) > get_braid_frequency(1)


def test_get_braid_frequency_rejects_invalid_symbol():
    with pytest.raises(ValueError):
        get_braid_frequency(7)


def test_generate_audio_params_returns_one_entry_per_symbol():
    params = generate_audio_params('AB')
    assert len(params) == 8


def test_generate_audio_params_entries_have_expected_keys():
    entry = generate_audio_params('A')[0]
    assert {'symbol', 'frequency', 'duration_ms'} <= set(entry)


def test_generate_audio_params_uses_known_symbol_range():
    assert all(item['symbol'] in MODULATION_SYMBOLS for item in generate_audio_params('AB'))


def test_whitepaper_abstract_has_three_paragraphs():
    assert len(WHITEPAPER_ABSTRACT.split('\n\n')) == 3


def test_information_theory_grounding_shape():
    grounding = get_information_theory_grounding()
    assert {'alphabet_size', 'max_entropy_bits_per_symbol', 'symbols_per_ascii_character'} <= set(grounding)


def test_information_theory_grounding_entropy_matches_log2_five():
    grounding = get_information_theory_grounding()
    assert grounding['max_entropy_bits_per_symbol'] == round(math.log2(5), 6)


def test_information_theory_grounding_has_expected_utilization_bound():
    grounding = get_information_theory_grounding()
    assert 0 < grounding['seven_bit_ascii_utilization'] < 1
