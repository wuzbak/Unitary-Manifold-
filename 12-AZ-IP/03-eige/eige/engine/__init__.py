# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Engine helpers for EIGE upgrades."""

from .open_election_data import (
    OPEN_ELECTIONS_BASE,
    HARVARD_DATAVERSE_BASE,
    ANOMALY_DETECTORS,
    fetch_election_results,
    compute_integrity_score,
    detect_anomaly,
)
from .hils_audit_trail import AuditEntry, create_audit_entry, format_audit_log

__all__ = [
    "OPEN_ELECTIONS_BASE",
    "HARVARD_DATAVERSE_BASE",
    "ANOMALY_DETECTORS",
    "fetch_election_results",
    "compute_integrity_score",
    "detect_anomaly",
    "AuditEntry",
    "create_audit_entry",
    "format_audit_log",
]
