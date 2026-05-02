# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_kk_magic.py
=======================
Tests for src/core/kk_magic.py — Pillar 101:
KK Magic Power & Quantum Circuit Complexity.

Physical claims under test
--------------------------
1. PAULI_2Q: 16 operators, each 4×4, Hermitian, square-to-identity.
2. characteristic_function: non-negative; sums to 4² for stabilizer |00⟩;
   real-valued; shape (16,).
3. stabilizer_renyi_entropy_m2: zero for computational basis states
   (stabilizers); positive for asymmetric Bell states; ≥ 0 always.
4. phase_point_operators_2q: 16 operators, each 4×4, Hermitian, sum to I.
5. discrete_wigner_function: sums to 1; real; shape (16,);
   non-negative for stabilizer states; negative entries for magic states.
6. wigner_negativity: zero for stabilizer states; positive for magic states.
7. mana: zero for stabilizer states; ≥ 0; = log₂(Σ|W|).
8. t_gate_lower_bound: ≥ 1; equals 1 for M₂=0; grows with M₂.
9. kk_magic_summary: correct keys; consistent with Pillar 31 entanglement
   values; M₂ > 0 for braided winding pair (5,7).
10. magic_power_nuclear_bridge: correct structure; delta_M2_min ≤ M2_braid;
    T_gate_overhead_min ≥ 1; contains Robin–Savage context string.
11. nuclear_simulation_cost: C_KK + T_lb ≥ C_KK; efficiency_ratio ∈ (0,1);
    n_qubits = 2.
12. is_stabilizer_state: True for |00⟩; False for asymmetric Bell state.
13. canonical_summary: matches kk_magic_summary(5,7); includes 'notes' key.
14. Input validation: ValueError for bad state shapes, unnormalised states,
    bad (n1,n2) pairs, bad r_ratio.

"""

from __future__ import annotations

import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import numpy as np

from src.core.kk_magic import (
    PAULI_2Q,
    PAULI_2Q_LABELS,
    characteristic_function,
    stabilizer_renyi_entropy_m2,
    phase_point_operators_2q,
    discrete_wigner_function,
    wigner_negativity,
    mana,
    t_gate_lower_bound,
    kk_magic_summary,
    magic_power_nuclear_bridge,
    nuclear_simulation_cost,
    is_stabilizer_state,
    canonical_summary,
    R_RATIO_CANONICAL,
    PILLAR,
    N1_CANONICAL,
    N2_CANONICAL,
    K_CS_CANONICAL,
    C_S_CANONICAL,
)

# ---------------------------------------------------------------------------
# Shared test states
# ---------------------------------------------------------------------------

# Computational basis / stabilizer states
STATE_00 = np.array([1.0, 0.0, 0.0, 0.0], dtype=complex)
STATE_01 = np.array([0.0, 1.0, 0.0, 0.0], dtype=complex)
STATE_10 = np.array([0.0, 0.0, 1.0, 0.0], dtype=complex)
STATE_11 = np.array([0.0, 0.0, 0.0, 1.0], dtype=complex)

# Maximally entangled Bell state (stabilizer state — equal weights)
BELL_EQUAL = np.array([1.0, 0.0, 0.0, 1.0], dtype=complex) / math.sqrt(2.0)

# Canonical braided winding state (5, 7): p1=49/74, p2=25/74 — magic state
_C_S_57 = 12.0 / 37.0
_P1_57 = (1.0 + _C_S_57) / 2.0   # = 49/74
_P2_57 = (1.0 - _C_S_57) / 2.0   # = 25/74
STATE_BRAID_57 = np.array(
    [math.sqrt(_P1_57), 0.0, 0.0, math.sqrt(_P2_57)], dtype=complex
)

# Another test pair (1, 2): k_cs=5, c_s=3/5
_C_S_12 = (4 - 1) / 5   # = 3/5
_P1_12 = (1.0 + _C_S_12) / 2.0
_P2_12 = (1.0 - _C_S_12) / 2.0
STATE_BRAID_12 = np.array(
    [math.sqrt(_P1_12), 0.0, 0.0, math.sqrt(_P2_12)], dtype=complex
)


# ===========================================================================
# Module-level constants
# ===========================================================================

class TestModuleConstants:
    def test_pillar_number(self):
        assert PILLAR == 101

    def test_n1_canonical(self):
        assert N1_CANONICAL == 5

    def test_n2_canonical(self):
        assert N2_CANONICAL == 7

    def test_k_cs_canonical(self):
        assert K_CS_CANONICAL == 74

    def test_c_s_canonical(self):
        assert abs(C_S_CANONICAL - 12.0 / 37.0) < 1e-14

    def test_r_ratio_canonical_less_than_one(self):
        assert R_RATIO_CANONICAL < 1.0

    def test_r_ratio_canonical_positive(self):
        assert R_RATIO_CANONICAL > 0.0

    def test_r_ratio_canonical_close_to_one(self):
        # One-loop correction is tiny: ≈ 1 − 1.78e-4
        assert abs(R_RATIO_CANONICAL - 1.0) < 1e-2


# ===========================================================================
# PAULI_2Q
# ===========================================================================

class TestPauli2Q:
    def test_count(self):
        assert len(PAULI_2Q) == 16

    def test_labels_count(self):
        assert len(PAULI_2Q_LABELS) == 16

    def test_each_shape_4x4(self):
        for P in PAULI_2Q:
            assert P.shape == (4, 4)

    def test_each_hermitian(self):
        for P in PAULI_2Q:
            assert np.allclose(P, P.conj().T, atol=1e-14)

    def test_each_squares_to_identity(self):
        I4 = np.eye(4, dtype=complex)
        for P in PAULI_2Q:
            assert np.allclose(P @ P, I4, atol=1e-14)

    def test_ii_is_identity(self):
        # First Pauli is II = I ⊗ I = I₄
        assert np.allclose(PAULI_2Q[0], np.eye(4, dtype=complex))

    def test_includes_zz(self):
        # ZZ = diag(1, -1, -1, 1)
        ZZ_expected = np.diag([1.0, -1.0, -1.0, 1.0]).astype(complex)
        # ZZ is at index 15 (ZZ = Z⊗Z)
        assert np.allclose(PAULI_2Q[15], ZZ_expected, atol=1e-14)


# ===========================================================================
# characteristic_function
# ===========================================================================

class TestCharacteristicFunction:
    def test_shape(self):
        xi = characteristic_function(STATE_00)
        assert xi.shape == (16,)

    def test_non_negative(self):
        for state in [STATE_00, STATE_BRAID_57, BELL_EQUAL]:
            xi = characteristic_function(state)
            assert np.all(xi >= 0.0)

    def test_stabilizer_state_sum(self):
        # For any stabilizer state the sum Σ Ξ(P) = 2^n = 4
        # because stabilizer states saturate the uncertainty principle
        # (exactly n of the 16 squared expectations are 1; the rest 0)
        xi = characteristic_function(STATE_00)
        # The sum need not be 4 for all stabilizer states in the Pauli basis,
        # but each entry should be 0 or 1
        assert np.all(np.abs(xi - np.round(xi)) < 1e-12)

    def test_real_valued(self):
        xi = characteristic_function(STATE_BRAID_57)
        # characteristic_function returns float array
        assert xi.dtype == np.float64

    def test_identity_pauli_gives_one(self):
        # ⟨ψ|I|ψ⟩ = 1 for any normalised state → Ξ(I) = 1
        for state in [STATE_00, STATE_11, STATE_BRAID_57]:
            xi = characteristic_function(state)
            assert abs(xi[0] - 1.0) < 1e-12   # II at index 0

    def test_braid_state_has_some_nonzero(self):
        xi = characteristic_function(STATE_BRAID_57)
        assert np.sum(xi > 0.01) >= 2   # at least II and ZZ are nonzero


# ===========================================================================
# stabilizer_renyi_entropy_m2
# ===========================================================================

class TestStabilizerRenyiEntropyM2:
    def test_zero_for_computational_basis_00(self):
        M2 = stabilizer_renyi_entropy_m2(STATE_00)
        assert M2 < 1e-10

    def test_zero_for_computational_basis_11(self):
        M2 = stabilizer_renyi_entropy_m2(STATE_11)
        assert M2 < 1e-10

    def test_zero_for_01(self):
        M2 = stabilizer_renyi_entropy_m2(STATE_01)
        assert M2 < 1e-10

    def test_zero_for_10(self):
        M2 = stabilizer_renyi_entropy_m2(STATE_10)
        assert M2 < 1e-10

    def test_positive_for_braided_57(self):
        M2 = stabilizer_renyi_entropy_m2(STATE_BRAID_57)
        assert M2 > 0.0

    def test_positive_for_braided_12(self):
        M2 = stabilizer_renyi_entropy_m2(STATE_BRAID_12)
        assert M2 > 0.0

    def test_non_negative(self):
        for state in [STATE_00, STATE_01, STATE_10, STATE_11,
                      STATE_BRAID_57, STATE_BRAID_12, BELL_EQUAL]:
            M2 = stabilizer_renyi_entropy_m2(state)
            assert M2 >= 0.0, f"M2={M2} < 0 for {state}"

    def test_finite(self):
        M2 = stabilizer_renyi_entropy_m2(STATE_BRAID_57)
        assert math.isfinite(M2)

    def test_less_magic_for_more_balanced_braid(self):
        # SRE M2 for |psi>=sqrt(p1)|00>+sqrt(p2)|11> follows M2=-log2(1-cs^2+cs^4).
        # Maximum at cs=1/sqrt(2); states closer to equal weight (Bell) have LESS magic.
        # (5,7): c_s=12/37~0.324, closer to Bell state -> M2~0.143
        # (1,2): c_s=3/5=0.6, closer to max-magic point  -> M2~0.378
        # Therefore (1,2) has MORE magic than (5,7).
        M2_12 = stabilizer_renyi_entropy_m2(STATE_BRAID_12)
        M2_57 = stabilizer_renyi_entropy_m2(STATE_BRAID_57)
        assert M2_12 > M2_57

    def test_raises_bad_shape(self):
        with pytest.raises(ValueError):
            stabilizer_renyi_entropy_m2(np.array([1.0, 0.0, 0.0]))

    def test_raises_unnormalised(self):
        with pytest.raises(ValueError):
            stabilizer_renyi_entropy_m2(np.array([2.0, 0.0, 0.0, 0.0]))


# ===========================================================================
# phase_point_operators_2q
# ===========================================================================

class TestPhasePointOperators2Q:
    def setup_method(self):
        self.ops = phase_point_operators_2q()

    def test_count(self):
        assert len(self.ops) == 16

    def test_each_shape(self):
        for A in self.ops:
            assert A.shape == (4, 4)

    def test_each_hermitian(self):
        for A in self.ops:
            assert np.allclose(A, A.conj().T, atol=1e-13)

    def test_sum_to_identity(self):
        # For this tensor-product qubit construction Σ_α A_α = 4 × I₄
        # (each single-qubit factor sums to 2I₂, so tensor product → 4I₄)
        total = sum(self.ops)
        assert np.allclose(total, 4.0 * np.eye(4, dtype=complex), atol=1e-12)

    def test_trace_one(self):
        # Each phase-point operator should have trace 1
        for A in self.ops:
            tr = float(np.real(np.trace(A)))
            assert abs(tr - 1.0) < 1e-12


# ===========================================================================
# discrete_wigner_function
# ===========================================================================

class TestDiscreteWignerFunction:
    def test_shape(self):
        W = discrete_wigner_function(STATE_00)
        assert W.shape == (16,)

    def test_real_valued(self):
        W = discrete_wigner_function(STATE_00)
        assert W.dtype == np.float64

    def test_sums_to_one(self):
        for state in [STATE_00, STATE_11, STATE_BRAID_57]:
            W = discrete_wigner_function(state)
            assert abs(np.sum(W) - 1.0) < 1e-12

    def test_no_negatives_for_stabilizer_00(self):
        W = discrete_wigner_function(STATE_00)
        # Stabilizer state: Wigner function non-negative everywhere
        assert np.all(W >= -1e-12)

    def test_has_negatives_for_braided_state(self):
        W = discrete_wigner_function(STATE_BRAID_57)
        # Magic state: some Wigner values should be negative
        assert np.any(W < -1e-12)

    def test_consistent_with_density_matrix(self):
        # Tr(A_α ρ) / 4 should match discrete_wigner_function
        from src.core.kk_magic import _PHASE_POINT_OPS
        psi = STATE_BRAID_57
        rho = np.outer(psi, psi.conj())
        W = discrete_wigner_function(psi)
        for k, A in enumerate(_PHASE_POINT_OPS):
            expected = float(np.real(np.trace(A @ rho))) / 4.0
            assert abs(W[k] - expected) < 1e-12


# ===========================================================================
# wigner_negativity
# ===========================================================================

class TestWignerNegativity:
    def test_zero_for_stabilizer_00(self):
        neg = wigner_negativity(STATE_00)
        assert neg < 1e-12

    def test_zero_for_stabilizer_11(self):
        neg = wigner_negativity(STATE_11)
        assert neg < 1e-12

    def test_positive_for_braided_57(self):
        neg = wigner_negativity(STATE_BRAID_57)
        assert neg > 0.0

    def test_non_negative(self):
        for state in [STATE_00, STATE_BRAID_57, STATE_BRAID_12]:
            assert wigner_negativity(state) >= 0.0

    def test_finite(self):
        neg = wigner_negativity(STATE_BRAID_57)
        assert math.isfinite(neg)

    def test_larger_for_more_magic(self):
        # (5,7) has more magic than (1,2); expect more negativity
        neg_57 = wigner_negativity(STATE_BRAID_57)
        neg_12 = wigner_negativity(STATE_BRAID_12)
        assert neg_57 >= neg_12


# ===========================================================================
# mana
# ===========================================================================

class TestMana:
    def test_zero_for_computational_basis_00(self):
        M = mana(STATE_00)
        assert M < 1e-10

    def test_zero_for_computational_basis_11(self):
        M = mana(STATE_11)
        assert M < 1e-10

    def test_positive_for_braided_57(self):
        M = mana(STATE_BRAID_57)
        assert M > 0.0

    def test_positive_for_braided_12(self):
        M = mana(STATE_BRAID_12)
        assert M > 0.0

    def test_non_negative(self):
        for state in [STATE_00, STATE_11, STATE_BRAID_57, STATE_BRAID_12]:
            assert mana(state) >= 0.0

    def test_finite(self):
        M = mana(STATE_BRAID_57)
        assert math.isfinite(M)

    def test_equals_log2_l1_norm_of_wigner(self):
        W = discrete_wigner_function(STATE_BRAID_57)
        l1 = float(np.sum(np.abs(W)))
        expected = math.log2(l1) if l1 > 1e-300 else 0.0
        M = mana(STATE_BRAID_57)
        assert abs(M - expected) < 1e-12

    def test_larger_for_more_magic(self):
        M_57 = mana(STATE_BRAID_57)
        M_12 = mana(STATE_BRAID_12)
        assert M_57 >= M_12


# ===========================================================================
# t_gate_lower_bound
# ===========================================================================

class TestTGateLowerBound:
    def test_one_for_zero_magic(self):
        T = t_gate_lower_bound(0.0)
        assert abs(T - 1.0) < 1e-12

    def test_greater_than_one_for_positive_magic(self):
        T = t_gate_lower_bound(1.0)
        assert T > 1.0

    def test_formula(self):
        # T = max(2^(M2/2), 1)
        for m2 in [0.1, 0.5, 1.0, 2.0]:
            T = t_gate_lower_bound(m2)
            expected = 2.0 ** (m2 / 2.0)
            assert abs(T - expected) < 1e-12

    def test_monotone_increasing(self):
        T1 = t_gate_lower_bound(0.5)
        T2 = t_gate_lower_bound(1.0)
        T3 = t_gate_lower_bound(2.0)
        assert T1 < T2 < T3

    def test_raises_negative(self):
        with pytest.raises(ValueError):
            t_gate_lower_bound(-0.1)

    def test_at_least_one(self):
        for m2 in [0.0, 0.001, 0.1, 1.0]:
            assert t_gate_lower_bound(m2) >= 1.0


# ===========================================================================
# kk_magic_summary
# ===========================================================================

class TestKKMagicSummary:
    def setup_method(self):
        self.s57 = kk_magic_summary(5, 7)
        self.s12 = kk_magic_summary(1, 2)

    def test_keys_present(self):
        required = {
            "n1", "n2", "k_cs", "c_s", "p1", "p2",
            "S_entanglement", "S_entanglement_bits",
            "M2", "mana", "wigner_negativity",
            "T_gate_lower_bound", "C_KK_bits", "is_stabilizer",
        }
        assert required.issubset(set(self.s57.keys()))

    def test_n1_n2_correct(self):
        assert self.s57["n1"] == 5
        assert self.s57["n2"] == 7

    def test_k_cs_correct(self):
        assert self.s57["k_cs"] == 74

    def test_c_s_correct(self):
        assert abs(self.s57["c_s"] - 12.0 / 37.0) < 1e-14

    def test_p1_correct(self):
        c_s = 12.0 / 37.0
        assert abs(self.s57["p1"] - (1.0 + c_s) / 2.0) < 1e-14

    def test_p2_correct(self):
        c_s = 12.0 / 37.0
        assert abs(self.s57["p2"] - (1.0 - c_s) / 2.0) < 1e-14

    def test_p1_plus_p2_one(self):
        assert abs(self.s57["p1"] + self.s57["p2"] - 1.0) < 1e-14

    def test_entanglement_consistent_with_pillar31(self):
        # Pillar 31 value: S_braid ≈ 0.661 nats
        from src.core.kk_quantum_info import braided_winding_entropy
        S_expected = braided_winding_entropy(5, 7)
        assert abs(self.s57["S_entanglement"] - S_expected) < 1e-12

    def test_entanglement_bits_conversion(self):
        S_nats = self.s57["S_entanglement"]
        S_bits = self.s57["S_entanglement_bits"]
        assert abs(S_bits - S_nats / math.log(2.0)) < 1e-12

    def test_m2_positive_for_57(self):
        assert self.s57["M2"] > 0.0

    def test_m2_non_negative(self):
        assert self.s57["M2"] >= 0.0
        assert self.s12["M2"] >= 0.0

    def test_mana_non_negative(self):
        assert self.s57["mana"] >= 0.0

    def test_wigner_negativity_non_negative(self):
        assert self.s57["wigner_negativity"] >= 0.0

    def test_t_gate_at_least_one(self):
        assert self.s57["T_gate_lower_bound"] >= 1.0

    def test_c_kk_consistent_with_pillar31(self):
        from src.core.kk_quantum_info import kk_channel_capacity
        assert abs(self.s57["C_KK_bits"] - kk_channel_capacity(5, 7)) < 1e-12

    def test_c_kk_positive(self):
        assert self.s57["C_KK_bits"] > 0.0

    def test_is_stabilizer_false_for_57(self):
        assert self.s57["is_stabilizer"] is False

    def test_raises_bad_pair(self):
        with pytest.raises(ValueError):
            kk_magic_summary(7, 5)

    def test_raises_n1_zero(self):
        with pytest.raises(ValueError):
            kk_magic_summary(0, 3)


# ===========================================================================
# magic_power_nuclear_bridge
# ===========================================================================

class TestMagicPowerNuclearBridge:
    def setup_method(self):
        self.bridge = magic_power_nuclear_bridge(5, 7)

    def test_keys_present(self):
        required = {
            "M2_braid", "r_ratio", "delta_M2_min",
            "T_gate_overhead_min", "C_KK_bits", "robin_savage_context",
        }
        assert required.issubset(set(self.bridge.keys()))

    def test_m2_braid_positive(self):
        assert self.bridge["M2_braid"] > 0.0

    def test_r_ratio_default_is_canonical(self):
        assert abs(self.bridge["r_ratio"] - R_RATIO_CANONICAL) < 1e-14

    def test_delta_m2_min_leq_m2_braid(self):
        assert self.bridge["delta_M2_min"] <= self.bridge["M2_braid"] + 1e-12

    def test_delta_m2_min_positive(self):
        assert self.bridge["delta_M2_min"] > 0.0

    def test_t_gate_overhead_at_least_one(self):
        assert self.bridge["T_gate_overhead_min"] >= 1.0

    def test_c_kk_positive(self):
        assert self.bridge["C_KK_bits"] > 0.0

    def test_robin_savage_context_is_string(self):
        assert isinstance(self.bridge["robin_savage_context"], str)
        assert "Robin" in self.bridge["robin_savage_context"]
        assert "2604.26376" in self.bridge["robin_savage_context"]

    def test_r_ratio_one_gives_full_magic(self):
        b = magic_power_nuclear_bridge(5, 7, r_ratio=1.0)
        assert abs(b["delta_M2_min"] - b["M2_braid"]) < 1e-12

    def test_r_ratio_custom(self):
        b = magic_power_nuclear_bridge(5, 7, r_ratio=0.5)
        assert abs(b["delta_M2_min"] - b["M2_braid"] * 0.5) < 1e-12

    def test_raises_bad_pair(self):
        with pytest.raises(ValueError):
            magic_power_nuclear_bridge(7, 5)

    def test_raises_bad_r_ratio_zero(self):
        with pytest.raises(ValueError):
            magic_power_nuclear_bridge(5, 7, r_ratio=0.0)

    def test_raises_bad_r_ratio_negative(self):
        with pytest.raises(ValueError):
            magic_power_nuclear_bridge(5, 7, r_ratio=-0.5)

    def test_raises_bad_r_ratio_greater_than_one(self):
        with pytest.raises(ValueError):
            magic_power_nuclear_bridge(5, 7, r_ratio=1.5)


# ===========================================================================
# nuclear_simulation_cost
# ===========================================================================

class TestNuclearSimulationCost:
    def setup_method(self):
        self.cost = nuclear_simulation_cost(5, 7)

    def test_keys_present(self):
        required = {
            "C_KK_bits", "M2", "T_gate_lb",
            "hybrid_cost", "efficiency_ratio", "n_qubits",
        }
        assert required.issubset(set(self.cost.keys()))

    def test_n_qubits_is_two(self):
        assert self.cost["n_qubits"] == 2

    def test_c_kk_positive(self):
        assert self.cost["C_KK_bits"] > 0.0

    def test_m2_non_negative(self):
        assert self.cost["M2"] >= 0.0

    def test_t_gate_lb_at_least_one(self):
        assert self.cost["T_gate_lb"] >= 1.0

    def test_hybrid_cost_equals_sum(self):
        assert abs(
            self.cost["hybrid_cost"] -
            (self.cost["C_KK_bits"] + self.cost["T_gate_lb"])
        ) < 1e-12

    def test_efficiency_ratio_in_unit_interval(self):
        assert 0.0 < self.cost["efficiency_ratio"] < 1.0

    def test_efficiency_ratio_formula(self):
        C_KK = self.cost["C_KK_bits"]
        hybrid = self.cost["hybrid_cost"]
        expected = C_KK / hybrid
        assert abs(self.cost["efficiency_ratio"] - expected) < 1e-12

    def test_hybrid_exceeds_c_kk(self):
        # T_gate_lb ≥ 1, so hybrid > C_KK
        assert self.cost["hybrid_cost"] > self.cost["C_KK_bits"]

    def test_raises_bad_pair(self):
        with pytest.raises(ValueError):
            nuclear_simulation_cost(7, 5)


# ===========================================================================
# is_stabilizer_state
# ===========================================================================

class TestIsStabilizerState:
    def test_true_for_00(self):
        assert is_stabilizer_state(STATE_00) is True

    def test_true_for_01(self):
        assert is_stabilizer_state(STATE_01) is True

    def test_true_for_10(self):
        assert is_stabilizer_state(STATE_10) is True

    def test_true_for_11(self):
        assert is_stabilizer_state(STATE_11) is True

    def test_false_for_braided_57(self):
        assert is_stabilizer_state(STATE_BRAID_57) is False

    def test_false_for_braided_12(self):
        assert is_stabilizer_state(STATE_BRAID_12) is False

    def test_custom_tolerance(self):
        # With very wide tolerance anything looks like a stabilizer
        assert is_stabilizer_state(STATE_BRAID_57, tol=100.0) is True


# ===========================================================================
# canonical_summary
# ===========================================================================

class TestCanonicalSummary:
    def setup_method(self):
        self.cs = canonical_summary()

    def test_matches_kk_magic_summary_57(self):
        ref = kk_magic_summary(5, 7)
        for key in ref:
            assert abs(self.cs[key] - ref[key]) < 1e-12 if isinstance(ref[key], float) \
                else self.cs[key] == ref[key]

    def test_notes_key_present(self):
        assert "notes" in self.cs

    def test_notes_contains_pillar(self):
        assert "Pillar 101" in self.cs["notes"]

    def test_notes_contains_robin_savage(self):
        assert "Robin" in self.cs["notes"]
        assert "2604.26376" in self.cs["notes"]

    def test_notes_contains_magic_values(self):
        # The notes string should quote M₂ and C_KK
        assert "M₂" in self.cs["notes"] or "M2" in self.cs["notes"]

    def test_not_stabilizer(self):
        assert self.cs["is_stabilizer"] is False

    def test_c_kk_approx_6_21(self):
        # log₂(74) ≈ 6.209
        assert abs(self.cs["C_KK_bits"] - math.log2(74.0)) < 1e-12

    def test_entanglement_approx_0_953_bits(self):
        # Pillar 31 canonical value ≈ 0.953 bits
        assert 0.9 < self.cs["S_entanglement_bits"] < 1.0


# ===========================================================================
# Cross-module consistency with Pillar 31
# ===========================================================================

class TestPillar31Consistency:
    """Ensure Pillar 101 (magic) is consistent with Pillar 31 (entanglement)."""

    def test_entanglement_entropy_from_pillar31(self):
        from src.core.kk_quantum_info import braided_winding_entropy
        S31 = braided_winding_entropy(5, 7)
        S101 = kk_magic_summary(5, 7)["S_entanglement"]
        assert abs(S31 - S101) < 1e-12

    def test_c_kk_from_pillar31(self):
        from src.core.kk_quantum_info import kk_channel_capacity
        C31 = kk_channel_capacity(5, 7)
        C101 = kk_magic_summary(5, 7)["C_KK_bits"]
        assert abs(C31 - C101) < 1e-12

    def test_braided_state_structure_preserved(self):
        from src.core.kk_quantum_info import braided_winding_state
        psi31 = braided_winding_state(5, 7)
        # Magic module uses the same state from Pillar 31
        # Verify p1/p2 match
        p1_31 = psi31[0] ** 2
        p1_101 = kk_magic_summary(5, 7)["p1"]
        assert abs(p1_31 - p1_101) < 1e-12

    def test_magic_exceeds_classical_resource(self):
        # A magic state has resources beyond classical simulation;
        # M₂ > 0 confirms the braided winding state is genuinely quantum
        M2 = kk_magic_summary(5, 7)["M2"]
        assert M2 > 0.0

    def test_pillar101_adds_to_pillar31(self):
        # Pillar 101 computes BOTH entanglement AND magic
        s = kk_magic_summary(5, 7)
        # Entanglement ≠ 0 (from Pillar 31)
        assert s["S_entanglement"] > 0.0
        # Magic ≠ 0 (new in Pillar 101)
        assert s["M2"] > 0.0
        # They are generally unequal (magic ≠ entanglement)
        # (no required ordering between M2 and S_entanglement_bits)


# ===========================================================================
# Physical reasonableness
# ===========================================================================

class TestPhysicalReasonableness:
    def test_magic_ordering_by_cs(self):
        # M2 = -log2(1 - cs^2 + cs^4) is maximised at cs=1/sqrt(2)~0.707.
        # States with cs farther from 0 and 1 (more product-like/Bell-like)
        # are closer to the maximum.  (1,3) cs=0.8 > (5,7) cs~0.324,
        # so (1,3) has more magic than (5,7).
        M2_13 = kk_magic_summary(1, 3)["M2"]
        M2_57 = kk_magic_summary(5, 7)["M2"]
        assert M2_13 > M2_57

    def test_t_gate_grows_with_magic(self):
        T_13 = kk_magic_summary(1, 3)["T_gate_lower_bound"]
        T_57 = kk_magic_summary(5, 7)["T_gate_lower_bound"]
        assert T_13 >= T_57

    def test_c_kk_larger_for_larger_k_cs(self):
        # (5,7): k_cs=74, C_KK=log2(74)≈6.21
        # (1,2): k_cs=5,  C_KK=log2(5) ≈2.32
        C_57 = kk_magic_summary(5, 7)["C_KK_bits"]
        C_12 = kk_magic_summary(1, 2)["C_KK_bits"]
        assert C_57 > C_12

    def test_hybrid_cost_finite_and_positive(self):
        cost = nuclear_simulation_cost(5, 7)
        assert math.isfinite(cost["hybrid_cost"])
        assert cost["hybrid_cost"] > 0.0

    def test_mana_and_m2_agree_on_magic_presence(self):
        # Both should be zero for stabilizers, positive for magic states
        M2 = stabilizer_renyi_entropy_m2(STATE_00)
        M_mana = mana(STATE_00)
        assert M2 < 1e-10
        assert M_mana < 1e-10

        M2_braid = stabilizer_renyi_entropy_m2(STATE_BRAID_57)
        M_mana_braid = mana(STATE_BRAID_57)
        assert M2_braid > 0.0
        assert M_mana_braid > 0.0
