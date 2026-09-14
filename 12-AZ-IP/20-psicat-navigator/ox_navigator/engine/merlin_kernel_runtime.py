# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Kernel runtime surfaces for governed compiled-kernel migration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.core.kernel_runtime import (
    build_kernel_parity_receipt,
    detect_backend_capability,
    kernel_contract_schema,
    run_epistemic_compactification_sanity,
)

REPO_ROOT = Path(__file__).resolve().parents[4]


def get_kernel_runtime_board() -> dict[str, Any]:
    capability = detect_backend_capability()
    contract = kernel_contract_schema()
    return {
        "board_id": "psicat_kernel_runtime_board_v1",
        "ok": True,
        "capability": capability,
        "kernel_contracts": contract,
        "policy": {
            "preferred_lane_order": ["triton_compiled", "jax_xla", "numpy_cpu"],
            "hard_bypass_forbidden": True,
            "governed_local_execution_required": True,
            "backend_detection_note": "Backend identity is explicit; CUDA-visible ROCm environments are treated separately.",
        },
    }


def get_kernel_execution_receipts(points: int = 8, seed: int = 7) -> dict[str, Any]:
    receipt = build_kernel_parity_receipt(points=points, seed=seed)
    return {
        "ok": bool(receipt.get("ok")),
        "receipt": receipt,
        "governance": {
            "fail_closed": bool((receipt.get("gate") or {}).get("fail_closed", True)),
            "unchecked_or_unlogged_execution_forbidden": True,
        },
    }


def get_compactification_sanity_receipt() -> dict[str, Any]:
    return run_epistemic_compactification_sanity(
        mas_tracker_path=REPO_ROOT / "docs" / "mas_tracker.yml",
        fallibility_path=REPO_ROOT / "FALLIBILITY.md",
    )
