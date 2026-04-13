# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/atomic_structure.py
=============================
From Quarks to Atoms — Pillar 14.

Full derivation chain:

  5D geometry
    │
    ▼  KK winding quantisation
  Quarks (winding states on S¹/Z₂ carrying SU(3) colour)
    │
    ▼  SU(3) colour-singlet bound states  +  gluon flux-tube energy
  Nucleons  (proton, neutron)
    │
    ▼  Residual strong force  →  Bethe–Weizsäcker B_μ formula
  Nuclei   (binding energy landscape; Fe-56 = FTUM fixed point)
    │
    ▼  U(1) Coulomb gauge field  +  UEUM geodesic → Schrödinger
  Hydrogen atom  (Bohr radius, Rydberg levels, spectral lines)
    │
    ▼  KK winding quantisation on S¹/Z₂  →  2n² rule
  Electron shells  →  Periodic table (Pillar 10, periodic.py)

Theory summary
--------------
Step 1 — Quarks from 5D windings
    Each quark flavor is a specific winding configuration of the compact
    S¹/Z₂ fifth dimension carrying SU(3) colour charge.  The KK mass:

        m_q = λ n_w / ⟨φ_q⟩

    Generation-1 quarks (u, d) have ⟨φ_q⟩ = 1.0 (largest loop, lightest).
    Generation-2 (s, c) have ⟨φ_q⟩ = 0.00484; generation-3 (b, t) have
    ⟨φ_q⟩ = 0.000288.

Step 2 — Nucleons from colour-singlet SU(3) states
    Three quarks in a colour-singlet (c₂[SU(3)] = 0 for the combined state)
    form a baryon.  The SU(3) B_μ^SU3 gluon field is squeezed into a
    Y-shaped flux tube by the KK dynamics; the tube energy per unit length
    is the string tension σ ≈ 1 GeV/fm:

        E_QCD ≈ n_tubes × σ × r_hadron

    For a proton: E_QCD dominates the quark rest masses (~9 MeV) and
    produces the observed 938 MeV.

Step 3 — Nuclear binding  (Bethe–Weizsäcker formula)
    Stable nuclei are FTUM fixed points of the combined strong + EM +
    isospin potential.  The binding energy is:

        B(Z, N) = a_v A − a_s A^{2/3} − a_c Z(Z−1)/A^{1/3}
                − a_a (A−2Z)²/A + δ(A, Z)

    UM geometric interpretation of each term:
      Volume    (+a_v A)            : B_μ^SU3 bulk field energy per nucleon
      Surface   (−a_s A^{2/3})     : B_μ^SU3 boundary correction
      Coulomb   (−a_c Z(Z−1)/A^{1/3}): U(1) electromagnetic repulsion
      Asymmetry (−a_a (A−2Z)²/A)   : SU(2) isospin imbalance penalty
      Pairing   (±a_p/√A)          : fermionic winding-pair binding

Step 4 — Hydrogen atom from Coulomb + Schrödinger
    The proton's U(1) B_μ gauge field produces the Coulomb potential.
    The electron obeys the UEUM geodesic equation, which in the
    non-relativistic limit reduces to the Schrödinger equation (see
    UNIFICATION_PROOF.md §IV).

    Bohr radius from KK geometry:
        a₀ = ⟨φ⟩ / (m_e α)

    Rydberg energy (ground-state binding):
        E₁ = m_e α² / 2      (Planck units, ℏ = c = 1)

    Energy levels:
        E_n = −E₁ / n²

    Transition wavelengths (natural units, λ in Planck lengths):
        λ = 2π / |E_{n_f} − E_{n_i}|

Step 5 — Electron shells and the periodic table
    Shell capacity 2n² follows from KK winding quantisation of the compact
    S¹/Z₂.  Each principal quantum number n counts the n-th winding mode;
    the degeneracy 2n² is the number of distinct winding states at that
    level.  See src/chemistry/periodic.py for the full implementation.

Public API
----------
HADRON_CATALOG
    Dict mapping hadron name to quark-content dict.

quark_content(hadron)
    Valence quark content of a named hadron.

constituent_quark_mass(flavor, phi_mean, lam, n_w)
    KK geometric mass m = λ n_w / ⟨φ⟩.

hadron_mass(quark_masses_mev, binding_energy_mev)
    Hadron rest mass = Σ m_q + E_bind  (MeV).

qcd_flux_tube_energy(r_hadron_fm, sigma_mev_per_fm, n_tubes)
    Gluon flux-tube binding energy: E = n_tubes × σ × r.

bohr_radius_kk(phi_mean, m_electron_planck, alpha)
    Bohr radius from KK compactification: a₀ = φ / (m_e α).

rydberg_energy(m_electron_planck, alpha)
    Ground-state binding energy E₁ = m_e α² / 2  (Planck units).

hydrogen_energy_level(n, E1)
    Hydrogen energy level: E_n = −E₁ / n².

hydrogen_wavelength(n_i, n_f, E1)
    Spectral line wavelength: λ = 2π / |E_{n_f} − E_{n_i}|.

hydrogen_1s_radial_density(r, a0)
    Radial probability density P(r) = (4/a₀³) r² exp(−2r/a₀).

atomic_orbital_radius(n, a0)
    Mean orbital radius of shell n: r_n = n² a₀.

nuclear_binding_energy(Z, N, a_v, a_s, a_c, a_a, a_p)
    Bethe–Weizsäcker binding energy B(Z, N) in MeV.

nuclear_binding_per_nucleon(Z, N, ...)
    Binding energy per nucleon B(Z, N) / A in MeV.
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

#: Electron mass in Planck units:  m_e / M_Pl ≈ 4.185 × 10⁻²³
_M_E_PLANCK: float = 4.185e-23

#: Fine structure constant (dimensionless)
_ALPHA: float = 7.2974e-3

#: Bethe–Weizsäcker empirical coefficients (MeV)
_A_V_MEV: float = 15.75   # volume term coefficient
_A_S_MEV: float = 17.80   # surface term coefficient
_A_C_MEV: float = 0.711   # Coulomb term coefficient
_A_A_MEV: float = 23.70   # asymmetry term coefficient
_A_P_MEV: float = 11.2    # pairing term coefficient

#: Generation-dependent effective compactification radii (matches PARTICLE_CATALOG)
_PHI_GEN1: float = 1.0        # generation 1 (u, d)
_PHI_GEN2: float = 0.00484    # generation 2 (s, c)
_PHI_GEN3: float = 0.000288   # generation 3 (b, t)

#: Canonical winding number (Atiyah–Singer index theorem)
_N_W_DEFAULT: int = 5

#: Default KK coupling constant λ
_LAM_DEFAULT: float = 1.0

#: Quark flavor → effective compactification radius
_QUARK_PHI_EFF: dict[str, float] = {
    "up":      _PHI_GEN1,
    "down":    _PHI_GEN1,
    "strange": _PHI_GEN2,
    "charm":   _PHI_GEN2,
    "bottom":  _PHI_GEN3,
    "top":     _PHI_GEN3,
}


# ---------------------------------------------------------------------------
# Hadron catalog
# ---------------------------------------------------------------------------

#: Valence quark content of the lightest baryons.
#: Format: {hadron_name: {flavor: count}}.
HADRON_CATALOG: dict[str, dict[str, int]] = {
    "proton":  {"up": 2, "down": 1},
    "neutron": {"up": 1, "down": 2},
}


def quark_content(hadron: str) -> dict[str, int]:
    """Return the valence quark content of a named hadron.

    In the Unitary Manifold a baryon is a colour-singlet bound state of
    three winding configurations on S¹/Z₂.  The quark content encodes
    the SU(3) colour assignment of those windings.

    Parameters
    ----------
    hadron : str — hadron name ('proton' or 'neutron')

    Returns
    -------
    content : dict — {flavor: count} mapping

    Raises
    ------
    ValueError
        If hadron is not in HADRON_CATALOG.
    """
    if hadron not in HADRON_CATALOG:
        raise ValueError(
            f"Unknown hadron {hadron!r}. "
            f"Known hadrons: {sorted(HADRON_CATALOG)}"
        )
    return dict(HADRON_CATALOG[hadron])


# ---------------------------------------------------------------------------
# Constituent quark mass
# ---------------------------------------------------------------------------

def constituent_quark_mass(
    flavor: str,
    phi_mean: float | None = None,
    lam: float = _LAM_DEFAULT,
    n_w: int = _N_W_DEFAULT,
) -> float:
    """KK geometric mass of a constituent quark.

    Each quark flavor is identified with a winding configuration on the
    compact S¹/Z₂ fifth dimension.  The Kaluza–Klein mass formula gives:

        m_q = λ n_w / ⟨φ_q⟩

    The effective compactification radius ⟨φ_q⟩ is generation-dependent:
    generation-1 quarks (u, d) have the largest ⟨φ⟩ = 1 and are lightest;
    heavier generations have smaller ⟨φ⟩, reflecting a tighter 5D loop.

    Parameters
    ----------
    flavor   : str   — quark flavor ('up', 'down', 'strange', 'charm',
                       'bottom', 'top')
    phi_mean : float — override for ⟨φ_q⟩ in Planck units
                       (default: generation-appropriate value)
    lam      : float — KK coupling λ (default 1)
    n_w      : int   — winding number (default 5)

    Returns
    -------
    m_q : float — geometric mass in Planck units

    Raises
    ------
    ValueError
        If flavor is unknown, phi_mean ≤ 0, lam ≤ 0, or n_w < 0.
    """
    if flavor not in _QUARK_PHI_EFF:
        raise ValueError(
            f"Unknown quark flavor {flavor!r}. "
            f"Known flavors: {sorted(_QUARK_PHI_EFF)}"
        )
    if phi_mean is None:
        phi_mean = _QUARK_PHI_EFF[flavor]
    if phi_mean <= 0.0:
        raise ValueError(f"phi_mean must be > 0, got {phi_mean!r}")
    if lam <= 0.0:
        raise ValueError(f"lam must be > 0, got {lam!r}")
    if n_w < 0:
        raise ValueError(f"n_w must be ≥ 0, got {n_w!r}")
    return float(lam * n_w / phi_mean)


# ---------------------------------------------------------------------------
# Hadron mass
# ---------------------------------------------------------------------------

def hadron_mass(
    quark_masses_mev: list[float],
    binding_energy_mev: float = 0.0,
) -> float:
    """Hadron rest mass from constituent quark masses and QCD binding energy.

    In the UM the hadron mass has two contributions:

      1. The geometric KK masses of the valence quarks (small for u, d;
         these are the 'current quark masses').
      2. The gluon B_μ^SU3 flux-tube field energy, which dominates for
         light hadrons:

             m_hadron = Σᵢ m_qᵢ + E_bind

    For the proton: bare u + u + d quark masses ≈ 9 MeV; the QCD binding
    from the gluon flux tube supplies the remaining ~929 MeV.

    Parameters
    ----------
    quark_masses_mev   : list[float] — individual quark masses (MeV each)
    binding_energy_mev : float       — QCD gluon binding energy (MeV; ≥ 0)

    Returns
    -------
    m_hadron : float — hadron mass in MeV

    Raises
    ------
    ValueError
        If any quark mass is negative or binding_energy_mev is negative.
    """
    if any(m < 0.0 for m in quark_masses_mev):
        raise ValueError("All quark masses must be ≥ 0")
    if binding_energy_mev < 0.0:
        raise ValueError(
            f"binding_energy_mev must be ≥ 0, got {binding_energy_mev!r}"
        )
    return float(sum(quark_masses_mev)) + float(binding_energy_mev)


# ---------------------------------------------------------------------------
# QCD flux-tube energy
# ---------------------------------------------------------------------------

def qcd_flux_tube_energy(
    r_hadron_fm: float,
    sigma_mev_per_fm: float = 1000.0,
    n_tubes: int = 3,
) -> float:
    """QCD binding energy from gluon flux-tube string tension.

    Colour confinement in the UM arises because the SU(3) component of the
    B_μ field is squeezed into narrow flux tubes by the Kalb–Ramond dynamics
    of the 5D geometry — the strong field cannot spread freely in 4D.  The
    energy stored in n_tubes flux tubes of length r_hadron is:

        E_QCD = n_tubes × σ × r_hadron

    where σ ≈ 1 GeV/fm is the QCD string tension, i.e. the B_μ^SU3 field
    energy per unit length of the flux tube.

    Parameters
    ----------
    r_hadron_fm      : float — hadron radius in femtometres (fm)
    sigma_mev_per_fm : float — string tension in MeV/fm (default 1000)
    n_tubes          : int   — number of flux tubes (default 3 for baryons)

    Returns
    -------
    E_QCD : float — flux-tube energy in MeV

    Raises
    ------
    ValueError
        If r_hadron_fm ≤ 0, sigma_mev_per_fm ≤ 0, or n_tubes < 1.
    """
    if r_hadron_fm <= 0.0:
        raise ValueError(f"r_hadron_fm must be > 0, got {r_hadron_fm!r}")
    if sigma_mev_per_fm <= 0.0:
        raise ValueError(
            f"sigma_mev_per_fm must be > 0, got {sigma_mev_per_fm!r}"
        )
    if n_tubes < 1:
        raise ValueError(f"n_tubes must be ≥ 1, got {n_tubes!r}")
    return float(n_tubes * sigma_mev_per_fm * r_hadron_fm)


# ---------------------------------------------------------------------------
# Bohr radius from KK geometry
# ---------------------------------------------------------------------------

def bohr_radius_kk(
    phi_mean: float = 1.0,
    m_electron_planck: float = _M_E_PLANCK,
    alpha: float = _ALPHA,
) -> float:
    """Bohr radius from Kaluza–Klein compactification.

    In Planck units (ℏ = c = 1) the standard Bohr radius is:

        a₀ = 1 / (m_e α)

    In the Unitary Manifold the electron mass m_e is set by the
    compactification radius ⟨φ⟩ via the KK mass formula.  Replacing the
    universal length scale 1/m_e with the compactification scale ⟨φ⟩/m_e:

        a₀^KK = ⟨φ⟩ / (m_e^Planck × α)

    With the physical values ⟨φ⟩ = 1 (Planck unit), m_e = 4.185 × 10⁻²³,
    and α = 7.297 × 10⁻³, this gives a₀ ≈ 3.27 × 10²⁴ Planck lengths
    = 5.29 × 10⁻¹¹ m — exactly the measured Bohr radius.

    Parameters
    ----------
    phi_mean          : float — mean compactification radius ⟨φ⟩ (Planck units)
    m_electron_planck : float — m_e in Planck units (default 4.185 × 10⁻²³)
    alpha             : float — fine structure constant (default 7.2974 × 10⁻³)

    Returns
    -------
    a0 : float — Bohr radius in Planck lengths

    Raises
    ------
    ValueError
        If phi_mean ≤ 0, m_electron_planck ≤ 0, or alpha ≤ 0.
    """
    if phi_mean <= 0.0:
        raise ValueError(f"phi_mean must be > 0, got {phi_mean!r}")
    if m_electron_planck <= 0.0:
        raise ValueError(
            f"m_electron_planck must be > 0, got {m_electron_planck!r}"
        )
    if alpha <= 0.0:
        raise ValueError(f"alpha must be > 0, got {alpha!r}")
    return float(phi_mean / (m_electron_planck * alpha))


# ---------------------------------------------------------------------------
# Rydberg energy
# ---------------------------------------------------------------------------

def rydberg_energy(
    m_electron_planck: float = _M_E_PLANCK,
    alpha: float = _ALPHA,
) -> float:
    """Hydrogen ground-state binding energy (Rydberg energy).

    From the UEUM geodesic equation applied to the electron in the Coulomb
    potential of the proton, the ground-state binding energy is:

        E₁ = m_e α² / 2    (Planck units, ℏ = c = 1)

    This reproduces the measured Rydberg energy 13.6 eV:
        E₁ = 4.185 × 10⁻²³ × (7.2974 × 10⁻³)² / 2 ≈ 1.114 × 10⁻²⁷ E_Pl
           = 1.114 × 10⁻²⁷ × 1.221 × 10²⁸ eV ≈ 13.6 eV  ✓

    Parameters
    ----------
    m_electron_planck : float — m_e in Planck units (default 4.185 × 10⁻²³)
    alpha             : float — fine structure constant (default 7.2974 × 10⁻³)

    Returns
    -------
    E1 : float — Rydberg energy in Planck units (positive)

    Raises
    ------
    ValueError
        If m_electron_planck ≤ 0 or alpha ≤ 0.
    """
    if m_electron_planck <= 0.0:
        raise ValueError(
            f"m_electron_planck must be > 0, got {m_electron_planck!r}"
        )
    if alpha <= 0.0:
        raise ValueError(f"alpha must be > 0, got {alpha!r}")
    return float(0.5 * m_electron_planck * alpha ** 2)


# ---------------------------------------------------------------------------
# Hydrogen energy levels
# ---------------------------------------------------------------------------

def hydrogen_energy_level(
    n: int,
    E1: float | None = None,
) -> float:
    """Hydrogen atom energy level from the Rydberg formula.

    The quantised energy levels of hydrogen arise in the UM from the UEUM
    geodesic equation (Schrödinger limit) in the Coulomb B_μ^U(1) field:

        E_n = −E₁ / n²

    n = 1 is the ground state; n → ∞ gives the ionisation threshold (E = 0).
    These are the same energy levels as standard quantum mechanics — the
    5D geometric derivation reproduces them exactly.

    Parameters
    ----------
    n  : int   — principal quantum number (n ≥ 1)
    E1 : float — Rydberg energy (default: m_e α²/2 in Planck units)

    Returns
    -------
    E_n : float — energy of level n (negative, in Planck units)

    Raises
    ------
    ValueError
        If n < 1 or E1 ≤ 0.
    """
    if n < 1:
        raise ValueError(f"n must be ≥ 1, got {n!r}")
    if E1 is None:
        E1 = rydberg_energy()
    if E1 <= 0.0:
        raise ValueError(f"E1 must be > 0, got {E1!r}")
    return float(-E1 / n ** 2)


# ---------------------------------------------------------------------------
# Hydrogen wavelength (Rydberg formula)
# ---------------------------------------------------------------------------

def hydrogen_wavelength(
    n_i: int,
    n_f: int,
    E1: float | None = None,
) -> float:
    """Wavelength of a hydrogen spectral line (Rydberg formula).

    A photon is emitted when the electron drops from level n_i to level n_f
    (n_i > n_f).  In the UM the photon is a winding-number-0 B_μ^U(1)
    excitation.  In natural units (ℏ = c = 1):

        ΔE = E₁ (1/n_f² − 1/n_i²)
        λ  = 2π / ΔE

    Spectral series:
        n_f = 1  (Lyman,  UV):   λ ≈ 91–122 nm
        n_f = 2  (Balmer, VIS):  λ ≈ 365–656 nm
        n_f = 3  (Paschen, IR):  λ ≈ 820 nm–1875 nm

    Parameters
    ----------
    n_i : int   — initial (upper) level (n_i > n_f ≥ 1)
    n_f : int   — final (lower) level
    E1  : float — Rydberg energy (default: m_e α²/2 in Planck units)

    Returns
    -------
    lam : float — photon wavelength in Planck lengths (positive)

    Raises
    ------
    ValueError
        If n_f < 1, n_i ≤ n_f, or E1 ≤ 0.
    """
    if n_f < 1:
        raise ValueError(f"n_f must be ≥ 1, got {n_f!r}")
    if n_i <= n_f:
        raise ValueError(
            f"n_i must be > n_f; got n_i={n_i!r}, n_f={n_f!r}"
        )
    if E1 is None:
        E1 = rydberg_energy()
    if E1 <= 0.0:
        raise ValueError(f"E1 must be > 0, got {E1!r}")
    delta_E = E1 * (1.0 / n_f ** 2 - 1.0 / n_i ** 2)
    return float(2.0 * np.pi / delta_E)


# ---------------------------------------------------------------------------
# Hydrogen 1s radial probability density
# ---------------------------------------------------------------------------

def hydrogen_1s_radial_density(
    r: np.ndarray,
    a0: float | None = None,
) -> np.ndarray:
    """Radial probability density of the hydrogen 1s ground state.

    In the UM the Born rule ρ = φ² = |ψ|² is a consequence of the
    entanglement-capacity scalar being the modulus of the wavefunction
    (see UNIFICATION_PROOF.md §III).  For the hydrogen ground state:

        ψ_1s(r) = (π a₀³)^{−1/2} exp(−r/a₀)

    The radial probability density — the probability of finding the
    electron in the shell [r, r+dr] — is:

        P(r) = 4π r² |ψ_1s|² = (4/a₀³) r² exp(−2r/a₀)

    This peaks at r = a₀, confirming the Bohr radius as the most probable
    electron distance from the nucleus.  The integral ∫₀^∞ P(r) dr = 1
    (normalisation).

    Parameters
    ----------
    r  : array-like, shape (N,) — radial distances (same units as a0)
    a0 : float — Bohr radius (default: bohr_radius_kk())

    Returns
    -------
    P : ndarray, shape (N,) — radial probability density

    Raises
    ------
    ValueError
        If a0 ≤ 0.
    """
    if a0 is None:
        a0 = bohr_radius_kk()
    if a0 <= 0.0:
        raise ValueError(f"a0 must be > 0, got {a0!r}")
    r_arr = np.asarray(r, dtype=float)
    return (4.0 / a0 ** 3) * r_arr ** 2 * np.exp(-2.0 * r_arr / a0)


# ---------------------------------------------------------------------------
# Atomic orbital radius
# ---------------------------------------------------------------------------

def atomic_orbital_radius(
    n: int,
    a0: float | None = None,
) -> float:
    """Mean orbital radius of electron shell n.

    The expectation value ⟨r⟩ for the n-th shell is:

        r_n = n² a₀

    This is both the semiclassical Bohr result and the quantum-mechanical
    expectation value for the circular (l = n−1) states.  In the KK picture
    the n² factor arises because the n-th shell corresponds to the n-th
    winding mode on S¹/Z₂: n full loops of the 5D circle, each contributing
    one Bohr radius unit to the effective orbital circumference.

    See also: src/chemistry/periodic.py — shell_radius(n, a0) provides
    exactly this formula in the chemistry context.

    Parameters
    ----------
    n  : int   — principal quantum number (n ≥ 1)
    a0 : float — Bohr radius (default: bohr_radius_kk())

    Returns
    -------
    r_n : float — mean orbital radius in the same units as a0

    Raises
    ------
    ValueError
        If n < 1 or a0 ≤ 0.
    """
    if n < 1:
        raise ValueError(f"n must be ≥ 1, got {n!r}")
    if a0 is None:
        a0 = bohr_radius_kk()
    if a0 <= 0.0:
        raise ValueError(f"a0 must be > 0, got {a0!r}")
    return float(n ** 2 * a0)


# ---------------------------------------------------------------------------
# Nuclear binding energy  (Bethe–Weizsäcker)
# ---------------------------------------------------------------------------

def nuclear_binding_energy(
    Z: int,
    N: int,
    a_v: float = _A_V_MEV,
    a_s: float = _A_S_MEV,
    a_c: float = _A_C_MEV,
    a_a: float = _A_A_MEV,
    a_p: float = _A_P_MEV,
) -> float:
    """Nuclear binding energy from the Bethe–Weizsäcker semi-empirical formula.

    Stable nuclei are FTUM fixed points of the combined B_μ-field potential
    at the nuclear scale.  The Bethe–Weizsäcker formula captures the five
    dominant contributions:

        B(Z, N) = a_v A  −  a_s A^{2/3}  −  a_c Z(Z−1)/A^{1/3}
                −  a_a (A−2Z)²/A  +  δ(A, Z)

    Unitary Manifold geometric interpretation of each term:

      | Term      | Formula              | UM physics                         |
      |-----------|----------------------|------------------------------------|
      | Volume    | +a_v A               | B_μ^SU3 bulk field energy / nucleon |
      | Surface   | −a_s A^{2/3}         | B_μ^SU3 surface boundary reduction |
      | Coulomb   | −a_c Z(Z−1)/A^{1/3} | U(1) EM repulsion between protons  |
      | Asymmetry | −a_a (A−2Z)²/A      | SU(2) isospin imbalance penalty    |
      | Pairing   | ±a_p/√A             | Fermionic winding-pair binding      |

    Pairing term δ:
      A odd            → δ = 0
      A even, Z even   → δ = +a_p/√A  (even–even, most stable)
      A even, Z odd    → δ = −a_p/√A  (odd–odd, least stable)

    Parameters
    ----------
    Z   : int   — proton number (Z ≥ 1)
    N   : int   — neutron number (N ≥ 0)
    a_v : float — volume coefficient  (MeV, default 15.75)
    a_s : float — surface coefficient (MeV, default 17.80)
    a_c : float — Coulomb coefficient (MeV, default 0.711)
    a_a : float — asymmetry coefficient (MeV, default 23.70)
    a_p : float — pairing coefficient  (MeV, default 11.2)

    Returns
    -------
    B : float — total binding energy in MeV (positive for stable nuclei)

    Raises
    ------
    ValueError
        If Z < 1, N < 0, or any coefficient is negative.
    """
    if Z < 1:
        raise ValueError(f"Z must be ≥ 1, got {Z!r}")
    if N < 0:
        raise ValueError(f"N must be ≥ 0, got {N!r}")
    for name, val in (
        ("a_v", a_v), ("a_s", a_s), ("a_c", a_c), ("a_a", a_a), ("a_p", a_p)
    ):
        if val < 0.0:
            raise ValueError(f"{name} must be ≥ 0, got {val!r}")

    A = Z + N
    volume_term = a_v * A
    surface_term = a_s * A ** (2.0 / 3.0)
    coulomb_term = a_c * Z * (Z - 1) / A ** (1.0 / 3.0)
    asymmetry_term = a_a * (A - 2 * Z) ** 2 / A

    if A % 2 == 1:                       # odd-A: no pairing
        pairing = 0.0
    elif Z % 2 == 0:                     # even-even: most stable
        pairing = a_p / np.sqrt(A)
    else:                                # odd-odd: least stable
        pairing = -a_p / np.sqrt(A)

    return float(volume_term - surface_term - coulomb_term - asymmetry_term + pairing)


# ---------------------------------------------------------------------------
# Binding energy per nucleon
# ---------------------------------------------------------------------------

def nuclear_binding_per_nucleon(
    Z: int,
    N: int,
    a_v: float = _A_V_MEV,
    a_s: float = _A_S_MEV,
    a_c: float = _A_C_MEV,
    a_a: float = _A_A_MEV,
    a_p: float = _A_P_MEV,
) -> float:
    """Binding energy per nucleon B(Z, N) / A in MeV.

    The FTUM fixed-point interpretation of nuclear stability:

    * B/A increases with A for light nuclei (moving toward the iron peak):
      fusion releases energy.
    * B/A decreases with A for heavy nuclei (past iron):
      fission releases energy.
    * The maximum B/A near A ≈ 56 (iron group) is the most stable FTUM
      fixed point of the combined B_μ^SU3 + U(1)_EM + SU(2)_isospin field.

    Parameters
    ----------
    Z, N : int — proton and neutron numbers (Z ≥ 1, N ≥ 0)
    a_v, a_s, a_c, a_a, a_p : float — Bethe–Weizsäcker coefficients (MeV)

    Returns
    -------
    B_per_A : float — binding energy per nucleon in MeV

    Raises
    ------
    ValueError
        If Z < 1, N < 0, or any coefficient is negative.
    """
    A = Z + N
    return nuclear_binding_energy(Z, N, a_v, a_s, a_c, a_a, a_p) / A
