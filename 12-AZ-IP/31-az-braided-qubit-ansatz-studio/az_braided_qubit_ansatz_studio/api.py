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

from .circuit_export import build_braided_ansatz_circuit, validate_against_kk_vqe

API_ENDPOINTS = ("/api/status", "/api/circuit")


def _first(query: Mapping[str, List[str]], key: str, default: str | None = None) -> str | None:
    values = query.get(key)
    return values[0] if values else default


def dispatch_api_request(path: str, query: Mapping[str, List[str]]) -> Dict[str, Any]:
    if path == "/api/status":
        return {"product": "AZ Braided Qubit Ansatz Studio", "endpoints": list(API_ENDPOINTS)}

    if path == "/api/circuit":
        n_qubits = int(_first(query, "n_qubits", "8"))
        n_layers = int(_first(query, "n_layers", "2"))
        seed = int(_first(query, "seed", "42"))
        rng = np.random.default_rng(seed)
        theta = rng.uniform(-np.pi, np.pi, size=n_qubits * (n_layers + 1))

        circuit = build_braided_ansatz_circuit(theta, n_qubits, n_layers)
        validation = validate_against_kk_vqe(theta, n_qubits, n_layers)
        return {
            "n_qubits": n_qubits,
            "n_layers": n_layers,
            "seed": seed,
            "gate_count": len(circuit.gates),
            "circuit": circuit.to_dict(),
            "validation": validation,
        }

    raise KeyError(f"unknown API endpoint: {path}")
