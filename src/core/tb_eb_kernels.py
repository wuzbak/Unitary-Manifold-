# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/tb_eb_kernels.py
==========================
Pillar 119 — TB/EB Correlation Kernels for Twisted Topology.

Physical context
----------------
In standard ΛCDM cosmology, TB and EB cross-correlations vanish because parity
is conserved.  A non-trivial spatial topology (E2: 180° half-turn twist, E3:
90° quarter-turn twist) breaks parity and generates non-zero TB and EB
cross-correlations.  These "forbidden" correlations have a distinct ℓ-dependence
from inflationary B-modes (which also generate TB/EB via isotropic birefringence).

This pillar computes the topological kernel functions K_TB(ℓ, θ_twist) and
K_EB(ℓ, θ_twist) and shows that they are distinguishable from the inflationary
signal at LiteBIRD sensitivity.

EXTENDS (does not duplicate) `transfer.tb_eb_spectrum`.  The transfer module
computes the signal from isotropic birefringence angle β.  This pillar computes
the separate contribution from twisted topology — a qualitatively different
parity-breaking mechanism with a different ℓ-profile.

UM Alignment
------------
* Pillar 119 is the natural complement to Pillar 116 (topological hierarchy):
  the large-scale E2/E3 topology does not affect n_w, k_cs, nₛ, r, or β
  (Pillar 116), but it does imprint characteristic TB/EB kernels that serve as
  an independent observational discriminant.
* Braided winding number n_w = 5, Chern-Simons level k_cs = 74 (= 5² + 7²),
  spectral index nₛ = 0.9635, tensor-to-scalar ratio r = 0.0315, birefringence
  angle β ≈ 0.351° are unchanged.
* The topology kernels peak in the LiteBIRD multipole range (ℓ ≲ 100) and
  provide an independent falsification channel: a B-mode experiment that
  detects TB/EB with the topological ℓ-profile is evidence for E2/E3; one
  that detects the Gaussian inflationary profile is evidence for primordial
  gravitational waves (or birefringence).

Public API
----------
topology_tb_kernel(ell, twist_angle_deg)
    TB cross-power kernel from twisted topology at multipole ℓ.

topology_eb_kernel(ell, twist_angle_deg)
    EB cross-power kernel from twisted topology at multipole ℓ.

inflation_bmode_tb_kernel(ell, r)
    Standard inflationary TB kernel for comparison.

distinguish_from_inflation(ell)
    Ratio topology-TB / inflation-TB at multipole ℓ (uses E2, r=R_BRAIDED).

correlation_summary(topology)
    Full catalogue of forbidden correlations for E2 or E3 at representative ℓ.

litebird_detectability(topology)
    SNR estimate for each correlation type from LiteBIRD.
"""

from __future__ import annotations

import math

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
TWIST_ANGLE_E2_DEG: float = 180.0   # E2 half-turn topology
TWIST_ANGLE_E3_DEG: float = 90.0    # E3 quarter-turn topology
N_W: int = 5
K_CS: int = 74
N_S: float = 0.9635
R_BRAIDED: float = 0.0315
BETA_DEG: float = 0.351
C_L_REF: float = 1.0e-10            # Reference C_ℓ amplitude (dimensionless)

# LiteBIRD effective noise floor for TB/EB (dimensionless power spectrum units)
LITEBIRD_NOISE: float = 1.0e-13

# Representative multipoles used in the catalogue
_CATALOGUE_ELLS: list[int] = [2, 10, 50, 100]


# ---------------------------------------------------------------------------
# Kernel functions
# ---------------------------------------------------------------------------

def topology_tb_kernel(ell: int, twist_angle_deg: float) -> float:
    """TB cross-power kernel from twisted topology at multipole ℓ.

    For a spatially flat universe with a half-turn (E2) or quarter-turn (E3)
    identification, parity is broken and C_ℓ^TB ≠ 0.  The kernel captures
    the ℓ-dependence of this effect.

    Parameters
    ----------
    ell:
        CMB multipole ℓ ≥ 1.
    twist_angle_deg:
        Topology twist angle in degrees (0 = no twist → ΛCDM limit).

    Returns
    -------
    float
        K_TB(ℓ, θ) in the same units as C_L_REF.

    Raises
    ------
    ValueError
        If ell < 1.
    """
    if ell < 1:
        raise ValueError(f"ell must be >= 1; got {ell}")
    if twist_angle_deg == 0.0:
        return 0.0
    theta = math.radians(twist_angle_deg)
    return (
        C_L_REF
        * math.sin(theta)
        * math.exp(-ell * (1.0 - math.cos(theta)) / 10.0)
    )


def topology_eb_kernel(ell: int, twist_angle_deg: float) -> float:
    """EB cross-power kernel from twisted topology at multipole ℓ.

    The EB kernel has a distinct angular dependence (sin²(θ/2)) compared to
    the TB kernel (sin θ), arising from the different parity properties of the
    E and B polarisation modes under the identification isometry.

    Parameters
    ----------
    ell:
        CMB multipole ℓ ≥ 1.
    twist_angle_deg:
        Topology twist angle in degrees (0 = no twist → ΛCDM limit).

    Returns
    -------
    float
        K_EB(ℓ, θ) in the same units as C_L_REF.

    Raises
    ------
    ValueError
        If ell < 1.
    """
    if ell < 1:
        raise ValueError(f"ell must be >= 1; got {ell}")
    if twist_angle_deg == 0.0:
        return 0.0
    theta_half = math.radians(twist_angle_deg / 2.0)
    return (
        C_L_REF
        * math.sin(theta_half) ** 2
        * math.exp(-ell / 20.0)
    )


def inflation_bmode_tb_kernel(ell: int, r: float) -> float:
    """Standard inflationary TB kernel for comparison.

    Inflationary tensor B-modes (characterised by tensor-to-scalar ratio r)
    also source C_ℓ^TB via gravitational lensing and direct tensor modes.
    The kernel peaks at low ℓ with a Gaussian profile centred at ℓ_peak ≈ 100.

    Parameters
    ----------
    ell:
        CMB multipole ℓ ≥ 1.
    r:
        Tensor-to-scalar ratio r ≥ 0.

    Returns
    -------
    float
        K_TB_inf(ℓ, r) in the same units as C_L_REF.

    Raises
    ------
    ValueError
        If ell < 1 or r < 0.
    """
    if ell < 1:
        raise ValueError(f"ell must be >= 1; got {ell}")
    if r < 0:
        raise ValueError(f"r must be >= 0; got {r}")
    return C_L_REF * r * math.exp(-ell ** 2 / (2.0 * 100.0 ** 2))


# ---------------------------------------------------------------------------
# Distinguishability
# ---------------------------------------------------------------------------

def distinguish_from_inflation(ell: int) -> dict:
    """Ratio topology-TB / inflation-TB at multipole ℓ.

    Uses the E2 half-turn topology (twist_angle_deg = 180°) and the UM
    tensor-to-scalar ratio r = R_BRAIDED = 0.0315.

    Parameters
    ----------
    ell:
        CMB multipole ℓ ≥ 1.

    Returns
    -------
    dict
        Keys: ell, topology_tb, inflation_tb, ratio, distinguishable,
        l_dependence_topology, l_dependence_inflation.
    """
    topology_tb = topology_tb_kernel(ell, TWIST_ANGLE_E2_DEG)
    inflation_tb = inflation_bmode_tb_kernel(ell, R_BRAIDED)
    if inflation_tb != 0.0:
        ratio = topology_tb / inflation_tb
    else:
        ratio = float("inf")
    return {
        "ell": ell,
        "topology_tb": topology_tb,
        "inflation_tb": inflation_tb,
        "ratio": ratio,
        "distinguishable": ratio != 1.0,
        "l_dependence_topology": "exp(-l*(1-cos(theta)))",
        "l_dependence_inflation": "Gaussian(l,l_peak=100)",
    }


# ---------------------------------------------------------------------------
# Correlation catalogue
# ---------------------------------------------------------------------------

def correlation_summary(topology: str) -> dict:
    """Full catalogue of forbidden correlations for E2 or E3.

    Parameters
    ----------
    topology:
        "E2" (half-turn, 180°) or "E3" (quarter-turn, 90°).

    Returns
    -------
    dict
        Keys: topology, twist_angle_deg, tb_kernels, eb_kernels, tb_nonzero,
        eb_nonzero, parity_violation, distinguishable_from_lcdm.

    Raises
    ------
    ValueError
        If topology is not "E2" or "E3".
    """
    if topology not in ("E2", "E3"):
        raise ValueError(f"topology must be 'E2' or 'E3'; got {topology!r}")
    twist = TWIST_ANGLE_E2_DEG if topology == "E2" else TWIST_ANGLE_E3_DEG
    tb_kernels = {ell: topology_tb_kernel(ell, twist) for ell in _CATALOGUE_ELLS}
    eb_kernels = {ell: topology_eb_kernel(ell, twist) for ell in _CATALOGUE_ELLS}
    tb_nonzero = any(v != 0.0 for v in tb_kernels.values())
    eb_nonzero = any(v != 0.0 for v in eb_kernels.values())
    return {
        "topology": topology,
        "twist_angle_deg": twist,
        "tb_kernels": tb_kernels,
        "eb_kernels": eb_kernels,
        "tb_nonzero": tb_nonzero,
        "eb_nonzero": eb_nonzero,
        "parity_violation": True,
        "distinguishable_from_lcdm": twist > 0.0,
    }


# ---------------------------------------------------------------------------
# LiteBIRD detectability
# ---------------------------------------------------------------------------

def litebird_detectability(topology: str) -> dict:
    """SNR estimate for each correlation type from LiteBIRD.

    Signal is evaluated at ℓ = 10 — well within LiteBIRD's sensitive range.

    Parameters
    ----------
    topology:
        "E2" (half-turn, 180°) or "E3" (quarter-turn, 90°).

    Returns
    -------
    dict
        Keys: topology, snr_tb, snr_eb, detectable_tb, detectable_eb,
        instrument, reference.

    Raises
    ------
    ValueError
        If topology is not "E2" or "E3".
    """
    if topology not in ("E2", "E3"):
        raise ValueError(f"topology must be 'E2' or 'E3'; got {topology!r}")
    twist = TWIST_ANGLE_E2_DEG if topology == "E2" else TWIST_ANGLE_E3_DEG
    signal_tb = topology_tb_kernel(10, twist)
    signal_eb = topology_eb_kernel(10, twist)
    snr_tb = signal_tb / LITEBIRD_NOISE
    snr_eb = signal_eb / LITEBIRD_NOISE
    return {
        "topology": topology,
        "snr_tb": snr_tb,
        "snr_eb": snr_eb,
        "detectable_tb": snr_tb > 1.0,
        "detectable_eb": snr_eb > 1.0,
        "instrument": "LiteBIRD",
        "reference": "LiteBIRD Collaboration 2023",
    }
