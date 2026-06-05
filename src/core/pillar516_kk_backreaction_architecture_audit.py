# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 516 — KK backreaction coupling architecture audit.

STATUS: KK_BACKREACTION_ARCHITECTURE_AUDIT_COMPLETE

This module does not claim that full non-perturbative KK backreaction is solved.
It certifies the current architectural boundary in ``src/core/evolution.py``:

- winding evolution is live and auditable via ``track_winding=True``
- a KK backreaction source term exists structurally
- the default production regime remains decoupled because
  ``n_kk_modes = 0`` and ``kk_backreaction_coupling = 0.0``
- simultaneous winding evolution with a dynamically populated KK tower remains
  open work
"""
from __future__ import annotations

from typing import Dict

__all__ = [
    "PILLAR_ID",
    "PILLAR_STATUS",
    "kk_backreaction_architecture_report",
    "regime_map",
]

PILLAR_ID: int = 516
PILLAR_STATUS: str = "KK_BACKREACTION_ARCHITECTURE_AUDIT_COMPLETE"


_DEF_MATHEMATICAL_GAP = (
    "To close the coupled KK-winding problem one must define a controlled KK tower "
    "truncation N_kk with an explicit tail bound, evolve the radion/metric step with "
    "a backreaction term derived from a mode-energy sum Σ_n |psi_n|^2, re-measure the "
    "braid winding sector after each coupled update, and prove that the alternating "
    "geometry-plus-KK iteration converges to a stable fixed point rather than exciting "
    "runaway KK occupation or sector-flipping numerical artifacts."
)


_DEF_OPEN_WORK = (
    "Full dynamic coupling requires: (1) KK mode sum truncation at N_kk modes with "
    "convergence certificate, (2) backreaction correction to walker_pearson_step "
    "proportional to sum_n |psi_n|^2 * kk_coupling, (3) winding-number re-measurement "
    "after each backreaction step, (4) convergence criterion for coupled iteration"
)


def kk_backreaction_architecture_report() -> Dict[str, object]:
    """Return a machine-readable Pillar 516 architecture certificate."""
    return {
        "pillar_id": PILLAR_ID,
        "status": PILLAR_STATUS,
        "current_implementation": (
            "Winding evolution tracks sector changes via gradient-space algorithm; KK tower "
            "is decoupled in current run_evolution() call (n_kk_modes=0, "
            "kk_backreaction_coupling=0.0)"
        ),
        "open_work": _DEF_OPEN_WORK,
        "architecture_limit_certified": True,
        "closes_pillar": None,
        "blocking_for": "Full non-perturbative winding-geometry coupling proof",
        "mathematical_gap": _DEF_MATHEMATICAL_GAP,
        "estimated_closure": (
            "Requires external lattice QFT computation or non-perturbative 5D-KK "
            "quantum-gravity code"
        ),
        "falsifier_impact": (
            "KK backreaction decoupling is conservative — it underestimates winding-geometry "
            "coupling. The current irreversibility proof is a lower bound. Enabling "
            "backreaction would strengthen, not weaken, the irreversibility claim IF the KK "
            "tower is stable."
        ),
    }


def regime_map() -> Dict[str, str]:
    """Return the operational regime map for the current evolution architecture."""
    return {
        "factory_ic": (
            "FieldState.flat() is intentionally near-flat: metric/B/phi perturbations are "
            "seeded at ~1e-4 for stable factory initial conditions, not because the solver is "
            "caged. Test refs: tests/test_pillar515_nonlinear_metric_evolution.py::"
            "TestFactoryVsSolverDistinction::test_factory_near_minkowski_is_by_design and "
            "tests/test_evolution_regime_map.py::test_factory_ic_near_flat_is_by_design"
        ),
        "solver_large_deviation": (
            "run_evolution() can evolve substantially larger departures than the factory seed; "
            "the audited live regime includes braided scalar amplitudes up to 0.5 with winding "
            "tracking intact when dt respects stability limits. Test refs: "
            "tests/test_pillar515_nonlinear_metric_evolution.py::"
            "test_solver_can_handle_large_initial_deviation and "
            "tests/test_evolution_regime_map.py::test_solver_can_handle_large_deviation_amplitude"
        ),
        "backreaction_decoupled": (
            "The architecture contains a KK backreaction hook, but the default certified run "
            "path is decoupled because FieldState defaults to n_kk_modes=0 and "
            "kk_backreaction_coupling=0.0, so the KK source vanishes. Test refs: "
            "tests/test_pillar516_kk_backreaction_architecture_audit.py::"
            "test_architecture_limit_certified_true and "
            "tests/test_evolution_regime_map.py::test_regime_map_documents_backreaction_decoupled"
        ),
        "winding_tracking_live": (
            "Topological sector tracking is active now: run_evolution(track_winding=True) returns "
            "winding_history with one entry per saved state, allowing live audit of winding-sector "
            "preservation or transition. Test refs: tests/test_pillar512_winding_history_tracking.py "
            "and tests/test_evolution_regime_map.py::test_winding_tracking_history_length"
        ),
    }
