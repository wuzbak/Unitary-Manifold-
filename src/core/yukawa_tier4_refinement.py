# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tier Acceleration Sprint (v10.25): Tier-4 coordinated Yukawa refinement package.

This package intentionally focuses on residual compression and cross-generation
consistency evidence, while preserving no-inflation governance:
  - calibration-assisted compression is permitted for diagnostics,
  - status promotion is blocked if purity gates are not passed.
"""
from __future__ import annotations

import math
from typing import Dict, List

from src.sixd.yukawa_hierarchy_6d import C_L_TOP, PI_KR, yukawa_hierarchy_table

__all__ = [
    "SUPPRESSION_SCAN_MIN",
    "SUPPRESSION_SCAN_MAX",
    "SUPPRESSION_SCAN_STEP",
    "BEST_SUPPRESSION_STRENGTH",
    "BASELINE_MAX_RESIDUAL_PCT",
    "REFINED_MAX_RESIDUAL_PCT",
    "BASELINE_MEDIAN_RESIDUAL_PCT",
    "REFINED_MEDIAN_RESIDUAL_PCT",
    "RESIDUAL_COMPRESSION_PCT",
    "tier4_refined_table",
    "tier4_yukawa_certificate",
]

SUPPRESSION_SCAN_MIN: float = 0.00
SUPPRESSION_SCAN_MAX: float = 1.20
SUPPRESSION_SCAN_STEP: float = 0.01


_DEF_BASE = yukawa_hierarchy_table()


def _refined_row(row: Dict, suppression_strength: float) -> Dict:
    c_shift = float(row["c_L"]) - C_L_TOP
    suppression = math.exp(-suppression_strength * PI_KR * c_shift * c_shift)
    y_refined = float(row["y_pred"]) * suppression
    residual_refined = abs(y_refined - float(row["y_pdg"])) / float(row["y_pdg"]) * 100.0
    out = dict(row)
    out.update(
        {
            "suppression_factor": suppression,
            "y_pred_refined": y_refined,
            "residual_refined_pct": residual_refined,
        }
    )
    return out


def _score_rows(rows: List[Dict]) -> float:
    # robust cross-generation objective: sum of squared log-ratio errors
    score = 0.0
    for r in rows:
        y_pred = max(float(r["y_pred_refined"]), 1e-30)
        y_obs = max(float(r["y_pdg"]), 1e-30)
        ratio = max(y_pred / y_obs, y_obs / y_pred)
        score += math.log10(ratio) ** 2
    return score


_best_score = None
_best_s = SUPPRESSION_SCAN_MIN
for i in range(int(round((SUPPRESSION_SCAN_MAX - SUPPRESSION_SCAN_MIN) / SUPPRESSION_SCAN_STEP)) + 1):
    s = SUPPRESSION_SCAN_MIN + i * SUPPRESSION_SCAN_STEP
    rows = [_refined_row(r, s) for r in _DEF_BASE]
    score = _score_rows(rows)
    if _best_score is None or score < _best_score:
        _best_score = score
        _best_s = s

BEST_SUPPRESSION_STRENGTH: float = round(_best_s, 2)


_DEF_REFINED = [_refined_row(r, BEST_SUPPRESSION_STRENGTH) for r in _DEF_BASE]

BASELINE_MAX_RESIDUAL_PCT: float = max(float(r["residual_pct"]) for r in _DEF_BASE)
REFINED_MAX_RESIDUAL_PCT: float = max(float(r["residual_refined_pct"]) for r in _DEF_REFINED)

_BASE_SORT = sorted(float(r["residual_pct"]) for r in _DEF_BASE)
_REF_SORT = sorted(float(r["residual_refined_pct"]) for r in _DEF_REFINED)
BASELINE_MEDIAN_RESIDUAL_PCT: float = 0.5 * (_BASE_SORT[1] + _BASE_SORT[2])
REFINED_MEDIAN_RESIDUAL_PCT: float = 0.5 * (_REF_SORT[1] + _REF_SORT[2])

if BASELINE_MEDIAN_RESIDUAL_PCT > 0:
    RESIDUAL_COMPRESSION_PCT: float = (
        (BASELINE_MEDIAN_RESIDUAL_PCT - REFINED_MEDIAN_RESIDUAL_PCT)
        / BASELINE_MEDIAN_RESIDUAL_PCT
        * 100.0
    )
else:
    RESIDUAL_COMPRESSION_PCT = 0.0


def tier4_refined_table() -> List[Dict]:
    """Return per-fermion baseline and refined residuals."""
    return [dict(row) for row in _DEF_REFINED]


def tier4_yukawa_certificate() -> Dict:
    """Return Tier-4 package evidence with no-inflation promotion guard."""
    rows = tier4_refined_table()
    monotone = [r["y_pred_refined"] for r in rows]
    gates = {
        "residual_compression_pass": RESIDUAL_COMPRESSION_PCT > 90.0,
        "cross_generation_consistency_pass": monotone[0] >= monotone[1] >= monotone[2] >= monotone[3],
        "axiomzero_purity_pass": False,  # calibration uses observational anchoring
    }
    promote = all(gates.values())

    return {
        "package": "Tier-4 Yukawa coordinated refinement",
        "suppression_strength": BEST_SUPPRESSION_STRENGTH,
        "rows": rows,
        "baseline_max_residual_pct": BASELINE_MAX_RESIDUAL_PCT,
        "refined_max_residual_pct": REFINED_MAX_RESIDUAL_PCT,
        "baseline_median_residual_pct": BASELINE_MEDIAN_RESIDUAL_PCT,
        "refined_median_residual_pct": REFINED_MEDIAN_RESIDUAL_PCT,
        "residual_compression_pct": RESIDUAL_COMPRESSION_PCT,
        "gates": gates,
        "promotion_allowed": promote,
        "status_policy": (
            "no_status_change_without_purity_gate; Tier-4 currently evidence-only"
            if not promote
            else "promotion_permitted"
        ),
        "toe_score_delta": 0.0,
    }
