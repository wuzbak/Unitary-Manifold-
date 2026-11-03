# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""JSON API dispatch — Phase 2 of article-354 direction #4.

Wraps `circuit_export.py` for live HTTP access. `/api/circuit` builds and
validates a braided-lattice ansatz circuit for a deterministic (seeded)
parameter vector, so the endpoint is reproducible without requiring the
caller to post a parameter array over GET.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping

import numpy as np

from .circuit_export import (
    MAX_LAYERS,
    MAX_QUBITS,
    MIN_QUBITS,
    build_braided_ansatz_circuit,
    export_openqasm2,
    validate_against_kk_vqe,
)

API_ENDPOINTS = ("/api/status", "/api/circuit")


def _first(query: Mapping[str, List[str]], key: str, default: str | None = None) -> str | None:
    values = query.get(key)
    return values[0] if values else default


def dispatch_api_request(path: str, query: Mapping[str, List[str]]) -> Dict[str, Any]:
    if path == "/api/status":
        return {"product": "AZ Braided Qubit Ansatz Studio", "endpoints": list(API_ENDPOINTS)}

    if path == "/api/circuit":
        allowed = {"n_qubits", "n_layers", "seed", "angles"}
        if set(query) - allowed or any(len(values) != 1 for values in query.values()):
            raise ValueError("unknown or repeated query parameters")
        if "angles" in query and "seed" in query:
            raise ValueError("provide either angles or seed, not both")
        try:
            n_qubits = int(_first(query, "n_qubits", "8"))
            n_layers = int(_first(query, "n_layers", "2"))
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("n_qubits and n_layers must be integers") from exc
        if not MIN_QUBITS <= n_qubits <= MAX_QUBITS:
            raise ValueError(f"n_qubits must be in {MIN_QUBITS}..{MAX_QUBITS}")
        if not 0 <= n_layers <= MAX_LAYERS:
            raise ValueError(f"n_layers must be in 0..{MAX_LAYERS}")
        if "angles" in query:
            raw_angles = _first(query, "angles")
            if raw_angles is None or len(raw_angles) > 4096:
                raise ValueError("angles must be a non-empty list no longer than 4096 characters")
            try:
                theta = np.asarray([float(value.strip()) for value in raw_angles.split(",")], dtype=float)
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError("angles must be comma-separated finite numbers") from exc
            seed = None
            parameter_source = "user"
        else:
            try:
                seed = int(_first(query, "seed", "42"))
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError("seed must be an integer") from exc
            if not 0 <= seed <= 2**32 - 1:
                raise ValueError("seed must be in 0..4294967295")
            rng = np.random.default_rng(seed)
            theta = rng.uniform(-np.pi, np.pi, size=n_qubits * (n_layers + 1))
            parameter_source = "seeded"

        circuit = build_braided_ansatz_circuit(theta, n_qubits, n_layers)
        validation = validate_against_kk_vqe(theta, n_qubits, n_layers)
        return {
            "n_qubits": n_qubits,
            "n_layers": n_layers,
            "seed": seed,
            "parameter_source": parameter_source,
            "gate_count": len(circuit.gates),
            "circuit": circuit.to_dict(),
            "openqasm2": export_openqasm2(circuit),
            "validation": validation,
        }

    raise KeyError(f"unknown API endpoint: {path}")
