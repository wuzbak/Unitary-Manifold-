# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 236 — Critique Hardening Engine (2026).

Adjacency track (non-hardgate): provides a reproducible framework to harden
repository scientific practice against critique by combining:
1) external-validation ledgering,
2) source-quality ladder labeling,
3) preregistered falsification routing,
4) Monte Carlo stability simulation.

🔵 ADJACENT TRACK — This module does NOT alter the Unitary Manifold ToE score.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

import numpy as np

__provenance__ = {
    "pillar": 236,
    "title": "Critique Hardening Engine",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "status": (
        "ADJACENT RESEARCH TRACK — critique hardening via external validation, "
        "source-quality tiering, preregistered falsification, and simulation"
    ),
}

N_W: int = 5
K_CS: int = 74
C_S: float = 12.0 / 37.0

NS_UM: float = 0.9635
R_UM_BRAIDED: float = 0.0315
BETA_UM_PRIMARY_DEG: float = 0.331
BETA_UM_SHADOW_DEG: float = 0.273
P236_W0_UM: float = -0.9302
P236_WA_UM: float = 0.0

_PROB_FLOOR: float = 1e-12  # avoids log2(0) in entropy calculation


@dataclass(frozen=True)
class ExternalConstraint:
    """Observation-side constraint used by Pillar 236 checks."""

    observable: str
    observed: float
    sigma: float | None = None
    upper_bound: float | None = None
    confidence_level: str = "68%"
    experiment: str = ""
    year: int = 0
    source_url: str = ""
    source_tier: str = "T2"


def source_quality_ladder() -> dict[str, dict[str, str | int]]:
    """Return canonical source-quality tiers for critique hardening."""
    return {
        "T1": {
            "rank": 1,
            "label": "First-principles derivation + executable verification",
            "usage_rule": "Allowed for hardgate claims.",
        },
        "T2": {
            "rank": 2,
            "label": "Peer-reviewed measurement or major-collaboration release",
            "usage_rule": "Allowed for external validation comparisons.",
        },
        "T3": {
            "rank": 3,
            "label": "Cross-check source or independent secondary analysis",
            "usage_rule": "Allowed for triangulation, not sole hardgate support.",
        },
        "T4": {
            "rank": 4,
            "label": "Methodological commentary / forecast document",
            "usage_rule": "Allowed for planning and readiness only.",
        },
        "T5": {
            "rank": 5,
            "label": "Outreach or speculative discussion",
            "usage_rule": "Not admissible as standalone quantitative evidence.",
        },
    }


def default_external_constraints() -> dict[str, ExternalConstraint]:
    """Canonical external constraints used by this pillar.

    Values reflect repository-tracked observational anchors and can be updated as
    new releases arrive.
    """
    return {
        "n_s": ExternalConstraint(
            observable="n_s",
            observed=0.9649,
            sigma=0.0042,
            confidence_level="68%",
            experiment="Planck 2018",
            year=2018,
            source_url="https://arxiv.org/abs/1807.06209",
            source_tier="T2",
        ),
        "r": ExternalConstraint(
            observable="r",
            observed=0.0,
            upper_bound=0.036,
            confidence_level="95%",
            experiment="BICEP/Keck BK18",
            year=2022,
            source_url="https://arxiv.org/abs/2203.16556",
            source_tier="T2",
        ),
        "beta": ExternalConstraint(
            observable="beta_deg",
            observed=0.342,
            sigma=0.094,
            confidence_level="68%",
            experiment="Planck PR4 / NPIPE",
            year=2022,
            source_url="https://arxiv.org/abs/2201.07241",
            source_tier="T2",
        ),
        "w0": ExternalConstraint(
            observable="w0",
            observed=-0.90,
            sigma=0.055,
            confidence_level="68%",
            experiment="DESI DR2 combined",
            year=2025,
            source_url="https://arxiv.org/abs/2503.14738",
            source_tier="T2",
        ),
        "wa": ExternalConstraint(
            observable="wa",
            observed=-0.55,
            sigma=0.20,
            confidence_level="68%",
            experiment="DESI DR2 combined",
            year=2025,
            source_url="https://arxiv.org/abs/2503.14738",
            source_tier="T2",
        ),
        "litebird_beta_sigma": ExternalConstraint(
            observable="sigma_beta_deg",
            observed=0.02,
            sigma=None,
            confidence_level="forecast",
            experiment="LiteBIRD mission forecast",
            year=2023,
            source_url="https://arxiv.org/abs/2202.02773",
            source_tier="T4",
        ),
    }


def default_predictions() -> dict[str, float]:
    """Return canonical UM predictions compared by this pillar."""
    return {
        "n_s": NS_UM,
        "r": R_UM_BRAIDED,
        "beta_primary": BETA_UM_PRIMARY_DEG,
        "beta_shadow": BETA_UM_SHADOW_DEG,
        "w0": P236_W0_UM,
        "wa": P236_WA_UM,
    }


def _validate_constraint(c: ExternalConstraint) -> None:
    if c.sigma is not None and c.sigma <= 0:
        raise ValueError(f"sigma must be > 0 for {c.observable}")
    if c.upper_bound is not None and c.upper_bound < 0:
        raise ValueError(f"upper_bound must be >= 0 for {c.observable}")


def evaluate_against_constraint(predicted: float, constraint: ExternalConstraint) -> dict[str, Any]:
    """Evaluate one prediction vs one external constraint."""
    _validate_constraint(constraint)

    if constraint.upper_bound is not None:
        margin = constraint.upper_bound - predicted
        verdict = "CONSISTENT" if margin >= 0 else "FALSIFIED"
        return {
            "observable": constraint.observable,
            "predicted": predicted,
            "observed": constraint.observed,
            "upper_bound": constraint.upper_bound,
            "margin": margin,
            "sigma_distance": None,
            "verdict": verdict,
            "experiment": constraint.experiment,
            "source_tier": constraint.source_tier,
            "source_url": constraint.source_url,
        }

    if constraint.sigma is None:
        return {
            "observable": constraint.observable,
            "predicted": predicted,
            "observed": constraint.observed,
            "upper_bound": None,
            "margin": None,
            "sigma_distance": None,
            "verdict": "INFORMATIONAL",
            "experiment": constraint.experiment,
            "source_tier": constraint.source_tier,
            "source_url": constraint.source_url,
        }

    sigma_distance = abs(predicted - constraint.observed) / constraint.sigma
    if sigma_distance >= 3.0:
        verdict = "FALSIFIED"
    elif sigma_distance >= 2.0:
        verdict = "HIGH_TENSION"
    elif sigma_distance >= 1.0:
        verdict = "TENSION"
    else:
        verdict = "CONSISTENT"

    return {
        "observable": constraint.observable,
        "predicted": predicted,
        "observed": constraint.observed,
        "upper_bound": None,
        "margin": None,
        "sigma_distance": sigma_distance,
        "verdict": verdict,
        "experiment": constraint.experiment,
        "source_tier": constraint.source_tier,
        "source_url": constraint.source_url,
    }


def preregistered_falsification_table() -> list[dict[str, str]]:
    """Return preregistered kill-conditions for major observable lanes."""
    return [
        {
            "id": "F-BETA-1",
            "observable": "beta_deg",
            "trigger": "LiteBIRD publication",
            "kill_condition": "beta outside [0.22, 0.38] deg or in [0.29, 0.31] gap at >=3 sigma",
            "decision_rule": "Mark braided-winding mechanism FALSIFIED.",
        },
        {
            "id": "F-NS-1",
            "observable": "n_s",
            "trigger": "CMB-S4 consolidated release",
            "kill_condition": "n_s inconsistent with 0.9635 at >3 sigma",
            "decision_rule": "Mark inflationary closure lane FALSIFIED.",
        },
        {
            "id": "F-R-1",
            "observable": "r",
            "trigger": "CMB-S4 / LiteBIRD B-mode release",
            "kill_condition": "r confirmed >0.036 or strongly <0.01 against braided channel assumptions",
            "decision_rule": "Mark braided tensor lane FALSIFIED.",
        },
        {
            "id": "F-WA-1",
            "observable": "wa",
            "trigger": "DESI DR3+ combined posterior",
            "kill_condition": "wa != 0 at >=3 sigma and persistent across validated combinations",
            "decision_rule": "Mark frozen-radion dark-energy lane FALSIFIED.",
        },
    ]


def critique_hardening_ledger(
    predictions: dict[str, float] | None = None,
    constraints: dict[str, ExternalConstraint] | None = None,
) -> list[dict[str, Any]]:
    """Compute external-validation ledger rows for core observable checks."""
    p = default_predictions() if predictions is None else dict(predictions)
    c = default_external_constraints() if constraints is None else dict(constraints)

    rows = [
        {
            "claim_id": "P2",
            "check": evaluate_against_constraint(p["n_s"], c["n_s"]),
            "prediction_label": "n_s = 0.9635",
        },
        {
            "claim_id": "P3",
            "check": evaluate_against_constraint(p["r"], c["r"]),
            "prediction_label": "r_braided = 0.0315",
        },
        {
            "claim_id": "P1-primary",
            "check": evaluate_against_constraint(p["beta_primary"], c["beta"]),
            "prediction_label": "beta_primary = 0.331 deg",
        },
        {
            "claim_id": "P1-shadow",
            "check": evaluate_against_constraint(p["beta_shadow"], c["beta"]),
            "prediction_label": "beta_shadow = 0.273 deg",
        },
        {
            "claim_id": "P4-w0",
            "check": evaluate_against_constraint(p["w0"], c["w0"]),
            "prediction_label": "w0 = -0.9302",
        },
        {
            "claim_id": "P4-wa",
            "check": evaluate_against_constraint(p["wa"], c["wa"]),
            "prediction_label": "wa = 0",
        },
    ]
    return rows


def ledger_summary(rows: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Summarize consistency/tension/falsification counts for the ledger."""
    ledger_rows = critique_hardening_ledger() if rows is None else list(rows)
    counts = {"CONSISTENT": 0, "TENSION": 0, "HIGH_TENSION": 0, "FALSIFIED": 0, "INFORMATIONAL": 0}
    for row in ledger_rows:
        verdict = str(row["check"]["verdict"])
        counts[verdict] = counts.get(verdict, 0) + 1

    severity_rank = {"INFORMATIONAL": -1, "CONSISTENT": 0, "TENSION": 1, "HIGH_TENSION": 2, "FALSIFIED": 3}
    max_row = max(ledger_rows, key=lambda x: severity_rank.get(str(x["check"]["verdict"]), 0))

    return {
        "n_checks": len(ledger_rows),
        "counts": counts,
        "max_severity": max_row["check"]["verdict"],
        "highest_risk_claim_id": max_row["claim_id"],
    }


def _sample_constraint(rng: np.random.Generator, c: ExternalConstraint) -> float:
    if c.upper_bound is not None:
        return c.upper_bound
    if c.sigma is None:
        return c.observed
    return float(rng.normal(loc=c.observed, scale=c.sigma))


def monte_carlo_critique_stability(
    samples: int = 200,
    seed: int = 236,
) -> dict[str, Any]:
    """Monte Carlo stress-test of ledger verdict stability under measurement uncertainty."""
    if samples <= 0:
        raise ValueError("samples must be > 0")

    rng = np.random.default_rng(seed)
    base_predictions = default_predictions()
    base_constraints = default_external_constraints()

    keys = ["n_s", "r", "beta", "w0", "wa"]
    verdict_counts: dict[str, dict[str, int]] = {
        "P2": {},
        "P3": {},
        "P1-primary": {},
        "P1-shadow": {},
        "P4-w0": {},
        "P4-wa": {},
    }

    for _ in range(samples):
        sampled_constraints = dict(base_constraints)
        for key in keys:
            c = base_constraints[key]
            sampled_constraints[key] = ExternalConstraint(
                observable=c.observable,
                observed=_sample_constraint(rng, c),
                sigma=c.sigma,
                upper_bound=c.upper_bound,
                confidence_level=c.confidence_level,
                experiment=c.experiment,
                year=c.year,
                source_url=c.source_url,
                source_tier=c.source_tier,
            )

        rows = critique_hardening_ledger(predictions=base_predictions, constraints=sampled_constraints)
        for row in rows:
            cid = str(row["claim_id"])
            if cid not in verdict_counts:
                continue
            verdict = str(row["check"]["verdict"])
            verdict_counts[cid][verdict] = verdict_counts[cid].get(verdict, 0) + 1

    stability: dict[str, dict[str, float]] = {}
    for cid, vdict in verdict_counts.items():
        if not vdict:
            stability[cid] = {"dominant_verdict": "N/A", "dominant_fraction": 0.0, "entropy": 0.0}
            continue
        dominant_verdict, dominant_count = max(vdict.items(), key=lambda kv: kv[1])
        probs = np.array([count / samples for count in vdict.values()])
        entropy = float(-np.sum(probs * np.log2(np.maximum(probs, _PROB_FLOOR))))
        stability[cid] = {
            "dominant_verdict": dominant_verdict,
            "dominant_fraction": dominant_count / samples,
            "entropy": entropy,
        }

    return {
        "samples": samples,
        "seed": seed,
        "per_claim": stability,
    }


def pillar236_critique_hardening_report(samples: int = 200, seed: int = 236) -> dict[str, Any]:
    """Integrated report for Pillar 236."""
    ladder = source_quality_ladder()
    ledger = critique_hardening_ledger()
    summary = ledger_summary(ledger)
    prereg = preregistered_falsification_table()
    stability = monte_carlo_critique_stability(samples=samples, seed=seed)

    return {
        "pillar": 236,
        "status": __provenance__["status"],
        "source_quality_ladder": ladder,
        "external_validation_ledger": ledger,
        "ledger_summary": summary,
        "preregistered_falsifiers": prereg,
        "stability_simulation": stability,
        "falsification_condition": (
            "This hardening layer fails if it hides critique, weakens preregistered "
            "kill criteria after data release, or collapses source-tier discipline."
        ),
    }


__all__ = [
    "N_W",
    "K_CS",
    "C_S",
    "NS_UM",
    "R_UM_BRAIDED",
    "BETA_UM_PRIMARY_DEG",
    "BETA_UM_SHADOW_DEG",
    "P236_W0_UM",
    "P236_WA_UM",
    "ExternalConstraint",
    "__provenance__",
    "source_quality_ladder",
    "default_external_constraints",
    "default_predictions",
    "evaluate_against_constraint",
    "preregistered_falsification_table",
    "critique_hardening_ledger",
    "ledger_summary",
    "monte_carlo_critique_stability",
    "pillar236_critique_hardening_report",
]
