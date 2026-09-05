# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1072_hardgate_non_breakage_veto import (
    CORE_HARDGATE_ANCHORS,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    hardgate_non_breakage_veto,
    pillar1072_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1072
    assert PILLAR_GATE == "SPRINT_CF_TRACK_B_HARDGATE_NON_BREAKAGE_VETO"
    assert PILLAR_STATUS == "SPRINT_CF_TRACK_B_HARDGATE_NON_BREAKAGE_VETO_COMPLETE"
    assert PILLAR_VALID is True


def test_veto_passes_no_breakage() -> None:
    r = hardgate_non_breakage_veto()
    assert r["hardgate_breakage_detected"] is False
    assert r["extension_retracted"] is False
    assert r["verdict"] == "NO_HARDGATE_BREAKAGE_DETECTED"
    assert r["all_hardgate_pillars_touched"] == []


def test_core_hardgate_anchors_present() -> None:
    r = hardgate_non_breakage_veto()
    assert set(r["core_hardgate_anchors"]) == set(CORE_HARDGATE_ANCHORS)
    assert "N_W_EQ_5_UNIQUENESS_PILLAR_70D" in CORE_HARDGATE_ANCHORS
    assert "K_CS_EQ_74_DERIVATION_PILLARS_58_537" in CORE_HARDGATE_ANCHORS


def test_summary() -> None:
    s = pillar1072_summary()
    assert s["pillar"] == 1072
    assert s["extension_retracted"] is False
