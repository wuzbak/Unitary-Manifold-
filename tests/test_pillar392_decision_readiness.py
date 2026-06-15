# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Tests for Pillar 392 — Decision Readiness Package v12.8.

Validates decision-window metadata, individual rehearsal drill routing
functions, the full drill suite, and the readiness audit.
"""

import pytest

from src.core.decision_readiness_package_v128 import (
    ObservationalVerdict,
    DecisionWindow,
    DECISION_WINDOWS,
    CANONICAL_DRILL_SCENARIOS,
    get_window,
    run_desi_dr3_drill,
    run_so_dr1_drill,
    run_juno_drill,
    run_litebird_drill,
    run_all_drills,
    decision_readiness_audit,
    ReadinessReport,
    pillar_392_status,
)


# ──────────────────────────────────────────────────────────────────────────────
# Decision window registry
# ──────────────────────────────────────────────────────────────────────────────

class TestDecisionWindowRegistry:

    def test_at_least_six_windows_defined(self):
        assert len(DECISION_WINDOWS) >= 6

    def test_desi_dr3_registered(self):
        w = get_window("DESI_DR3")
        assert w is not None
        assert w.experiment

    def test_so_dr1_registered(self):
        assert get_window("SO_DR1") is not None

    def test_juno_registered(self):
        assert get_window("JUNO") is not None

    def test_litebird_registered(self):
        w = get_window("LITEBIRD")
        assert w is not None
        assert w.expected_year == 2032

    def test_spherex_registered(self):
        assert get_window("SPHEREX") is not None

    def test_cmb_s4_registered(self):
        assert get_window("CMB_S4") is not None

    def test_get_nonexistent_window_returns_none(self):
        assert get_window("NONEXISTENT_WINDOW") is None

    def test_all_windows_have_routing_function(self):
        for w in DECISION_WINDOWS:
            assert w.routing_function, f"{w.name} has no routing function"

    def test_all_windows_have_source_module(self):
        for w in DECISION_WINDOWS:
            assert w.routing_source_module, f"{w.name} has no source module"

    def test_high_tension_windows_preregistered(self):
        high_tension = [
            w for w in DECISION_WINDOWS
            if w.current_verdict in (
                ObservationalVerdict.HIGH_TENSION, ObservationalVerdict.TENSION
            )
        ]
        for w in high_tension:
            assert w.preregistered, f"{w.name} has HIGH_TENSION but is not preregistered"

    def test_near_term_windows_preregistered(self):
        near_term = [w for w in DECISION_WINDOWS if w.expected_year <= 2028]
        for w in near_term:
            assert w.preregistered, f"{w.name} (≤2028) not preregistered"


# ──────────────────────────────────────────────────────────────────────────────
# DESI DR3 drill
# ──────────────────────────────────────────────────────────────────────────────

class TestDesiDR3Drill:

    def test_near_falsification_scenario(self):
        # wₐ = -0.62, σ = 0.18 → 3.44σ → FALSIFIED
        verdict = run_desi_dr3_drill(wa=-0.62, sigma=0.18)
        assert verdict == ObservationalVerdict.FALSIFIED

    def test_high_tension_scenario(self):
        # |wₐ|/σ = 2.75σ → HIGH_TENSION
        verdict = run_desi_dr3_drill(wa=-0.55, sigma=0.20)
        assert verdict == ObservationalVerdict.HIGH_TENSION

    def test_tension_scenario(self):
        # |wₐ|/σ = 2.3σ → TENSION
        verdict = run_desi_dr3_drill(wa=-0.46, sigma=0.20)
        assert verdict == ObservationalVerdict.TENSION

    def test_resolved_scenario(self):
        # wₐ ≈ 0 → CONSISTENT
        verdict = run_desi_dr3_drill(wa=-0.05, sigma=0.25)
        assert verdict == ObservationalVerdict.CONSISTENT

    def test_zero_wa_is_consistent(self):
        verdict = run_desi_dr3_drill(wa=0.0, sigma=0.25)
        assert verdict == ObservationalVerdict.CONSISTENT

    def test_positive_wa_can_falsify(self):
        verdict = run_desi_dr3_drill(wa=0.80, sigma=0.20)
        assert verdict == ObservationalVerdict.FALSIFIED


# ──────────────────────────────────────────────────────────────────────────────
# SO DR1 drill
# ──────────────────────────────────────────────────────────────────────────────

class TestSoDR1Drill:

    def test_um_confirmed(self):
        # r = 0.0315 at σ_r = 0.006 → ~5.25σ detection → CONFIRMED
        verdict = run_so_dr1_drill(r_measured=0.0315, sigma_r=0.006)
        assert verdict == ObservationalVerdict.CONFIRMED

    def test_um_falsified(self):
        # r = 0.008, σ = 0.003, distance from UM = 7.8σ → FALSIFIED
        verdict = run_so_dr1_drill(r_measured=0.008, sigma_r=0.003)
        assert verdict == ObservationalVerdict.FALSIFIED

    def test_act_like_high_tension(self):
        # r < 0.016 → HIGH_TENSION (mimicking ACT DR6)
        verdict = run_so_dr1_drill(r_measured=0.015, sigma_r=0.006)
        assert verdict == ObservationalVerdict.HIGH_TENSION

    def test_intermediate_consistent(self):
        # r = 0.025, σ = 0.008 → not clearly falsified or confirmed
        verdict = run_so_dr1_drill(r_measured=0.025, sigma_r=0.008)
        assert verdict == ObservationalVerdict.CONSISTENT


# ──────────────────────────────────────────────────────────────────────────────
# JUNO drill
# ──────────────────────────────────────────────────────────────────────────────

class TestJunoDrill:

    def test_consistent_match(self):
        verdict = run_juno_drill(dm31_measured=2.452e-3, sigma=0.012e-3)
        assert verdict == ObservationalVerdict.CONSISTENT

    def test_falsified_high_residual(self):
        # 2.600e-3 vs 2.452e-3 → 12.3σ → FALSIFIED
        verdict = run_juno_drill(dm31_measured=2.600e-3, sigma=0.012e-3)
        assert verdict == ObservationalVerdict.FALSIFIED

    def test_tension_moderate_residual(self):
        # 2.477e-3 vs 2.452e-3 → 2.1σ → TENSION
        verdict = run_juno_drill(dm31_measured=2.477e-3, sigma=0.012e-3)
        assert verdict == ObservationalVerdict.TENSION

    def test_pdg_central_value_consistent(self):
        # PDG 2.453e-3 vs UM 2.452e-3 → tiny residual
        verdict = run_juno_drill(dm31_measured=2.453e-3, sigma=0.012e-3)
        assert verdict == ObservationalVerdict.CONSISTENT


# ──────────────────────────────────────────────────────────────────────────────
# LiteBIRD drill
# ──────────────────────────────────────────────────────────────────────────────

class TestLiteBIRDDrill:

    def test_primary_sector_confirmed(self):
        # β = 0.331°, σ = 0.020° → within 1σ of primary
        verdict = run_litebird_drill(beta_deg=0.331, sigma_deg=0.020)
        assert verdict == ObservationalVerdict.CONFIRMED

    def test_shadow_sector_confirmed(self):
        # β = 0.273°, σ = 0.020° → within 1σ of shadow
        verdict = run_litebird_drill(beta_deg=0.273, sigma_deg=0.020)
        assert verdict == ObservationalVerdict.CONFIRMED

    def test_below_admissible_window_falsified(self):
        # β = 0.14°, σ = 0.015° → (0.22−0.14)/0.015 = 5.3σ below window → FALSIFIED
        verdict = run_litebird_drill(beta_deg=0.14, sigma_deg=0.015)
        assert verdict == ObservationalVerdict.FALSIFIED

    def test_above_admissible_window_falsified(self):
        # β = 0.42°, σ = 0.010° → 4σ above 0.38° → FALSIFIED
        verdict = run_litebird_drill(beta_deg=0.42, sigma_deg=0.010)
        assert verdict == ObservationalVerdict.FALSIFIED

    def test_intersector_gap_falsified(self):
        # β = 0.300°, σ = 0.005° → in gap (0.29°, 0.31°) → FALSIFIED
        verdict = run_litebird_drill(beta_deg=0.300, sigma_deg=0.005)
        assert verdict == ObservationalVerdict.FALSIFIED

    def test_gap_boundary_not_falsified(self):
        # β = 0.300°, σ = 0.050° → large uncertainty covers both sectors
        verdict = run_litebird_drill(beta_deg=0.300, sigma_deg=0.050)
        # Not falsified at 3σ with that large uncertainty
        assert verdict != ObservationalVerdict.FALSIFIED


# ──────────────────────────────────────────────────────────────────────────────
# Full drill suite
# ──────────────────────────────────────────────────────────────────────────────

class TestFullDrillSuite:

    def test_all_scenarios_return_results(self):
        results = run_all_drills()
        assert len(results) == len(CANONICAL_DRILL_SCENARIOS)

    def test_all_results_have_required_keys(self):
        results = run_all_drills()
        required_keys = {"window", "scenario", "mock_value", "mock_sigma",
                         "expected", "actual", "passed"}
        for r in results:
            assert required_keys <= set(r.keys()), f"Missing keys in {r}"

    def test_canonical_scenarios_all_pass(self):
        results = run_all_drills()
        failed = [r for r in results if not r["passed"]]
        assert not failed, (
            f"Rehearsal drill failures: {failed}"
        )


# ──────────────────────────────────────────────────────────────────────────────
# Readiness audit
# ──────────────────────────────────────────────────────────────────────────────

class TestReadinessAudit:

    def test_audit_returns_report(self):
        report = decision_readiness_audit()
        assert isinstance(report, ReadinessReport)

    def test_report_has_windows(self):
        report = decision_readiness_audit()
        assert len(report.windows) > 0

    def test_summary_structure(self):
        report = decision_readiness_audit()
        s = report.summary()
        assert "total_windows" in s
        assert "near_term_windows" in s
        assert "drill_pass_rate" in s
        assert "all_drills_pass" in s

    def test_all_canonical_drills_pass_in_audit(self):
        report = decision_readiness_audit()
        assert report.all_drills_pass, (
            f"Failed drills: {report.failed_drills()}"
        )

    def test_near_term_windows_are_ready(self):
        report = decision_readiness_audit()
        s = report.summary()
        assert s["near_term_ready"] == s["near_term_windows"], (
            f"Not all near-term windows ready: {report.unready_windows()}"
        )


# ──────────────────────────────────────────────────────────────────────────────
# Pillar status
# ──────────────────────────────────────────────────────────────────────────────

class TestPillar392Status:

    def test_status_structure(self):
        status = pillar_392_status()
        assert status["pillar"] == 392
        assert status["label"] == "ADJACENT_TRACK"
        assert status["hils_status"] == "ACTIVE"

    def test_windows_covered(self):
        status = pillar_392_status()
        assert "DESI_DR3" in status["windows_covered"]
        assert "LITEBIRD" in status["windows_covered"]

    def test_readiness_summary_present(self):
        status = pillar_392_status()
        assert "readiness_summary" in status

    def test_high_tension_windows_identified(self):
        status = pillar_392_status()
        high_tension = status["high_tension_windows"]
        # DESI and ACT/SO are known HIGH_TENSION
        assert len(high_tension) >= 1
