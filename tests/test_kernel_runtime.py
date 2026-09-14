# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0

from __future__ import annotations

from pathlib import Path

from src.core.kernel_runtime import (
    build_kernel_benchmark_receipt,
    build_kernel_parity_receipt,
    detect_backend_capability,
    kernel_contract_schema,
    run_epistemic_compactification_sanity,
)


def test_kernel_contract_schema_exposes_governed_contracts():
    payload = kernel_contract_schema()
    assert payload["schema_version"] == "kernel_contracts_v1"
    assert len(payload["contracts"]) >= 2
    ids = {item["contract_id"] for item in payload["contracts"]}
    assert "metric.curvature.v1" in ids
    assert payload["governance"]["unchecked_bypass_forbidden"] is True


def test_detect_backend_capability_has_explicit_identity_fields():
    capability = detect_backend_capability()
    assert "selected_backend" in capability
    assert "torch" in capability
    assert "jax" in capability
    assert "wavefront_hint" in capability


def test_kernel_parity_receipt_is_fail_closed_when_compiled_lane_missing():
    receipt = build_kernel_parity_receipt(points=6, seed=3)
    assert receipt["ok"] is True
    assert "numpy_reference" in receipt["lanes"]
    assert "triton_compiled" in receipt["lanes"]
    assert "triton_metric_block_compiled" in receipt["lanes"]
    assert "max_abs_error_vs_numpy_outer_bb" in receipt["lanes"]["triton_compiled"]
    assert "max_abs_error_vs_numpy_kk_4x4_block" in receipt["lanes"]["triton_metric_block_compiled"]
    assert "gate" in receipt


def test_epistemic_compactification_sanity_scans_mas_tracker_and_fallibility():
    repo_root = Path(__file__).resolve().parents[1]
    payload = run_epistemic_compactification_sanity(
        mas_tracker_path=repo_root / "docs" / "mas_tracker.yml",
        fallibility_path=repo_root / "FALLIBILITY.md",
    )
    assert payload["check_count"] >= 6
    assert any(item["id"] == "mas_tracker_remaining_open" for item in payload["checks"])


def test_kernel_benchmark_receipt_has_hotspot_metrics():
    payload = build_kernel_benchmark_receipt(points=32, seed=5, repeats=2)
    assert payload["ok"] is True
    outer_metrics = payload["benchmarks"]["outer_bb_hotspot"]
    metric_block_metrics = payload["benchmarks"]["kk_4x4_metric_block_hotspot"]
    assert outer_metrics["repeats"] == 2
    assert metric_block_metrics["repeats"] == 2
    assert "max_abs_error_vs_reference" in outer_metrics
    assert "max_abs_error_vs_reference" in metric_block_metrics
