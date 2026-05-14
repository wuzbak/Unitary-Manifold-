# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
tests/test_xdiag_bridge_production.py
======================================
Production-parity tests for the UM ↔ XDiag bridge (v10.55 enhancement).

Covers:
- Schema version guard (assert_schema_version)
- Extended parity report (charge_gap, spin_gap, double_occupancy, staggered_magnetization)
- Multi-metric parity gate with per-metric delta and tolerance
- ParityDelta.passed field
- ParityReport summary string
- production_health_check() end-to-end
- parity_report with optional metrics
- assert_parity raises on failure with informative message

EPISTEMIC STATUS — ADJACENT ENGINEERING LANE (NON-HARDGATE).
"""
from __future__ import annotations

import math

import pytest

from src.quantum.xdiag_bridge.contract import (
    XDIAG_UM_SCHEMA_VERSION,
    assert_schema_version,
    build_xdiag_bridge_spec,
    spec_from_dict,
)
from src.quantum.xdiag_bridge.parity import (
    OPTIONAL_METRICS,
    REQUIRED_METRICS,
    ParityDelta,
    ParityReport,
    ParityTolerance,
    assert_parity,
    parity_report,
)
from src.quantum.xdiag_bridge.workflow import production_health_check


# ===========================================================================
# Schema version guard — assert_schema_version
# ===========================================================================


def test_schema_version_guard_exact_match() -> None:
    payload = {"schema_version": XDIAG_UM_SCHEMA_VERSION}
    assert_schema_version(payload)  # should not raise


def test_schema_version_guard_mismatch_raises() -> None:
    payload = {"schema_version": "0.9.9"}
    with pytest.raises(ValueError, match="schema version mismatch"):
        assert_schema_version(payload, strict=True)


def test_schema_version_guard_missing_key_raises() -> None:
    with pytest.raises(KeyError):
        assert_schema_version({})


def test_schema_version_guard_non_strict_same_major_ok() -> None:
    payload = {"schema_version": "1.0.0"}  # same major
    assert_schema_version(payload, strict=False)  # should not raise


def test_schema_version_guard_non_strict_different_major_raises() -> None:
    payload = {"schema_version": "2.0.0"}
    with pytest.raises(ValueError, match="major schema version mismatch"):
        assert_schema_version(payload, strict=False)


def test_schema_version_constant() -> None:
    assert XDIAG_UM_SCHEMA_VERSION == "1.0.0"


# ===========================================================================
# REQUIRED_METRICS / OPTIONAL_METRICS constants
# ===========================================================================


def test_required_metrics_tuple() -> None:
    assert isinstance(REQUIRED_METRICS, tuple)
    assert "ground_energy" in REQUIRED_METRICS
    assert "first_gap" in REQUIRED_METRICS
    assert "staggered_magnetization" in REQUIRED_METRICS


def test_optional_metrics_tuple() -> None:
    assert isinstance(OPTIONAL_METRICS, tuple)
    assert "charge_gap" in OPTIONAL_METRICS
    assert "spin_gap" in OPTIONAL_METRICS
    assert "double_occupancy" in OPTIONAL_METRICS


def test_required_and_optional_no_overlap() -> None:
    assert set(REQUIRED_METRICS).isdisjoint(set(OPTIONAL_METRICS))


# ===========================================================================
# ParityTolerance
# ===========================================================================


def test_parity_tolerance_defaults() -> None:
    tol = ParityTolerance()
    assert tol.energy_abs_tol == 1e-8
    assert tol.observable_abs_tol == 1e-6


def test_parity_tolerance_tol_for_energy_metrics() -> None:
    tol = ParityTolerance()
    for m in ("ground_energy", "first_gap", "charge_gap", "spin_gap"):
        assert tol.tol_for(m) == tol.energy_abs_tol


def test_parity_tolerance_tol_for_observable_metrics() -> None:
    tol = ParityTolerance()
    for m in ("staggered_magnetization", "double_occupancy"):
        assert tol.tol_for(m) == tol.observable_abs_tol


# ===========================================================================
# ParityDelta
# ===========================================================================


def test_parity_delta_passed_true() -> None:
    d = ParityDelta(
        metric="ground_energy",
        um_value=-1.0,
        xdiag_value=-1.0 + 1e-9,
        abs_delta=1e-9,
        tolerance=1e-8,
        passed=True,
    )
    assert d.passed


def test_parity_delta_passed_false() -> None:
    d = ParityDelta(
        metric="first_gap",
        um_value=1.0,
        xdiag_value=1.1,
        abs_delta=0.1,
        tolerance=1e-8,
        passed=False,
    )
    assert not d.passed


# ===========================================================================
# parity_report — required metrics only
# ===========================================================================


def _good_metrics() -> dict[str, float]:
    return {
        "ground_energy": -2.0,
        "first_gap": 0.5,
        "staggered_magnetization": 0.1,
    }


def test_parity_report_all_pass() -> None:
    um = _good_metrics()
    xd = _good_metrics().copy()
    report = parity_report(um, xd)
    assert report.ok
    assert report.n_metrics_failed == 0
    assert report.n_metrics_checked == 3


def test_parity_report_summary_ok_string() -> None:
    um = _good_metrics()
    report = parity_report(um, um.copy())
    assert "PARITY OK" in report.summary


def test_parity_report_one_metric_fails() -> None:
    um = _good_metrics()
    xd = _good_metrics()
    xd["ground_energy"] = -2.0 + 1.0  # large delta
    report = parity_report(um, xd)
    assert not report.ok
    assert report.n_metrics_failed >= 1


def test_parity_report_summary_failed_string() -> None:
    um = _good_metrics()
    xd = {**_good_metrics(), "ground_energy": 0.0}
    report = parity_report(um, xd)
    assert "PARITY FAILED" in report.summary
    assert "ground_energy" in report.summary


def test_parity_report_deltas_have_passed_field() -> None:
    um = _good_metrics()
    report = parity_report(um, um.copy())
    for d in report.deltas:
        assert isinstance(d, ParityDelta)
        assert d.passed


def test_parity_report_missing_required_um_raises() -> None:
    um = {"ground_energy": -2.0}  # missing first_gap + staggered_magnetization
    xd = _good_metrics()
    with pytest.raises(ValueError, match="Missing required metric in UM"):
        parity_report(um, xd)


def test_parity_report_missing_required_xdiag_raises() -> None:
    um = _good_metrics()
    xd = {"ground_energy": -2.0}
    with pytest.raises(ValueError, match="Missing required metric in XDiag"):
        parity_report(um, xd)


# ===========================================================================
# parity_report — optional metrics
# ===========================================================================


def test_parity_report_includes_optional_when_present() -> None:
    um = {**_good_metrics(), "charge_gap": 1.0, "spin_gap": 0.5}
    xd = {**_good_metrics(), "charge_gap": 1.0, "spin_gap": 0.5}
    report = parity_report(um, xd)
    assert report.n_metrics_checked == 5  # 3 required + 2 optional


def test_parity_report_optional_only_one_dict_skipped() -> None:
    um = {**_good_metrics(), "charge_gap": 1.0}  # only in um
    xd = _good_metrics()                           # not in xd
    report = parity_report(um, xd)
    assert report.n_metrics_checked == 3  # optional charge_gap skipped


def test_parity_report_optional_metric_fail() -> None:
    um = {**_good_metrics(), "charge_gap": 1.0}
    xd = {**_good_metrics(), "charge_gap": 1.0 + 1.0}  # large delta
    report = parity_report(um, xd)
    assert not report.ok
    failed = [d.metric for d in report.deltas if not d.passed]
    assert "charge_gap" in failed


def test_parity_report_full_optional_all_pass() -> None:
    metrics = {
        **_good_metrics(),
        "charge_gap": 1.0,
        "spin_gap": 0.3,
        "double_occupancy": 0.05,
    }
    report = parity_report(metrics, metrics.copy())
    assert report.ok
    assert report.n_metrics_checked == 6  # 3 required + 3 optional


# ===========================================================================
# assert_parity
# ===========================================================================


def test_assert_parity_passes_on_exact_match() -> None:
    um = _good_metrics()
    report = assert_parity(um, um.copy())
    assert report.ok


def test_assert_parity_raises_on_failure() -> None:
    um = _good_metrics()
    xd = {**_good_metrics(), "ground_energy": 100.0}
    with pytest.raises(ValueError, match="parity gate failed"):
        assert_parity(um, xd)


def test_assert_parity_error_message_includes_metric() -> None:
    um = _good_metrics()
    xd = {**_good_metrics(), "staggered_magnetization": 99.0}
    with pytest.raises(ValueError, match="staggered_magnetization"):
        assert_parity(um, xd)


# ===========================================================================
# parity_report — custom tolerances
# ===========================================================================


def test_parity_report_custom_strict_tolerance() -> None:
    tol = ParityTolerance(energy_abs_tol=1e-14)
    um = _good_metrics()
    xd = {**_good_metrics(), "ground_energy": -2.0 + 1e-10}  # > 1e-14
    report = parity_report(um, xd, tolerance=tol)
    assert not report.ok


def test_parity_report_custom_loose_tolerance() -> None:
    tol = ParityTolerance(energy_abs_tol=100.0)
    um = _good_metrics()
    xd = {**_good_metrics(), "ground_energy": -2.0 + 1.0}  # 1 < 100
    report = parity_report(um, xd, tolerance=tol)
    assert report.ok


# ===========================================================================
# production_health_check
# ===========================================================================


def test_production_health_check_passes() -> None:
    result = production_health_check()
    assert result["passed"] is True


def test_production_health_check_schema_version() -> None:
    result = production_health_check()
    assert result["schema_version"] == XDIAG_UM_SCHEMA_VERSION


def test_production_health_check_run_id_non_empty() -> None:
    result = production_health_check()
    assert isinstance(result["run_id"], str)
    assert len(result["run_id"]) > 0


def test_production_health_check_schema_roundtrip_ok() -> None:
    result = production_health_check()
    assert result["schema_roundtrip_ok"] is True


def test_production_health_check_term_count_positive() -> None:
    result = production_health_check()
    assert result["term_count"] > 0


def test_production_health_check_status_string() -> None:
    result = production_health_check()
    assert "PRODUCTION_HEALTH_CHECK_PASSED" in result["status"]


def test_production_health_check_adjacent_lane_label() -> None:
    result = production_health_check()
    assert "adjacent" in result["status"].lower()
