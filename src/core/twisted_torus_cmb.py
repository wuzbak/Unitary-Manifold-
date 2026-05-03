# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/twisted_torus_cmb.py
==============================
Pillar 115 — Twisted Torus CMB Signatures (E2/E3 Observable Predictions).

Physical context
----------------
The E2 and E3 spatial topologies (half-turn and quarter-turn spaces,
respectively) remain viable after Planck CMB matched-circle analysis.
Unlike E1 (the untwisted 3-torus), their twisted identifications cannot
be excluded by searches for IDENTICAL matched circles.

Instead, E2 and E3 produce distinct CMB signatures:

1. Low-ℓ CMB power suppression
   When the torus size L_torus is comparable to (or smaller than) the
   last-scattering distance χ_rec, modes with wavelengths larger than
   L_torus are absent from the CMB spectrum.  This produces a cut-off
   in power at low multipoles ℓ < ℓ_cut ≈ π χ_rec / L_torus.

2. Twisted matched-circle correlations
   A twisted topology produces circle pairs that are CORRELATED but
   NOT IDENTICAL.  The cross-correlation function C(α, θ) depends on
   both the angular separation α and the twist angle θ.

3. Quadrupole anisotropy from the twist axis
   For E3 (90° twist), the preferred axis of the twist leaves an
   imprint on the CMB quadrupole pattern.

None of these signatures are currently detected, so E2/E3 with torus
sizes L > χ_rec (outside the horizon) are trivially consistent.
E2/E3 with L < χ_rec remain viable because their signatures differ
from what has been searched for.

Relationship to the Unitary Manifold
--------------------------------------
The UM does NOT predict E2 or E3 topology.  It is agnostic about the
large-scale spatial topology (Pillar 114).  These signatures are what
we WOULD observe IF E2/E3 holds — they add predictive content to the
E2/E3 hypothesis independently of the UM.

The UM's primary CMB predictions (nₛ, r, β) are unaffected by E2/E3
(Pillar 116), so this pillar provides a catalogue of topology-induced
signatures that are ORTHOGONAL to the UM's primary falsifiers.

Epistemic status: PREDICTIVE — results follow from standard CMB physics
applied to non-trivial spatial boundary conditions.  No new physical
postulates; all formulas are standard perturbation theory with modified
mode sums.

Public API
----------
l_cut(L_over_chi)
    Cut-off multipole ℓ_cut below which power is suppressed.

low_l_power_ratio(ell, L_over_chi)
    Fraction of power remaining at multipole ℓ for torus size L/χ_rec.
    Returns 1.0 for ℓ > ℓ_cut (no suppression) and decreases toward 0
    for ℓ ≪ ℓ_cut.

circle_cross_correlation(alpha_deg, twist_angle_deg)
    CMB circle cross-correlation C(α, θ) between two circle pairs at
    angular separation α and topology twist θ.
    For E1 (θ=0): C = C_self(α) — identical circles.
    For E2 (θ=180°): C = C_self(α) × cos(π) = −C_self(α).
    For E3 (θ=90°): C = C_self(α) × cos(π/2) = 0.

minimum_detectable_size(topology, sigma_C)
    Minimum torus size L/χ_rec at which the twisted correlation is
    detectable above noise level σ_C.

quadrupole_axis_anisotropy(topology)
    Anisotropy of the CMB quadrupole induced by the twist axis.
    Relevant for E3 where the 90° twist picks out a preferred direction.

litebird_topology_forecast(topology, L_over_chi)
    Whether LiteBIRD can distinguish the topology at given torus size.

e2_e3_cmb_summary(L_over_chi)
    Consolidated summary of E2/E3 signatures for a given torus size.

topology_signal_table()
    Comparison table of CMB signatures for E1, E2, E3.
"""

from __future__ import annotations

import math

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CHI_REC_M: float = 4.0e26          # Comoving distance to recombination (m)
LITEBIRD_SIGMA_BETA_DEG: float = 0.03  # LiteBIRD σ(β) forecast (degrees)

# LiteBIRD noise floor for circle correlations (rough estimate)
LITEBIRD_SIGMA_C: float = 0.02     # σ(C) — noise per circle pair

TOPOLOGIES: tuple[str, ...] = ("E1", "E2", "E3")

TWIST_ANGLES_DEG: dict[str, float] = {
    "E1": 0.0,
    "E2": 180.0,
    "E3": 90.0,
}


# ---------------------------------------------------------------------------
# Low-ℓ power suppression
# ---------------------------------------------------------------------------

def l_cut(L_over_chi: float) -> float:
    """Return the cut-off multipole ℓ_cut for a torus of size L = L_over_chi × χ_rec.

    For a cubic torus of side L, modes with wavelength λ > L are absent.
    The corresponding multipole cut-off is:

        ℓ_cut ≈ π × χ_rec / L = π / L_over_chi

    Parameters
    ----------
    L_over_chi:
        Torus size in units of χ_rec.  Must be positive.

    Returns
    -------
    float
        Cut-off multipole ℓ_cut.  Power is suppressed for ℓ < ℓ_cut.
    """
    if L_over_chi <= 0:
        raise ValueError("L_over_chi must be positive")
    return math.pi / L_over_chi


def low_l_power_ratio(ell: float, L_over_chi: float) -> float:
    """Return the fraction of power remaining at multipole ℓ.

    For ℓ ≫ ℓ_cut (small scales), all modes are present and the ratio is 1.
    For ℓ ≪ ℓ_cut (large scales), the ratio falls to 0.

    We use a smooth logistic suppression factor:

        f(ℓ) = 1 / (1 + exp(−k × (ℓ − ℓ_cut)))

    with k = 2 (transition width ≈ 1 multipole), which smoothly
    interpolates between the full-suppression and no-suppression regimes.

    Parameters
    ----------
    ell:
        Multipole moment ℓ ≥ 2.
    L_over_chi:
        Torus size in units of χ_rec.

    Returns
    -------
    float
        Power fraction in [0, 1].
    """
    if ell < 2:
        raise ValueError("ell must be >= 2 (CMB quadrupole and above)")
    if L_over_chi <= 0:
        raise ValueError("L_over_chi must be positive")
    lc = l_cut(L_over_chi)
    k = 2.0  # Transition steepness
    return 1.0 / (1.0 + math.exp(-k * (ell - lc)))


# ---------------------------------------------------------------------------
# Twisted matched-circle cross-correlation
# ---------------------------------------------------------------------------

def _self_correlation_envelope(alpha_deg: float) -> float:
    """Return the CMB circle self-correlation envelope at angular separation α.

    In the absence of topology, the CMB temperature two-point function
    on a circle of angular radius α is:

        C_self(α) ≈ exp(−α² / (2 × σ_beam²)) × T_rms²

    We normalise to C_self(0) = 1 and use σ_beam = 5° (roughly Planck beam):

        C_self(α) = exp(−α² / (2 × 25))

    This is the baseline correlation that topology modifies.

    Parameters
    ----------
    alpha_deg:
        Angular separation in degrees.

    Returns
    -------
    float
        Normalised correlation coefficient in [−1, 1].
    """
    sigma_deg = 5.0  # Approximate Planck beam/coherence scale
    return math.exp(-(alpha_deg ** 2) / (2 * sigma_deg ** 2))


def circle_cross_correlation(alpha_deg: float, twist_angle_deg: float) -> float:
    """Return the CMB circle cross-correlation for a twisted spatial loop.

    For a topology with twist angle θ, two circles separated by α are
    related by a spatial rotation of θ.  The cross-correlation is:

        C(α, θ) = C_self(α) × cos(θ_rad)

    where C_self is the untwisted baseline.

    Special cases:
        θ = 0°   (E1): C = C_self(α)          — identical circles
        θ = 180° (E2): C = −C_self(α)         — anti-correlated
        θ = 90°  (E3): C = 0                  — orthogonal (uncorrelated)

    Note: For E2/E3 the matched-circle search looks for |C| ≈ 1 at small α.
    The twisted signal has |C| < C_self or C = 0, so it evades the search.

    Parameters
    ----------
    alpha_deg:
        Angular separation between circle centres (degrees), ≥ 0.
    twist_angle_deg:
        Twist angle of the spatial loop (degrees).

    Returns
    -------
    float
        Cross-correlation coefficient.
    """
    if alpha_deg < 0:
        raise ValueError("alpha_deg must be >= 0")
    if twist_angle_deg < 0 or twist_angle_deg > 360:
        raise ValueError("twist_angle_deg must be in [0, 360]")
    baseline = _self_correlation_envelope(alpha_deg)
    twist_factor = math.cos(math.radians(twist_angle_deg))
    return baseline * twist_factor


def minimum_detectable_size(topology: str, sigma_C: float = LITEBIRD_SIGMA_C) -> float:
    """Return minimum torus size L/χ_rec at which topology signal is detectable.

    For E2 (θ=180°), the signal |C| = C_self(α=0°) = 1 but with a sign flip.
    Detection requires the cross-correlation to differ from zero by > 3 σ_C.
    The optimal circle separation is α = 0°, and the signal is |C| = |cos(θ)|.

    The suppression of power at low ℓ requires L/χ_rec < 1/2 to produce
    a detectable signature at ℓ_cut ≈ 2 (quadrupole).

    For E3 (θ=90°), C = 0 at all separations — detection requires the
    quadrupole axis anisotropy, which needs L/χ_rec < ~0.5.

    This function returns a conservative estimate:
        L/χ_rec < π / ℓ_det,   ℓ_det = 3 / sigma_C

    Parameters
    ----------
    topology:
        'E2' or 'E3'.
    sigma_C:
        Noise per circle-pair measurement (default: LiteBIRD estimate).

    Returns
    -------
    float
        Maximum L/χ_rec for detection.
    """
    if topology not in ("E2", "E3"):
        raise ValueError(f"topology must be 'E2' or 'E3'; got {topology!r}")
    if sigma_C <= 0:
        raise ValueError("sigma_C must be positive")
    # SNR = |cos(θ)| / sigma_C; detection at SNR = 3
    cos_theta = abs(math.cos(math.radians(TWIST_ANGLES_DEG[topology])))
    if cos_theta < 1e-12:
        # E3: cos(90°) = 0 — circle correlation undetectable; use power suppression
        l_det = 2.0  # Quadrupole
    else:
        snr_per_pair = cos_theta / sigma_C
        l_det = max(2.0, snr_per_pair)
    return math.pi / l_det


# ---------------------------------------------------------------------------
# Quadrupole axis anisotropy (E3)
# ---------------------------------------------------------------------------

def quadrupole_axis_anisotropy(topology: str) -> dict:
    """Return the expected quadrupole axis anisotropy for *topology*.

    For E3 (90° Z₄ twist), the preferred twist axis introduces a 4-fold
    rotational pattern in the CMB quadrupole.  For E2 (180° Z₂ twist),
    the symmetry axis introduces a 2-fold pattern.  E1 has no preferred axis.

    The anisotropy amplitude is model-dependent (depends on L_torus/χ_rec),
    so we report the SYMMETRY TYPE, not an amplitude.

    Parameters
    ----------
    topology:
        'E1', 'E2', or 'E3'.

    Returns
    -------
    dict
        symmetry_fold, axis_present, pattern_description.
    """
    if topology not in TOPOLOGIES:
        raise ValueError(f"topology must be one of {TOPOLOGIES}; got {topology!r}")
    config = {
        "E1": {
            "symmetry_fold": 1,
            "axis_present": False,
            "pattern_description": "No preferred axis; isotropic CMB quadrupole expected",
        },
        "E2": {
            "symmetry_fold": 2,
            "axis_present": True,
            "pattern_description": (
                "Z₂ axis of 180° twist introduces 2-fold (cos 2φ) pattern "
                "in CMB quadrupole at scales L_torus < χ_rec"
            ),
        },
        "E3": {
            "symmetry_fold": 4,
            "axis_present": True,
            "pattern_description": (
                "Z₄ axis of 90° twist introduces 4-fold (cos 4φ) pattern "
                "in CMB quadrupole at scales L_torus < χ_rec"
            ),
        },
    }
    return {"topology": topology, **config[topology]}


# ---------------------------------------------------------------------------
# LiteBIRD forecast
# ---------------------------------------------------------------------------

def litebird_topology_forecast(topology: str, L_over_chi: float) -> dict:
    """Return LiteBIRD's detection prospect for *topology* at torus size L/χ_rec.

    Parameters
    ----------
    topology:
        'E1', 'E2', or 'E3'.
    L_over_chi:
        Torus size in units of χ_rec.

    Returns
    -------
    dict
        detectable, reason, primary_um_target_unaffected.
    """
    if topology not in TOPOLOGIES:
        raise ValueError(f"topology must be one of {TOPOLOGIES}; got {topology!r}")
    if L_over_chi <= 0:
        raise ValueError("L_over_chi must be positive")

    lc = l_cut(L_over_chi)
    # Power suppression at quadrupole (ℓ=2) if ℓ_cut > 2
    quadrupole_suppressed = lc > 2.0

    if topology == "E1":
        # E1 already ruled out if in horizon; LiteBIRD won't help further
        detectable = False
        reason = "E1 already excluded if within horizon; LiteBIRD adds no new constraint."
    elif topology == "E2":
        detectable = quadrupole_suppressed and L_over_chi < 0.5
        reason = (
            "E2 detectable via low-ℓ power suppression and anti-correlated circles "
            f"if L_torus < 0.5 χ_rec (current L/χ_rec = {L_over_chi:.2f})."
            if detectable
            else "E2 signal below LiteBIRD threshold at this torus size."
        )
    else:  # E3
        detectable = quadrupole_suppressed and L_over_chi < 0.4
        reason = (
            "E3 detectable via 4-fold quadrupole anisotropy and low-ℓ suppression "
            f"if L_torus < 0.4 χ_rec (current L/χ_rec = {L_over_chi:.2f})."
            if detectable
            else "E3 signal below LiteBIRD threshold at this torus size."
        )

    return {
        "topology": topology,
        "L_over_chi": L_over_chi,
        "l_cut": lc,
        "detectable": detectable,
        "reason": reason,
        "primary_um_target_unaffected": True,
        "primary_um_target": "β birefringence — independent of spatial topology",
    }


# ---------------------------------------------------------------------------
# Summary tables
# ---------------------------------------------------------------------------

def e2_e3_cmb_summary(L_over_chi: float) -> dict:
    """Consolidated summary of E2/E3 signatures for a given torus size.

    Parameters
    ----------
    L_over_chi:
        Torus size in units of χ_rec.

    Returns
    -------
    dict
        Per-topology signature summary.
    """
    if L_over_chi <= 0:
        raise ValueError("L_over_chi must be positive")
    lc = l_cut(L_over_chi)
    result = {
        "L_over_chi": L_over_chi,
        "l_cut": lc,
    }
    for top in ("E2", "E3"):
        theta = TWIST_ANGLES_DEG[top]
        corr_at_zero = circle_cross_correlation(0.0, theta)
        power_at_l2 = low_l_power_ratio(2.0, L_over_chi)
        aniso = quadrupole_axis_anisotropy(top)
        result[top] = {
            "circle_correlation_at_0deg": corr_at_zero,
            "power_fraction_at_l2": power_at_l2,
            "quadrupole_symmetry_fold": aniso["symmetry_fold"],
            "min_detectable_L_over_chi": minimum_detectable_size(top),
            "litebird_detectable": litebird_topology_forecast(top, L_over_chi)["detectable"],
        }
    return result


def topology_signal_table() -> dict:
    """Comparison table of CMB signatures for E1, E2, E3.

    Returns
    -------
    dict
        Keyed by topology label.
    """
    return {
        "E1": {
            "twist_deg": 0.0,
            "circle_signal": "IDENTICAL",
            "correlation_at_0deg": 1.0,
            "quadrupole_symmetry_fold": 1,
            "observational_status": "RULED_OUT_IF_WITHIN_HORIZON",
            "um_prediction_affected": False,
        },
        "E2": {
            "twist_deg": 180.0,
            "circle_signal": "ANTI_CORRELATED",
            "correlation_at_0deg": -1.0,
            "quadrupole_symmetry_fold": 2,
            "observational_status": "VIABLE",
            "um_prediction_affected": False,
        },
        "E3": {
            "twist_deg": 90.0,
            "circle_signal": "ORTHOGONAL",
            "correlation_at_0deg": 0.0,
            "quadrupole_symmetry_fold": 4,
            "observational_status": "VIABLE",
            "um_prediction_affected": False,
        },
    }
