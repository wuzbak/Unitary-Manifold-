# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""DESI DR3 preregistration tracking helpers for the Falsification Observatory."""

from __future__ import annotations

from dataclasses import asdict
from math import sqrt

DESI_DR3_PREREGISTRATION = {
    "preregistration_date": "2026-08-29",
    "w0_prediction": -1.0,
    "wa_prediction": 0.0,
    "pillar": "P824",
    "status": "PREREGISTERED",
}

_REFERENCE_SIGMA = 0.1


def check_desi_tension(w0_observed: float, wa_observed: float) -> dict:
    """Return a simple sigma-style tension summary for the P824 preregistration."""
    delta_w0 = float(w0_observed) - DESI_DR3_PREREGISTRATION["w0_prediction"]
    delta_wa = float(wa_observed) - DESI_DR3_PREREGISTRATION["wa_prediction"]
    tension_sigma = sqrt(delta_w0 ** 2 + delta_wa ** 2) / _REFERENCE_SIGMA
    consistent = tension_sigma < 3.0
    if tension_sigma < 1.5:
        verdict = "Consistent with the P824 DESI DR3 preregistration."
    elif tension_sigma < 3.0:
        verdict = "In mild tension with the P824 DESI DR3 preregistration."
    else:
        verdict = "In strong tension with the P824 DESI DR3 preregistration."
    return {
        "tension_sigma": tension_sigma,
        "consistent": consistent,
        "verdict": verdict,
        "delta_w0": delta_w0,
        "delta_wa": delta_wa,
    }


def get_falsification_status() -> dict:
    """Return the observatory registry split into open and closed claims."""
    from .routing import route_all

    claims = [asdict(result) for result in route_all({})]
    open_claims = [claim for claim in claims if claim["verdict"] == "AWAITING_DATA"]
    closed_claims = [claim for claim in claims if claim["verdict"] != "AWAITING_DATA"]
    return {
        "desi_dr3_preregistration": dict(DESI_DR3_PREREGISTRATION),
        "open_claims": open_claims,
        "closed_claims": closed_claims,
        "open_count": len(open_claims),
        "closed_count": len(closed_claims),
        "total_claims": len(claims),
    }
