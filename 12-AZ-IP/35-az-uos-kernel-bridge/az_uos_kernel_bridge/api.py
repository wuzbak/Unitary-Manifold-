# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Host-side JSON API dispatch for the Product 35 bridge contract.

Wraps the source cross-check, scheduler contract, and strict IPC message
adapter for local HTTP access; it does not connect to a running kernel.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List, Mapping

from .addressing import N_RINGS, WindingAddress, validate_against_kk_channel_rs
from .interface_contract import GEODESIC_SCHEDULABLE_RUST_CONTRACT
from .ipc_message import decode_kernel_message, encode_kernel_message

API_ENDPOINTS = (
    "/api/status",
    "/api/validate-adjacency",
    "/api/neighbors",
    "/api/contract",
    "/api/ipc-message (POST)",
)


def _first(query: Mapping[str, List[str]], key: str, default: str | None = None) -> str | None:
    values = query.get(key)
    return values[0] if values else default


def dispatch_api_request(
    path: str,
    query: Mapping[str, List[str]],
    *,
    method: str = "GET",
    body: Any = None,
) -> Dict[str, Any]:
    if path == "/api/ipc-message":
        if method != "POST":
            raise KeyError("POST required for /api/ipc-message")
        message = decode_kernel_message(body)
        return {
            "kernel_message": message.to_dict(),
            "json_adapter_record": encode_kernel_message(message),
            "transport_note": "JSON adapter record; not a kernel wire ABI",
        }
    if method != "GET":
        raise KeyError(f"unsupported method for API endpoint: {method}")

    if path == "/api/status":
        return {"product": "AZ UOS/AZ-KERNEL Bridge", "endpoints": list(API_ENDPOINTS), "n_rings": N_RINGS}

    if path == "/api/validate-adjacency":
        return validate_against_kk_channel_rs()

    if path == "/api/neighbors":
        ring = int(_first(query, "ring", "0"))
        address = WindingAddress(ring)
        neighbors = address.neighbors()
        return {"ring": ring, "neighbors": [n.ring for n in neighbors]}

    if path == "/api/contract":
        return {"rust_contract": [asdict(field) for field in GEODESIC_SCHEDULABLE_RUST_CONTRACT]}

    raise KeyError(f"unknown API endpoint: {path}")
