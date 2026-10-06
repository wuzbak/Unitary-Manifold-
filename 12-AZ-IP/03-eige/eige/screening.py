# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Statistical anomaly screens that produce *investigation leads*, never evidence.

Unusual turnout or residual-vote rates have many innocent causes: ballot
design, a local referendum, demographic differences, a polling place moved,
a data-entry error.  A flagged unit means "a person should look at this";
it is never a finding of fraud and must not be reported as one.

Screens use a robust z-score (median / MAD, Iglewicz & Hoaglin 1993) with the
conventional 3.5 threshold, so a few extreme units cannot mask each other.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from typing import List, Mapping, Sequence

EVIDENTIARY_STATUS = "investigation_lead_not_evidence"
DISCLAIMER = (
    "This is a statistical screening lead, not evidence of fraud or error. "
    "Flagged units commonly have legitimate explanations and require human review."
)
ROBUST_Z_THRESHOLD = 3.5


@dataclass(frozen=True)
class Lead:
    unit_id: str
    screen: str
    value: float
    robust_z: float
    explanation: str

    def as_dict(self) -> dict:
        return {
            "unit_id": self.unit_id,
            "screen": self.screen,
            "value": round(self.value, 6),
            "robust_z": round(self.robust_z, 3),
            "explanation": self.explanation,
            "evidentiary_status": EVIDENTIARY_STATUS,
            "disclaimer": DISCLAIMER,
        }


def robust_z(values: Sequence[float]) -> List[float]:
    if len(values) < 3:
        return [0.0] * len(values)
    med = statistics.median(values)
    mad = statistics.median([abs(v - med) for v in values])
    if mad == 0:
        return [0.0] * len(values)
    return [0.6745 * (v - med) / mad for v in values]


def _screen(units: Sequence[Mapping], rate_fn, name: str, describe) -> List[Lead]:
    rates = [rate_fn(u) for u in units]
    leads = []
    for u, r, z in zip(units, rates, robust_z(rates)):
        if abs(z) > ROBUST_Z_THRESHOLD:
            leads.append(Lead(str(u["id"]), name, r, z, describe(r, z)))
    return leads


def turnout_outliers(units: Sequence[Mapping]) -> List[Lead]:
    """Units need ``id``, ``registered`` (>0) and ``ballots``."""
    for u in units:
        if int(u["registered"]) <= 0 or int(u["ballots"]) < 0:
            raise ValueError(f"unit {u.get('id')}: registered must be > 0 and ballots >= 0")
    return _screen(
        units,
        lambda u: int(u["ballots"]) / int(u["registered"]),
        "turnout_outlier",
        lambda r, z: f"Turnout {r:.1%} is unusual relative to peer units (robust z = {z:.1f}).",
    )


def residual_vote_outliers(units: Sequence[Mapping]) -> List[Lead]:
    """Residual vote rate (ballots without a valid vote in a vote-for-1 contest).

    Units need ``id``, ``ballots`` (>0) and ``valid_votes``.
    """
    for u in units:
        if int(u["ballots"]) <= 0 or not 0 <= int(u["valid_votes"]) <= int(u["ballots"]):
            raise ValueError(f"unit {u.get('id')}: need ballots > 0 and 0 <= valid_votes <= ballots")
    return _screen(
        units,
        lambda u: 1 - int(u["valid_votes"]) / int(u["ballots"]),
        "residual_vote_outlier",
        lambda r, z: f"Residual vote rate {r:.1%} is unusual relative to peer units (robust z = {z:.1f}); "
        "common causes include ballot design and scanner thresholds.",
    )
