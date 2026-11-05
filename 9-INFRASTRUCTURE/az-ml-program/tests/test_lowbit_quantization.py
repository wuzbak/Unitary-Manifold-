# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Contract tests for the bounded standard-library low-bit reference."""

from __future__ import annotations

import hashlib
import json
import math
import random
import struct

import pytest

from src.infrastructure.lowbit_quantization import (
    QuantizedTensor,
    benchmark_reference,
    quantize,
)


def _reference_unpack(packed: bytes, count: int, bits: int) -> tuple[int, ...]:
    result = []
    for index in range(count):
        start = index * bits
        code = sum(
            ((packed[position // 8] >> (position % 8)) & 1) << bit
            for bit, position in enumerate(range(start, start + bits))
        )
        result.append(code)
    return tuple(result)


def _rebuild_with(encoded: bytes, *, metadata=None, packed=None) -> bytes:
    magic = b"AZLQ\x01"
    metadata_size = struct.unpack_from("<I", encoded, len(magic))[0]
    start = len(magic) + 4
    old_meta = json.loads(encoded[start:start + metadata_size])
    new_meta = old_meta if metadata is None else metadata
    new_packed = encoded[start + metadata_size:-32] if packed is None else packed
    meta_bytes = json.dumps(
        new_meta, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode("ascii")
    body = magic + struct.pack("<I", len(meta_bytes)) + meta_bytes + new_packed
    return body + hashlib.sha256(body).digest()


@pytest.mark.parametrize(("bits", "expected"), [(2, b"\x38"), (3, b"\xe0\x01")])
def test_independent_known_byte_packing_across_trailing_boundary(bits, expected):
    tensor = quantize([0, 1, 2], bit_width=bits, group_size=3)
    assert tensor.packed == expected
    assert _reference_unpack(tensor.packed, 3, bits) == (
        (0, 2, 3) if bits == 2 else (0, 4, 7)
    )
    scale = 2 / ((1 << bits) - 1)
    expected_middle = (2 if bits == 2 else 4) * scale
    assert tensor.dequantize() == (0.0, expected_middle, 2.0)


def test_symmetric_expected_codes_and_flattened_group_metadata():
    tensor = quantize([-1, 0, 1, 2, -2], bit_width=2, group_size=3, mode="symmetric")
    assert tensor.scales == (1.0, 2.0)
    assert tensor.zero_points == (2, 2)
    assert _reference_unpack(tensor.packed, 5, 2) == (1, 2, 3, 3, 1)
    assert tensor.dequantize() == (-1.0, 0.0, 1.0, 2.0, -2.0)


@pytest.mark.parametrize("bits", [2, 3, 4])
@pytest.mark.parametrize("mode", ["symmetric", "asymmetric"])
def test_seeded_values_pack_and_decode_deterministically(bits, mode):
    rng = random.Random(481516)
    values = [rng.uniform(-3.0, 5.0) for _ in range(37)]
    first = quantize(values, bit_width=bits, group_size=8, mode=mode)
    second = quantize(iter(values), bit_width=bits, group_size=8, mode=mode)
    assert first == second
    assert _reference_unpack(first.packed, len(values), bits) == _reference_unpack(
        second.packed, len(values), bits,
    )
    assert len(first.packed) == (len(values) * bits + 7) // 8
    assert first.dequantize() == second.dequantize()
    assert QuantizedTensor.from_bytes(first.to_bytes()) == first


@pytest.mark.parametrize(
    ("values", "mode"),
    [([0, 0, 0], "symmetric"), ([0, 0, 0], "asymmetric"),
     ([2.5, 2.5], "symmetric"), ([-2.5, -2.5], "asymmetric"),
     ([2.5, 2.5], "asymmetric"), ([-3, 4], "asymmetric")],
)
def test_constant_zero_negative_and_boundary_groups(values, mode):
    tensor = quantize(values, bit_width=3, group_size=2, mode=mode)
    assert all(value == pytest.approx(expected) for value, expected in zip(
        tensor.dequantize(), values,
    ))


@pytest.mark.parametrize("bits", [2, 3, 4])
def test_finite_float_boundaries_remain_encodable(bits):
    largest = float.fromhex("0x1.fffffffffffffp+1023")
    tiny = math.ulp(0.0)
    for values in ([-largest, largest], [tiny, tiny], [-tiny, -tiny]):
        try:
            tensor = quantize(values, bit_width=bits, group_size=2, mode="asymmetric")
        except ValueError as exc:
            assert "finite decode range" in str(exc)
            assert values == [-largest, largest]
            continue
        assert all(math.isfinite(value) for value in tensor.dequantize())
        assert QuantizedTensor.from_bytes(tensor.to_bytes()) == tensor


@pytest.mark.parametrize("bits", [2, 3, 4])
@pytest.mark.parametrize("values", [[100.0, 100.25, 101.0], [-101.0, -100.25, -100.0]])
def test_single_sign_narrow_range_independent_reference_and_half_step_bound(bits, values):
    qmax = (1 << bits) - 1
    low, high = min(0.0, min(values)), max(0.0, max(values))
    scale = (high - low) / qmax
    zero = min(qmax, max(0, round(-low / scale)))
    expected_codes = tuple(min(qmax, max(0, round(value / scale) + zero)) for value in values)
    expected_decoded = tuple((code - zero) * scale for code in expected_codes)
    tensor = quantize(values, bit_width=bits, group_size=3)
    assert tensor.scales == (scale,)
    assert tensor.zero_points == (zero,)
    assert _reference_unpack(tensor.packed, len(values), bits) == expected_codes
    assert tensor.dequantize() == expected_decoded
    expected_errors = tuple(abs(actual - value) for actual, value in zip(expected_decoded, values))
    metrics = tensor.metrics(values)
    assert metrics.max_absolute_error == max(expected_errors)
    assert metrics.mean_squared_error == math.fsum(
        error * error / len(values) for error in expected_errors
    )
    assert metrics.max_absolute_error <= scale / 2 + 1e-12


def test_malformed_finite_scales_that_overflow_decode_are_rejected():
    tensor = quantize([0.0, 1.0], bit_width=3, group_size=2)
    encoded = tensor.to_bytes()
    start = len(b"AZLQ\x01") + 4
    size = struct.unpack_from("<I", encoded, len(b"AZLQ\x01"))[0]
    metadata = json.loads(encoded[start:start + size])
    metadata["scales"] = [float.fromhex("0x1.fffffffffffffp+1023")]
    with pytest.raises(ValueError, match="finite decode range"):
        QuantizedTensor.from_bytes(_rebuild_with(encoded, metadata=metadata))


def test_extreme_error_metrics_fail_explicitly():
    values = [-1e200, -0.5e200, 1e200]
    tensor = quantize(values, bit_width=2, group_size=3, mode="symmetric")
    assert all(math.isfinite(value) for value in tensor.dequantize())
    with pytest.raises(ValueError, match="metrics exceed"):
        tensor.metrics(values)


def test_actual_large_vector_serialization_is_below_four_bits_per_weight():
    values = tuple(((index % 257) - 128) / 128 for index in range(32768))
    tensor = quantize(values, bit_width=3, group_size=1024, mode="symmetric")
    metrics = tensor.metrics(values)
    assert len(tensor.packed) == 12288
    assert metrics.serialized_bytes == len(tensor.to_bytes())
    assert metrics.effective_bits_per_weight == 8 * len(tensor.to_bytes()) / len(values)
    assert 3 < metrics.effective_bits_per_weight < 4
    assert metrics.max_absolute_error <= 1 / 6 + 1e-15
    assert QuantizedTensor.from_bytes(tensor.to_bytes()) == tensor


def test_serialized_size_metrics_include_metadata_and_checksum():
    values = [-1.0, -0.5, 0.25, 1.0, 2.0]
    tensor = quantize(values, bit_width=3, group_size=2, mode="asymmetric")
    metrics = tensor.metrics(values)
    errors = [abs(a - b) for a, b in zip(tensor.dequantize(), values)]
    assert metrics.max_absolute_error == max(errors)
    assert metrics.mean_squared_error == sum(error * error for error in errors) / len(errors)
    assert metrics.serialized_bytes == len(tensor.to_bytes())
    assert metrics.effective_bits_per_weight == 8 * len(tensor.to_bytes()) / len(values)
    assert metrics.effective_bits_per_weight > 3
    with pytest.raises(ValueError, match="identity"):
        tensor.metrics([*values[:-1], 9])


def test_save_load_exact_packed_artifact(tmp_path):
    tensor = quantize([0.125, -0.5, 1.75, -2.0, 0.0], bit_width=3, group_size=2)
    path = tensor.save(tmp_path / "weights.azlq")
    assert path.read_bytes() == tensor.to_bytes()
    assert QuantizedTensor.load(path) == tensor
    assert QuantizedTensor.load(path).packed == tensor.packed


def test_integrity_rejects_tampered_payload_and_truncation():
    tensor = quantize([1, 2, 3, 4], bit_width=3, group_size=2)
    encoded = tensor.to_bytes()
    altered = bytearray(encoded)
    altered[-33] ^= 0x01
    with pytest.raises(ValueError, match="integrity"):
        QuantizedTensor.from_bytes(bytes(altered))
    with pytest.raises(ValueError):
        QuantizedTensor.from_bytes(encoded[:-1])


@pytest.mark.parametrize(
    ("metadata_update", "packed_update", "message"),
    [
        ({"group_size": True}, None, "integer"),
        ({"value_count": 0}, None, "integer"),
        ({"bit_width": 8}, None, "bit_width"),
        ({"scales": [float("nan"), 1]}, None, "scales"),
        ({"zero_points": [True, 0]}, None, "zero_points"),
        ({"zero_points": [8, 0]}, None, "zero_points"),
        (None, b"\x00", "packed length"),
    ],
)
def test_checksum_valid_but_malformed_artifact_rejected(
    metadata_update, packed_update, message,
):
    tensor = quantize([1, 2, 3, 4], bit_width=3, group_size=2)
    encoded = tensor.to_bytes()
    magic = b"AZLQ\x01"
    metadata_size = struct.unpack_from("<I", encoded, len(magic))[0]
    start = len(magic) + 4
    metadata = json.loads(encoded[start:start + metadata_size])
    if metadata_update:
        metadata.update(metadata_update)
    malformed = _rebuild_with(encoded, metadata=metadata, packed=packed_update)
    with pytest.raises(ValueError, match=message):
        QuantizedTensor.from_bytes(malformed)


def test_nonzero_unused_bits_and_duplicate_metadata_keys_rejected():
    tensor = quantize([0, 1, 2], bit_width=2, group_size=3)
    packed = bytes([tensor.packed[0] | 0xC0])
    with pytest.raises(ValueError, match="trailing unused bits"):
        QuantizedTensor.from_bytes(_rebuild_with(tensor.to_bytes(), packed=packed))

    encoded = tensor.to_bytes()
    magic = b"AZLQ\x01"
    start = len(magic) + 4
    metadata_size = struct.unpack_from("<I", encoded, len(magic))[0]
    text = encoded[start:start + metadata_size].decode("ascii")
    duplicated = text[:-1] + ',"mode":"asymmetric"}'
    body = magic + struct.pack("<I", len(duplicated)) + duplicated.encode("ascii")
    body += encoded[start + metadata_size:-32]
    with pytest.raises(ValueError, match="metadata"):
        QuantizedTensor.from_bytes(body + hashlib.sha256(body).digest())


@pytest.mark.parametrize(
    ("values", "kwargs"),
    [
        ([], {"bit_width": 2, "group_size": 1}),
        ([True], {"bit_width": 2, "group_size": 1}),
        ([float("nan")], {"bit_width": 2, "group_size": 1}),
        ([float("inf")], {"bit_width": 2, "group_size": 1}),
        ([1], {"bit_width": True, "group_size": 1}),
        ([1], {"bit_width": 5, "group_size": 1}),
        ([1], {"bit_width": 2, "group_size": True}),
        ([1], {"bit_width": 2, "group_size": 0}),
        ([1], {"bit_width": 2, "group_size": 1, "mode": "other"}),
    ],
)
def test_invalid_inputs_and_configuration_rejected(values, kwargs):
    with pytest.raises(ValueError):
        quantize(values, **kwargs)


def test_tiny_benchmark_has_receipt_and_never_promotes():
    first = benchmark_reference(repetitions=1)
    second = benchmark_reference(repetitions=1)
    assert first["input_sha256"] == second["input_sha256"]
    assert len(first["source_sha256"]) == 64
    assert first["source_sha256"] == second["source_sha256"]
    assert first["float32_serialized_bytes"] == 256
    assert first["scope"].startswith("64-value deterministic CPU")
    assert set(first["results"]) == {"2", "3"}
    for bits, result in first["results"].items():
        assert result["serialized_bytes"] > (64 * int(bits) + 7) // 8
        assert result["elapsed_seconds"] >= 0
    receipt = first["receipt"]
    assert receipt["promotion"]["eligible"] is False
    assert receipt["promotion"]["model_claim"] is False
    assert receipt["promotion"]["backend_claim"] is False


def test_benchmark_repetition_bool_rejected():
    with pytest.raises(ValueError, match="repetitions"):
        benchmark_reference(repetitions=True)
