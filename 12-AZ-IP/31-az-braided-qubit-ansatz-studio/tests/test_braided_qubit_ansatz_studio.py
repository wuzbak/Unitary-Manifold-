# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
import sys
from pathlib import Path
import subprocess

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import numpy as np
import pytest

from az_braided_qubit_ansatz_studio import (
    build_braided_ansatz_circuit,
    export_openqasm2,
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


@pytest.mark.parametrize(
    ("n_qubits", "n_layers"),
    [(1, 0), (9, 0), (2, -1), (2, 9), (True, 1)],
)
def test_build_rejects_unsupported_or_unbounded_dimensions(n_qubits, n_layers):
    with pytest.raises(ValueError):
        build_braided_ansatz_circuit(np.zeros(6), n_qubits, n_layers)


@pytest.mark.parametrize("bad_angle", [np.nan, np.inf, -np.inf])
def test_build_rejects_nonfinite_parameters(bad_angle):
    with pytest.raises(ValueError, match="finite"):
        build_braided_ansatz_circuit(np.array([bad_angle] * 6), 2, 2)


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


def test_openqasm2_export_contains_portable_register_and_gate_operations():
    theta = np.array([0.25, -0.5, 0.75, 0.0])
    circuit = build_braided_ansatz_circuit(theta, n_qubits=2, n_layers=1)
    qasm = export_openqasm2(circuit)
    assert qasm.startswith('OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[2];\n')
    assert "ry(0.25) q[0];" in qasm
    assert "cx q[0],q[1];" in qasm
    assert not any(line.startswith("measure") for line in qasm.splitlines())


def test_openqasm2_export_rejects_malformed_gate():
    from az_braided_qubit_ansatz_studio import BraidedAnsatzCircuit, Gate

    bad_gates = [
        (Gate("CNOT", (0, 0)), "distinct"),
        (Gate("RY", (2,), 0.1), "outside"),
        (Gate("RY", (0,), "not-an-angle"), "finite"),
        (Gate("RY", (0,), float("inf")), "finite"),
        (Gate("RY", (0, 1), 0.1), "exactly one"),
        (Gate("CNOT", (0,)), "two integer"),
        (Gate("UNKNOWN", (0,)), "unsupported"),
        (object(), "malformed"),
    ]
    for gate, message in bad_gates:
        with pytest.raises(ValueError, match=message):
            export_openqasm2(BraidedAnsatzCircuit(2, 0, [gate]))


def test_openqasm2_export_rejects_malformed_circuit_container():
    from az_braided_qubit_ansatz_studio import BraidedAnsatzCircuit

    with pytest.raises(ValueError, match="list or tuple"):
        export_openqasm2(BraidedAnsatzCircuit(2, 0, None))


def test_cli_exports_openqasm2():
    completed = subprocess.run(
        [
            sys.executable,
            str(PRODUCT_ROOT / "run.py"),
            "export",
            "--n-qubits",
            "2",
            "--n-layers",
            "1",
            "--seed",
            "17",
        ],
        cwd=PRODUCT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.startswith("OPENQASM 2.0;\n")
    assert "qreg q[2];" in completed.stdout
    assert "cx q[0],q[1];" in completed.stdout


def test_cli_exports_user_supplied_angles_and_rejects_implicit_demo():
    script = str(PRODUCT_ROOT / "run.py")
    completed = subprocess.run(
        [
            sys.executable,
            script,
            "export",
            "--n-qubits",
            "2",
            "--n-layers",
            "1",
            "--angles",
            "0.25,-0.5,0.75,0",
        ],
        cwd=PRODUCT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr
    assert "ry(0.25) q[0];" in completed.stdout

    implicit = subprocess.run(
        [sys.executable, script],
        cwd=PRODUCT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert implicit.returncode != 0
    assert "the following arguments are required: command" in implicit.stderr
