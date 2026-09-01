# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
from __future__ import annotations

import sys
from pathlib import Path

import pytest

APP_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_ROOT))

from AxiomZero import IDENTITY
from AxiomZero.sprint_ba_status import (
    STATUS_LABELS,
    SPRINT_BA_STATUS,
    get_pillar_status,
    get_sprint_ba_status,
    validate_sprint_ba_status,
)


def test_status_module_registered_range():
    assert SPRINT_BA_STATUS["pillar_window"] == {"start": "P837", "end": "P860", "count": 24}


def test_status_labels_are_honest_and_complete():
    assert STATUS_LABELS == ("CLOSED", "PARTIAL", "OPEN")
    assert SPRINT_BA_STATUS["status_labels"] == ["CLOSED", "PARTIAL", "OPEN"]


def test_all_pillars_present_in_order():
    assert list(SPRINT_BA_STATUS["pillars"]) == [f"P{pillar_number}" for pillar_number in range(837, 861)]


def test_summary_counts_match_expected_closures():
    assert SPRINT_BA_STATUS["summary"] == {"CLOSED": 2, "PARTIAL": 1, "OPEN": 21}


def test_p849_is_closed_for_k_cs_74():
    entry = get_pillar_status("P849")
    assert entry["status"] == "CLOSED"
    assert "74" in entry["summary"]
    assert entry["artifact"] == "k_CS=74"


def test_p853_is_partial_for_phi0_equals_one():
    entry = get_pillar_status("P853")
    assert entry["status"] == "PARTIAL"
    assert "φ₀ = 1" in entry["summary"]
    assert entry["artifact"] == "phi0=1"


def test_p858_tracks_dimensional_chain_closure():
    entry = get_pillar_status("P858")
    assert entry["status"] == "CLOSED"
    assert entry["step_count"] == 7
    assert entry["artifact"].startswith("11D")
    assert entry["artifact"].endswith("4D")


def test_unknown_pillars_remain_open():
    assert get_pillar_status("P837")["status"] == "OPEN"
    assert get_pillar_status("P860")["status"] == "OPEN"


def test_get_sprint_ba_status_returns_copy():
    payload = get_sprint_ba_status()
    payload["pillars"]["P849"]["status"] = "OPEN"
    assert SPRINT_BA_STATUS["pillars"]["P849"]["status"] == "CLOSED"


def test_get_pillar_status_returns_copy():
    entry = get_pillar_status("P849")
    entry["status"] = "OPEN"
    assert get_pillar_status("P849")["status"] == "CLOSED"


def test_validator_accepts_default_payload():
    result = validate_sprint_ba_status()
    assert result["valid"] is True
    assert all(result["checks"].values())


def test_validator_detects_invalid_label():
    payload = get_sprint_ba_status()
    payload["pillars"]["P837"]["status"] = "MAYBE"
    result = validate_sprint_ba_status(payload)
    assert result["valid"] is False
    assert result["checks"]["labels_ok"] is False


def test_unknown_pillar_raises_key_error():
    with pytest.raises(KeyError):
        get_pillar_status("P900")


def test_readme_mentions_sprint_ba_and_v25_5():
    readme = (APP_ROOT / "README.md").read_text(encoding="utf-8")
    assert "Sprint BA" in readme
    assert "v25.5" in readme


def test_identity_exposes_repository_version():
    assert IDENTITY["unitary_manifold_version"] == "v25.5"
    assert IDENTITY["sprint"] == "BA"
