# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""φ₀ ground-state calibration helpers for Holon Zero."""

from __future__ import annotations

PHI_0_STATUS = {
    "value": 1.0,
    "closure": "PARTIAL",
    "pillar": "P853",
    "mechanism": "N_flux=1 partial closure",
    "caveat": "Full first-principles derivation remains open",
}

OMEGA_0_SUB_PILLARS = [
    {"id": "70-B", "name": "Observer loop closure", "status": "CONSISTENT"},
    {"id": "70-C", "name": "Co-emergence coupling", "status": "CONSISTENT"},
    {"id": "70-D", "name": "Ground-state audit witness", "status": "PARTIAL"},
]


def calibrate_ground_state(phi0: float = 1.0) -> dict:
    """Return a compact calibration summary around the φ₀ reference point."""
    phi0 = float(phi0)
    deviation = abs(phi0 - PHI_0_STATUS["value"])
    status = "CONSISTENT" if deviation <= 0.05 else "DRIFTED"
    return {
        "phi0": phi0,
        "kk_mass_ratio": round(phi0 / PHI_0_STATUS["value"], 6),
        "radion_vev": round(phi0 * (74 / 35), 6),
        "status": status,
    }


def get_sub_pillar(sub_id: str) -> dict:
    """Return Ω₀ sub-pillar metadata by id."""
    normalised = sub_id.strip().upper()
    for pillar in OMEGA_0_SUB_PILLARS:
        if pillar["id"].upper() == normalised:
            return dict(pillar)
    raise KeyError(f"Unknown Ω₀ sub-pillar: {sub_id}")


def run_ground_state_audit() -> dict:
    """Check Ω₀ consistency against all registered sub-pillars."""
    issues = [
        pillar["id"]
        for pillar in OMEGA_0_SUB_PILLARS
        if pillar["status"] not in {"CONSISTENT", "PARTIAL"}
    ]
    calibration = calibrate_ground_state(PHI_0_STATUS["value"])
    return {
        "omega_0": "Ω₀ Ground State",
        "phi0_status": dict(PHI_0_STATUS),
        "calibration": calibration,
        "sub_pillars": [dict(pillar) for pillar in OMEGA_0_SUB_PILLARS],
        "consistent": not issues and calibration["status"] == "CONSISTENT",
        "issues": issues,
        "n_sub_pillars": len(OMEGA_0_SUB_PILLARS),
    }
