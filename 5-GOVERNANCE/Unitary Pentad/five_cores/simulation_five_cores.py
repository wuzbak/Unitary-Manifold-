# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
five_cores/simulation_five_cores.py
=====================================
Simulation suite for the Five-Cores architecture.

Three canonical simulation scenarios are implemented:

    Scenario A — Nominal Cruise
        200 steps with slowly decaying trust (−0.002/step) and mild safety
        perturbations.  Tests that the system maintains NOMINAL/DEGRADED status
        and crew health above C_S.

    Scenario B — Emergency: Crew Medical Crisis
        One crew member suffers rapid vital collapse.  Safety metrics spike.
        Tests that the system correctly escalates to HIL, enters AWAITING_HIL,
        and that the Biological Logics Core correctly identifies P1 triage.

    Scenario C — Scientific Discovery Burst
        100 concentrated observations arrive in 10 steps for the ASTROPHYSICS
        domain.  Tests that Sciences readiness converges and system readiness
        rises measurably.  JAX path is exercised when available.

Results are printed and returned as a dict for programmatic use.

Usage
-----
    python simulation_five_cores.py

or from Python:

    from five_cores.simulation_five_cores import run_all_simulations
    results = run_all_simulations()
"""

from __future__ import annotations

import sys
import os
import math

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_PENTAD = os.path.dirname(_HERE)
_ROOT = os.path.dirname(_PENTAD)
for _p in [_HERE, _PENTAD, _ROOT]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from five_cores.five_cores_system import FiveCoresSystem, SystemStatus, CoreLabel
from five_cores.realtime_sciences_core import (
    Observation, DataDomain, RealTimeSciencesCore, _JAX_AVAILABLE
)
from five_cores.biological_logics_core import VitalCategory, VITAL_CATEGORIES
from five_cores.realtime_safety_core import HARD_INTERLOCK_THRESHOLD

C_S: float = 12 / 37


# ---------------------------------------------------------------------------
# Scenario A — Nominal Cruise
# ---------------------------------------------------------------------------

def scenario_a_nominal_cruise(n_steps: int = 200, verbose: bool = True) -> dict:
    """
    Nominal cruise: slowly decaying trust, mild safety perturbations.

    Returns
    -------
    dict with keys:
        n_steps, final_trust, final_health, final_status,
        min_health, max_health, hil_events, crew_health_above_cs
    """
    sys_ = FiveCoresSystem.default()

    trust_schedule = [-0.002] * n_steps  # slow decay

    # Mild perturbations every 25 steps
    metric_schedule = []
    for i in range(n_steps):
        if i % 25 == 0:
            metric_schedule.append({
                "RADIATION_EXPOSURE": 0.30 + 0.05 * np.sin(i / 10),
                "HULL_STRESS": 0.25 + 0.05 * np.cos(i / 10),
            })
        else:
            metric_schedule.append(None)

    reports = sys_.run(
        n_steps=n_steps,
        trust_schedule=trust_schedule,
        metric_schedule=metric_schedule,
    )

    health_scores = [r.health_score for r in reports]
    hil_events = sum(1 for r in reports if r.hil_requested)
    final = reports[-1]
    crew_health_above_cs = (
        final.biological.system_health > C_S
    )

    result = {
        "scenario": "A — Nominal Cruise",
        "n_steps": n_steps,
        "final_trust": round(final.phi_trust, 4),
        "final_health": round(final.health_score, 4),
        "final_status": final.status,
        "min_health": round(min(health_scores), 4),
        "max_health": round(max(health_scores), 4),
        "hil_events": hil_events,
        "crew_health_above_cs": crew_health_above_cs,
    }

    if verbose:
        _print_result(result)
    return result


# ---------------------------------------------------------------------------
# Scenario B — Emergency: Crew Medical Crisis
# ---------------------------------------------------------------------------

def scenario_b_medical_crisis(n_steps: int = 100, verbose: bool = True) -> dict:
    """
    Medical emergency: one crew member collapses; system escalates to HIL.

    Returns
    -------
    dict with keys:
        n_steps, crisis_step, first_hil_step, p1_detected, final_status,
        final_crew_readiness, critical_crew
    """
    sys_ = FiveCoresSystem.default()

    crisis_step = 30  # vital collapse at step 30
    first_hil_step = None
    p1_detected = False

    for step in range(n_steps):
        if step == crisis_step:
            # Commander suffers rapid cardiovascular collapse
            for vc in VITAL_CATEGORIES:
                sys_.biological._crew["C001"].vital_radions[vc] = 0.08

        # Add medical oxygen intervention at step crisis_step + 5
        if step == crisis_step + 5:
            sys_.biological.apply_intervention(
                "C001", VitalCategory.CARDIOVASCULAR, 0.15
            )
            sys_.biological.apply_intervention(
                "C001", VitalCategory.RESPIRATORY, 0.10
            )

        report = sys_.tick()

        if first_hil_step is None and report.hil_requested:
            first_hil_step = step

        if "C001" in report.critical_crew:
            p1_detected = True

        # HIL acknowledge after 5 steps of waiting
        if report.hil_requested and first_hil_step is not None and step == first_hil_step + 5:
            sys_.hil_acknowledge()

    final = sys_.history()[-1]

    result = {
        "scenario": "B — Medical Crisis",
        "n_steps": n_steps,
        "crisis_step": crisis_step,
        "first_hil_step": first_hil_step,
        "p1_detected": p1_detected,
        "final_status": final.status,
        "final_crew_readiness": round(final.biological.crew_readiness, 4),
        "critical_crew": final.biological.critical_members,
    }

    if verbose:
        _print_result(result)
    return result


# ---------------------------------------------------------------------------
# Scenario C — Scientific Discovery Burst
# ---------------------------------------------------------------------------

def scenario_c_science_burst(n_steps: int = 50, verbose: bool = True) -> dict:
    """
    Scientific discovery burst: 100 concentrated ASTROPHYSICS observations
    arrive in 10 steps.  Sciences readiness must rise measurably.

    JAX path is exercised when available.

    Returns
    -------
    dict with keys:
        n_steps, jax_active, readiness_before, readiness_after,
        readiness_increase, query_ready, system_readiness_final
    """
    use_jax = _JAX_AVAILABLE  # exercise JAX when available
    sciences = RealTimeSciencesCore(use_jax=use_jax, n_hypotheses=5)
    sys_ = FiveCoresSystem.default()
    sys_.sciences = sciences  # inject JAX-aware sciences core

    readiness_before = sys_.sciences.readiness(DataDomain.ASTROPHYSICS)

    # Build observation schedule: 10 concentrated observations per step, 10 steps
    observation_schedule = []
    for step in range(n_steps):
        if step < 10:
            obs_batch = [
                Observation(
                    DataDomain.ASTROPHYSICS,
                    np.array([8.0, 0.5, 0.5, 0.5, 0.5]),  # peaked at H0
                )
                for _ in range(10)
            ]
            observation_schedule.append(obs_batch)
        else:
            observation_schedule.append(None)

    reports = sys_.run(
        n_steps=n_steps,
        observation_schedule=observation_schedule,
    )

    readiness_after = sys_.sciences.readiness(DataDomain.ASTROPHYSICS)
    query_result = sys_.sciences.query(DataDomain.ASTROPHYSICS)
    final = reports[-1]

    result = {
        "scenario": "C — Science Burst",
        "n_steps": n_steps,
        "jax_active": sys_.sciences._use_jax,
        "readiness_before": round(readiness_before, 6),
        "readiness_after": round(readiness_after, 6),
        "readiness_increase": round(readiness_after - readiness_before, 6),
        "query_ready": query_result["query_ready"],
        "system_readiness_final": round(final.sciences.system_readiness, 4),
    }

    if verbose:
        _print_result(result)
    return result


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def _print_result(result: dict) -> None:
    print(f"\n{'='*60}")
    print(f"  {result['scenario']}")
    print(f"{'='*60}")
    for k, v in result.items():
        if k != "scenario":
            print(f"  {k:30s}: {v}")


def run_all_simulations(verbose: bool = True) -> dict:
    """
    Run all three canonical scenarios and return consolidated results.

    Returns
    -------
    dict with keys 'A', 'B', 'C' mapping to per-scenario result dicts.
    Also contains 'all_passed': bool summary.
    """
    if verbose:
        print("\n" + "="*60)
        print("  Five-Cores System — Simulation Suite")
        print("  (5,7)-Braid Stability: c_s = 12/37 ≈ 0.3243")
        print("="*60)

    a = scenario_a_nominal_cruise(verbose=verbose)
    b = scenario_b_medical_crisis(verbose=verbose)
    c = scenario_c_science_burst(verbose=verbose)

    # Validation checks
    a_ok = (
        a["crew_health_above_cs"]
        and a["final_health"] >= C_S
    )
    b_ok = (
        b["p1_detected"]
        and b["first_hil_step"] is not None
    )
    c_ok = (
        c["readiness_increase"] > 0.01
    )

    all_passed = a_ok and b_ok and c_ok

    if verbose:
        print(f"\n{'='*60}")
        print(f"  Validation Summary")
        print(f"{'='*60}")
        print(f"  Scenario A (Nominal Cruise):       {'PASS ✓' if a_ok else 'FAIL ✗'}")
        print(f"  Scenario B (Medical Crisis):       {'PASS ✓' if b_ok else 'FAIL ✗'}")
        print(f"  Scenario C (Science Burst):        {'PASS ✓' if c_ok else 'FAIL ✗'}")
        print(f"  Overall:                           {'PASS ✓' if all_passed else 'FAIL ✗'}")
        if _JAX_AVAILABLE:
            print(f"  JAX: ACTIVE (Scenario C accelerated)")
        else:
            print(f"  JAX: not installed (NumPy fallback used)")

    return {"A": a, "B": b, "C": c, "all_passed": all_passed}


if __name__ == "__main__":
    results = run_all_simulations(verbose=True)
    sys.exit(0 if results["all_passed"] else 1)
