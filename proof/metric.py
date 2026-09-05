# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Formal-entry-point exports of the canonical KK geometry implementation.

This is deliberately not a second numerical implementation: previously the
two copies silently drifted. Independent verification lives in symbolic
line-element, inverse, gauge, curvature and convergence tests. The proof
entry point requires the repository's src/ tree, not just this directory.
"""

from pathlib import Path
import sys

_ROOT = str(Path(__file__).resolve().parents[1])
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from src.core.metric import (
    _grad,
    _riemann_from_christoffel,
    assemble_5d_metric,
    assemble_warped_5d_metric,
    christoffel,
    compute_5d_curvature,
    compute_curvature,
    extract_alpha_from_curvature,
    field_strength,
    inverse_5d_metric,
    derive_nw_index_theorem,
    z2_parity_clarification,
)
