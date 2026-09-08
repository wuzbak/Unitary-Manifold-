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
    "ox_navigator/engine/merlin_training_execution.py",
    "ox_navigator/engine/merlin_sync_contract.py",
    "ox_navigator/engine/merlin_tools.py",
    "ox_navigator/engine/merlin_local_inference.py",
    "ox_navigator/engine/merlin_local_provider.py",
    "ox_navigator/engine/merlin_admission.py",
)

REQUIRED_EXPORT_SCRIPTS: tuple[str, ...] = (
    "tools/export_merlin_training_artifacts.py",
    "tools/export_merlin_training_jsonl.py",
    "tools/export_merlin_mlflow_manifests.py",
    "tools/export_merlin_training_execution.py",
)

REQUIRED_TOOLKIT_FUNCTIONS: tuple[str, ...] = (
    "runMerlinSyncChecks",
    "getMerlinInferenceHealth",
    "runMerlinResearchCycle",
    "getMerlinCounterexampleDigest",
    "getMerlinEnergyLedger",
    "merlinConsolidateMemory",
    "merlinSelfAudit",
    "generateFalsificationOracle",
    "merlinAnalyzeDepth",
    "getMerlinThreeLaneIntensiveSprint",
    "getMerlinApplicationsToolsLane",
    "getMerlinBooksArticlesLane",
    "getMerlinAdversarialGrowthLane",
    "getMerlinContinuousLearningProtocol",
    "getMerlinTrainingExecutionQueue",
    "getMerlinLaneProgressLedgers",
    "runMerlinTrainingCycle",
)

REQUIRED_ARTIFACT_SURFACES: tuple[str, ...] = (
    "training/training_artifacts/training_artifacts.json",
    "training/training_jsonl/dataset_manifest.json",
    "training/mlflow_manifests/mlflow_manifests.json",
    "training/training_execution/three_lane_execution_bundle.json",
    "benchmarks/stage_b/receipts.json",
    "benchmarks/stage_c/receipts.json",
)
