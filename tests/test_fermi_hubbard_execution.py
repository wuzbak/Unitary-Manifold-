# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
from __future__ import annotations

from pathlib import Path

import numpy as np

from src.quantum.execution import ExecutionConfig, run_time_evolution, save_run_artifact
from src.quantum.fermi_hubbard import build_fermi_hubbard_1d


def test_time_evolution_returns_normalized_state_and_history() -> None:
    model = build_fermi_hubbard_1d(n_sites=2, hopping_t=1.0, interaction_u=2.0)
    cfg = ExecutionConfig(total_time=0.2, trotter_steps=4, mapping="jw", backend="simulator")
    result = run_time_evolution(model, cfg)

    assert np.isclose(np.linalg.norm(result.final_state), 1.0)
    assert len(result.observable_history) == 5
    assert result.manifest.mapping == "jw"


def test_hardware_adapter_lane_returns_payload() -> None:
    model = build_fermi_hubbard_1d(n_sites=2, hopping_t=1.0, interaction_u=2.0)
    cfg = ExecutionConfig(total_time=0.1, trotter_steps=2, mapping="jw", backend="hardware")
    result = run_time_evolution(model, cfg)
    assert bool(result.backend_payload["hardware_emulated"]) is True


def test_run_artifact_written(tmp_path: Path) -> None:
    model = build_fermi_hubbard_1d(n_sites=2, hopping_t=1.0, interaction_u=2.0)
    cfg = ExecutionConfig(total_time=0.1, trotter_steps=2)
    result = run_time_evolution(model, cfg)
    path = save_run_artifact(result, str(tmp_path))
    assert path.exists()
    assert path.suffix == ".json"
