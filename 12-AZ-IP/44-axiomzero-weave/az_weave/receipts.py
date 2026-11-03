# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Use the monorepo's execution-spine contract without promoting its claims."""

from pathlib import Path
import sys


def execution_record(root: Path, *, status: str, sources: list[str], semantic_sha256: str) -> dict:
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from src.infrastructure.execution_spine import ExecutionSpineRecord, build_fail_closed_governance

    return ExecutionSpineRecord(
        surface_id="az-ip-44-weave", surface_kind="integration",
        lane="adjacent-software", status=status,
        summary="Source-grounded weave receipt; not physics closure or model superiority.",
        canonical_paths=["12-AZ-IP/44-axiomzero-weave/"],
        sources=sources,
        governance=build_fail_closed_governance(
            epistemic_label="ADJACENT TRACK",
            promotion_rule="No automatic scientific or memory promotion.",
            residual_blockers=["Independent evidence review; production identity and deployment remain external."]),
        compatibility={"semantic_sha256": semantic_sha256},
        promotion={"physics": False, "authority": False, "model_superiority": False},
    ).to_dict()
