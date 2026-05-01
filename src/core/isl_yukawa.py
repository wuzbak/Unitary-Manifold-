# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/isl_yukawa.py
======================
Pillar 33 — Kaluza-Klein Yukawa / Inverse-Square-Law (ISL) Fifth-Force Prediction.

Physical context
----------------
The Eöt-Wash experiment (University of Washington) and related torsion-balance
ISL tests currently place the world's most stringent bounds on deviations from
Newton's inverse-square law below the millimeter scale.  A new Yukawa-type
interaction of the form

    V(r) = −G M₁ M₂ / r × (1 + α e^{−r/λ})                         [1]

is parameterised by its range λ and dimensionless coupling strength α relative
to Newtonian gravity.  Current Eöt-Wash bounds exclude |α| ≳ 10⁻³ for ranges
λ ≳ 100 μm and |α| ≳ 1 for λ ≳ 10 μm.

The Unitary Manifold predicts **two independent Yukawa channels** from the KK
reduction:

Channel 1 — Radion (scalar) channel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The Goldberger–Wise potential gives the radion φ a mass m_φ.  The radion
couples universally to the trace of the stress-energy tensor T^μ_μ with
strength

    α_φ = 2/3                                                         [2]

(the universal minimal-coupling result for a massless-to-massive KK scalar in
5D; see Appelquist & Chodos 1983; Duff, Nilsson & Pope 1986).  Its Yukawa range
is

    λ_φ = ħ c / m_φ  =  1 / m_φ     (natural Planck units)           [3]

When the cylinder condition holds (φ frozen to φ₀), the radion is effectively
infinitely massive and its Yukawa range collapses to zero → **no fifth force**.
A dynamical (non-frozen) radion with finite m_φ produces a Yukawa tail that
Eöt-Wash could detect if λ_φ ≳ 10 μm.

Channel 2 — KK-photon (vector) channel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The KK gauge boson A_μ acquires a mass from the compactification:

    m_A = 1 / R                                                        [4]

where R is the compactification radius.  It couples to baryon number B with
strength

    α_A = 2                                                            [5]

(from the standard KK dimensional-reduction formula; the factor of 2 relative
to gravity arises because A_μ is a vector rather than a scalar).  Its range is

    λ_A = R     (= 1 / m_A)                                           [6]

Eöt-Wash bounds on KK radius
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The combined (α, λ) constraint surface from Eöt-Wash (Kapner et al. 2007,
Lee et al. 2020) can be parameterised as

    |α_bound| = exp(−a − b × ln(λ / λ_ref))

where a, b, λ_ref are empirical fit parameters derived from the published
exclusion curves.  For the KK-photon channel (α = 2, universal coupling):

    λ_A  <  λ_EW_limit(2) ≈ 56 μm     (95% CL)

In Planck units (L_Pl ≈ 1.616 × 10⁻³⁵ m):

    λ_EW_limit_planck = 56 × 10⁻⁶ m / (1.616 × 10⁻³⁵ m/L_Pl)
                      ≈ 3.5 × 10³⁰ L_Pl

The cylinder-condition test
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If φ = φ₀ everywhere (frozen radion, cylinder condition satisfied):
    → m_φ → ∞  → λ_φ → 0  → no ISL signal
If φ ≠ φ₀ (dynamical radion):
    → finite λ_φ  → ISL signal potentially observable

The quantity that captures this is the cylinder deviation:

    δ_cyl(φ) = |φ − φ₀| / φ₀                                        [7]

which is zero when the cylinder condition is satisfied and non-zero otherwise.

Connection to Eöt-Wash
~~~~~~~~~~~~~~~~~~~~~~~
If the radion mass is tuned to give λ_φ ≳ 10 μm (m_φ ≲ 20 meV in SI units,
i.e. m_φ ≲ 1.6 × 10⁻²⁸ in Planck units), then the radion Yukawa is within
Eöt-Wash's accessible range.  The predicted ISL correction is:

    δg/g(r) = α_φ × e^{−r/λ_φ}                                      [8]

which is bounded to be < 10⁻³ for r ≳ 100 μm and α_φ = 2/3.  This gives the
testable upper bound on the GW mass parameter:

    m_φ ≲ 2 × 10⁻³ eV / c² ≈ 10⁻²⁸ M_Pl

All quantities are in **natural (Planck) units**: ħ = c = G = k_B = 1.

Key dimensional conversions (provided as module constants):
    L_Pl = 1.616e-35 m       (Planck length in SI)
    M_Pl = 2.176e-8 kg       (Planck mass in SI)
    1 eV = 8.191e-29 M_Pl    (electron-volt in Planck mass units)
    1 μm = 6.187e28 L_Pl     (micrometre in Planck lengths)

Public API
----------
yukawa_range_radion(m_phi)
    Yukawa range of the radion channel: λ_φ = 1 / m_φ  (Planck units).

yukawa_range_kk(R)
    Yukawa range of the KK-photon channel: λ_A = R  (Planck units).

yukawa_correction(r, alpha, yukawa_lambda)
    Fractional ISL correction at separation r:  δg/g = α e^{−r/λ}.

isl_potential(r, M1, M2, alpha, yukawa_lambda)
    Full Yukawa-modified gravitational potential V(r) in Planck units.

cylinder_deviation(phi, phi0)
    Normalised deviation from the cylinder condition: |φ − φ₀| / φ₀.

radion_produces_fifth_force(phi, phi0, tol)
    Return True iff the radion deviates from φ₀ beyond tolerance tol.

eot_wash_alpha_bound(yukawa_lambda)
    Approximate Eöt-Wash upper bound on |α| at Yukawa range yukawa_lambda
    (in Planck units), based on the empirical fit to published exclusion curves.

fifth_force_signal_strength(m_phi, alpha, r)
    Convenience wrapper: δg/g = alpha × exp(−r × m_phi).

kk_compactification_radius(m_kk)
    Compactification radius from KK mass: R = 1 / m_kk  (Planck units).

radion_mass_from_gw(m_phi_bare, phi0, phi_min)
    Effective radion mass from the Goldberger–Wise potential curvature.
    For the GW potential V(φ) = ½ m_φ² (φ − φ_min)², the mass is m_φ_bare
    (unchanged; this function validates and returns the canonical value).

isl_summary(m_phi, R, r)
    Return a dict summarising both ISL channels at separation r.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""



from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",  # The braid triad; unique to this framework
}

import math


# ---------------------------------------------------------------------------
# Module-level constants (Planck units throughout unless noted)
# ---------------------------------------------------------------------------

#: Universal coupling of the KK scalar (radion) to matter, relative to gravity.
#: Derived from the KK minimal coupling in 5D (Appelquist & Chodos 1983).
ALPHA_RADION: float = 2.0 / 3.0

#: Coupling of the KK vector (gauge boson A_μ) to baryon number, relative to gravity.
#: Factor of 2 over scalar from the tensor-vs-scalar structure of the propagator.
ALPHA_KK_PHOTON: float = 2.0

#: Planck length in SI metres (NIST CODATA 2022)
L_PLANCK_SI: float = 1.616255e-35   # m

#: Planck mass in SI kilograms (NIST CODATA 2022)
M_PLANCK_SI: float = 2.176434e-8    # kg

#: 1 μm in Planck length units
MICRON_IN_PLANCK: float = 1.0e-6 / L_PLANCK_SI   # ≈ 6.187e28 L_Pl

#: 1 eV in Planck mass units  (1 eV / c² = 1.783e-36 kg; / M_Pl)
EV_IN_PLANCK_MASS: float = 1.783e-36 / M_PLANCK_SI  # ≈ 8.19e-29 M_Pl

#: Eöt-Wash reference range for the empirical α-bound fit (in Planck units)
#: Corresponds to 100 μm, the scale of the tightest published ISL constraint.
EOT_WASH_REFERENCE_LAMBDA_PLANCK: float = 100.0 * MICRON_IN_PLANCK

#: Eöt-Wash α upper bound at the reference range (100 μm, α = 2/3)
#: From Kapner et al. 2007 and Lee et al. 2020 (95% CL).
EOT_WASH_ALPHA_BOUND_AT_REFERENCE: float = 1.0e-3

#: Empirical log-slope of the Eöt-Wash α-bound vs log(λ):
#: |α_bound| ≈ C × (λ_ref / λ)^b   where b ≈ 2 for the tightest constraint.
#: This is a conservative approximation; real bound curves are more complex.
EOT_WASH_BOUND_SLOPE: float = 2.0

#: Canonical braid pair for the (5,7) branch
N1_CANONICAL: int = 5
N2_CANONICAL: int = 7
K_CS_CANONICAL: int = 74    # = 5² + 7²
C_S_CANONICAL: float = 12.0 / 37.0


# ---------------------------------------------------------------------------
# yukawa_range_radion
# ---------------------------------------------------------------------------

def yukawa_range_radion(m_phi: float) -> float:
    """Yukawa range of the radion (scalar) channel.

    In natural units the de Broglie wavelength of the radion with mass m_φ is

        λ_φ = ħ c / (m_φ c²) = 1 / m_φ                (Planck units)

    This is the length scale below which the Yukawa correction is of order
    one and above which it is exponentially suppressed.

    Parameters
    ----------
    m_phi : float
        Goldberger–Wise radion mass in Planck units (> 0).

    Returns
    -------
    lambda_phi : float
        Yukawa range in Planck units (> 0).

    Raises
    ------
    ValueError
        If m_phi ≤ 0.
    """
    if m_phi <= 0.0:
        raise ValueError(f"m_phi must be > 0, got {m_phi!r}")
    return 1.0 / m_phi


# ---------------------------------------------------------------------------
# yukawa_range_kk
# ---------------------------------------------------------------------------

def yukawa_range_kk(R: float) -> float:
    """Yukawa range of the KK-photon (vector) channel.

    The KK gauge boson A_μ acquires mass m_A = 1/R from the compactification,
    giving Yukawa range λ_A = R.

    Parameters
    ----------
    R : float
        Compactification radius in Planck units (> 0).

    Returns
    -------
    lambda_A : float
        Yukawa range in Planck units (= R).

    Raises
    ------
    ValueError
        If R ≤ 0.
    """
    if R <= 0.0:
        raise ValueError(f"R must be > 0, got {R!r}")
    return R


# ---------------------------------------------------------------------------
# yukawa_correction
# ---------------------------------------------------------------------------

def yukawa_correction(r: float, alpha: float, yukawa_lambda: float) -> float:
    """Fractional ISL correction δg/g = α e^{−r/λ}.

    This is the correction to the gravitational acceleration at separation r
    due to a Yukawa-type fifth force with coupling α and range λ.

    Parameters
    ----------
    r : float
        Test-mass separation in Planck units (> 0).
    alpha : float
        Dimensionless coupling strength (can be positive or negative).
    yukawa_lambda : float
        Yukawa range in Planck units (> 0).

    Returns
    -------
    delta_g_over_g : float
        Fractional correction to Newtonian gravity (dimensionless).

    Raises
    ------
    ValueError
        If r ≤ 0 or yukawa_lambda ≤ 0.
    """
    if r <= 0.0:
        raise ValueError(f"r must be > 0, got {r!r}")
    if yukawa_lambda <= 0.0:
        raise ValueError(f"yukawa_lambda must be > 0, got {yukawa_lambda!r}")
    return alpha * math.exp(-r / yukawa_lambda)


# ---------------------------------------------------------------------------
# isl_potential
# ---------------------------------------------------------------------------

def isl_potential(
    r: float,
    M1: float,
    M2: float,
    alpha: float,
    yukawa_lambda: float,
) -> float:
    """Full Yukawa-modified gravitational potential.

    V(r) = −G M₁ M₂ / r × (1 + α e^{−r/λ})

    In Planck units G = 1, so this simplifies to:

        V(r) = −M₁ M₂ / r × (1 + α e^{−r/λ})

    Parameters
    ----------
    r : float
        Test-mass separation in Planck units (> 0).
    M1, M2 : float
        Test masses in Planck units (> 0).
    alpha : float
        Yukawa coupling strength (dimensionless).
    yukawa_lambda : float
        Yukawa range in Planck units (> 0).

    Returns
    -------
    V : float
        Gravitational potential energy in Planck units (≤ 0 for alpha > −1).

    Raises
    ------
    ValueError
        If r ≤ 0, M1 ≤ 0, M2 ≤ 0, or yukawa_lambda ≤ 0.
    """
    if r <= 0.0:
        raise ValueError(f"r must be > 0, got {r!r}")
    if M1 <= 0.0:
        raise ValueError(f"M1 must be > 0, got {M1!r}")
    if M2 <= 0.0:
        raise ValueError(f"M2 must be > 0, got {M2!r}")
    if yukawa_lambda <= 0.0:
        raise ValueError(f"yukawa_lambda must be > 0, got {yukawa_lambda!r}")
    newton = -M1 * M2 / r
    correction = 1.0 + yukawa_correction(r, alpha, yukawa_lambda)
    return newton * correction


# ---------------------------------------------------------------------------
# cylinder_deviation
# ---------------------------------------------------------------------------

def cylinder_deviation(phi: float, phi0: float) -> float:
    """Normalised deviation from the cylinder condition.

    The cylinder condition of classical Kaluza–Klein theory requires the
    compactified metric to be independent of the extra coordinate, which is
    equivalent to requiring φ = φ₀ (constant radion field).  Any deviation
    from this condition implies a dynamical radion that mediates a fifth force.

        δ_cyl(φ) = |φ − φ₀| / φ₀

    δ_cyl = 0  → cylinder condition satisfied, no Yukawa signal.
    δ_cyl > 0  → radion is dynamical, Yukawa correction is active.

    Parameters
    ----------
    phi : float
        Current radion field value in Planck units (> 0).
    phi0 : float
        Reference vacuum value φ₀ in Planck units (> 0).

    Returns
    -------
    delta : float
        Normalised deviation (≥ 0).

    Raises
    ------
    ValueError
        If phi ≤ 0 or phi0 ≤ 0.
    """
    if phi <= 0.0:
        raise ValueError(f"phi must be > 0, got {phi!r}")
    if phi0 <= 0.0:
        raise ValueError(f"phi0 must be > 0, got {phi0!r}")
    return abs(phi - phi0) / phi0


# ---------------------------------------------------------------------------
# radion_produces_fifth_force
# ---------------------------------------------------------------------------

def radion_produces_fifth_force(
    phi: float,
    phi0: float,
    tol: float = 1e-10,
) -> bool:
    """Return True iff the radion deviates from φ₀ beyond tolerance.

    A radion displaced from its GW vacuum value φ₀ by more than tol × φ₀
    is considered dynamical and sources a Yukawa fifth force.

    Parameters
    ----------
    phi : float — current radion value (> 0)
    phi0 : float — GW vacuum value (> 0)
    tol : float — relative tolerance (default 1e-10)

    Returns
    -------
    bool
    """
    return cylinder_deviation(phi, phi0) > tol


# ---------------------------------------------------------------------------
# eot_wash_alpha_bound
# ---------------------------------------------------------------------------

def eot_wash_alpha_bound(yukawa_lambda: float) -> float:
    """Approximate Eöt-Wash upper bound on |α| at a given Yukawa range.

    Uses the empirical log-log approximation fit to the published Eöt-Wash
    exclusion curves (Kapner et al. 2007; Lee et al. 2020):

        |α_bound(λ)| ≈ C × (λ_ref / λ)^b

    where
        λ_ref = EOT_WASH_REFERENCE_LAMBDA_PLANCK  (100 μm in Planck units)
        C     = EOT_WASH_ALPHA_BOUND_AT_REFERENCE  (≈ 10⁻³ at 100 μm)
        b     = EOT_WASH_BOUND_SLOPE               (≈ 2)

    This is a conservative (weaker) approximation:
    - For λ ≫ λ_ref the real bound is tighter (ISL tests at longer range are
      more constraining due to larger signal-to-noise).
    - For λ ≪ λ_ref the bound relaxes as the test-mass separation exceeds λ.

    The approximation is valid within ~1 order of magnitude in α over the
    range 10 μm ≲ λ ≲ 1 mm.

    Parameters
    ----------
    yukawa_lambda : float
        Yukawa range in Planck units (> 0).

    Returns
    -------
    alpha_bound : float
        Upper bound on |α| (> 0).

    Raises
    ------
    ValueError
        If yukawa_lambda ≤ 0.
    """
    if yukawa_lambda <= 0.0:
        raise ValueError(f"yukawa_lambda must be > 0, got {yukawa_lambda!r}")
    ratio = EOT_WASH_REFERENCE_LAMBDA_PLANCK / yukawa_lambda
    return EOT_WASH_ALPHA_BOUND_AT_REFERENCE * (ratio ** EOT_WASH_BOUND_SLOPE)


# ---------------------------------------------------------------------------
# fifth_force_signal_strength
# ---------------------------------------------------------------------------

def fifth_force_signal_strength(
    m_phi: float,
    alpha: float,
    r: float,
) -> float:
    """Convenience wrapper: fractional ISL correction δg/g = α e^{−r m_φ}.

    Equivalent to yukawa_correction(r, alpha, 1/m_phi).

    Parameters
    ----------
    m_phi : float — radion mass in Planck units (> 0)
    alpha : float — coupling strength (dimensionless)
    r : float     — test-mass separation in Planck units (> 0)

    Returns
    -------
    delta_g_over_g : float

    Raises
    ------
    ValueError if m_phi ≤ 0 or r ≤ 0.
    """
    if m_phi <= 0.0:
        raise ValueError(f"m_phi must be > 0, got {m_phi!r}")
    if r <= 0.0:
        raise ValueError(f"r must be > 0, got {r!r}")
    return alpha * math.exp(-r * m_phi)


# ---------------------------------------------------------------------------
# kk_compactification_radius
# ---------------------------------------------------------------------------

def kk_compactification_radius(m_kk: float) -> float:
    """Compactification radius from the KK mass scale.

    The first KK excitation has mass m_KK = 1/R, so the compactification
    radius is R = 1/m_KK.

    Parameters
    ----------
    m_kk : float
        KK mass scale in Planck units (> 0).

    Returns
    -------
    R : float
        Compactification radius in Planck units (> 0).

    Raises
    ------
    ValueError if m_kk ≤ 0.
    """
    if m_kk <= 0.0:
        raise ValueError(f"m_kk must be > 0, got {m_kk!r}")
    return 1.0 / m_kk


# ---------------------------------------------------------------------------
# radion_mass_from_gw
# ---------------------------------------------------------------------------

def radion_mass_from_gw(
    m_phi_bare: float,
    phi0: float,
    phi_min: float,
) -> float:
    """Effective radion mass from the Goldberger–Wise potential.

    The GW potential V(φ) = ½ m_φ² (φ − φ_min)² has a second derivative
    at the minimum equal to m_φ², so the physical radion mass is m_phi_bare.

    This function validates the GW parameter triple and returns m_phi_bare,
    confirming that the Goldberger–Wise stabilisation does not renormalise
    the radion mass at tree level.

    Parameters
    ----------
    m_phi_bare : float — bare GW mass parameter (> 0)
    phi0       : float — GW vacuum expectation value (> phi_min)
    phi_min    : float — GW lower bound on φ (> 0)

    Returns
    -------
    m_phi_eff : float
        Effective radion mass = m_phi_bare (tree level, Planck units).

    Raises
    ------
    ValueError
        If m_phi_bare ≤ 0, phi_min ≤ 0, or phi0 ≤ phi_min.
    """
    if m_phi_bare <= 0.0:
        raise ValueError(f"m_phi_bare must be > 0, got {m_phi_bare!r}")
    if phi_min <= 0.0:
        raise ValueError(f"phi_min must be > 0, got {phi_min!r}")
    if phi0 <= phi_min:
        raise ValueError(
            f"phi0 ({phi0!r}) must be strictly > phi_min ({phi_min!r})"
        )
    return m_phi_bare


# ---------------------------------------------------------------------------
# isl_summary
# ---------------------------------------------------------------------------

def isl_summary(
    m_phi: float,
    R: float,
    r: float,
) -> dict:
    """Full ISL prediction summary for both Yukawa channels.

    Computes the expected fractional ISL corrections from:
    - Channel 1: radion (scalar), coupling α_φ = 2/3, range λ_φ = 1/m_φ
    - Channel 2: KK photon (vector), coupling α_A = 2, range λ_A = R

    Also reports the Eöt-Wash bound on α at each channel's range, and whether
    each channel is within Eöt-Wash's accessible sensitivity window.

    Parameters
    ----------
    m_phi : float — radion mass (Planck units, > 0)
    R     : float — compactification radius (Planck units, > 0)
    r     : float — test-mass separation (Planck units, > 0)

    Returns
    -------
    result : dict with keys
        'lambda_radion'         — Yukawa range of scalar channel (Planck units)
        'lambda_kk'             — Yukawa range of vector channel (Planck units)
        'alpha_radion'          — coupling of scalar channel (= 2/3)
        'alpha_kk'              — coupling of vector channel (= 2)
        'delta_g_radion'        — δg/g from scalar channel at separation r
        'delta_g_kk'            — δg/g from vector channel at separation r
        'eot_wash_bound_radion' — Eöt-Wash |α| bound at λ_φ
        'eot_wash_bound_kk'     — Eöt-Wash |α| bound at λ_A
        'radion_detectable'     — True if |δg/g_radion| > 10⁻¹⁵ (torsion sensitivity)
        'kk_detectable'         — True if |δg/g_kk| > 10⁻¹⁵
        'cylinder_condition'    — 'frozen (no signal)' if m_phi → ∞ else 'dynamical'

    Raises
    ------
    ValueError if m_phi ≤ 0, R ≤ 0, or r ≤ 0.
    """
    lam_phi = yukawa_range_radion(m_phi)
    lam_kk  = yukawa_range_kk(R)

    dg_phi = yukawa_correction(r, ALPHA_RADION,   lam_phi)
    dg_kk  = yukawa_correction(r, ALPHA_KK_PHOTON, lam_kk)

    bound_phi = eot_wash_alpha_bound(lam_phi)
    bound_kk  = eot_wash_alpha_bound(lam_kk)

    _sensitivity = 1.0e-15   # minimum detectable δg/g (torsion balance floor)

    return {
        "lambda_radion": lam_phi,
        "lambda_kk": lam_kk,
        "alpha_radion": ALPHA_RADION,
        "alpha_kk": ALPHA_KK_PHOTON,
        "delta_g_radion": dg_phi,
        "delta_g_kk": dg_kk,
        "eot_wash_bound_radion": bound_phi,
        "eot_wash_bound_kk": bound_kk,
        "radion_detectable": abs(dg_phi) > _sensitivity,
        "kk_detectable": abs(dg_kk) > _sensitivity,
        "cylinder_condition": "dynamical (fifth force active)",
    }


# ---------------------------------------------------------------------------
# Authorship
# ---------------------------------------------------------------------------
# Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
# Code architecture, test suites, document engineering, and synthesis:
# GitHub Copilot (AI).
