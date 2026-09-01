# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
12-AZ-IP/lib/open_science — Shared open-science data integration layer.

Provides unified access to:
- Planck/BICEP CMB data references
- DESI DR3 preregistration tracking
- LiteBIRD falsification countdown
- NASA FIRMS fire data
- NOAA space weather
- arXiv preprint feed helpers

All network calls have offline fallbacks — never raise on network failure.

Theory: ThomasCory Walker-Pearson (2026)
Code: GitHub Copilot (AI)
"""
from .litebird import assess_birefringence_measurement, days_to_litebird, LITEBIRD_LAUNCH_YEAR, BIREFRINGENCE_PREDICTION
from .desi import check_desi_tension, get_falsification_status, DESI_DR3_PREREGISTRATION
from .arxiv import fetch_recent_kk_preprints
from .planck import get_planck_cmb_reference, PLANCK_N_S, PLANCK_R_UPPER

__all__ = [
    "assess_birefringence_measurement",
    "days_to_litebird",
    "LITEBIRD_LAUNCH_YEAR",
    "BIREFRINGENCE_PREDICTION",
    "check_desi_tension",
    "get_falsification_status",
    "DESI_DR3_PREREGISTRATION",
    "fetch_recent_kk_preprints",
    "get_planck_cmb_reference",
    "PLANCK_N_S",
    "PLANCK_R_UPPER",
]
