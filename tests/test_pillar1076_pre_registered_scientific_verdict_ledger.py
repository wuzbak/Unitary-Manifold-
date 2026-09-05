# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1076_pre_registered_scientific_verdict_ledger import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    REGISTRATION_TAG,
    TRACK_C_PILLARS,
    pillar1076_summary,
    scientific_verdict_ledger_report,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1076
    assert PILLAR_GATE == "SPRINT_CF_TRACK_C_PRE_REGISTERED_SCIENTIFIC_VERDICT_LEDGER"
    assert (
        PILLAR_STATUS
        == "SPRINT_CF_TRACK_C_PRE_REGISTERED_SCIENTIFIC_VERDICT_LEDGER_COMPLETE"
    )
    assert PILLAR_VALID is True


def test_ledger_registers_two_falsifiers() -> None:
    r = scientific_verdict_ledger_report()
    assert TRACK_C_PILLARS == [1074, 1075]
    assert len(r["falsifier_entries"]) == 2
    assert r["all_track_c_theorems_stated"] is True
    assert r["total_lean4_delta"] == 20


def test_post_hoc_softening_forbidden() -> None:
    r = scientific_verdict_ledger_report()
    assert r["post_hoc_softening_forbidden"] is True
    assert r["registration_tag"] == REGISTRATION_TAG


def test_summary() -> None:
    s = pillar1076_summary()
    assert s["pillar"] == 1076
    assert s["total_lean4_delta"] == 20
