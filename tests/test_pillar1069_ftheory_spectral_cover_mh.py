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
    assert r["outcome"] in {
        "EXTENSION_CLOSES_LANE",
        "EXTENSION_FAILS_WITH_EXACT_RESIDUAL",
        "EXTENSION_BREAKS_HARDGATE",
    }
    assert r["runtime_label_changed"] is False
    assert M_H_OBSERVED_GEV == 125.25


def test_summary() -> None:
    s = pillar1069_summary()
    assert s["pillar"] == 1069
