# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_topological_hierarchy.py
=====================================
Tests for src/core/topological_hierarchy.py — Pillar 116:
Topological Hierarchy: Compact Dimension vs Global Spatial Topology.

Physical claims under test
--------------------------
1. planck_scale_m: returns ~1.6e-35 m.
2. hubble_scale_m: returns ~1.3e26 m.
3. recombination_scale_m: returns ~4e26 m.
4. kk_mass_scale_eV: returns ~1.2e28 eV (Planck mass).
5. topology_mass_scale_eV: returns ~1.5e-33 eV (ℏ H_0).
6. scale_ratio: returns > 10^60.
7. decoupling_proof_steps: returns >= 6 steps; each has step/title/statement.
8. um_observable_topology_independence: topology_dependent=False; spatial_topology_enters=False.
9. kk_spectrum_topology_independence: depends_on_spatial_topology=False; correction < 1e-58.
10. compact_vs_global_classification: correct scale assignments; coupling = "None".
11. appelquist_carazzone_bound: (m_IR/m_UV)^n < 1; n=1 < 10^-60; n=2 even smaller.
12. separation_of_scales_summary: um_observables_affected=False; log10 > 60; 6 proof steps.
13. Input validation: ValueError on unknown observables, n_dim < 1.
"""

from __future__ import annotations

import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src.core.topological_hierarchy import (
    planck_scale_m,
    hubble_scale_m,
    recombination_scale_m,
    kk_mass_scale_eV,
    topology_mass_scale_eV,
    scale_ratio,
    decoupling_proof_steps,
    um_observable_topology_independence,
    kk_spectrum_topology_independence,
    compact_vs_global_classification,
    appelquist_carazzone_bound,
    separation_of_scales_summary,
    PLANCK_LENGTH_M,
    M_PLANCK_EV,
    M_TOPO_EV,
    SCALE_RATIO,
    N_S,
    R_BRAIDED,
    BETA_DEG,
    K_CS,
    N_W,
)


# ---------------------------------------------------------------------------
# Scale accessors
# ---------------------------------------------------------------------------

class TestScaleAccessors:
    def test_planck_scale_order_of_magnitude(self):
        lp = planck_scale_m()
        assert 1e-36 < lp < 1e-34

    def test_planck_scale_value(self):
        assert planck_scale_m() == pytest.approx(1.616255e-35, rel=1e-4)

    def test_hubble_scale_order(self):
        rh = hubble_scale_m()
        assert 1e25 < rh < 1e27

    def test_recombination_scale_order(self):
        chi = recombination_scale_m()
        assert 1e25 < chi < 1e27

    def test_recombination_larger_than_hubble(self):
        # χ_rec > R_H because recombination was at z≈1100
        assert recombination_scale_m() > hubble_scale_m() * 0.5

    def test_kk_mass_order(self):
        m = kk_mass_scale_eV()
        assert 1e27 < m < 1e29   # M_Pl ~ 1.22e28 eV

    def test_topology_mass_order(self):
        m = topology_mass_scale_eV()
        assert 1e-35 < m < 1e-31  # ℏ H_0 ~ 1.5e-33 eV

    def test_kk_mass_much_larger_than_topology_mass(self):
        assert kk_mass_scale_eV() > topology_mass_scale_eV() * 1e59


# ---------------------------------------------------------------------------
# scale_ratio
# ---------------------------------------------------------------------------

class TestScaleRatio:
    def test_ratio_exceeds_1e60(self):
        assert scale_ratio() > 1e60

    def test_ratio_consistent_with_constants(self):
        # ratio = M_Planck_eV / M_topo_eV
        expected = M_PLANCK_EV / M_TOPO_EV
        assert scale_ratio() == pytest.approx(expected, rel=1e-6)


# ---------------------------------------------------------------------------
# decoupling_proof_steps
# ---------------------------------------------------------------------------

class TestDecouplingProofSteps:
    def test_at_least_6_steps(self):
        steps = decoupling_proof_steps()
        assert len(steps) >= 6

    def test_step_numbers_sequential(self):
        steps = decoupling_proof_steps()
        for i, step in enumerate(steps, start=1):
            assert step["step"] == i

    def test_each_step_has_required_keys(self):
        steps = decoupling_proof_steps()
        for step in steps:
            assert "step" in step
            assert "title" in step
            assert "statement" in step

    def test_step_1_identifies_scales(self):
        steps = decoupling_proof_steps()
        assert "scale" in steps[0]["statement"].lower() or "compact" in steps[0]["statement"].lower()

    def test_appelquist_mentioned(self):
        steps = decoupling_proof_steps()
        text = " ".join(s["statement"] for s in steps)
        assert "Appelquist" in text or "decoupl" in text.lower()

    def test_final_step_is_qed(self):
        steps = decoupling_proof_steps()
        last = steps[-1]["statement"]
        assert "QED" in last or "topology-independent" in last


# ---------------------------------------------------------------------------
# um_observable_topology_independence
# ---------------------------------------------------------------------------

class TestUMObservableTopologyIndependence:
    @pytest.mark.parametrize("obs", ["ns", "r", "beta", "k_cs", "n_w"])
    def test_not_topology_dependent(self, obs):
        d = um_observable_topology_independence(obs)
        assert d["topology_dependent"] is False

    @pytest.mark.parametrize("obs", ["ns", "r", "beta", "k_cs", "n_w"])
    def test_spatial_topology_does_not_enter(self, obs):
        d = um_observable_topology_independence(obs)
        assert d["spatial_topology_enters"] is False

    def test_ns_value(self):
        d = um_observable_topology_independence("ns")
        assert d["value"] == pytest.approx(N_S, rel=1e-6)

    def test_r_value(self):
        d = um_observable_topology_independence("r")
        assert d["value"] == pytest.approx(R_BRAIDED, rel=1e-6)

    def test_k_cs_value(self):
        d = um_observable_topology_independence("k_cs")
        assert d["value"] == K_CS

    def test_n_w_value(self):
        d = um_observable_topology_independence("n_w")
        assert d["value"] == N_W

    def test_derivation_present(self):
        for obs in ["ns", "r", "beta", "k_cs", "n_w"]:
            d = um_observable_topology_independence(obs)
            assert len(d["derivation"]) > 10

    def test_invalid_observable_raises(self):
        with pytest.raises(ValueError):
            um_observable_topology_independence("unknown")

    def test_suppression_factor_present(self):
        d = um_observable_topology_independence("ns")
        assert "suppression_factor" in d


# ---------------------------------------------------------------------------
# kk_spectrum_topology_independence
# ---------------------------------------------------------------------------

class TestKKSpectrumTopologyIndependence:
    def test_not_dependent_on_spatial_topology(self):
        k = kk_spectrum_topology_independence()
        assert k["depends_on_spatial_topology"] is False

    def test_correction_tiny(self):
        k = kk_spectrum_topology_independence()
        assert k["correction_from_spatial_topology"] < 1e-58

    def test_log10_correction_very_negative(self):
        k = kk_spectrum_topology_independence()
        assert k["correction_log10"] < -58

    def test_kk_mass_formula_present(self):
        k = kk_spectrum_topology_independence()
        assert "M_n" in k["kk_mass_formula"] or "M_" in k["kk_mass_formula"]

    def test_conclusion_present(self):
        k = kk_spectrum_topology_independence()
        assert len(k["conclusion"]) > 20


# ---------------------------------------------------------------------------
# compact_vs_global_classification
# ---------------------------------------------------------------------------

class TestCompactVsGlobalClassification:
    def test_has_compact_key(self):
        c = compact_vs_global_classification()
        assert "compact_extra_dimension" in c

    def test_has_global_key(self):
        c = compact_vs_global_classification()
        assert "global_spatial_topology" in c

    def test_scale_ratio_present(self):
        c = compact_vs_global_classification()
        assert c["scale_ratio"] > 1e60

    def test_log10_scale_ratio(self):
        c = compact_vs_global_classification()
        assert c["log10_scale_ratio"] > 60

    def test_coupling_is_none(self):
        c = compact_vs_global_classification()
        assert "None" in c["coupling"]

    def test_compact_dim_is_5th(self):
        c = compact_vs_global_classification()
        assert "5" in c["compact_extra_dimension"]["dimension"]

    def test_global_topology_cmb_relevant(self):
        c = compact_vs_global_classification()
        assert c["global_spatial_topology"]["cmb_paper_relevant"] is True

    def test_compact_dim_not_cmb_paper_relevant(self):
        c = compact_vs_global_classification()
        assert c["compact_extra_dimension"]["cmb_paper_relevant"] is False

    def test_conclusion_present(self):
        c = compact_vs_global_classification()
        assert len(c["conclusion"]) > 20


# ---------------------------------------------------------------------------
# appelquist_carazzone_bound
# ---------------------------------------------------------------------------

class TestAppelquistCarazzaneBound:
    def test_n1_tiny(self):
        b = appelquist_carazzone_bound(1)
        assert b < 1e-58

    def test_n2_even_smaller(self):
        b1 = appelquist_carazzone_bound(1)
        b2 = appelquist_carazzone_bound(2)
        assert b2 < b1

    def test_n1_positive(self):
        assert appelquist_carazzone_bound(1) > 0

    def test_n0_raises(self):
        with pytest.raises(ValueError):
            appelquist_carazzone_bound(0)

    def test_negative_n_raises(self):
        with pytest.raises(ValueError):
            appelquist_carazzone_bound(-1)

    def test_geometric_scaling(self):
        # b(n=2) = b(n=1)^2
        b1 = appelquist_carazzone_bound(1)
        b2 = appelquist_carazzone_bound(2)
        assert b2 == pytest.approx(b1 ** 2, rel=1e-6)


# ---------------------------------------------------------------------------
# separation_of_scales_summary
# ---------------------------------------------------------------------------

class TestSeparationOfScalesSummary:
    def test_um_observables_not_affected(self):
        s = separation_of_scales_summary()
        assert s["um_observables_affected_by_spatial_topology"] is False

    def test_log10_over_60(self):
        s = separation_of_scales_summary()
        assert s["log10_scale_ratio"] > 60

    def test_proof_steps_count(self):
        s = separation_of_scales_summary()
        assert s["proof_steps"] >= 6

    def test_epistemic_status(self):
        s = separation_of_scales_summary()
        assert "PROVED" in s["epistemic_status"]

    def test_statement_mentions_observables(self):
        s = separation_of_scales_summary()
        assert "nₛ" in s["statement"] or "0.9635" in s["statement"]

    def test_pillar_number(self):
        s = separation_of_scales_summary()
        assert s["pillar"] == 116

    def test_appelquist_carazzone_in_statement(self):
        s = separation_of_scales_summary()
        assert "Appelquist" in s["statement"] or "decoupl" in s["statement"].lower()

    def test_n1_suppression_tiny(self):
        s = separation_of_scales_summary()
        assert s["appelquist_carazzone_n1"] < 1e-58
