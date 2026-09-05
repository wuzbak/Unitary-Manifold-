# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1074_litebird_beta_gap_sharpness_theorem import (
    ADMISSIBLE_WINDOW_DEG,
    BETA_CANONICAL_DEG,
    BETA_DERIVED_DEG,
    EXCLUDED_GAP_DEG,
    LEAN4_THEOREM_DELTA,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    litebird_beta_gap_sharpness_report,
    pillar1074_summary,
    theorem_statement,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1074
    assert PILLAR_GATE == "SPRINT_CF_TRACK_C_LITEBIRD_BETA_GAP_SHARPNESS_THEOREM"
    assert PILLAR_STATUS == "SPRINT_CF_TRACK_C_LITEBIRD_BETA_GAP_SHARPNESS_THEOREM_STATED"
    assert PILLAR_VALID is True


def test_admissible_window_and_gap_fixed() -> None:
    assert ADMISSIBLE_WINDOW_DEG == (0.22, 0.38)
    assert EXCLUDED_GAP_DEG == (0.29, 0.31)


def test_canonical_and_derived_sectors_are_admissible() -> None:
    thm = theorem_statement()
    assert thm["canonical_sector_admissible"] is True
    assert thm["derived_sector_admissible"] is True
    # Both canonical values sit strictly outside the interior gap.
    for a in BETA_CANONICAL_DEG:
        assert not (EXCLUDED_GAP_DEG[0] < a < EXCLUDED_GAP_DEG[1])
    for a in BETA_DERIVED_DEG:
        assert not (EXCLUDED_GAP_DEG[0] < a < EXCLUDED_GAP_DEG[1])


def test_report_is_pre_registered_falsifier() -> None:
    r = litebird_beta_gap_sharpness_report()
    assert r["theorem"]["closure_type"] == "PRE_REGISTERED_FALSIFIER_GAP_THEOREM"
    assert r["runtime_label_changed"] is False
    assert r["lean4_theorem_delta"] == LEAN4_THEOREM_DELTA


def test_summary() -> None:
    s = pillar1074_summary()
    assert s["pillar"] == 1074
