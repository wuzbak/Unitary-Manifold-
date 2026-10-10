# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import numpy as np
import pytest

from az_braided_qubit_ansatz_studio import (
    build_braided_ansatz_circuit,
    simulate_circuit,
    validate_against_kk_vqe,
)


def test_build_braided_ansatz_circuit_gate_count():
    theta = np.zeros(3 * 3)
    circuit = build_braided_ansatz_circuit(theta, n_qubits=3, n_layers=2)
    # 2 layers * (3 RY + 2 CNOT) + final 3 RY = 2*5 + 3 = 13
    assert len(circuit.gates) == 13
    assert circuit.to_dict()["n_qubits"] == 3


def test_build_braided_ansatz_circuit_rejects_wrong_param_count():
    with pytest.raises(ValueError):
        build_braided_ansatz_circuit(np.zeros(5), n_qubits=3, n_layers=2)


def test_simulate_circuit_identity_for_zero_angles_is_ground_state():
    theta = np.zeros(2 * 3)
    circuit = build_braided_ansatz_circuit(theta, n_qubits=2, n_layers=2)
    state = simulate_circuit(circuit)
    assert state[0] == pytest.approx(1.0)
    assert np.sum(np.abs(state) ** 2) == pytest.approx(1.0)


@pytest.mark.parametrize("n_qubits", [2, 3, 4, 5])
def test_validate_against_kk_vqe_matches_reference_implementation(n_qubits):
    rng = np.random.default_rng(n_qubits)
    theta = rng.uniform(-np.pi, np.pi, size=n_qubits * 3)
    result = validate_against_kk_vqe(theta, n_qubits, n_layers=2)
    assert result["matches_kk_vqe"] is True
    assert result["max_abs_diff"] < 1e-9


def test_validate_against_kk_vqe_eight_qubit_braided_lattice_instance():
    rng = np.random.default_rng(8)
    theta = rng.uniform(-np.pi, np.pi, size=8 * 3)
    result = validate_against_kk_vqe(theta, n_qubits=8, n_layers=2)
    assert result["n_qubits"] == 8
    assert result["matches_kk_vqe"] is True


def test_gate_to_dict_includes_theta_for_ry_only():
    theta = np.array([0.1, 0.2, 0.3])
    circuit = build_braided_ansatz_circuit(theta, n_qubits=3, n_layers=0)
    assert all("theta" in g.to_dict() for g in circuit.gates)
