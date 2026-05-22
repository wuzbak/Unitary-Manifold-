# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Observatory Routing Daemon (ORD)."""
import pytest

from src.core.observatory_routing_daemon import (
    EXPERIMENT_REGISTRY,
    ROUTING_DISPATCH,
    VERDICT_CODES,
    BETA_PREDICTION_CANONICAL,
    BETA_ADMISSIBLE_WINDOW,
    BETA_PREDICTED_GAP,
    NU_MASS_SUM_UM_LOW, NU_MASS_SUM_UM_HIGH, NU_MASS_FALSIFICATION_EV,
    GW_PEAK_FREQ_MHZ_LOW, GW_PEAK_FREQ_MHZ_HIGH, GW_PEAK_FREQ_MHZ_CENTRAL,
    route_juno,
    route_so,
    route_desi,
    route_litebird,
    route_katrin,
    route_lisa,
    route_hyperk,
    route_cmbs4,
    dispatch,
    format_verdict,
    simulate_all_experiments,
    ord_status_report,
    VERDICT_CODES,
)


class TestRegistry:
    def test_registry_non_empty(self):
        assert len(EXPERIMENT_REGISTRY) > 0

    def test_juno_in_registry(self):
        assert "JUNO" in EXPERIMENT_REGISTRY

    def test_so_in_registry(self):
        assert "SIMONS_OBSERVATORY" in EXPERIMENT_REGISTRY

    def test_desi_in_registry(self):
        assert "DESI_DR3" in EXPERIMENT_REGISTRY

    def test_litebird_in_registry(self):
        assert "LITEBIRD" in EXPERIMENT_REGISTRY

    def test_each_entry_has_required_fields(self):
        required = ["full_name", "observable", "pillar", "um_prediction",
                    "falsification_condition"]
        for key, entry in EXPERIMENT_REGISTRY.items():
            for field in required:
                assert field in entry, f"Missing {field} in {key}"

    def test_routing_dispatch_covers_registry(self):
        for key in EXPERIMENT_REGISTRY:
            if key != "DESI_DR4":  # special case
                assert key in ROUTING_DISPATCH, f"{key} not in ROUTING_DISPATCH"


class TestVerdictCodes:
    def test_has_falsified(self):
        assert "FALSIFIED" in VERDICT_CODES

    def test_has_confirmed(self):
        assert "CONFIRMED" in VERDICT_CODES

    def test_has_high_tension(self):
        assert "HIGH_TENSION" in VERDICT_CODES

    def test_falsified_severity(self):
        assert VERDICT_CODES["FALSIFIED"]["severity"] == "CRITICAL"

    def test_confirmed_severity(self):
        assert VERDICT_CODES["CONFIRMED"]["severity"] == "POSITIVE"


class TestBirefringenceConstants:
    def test_canonical_tuple(self):
        assert isinstance(BETA_PREDICTION_CANONICAL, tuple)
        assert len(BETA_PREDICTION_CANONICAL) == 2

    def test_admissible_window_contains_canonical(self):
        for beta in BETA_PREDICTION_CANONICAL:
            assert BETA_ADMISSIBLE_WINDOW[0] <= beta <= BETA_ADMISSIBLE_WINDOW[1]

    def test_gap_inside_window(self):
        assert BETA_ADMISSIBLE_WINDOW[0] < BETA_PREDICTED_GAP[0]
        assert BETA_PREDICTED_GAP[1] < BETA_ADMISSIBLE_WINDOW[1]


class TestRouteJuno:
    def test_no_at_3sigma_confirmed(self):
        r = route_juno("NO", 3.5)
        assert r["verdict"] == "CONFIRMED"

    def test_io_at_3sigma_falsified(self):
        r = route_juno("IO", 3.5)
        assert r["verdict"] == "FALSIFIED"

    def test_io_at_2sigma_tension(self):
        r = route_juno("IO", 2.5)
        assert r["verdict"] in ("HIGH_TENSION",)

    def test_has_verdict_key(self):
        r = route_juno("NO", 3.5)
        assert "verdict" in r

    def test_has_ordering_verdict(self):
        r = route_juno("NO", 3.5)
        assert "ordering_verdict" in r
        assert r["verdict"] == r["ordering_verdict"]

    def test_with_dm31(self):
        r = route_juno("NO", 3.5, dm31_measured=2.454e-3, dm31_sigma_percent=0.5)
        assert "dm31_verdict" in r
        assert r["dm31_verdict"] is not None


class TestRouteSO:
    def test_r_at_um_confirmed(self):
        r = route_so(0.0315, 0.003)
        assert r["verdict"] == "CONFIRMED"

    def test_r_below_010_falsified(self):
        r = route_so(0.005, 0.003)
        assert r["verdict"] == "FALSIFIED"

    def test_has_verdict(self):
        r = route_so(0.030, 0.003)
        assert "verdict" in r


class TestRouteDESI:
    def test_wa_zero_resolved(self):
        r = route_desi(0.0, 0.17)
        assert r["verdict"] == "RESOLVED"

    def test_wa_negative_large_falsified(self):
        # wₐ = -0.60 ± 0.15 → 4σ → FALSIFIED
        r = route_desi(-0.60, 0.15)
        assert r["verdict"] == "FALSIFIED"

    def test_data_label_included(self):
        r = route_desi(-0.30, 0.17, "Test DR")
        assert r["experiment"] == "Test DR"


class TestRouteLiteBIRD:
    def test_in_window_consistent(self):
        # β = 0.270° — in window, close to canonical 0.273°
        r = route_litebird(0.270, 0.01)
        assert r["verdict"] in ("CONSISTENT", "CONFIRMED")

    def test_gap_falsified(self):
        # β = 0.300° — in gap [0.29, 0.31]
        r = route_litebird(0.300, 0.005)
        assert r["verdict"] == "FALSIFIED_GAP"

    def test_outside_window_falsified(self):
        # β = 0.10° — well outside [0.22, 0.38]
        r = route_litebird(0.10, 0.005)
        assert r["verdict"] == "FALSIFIED"

    def test_canonical_confirmed(self):
        # β = 0.273° — right at lower canonical prediction
        r = route_litebird(0.273, 0.005)
        assert r["verdict"] in ("CONFIRMED", "CONSISTENT")

    def test_above_window_high_tension(self):
        # β = 0.42° — just above window [0.22, 0.38]
        r = route_litebird(0.42, 0.005)
        assert r["verdict"] in ("FALSIFIED", "HIGH_TENSION")

    def test_has_beta_measured(self):
        r = route_litebird(0.273, 0.01)
        assert "beta_measured" in r
        assert abs(r["beta_measured"] - 0.273) < 1e-9


class TestRouteKATRIN:
    def test_consistent_low_mass(self):
        r = route_katrin(0.07, 0.05)
        assert r["verdict"] == "CONSISTENT"

    def test_falsified_high_mass(self):
        r = route_katrin(0.8, 0.05)
        assert r["verdict"] == "FALSIFIED"

    def test_has_falsification_threshold(self):
        r = route_katrin(0.1, 0.05)
        assert "falsification_threshold_ev" in r

    def test_um_prediction_range(self):
        r = route_katrin(0.08, 0.05)
        low, high = r["um_prediction_range"]
        assert low == NU_MASS_SUM_UM_LOW
        assert high == NU_MASS_SUM_UM_HIGH


class TestRouteLISA:
    def test_central_prediction_confirmed(self):
        r = route_lisa(7.0, 2.0)
        assert r["verdict"] == "CONFIRMED"

    def test_outside_range_falsified(self):
        # f_peak = 0.1 mHz — below range [1, 30]
        r = route_lisa(0.1, 0.05)
        assert r["verdict"] in ("FALSIFIED", "HIGH_TENSION")

    def test_has_admissible_range(self):
        r = route_lisa(7.0, 2.0)
        assert "admissible_range_mhz" in r
        low, high = r["admissible_range_mhz"]
        assert low == GW_PEAK_FREQ_MHZ_LOW
        assert high == GW_PEAK_FREQ_MHZ_HIGH


class TestDispatch:
    def test_dispatch_juno(self):
        result = dispatch("JUNO", measured_ordering="NO", ordering_sigma=3.5)
        assert result["verdict"] == "CONFIRMED"

    def test_dispatch_so(self):
        result = dispatch("SIMONS_OBSERVATORY", r_measured=0.0315, r_sigma=0.003)
        assert result["verdict"] == "CONFIRMED"

    def test_dispatch_desi(self):
        result = dispatch("DESI_DR3", wa_measured=0.0, wa_sigma=0.17)
        assert result["verdict"] == "RESOLVED"

    def test_dispatch_case_insensitive(self):
        result = dispatch("juno", measured_ordering="NO", ordering_sigma=3.5)
        assert result["verdict"] == "CONFIRMED"

    def test_dispatch_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown experiment"):
            dispatch("UNKNOWN_TELESCOPE", x=1)

    def test_dispatch_litebird(self):
        result = dispatch("LITEBIRD", beta_deg_measured=0.273, beta_sigma_deg=0.01)
        assert "verdict" in result

    def test_dispatch_katrin(self):
        result = dispatch("KATRIN", sum_m_nu_ev=0.08, sum_m_nu_sigma_ev=0.05)
        assert result["verdict"] == "CONSISTENT"

    def test_dispatch_lisa(self):
        result = dispatch("LISA", f_peak_mhz=7.0, f_sigma_mhz=2.0)
        assert result["verdict"] == "CONFIRMED"


class TestFormatVerdict:
    def test_returns_dict(self):
        routing = route_so(0.0315, 0.003)
        fv = format_verdict(routing, "2027-06-01")
        assert isinstance(fv, dict)

    def test_has_ord_version(self):
        routing = route_so(0.0315, 0.003)
        fv = format_verdict(routing)
        assert "v11.18" in fv["ord_version"]

    def test_has_severity(self):
        routing = route_so(0.0315, 0.003)
        fv = format_verdict(routing)
        assert fv["severity"] == "POSITIVE"

    def test_falsified_requires_fast_response(self):
        routing = route_so(0.005, 0.003)
        fv = format_verdict(routing)
        assert fv["required_response_hours"] == 24

    def test_consistent_no_response_required(self):
        routing = route_so(0.030, 0.003)
        fv = format_verdict(routing)
        # CONSISTENT → no response required
        if fv["verdict"] == "CONSISTENT":
            assert fv["required_response_hours"] is None

    def test_documents_to_update_for_falsified(self):
        routing = route_so(0.005, 0.003)
        fv = format_verdict(routing)
        docs = fv["documents_to_update"]
        assert "docs/CLAIM_MASTER_BOARD.md" in docs
        assert "STATUS.md" in docs

    def test_documents_to_update_for_confirmed(self):
        routing = route_so(0.0315, 0.003)
        fv = format_verdict(routing)
        docs = fv["documents_to_update"]
        assert "STATUS.md" in docs


class TestSimulation:
    def test_returns_dict(self):
        sims = simulate_all_experiments()
        assert isinstance(sims, dict)

    def test_juno_um_confirmed(self):
        sims = simulate_all_experiments()
        assert sims["JUNO_um_confirmed"]["verdict"] == "CONFIRMED"

    def test_juno_falsified_scenario(self):
        sims = simulate_all_experiments()
        assert sims["JUNO_falsified_test"]["verdict"] == "FALSIFIED"

    def test_so_confirmed(self):
        sims = simulate_all_experiments()
        assert sims["SO_um_confirmed"]["verdict"] == "CONFIRMED"

    def test_so_falsified(self):
        sims = simulate_all_experiments()
        assert sims["SO_falsified_test"]["verdict"] == "FALSIFIED"

    def test_desi_um_confirmed(self):
        sims = simulate_all_experiments()
        assert sims["DESI_um_confirmed"]["verdict"] == "RESOLVED"

    def test_litebird_gap_falsified(self):
        sims = simulate_all_experiments()
        assert "FALSIFIED" in sims["LITEBIRD_gap_test"]["verdict"]

    def test_katrin_consistent(self):
        sims = simulate_all_experiments()
        assert sims["KATRIN_consistent_test"]["verdict"] == "CONSISTENT"

    def test_lisa_confirmed(self):
        sims = simulate_all_experiments()
        assert sims["LISA_confirmed_test"]["verdict"] == "CONFIRMED"

    def test_has_multiple_scenarios(self):
        sims = simulate_all_experiments()
        assert len(sims) >= 8


class TestStatusReport:
    def test_returns_dict(self):
        report = ord_status_report()
        assert isinstance(report, dict)

    def test_version(self):
        report = ord_status_report()
        assert "v11.18" in report["ord_version"]

    def test_watched_experiments_count(self):
        report = ord_status_report()
        assert report["watched_experiments"] >= 8

    def test_has_critical_falsifiers(self):
        report = ord_status_report()
        assert "critical_falsifiers" in report
        assert "primary" in report["critical_falsifiers"]

    def test_primary_falsifier_is_litebird(self):
        report = ord_status_report()
        assert "LiteBIRD" in report["critical_falsifiers"]["primary"]

    def test_next_expected_experiments(self):
        report = ord_status_report()
        assert "JUNO" in report["next_expected"]
        assert "SIMONS_OBSERVATORY" in report["next_expected"]
