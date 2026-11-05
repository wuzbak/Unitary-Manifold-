# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Bounded CPU reference for groupwise affine low-bit weight quantization.

This module covers flattened numeric vectors only. It is not a transformer
converter, model backend, deployment path, or performance claim.

Support matrix: 2/3 bits plus a 4-bit reference; symmetric signed or asymmetric
zero-inclusive affine groups; final partial groups; CPU/Python only. Rounding
uses nearest ties-to-even. Codes are unsigned, least-significant-bit first,
contiguous across byte boundaries, with zero padding in the final byte.
Quantization is lossy; packed artifact save/load is exact. Effective bits count
the entire serialized file, including metadata, framing, and integrity digest.
SHA-256 detects corruption, not authenticity against a writer who rehashes data.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from numbers import Real
from pathlib import Path
import struct
import time
from typing import Iterable

from .execution_spine import ExecutionSpineRecord, build_fail_closed_governance

LOWBIT_SCHEMA_VERSION = "az_lowbit_quantization_v1"
_MAGIC = b"AZLQ\x01"
_DIGEST_SIZE = hashlib.sha256().digest_size
_SUPPORTED_BITS = frozenset({2, 3, 4})
_SUPPORTED_MODES = frozenset({"symmetric", "asymmetric"})


def _canonical_json(payload: dict[str, object]) -> bytes:
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False,
    ).encode("ascii")


def _unique_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate metadata key: {key!r}.")
        result[key] = value
    return result


def _values(values: Iterable[Real]) -> tuple[float, ...]:
    if isinstance(values, (str, bytes, bytearray)):
        raise ValueError("values must be a non-empty iterable of finite real numbers.")
    try:
        result = tuple(values)
    except TypeError as exc:
        raise ValueError("values must be a non-empty iterable of finite real numbers.") from exc
    if not result:
        raise ValueError("values must not be empty.")
    converted: list[float] = []
    for value in result:
        if isinstance(value, bool) or not isinstance(value, Real):
            raise ValueError("values must contain only finite real numbers; bool is not accepted.")
        try:
            number = float(value)
        except (OverflowError, ValueError) as exc:
            raise ValueError("values must contain only representable finite real numbers.") from exc
        if not math.isfinite(number):
            raise ValueError("values must contain only finite real numbers.")
        converted.append(number)
    return tuple(converted)


def _input_hash(values: tuple[float, ...]) -> str:
    digest = hashlib.sha256()
    digest.update(struct.pack("<Q", len(values)))
    for value in values:
        digest.update(struct.pack("<d", value))
    return digest.hexdigest()


def _integer(name: str, value: object, *, minimum: int = 1) -> int:
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}; bool is not accepted.")
    return value


def _pack_codes(codes: tuple[int, ...], bits: int) -> bytes:
    packed = bytearray((len(codes) * bits + 7) // 8)
    bit_offset = 0
    for code in codes:
        for bit in range(bits):
            if code & (1 << bit):
                position = bit_offset + bit
                packed[position // 8] |= 1 << (position % 8)
        bit_offset += bits
    return bytes(packed)


def _unpack_codes(packed: bytes, count: int, bits: int) -> tuple[int, ...]:
    result = []
    bit_offset = 0
    for _ in range(count):
        code = 0
        for bit in range(bits):
            position = bit_offset + bit
            code |= ((packed[position // 8] >> (position % 8)) & 1) << bit
        result.append(code)
        bit_offset += bits
    return tuple(result)


@dataclass(frozen=True)
class QuantizationMetrics:
    max_absolute_error: float
    mean_squared_error: float
    serialized_bytes: int
    effective_bits_per_weight: float
    input_sha256: str


@dataclass(frozen=True)
class QuantizedTensor:
    """Immutable packed tensor plus the complete groupwise decode metadata."""

    bit_width: int
    mode: str
    group_size: int
    value_count: int
    scales: tuple[float, ...]
    zero_points: tuple[int, ...]
    input_sha256: str
    packed: bytes
    schema_version: str = LOWBIT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != LOWBIT_SCHEMA_VERSION:
            raise ValueError(f"Unsupported low-bit schema version: {self.schema_version!r}.")
        if type(self.bit_width) is not int or self.bit_width not in _SUPPORTED_BITS:
            raise ValueError(f"bit_width must be one of {sorted(_SUPPORTED_BITS)}.")
        if not isinstance(self.mode, str) or self.mode not in _SUPPORTED_MODES:
            raise ValueError(f"mode must be one of {sorted(_SUPPORTED_MODES)}.")
        _integer("group_size", self.group_size)
        _integer("value_count", self.value_count)
        group_count = (self.value_count + self.group_size - 1) // self.group_size
        if not isinstance(self.scales, tuple) or len(self.scales) != group_count:
            raise ValueError("scales must contain exactly one value per group.")
        if any(isinstance(scale, bool) or not isinstance(scale, Real)
               or not math.isfinite(float(scale)) or float(scale) <= 0 for scale in self.scales):
            raise ValueError("scales must be finite positive real numbers.")
        object.__setattr__(self, "scales", tuple(float(scale) for scale in self.scales))
        if not isinstance(self.zero_points, tuple) or len(self.zero_points) != group_count:
            raise ValueError("zero_points must contain exactly one integer per group.")
        if any(type(point) is not int for point in self.zero_points):
            raise ValueError("zero_points must be integers; bool is not accepted.")
        code_max = (1 << self.bit_width) - 1
        if any(point < 0 or point > code_max for point in self.zero_points):
            raise ValueError("zero_points are outside the encoded value range.")
        if self.mode == "symmetric":
            expected = 1 << (self.bit_width - 1)
            if any(point != expected for point in self.zero_points):
                raise ValueError("symmetric zero_points do not match the signed code offset.")
        if not isinstance(self.input_sha256, str) or len(self.input_sha256) != 64:
            raise ValueError("input_sha256 must be a lowercase SHA-256 digest.")
        try:
            bytes.fromhex(self.input_sha256)
        except ValueError as exc:
            raise ValueError("input_sha256 must be a lowercase SHA-256 digest.") from exc
        if (self.input_sha256.lower() != self.input_sha256
                or any(character not in "0123456789abcdef" for character in self.input_sha256)):
            raise ValueError("input_sha256 must be a lowercase SHA-256 digest.")
        if not isinstance(self.packed, bytes):
            raise ValueError("packed must be immutable bytes.")
        expected_length = (self.value_count * self.bit_width + 7) // 8
        if len(self.packed) != expected_length:
            raise ValueError("packed length does not match value_count and bit_width.")
        remainder = (self.value_count * self.bit_width) % 8
        if remainder and self.packed[-1] >> remainder:
            raise ValueError("packed data has nonzero trailing unused bits.")
        codes = _unpack_codes(self.packed, self.value_count, self.bit_width)
        if self.mode == "symmetric":
            if any(code == 0 for code in codes):
                raise ValueError("packed symmetric code uses an unsupported endpoint.")
        for index, code in enumerate(codes):
            group = index // self.group_size
            if not math.isfinite((code - self.zero_points[group]) * self.scales[group]):
                raise ValueError("Encoded values exceed the finite decode range.")

    def dequantize(self) -> tuple[float, ...]:
        """Return the deterministic decoded flattened vector."""
        codes = _unpack_codes(self.packed, self.value_count, self.bit_width)
        decoded = []
        offset = 1 << (self.bit_width - 1)
        for index, code in enumerate(codes):
            group = index // self.group_size
            if self.mode == "symmetric":
                difference = code - offset
            else:
                difference = code - self.zero_points[group]
            value = difference * self.scales[group]
            if not math.isfinite(value):
                raise ValueError("Encoded values exceed the finite decode range.")
            decoded.append(value)
        return tuple(decoded)

    def to_bytes(self) -> bytes:
        """Serialize metadata and packed bytes with a SHA-256 integrity digest."""
        metadata = _canonical_json({
            "schema_version": self.schema_version,
            "bit_width": self.bit_width,
            "mode": self.mode,
            "group_size": self.group_size,
            "value_count": self.value_count,
            "scales": list(self.scales),
            "zero_points": list(self.zero_points),
            "input_sha256": self.input_sha256,
        })
        body = _MAGIC + struct.pack("<I", len(metadata)) + metadata + self.packed
        return body + hashlib.sha256(body).digest()

    @classmethod
    def from_bytes(cls, data: bytes) -> "QuantizedTensor":
        """Parse and verify an encoded tensor, rejecting malformed or altered bytes."""
        if not isinstance(data, bytes):
            raise ValueError("serialized tensor must be bytes.")
        if len(data) < len(_MAGIC) + 4 + _DIGEST_SIZE or not data.startswith(_MAGIC):
            raise ValueError("Invalid low-bit tensor header.")
        body, digest = data[:-_DIGEST_SIZE], data[-_DIGEST_SIZE:]
        if not hashlib.sha256(body).digest() == digest:
            raise ValueError("Low-bit tensor SHA-256 integrity check failed.")
        metadata_length = struct.unpack_from("<I", body, len(_MAGIC))[0]
        metadata_start = len(_MAGIC) + 4
        metadata_end = metadata_start + metadata_length
        if metadata_end > len(body):
            raise ValueError("Truncated low-bit tensor metadata.")
        try:
            metadata = json.loads(
                body[metadata_start:metadata_end].decode("ascii"),
                object_pairs_hook=_unique_json_object,
            )
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            raise ValueError("Malformed low-bit tensor metadata.") from exc
        expected_fields = {
            "schema_version", "bit_width", "mode", "group_size", "value_count",
            "scales", "zero_points", "input_sha256",
        }
        if not isinstance(metadata, dict) or set(metadata) != expected_fields:
            raise ValueError("Malformed low-bit tensor metadata schema.")
        if type(metadata["bit_width"]) is not int:
            raise ValueError("bit_width metadata must be an integer.")
        if type(metadata["group_size"]) is not int or type(metadata["value_count"]) is not int:
            raise ValueError("count metadata must contain integers.")
        if (not isinstance(metadata["scales"], list)
                or not isinstance(metadata["zero_points"], list)):
            raise ValueError("scale and zero-point metadata must be arrays.")
        return cls(
            bit_width=metadata["bit_width"],
            mode=metadata["mode"],
            group_size=metadata["group_size"],
            value_count=metadata["value_count"],
            scales=tuple(metadata["scales"]),
            zero_points=tuple(metadata["zero_points"]),
            input_sha256=metadata["input_sha256"],
            packed=body[metadata_end:],
            schema_version=metadata["schema_version"],
        )

    def save(self, path: str | Path) -> Path:
        """Write the encoded artifact to the caller-selected path."""
        target = Path(path)
        target.write_bytes(self.to_bytes())
        return target

    @classmethod
    def load(cls, path: str | Path) -> "QuantizedTensor":
        """Read and validate an encoded artifact from the caller-selected path."""
        try:
            return cls.from_bytes(Path(path).read_bytes())
        except OSError as exc:
            raise ValueError(f"Unable to read low-bit tensor: {exc}") from exc

    def metrics(self, original: Iterable[Real]) -> QuantizationMetrics:
        values = _values(original)
        if len(values) != self.value_count or _input_hash(values) != self.input_sha256:
            raise ValueError("original values do not match this tensor's recorded input identity.")
        decoded = self.dequantize()
        errors = tuple(abs(actual - expected) for actual, expected in zip(decoded, values))
        if any(not math.isfinite(error) or not math.isfinite(error * error) for error in errors):
            raise ValueError("Error metrics exceed the finite representable range.")
        try:
            mse = math.fsum((error * error) / len(errors) for error in errors)
        except OverflowError as exc:
            raise ValueError("Error metrics exceed the finite representable range.") from exc
        if not math.isfinite(mse):
            raise ValueError("Error metrics exceed the finite representable range.")
        serialized_bytes = len(self.to_bytes())
        return QuantizationMetrics(
            max_absolute_error=max(errors),
            mean_squared_error=mse,
            serialized_bytes=serialized_bytes,
            effective_bits_per_weight=8 * serialized_bytes / self.value_count,
            input_sha256=self.input_sha256,
        )


def quantize(
    values: Iterable[Real],
    *,
    bit_width: int,
    group_size: int,
    mode: str = "asymmetric",
) -> QuantizedTensor:
    """Quantize finite values; reject calibration producing nonfinite decoded values.

    Asymmetric calibration includes zero, including for single-sign groups.
    Extremely small magnitudes use the least positive float scale; extremely
    large finite inputs may raise ValueError if rounded decoding would overflow.
    """
    numbers = _values(values)
    if type(bit_width) is not int or bit_width not in _SUPPORTED_BITS:
        raise ValueError(f"bit_width must be one of {sorted(_SUPPORTED_BITS)}.")
    _integer("group_size", group_size)
    if not isinstance(mode, str) or mode not in _SUPPORTED_MODES:
        raise ValueError(f"mode must be one of {sorted(_SUPPORTED_MODES)}.")
    scales: list[float] = []
    zero_points: list[int] = []
    codes: list[int] = []
    code_max = (1 << bit_width) - 1
    if mode == "symmetric":
        offset = 1 << (bit_width - 1)
        qmax = offset - 1
        for start in range(0, len(numbers), group_size):
            group = numbers[start:start + group_size]
            maximum = max(abs(value) for value in group)
            scale = max(maximum / qmax, math.ulp(0.0)) if maximum else 1.0
            scales.append(scale)
            zero_points.append(offset)
            codes.extend(
                min(qmax, max(-qmax, round(value / scale))) + offset
                for value in group
            )
    else:
        for start in range(0, len(numbers), group_size):
            group = numbers[start:start + group_size]
            minimum, maximum = min(0.0, min(group)), max(0.0, max(group))
            if minimum == maximum:
                if minimum == 0:
                    scale, zero_point, quantized = 1.0, 0, 0
                elif minimum > 0:
                    scale, zero_point, quantized = max(minimum / code_max, math.ulp(0.0)), 0, code_max
                else:
                    scale, zero_point, quantized = max(-minimum / code_max, math.ulp(0.0)), code_max, 0
                scales.append(scale)
                zero_points.append(zero_point)
                codes.extend((quantized,) * len(group))
                continue
            span = (
                maximum / code_max - minimum / code_max
                if minimum < 0 < maximum
                else (maximum - minimum) / code_max
            )
            scale = max(span, math.ulp(0.0))
            zero_point = min(code_max, max(0, round(-minimum / scale)))
            scales.append(scale)
            zero_points.append(zero_point)
            codes.extend(
                min(code_max, max(0, round(value / scale) + zero_point))
                for value in group
            )
    return QuantizedTensor(
        bit_width=bit_width,
        mode=mode,
        group_size=group_size,
        value_count=len(numbers),
        scales=tuple(scales),
        zero_points=tuple(zero_points),
        input_sha256=_input_hash(numbers),
        packed=_pack_codes(tuple(codes), bit_width),
    )


def benchmark_reference(*, repetitions: int = 3) -> dict[str, object]:
    """Run a tiny deterministic CPU comparison; this is not a model benchmark."""
    _integer("repetitions", repetitions)
    values = tuple(
        ((index % 17) - 8) / 8 + ((index % 5) - 2) / 64
        for index in range(64)
    )
    results: dict[str, object] = {}
    for bits in (2, 3):
        start = time.perf_counter()
        tensor = None
        for _ in range(repetitions):
            tensor = quantize(values, bit_width=bits, group_size=16, mode="symmetric")
            tensor.to_bytes()
        elapsed = time.perf_counter() - start
        assert tensor is not None
        metrics = tensor.metrics(values)
        results[str(bits)] = {
            "elapsed_seconds": elapsed,
            "max_absolute_error": metrics.max_absolute_error,
            "mean_squared_error": metrics.mean_squared_error,
            "serialized_bytes": metrics.serialized_bytes,
            "effective_bits_per_weight": metrics.effective_bits_per_weight,
        }
    float32_bytes = b"".join(struct.pack("<f", value) for value in values)
    input_hash = _input_hash(values)
    source_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return {
        "scope": "64-value deterministic CPU reference only; not a model or backend benchmark",
        "input_sha256": input_hash,
        "source_sha256": source_hash,
        "float32_serialized_bytes": len(float32_bytes),
        "repetitions": repetitions,
        "results": results,
        "receipt": ExecutionSpineRecord(
            surface_id=f"az-lowbit-reference:{input_hash[:16]}",
            surface_kind="bounded_lowbit_reference_benchmark",
            lane="non-hardgate-ml-infrastructure",
            status="reference_measured",
            summary="Measured a tiny deterministic flattened-vector CPU reference only.",
            canonical_paths=["src/infrastructure/lowbit_quantization.py"],
            sources=["src/infrastructure/lowbit_quantization.py"],
            governance=build_fail_closed_governance(
                epistemic_label="bounded toy-vector algorithm reference",
                promotion_rule="Reference measurements do not establish model, backend, or production capability.",
                residual_blockers=[
                    "No transformer or model artifact was loaded.",
                    "No CUDA, kernel, serving, or deployment behavior was measured.",
                ],
            ),
            compatibility={
                "input_sha256": input_hash,
                "source_sha256": source_hash,
                "float32_serialized_bytes": len(float32_bytes),
                "measurements": results,
            },
            promotion={
                "eligible": False,
                "reason": "A toy reference benchmark is not capability validation.",
                "model_claim": False,
                "backend_claim": False,
            },
        ).to_dict(),
    }


__all__ = [
    "LOWBIT_SCHEMA_VERSION",
    "QuantizationMetrics",
    "QuantizedTensor",
    "benchmark_reference",
    "quantize",
]
