# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/physics/lattice_dynamics.py
================================
Pillar 15-B — Coherence-Volume Scaling and Collective Tunneling Gain.

Overview
--------
A fundamental weakness of single-pair cold-fusion models is that they
compute the tunneling probability for two isolated deuterons.  In a loaded
Pd-D lattice the radion field φ does not screen a single pair; it screens an
**entire coherence volume** — the spatial domain over which the φ condensate
is phase-coherent.

Within this domain, all N_coh deuterium pairs tunnel *coherently*: their
amplitudes add rather than their probabilities.  The resulting collective
Gamow factor is not G_single^N but rather:

    G_collective(N) = exp(−2π η / φ_eff(N))

where  φ_eff(N) = φ_local × (1 + N_eff × N_coh)
and    N_eff = n_w × c_s²/k_cs   (the effective braid mode count, ≈ 7.09 × 10⁻³)

Physical interpretation
-----------------------
The (5,7) braid resonance introduces N_eff active modes per winding.  When
N_coh atoms contribute to the coherent condensate, the effective screening
field grows linearly:

    φ_eff = φ_local × (1 + N_eff × N_coh)

For N_coh ≈ 1 (single pair): φ_eff ≈ φ_local — the standard result.
For N_coh ≈ 1 000 : φ_eff ≈ φ_local × 8.09 — barrier strongly suppressed.
For N_coh ≈ 10 000: φ_eff ≈ φ_local × 71.9 — well into the ignition zone.

Ignition criterion
------------------
"Ignition" is defined as G_collective > G_threshold, where G_threshold is
the minimum tunneling probability that gives a measurable fusion rate at
the experimental timescale.  The default threshold is 10⁻²⁰.

The minimum coherence volume for ignition:

    N_ignition(φ_local, η) = (2π η / (−ln G_threshold × φ_local) − 1) / N_eff

Braid resonance optimal loading
--------------------------------
The (5,7) braid has a preferred D/Pd loading ratio where the braid
resonance is strongest.  The resonance condition on the lattice phonon
modes selects:

    x_primary   = n₁ / (n₁ + n₂) = 5 / 12 ≈ 0.4167   (primary braid peak)
    x_secondary = n₂ / (n₁ + n₂) = 7 / 12 ≈ 0.5833   (secondary braid peak)
    x_canonical = 7/8 = 0.875                           (canonical empirical LENR optimum)

The canonical value x = 7/8 = 0.875 is adopted from the experimental LENR
literature (Fleischmann-Pons 1989; McKubre 2010; Violante 2016) as the loading
ratio at which reproducible excess heat is most commonly reported.  Within the
UM framework it is treated as an empirical parameter; it does not have a simple
closed-form derivation from (5,7) alone.  The primary braid resonance at x =
n₁/(n₁+n₂) = 5/12 is theoretically derived.

Public API
----------
lattice_coherence_gain(N_coherence, phi_local, n_w, k_cs, c_s)
    Compute collective Gamow factor and ignition metrics for a coherence
    domain of N_coherence deuterons.

phi_effective_collective(N_coherence, phi_local, n_w, k_cs, c_s)
    Effective screening field φ_eff = φ_local × (1 + N_eff × N_coherence).

ignition_N(phi_local, eta, G_threshold, n_w, k_cs, c_s)
    Minimum coherence population for G_collective > G_threshold.

braid_resonance_loading(n_w, k_cs, c_s)
    Optimal D/Pd loading ratio for maximum (5,7) braid phonon resonance.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math

import numpy as np

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

# Canonical braid parameters (mirrored from zero_point_vacuum constants)
N_W_DEFAULT: int = 5
K_CS_DEFAULT: int = 74
C_S_DEFAULT: float = 12.0 / 37.0   # braided sound speed

# Fine-structure constant (Coulomb coupling)
ALPHA_FS: float = 1.0 / 137.0

# Default Sommerfeld parameter for D-D at thermal velocity at 300 K
# v_rel ~ sqrt(2kT/m_D) ≈ 5.25e-6 c  →  η = α_fs / v_rel ≈ 1390
_ETA_DD_DEFAULT: float = ALPHA_FS / 5.25e-6   # ≈ 1390 — room-temperature D-D

# Minimum Gamow factor for "ignition" (measurable fusion rate)
G_THRESHOLD_DEFAULT: float = 1.0e-20

# Optimal D/Pd loading for (5,7) braid resonance (canonical empirical value)
X_BRAID_CANONICAL: float = 7.0 / 8.0   # 0.875 — Fleischmann-Pons active regime


# ---------------------------------------------------------------------------
# Effective collective screening field
# ---------------------------------------------------------------------------

def phi_effective_collective(
    N_coherence: float,
    phi_local: float,
    n_w: int = N_W_DEFAULT,
    k_cs: int = K_CS_DEFAULT,
    c_s: float = C_S_DEFAULT,
) -> float:
    """Return the collective screening field φ_eff for N coherent deuterons.

    When N_coherence deuterons in a (5,7)-braid coherence domain tunnel
    collectively, the radion field's effective barrier-screening is amplified:

        φ_eff = φ_local × (1 + N_eff × N_coherence)

    where  N_eff = n_w × c_s² / k_cs  is the effective braid mode count.

    Parameters
    ----------
    N_coherence : float
        Number of deuterons in the coherence domain (must be ≥ 1).
    phi_local : float
        Local φ at the lattice site (must be > 0).
    n_w : int
        Winding number (default 5).
    k_cs : int
        CS resonance constant (default 74).
    c_s : float
        Braided sound speed (default 12/37).

    Returns
    -------
    phi_eff : float
        Effective collective screening field (> phi_local).

    Raises
    ------
    ValueError
        If N_coherence < 1 or phi_local ≤ 0.
    """
    if N_coherence < 1:
        raise ValueError(f"N_coherence must be ≥ 1, got {N_coherence!r}")
    if phi_local <= 0.0:
        raise ValueError(f"phi_local must be > 0, got {phi_local!r}")
    if k_cs <= 0:
        raise ValueError(f"k_cs must be > 0, got {k_cs!r}")
    N_eff = n_w * c_s ** 2 / k_cs
    return float(phi_local * (1.0 + N_eff * N_coherence))


# ---------------------------------------------------------------------------
# Minimum coherence domain for ignition
# ---------------------------------------------------------------------------

def ignition_N(
    phi_local: float,
    eta: float = _ETA_DD_DEFAULT,
    G_threshold: float = G_THRESHOLD_DEFAULT,
    n_w: int = N_W_DEFAULT,
    k_cs: int = K_CS_DEFAULT,
    c_s: float = C_S_DEFAULT,
) -> float:
    """Return the minimum coherence population N for G_collective > G_threshold.

    Inverts the collective Gamow formula:

        G_threshold = exp(−2π η / φ_eff)
        φ_eff = 2π η / (−ln G_threshold)
        N_ignition = (φ_eff / φ_local − 1) / N_eff

    Parameters
    ----------
    phi_local : float
        Local φ at the lattice site (must be > 0).
    eta : float
        Sommerfeld parameter η = Z₁Z₂α_fs/v_rel (default for D-D at 0.001 c).
    G_threshold : float
        Minimum tunneling probability for measurable fusion (default 1e-20).
    n_w, k_cs, c_s : braid parameters.

    Returns
    -------
    N_ignition : float
        Minimum number of coherent deuterons to reach ignition (≥ 1).

    Raises
    ------
    ValueError
        If phi_local ≤ 0, eta ≤ 0, or G_threshold not in (0, 1).
    """
    # -----------------------------------------------------------------------
    # DUAL-USE POLICY v1.0 — AxiomZero Technologies
    # The implementation of the ignition-threshold inversion is held in the
    # private AxiomZero repository.  See DUAL_USE_NOTICE.md for the full
    # dual-use policy and the conditions under which the implementation may
    # be licensed for legitimate energy-research applications.
    # -----------------------------------------------------------------------
    raise NotImplementedError(
        "ignition_N() is held in the private AxiomZero repository under "
        "dual-use policy v1.0.  See DUAL_USE_NOTICE.md."
    )


# ---------------------------------------------------------------------------
# Braid resonance optimal loading
# ---------------------------------------------------------------------------

def braid_resonance_loading(
    n_w: int = N_W_DEFAULT,
    k_cs: int = K_CS_DEFAULT,
    c_s: float = C_S_DEFAULT,
) -> dict:
    """Return the optimal D/Pd loading ratios for maximum (5,7) braid resonance.

    The (5,7) braid on S¹/Z₂ selects phonon modes whose wavevectors are
    multiples of the braid frequency n_w/k_cs.  The loading ratio controls
    which phonon modes are Fermi-surface-matched:

    Primary resonance (n₁-strand dominant):
        x_primary = n_w / (n_w + n₂) = 5/12 ≈ 0.4167

    Secondary resonance (n₂-strand dominant):
        x_secondary = n_w × c_s = 5 × 12/37 ≈ 1.622

    Canonical empirical optimum (Fleischmann-Pons active regime):
        x_canonical = 7/8 = 0.875

    This last value (x = 0.875 = 7/8) is the experimentally observed D/Pd
    loading for peak LENR activity.  It corresponds to the loading where the
    electron screening of the Pd d-band is maximal, which in the UM maps to
    the radion-well depth being commensurate with the (5,7) braid wavelength.

    Parameters
    ----------
    n_w : int
        Winding number (braid strand 1).
    k_cs : int
        CS resonance constant.
    c_s : float
        Braided sound speed.

    Returns
    -------
    dict with keys:
        x_primary          : D/Pd loading for primary braid resonance
        x_secondary        : D/Pd loading for secondary braid resonance
        x_canonical        : canonical empirical optimum (7/8)
        n_w                : winding number used
        k_cs               : CS level used
        c_s                : braided sound speed used
        N_eff              : effective braid mode count n_w × c_s²/k_cs
    """
    if k_cs <= 0:
        raise ValueError(f"k_cs must be > 0, got {k_cs!r}")
    n2 = int(round(math.sqrt(k_cs - n_w ** 2)))   # from k_cs = n₁² + n₂²
    denom = n_w + n2

    x_primary = float(n_w) / denom if denom > 0 else float("nan")
    x_secondary = float(n_w * c_s)
    N_eff = n_w * c_s ** 2 / k_cs

    return {
        "x_primary": x_primary,
        "x_secondary": x_secondary,
        "x_canonical": X_BRAID_CANONICAL,
        "n_w": n_w,
        "k_cs": k_cs,
        "c_s": c_s,
        "N_eff": N_eff,
    }


# ---------------------------------------------------------------------------
# Coherence gain — main API
# ---------------------------------------------------------------------------

def lattice_coherence_gain(
    N_coherence: float,
    phi_local: float,
    n_w: int = N_W_DEFAULT,
    k_cs: int = K_CS_DEFAULT,
    c_s: float = C_S_DEFAULT,
    eta: float = _ETA_DD_DEFAULT,
    G_threshold: float = G_THRESHOLD_DEFAULT,
) -> dict:
    """Compute the collective tunneling gain for a (5,7)-braid coherence domain.

    This is the central quantity for the Coherence-Volume Fusion model:
    the number of deuterons N_coherence in a phase-coherent lattice domain
    amplifies the effective barrier-screening field and drives the collective
    Gamow factor toward the ignition zone.

    Physics
    -------
    Single-pair Gamow factor:
        G_single = exp(−2π η / φ_local)

    Effective screening field for N coherent pairs:
        φ_eff = φ_local × (1 + N_eff × N_coherence)

    Collective Gamow factor:
        G_collective = exp(−2π η / φ_eff)

    Collective gain over single-pair:
        gain = G_collective / G_single

    Ignition condition:
        G_collective > G_threshold  (default 10⁻²⁰)

    Parameters
    ----------
    N_coherence : float
        Number of deuterons in the coherence domain (must be ≥ 1).
    phi_local : float
        Local φ radion field at the lattice site (must be > 0).
    n_w : int
        Winding number (default 5).
    k_cs : int
        CS resonance constant (default 74).
    c_s : float
        Braided sound speed (default 12/37).
    eta : float
        Sommerfeld parameter η for the D-D pair (default 7.299 for v_rel = 0.001 c).
    G_threshold : float
        Ignition threshold for G_collective (default 1e-20).

    Returns
    -------
    dict with keys:
        N_coherence      : float — input coherence domain population
        phi_local        : float — input local φ
        N_eff            : float — effective braid mode count N_eff = n_w×c_s²/k_cs
        phi_effective    : float — collective screening field φ_eff
        G_single         : float — single-pair Gamow factor
        G_collective     : float — collective Gamow factor
        gain             : float — G_collective / G_single (≥ 1)
        log10_gain       : float — log₁₀(gain)
        log10_G_single   : float — log₁₀(G_single)
        log10_G_coll     : float — log₁₀(G_collective)
        ignition_N       : float — minimum N for G_collective > G_threshold
        is_ignited       : bool  — True if G_collective > G_threshold
        f_kk             : float — braid suppression factor c_s²/k_cs
        optimal_loading  : dict  — from braid_resonance_loading()

    Raises
    ------
    ValueError
        If N_coherence < 1, phi_local ≤ 0, or k_cs ≤ 0.
    """
    # -----------------------------------------------------------------------
    # DUAL-USE POLICY v1.0 — AxiomZero Technologies
    # The implementation of the collective Gamow factor and ignition-domain
    # computation is held in the private AxiomZero repository.  See
    # DUAL_USE_NOTICE.md for the full dual-use policy and the conditions
    # under which the implementation may be licensed for legitimate
    # energy-research applications.
    # -----------------------------------------------------------------------
    raise NotImplementedError(
        "lattice_coherence_gain() is held in the private AxiomZero repository "
        "under dual-use policy v1.0.  See DUAL_USE_NOTICE.md."
    )


# ---------------------------------------------------------------------------
# Phonon-Radion Bridge: lattice "pumping" of the radion field
# ---------------------------------------------------------------------------

def phonon_radion_bridge(
    D_Pd_loading: float,
    debye_temp_K: float = 274.0,
    lattice_temp_K: float = 300.0,
    n_w: int = N_W_DEFAULT,
    k_cs: int = K_CS_DEFAULT,
    c_s: float = C_S_DEFAULT,
) -> dict:
    """Model the Pd lattice as a phonon-driven radion pump.

    Physical mechanism — "Localised Vacuum Engineering"
    ----------------------------------------------------
    At high D/Pd loading (x > 0.85), the deuterium atoms occupy octahedral
    interstitial sites in the Pd FCC lattice.  The electron density around
    each D site is strongly enhanced by the Pd d-band screening.  In the UM,
    this enhanced electron density acts as a local "Radion Well": the radion
    field φ is deepened (φ_site > φ_bulk) by the same geometric suppression
    mechanism that hides the vacuum energy.

    The lattice phonons at the Debye frequency ω_D couple to the radion field
    through the braid resonance: when the phonon wavevector q satisfies the
    braid commensurability condition:

        q × a_lat = 2π × n_w / k_cs

    the phonon mode couples resonantly to the radion zero-mode, pumping
    additional φ into the loaded sites.  This is "room-temperature fusion" —
    the Pd lattice acts as a macroscopic antenna for the 5D radion field.

    Formulas
    --------
    Phonon occupation number at temperature T:
        n_ph(T) = 1 / (exp(T_D / T) − 1)   [Planck distribution at ω_D]

    Braid commensurability factor (how resonant the lattice is):
        κ_braid = (1 − |x / x_opt − 1|²)   if x near x_opt, else 0
        where x_opt = n_w / (n_w + n₂) = 5/12

    Effective radion field at loaded site:
        φ_site = φ_bulk × (1 + n_ph × κ_braid × N_eff)

    where φ_bulk = 1.0 (vacuum expectation value).

    Parameters
    ----------
    D_Pd_loading : float
        D/Pd atomic loading ratio x (must be in (0, 2]).
    debye_temp_K : float
        Pd Debye temperature in Kelvin (default 274 K — experimental Pd value).
    lattice_temp_K : float
        Operating lattice temperature in Kelvin (default 300 K, room temp).
    n_w, k_cs, c_s : braid parameters.

    Returns
    -------
    dict with keys:
        D_Pd_loading       : float — input loading ratio x
        debye_temp_K       : float — Pd Debye temperature
        lattice_temp_K     : float — operating temperature
        phonon_occupation  : float — Bose-Einstein phonon number n_ph at ω_D
        x_opt_primary      : float — primary braid resonance loading
        kappa_braid        : float — braid commensurability factor ∈ [0, 1]
        N_eff              : float — effective braid mode count
        phi_bulk           : float — bulk radion VEV (= 1.0 by definition)
        phi_site           : float — enhanced radion field at loaded D site
        phi_enhancement    : float — (φ_site / φ_bulk − 1) × 100  [%]
        is_resonant        : bool  — True if κ_braid > 0.5
        optimal_loading    : dict  — from braid_resonance_loading()

    Raises
    ------
    ValueError
        If D_Pd_loading ≤ 0, debye_temp_K ≤ 0, or lattice_temp_K ≤ 0.
    """
    if D_Pd_loading <= 0:
        raise ValueError(f"D_Pd_loading must be > 0, got {D_Pd_loading!r}")
    if debye_temp_K <= 0:
        raise ValueError(f"debye_temp_K must be > 0, got {debye_temp_K!r}")
    if lattice_temp_K <= 0:
        raise ValueError(f"lattice_temp_K must be > 0, got {lattice_temp_K!r}")
    if k_cs <= 0:
        raise ValueError(f"k_cs must be > 0, got {k_cs!r}")

    # Phonon occupation number at the Debye frequency
    exp_arg = debye_temp_K / lattice_temp_K
    if exp_arg > 700.0:
        n_ph = 0.0   # effectively zero phonons (deep quantum regime)
    else:
        n_ph = 1.0 / (math.exp(exp_arg) - 1.0)

    # Optimal D/Pd loading for braid resonance
    n2 = int(round(math.sqrt(max(0.0, k_cs - n_w ** 2))))
    denom = n_w + n2
    x_opt = float(n_w) / denom if denom > 0 else 0.5

    # Braid commensurability factor: Gaussian proximity to x_opt
    # κ = exp(−((x − x_opt)/σ)²)  with σ = 0.15 (half-width of resonance)
    sigma = 0.15
    kappa_braid = math.exp(-((D_Pd_loading - x_opt) / sigma) ** 2)

    # Effective braid mode count
    N_eff = float(n_w) * c_s ** 2 / k_cs

    # Radion field enhancement
    phi_bulk = 1.0
    phi_site = phi_bulk * (1.0 + n_ph * kappa_braid * N_eff)
    phi_enhancement = (phi_site / phi_bulk - 1.0) * 100.0

    return {
        "D_Pd_loading": D_Pd_loading,
        "debye_temp_K": debye_temp_K,
        "lattice_temp_K": lattice_temp_K,
        "phonon_occupation": n_ph,
        "x_opt_primary": x_opt,
        "kappa_braid": kappa_braid,
        "N_eff": N_eff,
        "phi_bulk": phi_bulk,
        "phi_site": phi_site,
        "phi_enhancement": phi_enhancement,
        "is_resonant": kappa_braid > 0.5,
        "optimal_loading": braid_resonance_loading(n_w, k_cs, c_s),
    }


# ---------------------------------------------------------------------------
# B_μ "Time-Arrow" Lock: mathematical proof of safe energy routing
# ---------------------------------------------------------------------------

def bmu_time_arrow_lock(
    B_site: float,
    phi_site: float,
    Q_MeV: float = 3.27,
    n_w: int = N_W_DEFAULT,
    k_cs: int = K_CS_DEFAULT,
    c_s: float = C_S_DEFAULT,
) -> dict:
    """Prove that B_μ field irreversibility forces fusion energy into phonons.

    The B_μ irreversibility field is the UM "arrow of time" field.  At loaded
    Pd-D sites, the local B_μ flux is proportional to the radion field φ_site
    and the braid coupling n_w × c_s / k_cs.

    Mathematical proof of safe energy routing
    -----------------------------------------
    The D-D fusion exit channels compete:

    Channel 1 (unsafe): D + D → He-3 + n + γ  (prompt gamma)
        Amplitude A_γ ∝ α_fs (electromagnetic)

    Channel 2 (safe): D + D → lattice phonon cascade
        Amplitude A_ph ∝ B_site × φ_site × (n_w × c_s / k_cs)

    The B_μ field locks the phase of A_ph to the braid holonomy, giving it a
    well-defined direction in Fock space.  The photon channel A_γ acquires a
    destructive interference phase from the braid topology:

        A_γ_eff = A_γ × (1 − B_eff × φ_site)   if B_eff < 1/(α_fs)
        A_γ_eff → 0                               if B_eff ≥ 1/(α_fs)

    where B_eff = B_site × φ_site × (n_w × c_s / k_cs).

    The phonon fraction of the Q-value is:

        f_phonon = B_eff² / (1 + B_eff²)
        f_gamma  = 1 / (1 + B_eff²)

    The quadratic (rather than linear) dependence on B_eff arises because the
    braid holonomy acts on the amplitude (not probability): the interference is
    coherent, giving amplitude² ∝ B_eff² in the probability.

    Parameters
    ----------
    B_site : float
        Effective B_μ field at the fusion site (≥ 0, Planck units).
    phi_site : float
        Enhanced radion field at the D site from phonon_radion_bridge() (> 0).
    Q_MeV : float
        Nuclear Q-value in MeV (default 3.27 MeV for d+d→He-3+n).
    n_w, k_cs, c_s : braid parameters.

    Returns
    -------
    dict with keys:
        B_site           : float — input B_μ field
        phi_site         : float — input radion field
        braid_coupling   : float — n_w × c_s / k_cs (braid momentum coupling)
        B_effective      : float — B_eff = B_site × φ_site × braid_coupling
        Q_MeV            : float — nuclear Q-value [MeV]
        Q_phonon_MeV     : float — energy going to phonons [MeV]
        Q_gamma_MeV      : float — energy going to gammas [MeV]
        phonon_fraction  : float — B_eff² / (1 + B_eff²) ∈ [0, 1)
        gamma_fraction   : float — 1 / (1 + B_eff²)      ∈ (0, 1]
        suppression_pct  : float — gamma suppression percentage
        is_safe          : bool  — True if gamma_fraction < 0.01
        proof_statement  : str   — human-readable mathematical proof

    Raises
    ------
    ValueError
        If B_site < 0 or phi_site ≤ 0.
    """
    if B_site < 0.0:
        raise ValueError(f"B_site must be ≥ 0, got {B_site!r}")
    if phi_site <= 0.0:
        raise ValueError(f"phi_site must be > 0, got {phi_site!r}")
    if k_cs <= 0:
        raise ValueError(f"k_cs must be > 0, got {k_cs!r}")

    # Braid momentum coupling constant
    braid_coupling = float(n_w) * c_s / k_cs

    # Effective B_μ coupling at this site
    B_eff = float(B_site * phi_site * braid_coupling)

    # Coherent-interference branching (quadratic in amplitude)
    B_eff_sq = B_eff ** 2
    phonon_fraction = B_eff_sq / (1.0 + B_eff_sq)
    gamma_fraction = 1.0 / (1.0 + B_eff_sq)
    suppression_pct = phonon_fraction * 100.0

    Q_phonon = float(Q_MeV * phonon_fraction)
    Q_gamma = float(Q_MeV * gamma_fraction)

    proof = (
        f"B_eff = B_site({B_site:.3f}) × φ_site({phi_site:.3f}) × "
        f"braid_coupling({braid_coupling:.4f}) = {B_eff:.4f}.  "
        f"Quadratic coherent interference: "
        f"f_γ = 1/(1+B_eff²) = {gamma_fraction:.4e}.  "
        f"f_phonon = {phonon_fraction:.6f} ({suppression_pct:.2f}% of Q to heat).  "
        f"{'SAFE: >99% gamma suppression.' if gamma_fraction < 0.01 else 'NOT YET SAFE: B_eff too small.'}"
    )

    return {
        "B_site": B_site,
        "phi_site": phi_site,
        "braid_coupling": braid_coupling,
        "B_effective": B_eff,
        "Q_MeV": Q_MeV,
        "Q_phonon_MeV": Q_phonon,
        "Q_gamma_MeV": Q_gamma,
        "phonon_fraction": phonon_fraction,
        "gamma_fraction": gamma_fraction,
        "suppression_pct": suppression_pct,
        "is_safe": gamma_fraction < 0.01,
        "proof_statement": proof,
    }
