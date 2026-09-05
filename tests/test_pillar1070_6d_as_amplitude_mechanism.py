# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1070_6d_as_amplitude_mechanism import (
    FREE_PARAMETERS_INTRODUCED,
    HARDGATE_PILLARS_TOUCHED,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    PLANCK_A_S,
    SIX_D_ENHANCEMENT_FACTOR,
    as_mechanism_report,
    pillar1070_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1070
    assert PILLAR_GATE == "SPRINT_CF_TRACK_B_6D_AS_AMPLITUDE_MECHANISM"
    assert PILLAR_STATUS == "SPRINT_CF_TRACK_B_6D_AS_AMPLITUDE_MECHANISM_ATTEMPTED"
    assert PILLAR_VALID is True


def test_no_new_free_parameters() -> None:
    assert FREE_PARAMETERS_INTRODUCED == []


def test_no_hardgate_pillars_touched() -> None:
    assert HARDGATE_PILLARS_TOUCHED == []


def test_enhancement_does_not_close_gap() -> None:
    r = as_mechanism_report()
    assert SIX_D_ENHANCEMENT_FACTOR > 1.0
    assert SIX_D_ENHANCEMENT_FACTOR < 4.0
    assert PLANCK_A_S == 2.100e-9
    assert r["outcome"] == "EXTENSION_FAILS_WITH_EXACT_RESIDUAL"
    assert r["runtime_label_changed"] is False


def test_summary() -> None:
    s = pillar1070_summary()
    assert s["pillar"] == 1070
