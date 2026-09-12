# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.formal_frontier_work_queues import build_frontier_work_queue


def test_frontier_work_queue_dispatch() -> None:
    action_units = build_frontier_work_queue("ACTION_TO_EVOLUTION_BOUNDARY")
    aps_units = build_frontier_work_queue("APS_ETA_AXIOM_HALF_CLASS")
    assert len(action_units) == 7
    assert len(aps_units) == 2
    assert build_frontier_work_queue("UNKNOWN_ROW") == []
