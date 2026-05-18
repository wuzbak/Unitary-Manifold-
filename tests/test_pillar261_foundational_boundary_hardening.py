# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

from src.core.pillar261_foundational_boundary_hardening import (
    ADJACENCY_TRACK_LABEL,
    boundary_no_go_statement,
    foundational_boundary_rows,
    pillar261_foundational_boundary_report,
)


def test_foundational_boundary_rows_shape():
    rows = foundational_boundary_rows()
    assert len(rows) >= 4
    assert all("gate" in row and "promotion_rule" in row for row in rows)


def test_boundary_no_go_statement_has_gate_key():
    statement = boundary_no_go_statement("ADM_FULL_DYNAMICAL_5D")
    assert statement.startswith("NO_GO::ADM_FULL_DYNAMICAL_5D")


def test_pillar261_report_shape():
    report = pillar261_foundational_boundary_report()
    assert report["pillar"] == 261
    assert report["adjacency_label"] == ADJACENCY_TRACK_LABEL
    assert report["status"] in {"OPEN_BOUNDARIES_HARDENED", "TOKEN_SYNC_TENSION"}
    assert "ADM_FULL_DYNAMICAL_5D" in report["open_gates"]
    assert report["separation_guard"] is True
