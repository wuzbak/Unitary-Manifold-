# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 243 — Unified Scientific Interoperability & Validation Fabric (USIVF).

Adjacent research track (non-hardgate): a deterministic interoperability engine
that combines transferable workflow patterns inspired by:

- Einstein Toolkit (large-scale numerical-relativity workflow discipline)
- xAct / FeynCalc / Cadabra (symbolic identity and reduction consistency)
- CAMB / CLASS / CosmoMC / PyTransport (cosmology pipeline contracts)
- SageMath ecosystem (broad mathematical verification and test culture)

The USIVF does not claim that external frameworks are equivalent in scope.  It
implements a reproducible, contract-driven synthesis layer inside this
repository while preserving strict hardgate separation.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import random
from typing import Any

try:
    import mpmath
except ImportError:  # pragma: no cover - optional dependency
    mpmath = None

try:
    import sympy
except ImportError:  # pragma: no cover - optional dependency
    sympy = None

N_W: int = 5
N_2: int = 7
K_CS: int = 74
C_S: float = 12.0 / 37.0
XI_C: float = 35.0 / 74.0
PHI0: float = 0.7390851332151607
HOLON_THEORETICAL_CONFIDENCE: float = 1.0
MATH_BACKEND_TOLERANCE_EXPONENT: int = -12

ADJACENCY_TRACK_LABEL: str = "ADJACENT_TRACK_NON_HARDGATE"
USIVF_TRACK_LABEL: str = "USIVF_INTEROPERABILITY_TRACK"
OPERATIONAL_MODULE: bool = True
OPERATIONAL_MODULE_CATEGORY: str = "CI_WORKFLOW_ENGINEERING"

LANE_ORDER: tuple[str, ...] = (
    "numerical_relativity_workflow",
    "symbolic_algebra_consistency",
    "cosmology_pipeline_compatibility",
    "mathematical_verification",
    "governance_assistant_traceability",
)
N_LANES: int = len(LANE_ORDER)

CONTRACT_THRESHOLDS: dict[str, float] = {
    "numerical_relativity_workflow": 0.75,
    "symbolic_algebra_consistency": 0.80,
    "cosmology_pipeline_compatibility": 0.78,
    "mathematical_verification": 0.82,
    "governance_assistant_traceability": 0.80,
}

__provenance__ = {
    "pillar": 243,
    "title": "Unified Scientific Interoperability & Validation Fabric (USIVF)",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "status": (
        "ADJACENT RESEARCH TRACK — deterministic interoperability and validation "
        "fabric; non-hardgate, no ToE score delta"
    ),
    "external_scope_statement": (
        "Einstein Toolkit strongest match for large computational-physics "
        "infrastructure (numerical relativity focus); xAct/FeynCalc/Cadabra "
        "symbolic-algebra strengths; CAMB/CLASS/CosmoMC/PyTransport cosmology "
        "pipeline strengths; SageMath broad math verification culture."
    ),
}


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))


def _validate01(name: str, value: float) -> float:
    v = float(value)
    if not (0.0 <= v <= 1.0):
        raise ValueError(f"{name} must be in [0, 1], got {value}")
    return v


@dataclass(frozen=True)
class InteroperabilityScenario:
    """Input metrics for USIVF lane scoring, all in [0, 1]."""

    nr_job_success_rate: float
    nr_reproducibility_rate: float
    symbolic_identity_pass_rate: float
    symbolic_reduction_stability: float
    cosmology_contract_pass_rate: float
    cosmology_tolerance_pass_rate: float
    math_invariant_pass_rate: float
    math_reproducibility_rate: float
    governance_traceability_rate: float
    assistant_auditability_rate: float

    def __post_init__(self) -> None:
        _validate01("nr_job_success_rate", self.nr_job_success_rate)
        _validate01("nr_reproducibility_rate", self.nr_reproducibility_rate)
        _validate01("symbolic_identity_pass_rate", self.symbolic_identity_pass_rate)
        _validate01("symbolic_reduction_stability", self.symbolic_reduction_stability)
        _validate01("cosmology_contract_pass_rate", self.cosmology_contract_pass_rate)
        _validate01("cosmology_tolerance_pass_rate", self.cosmology_tolerance_pass_rate)
        _validate01("math_invariant_pass_rate", self.math_invariant_pass_rate)
        _validate01("math_reproducibility_rate", self.math_reproducibility_rate)
        _validate01("governance_traceability_rate", self.governance_traceability_rate)
        _validate01("assistant_auditability_rate", self.assistant_auditability_rate)


def separation_guard() -> dict[str, Any]:
    """Explicit non-hardgate boundary declaration for this adjacent lane."""
    return {
        "label": ADJACENCY_TRACK_LABEL,
        "track": USIVF_TRACK_LABEL,
        "hardgate_isolation": True,
        "toe_score_delta_allowed": False,
        "physics_claim_promotion_allowed": False,
        "message": (
            "USIVF is an adjacent interoperability lane only. It does not promote "
            "hardgate physics claims by itself."
        ),
    }


def numerical_relativity_workflow_readiness(s: InteroperabilityScenario) -> float:
    return _clamp01(0.5 * (s.nr_job_success_rate + s.nr_reproducibility_rate))


def symbolic_algebra_consistency_score(s: InteroperabilityScenario) -> float:
    return _clamp01(0.5 * (s.symbolic_identity_pass_rate + s.symbolic_reduction_stability))


def cosmology_pipeline_compatibility_score(s: InteroperabilityScenario) -> float:
    return _clamp01(0.5 * (s.cosmology_contract_pass_rate + s.cosmology_tolerance_pass_rate))


def mathematical_verification_score(s: InteroperabilityScenario) -> float:
    return _clamp01(0.5 * (s.math_invariant_pass_rate + s.math_reproducibility_rate))


def governance_assistant_traceability_score(s: InteroperabilityScenario) -> float:
    return _clamp01(0.5 * (s.governance_traceability_rate + s.assistant_auditability_rate))


def mathematical_backend_verification(
    dps: int = 50,
    phi0: float = PHI0,
) -> dict[str, Any]:
    """Deterministic symbolic+numeric verification lane helper.

    Returns a compact contract record that uses:
    - sympy for symbolic identity validation
    - mpmath for high-precision fixed-point residual evaluation
    """
    symbolic_ok = False
    if sympy is not None:
        x, y = sympy.symbols("x y", real=True)
        identity = (x + y) ** 2 - (x**2 + 2 * x * y + y**2)
        symbolic_ok = bool(sympy.simplify(identity) == 0)

    numeric_ok = False
    residual = float("nan")
    tolerance = float("nan")
    if mpmath is not None:
        with mpmath.workdps(dps):
            phi_mp = mpmath.mpf(phi0)
            residual_signed_mp = mpmath.cos(phi_mp) - phi_mp
            residual_mp = abs(residual_signed_mp)
            tolerance_mp = mpmath.mpf(10) ** MATH_BACKEND_TOLERANCE_EXPONENT
            residual = float(residual_mp)
            tolerance = float(tolerance_mp)
            numeric_ok = bool(residual_mp <= tolerance_mp)

    return {
        "sympy_available": sympy is not None,
        "mpmath_available": mpmath is not None,
        "symbolic_identity_passed": symbolic_ok,
        "numeric_fixed_point_passed": numeric_ok,
        "passed": (sympy is not None) and (mpmath is not None) and symbolic_ok and numeric_ok,
        "dps": int(dps),
        "phi0": float(phi0),
        "residual_abs": residual,
        "tolerance_abs": tolerance,
    }


def lane_scores(s: InteroperabilityScenario) -> dict[str, float]:
    return {
        "numerical_relativity_workflow": numerical_relativity_workflow_readiness(s),
        "symbolic_algebra_consistency": symbolic_algebra_consistency_score(s),
        "cosmology_pipeline_compatibility": cosmology_pipeline_compatibility_score(s),
        "mathematical_verification": mathematical_verification_score(s),
        "governance_assistant_traceability": governance_assistant_traceability_score(s),
    }


def deterministic_run_id(s: InteroperabilityScenario, seed: int = 243) -> str:
    payload = (
        f"{seed}|"
        f"{s.nr_job_success_rate:.6f}|{s.nr_reproducibility_rate:.6f}|"
        f"{s.symbolic_identity_pass_rate:.6f}|{s.symbolic_reduction_stability:.6f}|"
        f"{s.cosmology_contract_pass_rate:.6f}|{s.cosmology_tolerance_pass_rate:.6f}|"
        f"{s.math_invariant_pass_rate:.6f}|{s.math_reproducibility_rate:.6f}|"
        f"{s.governance_traceability_rate:.6f}|{s.assistant_auditability_rate:.6f}"
    ).encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()[:16]
    return f"usivf-{seed}-{digest}"


def workflow_manifest(s: InteroperabilityScenario, seed: int = 243) -> dict[str, Any]:
    """Deterministic workflow metadata inspired by ET-style run discipline."""
    scores = lane_scores(s)
    return {
        "engine": "USIVF",
        "pillar": 243,
        "deterministic_run_id": deterministic_run_id(s, seed=seed),
        "lane_count": N_LANES,
        "lane_order": LANE_ORDER,
        "seed_constants": {"N_W": N_W, "K_CS": K_CS, "C_S": C_S, "XI_C": XI_C},
        "inspiration_map": {
            "numerical_relativity_workflow": "Einstein Toolkit",
            "symbolic_algebra_consistency": "xAct/FeynCalc/Cadabra",
            "cosmology_pipeline_compatibility": "CAMB/CLASS/CosmoMC/PyTransport",
            "mathematical_verification": "SageMath-style validation culture",
            "governance_assistant_traceability": "UM governance + assistant stack",
        },
        "lane_jobs": [
            {
                "lane": lane,
                "target_score": CONTRACT_THRESHOLDS[lane],
                "measured_score": scores[lane],
                "status": "PASS" if scores[lane] >= CONTRACT_THRESHOLDS[lane] else "FAIL",
            }
            for lane in LANE_ORDER
        ],
    }


def interoperability_contract_results(
    s: InteroperabilityScenario,
    thresholds: dict[str, float] | None = None,
) -> dict[str, Any]:
    thresholds = thresholds or CONTRACT_THRESHOLDS
    missing = set(LANE_ORDER) - set(thresholds)
    if missing:
        raise ValueError(f"Missing thresholds for lanes: {sorted(missing)}")
    for lane in LANE_ORDER:
        _validate01(f"threshold[{lane}]", thresholds[lane])

    scores = lane_scores(s)
    by_lane: dict[str, dict[str, float | bool]] = {}
    failed: list[str] = []
    for lane in LANE_ORDER:
        score = scores[lane]
        target = float(thresholds[lane])
        passed = score >= target
        if not passed:
            failed.append(lane)
        by_lane[lane] = {
            "score": score,
            "target": target,
            "passed": passed,
            "deficit": _clamp01(target - score),
        }
    failure_fraction = len(failed) / N_LANES
    return {
        "by_lane": by_lane,
        "failed_lanes": failed,
        "passed_all_contracts": len(failed) == 0,
        "failure_fraction": failure_fraction,
    }


def contract_penalty(s: InteroperabilityScenario) -> float:
    contracts = interoperability_contract_results(s)
    return _clamp01(C_S * contracts["failure_fraction"])


def overall_interoperability_confidence_index(s: InteroperabilityScenario) -> float:
    """Aggregate lane confidence index in [0, 1].

    Formula:
        mean_lane_score = mean(lane_scores)
        penalty         = C_S × failure_fraction
        index           = clamp(mean_lane_score × (1 − penalty) × HOLON_CONF)
    """
    scores = lane_scores(s)
    mean_lane_score = sum(scores.values()) / len(scores)
    penalty = contract_penalty(s)
    return _clamp01(mean_lane_score * (1.0 - penalty) * HOLON_THEORETICAL_CONFIDENCE)


def interoperability_status(index: float) -> str:
    x = _validate01("index", index)
    if x < 0.50:
        return "USIVF_CRITICAL"
    if x < 0.68:
        return "USIVF_PARTIAL"
    if x < 0.84:
        return "USIVF_OPERATIONAL"
    return "USIVF_ROBUST"


def monte_carlo_interoperability(
    s: InteroperabilityScenario,
    n_trials: int = 200,
    seed: int = 243,
) -> dict[str, float]:
    if n_trials < 1:
        raise ValueError("n_trials must be >= 1")
    rng = random.Random(seed)
    vals: list[float] = []
    for _ in range(n_trials):
        p = InteroperabilityScenario(
            nr_job_success_rate=_clamp01(s.nr_job_success_rate + rng.uniform(-0.05, 0.05)),
            nr_reproducibility_rate=_clamp01(s.nr_reproducibility_rate + rng.uniform(-0.05, 0.05)),
            symbolic_identity_pass_rate=_clamp01(s.symbolic_identity_pass_rate + rng.uniform(-0.05, 0.05)),
            symbolic_reduction_stability=_clamp01(s.symbolic_reduction_stability + rng.uniform(-0.05, 0.05)),
            cosmology_contract_pass_rate=_clamp01(s.cosmology_contract_pass_rate + rng.uniform(-0.05, 0.05)),
            cosmology_tolerance_pass_rate=_clamp01(s.cosmology_tolerance_pass_rate + rng.uniform(-0.05, 0.05)),
            math_invariant_pass_rate=_clamp01(s.math_invariant_pass_rate + rng.uniform(-0.05, 0.05)),
            math_reproducibility_rate=_clamp01(s.math_reproducibility_rate + rng.uniform(-0.05, 0.05)),
            governance_traceability_rate=_clamp01(s.governance_traceability_rate + rng.uniform(-0.05, 0.05)),
            assistant_auditability_rate=_clamp01(s.assistant_auditability_rate + rng.uniform(-0.05, 0.05)),
        )
        vals.append(overall_interoperability_confidence_index(p))

    vals.sort()
    return {
        "mean_index": sum(vals) / len(vals),
        "p10_index": vals[max(0, int(0.1 * len(vals)) - 1)],
        "p50_index": vals[len(vals) // 2],
        "p90_index": vals[min(len(vals) - 1, int(0.9 * len(vals)))],
    }


def usivf_full_report(
    s: InteroperabilityScenario,
    n_trials: int = 200,
    seed: int = 243,
) -> dict[str, Any]:
    scores = lane_scores(s)
    contracts = interoperability_contract_results(s)
    index = overall_interoperability_confidence_index(s)
    return {
        "pillar": 243,
        "status": __provenance__["status"],
        "adjacent_track_label": ADJACENCY_TRACK_LABEL,
        "usivf_track_label": USIVF_TRACK_LABEL,
        "lane_count_equals_n_w": N_LANES == N_W,
        "lane_order": LANE_ORDER,
        "lane_scores": scores,
        "contracts": contracts,
        "contract_penalty": contract_penalty(s),
        "overall_interoperability_confidence_index": index,
        "overall_status": interoperability_status(index),
        "workflow_manifest": workflow_manifest(s, seed=seed),
        "monte_carlo": monte_carlo_interoperability(s, n_trials=n_trials, seed=seed),
        "mathematical_backend_verification": mathematical_backend_verification(),
        "separation_guard": separation_guard(),
        "falsification_condition": (
            "FALSIFIED as an adjacent interoperability engine if reproducible "
            "cross-lane contract checks systematically fail against declared "
            "benchmarks and tolerance gates."
        ),
    }


def baseline_interoperability_scenario() -> InteroperabilityScenario:
    return InteroperabilityScenario(
        nr_job_success_rate=0.86,
        nr_reproducibility_rate=0.84,
        symbolic_identity_pass_rate=0.88,
        symbolic_reduction_stability=0.83,
        cosmology_contract_pass_rate=0.81,
        cosmology_tolerance_pass_rate=0.79,
        math_invariant_pass_rate=0.87,
        math_reproducibility_rate=0.86,
        governance_traceability_rate=0.90,
        assistant_auditability_rate=0.88,
    )


def pillar243_usivf_report(
    n_trials: int = 200,
    seed: int = 243,
) -> dict[str, Any]:
    return usivf_full_report(
        baseline_interoperability_scenario(),
        n_trials=n_trials,
        seed=seed,
    )


__all__ = [
    "N_W",
    "N_2",
    "K_CS",
    "C_S",
    "XI_C",
    "PHI0",
    "HOLON_THEORETICAL_CONFIDENCE",
    "MATH_BACKEND_TOLERANCE_EXPONENT",
    "ADJACENCY_TRACK_LABEL",
    "USIVF_TRACK_LABEL",
    "LANE_ORDER",
    "N_LANES",
    "CONTRACT_THRESHOLDS",
    "__provenance__",
    "InteroperabilityScenario",
    "separation_guard",
    "numerical_relativity_workflow_readiness",
    "symbolic_algebra_consistency_score",
    "cosmology_pipeline_compatibility_score",
    "mathematical_verification_score",
    "mathematical_backend_verification",
    "governance_assistant_traceability_score",
    "lane_scores",
    "deterministic_run_id",
    "workflow_manifest",
    "interoperability_contract_results",
    "contract_penalty",
    "overall_interoperability_confidence_index",
    "interoperability_status",
    "monte_carlo_interoperability",
    "usivf_full_report",
    "baseline_interoperability_scenario",
    "pillar243_usivf_report",
]
