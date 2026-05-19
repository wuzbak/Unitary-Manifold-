# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
from src.core.pillar225_juno_hyperk_neutron_oscillation_readiness import (
    ADJACENCY_TRACK_LABEL,
    pillar225_readiness_brief,
    readiness_components,
)


def test_components_shape():
    comps = readiness_components()
    assert len(comps) == 4
    assert all("score" in c for c in comps)


def test_readiness_brief_status():
    brief = pillar225_readiness_brief()
    assert brief["pillar"] == 225
    assert brief["adjacency_label"] == ADJACENCY_TRACK_LABEL
    assert brief["status"] in {"READY", "PARTIAL_READINESS"}
