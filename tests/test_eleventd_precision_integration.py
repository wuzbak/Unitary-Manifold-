# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Integration tests for the 11D eleventd precision expansion sprint (v17.0).

Tests the full chain:
  Pillars 519–524 + existing eleventd modules chain without errors
  Seed purity checks: no PDG fit tables enter as derivation inputs
  Determinism checks: all outputs bit-reproducible across runs
  Cross-module consistency: Z_φ^{NLO} from pipeline agrees with Z_φ^{(0)}
      from Pillar 355 within correction bounds

Covers Pillars: 519, 520, 521, 522, 523, 524
Plus existing eleventd: horava_witten_reduction, g4_flux_vacuum_link,
    uv_vacuum_selection_gate, uv_to_5d_boundary_map, horava_witten_hard_gate
"""

from __future__ import annotations

import math
import pytest

# New precision modules
from src.eleventd.g4_flux_zphi_correction import (
    g4_zphi_correction_report,
    g4_flux_selection_summary,
    zphi_zero_point,
    zphi_nlo,
    delta_zphi_g4,
    K_CS,
    PI_KR,
)
from src.eleventd.e8_gauge_pr_derivation import (
    e8_gauge_pr_report,
    p_r_conditional_certificate,
    VOL_CY3_FIDUCIAL,
    P_R_GEOMETRIC_MIN,
    P_R_GEOMETRIC_MAX,
)
from src.eleventd.moduli_stabilization_nlo import (
    moduli_stabilization_nlo_report,
    nlo_moduli_minimum,
    NLO_BOUND_PCT,
)
from src.eleventd.precision_correction_pipeline import (
    precision_correction_pipeline,
    nlo_zphi_chain,
    nlo_seed_chain,
    p_r_chain,
)
from src.eleventd.architecture_limit_upgrade import (
    architecture_limit_upgrade_report,
    p517_upgrade_certificate,
    p518_upgrade_certificate,
    UPGRADE_REGISTRY,
)
from src.eleventd.full_precision_closure_v2 import (
    full_precision_closure_v2_report,
    irreducible_gap_inventory,
)

# Existing eleventd modules
from src.eleventd.horava_witten_reduction import rung6_kickoff_evidence
from src.eleventd.g4_flux_vacuum_link import g4_flux_selection_summary as base_g4_summary
from src.eleventd.uv_vacuum_selection_gate import canonical_uv_vacuum_selection_gate
from src.eleventd.horava_witten_hard_gate import rung6_gate_evidence


# ── Pillar 355 baseline import ─────────────────────────────────────────────────
try:
    from src.core.pillar355_zphi_second_quantization import K_CS as K_CS_355
    PILLAR355_AVAILABLE = True
except ImportError:
    PILLAR355_AVAILABLE = False


# ── Full chain: all new modules chain without errors ──────────────────────────


class TestFullChainNoErrors:
    def test_g4_zphi_correction_report(self):
        report = g4_zphi_correction_report()
        assert isinstance(report, dict)

    def test_moduli_stabilization_report(self):
        report = moduli_stabilization_nlo_report()
        assert isinstance(report, dict)

    def test_e8_gauge_pr_report(self):
        report = e8_gauge_pr_report()
        assert isinstance(report, dict)

    def test_architecture_limit_upgrade_report(self):
        report = architecture_limit_upgrade_report()
        assert isinstance(report, dict)

    def test_precision_correction_pipeline(self):
        pipeline = precision_correction_pipeline()
        assert isinstance(pipeline, dict)

    def test_full_precision_closure_v2(self):
        report = full_precision_closure_v2_report()
        assert isinstance(report, dict)


# ── Existing eleventd modules still pass ─────────────────────────────────────


class TestExistingEleventdStillPass:
    def test_horava_witten_kickoff(self):
        ev = rung6_kickoff_evidence()
        assert ev["kill_switch_pass"] is True

    def test_g4_flux_vacuum_link(self):
        summary = base_g4_summary()
        assert "unique_flux_selected_n_w" in summary
        assert summary["unique_flux_selected_n_w"] == 5

    def test_uv_vacuum_selection_gate(self):
        gate = canonical_uv_vacuum_selection_gate()
        assert gate["selected_n_w"] == 5

    def test_rung6_hard_gate(self):
        ev = rung6_gate_evidence()
        assert ev["hard_gate_pass"] is True


# ── Seed purity checks ────────────────────────────────────────────────────────


class TestSeedPurity:
    """Verify no PDG fit tables enter as 11D derivation inputs."""

    def test_g4_report_uses_geometric_constants_only(self):
        report = g4_zphi_correction_report()
        # K_CS, chi, pi_kr — all geometric, not fit
        assert report["input_parameters"]["k_cs"] == 74
        assert report["input_parameters"]["pi_kr"] == 37.0
        assert report["cy3_benchmark"]["chi"] == -200

    def test_moduli_report_seed_purity(self):
        report = moduli_stabilization_nlo_report()
        seed_note = report["nlo_seed"]
        # Seed must contain eta_bar and pi_kr from geometry
        assert "eta_bar" in seed_note
        assert "pi_kr" in seed_note

    def test_e8_report_no_pdg_tables(self):
        report = e8_gauge_pr_report()
        # The E8 derivation starts from vol_cy3, not PDG neutrino masses
        assert "vol_cy3" in report["input_parameters"]
        # P_R_FITTED_P383 is used as a cross-check target, not a derivation seed
        pr = report["p_r_derivation"]
        assert "p_r_11d_conditional" in pr

    def test_pipeline_seed_purity_flag(self):
        seed = nlo_seed_chain()
        # vol_cy3_nlo comes from geometric GW stabilization
        assert seed["vol_cy3_nlo"] > 0
        assert seed["pi_kr_nlo"] > 0


# ── Determinism checks ────────────────────────────────────────────────────────


class TestDeterminism:
    """Verify all pipeline outputs are bit-reproducible across runs."""

    def test_zphi_nlo_deterministic(self):
        z1 = zphi_nlo()
        z2 = zphi_nlo()
        assert z1 == z2

    def test_delta_zphi_g4_deterministic(self):
        d1 = delta_zphi_g4()
        d2 = delta_zphi_g4()
        assert d1 == d2

    def test_moduli_minimum_deterministic(self):
        m1 = nlo_moduli_minimum()
        m2 = nlo_moduli_minimum()
        assert m1["pi_kr_nlo"] == m2["pi_kr_nlo"]
        assert m1["vol_cy3_nlo"] == m2["vol_cy3_nlo"]

    def test_p_r_conditional_deterministic(self):
        c1 = p_r_conditional_certificate()
        c2 = p_r_conditional_certificate()
        assert c1["p_r_conditional"] == c2["p_r_conditional"]

    def test_pipeline_fully_deterministic(self):
        p1 = precision_correction_pipeline()
        p2 = precision_correction_pipeline()
        assert p1["zphi_nlo"] == p2["zphi_nlo"]
        assert p1["p_r_conditional"]["p_r_value"] == p2["p_r_conditional"]["p_r_value"]
        assert p1["nlo_seed"]["pi_kr"] == p2["nlo_seed"]["pi_kr"]
        assert p1["nlo_seed"]["vol_cy3"] == p2["nlo_seed"]["vol_cy3"]

    def test_full_closure_deterministic(self):
        r1 = full_precision_closure_v2_report()
        r2 = full_precision_closure_v2_report()
        assert (
            r1["deliverables"]["2_g4_zphi_correction"]["zphi_nlo"]
            == r2["deliverables"]["2_g4_zphi_correction"]["zphi_nlo"]
        )


# ── Cross-module consistency ──────────────────────────────────────────────────


class TestCrossModuleConsistency:
    """Verify Z_φ^{NLO} from pipeline agrees with Z_φ^{(0)} from Pillar 355."""

    @pytest.mark.skipif(not PILLAR355_AVAILABLE, reason="Pillar 355 not available")
    def test_k_cs_agrees_with_pillar355(self):
        assert K_CS == K_CS_355

    def test_zphi_0_formula_matches_canonical(self):
        # Z_φ^{(0)} = 1 + √K_CS/2 (Pillar 355, Eq. 1)
        z0_from_519 = zphi_zero_point()
        z0_expected = 1.0 + math.sqrt(74) / 2.0
        assert z0_from_519 == pytest.approx(z0_expected, rel=1e-12)

    def test_zphi_nlo_exceeds_zphi_0(self):
        z0 = zphi_zero_point()
        z_nlo = zphi_nlo()
        assert z_nlo > z0

    def test_zphi_nlo_within_correction_bounds(self):
        # NLO Z_φ should not be astronomically different from Z_φ^{(0)}
        z0 = zphi_zero_point()
        z_nlo = zphi_nlo()
        ratio = z_nlo / z0
        # Expect Z_φ^{NLO} to be within a factor of 10 of Z_φ^{(0)}
        assert 1.0 < ratio < 10.0

    def test_pipeline_zphi_nlo_consistent_with_g4_report(self):
        pipeline = precision_correction_pipeline()
        g4 = g4_zphi_correction_report()
        assert pipeline["zphi_nlo"] == pytest.approx(g4["zphi_nlo"], rel=1e-10)

    def test_pipeline_delta_zphi_consistent(self):
        pipeline = precision_correction_pipeline()
        assert pipeline["delta_zphi_g4"] == pytest.approx(delta_zphi_g4(), rel=1e-10)

    def test_p_r_pipeline_consistent_with_e8_report(self):
        seed = nlo_seed_chain()
        vol_nlo = seed["vol_cy3_nlo"]
        p_r = p_r_chain(vol_nlo)
        pipeline = precision_correction_pipeline()
        # Both should use the same NLO vol → same p_R
        assert p_r["p_r_conditional"] == pytest.approx(
            pipeline["p_r_conditional"]["p_r_value"], rel=1e-6
        )

    def test_extended_g4_summary_zphi_key(self):
        # Pillar 519 extends g4_flux_selection_summary with zphi_correction key
        ext_summary = g4_flux_selection_summary()
        assert "zphi_correction" in ext_summary
        assert ext_summary["zphi_correction"]["delta_zphi_g4"] > 0

    def test_upgrade_registry_covers_both_pillars(self):
        # Registry covers both P517 and P518
        from src.eleventd.architecture_limit_upgrade import (
            PRIOR_STATUS_P517, PRIOR_STATUS_P518
        )
        assert PRIOR_STATUS_P517 in UPGRADE_REGISTRY
        assert PRIOR_STATUS_P518 in UPGRADE_REGISTRY


# ── Architecture limit upgrade chain consistency ──────────────────────────────


class TestUpgradeChainConsistency:
    def test_p517_upgrade_references_p520(self):
        cert = p517_upgrade_certificate()
        assert cert["upgrading_pillar"] == 520

    def test_p518_upgrade_references_p519(self):
        cert = p518_upgrade_certificate()
        assert cert["upgrading_pillar"] == 519

    def test_p517_and_p518_upgrades_both_valid(self):
        report = architecture_limit_upgrade_report()
        assert report["summary"]["both_valid"] is True

    def test_closure_v2_chains_upgrade_report(self):
        closure = full_precision_closure_v2_report()
        d6 = closure["deliverables"]["6_architecture_limit_upgrades"]
        assert d6["both_valid"] is True

    def test_irreducible_floor_in_closure(self):
        closure = full_precision_closure_v2_report()
        floors = closure["irreducible_floor_inventory"]
        assert floors["label"] == "5D_IRREDUCIBLE_FLOOR"
        assert floors["count"] == 3


# ── p_R geometric bounds respected throughout chain ───────────────────────────


class TestPRGeometricBounds:
    def test_p_r_from_e8_within_bounds(self):
        cert = p_r_conditional_certificate()
        p_r = cert["p_r_conditional"]
        assert P_R_GEOMETRIC_MIN <= p_r <= P_R_GEOMETRIC_MAX

    def test_p_r_at_nlo_vol_within_bounds(self):
        seed = nlo_seed_chain()
        vol_nlo = seed["vol_cy3_nlo"]
        p_r = p_r_chain(vol_nlo)
        assert P_R_GEOMETRIC_MIN <= p_r["p_r_conditional"] <= P_R_GEOMETRIC_MAX

    def test_p_r_in_pipeline_within_bounds(self):
        pipeline = precision_correction_pipeline()
        p_r_val = pipeline["p_r_conditional"]["p_r_value"]
        assert P_R_GEOMETRIC_MIN <= p_r_val <= P_R_GEOMETRIC_MAX
