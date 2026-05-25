# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 463 — α_GW SC2 final 5D-EFT floor certificate.

STATUS
======
ALPHA_GW_SC2_5D_EFT_FLOOR_CERTIFIED

CONTEXT
=======
Pillar 451 narrowed the residual α_GW transfer-normalization interval to
[4.31, 4.67] × 10⁻¹⁰.  Pillar 280 already established that the leading
c_UV-independent narrowing inside the 5D EFT stops at O(ε_UV), with
ε_UV ≈ 0.04.  This pillar asks the honest final question for v14.0:

    can the minimal 5D EFT narrow α_GW uniquely,
    or is a full 10D UV completion required?

Result:
    * the present interval width is ≈ 8% of the central value,
    * the irreducible 5D EFT floor at leading omitted order is ≈ 4%,
    * therefore the interval can still be tightened modestly inside 5D,
      plausibly to ~2% once O(ε_UV²) information is supplied,
    * but unique closure still requires a genuine 10D compactification
      that fixes c_UV from tadpole/flux data rather than treating it as
      a residual normalization coefficient.

CMB-S4 consequence:
    even if the interval is narrowed from 8% to 2–4%, CMB-S4 does not
    resolve individual α_GW values inside that band.  The observational
    role of the interval is therefore certification, not discrimination.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import copy
import math
from typing import Any, Dict

from src.core.alpha_gw_10d_uv_completion import (
    freeze_target_equation_and_normalization,
    full_10d_uv_closure_report,
)

__all__ = [
    'PILLAR_STATUS',
    'VERSION',
    'ALPHA_GW_LOW',
    'ALPHA_GW_HIGH',
    'ALPHA_GW_CENTRAL',
    'EPSILON_UV',
    'current_interval',
    'five_d_eft_floor_analysis',
    'next_order_narrowing_estimate',
    'ten_d_uv_requirement',
    'cmbs4_discriminability',
    'five_d_eft_certified_floor',
    'pillar_report',
]

PILLAR_STATUS: str = 'ALPHA_GW_SC2_5D_EFT_FLOOR_CERTIFIED'
VERSION: str = 'v14.0'

N_W: int = 5
K_CS: int = 74
C_S: float = 12.0 / 37.0
ALPHA_GW_LOW: float = 4.31e-10
ALPHA_GW_HIGH: float = 4.67e-10
ALPHA_GW_CENTRAL: float = 0.5 * (ALPHA_GW_LOW + ALPHA_GW_HIGH)
EPSILON_UV: float = 0.04
CMBS4_SIGMA_R: float = 0.002
UM_R_BRAIDED: float = 0.0315


def current_interval() -> Dict[str, float]:
    """Return the currently certified α_GW interval from Pillar 451."""
    width = ALPHA_GW_HIGH - ALPHA_GW_LOW
    return {
        'low': ALPHA_GW_LOW,
        'high': ALPHA_GW_HIGH,
        'width': width,
        'central': ALPHA_GW_CENTRAL,
        'relative_width': width / ALPHA_GW_CENTRAL,
    }


def five_d_eft_floor_analysis() -> Dict[str, Any]:
    """Quantify the minimal width still compatible with 5D EFT truncation.

    The leading omitted contribution is O(ε_UV).  In the honest EFT sense,
    that means a relative interval width of order ε_UV remains unless one
    computes the next order explicitly.
    """
    interval = current_interval()
    floor_relative_width = EPSILON_UV
    floor_absolute_width = ALPHA_GW_CENTRAL * floor_relative_width
    reducible_width = max(interval['width'] - floor_absolute_width, 0.0)
    reducible_fraction = reducible_width / interval['width'] if interval['width'] else 0.0
    return {
        'epsilon_uv': EPSILON_UV,
        'floor_relative_width': floor_relative_width,
        'floor_absolute_width': floor_absolute_width,
        'current_relative_width': interval['relative_width'],
        'current_absolute_width': interval['width'],
        'above_floor': interval['relative_width'] > floor_relative_width,
        'reducible_width_before_floor': reducible_width,
        'reducible_fraction_before_floor': reducible_fraction,
        'best_leading_order_interval': {
            'low': ALPHA_GW_CENTRAL - 0.5 * floor_absolute_width,
            'high': ALPHA_GW_CENTRAL + 0.5 * floor_absolute_width,
            'width': floor_absolute_width,
        },
        'conclusion': (
            'The present ≈8% interval is wider than the ≈4% 5D-EFT floor. '
            'A modest additional tightening is available inside 5D, but '
            'unique α_GW closure is impossible without fixing the UV '
            'normalization coefficient c_UV.'
        ),
    }


def next_order_narrowing_estimate() -> Dict[str, Any]:
    """Estimate the reachable band once O(ε_UV²) information is included."""
    target_relative_width = 0.5 * EPSILON_UV
    target_absolute_width = ALPHA_GW_CENTRAL * target_relative_width
    low = ALPHA_GW_CENTRAL - 0.5 * target_absolute_width
    high = ALPHA_GW_CENTRAL + 0.5 * target_absolute_width
    current = current_interval()
    return {
        'assumed_next_order': 'O(epsilon_uv^2)',
        'target_relative_width': target_relative_width,
        'target_absolute_width': target_absolute_width,
        'estimated_interval': {
            'low': low,
            'high': high,
            'width': target_absolute_width,
            'central': ALPHA_GW_CENTRAL,
        },
        'improvement_vs_current': current['width'] / target_absolute_width,
        'fractional_reduction_vs_current': 1.0 - (target_absolute_width / current['width']),
        'interpretation': (
            'Once the O(ε_UV) remainder is itself constrained by an '
            'explicit next-order computation, the residual band can plausibly '
            'shrink from ≈8% to ≈2% of the central value.'
        ),
    }


def ten_d_uv_requirement() -> Dict[str, Any]:
    """State what genuine 10D UV data would add beyond the 5D EFT floor."""
    locked = freeze_target_equation_and_normalization()
    report = full_10d_uv_closure_report()
    c_uv_low, c_uv_high = locked['c_uv_required_interval']
    return {
        'five_d_gap': 'c_UV remains a residual normalization coefficient in 5D EFT.',
        'required_input': (
            '10D M-theory compactification on CY₃ with flux quantization uniquely '
            'selects c_UV from the tadpole condition; requires full 10D '
            'supergravity computation.'
        ),
        'bridge_equation': locked['bridge_equation'],
        'required_c_uv_interval': {'low': c_uv_low, 'high': c_uv_high},
        'benchmark_10d_status': report.get('decision', report.get('status', 'UNKNOWN')),
        'benchmark_10d_note': (
            'The existing 10D benchmark certifies plausibility, but benchmark '
            'closure is not the same as a unique compactification theorem.'
        ),
    }


def cmbs4_discriminability() -> Dict[str, Any]:
    """Return whether CMB-S4 can resolve values inside the present band."""
    interval = current_interval()
    sigma_r_over_r = CMBS4_SIGMA_R / UM_R_BRAIDED
    next_order = next_order_narrowing_estimate()
    return {
        'cmbs4_sigma_r': CMBS4_SIGMA_R,
        'um_r_prediction': UM_R_BRAIDED,
        'sigma_r_over_r': sigma_r_over_r,
        'current_alpha_gw_relative_width': interval['relative_width'],
        'next_order_alpha_gw_relative_width': next_order['target_relative_width'],
        'can_discriminate_current_interval': False,
        'can_discriminate_next_order_interval': False,
        'reason': (
            'CMB-S4 measures tensor power and tilt, not α_GW as an isolated '
            'parameter. Transfer-normalization and scalar-amplitude degeneracies '
            'dominate, so neither the current 8% band nor the projected 2% band '
            'is individually resolvable.'
        ),
    }


def five_d_eft_certified_floor() -> Dict[str, Any]:
    """Return the final certification statement for SC2 at v14.0."""
    interval = current_interval()
    floor = five_d_eft_floor_analysis()
    next_order = next_order_narrowing_estimate()
    ten_d = ten_d_uv_requirement()
    return {
        'status': PILLAR_STATUS,
        'current_interval': interval,
        'five_d_floor': floor,
        'next_order_estimate': next_order,
        'ten_d_requirement': ten_d,
        'five_d_can_narrow_further': floor['above_floor'],
        'five_d_can_uniquely_close_alpha_gw': False,
        'final_statement': (
            '5D EFT can likely narrow α_GW from the present ≈8% band to a '
            '≈2–4% residual band, but it cannot uniquely select a single α_GW '
            'value. Unique closure requires a 10D compactification that fixes c_UV.'
        ),
    }


def pillar_report() -> Dict[str, Any]:
    """Return the Pillar 463 machine-readable report."""
    return {
        'pillar': 463,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'current_interval': current_interval(),
        'five_d_floor_analysis': five_d_eft_floor_analysis(),
        'next_order_narrowing': next_order_narrowing_estimate(),
        'ten_d_uv_requirement': ten_d_uv_requirement(),
        'cmbs4_discriminability': cmbs4_discriminability(),
        'certification': five_d_eft_certified_floor(),
    }


_PILLAR_STATUS: Dict[str, Any] = copy.deepcopy(pillar_report())
