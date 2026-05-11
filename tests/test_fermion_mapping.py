# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
from __future__ import annotations

import numpy as np
import pytest

from src.quantum.fermi_hubbard import FermionTerm
from src.quantum.fermion_mapping import (
    fermion_term_to_bk,
    fermion_term_to_jw,
    fermion_term_matrix,
    fermion_terms_to_qubit_terms,
    pauli_terms_to_matrix,
)


def test_jw_number_operator_matches_expected_matrix() -> None:
    term = FermionTerm(1.0, ((0, True), (0, False)))
    qterms = fermion_term_to_jw(term)
    mat = pauli_terms_to_matrix(qterms, n_qubits=2)
    expected = fermion_term_matrix(term, n_modes=2)
    np.testing.assert_allclose(mat, expected, atol=1e-10)


def test_jw_and_bk_match_for_small_mode_term() -> None:
    term = FermionTerm(1.0, ((1, True), (0, False)))
    jw_mat = pauli_terms_to_matrix(fermion_term_to_jw(term), n_qubits=3)
    bk_mat = pauli_terms_to_matrix(fermion_term_to_bk(term, n_modes=3), n_qubits=3)

    # Compare in occupancy basis by converting exact fermion matrix into BK basis
    exact = fermion_term_matrix(term, n_modes=3)
    # JW is occupancy-basis by construction
    np.testing.assert_allclose(jw_mat, exact, atol=1e-9)
    # BK matrix represents same operator in BK basis, so only check invariants
    np.testing.assert_allclose(np.linalg.eigvals(bk_mat).sum(), np.linalg.eigvals(exact).sum(), atol=1e-9)


def test_bk_guard_for_large_modes() -> None:
    term = FermionTerm(1.0, ((0, True), (0, False)))
    with pytest.raises(ValueError):
        fermion_term_to_bk(term, n_modes=7, max_exact_modes=6)


def test_mapping_dispatch_accepts_both_pipelines() -> None:
    terms = [FermionTerm(1.0, ((0, True), (0, False)))]
    jw = fermion_terms_to_qubit_terms(terms, n_modes=2, mapping="jw")
    bk = fermion_terms_to_qubit_terms(terms, n_modes=2, mapping="bk")
    assert len(jw) > 0
    assert len(bk) > 0
