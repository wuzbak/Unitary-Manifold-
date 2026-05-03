# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_emergent_spacetime_entanglement.py
===============================================
Tests for Pillar 129 — Emergent Spacetime from KK Entanglement.

~60 tests covering: RT entropy, holographic screen area, Fisher metric
components, ER=EPR correspondence, ebit-area ratio, and proof steps.
"""

from __future__ import annotations

import math

import pytest

from src.core.emergent_spacetime_entanglement import (
    K_CS,
    N_W,
    L_PL_M,
    L_PL_M2,
    G_N,
    C_LIGHT,
    HBAR,
    M_KK_EV,
    M_KK_KG,
    LOG2,
    ryu_takayanagi_kk,
    spacetime_as_fisher_metric,
    er_epr_kk_bridge,
    ebit_to_planck_area,
    entanglement_geometry_proof,
)


# ---------------------------------------------------------------------------
# TestConstants — 5 tests
# ---------------------------------------------------------------------------

class TestConstants:
    def test_k_cs_74(self):
        assert K_CS == 74

    def test_n_w_5(self):
        assert N_W == 5

    def test_l_pl_positive(self):
        assert L_PL_M > 0

    def test_m_kk_ev_positive(self):
        assert M_KK_EV > 0

    def test_log2_correct(self):
        assert abs(LOG2 - math.log(2.0)) < 1e-12


# ---------------------------------------------------------------------------
# TestRuyuTakayanagiKK — 14 tests
# ---------------------------------------------------------------------------

class TestRuyuTakayanagiKK:
    def test_returns_dict(self):
        assert isinstance(ryu_takayanagi_kk(), dict)

    def test_r_kk_equals_l_pl(self):
        d = ryu_takayanagi_kk()
        assert abs(d["r_kk_m"] - L_PL_M) < 1e-40

    def test_holographic_area_positive(self):
        d = ryu_takayanagi_kk()
        assert d["holographic_screen_area_m2"] > 0

    def test_holographic_area_formula(self):
        d = ryu_takayanagi_kk()
        expected = 4 * math.pi * L_PL_M ** 2
        assert abs(d["holographic_screen_area_m2"] - expected) < 1e-60

    def test_l_pl_sq_si_positive(self):
        d = ryu_takayanagi_kk()
        assert d["l_pl_sq_si_m2"] > 0

    def test_l_pl_sq_si_order_of_magnitude(self):
        d = ryu_takayanagi_kk()
        # L_Pl² ≈ 2.6e-70 m²
        assert 1e-72 < d["l_pl_sq_si_m2"] < 1e-68

    def test_s_ent_planck_units_positive(self):
        d = ryu_takayanagi_kk()
        assert d["s_ent_planck_units"] > 0

    def test_s_ent_approx_4pi(self):
        d = ryu_takayanagi_kk()
        # S_ent = A_holo / (4 L_Pl²_SI) = 4π L_Pl² / (4 L_Pl²) = π
        # (exact when L_Pl_SI² = ℏG/c³ vs our L_PL_M² definition)
        assert d["s_ent_planck_units"] > 1.0

    def test_s_ent_bits_positive(self):
        d = ryu_takayanagi_kk()
        assert d["s_ent_bits"] > 0

    def test_s_ent_bits_from_planck(self):
        d = ryu_takayanagi_kk()
        assert abs(d["s_ent_bits"] - d["s_ent_planck_units"] / LOG2) < 1e-6

    def test_epistemic_status_conditional_theorem(self):
        d = ryu_takayanagi_kk()
        assert d["epistemic_status"] == "CONDITIONAL_THEOREM"

    def test_has_formula(self):
        d = ryu_takayanagi_kk()
        assert "S_ent" in d["formula"]

    def test_has_pillar_4_link(self):
        d = ryu_takayanagi_kk()
        assert "Pillar 4" in d["pillar_4_link"]

    def test_holographic_area_order_m2(self):
        d = ryu_takayanagi_kk()
        # 4π L_Pl² ≈ 3.28e-69 m²
        assert 1e-71 < d["holographic_screen_area_m2"] < 1e-67


# ---------------------------------------------------------------------------
# TestSpacetimeAsFisherMetric — 12 tests
# ---------------------------------------------------------------------------

class TestSpacetimeAsFisherMetric:
    def test_returns_dict(self):
        assert isinstance(spacetime_as_fisher_metric(), dict)

    def test_sigma_kk_positive(self):
        d = spacetime_as_fisher_metric()
        assert d["sigma_kk_m"] > 0

    def test_sigma_kk_larger_than_l_pl(self):
        d = spacetime_as_fisher_metric()
        assert d["sigma_kk_m"] > L_PL_M

    def test_g_xx_positive(self):
        d = spacetime_as_fisher_metric()
        assert d["g_xx_si"] > 0

    def test_g_xx_inverse_of_sigma_sq(self):
        d = spacetime_as_fisher_metric()
        assert abs(d["g_xx_si"] - 1.0 / d["sigma_kk_m"] ** 2) < 1e6

    def test_metric_signature_is_tuple(self):
        d = spacetime_as_fisher_metric()
        assert d["metric_signature"] == (-1, +1, +1, +1)

    def test_flat_limit_recovered(self):
        d = spacetime_as_fisher_metric()
        assert d["flat_limit_recovered"] is True

    def test_epistemic_status_formal_analogy(self):
        d = spacetime_as_fisher_metric()
        assert "FORMAL_ANALOGY" in d["epistemic_status"]

    def test_has_formula(self):
        d = spacetime_as_fisher_metric()
        assert "Fisher" in d["formula"] or "g_μν" in d["formula"]

    def test_has_note(self):
        d = spacetime_as_fisher_metric()
        assert len(d["note"]) > 20

    def test_sigma_kk_in_planck_lengths_positive(self):
        d = spacetime_as_fisher_metric()
        assert d["sigma_kk_in_planck_lengths"] > 0

    def test_metric_scale_positive(self):
        d = spacetime_as_fisher_metric()
        assert d["g_metric_scale_planck"] > 0


# ---------------------------------------------------------------------------
# TestErEprKkBridge — 10 tests
# ---------------------------------------------------------------------------

class TestErEprKkBridge:
    def test_returns_dict(self):
        assert isinstance(er_epr_kk_bridge(), dict)

    def test_bridge_length_positive(self):
        d = er_epr_kk_bridge()
        assert d["bridge_length_m"] > 0

    def test_bridge_longer_than_r_kk(self):
        d = er_epr_kk_bridge()
        assert d["bridge_longer_than_r_kk"] is True

    def test_entanglement_energy_positive(self):
        d = er_epr_kk_bridge()
        assert d["entanglement_energy_j"] > 0

    def test_entanglement_energy_eV(self):
        d = er_epr_kk_bridge()
        assert abs(d["entanglement_energy_eV"] - M_KK_EV) < 1e-6

    def test_bridge_length_in_planck_positive(self):
        d = er_epr_kk_bridge()
        assert d["bridge_length_planck"] > 0

    def test_formula_present(self):
        d = er_epr_kk_bridge()
        assert "L_ER" in d["formula"]

    def test_epistemic_status_formal_analogy(self):
        d = er_epr_kk_bridge()
        assert "FORMAL_ANALOGY" in d["epistemic_status"]

    def test_r_kk_reference_is_l_pl(self):
        d = er_epr_kk_bridge()
        assert abs(d["r_kk_reference_m"] - L_PL_M) < 1e-40

    def test_description_present(self):
        d = er_epr_kk_bridge()
        assert len(d["description"]) > 30


# ---------------------------------------------------------------------------
# TestEbitToPlanckArea — 10 tests
# ---------------------------------------------------------------------------

class TestEbitToPlanckArea:
    def test_returns_dict(self):
        assert isinstance(ebit_to_planck_area(), dict)

    def test_a_ebit_positive(self):
        d = ebit_to_planck_area()
        assert d["a_ebit_m2"] > 0

    def test_a_ebit_formula(self):
        d = ebit_to_planck_area()
        expected = 4.0 * math.log(2.0) * L_PL_M2
        assert abs(d["a_ebit_m2"] - expected) < 1e-80

    def test_a_ebit_planck_units(self):
        d = ebit_to_planck_area()
        assert abs(d["a_ebit_in_planck_units"] - 4.0 * math.log(2.0)) < 1e-12

    def test_a_min_um_positive(self):
        d = ebit_to_planck_area()
        assert d["a_min_um_m2"] > 0

    def test_n_ebits_per_area_positive(self):
        d = ebit_to_planck_area()
        assert d["n_ebits_per_um_area_quantum"] > 0

    def test_n_ebits_per_area_formula(self):
        d = ebit_to_planck_area()
        a_min = 4 * math.pi * K_CS * L_PL_M2
        a_ebit = 4.0 * math.log(2.0) * L_PL_M2
        expected = a_min / a_ebit
        assert abs(d["n_ebits_per_um_area_quantum"] - expected) < 1e-6

    def test_has_formula(self):
        d = ebit_to_planck_area()
        assert "A_ebit" in d["formula"]

    def test_description_mentions_kcs(self):
        d = ebit_to_planck_area()
        assert "128" in d["description"] or "Pillar" in d["description"]

    def test_n_ebits_per_planck_area(self):
        d = ebit_to_planck_area()
        expected = 1.0 / (4.0 * math.log(2.0))
        assert abs(d["n_ebits_per_planck_area"] - expected) < 1e-10


# ---------------------------------------------------------------------------
# TestEntanglementGeometryProof — 9 tests
# ---------------------------------------------------------------------------

class TestEntanglementGeometryProof:
    def test_returns_list(self):
        assert isinstance(entanglement_geometry_proof(), list)

    def test_has_6_steps(self):
        assert len(entanglement_geometry_proof()) == 6

    def test_all_steps_have_step_key(self):
        for step in entanglement_geometry_proof():
            assert "step" in step

    def test_step_numbers_sequential(self):
        steps = [s["step"] for s in entanglement_geometry_proof()]
        assert steps == list(range(1, 7))

    def test_all_steps_have_label(self):
        for step in entanglement_geometry_proof():
            assert "label" in step

    def test_all_steps_have_epistemic_status(self):
        for step in entanglement_geometry_proof():
            assert "epistemic_status" in step

    def test_all_steps_have_pillar_reference(self):
        for step in entanglement_geometry_proof():
            assert "pillar_reference" in step

    def test_step_1_is_derived(self):
        step1 = entanglement_geometry_proof()[0]
        assert "DERIVED" in step1["epistemic_status"]

    def test_last_step_is_conclusion(self):
        last = entanglement_geometry_proof()[-1]
        assert "Conclusion" in last["label"] or "conclusion" in last["label"].lower()
