# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_cmb_spatial_topology.py
====================================
Tests for src/core/cmb_spatial_topology.py — Pillar 114:
CMB Spatial Topology: E1/E2/E3 Classification and UM Compatibility.

Physical claims under test
--------------------------
1. e_topology_classes: returns correct properties for E1, E2, E3.
2. twist_holonomy: 0° (E1), 180° (E2), 90° (E3); ValueError on bad input.
3. twist_symmetry_group: Z1 (E1), Z2 (E2), Z4 (E3).
4. e1_ruled_out_status: status = RULED_OUT_IF_WITHIN_HORIZON.
5. e2_e3_viable_status: status = VIABLE for E2 and E3.
6. matched_circle_constraint: E1 constrained when L<χ; E2/E3 never constrained.
7. twisted_loop_correlation: cos(θ) formula; E1→1, E2→-1, E3→0.
8. scale_separation: ratio > 10^60; log10 > 60.
9. um_prediction_independence: all_independent=True; topology_dependent=False.
10. topology_compatible_with_um: True for all valid topologies.
11. z2_orbifold_analogy: causal_connection = False; analogy_type = STRUCTURAL_GEOMETRIC.
12. litebird_topology_sensitivity: primary_falsifier_unaffected = True.
13. Input validation: ValueError on unrecognised topology labels.
"""

from __future__ import annotations

import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src.core.cmb_spatial_topology import (
    e_topology_classes,
    twist_holonomy,
    twist_symmetry_group,
    e1_ruled_out_status,
    e2_e3_viable_status,
    matched_circle_constraint,
    twisted_loop_correlation,
    scale_separation,
    um_prediction_independence,
    topology_compatible_with_um,
    z2_orbifold_analogy,
    litebird_topology_sensitivity,
    TOPOLOGIES,
    TWIST_ANGLES_DEG,
    SYMMETRY_GROUPS,
    OBSERVATIONAL_STATUS,
    SCALE_SEPARATION,
)


# ---------------------------------------------------------------------------
# e_topology_classes
# ---------------------------------------------------------------------------

class TestETopologyClasses:
    def test_returns_three_keys(self):
        c = e_topology_classes()
        assert set(c.keys()) == {"E1", "E2", "E3"}

    def test_e1_properties(self):
        c = e_topology_classes()
        e1 = c["E1"]
        assert e1["twist_angle_deg"] == 0.0
        assert e1["symmetry_group"] == "Z1"
        assert "RULED_OUT" in e1["observational_status"]

    def test_e2_properties(self):
        c = e_topology_classes()
        e2 = c["E2"]
        assert e2["twist_angle_deg"] == 180.0
        assert e2["symmetry_group"] == "Z2"
        assert e2["observational_status"] == "VIABLE"

    def test_e3_properties(self):
        c = e_topology_classes()
        e3 = c["E3"]
        assert e3["twist_angle_deg"] == 90.0
        assert e3["symmetry_group"] == "Z4"
        assert e3["observational_status"] == "VIABLE"

    def test_all_have_required_keys(self):
        c = e_topology_classes()
        required = {"name", "twist_angle_deg", "symmetry_group", "observational_status",
                    "matched_circle_signal", "description"}
        for label, data in c.items():
            assert required.issubset(data.keys()), f"Missing keys in {label}"

    def test_e1_matched_circle_signal(self):
        c = e_topology_classes()
        assert c["E1"]["matched_circle_signal"] == "IDENTICAL_CIRCLES"

    def test_e2_e3_matched_circle_signal(self):
        c = e_topology_classes()
        assert c["E2"]["matched_circle_signal"] == "CORRELATED_BUT_DIFFERENT"
        assert c["E3"]["matched_circle_signal"] == "CORRELATED_BUT_DIFFERENT"


# ---------------------------------------------------------------------------
# twist_holonomy
# ---------------------------------------------------------------------------

class TestTwistHolonomy:
    def test_e1_zero(self):
        assert twist_holonomy("E1") == 0.0

    def test_e2_180(self):
        assert twist_holonomy("E2") == 180.0

    def test_e3_90(self):
        assert twist_holonomy("E3") == 90.0

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            twist_holonomy("E4")

    def test_case_sensitive(self):
        with pytest.raises(ValueError):
            twist_holonomy("e1")


# ---------------------------------------------------------------------------
# twist_symmetry_group
# ---------------------------------------------------------------------------

class TestTwistSymmetryGroup:
    def test_e1_z1(self):
        assert twist_symmetry_group("E1") == "Z1"

    def test_e2_z2(self):
        assert twist_symmetry_group("E2") == "Z2"

    def test_e3_z4(self):
        assert twist_symmetry_group("E3") == "Z4"

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            twist_symmetry_group("E5")


# ---------------------------------------------------------------------------
# e1_ruled_out_status
# ---------------------------------------------------------------------------

class TestE1RuledOutStatus:
    def test_status_field(self):
        s = e1_ruled_out_status()
        assert s["status"] == "RULED_OUT_IF_WITHIN_HORIZON"

    def test_topology_field(self):
        s = e1_ruled_out_status()
        assert s["topology"] == "E1"

    def test_condition_field(self):
        s = e1_ruled_out_status()
        assert "chi_rec" in s["condition"]

    def test_chi_rec_gpc_positive(self):
        s = e1_ruled_out_status()
        assert s["chi_rec_Gpc"] > 10.0  # ~14 Gpc

    def test_signal_type(self):
        s = e1_ruled_out_status()
        assert s["signal_type"] == "IDENTICAL_CIRCLES"


# ---------------------------------------------------------------------------
# e2_e3_viable_status
# ---------------------------------------------------------------------------

class TestE2E3ViableStatus:
    def test_e2_viable(self):
        s = e2_e3_viable_status("E2")
        assert s["status"] == "VIABLE"

    def test_e3_viable(self):
        s = e2_e3_viable_status("E3")
        assert s["status"] == "VIABLE"

    def test_e2_twist_180(self):
        s = e2_e3_viable_status("E2")
        assert "180" in s["twist"]

    def test_e3_twist_90(self):
        s = e3 = e2_e3_viable_status("E3")
        assert "90" in s["twist"]

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            e2_e3_viable_status("E1")

    def test_signal_type_correlated(self):
        for top in ("E2", "E3"):
            s = e2_e3_viable_status(top)
            assert "CORRELATED" in s["signal_type"]


# ---------------------------------------------------------------------------
# matched_circle_constraint
# ---------------------------------------------------------------------------

class TestMatchedCircleConstraint:
    def test_e1_within_horizon_constrained(self):
        r = matched_circle_constraint("E1", 0.5)
        assert r["constrained"] is True

    def test_e1_outside_horizon_not_constrained(self):
        r = matched_circle_constraint("E1", 1.5)
        assert r["constrained"] is False

    def test_e2_never_constrained_inside(self):
        r = matched_circle_constraint("E2", 0.3)
        assert r["constrained"] is False

    def test_e3_never_constrained_inside(self):
        r = matched_circle_constraint("E3", 0.3)
        assert r["constrained"] is False

    def test_e2_never_constrained_outside(self):
        r = matched_circle_constraint("E2", 2.0)
        assert r["constrained"] is False

    def test_within_horizon_flag_e1(self):
        r = matched_circle_constraint("E1", 0.5)
        assert r["within_horizon"] is True

    def test_invalid_topology(self):
        with pytest.raises(ValueError):
            matched_circle_constraint("E4", 0.5)

    def test_zero_l_raises(self):
        with pytest.raises(ValueError):
            matched_circle_constraint("E1", 0.0)

    def test_negative_l_raises(self):
        with pytest.raises(ValueError):
            matched_circle_constraint("E1", -0.5)


# ---------------------------------------------------------------------------
# twisted_loop_correlation
# ---------------------------------------------------------------------------

class TestTwistedLoopCorrelation:
    def test_e1_identity(self):
        """E1 has θ=0°: correlation = cos(0) = 1."""
        assert twisted_loop_correlation(0.0) == pytest.approx(1.0, rel=1e-9)

    def test_e2_anticorrelated(self):
        """E2 has θ=180°: correlation = cos(π) = -1."""
        assert twisted_loop_correlation(180.0) == pytest.approx(-1.0, rel=1e-9)

    def test_e3_orthogonal(self):
        """E3 has θ=90°: correlation = cos(π/2) = 0."""
        assert twisted_loop_correlation(90.0) == pytest.approx(0.0, abs=1e-12)

    def test_45_degrees(self):
        assert twisted_loop_correlation(45.0) == pytest.approx(math.cos(math.pi/4), rel=1e-9)

    def test_invalid_negative(self):
        with pytest.raises(ValueError):
            twisted_loop_correlation(-10.0)

    def test_invalid_over_360(self):
        with pytest.raises(ValueError):
            twisted_loop_correlation(361.0)


# ---------------------------------------------------------------------------
# scale_separation
# ---------------------------------------------------------------------------

class TestScaleSeparation:
    def test_ratio_large(self):
        s = scale_separation()
        assert s["ratio"] > 1e60

    def test_log10_over_60(self):
        s = scale_separation()
        assert s["log10_ratio"] > 60.0

    def test_planck_length_correct(self):
        s = scale_separation()
        assert abs(s["planck_length_m"] - 1.616255e-35) < 1e-40

    def test_chi_rec_correct(self):
        s = scale_separation()
        assert s["chi_rec_m"] > 1e26

    def test_interpretation_present(self):
        s = scale_separation()
        assert "interpretation" in s
        assert len(s["interpretation"]) > 10


# ---------------------------------------------------------------------------
# um_prediction_independence
# ---------------------------------------------------------------------------

class TestUMPredictionIndependence:
    def test_all_independent_flag(self):
        d = um_prediction_independence()
        assert d["all_independent"] is True

    def test_ns_not_dependent(self):
        d = um_prediction_independence()
        assert d["ns"]["topology_dependent"] is False

    def test_r_not_dependent(self):
        d = um_prediction_independence()
        assert d["r"]["topology_dependent"] is False

    def test_beta_not_dependent(self):
        d = um_prediction_independence()
        assert d["beta_deg"]["topology_dependent"] is False

    def test_ns_value_reasonable(self):
        d = um_prediction_independence()
        assert 0.95 < d["ns"]["value"] < 0.975

    def test_r_value_reasonable(self):
        d = um_prediction_independence()
        assert 0.01 < d["r"]["value"] < 0.04

    def test_explanation_present(self):
        d = um_prediction_independence()
        assert "explanation" in d
        assert "10^61" in d["explanation"] or "61" in d["explanation"]


# ---------------------------------------------------------------------------
# topology_compatible_with_um
# ---------------------------------------------------------------------------

class TestTopologyCompatibleWithUM:
    def test_e1_compatible(self):
        assert topology_compatible_with_um("E1") is True

    def test_e2_compatible(self):
        assert topology_compatible_with_um("E2") is True

    def test_e3_compatible(self):
        assert topology_compatible_with_um("E3") is True

    def test_simply_connected_compatible(self):
        assert topology_compatible_with_um("simply_connected") is True

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            topology_compatible_with_um("E5")


# ---------------------------------------------------------------------------
# z2_orbifold_analogy
# ---------------------------------------------------------------------------

class TestZ2OrbifoldAnalogy:
    def test_no_causal_connection(self):
        a = z2_orbifold_analogy()
        assert a["causal_connection"] is False

    def test_analogy_type(self):
        a = z2_orbifold_analogy()
        assert a["analogy_type"] == "STRUCTURAL_GEOMETRIC"

    def test_um_pillar_referenced(self):
        a = z2_orbifold_analogy()
        assert "Pillar" in a["um_z2_orbifold"]["pillar"]

    def test_e2_source_present(self):
        a = z2_orbifold_analogy()
        assert "APS" in a["e2_z2_spatial"]["source"] or "Planck" in a["e2_z2_spatial"]["source"]

    def test_interpretation_present(self):
        a = z2_orbifold_analogy()
        assert len(a["interpretation"]) > 20


# ---------------------------------------------------------------------------
# litebird_topology_sensitivity
# ---------------------------------------------------------------------------

class TestLiteBIRDTopologySensitivity:
    def test_primary_falsifier_unaffected(self):
        s = litebird_topology_sensitivity()
        assert s["primary_falsifier_unaffected"] is True

    def test_e2_key_present(self):
        s = litebird_topology_sensitivity()
        assert "E2" in s["topology_sensitivity"]

    def test_e3_key_present(self):
        s = litebird_topology_sensitivity()
        assert "E3" in s["topology_sensitivity"]

    def test_sigma_beta_forecast(self):
        s = litebird_topology_sensitivity()
        assert "0.03" in s["primary_um_target"]
