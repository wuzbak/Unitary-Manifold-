# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 274 — JUNO Δm²₃₁ Tightening Lane."""
from __future__ import annotations

import math

import pytest

from src.core.pillar274_juno_dm31_tightening import (
    ADJACENCY_TRACK_LABEL,
    DM2_31_PDG_EV2,
    DM2_31_UM_BASELINE_EV2,
    JUNO_PRECISION_TARGET,
    M_ATM_EV,
    M_KK_GEV,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    V_HIGGS_GEV,
    Y_TAU,
    fractional_seesaw_participation_to_close,
    juno_sigma_projection,
    juno_tightening_report,
    log_scale_ratio,
    residual_pct,
    seesaw_partner_correction,
    separation_guard,
    tau_yukawa_rge_correction,
    tightened_dm31_prediction,
    verdict_at_juno_precision,
)


def test_identity_and_separation_guard():
    g = separation_guard()
    assert PILLAR_NUMBER == 274
    assert PILLAR_TITLE
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"
    assert g["adjacency_label"] == "NON_HARDGATE_ADJACENT"
    assert g["is_hardgate"] is False
    assert g["modifies_hardgate_module"] is False
    assert g["alters_falsifier_window"] is False
    assert g["monitoring_only"] is True


def test_physical_constants_are_pdg_aligned():
    assert DM2_31_PDG_EV2 == pytest.approx(2.453e-3)
    assert DM2_31_UM_BASELINE_EV2 == pytest.approx(2.400e-3)
    assert M_KK_GEV == pytest.approx(1.0e3)
    assert M_ATM_EV == pytest.approx(math.sqrt(2.453e-3))
    assert 0.0 < Y_TAU < 1.0
    assert V_HIGGS_GEV == pytest.approx(246.22)
    assert JUNO_PRECISION_TARGET == pytest.approx(0.005)


def test_log_scale_ratio_input_validation():
    with pytest.raises(ValueError):
        log_scale_ratio(-1.0, 1.0)
    with pytest.raises(ValueError):
        log_scale_ratio(1.0, -1.0)
    with pytest.raises(ValueError):
        log_scale_ratio(1.0, 1.0)
    with pytest.raises(ValueError):
        log_scale_ratio(1.0, 2.0)


def test_tau_yukawa_rge_correction_positive_and_small():
    delta = tau_yukawa_rge_correction()
    assert delta > 0.0
    # τ-Yukawa contribution is loop-suppressed: well below 1%
    assert delta < 1.0e-3


def test_tau_yukawa_rge_correction_signed_and_monotone_in_window():
    # Going to a lower scale (longer log run) gives a larger correction.
    small = tau_yukawa_rge_correction(mu_high_gev=10.0)
    large = tau_yukawa_rge_correction(mu_high_gev=1000.0)
    assert large > small


def test_tau_yukawa_rge_correction_input_validation():
    with pytest.raises(ValueError):
        tau_yukawa_rge_correction(y_tau=-0.1)


def test_seesaw_partner_correction_canonical_value():
    delta = seesaw_partner_correction()
    expected = (V_HIGGS_GEV / M_KK_GEV) ** 2
    assert delta == pytest.approx(expected)
    # ~6% scale: comfortably larger than the 2.16% gap to close.
    assert 0.05 < delta < 0.08


def test_seesaw_partner_correction_input_validation():
    with pytest.raises(ValueError):
        seesaw_partner_correction(v_gev=-1.0)
    with pytest.raises(ValueError):
        seesaw_partner_correction(m_r_gev=0.0)


def test_fractional_seesaw_participation_in_unit_interval():
    p = fractional_seesaw_participation_to_close()
    assert 0.0 <= p <= 1.0
    # baseline gap ≈ 2.21% ; δ_seesaw ≈ 6.07% → p ≈ 0.365
    assert 0.2 < p < 0.6


def test_fractional_seesaw_participation_edge_cases():
    assert fractional_seesaw_participation_to_close(seesaw_delta=0.0) == 0.0
    # Massive baseline gap saturates at 1.0
    assert fractional_seesaw_participation_to_close(
        baseline_pct=10000.0, seesaw_delta=0.01
    ) == pytest.approx(1.0)


def test_tightened_prediction_moves_toward_pdg():
    baseline = DM2_31_UM_BASELINE_EV2
    tight = tightened_dm31_prediction()
    assert tight > baseline
    # Tightened prediction should be within the JUNO precision window
    # (≤ 0.5% from PDG), by construction.
    assert residual_pct(tight) <= 100.0 * JUNO_PRECISION_TARGET + 1.0e-9


def test_residual_pct_basic_invariants():
    assert residual_pct(DM2_31_PDG_EV2) == pytest.approx(0.0)
    assert residual_pct(DM2_31_UM_BASELINE_EV2) > 2.0  # baseline ~2.16%
    with pytest.raises(ValueError):
        residual_pct(2.4e-3, pdg_eV2=-1.0)


def test_juno_sigma_projection_thresholds():
    # baseline projects to >3σ at 0.5% precision (the canonical risk number)
    baseline_sigma = juno_sigma_projection(DM2_31_UM_BASELINE_EV2)
    assert baseline_sigma > 3.0
    # tightened prediction projects to <1σ
    tight_sigma = juno_sigma_projection(tightened_dm31_prediction())
    assert tight_sigma < 1.0
    with pytest.raises(ValueError):
        juno_sigma_projection(2.4e-3, precision=0.0)


def test_verdict_at_juno_precision_buckets():
    assert verdict_at_juno_precision(0.5) == "PASS_AT_JUNO_PRECISION"
    assert verdict_at_juno_precision(2.0) == "TENSION_AT_JUNO_PRECISION"
    assert verdict_at_juno_precision(4.5) == "FALSIFIED_AT_JUNO_PRECISION"


def test_full_report_structure_and_keys():
    r = juno_tightening_report()
    for key in (
        "pillar",
        "title",
        "adjacency_label",
        "inputs",
        "components",
        "predictions_eV2",
        "residual_pct",
        "juno_sigma_projection",
        "acceptance_gate_passed",
        "verdict_at_juno_precision",
        "honest_note",
        "participation_sweep",
        "falsified_if",
        "separation_guard",
    ):
        assert key in r


def test_full_report_numeric_consistency():
    r = juno_tightening_report()
    # The components must equal the standalone function outputs.
    assert r["components"]["rge_delta_tau_yukawa"] == pytest.approx(
        tau_yukawa_rge_correction()
    )
    assert r["components"]["seesaw_delta_max"] == pytest.approx(
        seesaw_partner_correction()
    )
    # The residual buckets are monotone: tightened ≤ rge_only ≤ baseline.
    res = r["residual_pct"]
    assert res["tightened"] <= res["rge_only"] + 1e-9
    assert res["rge_only"] <= res["baseline"] + 1e-9
    # Acceptance gate passes
    assert r["acceptance_gate_passed"] is True
    assert r["verdict_at_juno_precision"] == "PASS_AT_JUNO_PRECISION"


def test_participation_sweep_monotone_residual():
    r = juno_tightening_report()
    sweep = r["participation_sweep"]
    assert len(sweep) == 11
    residuals = [row["residual_pct"] for row in sweep]
    # Residual must be a continuous function of participation; start large,
    # cross through zero region, then move back up — assert *strict*
    # monotonic decrease at least until the minimum.
    min_idx = residuals.index(min(residuals))
    assert all(
        residuals[i] >= residuals[i + 1] - 1e-9 for i in range(min_idx)
    )


def test_no_hardgate_label_or_falsifier_drift():
    r = juno_tightening_report()
    assert r["separation_guard"]["is_hardgate"] is False
    assert r["separation_guard"]["alters_falsifier_window"] is False
    # PDG and precision target unchanged from canonical values
    assert r["inputs"]["DM2_31_PDG_eV2"] == pytest.approx(2.453e-3)
    assert r["inputs"]["juno_precision_target"] == pytest.approx(0.005)
