# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 232 — Universal Cancer Control Framework.

Adjacent applied research track (non-hardgate): this module does not claim a
single universal cure. It provides a universal *method* for:

1) prediction (quantified control probability from bottleneck vectors),
2) treatability direction (missing-key axis per cancer type), and
3) increasingly curable strategy design (multi-agent orchestration).

All "cure" language is hypothetical and operationalized as modelled control
probability under explicit assumptions.
"""
from __future__ import annotations

from decimal import Decimal, getcontext
import math
import statistics
from typing import Any, Mapping

try:
    from jax import config as jax_config
    import jax.numpy as jnp
    jax_config.update("jax_enable_x64", True)
    JAX_AVAILABLE = True
except (ImportError, ModuleNotFoundError):  # pragma: no cover - optional dependency
    jnp = None  # type: ignore[assignment]
    JAX_AVAILABLE = False

__provenance__ = {
    "pillar": 232,
    "title": "Universal Cancer Control Framework",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "status": (
        "ADJACENT RESEARCH TRACK — universal method for prediction and "
        "treatability routing; no claim of a clinically validated universal cure"
    ),
}

__all__ = [
    "N_W",
    "K_CS",
    "C_S",
    "PHI0",
    "JAX_AVAILABLE",
    "DEFAULT_AXIS_WEIGHTS",
    "precision_digits_for_bits",
    "precision_weighted_control_probability",
    "universal_prediction_engine",
    "missing_key_direction",
    "cancer_type_solution_directions",
    "multi_agent_cancer_workforce_plan",
    "pillar232_universal_control_hypothesis",
]

# Framework constants
N_W: int = 5
K_CS: int = 74
C_S: float = 12.0 / 37.0
PHI0: float = 0.7390851332151607

_VALID_BITS = {64, 128, 256, 512}
_EPS = Decimal("1e-30")

DEFAULT_AXIS_WEIGHTS: dict[str, float] = {
    "heterogeneity_gap": 0.20,
    "resistance_gap": 0.20,
    "immune_escape_gap": 0.15,
    "early_detection_gap": 0.15,
    "targetability_gap": 0.15,
    "access_gap": 0.15,
}

_DIRECTION_LIBRARY: dict[str, str] = {
    "heterogeneity_gap": "Prioritize multi-region profiling and adaptive combination scheduling.",
    "resistance_gap": "Front-load multi-agent resistance prevention and longitudinal ctDNA monitoring.",
    "immune_escape_gap": "Prioritize tumor-immune microenvironment conversion and rational IO combinations.",
    "early_detection_gap": "Deploy risk-stratified early-detection pathways with PPV-constrained thresholds.",
    "targetability_gap": "Expand actionable biomarker coverage and basket/umbrella precision protocols.",
    "access_gap": "Close enrollment/coverage barriers with decentralized trials and OOP protection.",
}


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def precision_digits_for_bits(precision_bits: int) -> int:
    """Return decimal digits needed to simulate a binary precision lane."""
    if precision_bits not in _VALID_BITS:
        raise ValueError(f"precision_bits must be one of {_VALID_BITS}.")
    # ceil(bits * log10(2)) with a small safety margin for chained operations.
    return int(math.ceil(precision_bits * math.log10(2))) + 5


def _validate_profile(profile: Mapping[str, float], axes: list[str]) -> None:
    for axis in axes:
        if axis not in profile:
            raise ValueError(f"Profile missing required axis: {axis}")
        if not (0.0 <= float(profile[axis]) <= 1.0):
            raise ValueError(f"{axis} must be in [0, 1], got {profile[axis]}")


def precision_weighted_control_probability(
    profile: Mapping[str, float],
    axis_weights: Mapping[str, float] | None = None,
    precision_bits: int = 256,
    use_jax: bool = True,
) -> dict[str, Any]:
    """Compute weighted geometric control probability from bottleneck gaps.

    Each axis is a normalized gap in [0, 1], where larger means more severe.
    The remediation term is (1-gap). The weighted geometric mean is:

        P_control = exp(sum_i w_i * ln(max(1-gap_i, eps))) / sum_i w_i

    [CALCULATED] arithmetic/log-exp pipeline.
    [SPECULATIVE] interpretation of P_control as a "hypothetical curability lane".
    """
    weights = dict(DEFAULT_AXIS_WEIGHTS if axis_weights is None else axis_weights)
    axes = list(weights.keys())
    if any(v < 0.0 for v in weights.values()):
        raise ValueError("All axis weights must be non-negative.")
    if sum(weights.values()) <= 0.0:
        raise ValueError("At least one axis weight must be positive.")
    _validate_profile(profile, axes)

    digits = precision_digits_for_bits(precision_bits)
    getcontext().prec = digits

    total_w = Decimal(str(sum(weights.values())))
    weighted_log_sum = Decimal("0")
    for axis, w in weights.items():
        remediation = Decimal(str(1.0 - float(profile[axis])))
        remediation = remediation if remediation > _EPS else _EPS
        weighted_log_sum += Decimal(str(w)) * remediation.ln()
    p_decimal = (weighted_log_sum / total_w).exp()
    p_hp = _clamp01(float(p_decimal))

    p_jax = None
    if use_jax and JAX_AVAILABLE:
        rem = jnp.asarray([1.0 - float(profile[a]) for a in axes], dtype=jnp.float64)
        rem = jnp.clip(rem, 1e-30, 1.0)
        w = jnp.asarray([weights[a] for a in axes], dtype=jnp.float64)
        p_jax = float(jnp.exp(jnp.sum(w * jnp.log(rem)) / jnp.sum(w)))

    limiting_axis = max(axes, key=lambda a: float(profile[a]))
    band = (
        "high-control-lane"
        if p_hp >= 0.70
        else "intermediate-control-lane"
        if p_hp >= 0.40
        else "low-control-lane"
    )
    return {
        "control_probability": p_hp,
        "control_probability_jax": p_jax,
        "precision_bits": precision_bits,
        "decimal_digits": digits,
        "limiting_axis": limiting_axis,
        "treatability_band": band,
        "status": (
            "CALCULATED (weighted geometric mean with high-precision decimal lane; "
            "optional JAX cross-check)"
        ),
        "notes": (
            "Interpretation as a curability trajectory is hypothetical and must be "
            "validated against longitudinal clinical outcomes."
        ),
    }


def universal_prediction_engine(
    cancer_profiles: Mapping[str, Mapping[str, float]],
    axis_weights: Mapping[str, float] | None = None,
    precision_bits: int = 256,
    use_jax: bool = True,
) -> dict[str, Any]:
    """Run prediction pipeline for multiple cancer types."""
    if not cancer_profiles:
        raise ValueError("cancer_profiles must be non-empty.")

    per_type: dict[str, Any] = {}
    probs: list[float] = []
    for cancer_type, profile in cancer_profiles.items():
        r = precision_weighted_control_probability(
            profile=profile,
            axis_weights=axis_weights,
            precision_bits=precision_bits,
            use_jax=use_jax,
        )
        per_type[cancer_type] = r
        probs.append(r["control_probability"])

    mean_control = sum(probs) / len(probs)
    median_control = float(statistics.median(probs))
    return {
        "n_cancer_types": len(per_type),
        "per_type": per_type,
        "portfolio_mean_control_probability": mean_control,
        "portfolio_median_control_probability": median_control,
        "status": "CALCULATED (deterministic multi-type aggregation)",
        "notes": (
            "Portfolio-level values summarize tractability under provided profile "
            "inputs; they are not clinical efficacy claims."
        ),
    }


def missing_key_direction(cancer_type: str, profile: Mapping[str, float]) -> dict[str, Any]:
    """Identify the largest unresolved axis and return the directional strategy."""
    _validate_profile(profile, list(DEFAULT_AXIS_WEIGHTS.keys()))
    missing_axis = max(DEFAULT_AXIS_WEIGHTS.keys(), key=lambda a: float(profile[a]))
    return {
        "cancer_type": cancer_type,
        "missing_key_axis": missing_axis,
        "gap_value": float(profile[missing_axis]),
        "direction": _DIRECTION_LIBRARY[missing_axis],
        "status": "CALCULATED (max-gap routing) + EMPIRICAL strategy direction",
    }


def cancer_type_solution_directions(
    cancer_profiles: Mapping[str, Mapping[str, float]],
) -> list[dict[str, Any]]:
    """Return missing-key direction for each cancer type."""
    if not cancer_profiles:
        raise ValueError("cancer_profiles must be non-empty.")
    return [missing_key_direction(name, profile) for name, profile in cancer_profiles.items()]


def multi_agent_cancer_workforce_plan(
    cancer_profiles: Mapping[str, Mapping[str, float]],
) -> dict[str, Any]:
    """Generate a multi-agent research workforce plan with coherence scoring."""
    if not cancer_profiles:
        raise ValueError("cancer_profiles must be non-empty.")
    directions = cancer_type_solution_directions(cancer_profiles)
    axis_counts: dict[str, int] = {}
    for d in directions:
        axis = d["missing_key_axis"]
        axis_counts[axis] = axis_counts.get(axis, 0) + 1
    if not axis_counts:
        raise ValueError("No direction axes available for workforce planning.")

    lead_axis = max(axis_counts, key=lambda k: axis_counts[k])
    coherence = axis_counts[lead_axis] / max(1, len(directions))
    coherence = _clamp01(0.5 * coherence + 0.5 * PHI0)

    agents = [
        {"agent": "A1-data-ingest", "role": "public-dataset ingestion + harmonization"},
        {"agent": "A2-prediction", "role": "risk/model calibration + external validation"},
        {"agent": "A3-biomarker", "role": "molecular stratification + actionability routing"},
        {"agent": "A4-therapy-design", "role": "combination/adaptive protocol optimization"},
        {"agent": "A5-trial-ops", "role": "decentralized enrollment + protocol logistics"},
        {"agent": "A6-access-equity", "role": "financial/toxicity/access barrier closure"},
        {"agent": "A7-precision-audit", "role": "256/512-bit numeric reproducibility checks"},
        {"agent": "A8-synthesis-lead", "role": "cross-agent coherence governance"},
    ]

    return {
        "lead_axis": lead_axis,
        "axis_distribution": axis_counts,
        "coherence_score": coherence,
        "agents": agents,
        "status": "CALCULATED (coverage/coherence scoring) + OPERATIONAL plan",
        "notes": (
            "Higher coherence score indicates stronger shared bottleneck focus "
            "across cancer types while preserving multi-agent specialization."
        ),
    }


def pillar232_universal_control_hypothesis(
    cancer_profiles: Mapping[str, Mapping[str, float]],
    precision_bits: int = 256,
    use_jax: bool = True,
) -> dict[str, Any]:
    """Integrated Pillar 232 pipeline for prediction + direction + orchestration."""
    prediction = universal_prediction_engine(
        cancer_profiles=cancer_profiles,
        precision_bits=precision_bits,
        use_jax=use_jax,
    )
    directions = cancer_type_solution_directions(cancer_profiles)
    workforce = multi_agent_cancer_workforce_plan(cancer_profiles)

    universal_viability = (
        "plausible-universal-method"
        if prediction["portfolio_mean_control_probability"] >= 0.40
        else "insufficient-current-tractability"
    )
    return {
        "prediction": prediction,
        "directions": directions,
        "workforce": workforce,
        "universal_method_viability": universal_viability,
        "status": (
            "HYPOTHETICAL-PLAUSIBLE framework output; not a treatment recommendation"
        ),
        "falsification_condition": (
            "If independent cohorts fail to show monotonic outcome improvement as "
            "the computed control_probability increases, the framework is invalid."
        ),
    }
