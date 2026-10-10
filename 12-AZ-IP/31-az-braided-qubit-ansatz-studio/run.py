#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""CLI entrypoint for the AZ Braided Qubit Ansatz Studio (Product 31)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from az_braided_qubit_ansatz_studio import build_braided_ansatz_circuit, validate_against_kk_vqe


def main(argv: list[str] | None = None) -> int:
    n_qubits = 8
    n_layers = 2
    rng = np.random.default_rng(42)
    theta = rng.uniform(-np.pi, np.pi, size=n_qubits * (n_layers + 1))

    circuit = build_braided_ansatz_circuit(theta, n_qubits, n_layers)
    validation = validate_against_kk_vqe(theta, n_qubits, n_layers)

    print(json.dumps({"validation": validation, "gate_count": len(circuit.gates)}, indent=2))
    print(
        "This is a simulated, simulation-validated gate export only — no "
        "cloud quantum backend was submitted to."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
