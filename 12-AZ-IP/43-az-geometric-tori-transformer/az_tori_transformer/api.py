# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""JSON API dispatch for the Geometric Tori Transformer (stdlib-only, GET-based)."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping

from .positional import rotation_orbit_periods, toroidal_relative_bias_indices
from .train_demo import run_toroidal_copy_demo

API_ENDPOINTS = ("/api/status", "/api/geometry", "/api/demo")


def _first(query: Mapping[str, List[str]], key: str, default: str | None = None) -> str | None:
    values = query.get(key)
    return values[0] if values else default


def dispatch_api_request(path: str, query: Mapping[str, List[str]]) -> Dict[str, Any]:
    if path == "/api/status":
        return {"product": "AZ Geometric Tori Transformer", "endpoints": list(API_ENDPOINTS)}

    if path == "/api/geometry":
        head_dim = int(_first(query, "head_dim", "8"))
        seq_len = int(_first(query, "seq_len", "16"))
        periods = rotation_orbit_periods(head_dim)
        bias_idx = toroidal_relative_bias_indices(seq_len)
        return {
            "head_dim": head_dim,
            "seq_len": seq_len,
            "rotation_orbit_periods": periods.tolist(),
            "relative_bias_index_sample": bias_idx[:min(seq_len, 8), :min(seq_len, 8)].tolist(),
        }

    if path == "/api/demo":
        seq_len = int(_first(query, "seq_len", "16"))
        vocab_size = int(_first(query, "vocab_size", "12"))
        shift = int(_first(query, "shift", "5"))
        steps = min(int(_first(query, "steps", "200")), 500)
        seed = int(_first(query, "seed", "0"))
        report = run_toroidal_copy_demo(
            seq_len=seq_len, vocab_size=vocab_size, shift=shift, steps=steps, seed=seed,
        )
        report.pop("loss_trace", None)
        return report

    raise KeyError(f"unknown API endpoint: {path}")
