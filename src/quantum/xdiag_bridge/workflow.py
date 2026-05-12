# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/quantum/xdiag_bridge/workflow.py
====================================
Bidirectional UM ↔ XDiag workflow helpers.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json

import numpy as np

from src.quantum.execution import ExecutionConfig
from src.quantum.fermi_hubbard import FermiHubbardHamiltonian

from .contract import XDiagBridgeSpec, build_xdiag_bridge_spec


@dataclass(frozen=True)
class XDiagExportPayload:
    run_id: str
    spec: XDiagBridgeSpec
    hamiltonian_terms: list[dict[str, object]]

    def to_dict(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "spec": self.spec.to_dict(),
            "hamiltonian_terms": self.hamiltonian_terms,
        }


@dataclass(frozen=True)
class XDiagBridgeArtifact:
    manifest: dict[str, object]
    spectra: list[float]
    observables: dict[str, object]
    backend_payload: dict[str, object]


def _serialize_term(coefficient: complex, operators: tuple[tuple[int, bool], ...]) -> dict[str, object]:
    return {
        "coefficient": {
            "real": float(np.real(coefficient)),
            "imag": float(np.imag(coefficient)),
        },
        "operators": [{"mode": int(mode), "creation": bool(creation)} for mode, creation in operators],
    }


def export_um_to_xdiag(
    model: FermiHubbardHamiltonian,
    config: ExecutionConfig,
    repository: str,
    repo_revision: str = "unknown",
    steward_approved: bool = False,
    notes: str = "",
) -> XDiagExportPayload:
    spec = build_xdiag_bridge_spec(
        model=model,
        config=config,
        repository=repository,
        repo_revision=repo_revision,
        steward_approved=steward_approved,
        notes=notes,
    )
    run_id = spec.deterministic_run_id()
    terms = [_serialize_term(t.coefficient, t.operators) for t in model.fermionic_terms()]
    return XDiagExportPayload(run_id=run_id, spec=spec, hamiltonian_terms=terms)


def ingest_xdiag_to_um_artifact(
    payload: XDiagExportPayload,
    xdiag_result: dict[str, object],
) -> XDiagBridgeArtifact:
    required = ("eigenvalues", "observables")
    missing = [k for k in required if k not in xdiag_result]
    if missing:
        raise ValueError(f"xdiag_result missing required fields: {missing}")

    eigenvalues_raw = xdiag_result["eigenvalues"]
    if not isinstance(eigenvalues_raw, list):
        raise ValueError("xdiag_result['eigenvalues'] must be a list")

    observables = xdiag_result["observables"]
    if not isinstance(observables, dict):
        raise ValueError("xdiag_result['observables'] must be an object")

    manifest = {
        "run_id": payload.run_id,
        "created_at_utc": payload.spec.provenance.generated_at_utc,
        "n_sites": payload.spec.lattice.n_sites,
        "n_modes": payload.spec.lattice.n_modes,
        "mapping": payload.spec.evolution.mapping,
        "backend": "xdiag_bridge",
        "total_time": payload.spec.evolution.total_time,
        "trotter_steps": payload.spec.evolution.trotter_steps,
        "parameters": {
            "hopping_t": payload.spec.couplings.hopping_t,
            "interaction_u": payload.spec.couplings.interaction_u,
            "chemical_potential": payload.spec.couplings.chemical_potential,
            "periodic": payload.spec.lattice.periodic,
        },
        "bridge": {
            "schema_version": payload.spec.schema_version,
            "integration_lane": payload.spec.integration_lane,
            "repository": payload.spec.provenance.repository,
            "repo_revision": payload.spec.provenance.repo_revision,
            "steward_approval_required": payload.spec.provenance.steward_approval_required,
            "steward_approved": payload.spec.provenance.steward_approved,
        },
    }

    backend_payload = {
        "hardware_emulated": False,
        "device": str(xdiag_result.get("device", "xdiag")),
        "wall_clock_seconds": float(xdiag_result.get("wall_clock_seconds", 0.0)),
        "peak_memory_mb": float(xdiag_result.get("peak_memory_mb", 0.0)),
    }

    spectra = [float(v) for v in eigenvalues_raw]

    return XDiagBridgeArtifact(
        manifest=manifest,
        spectra=spectra,
        observables=observables,
        backend_payload=backend_payload,
    )


def save_bridge_artifact(artifact: XDiagBridgeArtifact, output_dir: str) -> Path:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_id = str(artifact.manifest["run_id"])
    path = out_dir / f"{run_id}.xdiag_bridge.json"

    serializable = {
        "manifest": artifact.manifest,
        "spectra": artifact.spectra,
        "observables": artifact.observables,
        "backend_payload": artifact.backend_payload,
    }
    path.write_text(json.dumps(serializable, indent=2, sort_keys=True), encoding="utf-8")
    return path
