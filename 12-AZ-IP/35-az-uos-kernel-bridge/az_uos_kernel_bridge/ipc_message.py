# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Strict JSON adapter for AZ-KERNEL's current ``KKMessage`` shape."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any, Mapping

from .addressing import N_RINGS, parse_runtime_channel_pairs

_U32_MAX = (1 << 32) - 1
_U64_MAX = (1 << 64) - 1
_FIELDS = frozenset({"from_ring", "to_ring", "payload", "seq"})


@dataclass(frozen=True)
class KKMessage:
    """Python-side value matching the fields in ``ipc::kk_channel::KKMessage``."""

    from_ring: int
    to_ring: int
    payload: int
    seq: int

    def __post_init__(self) -> None:
        for field in ("from_ring", "to_ring"):
            value = getattr(self, field)
            if type(value) is not int or not 0 <= value < N_RINGS:
                raise ValueError(f"{field} must be an integer in [0, {N_RINGS})")
        for field, maximum in (("payload", _U64_MAX), ("seq", _U32_MAX)):
            value = getattr(self, field)
            if type(value) is not int or not 0 <= value <= maximum:
                raise ValueError(f"{field} must be an unsigned integer <= {maximum}")
        if (self.from_ring, self.to_ring) not in parse_runtime_channel_pairs():
            raise ValueError(
                "ring pair is not accepted by AZ-KERNEL ipc::create_channel"
            )

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


def decode_kernel_message(value: Mapping[str, Any]) -> KKMessage:
    """Validate an input object and construct a kernel-shaped message value."""
    if not isinstance(value, Mapping) or set(value) != _FIELDS:
        raise ValueError(f"message must contain exactly: {', '.join(sorted(_FIELDS))}")
    return KKMessage(**{field: value[field] for field in _FIELDS})


def encode_kernel_message(message: KKMessage) -> str:
    """Serialize the field-compatible JSON adapter record in canonical order.

    This JSON representation is a host-side adapter format, not a Rust memory
    layout or wire ABI implemented by the kernel.
    """
    return json.dumps(message.to_dict(), separators=(",", ":"), sort_keys=True)


def decode_kernel_message_json(data: str | bytes) -> KKMessage:
    """Decode one strict JSON record; duplicate keys and non-JSON numbers fail."""
    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON field: {key}")
            result[key] = value
        return result

    def reject_constant(value: str) -> None:
        raise ValueError(f"invalid JSON number: {value}")

    try:
        decoded = json.loads(
            data, object_pairs_hook=unique_object, parse_constant=reject_constant
        )
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError("message must be valid JSON") from exc
    return decode_kernel_message(decoded)
