# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 989 — Geometric flavor closure layer."""

from __future__ import annotations

from src.core.pillar989_flavor_closure_geometric_layer import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    flavor_closure_observables,
    flavor_closure_summary,
    flavor_geometric_parameters,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 989
    assert PILLAR_STATUS == "FLAVOR_CLOSURE_GEOMETRIC_LAYER_COMPLETE"
    assert PILLAR_VALID is True


def test_parameter_extraction() -> None:
    p = flavor_geometric_parameters()
    assert p["tau"] > 0
    assert p["rho"] > 0


def test_observable_shapes() -> None:
    obs = flavor_closure_observables()
    assert obs["status"] in {"FLAVOR_CLOSURE_GEOMETRIC_DERIVED", "FLAVOR_CLOSURE_GEOMETRIC_PARTIAL"}
    assert len(obs["generation_radii"]) == 3
    assert obs["theta13_deg"] > 0
    assert obs["vub"] > 0


def test_hierarchy_ordering() -> None:
    obs = flavor_closure_observables()
    ratios = obs["mass_hierarchy_ratios"]
    assert 0.0 < ratios["m_u_over_m_t"] < ratios["m_c_over_m_t"] < 1.0


def test_summary_fields() -> None:
    s = flavor_closure_summary()
    assert s["valid"] is True
    assert "runtime_status" in s
