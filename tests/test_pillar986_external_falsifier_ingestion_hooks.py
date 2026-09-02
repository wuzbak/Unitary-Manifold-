# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 986 — External Falsifier Ingestion Hooks."""

from __future__ import annotations

from src.core.pillar986_external_falsifier_ingestion_hooks import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    ingest_release,
    ingest_release_batch,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 986
    assert PILLAR_STATUS == "EXTERNAL_FALSIFIER_INGESTION_HOOKS_READY"
    assert PILLAR_VALID is True


def test_desi_routing() -> None:
    result = ingest_release({"experiment": "DESI_DR3", "sigma_wa_from_zero": 2.8})
    assert result["result"]["verdict"] == "TENSION"


def test_litebird_gap_is_falsified() -> None:
    result = ingest_release({"experiment": "LITEBIRD", "beta_deg": 0.300, "sigma_deg": 0.02})
    assert result["result"]["verdict"] == "FALSIFIED_GAP"


def test_batch_routing() -> None:
    batch = ingest_release_batch([
        {"experiment": "DESI_DR3", "sigma_wa_from_zero": 1.1},
        {"experiment": "LITEBIRD", "beta_deg": 0.331, "sigma_deg": 0.02},
    ])
    assert batch["n_payloads"] == 2
    assert len(batch["results"]) == 2


def test_alpha_s_ingestion_routes_outside_window() -> None:
    result = ingest_release({"experiment": "PDG_ALPHA_S", "alpha_s_mz": 0.1180, "sigma": 0.0009})
    assert result["result"]["verdict"] == "OUTSIDE_WINDOW_HIGH"
    assert result["result"]["trigger_uv_solver_rerun"] is True
