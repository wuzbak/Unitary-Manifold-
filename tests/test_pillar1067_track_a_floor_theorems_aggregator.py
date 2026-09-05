# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import src.core.pillar1067_track_a_floor_theorems_aggregator as module

from src.core.pillar1067_track_a_floor_theorems_aggregator import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    TRACK_A_LANES,
    pillar1067_summary,
    track_a_floor_theorems_aggregator,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1067
    assert PILLAR_GATE == "SPRINT_CF_TRACK_A_FLOOR_THEOREMS_AGGREGATOR"
    assert PILLAR_STATUS == "SPRINT_CF_TRACK_A_FLOOR_THEOREMS_AGGREGATOR_COMPLETE"
    assert PILLAR_VALID is True


def test_five_lanes_covered() -> None:
    assert len(TRACK_A_LANES) == 5


def test_declared_theorem_names_are_not_verified_physical_proofs() -> None:
    r = track_a_floor_theorems_aggregator()
    assert r["all_theorems_valid"] is False
    assert r["all_justifications_upgraded_to_lean4"] is False
    assert r["all_packets_valid"] is True
    assert r["scientific_progress"] is False
    assert r["verified_physical_theorem_count"] == 0
    assert r["runtime_labels_untouched"] is True
    assert r["total_lean4_delta"] == 48
    assert r["theorem_count_evidence_status"] == "DECLARED_NOT_VERIFIED"
    assert r["valid"] is True


def test_summary() -> None:
    s = pillar1067_summary()
    assert s["pillar"] == 1067


def test_theorem_flag_without_compilation_and_proof_evidence_is_not_proof(monkeypatch) -> None:
    report = module.cmb_amp_lower_bound_theorem_report()
    report.update(physical_theorem_proved=True, lean4_theorem_delta=100000)
    monkeypatch.setattr(module, "cmb_amp_lower_bound_theorem_report", lambda: report)
    result = module.track_a_floor_theorems_aggregator()
    assert result["verified_physical_theorem_count"] == 0
    assert result["scientific_progress"] is False
    assert result["all_theorems_valid"] is False
