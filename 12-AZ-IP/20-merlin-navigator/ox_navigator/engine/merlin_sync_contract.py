# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Canonical sync-check contract for Merlin parity verification."""

from __future__ import annotations

REQUIRED_ENGINE_MODULES: tuple[str, ...] = (
    "ox_navigator/engine/merlin_kernel_routing.py",
    "ox_navigator/engine/merlin_inference_health.py",
    "ox_navigator/engine/merlin_research_cycle.py",
    "ox_navigator/engine/merlin_energy_ledger.py",
    "ox_navigator/engine/merlin_meta_learning.py",
    "ox_navigator/engine/merlin_local_inference.py",
    "ox_navigator/engine/merlin_local_provider.py",
    "ox_navigator/engine/merlin_admission.py",
)

REQUIRED_EXPORT_SCRIPTS: tuple[str, ...] = (
    "tools/export_merlin_training_artifacts.py",
    "tools/export_merlin_training_jsonl.py",
    "tools/export_merlin_mlflow_manifests.py",
)
