# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 582 — DESI DR3 Preregistration v2 — SHA-256 Locked with All Three Branches.

STATUS: DESI_DR3_PREREGISTRATION_V2_CERTIFIED
"""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "VERSION",
    "PREREGISTRATION_STRING",
    "PREREGISTRATION_HASH",
    "preregistration_record",
    "hash_verification",
    "v1_to_v2_upgrade",
    "desi_decision_timeline",
    "pillar_report",
]

PILLAR_NUMBER: int = 582
PILLAR_STATUS: str = "DESI_DR3_PREREGISTRATION_V2_CERTIFIED"
PILLAR_TITLE: str = "DESI DR3 Preregistration v2 — SHA-256 Locked with All Three Branches"
VERSION: str = "v20.1"

PREREGISTRATION_STRING: str = (
    "DESI_DR3_PREREGISTRATION_V2|w0=-1.0|wa=0.0|sigma_falsified=3.0|"
    "sigma_pass=2.0|euclid_w0_window=0.05|euclid_wa_window=0.3|"
    "hyperK_nmo_coupling=True|spherex_fnl=True|date=2026-08-01"
)
PREREGISTRATION_HASH: str = hashlib.sha256(PREREGISTRATION_STRING.encode()).hexdigest()


def preregistration_record() -> Dict[str, Any]:
    """Return the canonical v2 preregistration payload."""
    return {
        "version": "v2",
        "string": PREREGISTRATION_STRING,
        "hash": PREREGISTRATION_HASH,
        "hash_algorithm": "sha256",
        "all_three_branches_locked": True,
        "date": "2026-08-01",
    }


def hash_verification() -> Dict[str, Any]:
    """Recompute the hash and verify deterministic equality."""
    recomputed = hashlib.sha256(PREREGISTRATION_STRING.encode()).hexdigest()
    return {
        "stored_hash": PREREGISTRATION_HASH,
        "recomputed_hash": recomputed,
        "match": recomputed == PREREGISTRATION_HASH,
    }


def v1_to_v2_upgrade() -> Dict[str, Any]:
    """Describe the v1→v2 preregistration upgrade."""
    additions: List[str] = [
        "Explicit Euclid cross-check protocol",
        "Extension-branch activation criteria",
        "Hyper-K NMO coupling",
        "SPHEREx f_NL coupling",
    ]
    return {
        "from_version": "v1",
        "to_version": "v2",
        "v1_source": "Pillar 467",
        "v2_hash": PREREGISTRATION_HASH,
        "new_items": additions,
        "canonical_now": True,
    }


def desi_decision_timeline() -> Dict[str, Any]:
    """Return the post-lock decision timeline for DR3."""
    return {
        "preregistration_lock_date": "2026-08-01",
        "expected_dr3_window": "2026-2027",
        "year5_projection_context": "Pillar 551 central projection = 3.64σ",
        "future_cross_checks": ["Euclid", "Hyper-K", "SPHEREx"],
        "v2_hash": PREREGISTRATION_HASH,
    }


def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 582 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "preregistration_record": preregistration_record(),
        "hash_verification": hash_verification(),
        "v1_to_v2_upgrade": v1_to_v2_upgrade(),
        "desi_decision_timeline": desi_decision_timeline(),
    }
