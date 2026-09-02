# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 982 — Runtime Architecture-Limit Registry."""

from __future__ import annotations

from src.core.pillar982_architecture_limit_registry_runtime import (
    DEEP_LAYER_LINKS,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    RUNTIME_ARCHITECTURE_LIMIT_REGISTRY,
    runtime_architecture_limit_registry,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 982
    assert PILLAR_STATUS == "RUNTIME_ARCHITECTURE_LIMIT_REGISTRY_COMPLETE"
    assert PILLAR_VALID is True


def test_registry_shape() -> None:
    assert len(RUNTIME_ARCHITECTURE_LIMIT_REGISTRY) >= 6
    assert all("lane" in row and "missing_objects" in row for row in RUNTIME_ARCHITECTURE_LIMIT_REGISTRY)
    assert all("deep_layer_ref" in row for row in RUNTIME_ARCHITECTURE_LIMIT_REGISTRY)


def test_runtime_summary() -> None:
    summary = runtime_architecture_limit_registry()
    assert summary["n_rows"] >= 6
    assert summary["open_lanes_mapped"] >= 4
    assert summary["architecture_signal"]["uv_cluster_fraction"] > 0.5
    assert summary["deep_links_covered"] is True


def test_deep_layer_links_present() -> None:
    assert set(DEEP_LAYER_LINKS.keys()) == {"uv_layer_987", "kk_layer_988", "flavor_layer_989"}
