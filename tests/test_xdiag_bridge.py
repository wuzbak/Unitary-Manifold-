# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.quantum.execution import ExecutionConfig
from src.quantum.fermi_hubbard import build_fermi_hubbard_1d
from src.quantum.xdiag_bridge import (
    ParityTolerance,
    RoutingThresholds,
    assert_parity,
    build_xdiag_bridge_spec,
    choose_route,
    export_um_to_xdiag,
    ingest_xdiag_to_um_artifact,
    save_bridge_artifact,
    spec_from_dict,
)


def _build_model_and_config() -> tuple[object, ExecutionConfig]:
    model = build_fermi_hubbard_1d(n_sites=3, hopping_t=1.0, interaction_u=2.5, periodic=True)
    cfg = ExecutionConfig(total_time=0.2, trotter_steps=4, mapping="jw", backend="simulator", shots=1024)
    return model, cfg


def test_bridge_spec_roundtrip_and_versioned_provenance() -> None:
    model, cfg = _build_model_and_config()
    spec = build_xdiag_bridge_spec(
        model=model,
        config=cfg,
        repository="wuzbak/Unitary-Manifold-",
        repo_revision="abc123",
        notes="adjacent track",
    )

    loaded = spec_from_dict(spec.to_dict())
    assert loaded.schema_version == "1.0.0"
    assert loaded.integration_lane == "xdiag_um_bridge_adjacent"
    assert loaded.provenance.steward_approval_required is False
    assert loaded.provenance.steward_approved is True
    assert loaded.provenance.repo_revision == "abc123"


def test_deterministic_run_id_is_stable() -> None:
    model, cfg = _build_model_and_config()
    spec = build_xdiag_bridge_spec(
        model=model,
        config=cfg,
        repository="wuzbak/Unitary-Manifold-",
        repo_revision="abc123",
    )

    assert spec.deterministic_run_id() == spec.deterministic_run_id()


def test_um_to_xdiag_payload_contains_hamiltonian_terms() -> None:
    model, cfg = _build_model_and_config()
    payload = export_um_to_xdiag(
        model=model,
        config=cfg,
        repository="wuzbak/Unitary-Manifold-",
        repo_revision="deadbeef",
    )

    assert payload.run_id.startswith("xdiag_3s_jw_200ms_4tr_")
    assert len(payload.hamiltonian_terms) > 0


def test_xdiag_ingest_creates_um_style_manifest() -> None:
    model, cfg = _build_model_and_config()
    payload = export_um_to_xdiag(model=model, config=cfg, repository="wuzbak/Unitary-Manifold-")

    artifact = ingest_xdiag_to_um_artifact(
        payload=payload,
        xdiag_result={
            "eigenvalues": [-1.2, -0.8],
            "observables": {"staggered_magnetization": 0.25},
            "device": "xdiag_sparse_cpu",
            "wall_clock_seconds": 0.56,
            "peak_memory_mb": 42.0,
        },
    )

    assert artifact.manifest["run_id"] == payload.run_id
    assert artifact.manifest["backend"] == "xdiag_bridge"
    bridge = artifact.manifest["bridge"]
    assert isinstance(bridge, dict)
    assert bridge["steward_approval_required"] is False
    assert bridge["steward_approved"] is True
    assert artifact.backend_payload["device"] == "xdiag_sparse_cpu"


def test_xdiag_ingest_missing_required_fields_fails_fast() -> None:
    model, cfg = _build_model_and_config()
    payload = export_um_to_xdiag(model=model, config=cfg, repository="wuzbak/Unitary-Manifold-")

    with pytest.raises(ValueError, match="missing required fields"):
        ingest_xdiag_to_um_artifact(payload=payload, xdiag_result={"eigenvalues": [-1.0]})


def test_save_bridge_artifact_writes_json(tmp_path: Path) -> None:
    model, cfg = _build_model_and_config()
    payload = export_um_to_xdiag(model=model, config=cfg, repository="wuzbak/Unitary-Manifold-")
    artifact = ingest_xdiag_to_um_artifact(
        payload=payload,
        xdiag_result={"eigenvalues": [-1.0], "observables": {"staggered_magnetization": 0.0}},
    )

    path = save_bridge_artifact(artifact, str(tmp_path))
    parsed = json.loads(path.read_text(encoding="utf-8"))
    assert path.name.endswith(".xdiag_bridge.json")
    assert parsed["manifest"]["run_id"] == payload.run_id


def test_parity_gate_pass_and_fail_fast() -> None:
    tol = ParityTolerance(energy_abs_tol=1e-4, gap_abs_tol=1e-4, observable_abs_tol=1e-4)

    assert_parity(
        um_metrics={"ground_energy": -1.0, "first_gap": 0.2, "staggered_magnetization": 0.3},
        xdiag_metrics={"ground_energy": -1.00001, "first_gap": 0.20001, "staggered_magnetization": 0.30001},
        tolerance=tol,
    )

    with pytest.raises(ValueError, match="parity gate failed"):
        assert_parity(
            um_metrics={"ground_energy": -1.0, "first_gap": 0.2, "staggered_magnetization": 0.3},
            xdiag_metrics={"ground_energy": -0.9, "first_gap": 0.2, "staggered_magnetization": 0.3},
            tolerance=tol,
        )


def test_routing_rules_are_deterministic() -> None:
    thresholds = RoutingThresholds(exact_dense_max_modes=12, sparse_min_modes=14)

    assert choose_route(10, thresholds=thresholds).route == "um_exact_dense"
    assert choose_route(13, thresholds=thresholds).route == "bridge_crosscheck"
    assert choose_route(16, thresholds=thresholds).route == "xdiag_sparse"
    assert choose_route(7, thresholds=thresholds, force_engine="xdiag").route == "xdiag_sparse"

    with pytest.raises(ValueError, match="force_engine"):
        choose_route(7, thresholds=thresholds, force_engine="invalid")
