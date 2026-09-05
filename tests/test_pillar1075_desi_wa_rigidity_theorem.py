# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1075_desi_wa_rigidity_theorem import (
    K_CS,
    LEAN4_THEOREM_DELTA,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    STRICT_SYMMETRY_WA,
    desi_wa_rigidity_report,
    pillar1075_summary,
    wa_max,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1075
    assert PILLAR_GATE == "SPRINT_CF_TRACK_C_DESI_WA_RIGIDITY_THEOREM"
    assert PILLAR_STATUS == "SPRINT_CF_TRACK_C_DESI_WA_RIGIDITY_THEOREM_STATED"
    assert PILLAR_VALID is True


def test_wa_max_topological() -> None:
    assert wa_max() == 1.0 / float(K_CS)
    assert STRICT_SYMMETRY_WA == 0.0


def test_report_is_external_rigidity() -> None:
    r = desi_wa_rigidity_report()
    assert r["theorem"]["closure_type"] == "PRE_REGISTERED_EXTERNAL_RIGIDITY_THEOREM"
    assert r["runtime_label_changed"] is False
    assert r["lean4_theorem_delta"] == LEAN4_THEOREM_DELTA


def test_summary() -> None:
    s = pillar1075_summary()
    assert s["pillar"] == 1075
