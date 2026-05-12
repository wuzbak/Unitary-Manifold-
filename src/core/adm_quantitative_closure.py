# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""ADM quantitative closure package for the delay-field time-parameterization gap.

This module operationalizes a quantitative closure audit on top of Pillar 100 and
Pillar 212 by combining:
- metric/lapse consistency checks,
- Hamiltonian/momentum vacuum checks,
- lapse invariance under positive radion rescaling,
- a machine-readable falsifier interface for non-attractor mismatch.
"""
from __future__ import annotations

from typing import Dict, Iterable, List

from src.core.pillar212_adm_decomposition import (
    adm_5d_metric,
    adm_consistency_check,
    hamiltonian_constraint,
    momentum_constraint,
    ricci_to_adm_time_coincidence,
)
from src.core.phi_radion_quantization import canonical_quantization_report

__all__ = [
    "DEFAULT_PHI_GRID",
    "lapse_scaling_invariance",
    "adm_constraint_audit",
    "adm_falsifier_interface",
    "off_attractor_time_mismatch_scan",
    "off_attractor_severity_profile",
    "radion_quantization_closure",
    "adm_quantitative_closure_report",
]

DEFAULT_PHI_GRID: List[float] = [0.25, 0.5, 1.0, 2.0, 4.0]
ATTRACTOR_PHI: float = 1.0
ATTRACTOR_PHI_TOLERANCE: float = 1e-12
MIN_DT_MISMATCH_FOR_RATIO: float = 1e-15


def _is_attractor_phi(phi_value: float) -> bool:
    return abs(phi_value - ATTRACTOR_PHI) < ATTRACTOR_PHI_TOLERANCE


def lapse_scaling_invariance(phi_values: Iterable[float] = DEFAULT_PHI_GRID) -> Dict[str, object]:
    """Verify N(phi)=phi^{-1/2} monotonicity and positivity over a scan grid."""
    phis = [float(v) for v in phi_values]
    lapses = [adm_5d_metric(phi=p)["lapse_N"] for p in phis]

    positive = all(x > 0.0 for x in lapses)
    monotone_decreasing = all(lapses[i] > lapses[i + 1] for i in range(len(lapses) - 1))

    return {
        "phi_values": phis,
        "lapse_values": lapses,
        "positive_lapse": positive,
        "strictly_monotone_decreasing": monotone_decreasing,
        "all_pass": positive and monotone_decreasing,
    }


def adm_constraint_audit(phi_values: Iterable[float] = DEFAULT_PHI_GRID) -> Dict[str, object]:
    """Audit Hamiltonian/momentum constraints over a radion grid in vacuum."""
    phis = [float(v) for v in phi_values]

    ham = [hamiltonian_constraint(phi=p, H_hubble=0.0) for p in phis]
    mom = [momentum_constraint(phi=p) for p in phis]

    ham_ok = all(item["constraint_satisfied"] for item in ham)
    mom_ok = all(item["satisfied"] for item in mom)

    return {
        "phi_values": phis,
        "hamiltonian_all_vacuum_satisfied": ham_ok,
        "momentum_all_satisfied": mom_ok,
        "hamiltonian_values": [item["hamiltonian_value"] for item in ham],
        "all_pass": ham_ok and mom_ok,
    }


def adm_falsifier_interface(phi_0: float = 1.0, sigma_dt_threshold: float = 1e-9) -> Dict[str, object]:
    """Map Ricci/ADM time mismatch to PASS/TENSION/FALSIFIED decisions."""
    coincidence = ricci_to_adm_time_coincidence(phi_0=phi_0)
    lapse = coincidence["lapse_at_phi0"]
    omega = coincidence["omega_at_phi0"]
    dt_mismatch = abs(lapse - omega)

    if dt_mismatch < sigma_dt_threshold:
        route = "PASS"
    elif dt_mismatch < 10.0 * sigma_dt_threshold:
        route = "TENSION"
    else:
        route = "FALSIFIED"

    return {
        "phi_0": phi_0,
        "lapse_at_phi0": lapse,
        "omega_at_phi0": omega,
        "dt_mismatch": dt_mismatch,
        "sigma_dt_threshold": sigma_dt_threshold,
        "route": route,
        "criterion": "|N(φ₀) - Ω(φ₀)| vs threshold",
    }


def off_attractor_time_mismatch_scan(
    phi_values: Iterable[float] = DEFAULT_PHI_GRID,
    sigma_dt_threshold: float = 1e-9,
) -> Dict[str, object]:
    """Scan Ricci/ADM mismatch away from the attractor."""
    phis = [float(v) for v in phi_values]
    scans = [
        adm_falsifier_interface(phi_0=phi, sigma_dt_threshold=sigma_dt_threshold)
        for phi in phis
    ]
    attractor_rows = [item for item in scans if _is_attractor_phi(item["phi_0"])]
    if not attractor_rows:
        raise ValueError(
            f"off_attractor_time_mismatch_scan requires phi={ATTRACTOR_PHI} in the scan grid."
        )
    non_attractor = [item for item in scans if not _is_attractor_phi(item["phi_0"])]
    return {
        "phi_values": phis,
        "routes": [item["route"] for item in scans],
        "dt_mismatch_values": [item["dt_mismatch"] for item in scans],
        "attractor_route": attractor_rows[0]["route"],
        "non_attractor_routes": [item["route"] for item in non_attractor],
        "non_attractor_detected": any(item["route"] != "PASS" for item in non_attractor),
        "scan": scans,
    }


def off_attractor_severity_profile(
    phi_values: Iterable[float] = DEFAULT_PHI_GRID,
    sigma_dt_threshold: float = 1e-9,
) -> Dict[str, object]:
    """Summarize off-attractor mismatch severity for closure-grade reporting."""
    scan = off_attractor_time_mismatch_scan(phi_values=phi_values, sigma_dt_threshold=sigma_dt_threshold)
    rows = list(scan["scan"])
    attractor_candidates = [item for item in rows if _is_attractor_phi(item["phi_0"])]
    if not attractor_candidates:
        raise ValueError(
            f"off_attractor_severity_profile requires phi={ATTRACTOR_PHI} in the scan grid."
        )
    attractor = attractor_candidates[0]
    worst = max(rows, key=lambda item: item["dt_mismatch"])
    non_attractor_rows = [item for item in rows if not _is_attractor_phi(item["phi_0"])]
    if not non_attractor_rows:
        raise ValueError("off_attractor_severity_profile requires at least one non-attractor phi value.")
    min_non_attractor = min(non_attractor_rows, key=lambda item: item["dt_mismatch"])
    # If attractor mismatch is numerically exact (or effectively exact), the
    # worst/off-attractor ratio is mathematically unbounded, so we return inf.
    ratio = (
        float("inf")
        if abs(attractor["dt_mismatch"]) < MIN_DT_MISMATCH_FOR_RATIO
        else worst["dt_mismatch"] / attractor["dt_mismatch"]
    )
    return {
        "sigma_dt_threshold": sigma_dt_threshold,
        "attractor_phi": attractor["phi_0"],
        "attractor_dt_mismatch": attractor["dt_mismatch"],
        "worst_phi": worst["phi_0"],
        "worst_dt_mismatch": worst["dt_mismatch"],
        "min_non_attractor_phi": min_non_attractor["phi_0"],
        "min_non_attractor_dt_mismatch": min_non_attractor["dt_mismatch"],
        "worst_to_attractor_ratio": ratio,
        "attractor_is_minimum": attractor["dt_mismatch"] <= min_non_attractor["dt_mismatch"],
        "all_off_attractor_nonpass": all(item["route"] != "PASS" for item in non_attractor_rows),
    }


def radion_quantization_closure() -> Dict[str, object]:
    """Return the local canonical quantization evidence bundle."""
    return canonical_quantization_report()


def adm_quantitative_closure_report() -> Dict[str, object]:
    """Consolidated closure report for the ADM quantitative gap."""
    inv = lapse_scaling_invariance()
    constraints = adm_constraint_audit()
    consistency = adm_consistency_check(n_samples=25)
    falsifier_attractor = adm_falsifier_interface(phi_0=1.0)
    off_attractor = off_attractor_time_mismatch_scan()
    severity = off_attractor_severity_profile()
    radion_quantization = radion_quantization_closure()

    all_pass = (
        inv["all_pass"]
        and constraints["all_pass"]
        and consistency["all_passed"]
        and falsifier_attractor["route"] == "PASS"
        and off_attractor["non_attractor_detected"]
        and severity["attractor_is_minimum"]
        and severity["all_off_attractor_nonpass"]
        and radion_quantization["status"] == "LOCAL_CANONICAL_CLOSURE"
    )

    return {
        "sprint": "ADM_QUANTITATIVE_CLOSURE",
        "version": "v10.32",
        "gap": "G1 ADM quantitative closure",
        "lapse_invariance": inv,
        "constraint_audit": constraints,
        "consistency_check": consistency,
        "falsifier_interface_attractor": falsifier_attractor,
        "off_attractor_time_scan": off_attractor,
        "off_attractor_severity_profile": severity,
        "radion_local_quantization": radion_quantization,
        "status": "CLOSED_QUANTITATIVE" if all_pass else "OPEN",
        "all_gates_pass": all_pass,
        "residual_open_item": (
            "Full 5D Wheeler-DeWitt constraint algebra, operator ordering, and non-local mode coupling remain open."
        ),
    }
