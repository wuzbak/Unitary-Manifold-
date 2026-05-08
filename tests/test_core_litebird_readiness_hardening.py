# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/litebird_readiness_hardening.py."""
from __future__ import annotations

from src.core.litebird_readiness_hardening import (
    CHECKLIST_VERSION,
    PUBLICATION_CHECKLIST,
    RECORD_TARGETS,
    litebird_prepublication_packet,
    litebird_publication_checklist,
    record_litebird_measurement,
)


def test_checklist_version():
    assert CHECKLIST_VERSION == "v10.26"


def test_publication_checklist_shape():
    checklist = litebird_publication_checklist()
    assert len(checklist) == len(PUBLICATION_CHECKLIST)
    assert all(item["required"] for item in checklist)


def test_packet_targets():
    packet = litebird_prepublication_packet()
    assert packet["record_targets"] == RECORD_TARGETS
    assert "falsification_check.py" in packet["command"]


def test_record_measurement_blocks_without_checklist():
    result = record_litebird_measurement(0.331, 0.02, "LiteBIRD draft", checklist_complete=False)
    assert result["ready_to_record"] is False


def test_record_measurement_executes_when_ready():
    result = record_litebird_measurement(0.331, 0.02, "LiteBIRD release")
    assert result["ready_to_record"] is True
    assert result["verdict"] in {"CONFIRMED", "CONSISTENT"}
