# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Hardware-portable gate-list export for the braided-lattice VQE ansatz.

`src/quantum/kk_vqe.ansatz_circuit()` already builds the ansatz as a dense
unitary matrix (Ry layers + a CNOT ladder) — this is fine for a classical
cross-check but is not the representation a real cloud quantum backend
expects. This module expresses the identical gate sequence as an explicit,
JSON-serializable list of single- and two-qubit gates (the representation a
transpiler for IBM Quantum, IonQ, or a comparable backend would consume),
and independently simulates that gate list with a from-scratch statevector
simulator so it can be cross-checked against `ansatz_circuit()`'s dense
matrix without trusting the same code path twice.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import numpy as np

from ._repo import ensure_repo_on_path

ensure_repo_on_path()

from src.quantum.kk_vqe import ansatz_circuit  # noqa: E402

MIN_QUBITS = 2
MAX_QUBITS = 8
MAX_LAYERS = 8


def _validate_dimensions(n_qubits: int, n_layers: int) -> None:
    if type(n_qubits) is not int or not MIN_QUBITS <= n_qubits <= MAX_QUBITS:
        raise ValueError(f"n_qubits must be an integer in {MIN_QUBITS}..{MAX_QUBITS}")
    if type(n_layers) is not int or not 0 <= n_layers <= MAX_LAYERS:
        raise ValueError(f"n_layers must be an integer in 0..{MAX_LAYERS}")


@dataclass(frozen=True)
class Gate:
    """One hardware-portable gate op."""

    name: str  # "RY" or "CNOT"
    qubits: tuple[int, ...]
    theta: float | None = None

    def to_dict(self) -> dict:
        d: dict = {"gate": self.name, "qubits": list(self.qubits)}
        if self.theta is not None:
            d["theta"] = self.theta
        return d


@dataclass(frozen=True)
class BraidedAnsatzCircuit:
    """A complete, exportable braided-lattice VQE ansatz circuit."""

    n_qubits: int
    n_layers: int
    gates: List[Gate] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "n_qubits": self.n_qubits,
            "n_layers": self.n_layers,
            "gates": [g.to_dict() for g in self.gates],
        }


def build_braided_ansatz_circuit(theta: np.ndarray, n_qubits: int, n_layers: int) -> BraidedAnsatzCircuit:
    """Build the explicit hardware-portable gate list for the same
    Ry-layers + CNOT-ladder ansatz that `kk_vqe.ansatz_circuit()` builds as
    a dense matrix.

    Parameter layout matches `kk_vqe.ansatz_circuit`: ``theta`` has
    ``n_qubits * (n_layers + 1)`` entries, one Ry angle per qubit per layer
    (including the final layer).
    """
    _validate_dimensions(n_qubits, n_layers)
    try:
        parameters = np.asarray(theta, dtype=float)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("theta must be a one-dimensional array of finite angles") from exc
    n_params_expected = n_qubits * (n_layers + 1)
    if parameters.ndim != 1 or parameters.size != n_params_expected:
        raise ValueError(
            f"theta has {parameters.size} elements; expected {n_params_expected} "
            f"for n_qubits={n_qubits}, n_layers={n_layers}."
        )
    if not np.all(np.isfinite(parameters)):
        raise ValueError("theta angles must all be finite")

    gates: List[Gate] = []
    for layer in range(n_layers):
        layer_thetas = parameters[layer * n_qubits : (layer + 1) * n_qubits]
        for q, t in enumerate(layer_thetas):
            gates.append(Gate("RY", (q,), float(t)))
        for q in range(n_qubits - 1):
            gates.append(Gate("CNOT", (q, q + 1)))
    final_thetas = parameters[n_layers * n_qubits : (n_layers + 1) * n_qubits]
    for q, t in enumerate(final_thetas):
        gates.append(Gate("RY", (q,), float(t)))

    return BraidedAnsatzCircuit(n_qubits=n_qubits, n_layers=n_layers, gates=gates)


def export_openqasm2(circuit: BraidedAnsatzCircuit) -> str:
    """Export the validated RY/CNOT circuit as an OpenQASM 2.0 input program.

    The output intentionally has no measurements, backend submission, or
    hardware-specific noise/transpilation settings.
    """
    if not isinstance(circuit, BraidedAnsatzCircuit):
        raise ValueError("circuit must be a BraidedAnsatzCircuit")
    _validate_dimensions(circuit.n_qubits, circuit.n_layers)
    if not isinstance(circuit.gates, (list, tuple)):
        raise ValueError("circuit gates must be a list or tuple")
    lines = [
        "OPENQASM 2.0;",
        'include "qelib1.inc";',
        f"qreg q[{circuit.n_qubits}];",
    ]
    for gate in circuit.gates:
        if not isinstance(gate, Gate) or not isinstance(gate.qubits, tuple):
            raise ValueError("circuit contains a malformed gate")
        if gate.name == "RY":
            if len(gate.qubits) != 1 or type(gate.qubits[0]) is not int:
                raise ValueError("RY gate must target exactly one integer qubit")
            (qubit,) = gate.qubits
            if not 0 <= qubit < circuit.n_qubits:
                raise ValueError("RY gate targets a qubit outside the circuit")
            try:
                angle = float(gate.theta)
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError("RY gate angle must be finite") from exc
            if not np.isfinite(angle):
                raise ValueError("RY gate angle must be finite")
            lines.append(f"ry({angle:.17g}) q[{qubit}];")
        elif gate.name == "CNOT":
            if len(gate.qubits) != 2 or any(type(q) is not int for q in gate.qubits):
                raise ValueError("CNOT gate must target two integer qubits")
            control, target = gate.qubits
            if (
                not 0 <= control < circuit.n_qubits
                or not 0 <= target < circuit.n_qubits
                or control == target
            ):
                raise ValueError("CNOT qubits must be distinct and inside the circuit")
            lines.append(f"cx q[{control}],q[{target}];")
        else:
            raise ValueError(f"unsupported gate: {gate.name}")
    return "\n".join(lines) + "\n"


def _ry(theta: float) -> np.ndarray:
    c, s = np.cos(theta / 2.0), np.sin(theta / 2.0)
    return np.array([[c, -s], [s, c]], dtype=complex)


def simulate_circuit(circuit: BraidedAnsatzCircuit) -> np.ndarray:
    """Independent from-scratch statevector simulator for the exported gate
    list. Deliberately avoids reusing `kk_vqe`'s matrix-construction code,
    so that agreement with `ansatz_circuit()` is a real cross-check."""
    export_openqasm2(circuit)
    n = circuit.n_qubits
    dim = 2**n
    state = np.zeros(dim, dtype=complex)
    state[0] = 1.0

    for gate in circuit.gates:
        if gate.name == "RY":
            (q,) = gate.qubits
            state = _apply_single_qubit_gate(state, n, q, _ry(gate.theta))
        elif gate.name == "CNOT":
            control, target = gate.qubits
            state = _apply_cnot(state, n, control, target)
        else:
            raise ValueError(f"unsupported gate: {gate.name}")
    return state


def _apply_single_qubit_gate(state: np.ndarray, n: int, qubit: int, mat: np.ndarray) -> np.ndarray:
    dim = 2**n
    new_state = np.zeros(dim, dtype=complex)
    bit = qubit  # ansatz_circuit's basis ordering has qubit 0 as the least-significant bit
    for i in range(dim):
        bit_val = (i >> bit) & 1
        amp = state[i]
        if amp == 0:
            continue
        for new_bit_val in (0, 1):
            coeff = mat[new_bit_val, bit_val]
            if coeff == 0:
                continue
            j = i ^ ((bit_val ^ new_bit_val) << bit)
            new_state[j] += coeff * amp
    return new_state


def _apply_cnot(state: np.ndarray, n: int, control: int, target: int) -> np.ndarray:
    dim = 2**n
    new_state = np.zeros(dim, dtype=complex)
    c_bit = control
    t_bit = target
    for i in range(dim):
        amp = state[i]
        if amp == 0:
            continue
        if (i >> c_bit) & 1:
            j = i ^ (1 << t_bit)
        else:
            j = i
        new_state[j] += amp
    return new_state


def validate_against_kk_vqe(theta: np.ndarray, n_qubits: int, n_layers: int, atol: float = 1e-9) -> dict:
    """Build the exportable gate list, simulate it independently, and
    confirm it reproduces the state `kk_vqe.ansatz_circuit()` predicts for
    the same parameters (applied to the |0...0> initial state)."""
    circuit = build_braided_ansatz_circuit(theta, n_qubits, n_layers)
    exported_state = simulate_circuit(circuit)

    reference_unitary = ansatz_circuit(theta, n_qubits, n_layers)
    reference_state = reference_unitary[:, 0]

    max_abs_diff = float(np.max(np.abs(exported_state - reference_state)))
    return {
        "n_qubits": n_qubits,
        "n_layers": n_layers,
        "n_gates": len(circuit.gates),
        "max_abs_diff": max_abs_diff,
        "matches_kk_vqe": max_abs_diff <= atol,
    }
