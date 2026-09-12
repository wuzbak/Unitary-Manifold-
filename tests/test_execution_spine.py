# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
from __future__ import annotations

import json
from pathlib import Path

from src.infrastructure.execution_spine import (
    EXECUTION_SPINE_SCHEMA_VERSION,
    ExecutionSpineHealthCheck,
    ExecutionSpineRecord,
    build_fail_closed_governance,
)
from src.quantum.execution import ExecutionConfig, run_time_evolution, save_run_artifact
from src.quantum.fermi_hubbard import build_fermi_hubbard_1d
from src.quantum.xdiag_bridge.workflow import XDiagBridgeArtifact, save_bridge_artifact


def test_execution_spine_record_roundtrip() -> None:
    record = ExecutionSpineRecord(
        surface_id="surface-1",
        surface_kind="artifact",
        lane="psicat_control_plane",
        status="READY",
        summary="Governed artifact.",
        canonical_paths=["9-INFRASTRUCTURE/EXECUTION_SPINE_CONVERGENCE_CHARTER.md"],
        sources=["tests/test_execution_spine.py"],
        governance=build_fail_closed_governance(
            epistemic_label="GOVERNANCE",
            promotion_rule="Receipts required.",
            residual_blockers=["Benchmark evidence pending."],
        ),
        compatibility={"primary_endpoint": "/api/psicat/example"},
        health_checks=[
            ExecutionSpineHealthCheck(
                check_id="doc_present",
                passed=True,
                status="pass",
                summary="Document exists.",
                details={"count": 1},
                sources=["tests/test_execution_spine.py"],
            ),
        ],
        promotion={"eligible": False, "gate": "benchmark_required"},
    )
    restored = ExecutionSpineRecord.from_dict(record.to_dict())
    assert restored.schema_version == EXECUTION_SPINE_SCHEMA_VERSION
    assert restored.health_checks[0].check_id == "doc_present"
    assert restored.governance["fail_closed"] is True


def test_execution_spine_record_from_dict_preserves_missing_timestamp() -> None:
    restored = ExecutionSpineRecord.from_dict(
        {
            "surface_id": "surface-2",
            "surface_kind": "artifact",
            "lane": "psicat_control_plane",
            "status": "READY",
            "summary": "No timestamp payload.",
        }
    )
    assert restored.generated_at_utc is None


def test_quantum_run_artifact_contains_execution_spine(tmp_path: Path) -> None:
    model = build_fermi_hubbard_1d(n_sites=2, hopping_t=1.0, interaction_u=2.0)
    cfg = ExecutionConfig(total_time=0.1, trotter_steps=2)
    result = run_time_evolution(model, cfg)
    path = save_run_artifact(result, str(tmp_path))
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["execution_spine"]["schema_version"] == EXECUTION_SPINE_SCHEMA_VERSION
    assert payload["execution_spine"]["lane"] == "lane_e_quantum_adjacent"
    assert payload["execution_spine"]["governance"]["epistemic_label"] == "ADJACENT_TRACK"
    assert payload["execution_spine"]["governance"]["fail_closed"] is True
    assert payload["execution_spine"]["health_checks"][0]["check_id"] == "observable_history_present"
    assert payload["execution_spine"]["promotion"]["gate"] == "adjacent_only"


def test_xdiag_bridge_artifact_contains_execution_spine(tmp_path: Path) -> None:
    artifact = XDiagBridgeArtifact(
        manifest={
            "run_id": "bridge-demo",
            "bridge": {"integration_lane": "xdiag_um_bridge_adjacent"},
        },
        spectra=[-0.5],
        observables={"double_occupancy": 0.5},
        backend_payload={"device": "xdiag"},
    )
    path = save_bridge_artifact(artifact, str(tmp_path))
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["execution_spine"]["surface_kind"] == "xdiag_bridge_artifact"
    assert payload["execution_spine"]["compatibility"]["optional_backend"] == "xdiag"
    assert payload["execution_spine"]["governance"]["fail_closed"] is True
    assert payload["execution_spine"]["health_checks"][0]["check_id"] == "spectra_present"
    assert payload["execution_spine"]["promotion"]["gate"] == "adjacent_only"
