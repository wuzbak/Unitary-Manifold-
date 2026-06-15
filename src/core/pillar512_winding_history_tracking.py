# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 512 — Winding History Tracking in run_evolution.

STATUS: WINDING_HISTORY_TRACKING_CERTIFIED

Closes the second structural gap: the evolution driver previously had no mechanism
to record how the topological winding number n_w changed (or remained constant)
over the course of a simulation run.

This pillar adds the ``track_winding=True`` parameter to ``run_evolution()``,
which causes the function to return a dict containing both the state history
and a parallel list of integer winding numbers recorded after each step.

Physical significance
---------------------
The winding history is the computational equivalent of "braided path history"
invoked in the critique.  Without recording n_w at every step, it is impossible
to distinguish:
  (a) a simulation where n_w is genuinely conserved (topological protection)
  (b) a simulation where n_w accidentally begins and ends at the same value
      while transiting through different winding sectors in between

Recording the full winding history makes the difference executable and testable.

The key tests enabled by this pillar:
  - Confirm that winding is stable over 100 steps for a clean braided IC
    (establishes the topology-without-backreaction baseline).
  - Confirm that winding fluctuates when KK backreaction is enabled
    (demonstrates that backreaction introduces genuine topological dynamics,
     answering the "hardcoded scaffold" critique).

Honest limitations
------------------
- Recording winding at every step adds O(N) compute per step via np.gradient.
- The winding number is computed from the instantaneous field, not from path
  integrals over the full trajectory.  This is an approximation.
- KK backreaction-induced winding fluctuations may reflect numerical artifacts
  for very small coupling rather than physical topological transitions.
"""
from __future__ import annotations

from typing import Dict, List

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "VERSION",
    "RETURN_FORMAT",
    "HONEST_LIMITATIONS",
    "pillar_report",
]

PILLAR_NUMBER: int = 512
PILLAR_STATUS: str = "WINDING_HISTORY_TRACKING_CERTIFIED"
PILLAR_TITLE: str = "Winding history tracking added to run_evolution"
VERSION: str = "v15.8"

RETURN_FORMAT: Dict[str, str] = {
    "when_track_winding_false": "List[FieldState] — backward compatible, default",
    "when_track_winding_true": (
        "Dict with keys: 'history' (List[FieldState]), "
        "'winding_history' (List[int]). "
        "Both lists have length steps + 1 (including initial state)."
    ),
}

HONEST_LIMITATIONS: List[str] = [
    "Winding recorded from instantaneous field, not from 5D path integral.",
    "O(N) extra compute per step; negligible for N <= 128 but scales.",
    "KK-coupling fluctuations may be numerical at very small coupling values.",
    "Backward compatibility: track_winding=False (default) returns plain list.",
]


def pillar_report() -> Dict[str, object]:
    """Return a machine-readable Pillar 512 status certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "what_was_added": [
            "run_evolution(..., track_winding=False) parameter in evolution.py",
            "Returns dict with 'history' and 'winding_history' when track_winding=True",
            "Backward-compatible: default False returns List[FieldState] as before",
        ],
        "gap_closed": (
            "Previously impossible to distinguish topology-stable from topology-"
            "fluctuating simulations post-hoc.  Now the full winding trajectory "
            "is recorded and testable."
        ),
        "return_format": RETURN_FORMAT,
        "honest_limitations": HONEST_LIMITATIONS,
    }
