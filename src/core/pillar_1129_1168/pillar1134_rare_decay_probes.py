# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1134 — generic evidentiary tools for rare-decay measurements.

🔵 ADJACENT TRACK — NOT A HARDGATE PHYSICS CLAIM

The November 2026 LHCb B0→μ+μ− result is reported as evidence: 3.0σ in
Run 3 and 3.2σ combined with Runs 1 and 2. These values are provenance
examples, not model predictions. The 3σ evidence and 5σ observation
conventions are labels for statistical communication, not physical laws.

This module deliberately does not encode a Unitary Manifold prediction.
A quantitative UM comparison requires an explicit spectrum, couplings,
effective-operator matching and uncertainties, none of which is supplied here.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from numbers import Real

__all__ = [
    "ADJACENT_TRACK_LABEL",
    "PILLAR_NUMBER",
    "PILLAR_TITLE",
    "EVIDENCE_THRESHOLD_SIGMA",
    "OBSERVATION_THRESHOLD_SIGMA",
    "LHCB_RUN3_BD_TO_MUMU_SIGMA",
    "LHCB_COMBINED_BD_TO_MUMU_SIGMA",
    "LHCB_PAPER_URL",
    "LHCB_OUTREACH_URL",
    "CERN_PRESS_URL",
    "ZEPTOVERSE_PRESS_URL",
    "SignificanceAssessment",
    "PredictionComparison",
    "classify_significance",
    "compare_prediction_to_measurement",
]

ADJACENT_TRACK_LABEL = "🔵 ADJACENT TRACK — NOT A HARDGATE PHYSICS CLAIM"
PILLAR_NUMBER = 1134
PILLAR_TITLE = "Rare B-meson decay probes and statistical evidence"

EVIDENCE_THRESHOLD_SIGMA = 3.0
OBSERVATION_THRESHOLD_SIGMA = 5.0

# Published LHCb significances; not branching-fraction inputs or UM predictions.
LHCB_RUN3_BD_TO_MUMU_SIGMA = 3.0
LHCB_COMBINED_BD_TO_MUMU_SIGMA = 3.2
LHCB_PAPER_URL = "https://arxiv.org/abs/2611.00230"
LHCB_OUTREACH_URL = (
    "https://lhcb-outreach.web.cern.ch/2026/11/03/"
    "evidence-for-the-decay-b0%e2%86%92%ce%bc%ce%bc-and-improved-measurements-of-"
    "bs0%e2%86%92%ce%bc%ce%bc/"
)
CERN_PRESS_URL = (
    "https://home.cern/lhcb-finds-evidence-of-one-in-ten-billion-particle-decay/"
)
ZEPTOVERSE_PRESS_URL = (
    "https://phys.org/news/2026-11-physicists-closer-zeptoverse-year-particle.html"
)


@dataclass(frozen=True)
class SignificanceAssessment:
    """Classification against conventional sigma thresholds."""

    significance_sigma: float
    classification: str
    evidence_threshold_sigma: float
    observation_threshold_sigma: float
    threshold_note: str


@dataclass(frozen=True)
class PredictionComparison:
    """A generic residual normalized by independent Gaussian uncertainties."""

    prediction: float
    measurement: float
    prediction_uncertainty: float
    measurement_uncertainty: float
    combined_uncertainty: float
    normalized_residual: float
    interpretation_note: str


def _finite_real(name: str, value: Real) -> float:
    """Validate a scalar numeric input and return it as a float."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number")
    try:
        result = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} must be finite") from exc
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def classify_significance(significance_sigma: Real) -> SignificanceAssessment:
    """Classify a nonnegative significance as below evidence, evidence, or observation.

    The inclusive 3σ and 5σ cutoffs are conventional reporting thresholds.
    """
    sigma = _finite_real("significance_sigma", significance_sigma)
    if sigma < 0:
        raise ValueError("significance_sigma must be nonnegative")

    if sigma >= OBSERVATION_THRESHOLD_SIGMA:
        classification = "observation"
    elif sigma >= EVIDENCE_THRESHOLD_SIGMA:
        classification = "evidence"
    else:
        classification = "below_evidence_threshold"

    return SignificanceAssessment(
        significance_sigma=sigma,
        classification=classification,
        evidence_threshold_sigma=EVIDENCE_THRESHOLD_SIGMA,
        observation_threshold_sigma=OBSERVATION_THRESHOLD_SIGMA,
        threshold_note=(
            "3σ evidence and 5σ observation are conventional statistical "
            "reporting thresholds, not physical laws."
        ),
    )


def compare_prediction_to_measurement(
    prediction: Real,
    measurement: Real,
    prediction_uncertainty: Real,
    measurement_uncertainty: Real,
) -> PredictionComparison:
    """Compute a generic uncertainty-normalized prediction residual.

    Inputs must use the same units. Independent uncertainties are combined in
    quadrature. This helper does not determine model adequacy and supplies no
    prediction values or uncertainty assumptions.
    """
    pred = _finite_real("prediction", prediction)
    measured = _finite_real("measurement", measurement)
    pred_unc = _finite_real("prediction_uncertainty", prediction_uncertainty)
    meas_unc = _finite_real("measurement_uncertainty", measurement_uncertainty)
    if pred_unc < 0 or meas_unc < 0:
        raise ValueError("uncertainties must be nonnegative")

    combined = math.hypot(pred_unc, meas_unc)
    difference = measured - pred
    if combined == 0:
        residual = 0.0 if difference == 0 else math.inf
    else:
        residual = difference / combined
        if not math.isfinite(residual):
            raise ValueError("comparison exceeds the finite range of this calculation")

    return PredictionComparison(
        prediction=pred,
        measurement=measured,
        prediction_uncertainty=pred_unc,
        measurement_uncertainty=meas_unc,
        combined_uncertainty=combined,
        normalized_residual=residual,
        interpretation_note=(
            "Generic comparison only: no model prediction, covariance model, "
            "or goodness-of-fit threshold is supplied."
        ),
    )
