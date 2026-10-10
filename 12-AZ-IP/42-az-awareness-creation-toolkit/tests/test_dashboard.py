# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from az_awareness_creation_toolkit.dashboard import build_home_health_snapshot


def test_home_health_snapshot_composes_all_three_sources():
    snapshot = build_home_health_snapshot().as_dict()
    assert snapshot["product_count"] >= 41
    assert snapshot["research_debt"]["total_items"] > 0
    assert set(snapshot["research_debt"].keys()) == {
        "n_open", "n_closed", "total_items", "open_fraction", "closed_fraction", "by_status",
    }
    assert sum(snapshot["falsification_fronts"].values()) == 7
    assert len(snapshot["falsification_detail"]) == 7
    assert snapshot["generated_at"]


def test_home_health_snapshot_is_json_serializable():
    import json

    snapshot = build_home_health_snapshot().as_dict()
    json.dumps(snapshot)  # must not raise
