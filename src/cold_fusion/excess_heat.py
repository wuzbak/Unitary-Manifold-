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
"""

from __future__ import annotations

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
    return float(tunneling_probability * v_rel / R_site)


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
    return float(N_active_sites * fusion_rate * Q_value)


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
    return float((cop_value - 1.0) * eta_thermal)


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
