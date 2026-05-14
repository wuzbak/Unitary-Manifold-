# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/quantum/fermion_mapping.py
==============================
Jordan–Wigner and Bravyi–Kitaev mapping pipeline for fermionic operators.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Literal

import numpy as np

from .fermi_hubbard import FermionTerm

MappingName = Literal["jw", "bk"]
# Exact BK decomposition scales exponentially; keep parity-verification lane bounded.
BK_EXACT_MODE_LIMIT = 6


PAULI_MATS: dict[str, np.ndarray] = {
    "I": np.array([[1, 0], [0, 1]], dtype=complex),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
}


@dataclass(frozen=True)
class PauliTerm:
    coefficient: complex
    ops: tuple[tuple[int, str], ...]


def _normalise_ops(ops: dict[int, str]) -> tuple[tuple[int, str], ...]:
    return tuple(sorted((q, p) for q, p in ops.items() if p != "I"))


def _pauli_mul(a: str, b: str) -> tuple[complex, str]:
    if a == "I":
        return 1.0 + 0.0j, b
    if b == "I":
        return 1.0 + 0.0j, a
    if a == b:
        return 1.0 + 0.0j, "I"

    table: dict[tuple[str, str], tuple[complex, str]] = {
        ("X", "Y"): (1j, "Z"),
        ("Y", "X"): (-1j, "Z"),
        ("Y", "Z"): (1j, "X"),
        ("Z", "Y"): (-1j, "X"),
        ("Z", "X"): (1j, "Y"),
        ("X", "Z"): (-1j, "Y"),
    }
    return table[(a, b)]


def multiply_pauli_terms(a: PauliTerm, b: PauliTerm) -> PauliTerm:
    ops: dict[int, str] = {q: p for q, p in a.ops}
    coeff = a.coefficient * b.coefficient
    for q, pb in b.ops:
        pa = ops.get(q, "I")
        phase, pnew = _pauli_mul(pa, pb)
        coeff *= phase
        if pnew == "I":
            ops.pop(q, None)
        else:
            ops[q] = pnew
    return PauliTerm(coeff, _normalise_ops(ops))


def simplify_pauli_sum(terms: list[PauliTerm], tol: float = 1e-12) -> list[PauliTerm]:
    merged: dict[tuple[tuple[int, str], ...], complex] = {}
    for t in terms:
        merged[t.ops] = merged.get(t.ops, 0.0 + 0.0j) + t.coefficient
    out = [PauliTerm(c, ops) for ops, c in merged.items() if abs(c) > tol]
    out.sort(key=lambda x: (len(x.ops), x.ops))
    return out


def _jw_ladder(mode: int, creation: bool) -> list[PauliTerm]:
    z_string = tuple((q, "Z") for q in range(mode))
    x_ops = _normalise_ops({**dict(z_string), mode: "X"})
    y_ops = _normalise_ops({**dict(z_string), mode: "Y"})
    if creation:
        return [PauliTerm(0.5, x_ops), PauliTerm(-0.5j, y_ops)]
    return [PauliTerm(0.5, x_ops), PauliTerm(0.5j, y_ops)]


def fermion_term_to_jw(term: FermionTerm) -> list[PauliTerm]:
    current = [PauliTerm(1.0 + 0.0j, tuple())]
    for mode, creation in term.operators:
        mapped = _jw_ladder(mode, creation)
        nxt: list[PauliTerm] = []
        for base in current:
            for op in mapped:
                nxt.append(multiply_pauli_terms(base, op))
        current = simplify_pauli_sum(nxt)
    current = [PauliTerm(term.coefficient * c.coefficient, c.ops) for c in current]
    return simplify_pauli_sum(current)


def fermion_term_matrix(term: FermionTerm, n_modes: int) -> np.ndarray:
    dim = 2**n_modes
    mat = np.zeros((dim, dim), dtype=complex)

    def apply_op(state: int, mode: int, creation: bool) -> tuple[complex, int] | None:
        occ = (state >> mode) & 1
        if creation and occ:
            return None
        if (not creation) and (not occ):
            return None
        lower = state & ((1 << mode) - 1)
        sign = -1.0 if (lower.bit_count() % 2) else 1.0
        if creation:
            new_state = state | (1 << mode)
        else:
            new_state = state & ~(1 << mode)
        return sign + 0.0j, new_state

    for ket in range(dim):
        coeff = term.coefficient + 0.0j
        state = ket
        valid = True
        for mode, creation in reversed(term.operators):
            out = apply_op(state, mode, creation)
            if out is None:
                valid = False
                break
            phase, state = out
            coeff *= phase
        if valid:
            mat[state, ket] += coeff
    return mat


def occupation_to_bk_index(occ_index: int, n_modes: int) -> int:
    occ = [(occ_index >> i) & 1 for i in range(n_modes)]
    bk = [0] * n_modes
    for k in range(n_modes):
        i1 = k + 1
        lsb = i1 & -i1
        start = i1 - lsb
        parity = 0
        for j in range(start, i1):
            parity ^= occ[j]
        bk[k] = parity
    out = 0
    for i, bit in enumerate(bk):
        out |= (bit & 1) << i
    return out


def _perm_occ_to_bk(n_modes: int) -> tuple[np.ndarray, np.ndarray]:
    dim = 2**n_modes
    p = np.array([occupation_to_bk_index(i, n_modes) for i in range(dim)], dtype=int)
    q = np.argsort(p)
    return p, q


def bk_basis_permutations(n_modes: int) -> tuple[np.ndarray, np.ndarray]:
    """Return occupancy↔BK basis permutation indices.

    Returns
    -------
    (occ_to_bk, bk_to_occ):
        - occ_to_bk[i_occ] = i_bk
        - bk_to_occ[i_bk] = i_occ
    """
    occ_to_bk, bk_to_occ = _perm_occ_to_bk(n_modes)
    return occ_to_bk, bk_to_occ


def matrix_to_pauli_terms(matrix: np.ndarray, n_qubits: int, tol: float = 1e-10) -> list[PauliTerm]:
    terms: list[PauliTerm] = []
    dim = 2**n_qubits
    norm = float(dim)

    for letters in product("IXYZ", repeat=n_qubits):
        p = PAULI_MATS[letters[0]]
        for c in letters[1:]:
            p = np.kron(p, PAULI_MATS[c])
        coeff = np.trace(p.conj().T @ matrix) / norm
        if abs(coeff) > tol:
            ops = tuple((q, letters[n_qubits - 1 - q]) for q in range(n_qubits) if letters[n_qubits - 1 - q] != "I")
            terms.append(PauliTerm(complex(coeff), ops))
    return simplify_pauli_sum(terms, tol=tol)


def fermion_term_to_bk(
    term: FermionTerm,
    n_modes: int,
    max_exact_modes: int = BK_EXACT_MODE_LIMIT,
) -> list[PauliTerm]:
    if n_modes > max_exact_modes:
        raise ValueError(
            f"BK exact mapping currently supports n_modes <= {max_exact_modes}; "
            "use JW mapping for larger-scale runs."
        )
    _, q = _perm_occ_to_bk(n_modes)
    occ_matrix = fermion_term_matrix(term, n_modes)
    bk_matrix = occ_matrix[np.ix_(q, q)]
    return matrix_to_pauli_terms(bk_matrix, n_qubits=n_modes)


def fermion_terms_to_qubit_terms(
    terms: list[FermionTerm],
    n_modes: int,
    mapping: MappingName = "jw",
) -> list[PauliTerm]:
    out: list[PauliTerm] = []
    for term in terms:
        if mapping == "jw":
            out.extend(fermion_term_to_jw(term))
        elif mapping == "bk":
            out.extend(fermion_term_to_bk(term, n_modes=n_modes))
        else:
            raise ValueError(f"Unknown mapping: {mapping}")
    return simplify_pauli_sum(out)


def pauli_terms_to_matrix(terms: list[PauliTerm], n_qubits: int) -> np.ndarray:
    dim = 2**n_qubits
    mat = np.zeros((dim, dim), dtype=complex)
    for term in terms:
        op = np.eye(dim, dtype=complex)
        for q in range(n_qubits):
            p = next((pp for qq, pp in term.ops if qq == q), "I")
            kron_part = PAULI_MATS[p]
            op = kron_part if q == 0 else np.kron(kron_part, op)
        mat += term.coefficient * op
    return mat
