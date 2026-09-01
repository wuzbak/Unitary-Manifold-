# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Engine exports for the Falsification Observatory."""

from .desi_tracker import DESI_DR3_PREREGISTRATION, check_desi_tension, get_falsification_status
from .litebird_countdown import (
    BIREFRINGENCE_PREDICTION,
    LITEBIRD_LAUNCH_YEAR,
    assess_birefringence_measurement,
    days_to_litebird,
)
from .routing import (
    api_desi,
    api_litebird,
    dispatch_api_request,
    route_act,
    route_all,
    route_desi,
    route_hllhc,
    route_juno,
    route_litebird,
    route_nedm,
    route_xenon,
)
from .verdict import VerdictResult

__all__ = [
    'VerdictResult',
    'DESI_DR3_PREREGISTRATION',
    'BIREFRINGENCE_PREDICTION',
    'LITEBIRD_LAUNCH_YEAR',
    'check_desi_tension',
    'get_falsification_status',
    'days_to_litebird',
    'assess_birefringence_measurement',
    'api_litebird',
    'api_desi',
    'dispatch_api_request',
    'route_litebird',
    'route_desi',
    'route_juno',
    'route_act',
    'route_hllhc',
    'route_nedm',
    'route_xenon',
    'route_all',
]
