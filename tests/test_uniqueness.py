"""
tests/test_uniqueness.py
========================
Tests for src/core/uniqueness.py — geometric uniqueness and ΛCDM no-go.

Covers:
  - build_topology_catalog: catalog completeness and correctness
  - check_topology: individual constraint verdicts
  - uniqueness_scan: S¹/Z₂ is the unique passing topology
  - lcdm_nogo_comparison: ΛCDM / RS1 cannot reproduce (n_s, r, β)
  - joint_prediction_overlap: UM prediction vs ΛCDM parameter space
  - integer_quantization_discriminant: β quantization observability
  - full_uniqueness_report: integration test
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import numpy as np

from src.core.uniqueness import (
    CompactTopology,
    TopologyVerdict,
    UniquenessScanResult,
    NoGoResult,
    OverlapResult,
    IntegerQuantizationDiscriminant,
    build_topology_catalog,
    check_topology,
    uniqueness_scan,
    lcdm_nogo_comparison,
    joint_prediction_overlap,
    integer_quantization_discriminant,
    full_uniqueness_report,
)


# ---------------------------------------------------------------------------
# Topology catalog
# ---------------------------------------------------------------------------

class TestBuildTopologyCatalog:
    def test_catalog_is_nonempty(self):
        cat = build_topology_catalog()
        assert len(cat) >= 6

    def test_catalog_contains_s1_z2(self):
        cat = build_topology_catalog()
        names = [t.name for t in cat]
        assert "S¹/Z₂" in names

    def test_catalog_contains_alternatives(self):
        cat = build_topology_catalog()
        names = [t.name for t in cat]
        # At least S¹, T², S² must be present as alternatives
        for expected in ("S¹", "T²", "S²"):
            assert expected in names, f"{expected!r} missing from catalog"

    def test_all_entries_are_compact_topology(self):
        cat = build_topology_catalog()
        for t in cat:
            assert isinstance(t, CompactTopology)

    def test_s1_z2_flags_correct(self):
        cat = build_topology_catalog()
        s1z2 = next(t for t in cat if t.name == "S¹/Z₂")
        assert s1z2.extra_dimensions == 1
        assert s1z2.is_orbifold is True
        assert s1z2.z2_group == "Z₂"
        assert s1z2.has_chiral_zero_modes is True
        assert s1z2.winding_quantized is True
        assert s1z2.anomaly_free is True

    def test_s1_flags_no_chirality(self):
        cat = build_topology_catalog()
        s1 = next(t for t in cat if t.name == "S¹")
        assert s1.is_orbifold is False
        assert s1.has_chiral_zero_modes is False

    def test_t2_is_two_dimensional(self):
        cat = build_topology_catalog()
        t2 = next(t for t in cat if t.name == "T²")
        assert t2.extra_dimensions == 2

    def test_no_duplicate_names(self):
        cat = build_topology_catalog()
        names = [t.name for t in cat]
        assert len(names) == len(set(names))


# ---------------------------------------------------------------------------
# check_topology — individual verdicts
# ---------------------------------------------------------------------------

class TestCheckTopology:
    def test_s1_z2_passes_all(self):
        cat = build_topology_catalog()
        s1z2 = next(t for t in cat if t.name == "S¹/Z₂")
        v = check_topology(s1z2)
        assert v.passes is True
        assert v.failure_reason == ""

    def test_s1_fails_c4_chirality(self):
        cat = build_topology_catalog()
        s1 = next(t for t in cat if t.name == "S¹")
        v = check_topology(s1)
        assert v.passes is False
        assert "C4" in v.failure_reason

    def test_t2_fails_c1_dimension(self):
        cat = build_topology_catalog()
        t2 = next(t for t in cat if t.name == "T²")
        v = check_topology(t2)
        assert v.passes is False
        assert "C1" in v.failure_reason

    def test_s2_fails_c1_dimension(self):
        cat = build_topology_catalog()
        s2 = next(t for t in cat if t.name == "S²")
        v = check_topology(s2)
        assert v.passes is False
        assert "C1" in v.failure_reason

    def test_cp1_fails_c1_dimension(self):
        cat = build_topology_catalog()
        cp1 = next(t for t in cat if t.name == "CP¹")
        v = check_topology(cp1)
        assert v.passes is False

    def test_s3_fails(self):
        cat = build_topology_catalog()
        s3 = next(t for t in cat if t.name == "S³")
        v = check_topology(s3)
        assert v.passes is False

    def test_s1_z4_fails(self):
        cat = build_topology_catalog()
        s1z4 = next((t for t in cat if t.name == "S¹/Z₄"), None)
        if s1z4 is not None:
            v = check_topology(s1z4)
            assert v.passes is False

    def test_verdict_has_topology(self):
        cat = build_topology_catalog()
        v = check_topology(cat[0])
        assert isinstance(v, TopologyVerdict)
        assert v.topology is cat[0]

    def test_custom_topology_no_orbifold_fails(self):
        top = CompactTopology(
            name="CustomS1",
            extra_dimensions=1,
            is_orbifold=False,
            z2_group="none",
            has_chiral_zero_modes=False,
            winding_quantized=True,
            anomaly_free=True,
        )
        v = check_topology(top)
        assert v.passes is False
        assert "C4" in v.failure_reason

    def test_custom_1d_z2_orbifold_passes(self):
        top = CompactTopology(
            name="CustomZ2",
            extra_dimensions=1,
            is_orbifold=True,
            z2_group="Z₂",
            has_chiral_zero_modes=True,
            winding_quantized=True,
            anomaly_free=True,
        )
        v = check_topology(top)
        assert v.passes is True


# ---------------------------------------------------------------------------
# uniqueness_scan
# ---------------------------------------------------------------------------

class TestUniquenessScan:
    def test_unique_passing_topology_is_s1_z2(self):
        result = uniqueness_scan()
        assert result.is_unique is True
        assert result.unique_topology is not None
        assert result.unique_topology.name == "S¹/Z₂"

    def test_exactly_one_topology_passes(self):
        result = uniqueness_scan()
        assert len(result.passing_topologies) == 1

    def test_all_catalog_entries_have_verdict(self):
        result = uniqueness_scan()
        cat = build_topology_catalog()
        for t in cat:
            assert t.name in result.verdicts

    def test_failing_topologies_list_nonempty(self):
        result = uniqueness_scan()
        assert len(result.failing_topologies) >= 5

    def test_uniqueness_theorem_string_nonempty(self):
        result = uniqueness_scan()
        assert isinstance(result.uniqueness_theorem, str)
        assert len(result.uniqueness_theorem) > 50

    def test_uniqueness_theorem_mentions_s1_z2(self):
        result = uniqueness_scan()
        assert "S¹/Z₂" in result.uniqueness_theorem

    def test_uniqueness_theorem_mentions_alternatives(self):
        result = uniqueness_scan()
        assert "alternative" in result.uniqueness_theorem.lower() or \
               str(len(result.failing_topologies)) in result.uniqueness_theorem

    def test_custom_catalog_with_two_passing_breaks_uniqueness(self):
        # Add a second passing topology — uniqueness should be False
        top_a = CompactTopology(
            name="A", extra_dimensions=1, is_orbifold=True, z2_group="Z₂",
            has_chiral_zero_modes=True, winding_quantized=True, anomaly_free=True,
        )
        top_b = CompactTopology(
            name="B", extra_dimensions=1, is_orbifold=True, z2_group="Z₂",
            has_chiral_zero_modes=True, winding_quantized=True, anomaly_free=True,
        )
        result = uniqueness_scan(catalog=[top_a, top_b])
        assert result.is_unique is False
        assert len(result.passing_topologies) == 2

    def test_custom_catalog_no_passing_raises(self):
        top = CompactTopology(
            name="Fails", extra_dimensions=2, is_orbifold=False, z2_group="none",
            has_chiral_zero_modes=False, winding_quantized=False, anomaly_free=False,
        )
        with pytest.raises(RuntimeError, match="no topology passed"):
            uniqueness_scan(catalog=[top])


# ---------------------------------------------------------------------------
# lcdm_nogo_comparison
# ---------------------------------------------------------------------------

class TestLcdmNogoComparison:
    # UM canonical predictions
    NS_UM = 0.9635
    R_UM = 0.003
    BETA_UM = 0.35

    def test_returns_nogo_result(self):
        result = lcdm_nogo_comparison(self.NS_UM, self.R_UM, self.BETA_UM)
        assert isinstance(result, NoGoResult)

    def test_lcdm_cannot_match_birefringence(self):
        result = lcdm_nogo_comparison(self.NS_UM, self.R_UM, self.BETA_UM)
        lcdm = result.model_verdicts["ΛCDM"]
        assert lcdm["can_match_beta"] is False

    def test_lcdm_cannot_match_tensor(self):
        result = lcdm_nogo_comparison(self.NS_UM, self.R_UM, self.BETA_UM)
        lcdm = result.model_verdicts["ΛCDM"]
        assert lcdm["can_match_r"] is False

    def test_slow_roll_cannot_match_birefringence(self):
        result = lcdm_nogo_comparison(self.NS_UM, self.R_UM, self.BETA_UM)
        sr = result.model_verdicts["ΛCDM + slow-roll inflation"]
        assert sr["can_match_beta"] is False

    def test_continuous_axion_can_match_all(self):
        result = lcdm_nogo_comparison(self.NS_UM, self.R_UM, self.BETA_UM)
        axion = result.model_verdicts["ΛCDM + continuous axion"]
        assert axion["can_match"] is True

    def test_rs1_cannot_match_birefringence(self):
        result = lcdm_nogo_comparison(self.NS_UM, self.R_UM, self.BETA_UM)
        rs1 = result.model_verdicts["Randall-Sundrum RS1"]
        assert rs1["can_match_beta"] is False

    def test_um_is_distinct(self):
        result = lcdm_nogo_comparison(self.NS_UM, self.R_UM, self.BETA_UM)
        assert result.um_is_distinct is True

    def test_discriminating_signatures_nonempty(self):
        result = lcdm_nogo_comparison(self.NS_UM, self.R_UM, self.BETA_UM)
        assert len(result.discriminating_signatures) >= 3

    def test_signatures_mention_quantization(self):
        result = lcdm_nogo_comparison(self.NS_UM, self.R_UM, self.BETA_UM)
        combined = " ".join(result.discriminating_signatures).lower()
        assert "quantiz" in combined or "integer" in combined

    def test_beta_zero_can_match_lcdm(self):
        # If β = 0, ΛCDM CAN match β
        result = lcdm_nogo_comparison(self.NS_UM, self.R_UM, 0.0)
        lcdm = result.model_verdicts["ΛCDM"]
        assert lcdm["can_match_beta"] is True

    def test_model_verdicts_has_all_models(self):
        result = lcdm_nogo_comparison(self.NS_UM, self.R_UM, self.BETA_UM)
        expected_models = {
            "ΛCDM",
            "ΛCDM + slow-roll inflation",
            "ΛCDM + continuous axion",
            "Randall-Sundrum RS1",
        }
        assert expected_models.issubset(set(result.model_verdicts.keys()))


# ---------------------------------------------------------------------------
# joint_prediction_overlap
# ---------------------------------------------------------------------------

class TestJointPredictionOverlap:
    NS_UM = 0.9635
    R_UM = 0.003
    BETA_UM = 0.35

    def test_returns_overlap_result(self):
        r = joint_prediction_overlap(self.NS_UM, self.R_UM, self.BETA_UM)
        assert isinstance(r, OverlapResult)

    def test_ns_in_lcdm_range(self):
        r = joint_prediction_overlap(self.NS_UM, self.R_UM, self.BETA_UM)
        assert r.ns_in_lcdm_range is True

    def test_r_in_lcdm_range(self):
        r = joint_prediction_overlap(self.NS_UM, self.R_UM, self.BETA_UM)
        # r=0.003 is within the 0–0.064 window
        assert r.r_in_lcdm_range is True

    def test_beta_outside_lcdm_range(self):
        # ΛCDM predicts β = 0 ± 0.14°; 0.35° is within the window (just)
        r = joint_prediction_overlap(self.NS_UM, self.R_UM, self.BETA_UM)
        # β = 0.35 is within ±0.14° window? No: 0.35 > 0.14
        assert r.beta_explained_lcdm is False

    def test_large_r_outside_lcdm(self):
        r = joint_prediction_overlap(0.965, 0.2, 0.0)
        assert r.r_in_lcdm_range is False

    def test_note_is_string(self):
        r = joint_prediction_overlap(self.NS_UM, self.R_UM, self.BETA_UM)
        assert isinstance(r.note, str) and len(r.note) > 20

    def test_custom_range_matching(self):
        r = joint_prediction_overlap(
            0.965, 0.003, 0.35,
            ns_lcdm_range=(0.96, 0.97),
            r_lcdm_range=(0.0, 0.01),
            beta_lcdm_range=(0.2, 0.5),
        )
        assert r.ns_in_lcdm_range is True
        assert r.r_in_lcdm_range is True
        assert r.beta_explained_lcdm is True
        assert r.joint_overlap is True


# ---------------------------------------------------------------------------
# integer_quantization_discriminant
# ---------------------------------------------------------------------------

class TestIntegerQuantizationDiscriminant:
    def test_returns_correct_type(self):
        d = integer_quantization_discriminant()
        assert isinstance(d, IntegerQuantizationDiscriminant)

    def test_spacing_positive(self):
        d = integer_quantization_discriminant()
        assert d.beta_spacing_deg > 0.0

    def test_discriminant_is_positive(self):
        d = integer_quantization_discriminant()
        assert d.discriminant > 0.0

    def test_current_sigma_stored(self):
        d = integer_quantization_discriminant(sigma_beta=0.14)
        assert d.current_sigma == pytest.approx(0.14)

    def test_high_precision_resolves_quantization(self):
        # With very small sigma, quantization should be resolved
        d = integer_quantization_discriminant(sigma_beta=0.001)
        assert d.quantization_resolved is True
        assert d.discriminant > 1.0

    def test_low_precision_does_not_resolve(self):
        # With large sigma, quantization is not resolved
        d = integer_quantization_discriminant(sigma_beta=2.0)
        assert d.quantization_resolved is False
        assert d.discriminant < 1.0

    def test_n_levels_in_window_positive(self):
        d = integer_quantization_discriminant(sigma_beta=0.14)
        assert d.n_levels_in_window >= 1

    def test_n_levels_decreases_with_smaller_sigma(self):
        d_wide = integer_quantization_discriminant(sigma_beta=0.5)
        d_narrow = integer_quantization_discriminant(sigma_beta=0.01)
        assert d_narrow.n_levels_in_window <= d_wide.n_levels_in_window

    def test_sigma_required_positive(self):
        d = integer_quantization_discriminant()
        assert d.sigma_required > 0.0


# ---------------------------------------------------------------------------
# full_uniqueness_report (integration test)
# ---------------------------------------------------------------------------

class TestFullUniquenessReport:
    def test_returns_dict(self):
        r = full_uniqueness_report()
        assert isinstance(r, dict)

    def test_has_required_keys(self):
        r = full_uniqueness_report()
        for key in ("uniqueness_scan", "nogo_comparison", "joint_overlap",
                    "quantization_discriminant", "ns", "r", "beta_deg"):
            assert key in r, f"Missing key: {key!r}"

    def test_uniqueness_holds(self):
        r = full_uniqueness_report()
        assert r["uniqueness_scan"].is_unique is True

    def test_um_is_distinct(self):
        r = full_uniqueness_report()
        assert r["nogo_comparison"].um_is_distinct is True

    def test_ns_in_planck_range(self):
        r = full_uniqueness_report()
        ns = r["ns"]
        # Planck 2018: 0.9607 ± 0.0042 (1σ)
        assert 0.950 < ns < 0.975, f"n_s = {ns:.4f} outside expected range"

    def test_r_small(self):
        r = full_uniqueness_report()
        # r = 16ε with φ₀_eff ≈ 31.4: r ≈ 16 × (4/φ₀²) ≈ 0.065–0.12
        assert 0.0 < r["r"] < 0.15, f"r = {r['r']:.4f} outside expected range"

    def test_beta_near_0p35(self):
        r = full_uniqueness_report()
        beta = r["beta_deg"]
        assert 0.1 < beta < 0.6, f"β = {beta:.4f}° outside expected range"
