# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1069_ftheory_spectral_cover_mh import (
    FREE_PARAMETERS_INTRODUCED,
    HARDGATE_PILLARS_TOUCHED,
    M_H_OBSERVED_GEV,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    ftheory_spectral_cover_report,
    pillar1069_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1069
    assert PILLAR_GATE == "SPRINT_CF_TRACK_B_FTHEORY_SPECTRAL_COVER_MH"
    assert PILLAR_STATUS == "SPRINT_CF_TRACK_B_FTHEORY_SPECTRAL_COVER_MH_ATTEMPTED"
    assert PILLAR_VALID is True


def test_no_new_free_parameters() -> None:
    assert FREE_PARAMETERS_INTRODUCED == []


def test_no_hardgate_pillars_touched() -> None:
    assert HARDGATE_PILLARS_TOUCHED == []


def test_report_reports_binary_outcome() -> None:
    r = ftheory_spectral_cover_report()
    assert r["outcome"] == "EXTENSION_UNESTABLISHED"
    assert r["m_h_ftheory_window_gev"] is None
    assert r["tightening_vs_prior"] is None
    assert r["scientific_progress"] is False
    assert r["runtime_label_changed"] is False
    assert M_H_OBSERVED_GEV == 125.25


def test_summary() -> None:
    s = pillar1069_summary()
    assert s["pillar"] == 1069


def test_assigning_observed_mass_cannot_earn_closure(monkeypatch) -> None:
    import src.core.pillar1069_ftheory_spectral_cover_mh as module

    monkeypatch.setattr(module, "M_H_FTHEORY_LOWER_GEV", M_H_OBSERVED_GEV)
    monkeypatch.setattr(module, "M_H_FTHEORY_UPPER_GEV", M_H_OBSERVED_GEV)
    report = module.ftheory_spectral_cover_report()
    assert report["m_h_ftheory_window_gev"] is None
    assert report["closure_earned"] is False
