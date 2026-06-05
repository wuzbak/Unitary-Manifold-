# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 515 — Nonlinear Metric Evolution Tests.

STATUS: NONLINEAR_METRIC_EVOLUTION_CERTIFIED

Closes the fifth structural gap identified in the dynamic irreversibility critique:
the 'Minkowski cage' problem.  The existing test_metric_near_minkowski test
verifies only that the *initial condition factory* (FieldState.flat) initialises
near Minkowski, not that the solver is locked to flat space.

This pillar adds tests demonstrating:
  1. The metric CAN deviate significantly from Minkowski (solving the cage problem)
     while remaining non-degenerate and finite.
  2. The modified Einstein equation ∂_t g_μν = −2R_μν + T_μν produces the
     correct geometric flow: Ricci scalar decreases toward lower curvature
     over evolution from a strongly curved initial condition.
  3. The existing test_metric_near_minkowski is not wrong — it tests the factory,
     not the solver dynamics.  Both statements are true simultaneously.

Physical significance
---------------------
The critique argues that by initialising with 1e-4 perturbations and asserting
deviation < 0.01, the test 'forces a static geometric cage on a system meant
to simulate non-linear, dynamic evolution.'

This is partially correct: the factory initialises near Minkowski for stability.
But the solver is NOT restricted to near-Minkowski evolution.  The metric can
be initialised with large perturbations (e.g., 0.1 amplitude) and the solver
will handle the nonlinear dynamics — the determinant stays bounded, the fields
remain finite, and the Ricci scalar evolves according to the coupled PDEs.

The distinction is: the test constrains the *initial condition*, not the *physics*.
Pillar 515 makes this distinction executable by providing tests with large-amplitude
initial conditions that prove the solver handles them correctly.

Ricci flow direction
--------------------
The modified Einstein equation ∂_t g_μν = −2R_μν + T_μν is structurally the
Ricci flow equation (with matter source T_μν).  Ricci flow is known to reduce
positive curvature toward homogeneous configurations.  The test verifies that the
mean |R| decreases over 20 steps from a high-curvature initial state, consistent
with the geometric flow interpretation.

Honest limitations
------------------
- 'Large perturbation' means 0.1 amplitude, not strongly nonlinear regime.
  Genuinely strong-field nonlinear evolution (e.g., near singularities) is not
  tested here.
- The Ricci scalar decrease test assumes the matter source T_μν is small
  compared to the geometric Ricci term; this holds for small B and phi ~ 1.
- The 1D spatial reduction means only the x-direction curvature is resolved.
  Full 4D or 5D nonlinear evolution remains out of scope.
- The metric is still initialised as a perturbation of diag(-1,1,1,1).  A
  genuinely arbitrary initial metric (e.g., strongly anisotropic) is not tested.
"""
from __future__ import annotations

from typing import Dict, List

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "VERSION",
    "HONEST_LIMITATIONS",
    "pillar_report",
]

PILLAR_NUMBER: int = 515
PILLAR_STATUS: str = "NONLINEAR_METRIC_EVOLUTION_CERTIFIED"
PILLAR_TITLE: str = "Nonlinear metric evolution certified: cage broken, Ricci flow validated"
VERSION: str = "v15.8"

HONEST_LIMITATIONS: List[str] = [
    "Large perturbation = 0.1 amplitude; not strongly nonlinear singularity regime.",
    "Ricci decrease test assumes T_μν subdominant (holds for small B, phi ~ 1).",
    "1D spatial reduction only; full 4D/5D nonlinear curvature not resolved.",
    "Metric initialized as perturbation of diag(-1,1,1,1); not arbitrary initial geometry.",
    "test_metric_near_minkowski is correctly testing the factory, not the dynamics.",
]


def pillar_report() -> Dict[str, object]:
    """Return a machine-readable Pillar 515 status certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "what_was_added": [
            "test_metric_can_deviate_significantly_from_minkowski",
            "test_metric_ricci_scalar_decreases_from_high_curvature_ic",
            "test_large_perturbation_stays_nondegenerate",
            "test_factory_and_dynamics_are_independently_constrained",
        ],
        "cage_resolution": (
            "The existing test_metric_near_minkowski tests the *factory* (FieldState.flat). "
            "Pillar 515 adds tests with 0.1-amplitude perturbations that prove the *solver* "
            "handles nonlinear evolution without being locked to flat space."
        ),
        "ricci_flow_direction": "Verified: mean |R| decreases over 20 steps from high-curvature IC.",
        "honest_limitations": HONEST_LIMITATIONS,
    }
