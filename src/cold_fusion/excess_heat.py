# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/cold_fusion/excess_heat.py
==============================
Excess heat and energy balance for LENR — Pillar 15.

In the Unitary Manifold, the anomalous heat reported in electrolytic Pd/D
experiments arises from φ-enhanced D+D fusion events at coherent lattice sites.
Each fusion event releases a nuclear Q-value; the total excess power is the
product of the active-site count, the per-site fusion rate, and Q.

The Coefficient of Performance (COP) is the ratio of output thermal power to
electrical input power.  COP > 1 constitutes experimentally verifiable excess
heat.  The anomalous-heat signature measures how many standard deviations the
observed excess sits above the background fluctuation noise.

Theory summary
--------------
d+d → He-3 + n   Q = 3.27 MeV
d+d → T + p       Q = 4.03 MeV

Fusion rate per site:
    R = T · v_rel / R_site

Excess heat power:
    P_excess = N_active · R · Q

Coefficient of performance:
    COP = P_out / P_in

φ coherence enhancement factor:
    factor = (φ_local / φ_threshold)²  if φ_local > φ_threshold, else 0

B_μ coherence factor:
    C = 1 + B_strength · φ_local

Anomalous heat significance:
    σ = P_excess / sqrt(background_variance)

Public API
----------
dd_fusion_q_value()
    Q = 3.27 MeV in Joules.

dd_proton_branch_q_value()
    Q = 4.03 MeV in Joules.

fusion_rate_per_site(tunneling_probability, v_rel, R_site)
    R = T · v_rel / R_site.

excess_heat_power(N_active_sites, fusion_rate, Q_value)
    P = N · R · Q.

cop(P_out, P_in)
    COP = P_out / P_in; raises ValueError if P_in ≤ 0.

is_excess_heat(P_out, P_in, threshold)
    True if P_out / P_in > threshold.

phi_coherent_enhancement(N_sites, phi_local, phi_threshold)
    factor = (φ_local/φ_threshold)² · N_sites if φ > φ_threshold, else 0.

b_field_coherence_factor(B_strength, phi_local)
    C = 1 + B_strength · φ_local.

energy_per_event(Q_value)
    E = Q_value  (alias for clarity).

cumulative_heat(fusion_rates, Q_value, dt)
    np.cumsum(fusion_rates) * Q_value * dt.

heat_to_electrical_efficiency(cop, eta_thermal)
    P_elec = (cop − 1) · eta_thermal.

anomalous_heat_signature(P_excess, background_variance)
    σ = P_excess / sqrt(background_variance).

calculate_energy_branching_ratio(B_site, phi_local, alpha_fs)
    Returns phonon/gamma branching fractions from B_μ momentum-sink mechanism.
    phonon_fraction = B_eff / (1 + B_eff),  B_eff = B_site × φ_local.
    is_safe is True when gamma_fraction < 0.01 (>99% gamma suppression).
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

import numpy as np


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_EV_TO_JOULE: float = 1.6e-19        # eV → Joules conversion
_Q_DD_NEUTRON_EV: float = 3.27e6     # d+d→He-3+n Q-value in eV
_Q_DD_PROTON_EV: float = 4.03e6      # d+d→T+p Q-value in eV
_NUMERICAL_EPSILON: float = 1e-30


# ---------------------------------------------------------------------------
# Q-values
# ---------------------------------------------------------------------------

def dd_fusion_q_value() -> float:
    """Q-value for the d+d → He-3 + n neutron branch.

    The dominant exothermic channel of deuterium–deuterium fusion releases:

        Q = 3.27 MeV = 3.27 × 10⁶ eV = 5.232 × 10⁻¹³ J

    Returns
    -------
    Q : float — Q-value in Joules
    """
    return float(_Q_DD_NEUTRON_EV * _EV_TO_JOULE)


def dd_proton_branch_q_value() -> float:
    """Q-value for the d+d → T + p proton branch.

    The second major exothermic channel of D–D fusion releases:

        Q = 4.03 MeV = 4.03 × 10⁶ eV = 6.448 × 10⁻¹³ J

    Returns
    -------
    Q : float — Q-value in Joules
    """
    return float(_Q_DD_PROTON_EV * _EV_TO_JOULE)


# ---------------------------------------------------------------------------
# Fusion rate per site
# ---------------------------------------------------------------------------

def fusion_rate_per_site(
    tunneling_probability: float,
    v_rel: float,
    R_site: float,
) -> float:
    """Fusion event rate per active lattice site.

    Combines the φ-enhanced tunneling probability with the classical attempt
    frequency v_rel / R_site:

        R = T · v_rel / R_site

    Parameters
    ----------
    tunneling_probability : float — T in [0, 1] (φ-enhanced Gamow factor)
    v_rel                 : float — relative velocity of the D pair (must be > 0)
    R_site                : float — inter-nuclear separation at the site (must be > 0)

    Returns
    -------
    R : float — fusion rate per site (events per Planck time)

    Raises
    ------
    ValueError
        If v_rel ≤ 0 or R_site ≤ 0.
    """
    if v_rel <= 0.0:
        raise ValueError(f"v_rel must be > 0, got {v_rel!r}")
    if R_site <= 0.0:
        raise ValueError(f"R_site must be > 0, got {R_site!r}")
    # -----------------------------------------------------------------------
    # DUAL-USE POLICY v1.0 — AxiomZero Technologies
    # The per-site absolute fusion rate is the key factor in computing device
    # power output.  Implementation withheld.  See DUAL_USE_NOTICE.md.
    # -----------------------------------------------------------------------
    raise NotImplementedError(
        "fusion_rate_per_site() is held in the private AxiomZero repository "
        "under dual-use policy v1.0.  See DUAL_USE_NOTICE.md."
    )


# ---------------------------------------------------------------------------
# Excess heat power
# ---------------------------------------------------------------------------

def excess_heat_power(
    N_active_sites: float,
    fusion_rate: float,
    Q_value: float,
) -> float:
    """Total excess heat power from LENR fusion events.

    The macroscopic excess power is the sum over all active lattice sites of
    the per-site fusion rate times the energy released per event:

        P_excess = N_active · R · Q

    Parameters
    ----------
    N_active_sites : float — number of active lattice sites (must be ≥ 0)
    fusion_rate    : float — per-site fusion rate (must be ≥ 0)
    Q_value        : float — energy released per fusion event in Joules

    Returns
    -------
    P : float — excess heat power in Watts (or Q-unit/time)

    Raises
    ------
    ValueError
        If N_active_sites < 0 or fusion_rate < 0.
    """
    if N_active_sites < 0.0:
        raise ValueError(f"N_active_sites must be ≥ 0, got {N_active_sites!r}")
    if fusion_rate < 0.0:
        raise ValueError(f"fusion_rate must be ≥ 0, got {fusion_rate!r}")
    # -----------------------------------------------------------------------
    # DUAL-USE POLICY v1.0 — AxiomZero Technologies
    # The total excess heat power from N active sites is the primary figure
    # of merit for LENR device design.  Implementation withheld.
    # See DUAL_USE_NOTICE.md.
    # -----------------------------------------------------------------------
    raise NotImplementedError(
        "excess_heat_power() is held in the private AxiomZero repository "
        "under dual-use policy v1.0.  See DUAL_USE_NOTICE.md."
    )


# ---------------------------------------------------------------------------
# Coefficient of performance
# ---------------------------------------------------------------------------

def cop(
    P_out: float,
    P_in: float,
) -> float:
    """Coefficient of performance for an LENR heat source.

    The COP is the ratio of total output thermal power to input electrical
    power:

        COP = P_out / P_in

    A COP > 1 means the device produces more heat than the electrical energy
    supplied — the surplus comes from the nuclear Q-values.

    Parameters
    ----------
    P_out : float — total output thermal power (Watts)
    P_in  : float — electrical input power (must be > 0, Watts)

    Returns
    -------
    COP : float — coefficient of performance (≥ 0)

    Raises
    ------
    ValueError
        If P_in ≤ 0.
    """
    if P_in <= 0.0:
        raise ValueError(f"P_in must be > 0, got {P_in!r}")
    return float(P_out / P_in)


# ---------------------------------------------------------------------------
# Excess heat flag
# ---------------------------------------------------------------------------

def is_excess_heat(
    P_out: float,
    P_in: float,
    threshold: float = 1.0,
) -> bool:
    """True if the output power exceeds input power by the given threshold ratio.

    Returns True when P_out / P_in > threshold, i.e. when the device is
    producing anomalous heat above the input level (or above any desired
    COP threshold).

    Parameters
    ----------
    P_out      : float — total output thermal power
    P_in       : float — electrical input power (must be > 0)
    threshold  : float — COP threshold (default 1.0; excess means > 1)

    Returns
    -------
    excess : bool — True if COP > threshold

    Raises
    ------
    ValueError
        If P_in ≤ 0.
    """
    return bool(cop(P_out, P_in) > threshold)


# ---------------------------------------------------------------------------
# φ coherent enhancement factor
# ---------------------------------------------------------------------------

def phi_coherent_enhancement(
    N_sites: float,
    phi_local: float,
    phi_threshold: float = 0.5,
) -> float:
    """Coherent φ-enhancement factor for the active-site count.

    When the local φ field exceeds a threshold, the tunneling condensate
    becomes phase-coherent and the effective number of contributing sites is
    amplified quadratically:

        factor = N_sites · (φ_local / φ_threshold)²   if φ_local > φ_threshold
        factor = 0                                     otherwise

    Parameters
    ----------
    N_sites       : float — number of loaded lattice sites (must be ≥ 0)
    phi_local     : float — local φ at the site (must be > 0)
    phi_threshold : float — coherence onset threshold (default 0.5, must be > 0)

    Returns
    -------
    factor : float — coherently enhanced effective site count (≥ 0)

    Raises
    ------
    ValueError
        If N_sites < 0, phi_local ≤ 0, or phi_threshold ≤ 0.
    """
    if N_sites < 0.0:
        raise ValueError(f"N_sites must be ≥ 0, got {N_sites!r}")
    if phi_local <= 0.0:
        raise ValueError(f"phi_local must be > 0, got {phi_local!r}")
    if phi_threshold <= 0.0:
        raise ValueError(f"phi_threshold must be > 0, got {phi_threshold!r}")
    if phi_local > phi_threshold:
        return float(N_sites * (phi_local / phi_threshold) ** 2)
    return 0.0


# ---------------------------------------------------------------------------
# B_μ coherence factor
# ---------------------------------------------------------------------------

def b_field_coherence_factor(
    B_strength: float,
    phi_local: float,
) -> float:
    """Constructive interference factor from the B_μ irreversibility field.

    The B_μ field and the φ scalar interfere constructively at loaded sites,
    boosting the effective tunneling amplitude:

        C = 1 + B_strength · φ_local

    For B_strength = 0 the factor is unity (no field applied).  Higher B or
    larger φ increases the coherent enhancement.

    Parameters
    ----------
    B_strength : float — local |B_μ| field strength (must be ≥ 0)
    phi_local  : float — local φ at the site (must be > 0)

    Returns
    -------
    C : float — coherence enhancement factor (≥ 1)

    Raises
    ------
    ValueError
        If B_strength < 0 or phi_local ≤ 0.
    """
    if B_strength < 0.0:
        raise ValueError(f"B_strength must be ≥ 0, got {B_strength!r}")
    if phi_local <= 0.0:
        raise ValueError(f"phi_local must be > 0, got {phi_local!r}")
    return float(1.0 + B_strength * phi_local)


# ---------------------------------------------------------------------------
# Energy per event
# ---------------------------------------------------------------------------

def energy_per_event(
    Q_value: float,
) -> float:
    """Energy released per fusion event (alias for Q_value).

    Thin convenience wrapper that makes the physical intent explicit in calling
    code: each fusion event deposits exactly Q_value of energy into the lattice.

    Parameters
    ----------
    Q_value : float — nuclear Q-value (Joules or Planck units)

    Returns
    -------
    E : float — energy deposited per event
    """
    return float(Q_value)


# ---------------------------------------------------------------------------
# Cumulative heat
# ---------------------------------------------------------------------------

def cumulative_heat(
    fusion_rates: np.ndarray,
    Q_value: float,
    dt: float,
) -> np.ndarray:
    """Cumulative heat deposited over a time series of fusion rates.

    Integrates the instantaneous excess power over time via a simple
    cumulative sum:

        H[t] = (Σ_{t'≤t} R[t']) · Q · dt

    Parameters
    ----------
    fusion_rates : array-like, shape (N,) — per-site fusion rate at each time step
    Q_value      : float — energy per fusion event
    dt           : float — time step size (must be > 0)

    Returns
    -------
    H : ndarray, shape (N,) — cumulative heat deposited up to each time step

    Raises
    ------
    ValueError
        If dt ≤ 0.
    """
    if dt <= 0.0:
        raise ValueError(f"dt must be > 0, got {dt!r}")
    rates = np.asarray(fusion_rates, dtype=float)
    return np.cumsum(rates) * Q_value * dt


# ---------------------------------------------------------------------------
# Heat-to-electrical efficiency
# ---------------------------------------------------------------------------

def heat_to_electrical_efficiency(
    cop_value: float,
    eta_thermal: float = 0.35,
) -> float:
    """Fraction of input power recoverable as electricity from excess heat.

    A heat engine operating at efficiency η_thermal converts the excess
    thermal power (COP − 1) times P_in into electricity.  Normalised per
    unit of input power:

        P_elec / P_in = (COP − 1) · η_thermal

    A COP of exactly 1 means no net electricity; COP > 1 means positive
    electrical output per unit input.

    Parameters
    ----------
    cop_value    : float — coefficient of performance (must be ≥ 0)
    eta_thermal  : float — Carnot/thermal conversion efficiency (default 0.35;
                           must be in (0, 1])

    Returns
    -------
    efficiency : float — normalised electrical output per unit input power

    Raises
    ------
    ValueError
        If cop_value < 0 or eta_thermal not in (0, 1].
    """
    if cop_value < 0.0:
        raise ValueError(f"cop_value must be ≥ 0, got {cop_value!r}")
    if not (0.0 < eta_thermal <= 1.0):
        raise ValueError(f"eta_thermal must be in (0, 1], got {eta_thermal!r}")
    # -----------------------------------------------------------------------
    # DUAL-USE POLICY v1.0 — AxiomZero Technologies
    # Converting LENR excess heat to net electrical power is the final step
    # in engineering a device.  Implementation withheld.
    # See DUAL_USE_NOTICE.md.
    # -----------------------------------------------------------------------
    raise NotImplementedError(
        "heat_to_electrical_efficiency() is held in the private AxiomZero "
        "repository under dual-use policy v1.0.  See DUAL_USE_NOTICE.md."
    )


# ---------------------------------------------------------------------------
# Anomalous heat signature
# ---------------------------------------------------------------------------

def anomalous_heat_signature(
    P_excess: float,
    background_variance: float,
) -> float:
    """Statistical significance of the anomalous heat signal in sigma units.

    The number of standard deviations by which the excess power exceeds the
    background noise floor:

        σ = P_excess / sqrt(background_variance)

    A value σ > 3 is conventionally regarded as a significant signal; σ > 5
    is discovery-level evidence.

    Parameters
    ----------
    P_excess            : float — measured excess heat power
    background_variance : float — variance of the background power fluctuations
                          (must be > 0)

    Returns
    -------
    sigma : float — signal significance in units of standard deviations

    Raises
    ------
    ValueError
        If background_variance ≤ 0.
    """
    if background_variance <= 0.0:
        raise ValueError(
            f"background_variance must be > 0, got {background_variance!r}"
        )
    return float(P_excess / np.sqrt(background_variance))


# ---------------------------------------------------------------------------
# B_μ energy branching ratio (phonon vs gamma)
# ---------------------------------------------------------------------------

def calculate_energy_branching_ratio(
    B_site: float,
    phi_local: float,
    alpha_fs: float = 1.0 / 137.0,
) -> dict:
    """Calculate the phonon/gamma branching ratio via the B_μ momentum-sink mechanism.

    Physical mechanism
    ------------------
    In standard D-D fusion the nuclear Q-value exits as free kinetic energy of
    the products (neutron/proton + He-3/Tritium), which quickly scatter and
    produce secondary gammas and fast neutrons — the "deadly radiation" problem.

    In the Unitary Manifold, the B_μ irreversibility field acts as a
    **momentum sink**: it couples to the outgoing momenta of the fusion products
    and distributes them into lattice phonon modes *before* a photon can be
    emitted.  The phonon coupling rate is boosted by the local radion field φ,
    which concentrates at the loaded D-occupied sites.

    Rate model
    ----------
    The photon (gamma) emission rate per unit energy is set by the fine-structure
    constant (classical electromagnetic decay):

        Γ_γ = α_fs   [in natural units, per energy unit]

    The B_μ-induced phonon coupling rate is amplified by the local field product
    B_site × φ_local (both dimensionless in Planck units):

        Γ_ph = B_site × φ_local × Γ_γ

    The total decay width is:

        Γ_total = Γ_γ + Γ_ph = Γ_γ × (1 + B_eff)

    where  B_eff = B_site × φ_local  is the effective B_μ coupling.

    Branching fractions
    -------------------
        f_phonon = Γ_ph / Γ_total = B_eff / (1 + B_eff)
        f_gamma  = Γ_γ  / Γ_total = 1    / (1 + B_eff)

    For B_eff ≫ 1 (strong B_μ coupling), f_phonon → 1 and f_gamma → 0:
    essentially all fusion energy becomes heat rather than radiation.

    Safety threshold
    ----------------
    The prompt-gamma suppression is considered safe (below detectable harm
    threshold for a Pd-D cell) when:

        f_gamma < 0.01   (>99% of energy goes to phonons)

    This requires  B_eff > 99, e.g. B_site = 1.0 with φ_local ≥ 99.

    Parameters
    ----------
    B_site : float
        Effective local B_μ field strength at the fusion site (≥ 0, Planck units).
        Computed via `src.cold_fusion.lattice.b_field_at_site`.
    phi_local : float
        Local φ radion field at the lattice site (must be > 0, Planck units).
        Computed via `src.cold_fusion.lattice.phi_at_lattice_site`.
    alpha_fs : float
        Fine-structure constant (default 1/137).  Sets the absolute gamma rate;
        cancels in the branching fractions but is included for completeness.

    Returns
    -------
    dict with keys:
        B_site          : float — input B_μ field strength
        phi_local       : float — input local φ field
        alpha_fs        : float — fine-structure constant used
        B_effective     : float — B_eff = B_site × φ_local (dimensionless coupling)
        Gamma_gamma     : float — photon emission rate (in α_fs units)
        Gamma_phonon    : float — phonon coupling rate (in α_fs units)
        Gamma_total     : float — total decay rate (in α_fs units)
        phonon_fraction : float — f_ph = B_eff / (1 + B_eff) ∈ [0, 1)
        gamma_fraction  : float — f_γ  = 1 / (1 + B_eff)    ∈ (0, 1]
        suppression_pct : float — gamma suppression = (1 − f_γ) × 100%
        is_safe         : bool  — True if f_γ < 0.01 (>99% gamma suppression)

    Raises
    ------
    ValueError
        If B_site < 0 or phi_local ≤ 0.
    """
    if B_site < 0.0:
        raise ValueError(f"B_site must be ≥ 0, got {B_site!r}")
    if phi_local <= 0.0:
        raise ValueError(f"phi_local must be > 0, got {phi_local!r}")

    # Effective B_μ coupling
    B_eff = float(B_site * phi_local)

    # Rate components (in units of alpha_fs)
    Gamma_gamma = float(alpha_fs)
    Gamma_phonon = float(B_eff * alpha_fs)
    Gamma_total = float((1.0 + B_eff) * alpha_fs)

    # Branching fractions
    phonon_fraction = float(B_eff / (1.0 + B_eff))
    gamma_fraction = float(1.0 / (1.0 + B_eff))
    suppression_pct = float((1.0 - gamma_fraction) * 100.0)

    return {
        "B_site": B_site,
        "phi_local": phi_local,
        "alpha_fs": alpha_fs,
        "B_effective": B_eff,
        "Gamma_gamma": Gamma_gamma,
        "Gamma_phonon": Gamma_phonon,
        "Gamma_total": Gamma_total,
        "phonon_fraction": phonon_fraction,
        "gamma_fraction": gamma_fraction,
        "suppression_pct": suppression_pct,
        "is_safe": gamma_fraction < 0.01,
    }
