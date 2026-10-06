# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Runtime mode configuration for EIGE.

EIGE distinguishes two runtime modes, read from the ``EIGE_MODE`` environment
variable:

``development`` (default)
    Development-only key providers, mock HSMs and mock attestation may be used,
    but every artifact they produce is labelled as development material.

``production``
    Any component that is development-only refuses to run and raises
    :class:`ProductionModeViolation`.  Real keys must come from an HSM.
"""

from __future__ import annotations

import os

MODE_ENV_VAR = "EIGE_MODE"
DEVELOPMENT = "development"
PRODUCTION = "production"
_VALID_MODES = (DEVELOPMENT, PRODUCTION)


class ProductionModeViolation(RuntimeError):
    """Raised when a development-only component is used in production mode."""


def runtime_mode() -> str:
    """Return the current runtime mode (``development`` or ``production``).

    Unknown values are treated as ``production`` so that a typo can never
    silently enable development-only behaviour.
    """
    value = os.environ.get(MODE_ENV_VAR, DEVELOPMENT).strip().lower()
    return value if value in _VALID_MODES else PRODUCTION


def is_production() -> bool:
    return runtime_mode() == PRODUCTION


def require_non_production(component: str) -> None:
    """Raise if ``component`` (a development-only facility) is used in production."""
    if is_production():
        raise ProductionModeViolation(
            f"{component} is development-only and refuses to run when "
            f"{MODE_ENV_VAR}={PRODUCTION}. Use an HSM-backed provider."
        )
