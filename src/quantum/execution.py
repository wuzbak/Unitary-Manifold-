# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/quantum/execution.py
========================
Simulator-first execution backend with hardware-adapter abstractions,
trotterized evolution workflow, and reproducibility manifests.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, UTC
import json
import time
from pathlib import Path
from typing import Protocol

import numpy as np
from scipy.linalg import expm

from src.infrastructure.execution_spine import (
    ExecutionSpineHealthCheck,
    ExecutionSpineRecord,
    build_fail_closed_governance,
    repo_rel,
)

from .fermi_hubbard import FermiHubbardHamiltonian
from .fermion_mapping import MappingName, fermion_terms_to_qubit_terms, pauli_terms_to_matrix
from .observables import ObservableSnapshot, snapshot_observables

REPO_ROOT = Path(__file__).resolve().parents[2]

# Placeholder coefficients for deterministic mock-hardware timing emulation.
MOCK_QUEUE_BASE_SEC = 0.25
MOCK_QUEUE_PER_MODE_SEC = 0.01
MOCK_COMPILE_BASE_SEC = 0.15
MOCK_COMPILE_PER_SITE_SEC = 0.02


@dataclass(frozen=True)
class ExecutionConfig:
    total_time: float
    trotter_steps: int
    mapping: MappingName = "jw"
    backend: str = "simulator"
    shots: int = 4096


@dataclass(frozen=True)
class RunManifest:
    run_id: str
    created_at_utc: str
    n_sites: int
    n_modes: int
    mapping: str
    backend: str
    total_time: float
    trotter_steps: int
    parameters: dict[str, float | bool | int]


@dataclass
class ExecutionResult:
    manifest: RunManifest
    wall_clock_seconds: float
    final_state: np.ndarray
    times: np.ndarray
    observable_history: list[ObservableSnapshot]
    backend_payload: dict[str, float | int | str | bool]


class HardwareAdapter(Protocol):
    def submit(self, manifest: RunManifest) -> dict[str, float | int | str | bool]:
        ...


class MockHardwareAdapter:
    """Deterministic hardware-adapter placeholder for queued execution metadata."""

    def submit(self, manifest: RunManifest) -> dict[str, float | int | str | bool]:
        queue_seconds = MOCK_QUEUE_BASE_SEC + MOCK_QUEUE_PER_MODE_SEC * manifest.n_modes
        compile_seconds = MOCK_COMPILE_BASE_SEC + MOCK_COMPILE_PER_SITE_SEC * manifest.n_sites
        return {
            "hardware_emulated": True,
            "queue_seconds": round(queue_seconds, 4),
            "compile_seconds": round(compile_seconds, 4),
            "shots": 4096,
            "device": "mock_hardware_adapter",
        }


def _half_filling_neel_state(model: FermiHubbardHamiltonian) -> np.ndarray:
    """Alternating |↑,↓,↑,↓,...> product state at half filling in site basis."""
    bits = 0
    for i in range(model.n_sites):
        spin = 0 if i % 2 == 0 else 1
        bits |= 1 << model.mode_index(i, spin)
    dim = 2 ** model.n_modes
    psi = np.zeros(dim, dtype=complex)
    psi[bits] = 1.0
    return psi


def _build_manifest(model: FermiHubbardHamiltonian, config: ExecutionConfig) -> RunManifest:
    run_id = (
        f"fh_{model.n_sites}s_{config.mapping}_{config.backend}_"
        f"{int(config.total_time * 1000)}ms_{config.trotter_steps}tr"
    )
    return RunManifest(
        run_id=run_id,
        created_at_utc=datetime.now(UTC).isoformat(),
        n_sites=model.n_sites,
        n_modes=model.n_modes,
        mapping=config.mapping,
        backend=config.backend,
        total_time=config.total_time,
        trotter_steps=config.trotter_steps,
        parameters={
            "hopping_t": model.hopping_t,
            "interaction_u": model.interaction_u,
            "chemical_potential": model.chemical_potential,
            "periodic": model.periodic,
        },
    )


def run_time_evolution(
    model: FermiHubbardHamiltonian,
    config: ExecutionConfig,
    adapter: HardwareAdapter | None = None,
    initial_state: np.ndarray | None = None,
) -> ExecutionResult:
    if config.trotter_steps <= 0:
        raise ValueError("trotter_steps must be positive")
    if config.total_time <= 0:
        raise ValueError("total_time must be positive")

    t0 = time.perf_counter()

    terms = model.fermionic_terms()
    qterms = fermion_terms_to_qubit_terms(terms, model.n_modes, mapping=config.mapping)
    h = pauli_terms_to_matrix(qterms, n_qubits=model.n_modes)

    dt = config.total_time / config.trotter_steps
    step_unitary = expm(-1j * dt * h)

    state = _half_filling_neel_state(model) if initial_state is None else initial_state.astype(complex)
    state = state / np.linalg.norm(state)

    times = np.linspace(0.0, config.total_time, config.trotter_steps + 1)
    history: list[ObservableSnapshot] = [snapshot_observables(state, model, mapping=config.mapping)]

    for _ in range(config.trotter_steps):
        state = step_unitary @ state
        state = state / np.linalg.norm(state)
        history.append(snapshot_observables(state, model, mapping=config.mapping))

    manifest = _build_manifest(model, config)

    if config.backend == "simulator":
        payload: dict[str, float | int | str | bool] = {"hardware_emulated": False, "device": "numpy_expm"}
    else:
        active_adapter = adapter if adapter is not None else MockHardwareAdapter()
        payload = active_adapter.submit(manifest)

    wall = time.perf_counter() - t0
    return ExecutionResult(
        manifest=manifest,
        wall_clock_seconds=wall,
        final_state=state,
        times=times,
        observable_history=history,
        backend_payload=payload,
    )


def save_run_artifact(result: ExecutionResult, output_dir: str) -> Path:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{result.manifest.run_id}.json"
    execution_spine = ExecutionSpineRecord(
        surface_id=result.manifest.run_id,
        surface_kind="quantum_run_artifact",
        lane="lane_e_quantum_adjacent",
        status="ADJACENT_EXECUTION_ARTIFACT",
        summary="Adjacent quantum execution artifact with fail-closed provenance and optional backend disclosure.",
        canonical_paths=[repo_rel(Path(__file__), REPO_ROOT)],
        sources=[
            repo_rel(Path(__file__), REPO_ROOT),
        ],
        governance=build_fail_closed_governance(
            epistemic_label="ADJACENT_TRACK",
            promotion_rule="Artifacts support adjacent execution benchmarking only and do not create hardgate closure.",
            optional_backend=result.manifest.backend != "simulator",
            residual_blockers=[
                "Optional external/hardware backends remain execution-dependent.",
            ],
        ),
        compatibility={
            "backend": result.manifest.backend,
            "simulator_first": True,
        },
        health_checks=[
            ExecutionSpineHealthCheck(
                check_id="observable_history_present",
                passed=bool(result.observable_history),
                status="pass" if result.observable_history else "fail",
                summary="Observable history must be present in every saved artifact.",
                details={"history_length": len(result.observable_history)},
                sources=[repo_rel(Path(__file__), REPO_ROOT)],
            ),
        ],
        promotion={
            "eligible": False,
            "gate": "adjacent_only",
            "reason": "Quantum execution artifacts remain governed adjacent-lane evidence surfaces.",
        },
    ).to_dict()

    serialisable = {
        "manifest": asdict(result.manifest),
        "wall_clock_seconds": result.wall_clock_seconds,
        "backend_payload": result.backend_payload,
        "execution_spine": execution_spine,
        "times": result.times.tolist(),
        "observables": [
            {
                "charge_density": s.charge_density.tolist(),
                "spin_density": s.spin_density.tolist(),
                "double_occupancy": s.double_occupancy.tolist(),
                "staggered_magnetization": s.staggered_magnetization,
            }
            for s in result.observable_history
        ],
    }

    out_path.write_text(json.dumps(serialisable, indent=2), encoding="utf-8")
    return out_path
