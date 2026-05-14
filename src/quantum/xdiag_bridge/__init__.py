# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
XDiag compatibility bridge for the Unitary Manifold adjacent quantum lane.
"""

from .contract import (
    XDIAG_UM_SCHEMA_VERSION,
    CouplingSpec,
    EvolutionSpec,
    LatticeSpec,
    ObservableSpec,
    ProvenanceSpec,
    SectorSpec,
    XDiagBridgeSpec,
    assert_schema_version,
    build_xdiag_bridge_spec,
    spec_from_dict,
)
from .parity import (
    OPTIONAL_METRICS,
    REQUIRED_METRICS,
    ParityDelta,
    ParityReport,
    ParityTolerance,
    assert_parity,
    parity_report,
)
from .routing import RoutingDecision, RoutingThresholds, choose_route
from .workflow import (
    XDiagBridgeArtifact,
    XDiagExportPayload,
    export_um_to_xdiag,
    ingest_xdiag_to_um_artifact,
    production_health_check,
    save_bridge_artifact,
)

__all__ = [
    "XDIAG_UM_SCHEMA_VERSION",
    "LatticeSpec",
    "CouplingSpec",
    "SectorSpec",
    "ObservableSpec",
    "EvolutionSpec",
    "ProvenanceSpec",
    "XDiagBridgeSpec",
    "assert_schema_version",
    "build_xdiag_bridge_spec",
    "spec_from_dict",
    "XDiagExportPayload",
    "XDiagBridgeArtifact",
    "export_um_to_xdiag",
    "ingest_xdiag_to_um_artifact",
    "production_health_check",
    "save_bridge_artifact",
    "REQUIRED_METRICS",
    "OPTIONAL_METRICS",
    "ParityTolerance",
    "ParityDelta",
    "ParityReport",
    "parity_report",
    "assert_parity",
    "RoutingThresholds",
    "RoutingDecision",
    "choose_route",
]
