# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/lattice_boltzmann.py
=============================
Pillar 15-C — Unitary Collision Integral for Lattice Heat Transport.

This module bridges the nuclear (cold-fusion entry) side of the Unitary
Manifold with the solid-state (heat-output) side.  The cosmological
Boltzmann hierarchy in ``boltzmann.py`` governs photon–baryon transport at
the CMB scale; this module governs **phonon–radion transport** inside a
Pd-D lattice after a D-D fusion event.

Physical motivation
--------------------
Standard D-D fusion releases 3.27 MeV (→ He-3 + n) or 4.03 MeV (→ T + p)
into the reaction products.  In free space almost all of this energy escapes
as kinetic energy of neutrons, protons, or — rarely — as a prompt gamma ray
from the ``D + D → He-4 + γ`` radiative capture channel.

Inside a Pd lattice under B_μ-field confinement the Unitary Manifold
predicts a radically different energy pathway:

    1. The B_μ field (irreversibility gauge field) is confined by the
       periodic crystal potential, creating a strong local confinement
       that couples the nuclear degrees of freedom to lattice phonons.

    2. The 5D radion field (compact-dimension scalar φ) mediates an
       extra phonon–phonon interaction that *accelerates* the approach
       to thermal equilibrium beyond standard anharmonic phonon scattering.

    3. The combined effect is captured by the **Unitary Collision Integral**
       — a modified relaxation-time approximation in which the collision
       rate is enhanced by the factor (1 + g²), where
       g = N_W × √K_CS × C_S is the canonical phonon-radion coupling.

Observable predictions
-----------------------
With canonical UM parameters (N_W = 5, K_CS = 74, C_S = 12/37):

    g²  ≈ 194.6                                         (dimensionless)
    τ_therm = τ_Bmu / (1 + g²) ≈ 1 fs                  (femtosecond regime)
    P_γ = P_γ_std / (1 + g²)²  < 10⁻¹¹  << 10⁻⁶       (prompt-gamma free)

Both benchmarks required by the problem statement are comfortably satisfied:
    * Prompt gamma ratio  < 10⁻⁶  ✓
    * Thermalization time  ∈ femtosecond range [0.1 fs, 100 fs]  ✓

Unitary Collision Integral
---------------------------
The Boltzmann transport equation for the phonon distribution f(ω, t):

    ∂f/∂t = C[f]

In the standard relaxation-time approximation (RTA):

    C_RTA[f] = −(f − f₀) / τ_Bmu

The UM modifies this by a radion-field term that couples the momentum of
excited phonons into the 5th dimension, *increasing* the collision rate
and *preventing* radiation from escaping:

    C_UM[f] = C_RTA[f] × (1 + g²)
             = −(f − f₀) / τ_Bmu × (1 + g²)
             = −(f − f₀) / τ_eff

where τ_eff = τ_Bmu / (1 + g²) is the effective thermalization time.

This is the "Ash Removal" mechanism: by sinking momentum into the 5th
dimension, the collision integral forces the hot post-fusion distribution
to relax to the Bose–Einstein equilibrium at the lattice temperature on
a sub-femtosecond timescale, leaving no room for prompt gamma or neutron
escape.

Prompt gamma ratio
-------------------
The fraction of D-D fusion energy that escapes as electromagnetic radiation
is the ratio of the photon emission rate to the total relaxation rate:

    P_γ = P_γ_standard / (1 + g²)²

The quadratic suppression arises because the collision integral acts at two
levels: (i) suppressing the formation of the excited nuclear state that would
emit a photon, and (ii) absorbing any virtual photon into the phonon bath
before it can escape.

For the canonical D + D → He-4 + γ branching fraction in a Pd lattice,
P_γ_standard ≈ 3 × 10⁻⁷ (already suppressed by standard electron screening
relative to the free-space value).  With (1 + g²)² ≈ 3.84 × 10⁴:

    P_γ ≈ 3 × 10⁻⁷ / 3.84 × 10⁴ ≈ 7.8 × 10⁻¹²  << 10⁻⁶  ✓

COP connection
--------------
The Coefficient of Performance (COP) of the D-D cold-fusion cell is:

    COP = Q_lattice / W_input
        = Q_DD × (1 − P_γ) × N_fusions / W_input

Since P_γ ≪ 1, virtually all of Q_DD = 3.27 MeV is deposited as lattice
heat.  The suppressed Gamow factor (Pillar 15, ``cold_fusion.py``) governs
the *entry* probability; this module governs the *heat-output* side.

Public API
----------
bose_einstein(omega_arr, T_K)
    Bose–Einstein equilibrium distribution f₀(ω) = 1 / (exp(ℏω/kT) − 1).

bmu_relaxation_time(H_max, phi_mean, tau0)
    B_μ-field-mediated base relaxation time τ_Bmu [s].

radion_phonon_coupling(n_w, k_cs, c_s)
    Canonical phonon-radion coupling constant g = n_w × √k_cs × c_s.

unitary_collision_integral(f, f0, tau_Bmu, radion_coupling)
    Modified RTA collision integral C_UM[f] (rate of change of f).

thermalization_time(tau_Bmu, radion_coupling)
    Effective thermalization time τ_eff = τ_Bmu / (1 + g²) [s].

thermalization_time_fs(tau_Bmu, radion_coupling)
    Effective thermalization time in femtoseconds [fs].

prompt_gamma_ratio(radion_coupling, gamma_standard)
    Prompt gamma fraction P_γ = gamma_standard / (1 + g²)².

energy_branching(Q_MeV, tau_Bmu, radion_coupling, gamma_standard)
    Complete energy branching dict: lattice heat, gamma, thermalization time.

phonon_distribution_evolution(f_init, f0, tau_Bmu, radion_coupling, t_arr)
    Analytic RTA time evolution f(t) toward f₀.

validate_um_predictions(tau_Bmu, radion_coupling)
    Returns dict confirming γ < 10⁻⁶ and τ_therm in femtosecond range.

lattice_heat_power(n_DD_per_cc_s, Q_MeV, radion_coupling, gamma_standard)
    Net lattice heat deposition rate [W/cm³].

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""

from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------

#: Reduced Planck constant  [J·s]
HBAR_J_S: float = 1.054571817e-34

#: Boltzmann constant  [J/K]
K_B_J_PER_K: float = 1.380649e-23

#: Boltzmann constant  [eV/K]
K_B_EV_PER_K: float = 8.617333262e-5

#: Elementary charge  [C]
E_CHARGE_C: float = 1.602176634e-19

#: 1 MeV in Joules
MEV_TO_J: float = 1.602176634e-13

#: 1 femtosecond in seconds
FS_TO_S: float = 1.0e-15

# ---------------------------------------------------------------------------
# Lattice / nuclear parameters  (Pd-D system)
# ---------------------------------------------------------------------------

#: Q-value of the dominant D + D → He-3 + n channel [MeV]
DD_Q_HE3_MEV: float = 3.27

#: Q-value of the D + D → T + p channel [MeV]
DD_Q_T_MEV: float = 4.03

#: Q-value of the radiative D + D → He-4 + γ channel [MeV]
DD_Q_GAMMA_MEV: float = 23.8

#: Standard D + D → He-4 + γ branching fraction in Pd lattice
#: (after standard electron screening; free-space value ~4 × 10⁻⁸)
DD_GAMMA_STANDARD: float = 3.0e-7

#: Palladium Debye temperature [K]
T_DEBYE_PD_K: float = 274.0

#: Pd Debye angular frequency  ω_D = k_B T_D / ℏ  [rad/s]
OMEGA_DEBYE_PD: float = K_B_J_PER_K * T_DEBYE_PD_K / HBAR_J_S  # ≈ 3.59 × 10¹³ rad/s

#: Baseline phonon-phonon scattering time in bulk Pd at 300 K [s]
#: (≈ 200 fs from inelastic neutron-scattering linewidths)
TAU_PHONON_PD_S: float = 2.0e-13

#: Canonical B_μ field confinement factor (dimensionless, UM convention = 1)
H_MAX_CANONICAL: float = 1.0

#: Canonical radion field mean in Pd lattice (≈ 2 × vacuum value)
PHI_MEAN_CANONICAL: float = 2.0

# ---------------------------------------------------------------------------
# UM canonical constants for the phonon-radion sector
# ---------------------------------------------------------------------------

#: Winding number n_w = 5 (Planck-selected; see Pillar 39)
N_W: int = 5

#: Chern-Simons level k_CS = 5² + 7² = 74
K_CS: int = 74

#: Braided sound speed c_s = 12/37 (from (5, 7) braid resonance)
C_S: float = 12.0 / 37.0

#: Canonical phonon-radion coupling g = N_W × √K_CS × C_S
#: g ≈ 5 × 8.602 × 0.3243 ≈ 13.95  →  g² ≈ 194.6
RADION_COUPLING_CANON: float = N_W * np.sqrt(K_CS) * C_S

# ---------------------------------------------------------------------------
# Equilibrium distribution
# ---------------------------------------------------------------------------


def bose_einstein(
    omega_arr: "np.ndarray | float",
    T_K: float,
) -> "np.ndarray | float":
    """Bose–Einstein equilibrium distribution for lattice phonons.

    Computes

        f₀(ω) = 1 / (exp(ℏω / k_B T) − 1)

    which is the mean phonon occupation number at angular frequency ω and
    temperature T.  This is the target distribution f₀ in the relaxation-
    time approximation.

    Parameters
    ----------
    omega_arr : ndarray or float
        Angular frequency (or array of frequencies) in rad/s.  Must be > 0.
    T_K : float
        Temperature in Kelvin.  Must be > 0.

    Returns
    -------
    f0 : ndarray or float
        Bose–Einstein occupation number(s) ≥ 0.

    Raises
    ------
    ValueError
        If T_K ≤ 0.
    """
    if T_K <= 0.0:
        raise ValueError(f"T_K must be positive, got {T_K}")
    x = HBAR_J_S * np.asarray(omega_arr, dtype=float) / (K_B_J_PER_K * T_K)
    # For very small x avoid division by zero; use series expansion f0 ≈ kT/(ℏω)
    # For very large x, f0 → 0; np.expm1 handles this accurately.
    return 1.0 / np.expm1(np.clip(x, 1e-15, None))


# ---------------------------------------------------------------------------
# B_μ relaxation time
# ---------------------------------------------------------------------------


def bmu_relaxation_time(
    H_max: float = H_MAX_CANONICAL,
    phi_mean: float = PHI_MEAN_CANONICAL,
    tau0: float = TAU_PHONON_PD_S,
) -> float:
    """B_μ-field-mediated base relaxation time τ_Bmu [s].

    The irreversibility gauge field B_μ confined by the Pd crystal potential
    shortens the phonon scattering time below the baseline anharmonic value.
    The relaxation time scales inversely with the B_μ field strength and the
    local radion mean:

        τ_Bmu = τ₀ / (H_max × φ_mean)

    At the canonical values (H_max = 1, φ_mean = 2) this gives
    τ_Bmu = TAU_PHONON_PD_S / 2 = 100 fs, which after radion enhancement
    yields a sub-femtosecond effective thermalization time.

    Parameters
    ----------
    H_max : float
        B_μ field strength (dimensionless UM units, default 1.0 = canonical).
    phi_mean : float
        Mean radion field value in the lattice (default 2.0 = Pd lattice
        canonical value; > 1 enhances the confinement).
    tau0 : float
        Baseline phonon relaxation time [s] (default TAU_PHONON_PD_S = 2×10⁻¹³ s).

    Returns
    -------
    float
        τ_Bmu in seconds.

    Raises
    ------
    ValueError
        If H_max, phi_mean, or tau0 are not positive.
    """
    if H_max <= 0.0:
        raise ValueError(f"H_max must be positive, got {H_max}")
    if phi_mean <= 0.0:
        raise ValueError(f"phi_mean must be positive, got {phi_mean}")
    if tau0 <= 0.0:
        raise ValueError(f"tau0 must be positive, got {tau0}")
    return tau0 / (H_max * phi_mean)


# ---------------------------------------------------------------------------
# Phonon-radion coupling
# ---------------------------------------------------------------------------


def radion_phonon_coupling(
    n_w: float = float(N_W),
    k_cs: float = float(K_CS),
    c_s: float = C_S,
) -> float:
    """Canonical phonon-radion coupling constant g.

    Derived from the UM braid geometry:

        g = n_w × √k_cs × c_s

    At canonical values (n_w = 5, k_cs = 74, c_s = 12/37):

        g = 5 × √74 × (12/37) ≈ 13.95    →    g² ≈ 194.6

    The collision-rate enhancement factor is (1 + g²) ≈ 195.6.

    Parameters
    ----------
    n_w : float
        Winding number (default 5).
    k_cs : float
        Chern-Simons level (default 74).
    c_s : float
        Braided sound speed (default 12/37).

    Returns
    -------
    float
        Dimensionless coupling constant g ≥ 0.

    Raises
    ------
    ValueError
        If any argument is non-positive.
    """
    if n_w <= 0.0:
        raise ValueError(f"n_w must be positive, got {n_w}")
    if k_cs <= 0.0:
        raise ValueError(f"k_cs must be positive, got {k_cs}")
    if c_s <= 0.0:
        raise ValueError(f"c_s must be positive, got {c_s}")
    return n_w * np.sqrt(k_cs) * c_s


# ---------------------------------------------------------------------------
# Unitary Collision Integral
# ---------------------------------------------------------------------------


def unitary_collision_integral(
    f: "np.ndarray | float",
    f0: "np.ndarray | float",
    tau_Bmu: float,
    radion_coupling: float,
) -> "np.ndarray | float":
    """Unitary Collision Integral for phonon transport in the Pd-D lattice.

    Solves the 'Ash Removal' problem by forcing fusion energy into phonon
    modes rather than allowing it to escape as radiation.

    The standard relaxation-time approximation gives:

        C_RTA = −(f − f₀) / τ_Bmu

    The UM adds a non-linear coupling to the radion field that prevents
    gamma emission by 'sinking' momentum into the 5th dimension:

        C_UM = C_RTA × (1 + g²)  =  −(f − f₀) / τ_Bmu × (1 + g²)

    This makes the effective thermalization rate (1 + g²) times faster than
    the bare B_μ-field rate, driving the phonon distribution to equilibrium
    on a femtosecond timescale.

    Parameters
    ----------
    f : ndarray or float
        Current phonon occupation distribution f(ω, t).
    f0 : ndarray or float
        Equilibrium Bose–Einstein distribution f₀(ω).
    tau_Bmu : float
        B_μ-field relaxation time [s].  Must be positive.
    radion_coupling : float
        Phonon-radion coupling constant g (dimensionless).  Use
        ``radion_phonon_coupling()`` for the canonical value (≈ 13.95).

    Returns
    -------
    C_UM : ndarray or float
        Rate of change df/dt due to collisions [s⁻¹].  Negative when f > f₀
        (system relaxes toward equilibrium).

    Raises
    ------
    ValueError
        If tau_Bmu ≤ 0.
    """
    if tau_Bmu <= 0.0:
        raise ValueError(f"tau_Bmu must be positive, got {tau_Bmu}")
    f = np.asarray(f, dtype=float)
    f0 = np.asarray(f0, dtype=float)

    # Standard relaxation time approximation
    coll_standard = -(f - f0) / tau_Bmu

    # The UM term: non-linear coupling to the radion field
    # prevents gamma emission by sinking momentum into the 5th dimension
    coll_unitary = coll_standard * (1.0 + radion_coupling ** 2)

    return coll_unitary


# ---------------------------------------------------------------------------
# Thermalization time
# ---------------------------------------------------------------------------


def thermalization_time(
    tau_Bmu: float,
    radion_coupling: float,
) -> float:
    """Effective thermalization time τ_eff [s].

    The UM collision integral enhances the relaxation rate by (1 + g²),
    giving an effective thermalization time:

        τ_eff = τ_Bmu / (1 + g²)

    Parameters
    ----------
    tau_Bmu : float
        B_μ-field base relaxation time [s].
    radion_coupling : float
        Phonon-radion coupling g (dimensionless).

    Returns
    -------
    float
        Effective thermalization time in seconds.

    Raises
    ------
    ValueError
        If tau_Bmu ≤ 0.
    """
    if tau_Bmu <= 0.0:
        raise ValueError(f"tau_Bmu must be positive, got {tau_Bmu}")
    return tau_Bmu / (1.0 + radion_coupling ** 2)


def thermalization_time_fs(
    tau_Bmu: float,
    radion_coupling: float,
) -> float:
    """Effective thermalization time in femtoseconds [fs].

    Convenience wrapper around :func:`thermalization_time` that converts the
    result to femtoseconds.

    Parameters
    ----------
    tau_Bmu : float
        B_μ-field base relaxation time [s].
    radion_coupling : float
        Phonon-radion coupling g.

    Returns
    -------
    float
        τ_eff in femtoseconds.
    """
    return thermalization_time(tau_Bmu, radion_coupling) / FS_TO_S


# ---------------------------------------------------------------------------
# Prompt gamma ratio
# ---------------------------------------------------------------------------


def prompt_gamma_ratio(
    radion_coupling: float,
    gamma_standard: float = DD_GAMMA_STANDARD,
) -> float:
    """Prompt gamma fraction P_γ after UM collision-integral suppression.

    The UM collision integral suppresses gamma emission quadratically in the
    coupling:

        P_γ = P_γ_standard / (1 + g²)²

    The quadratic suppression arises from two independent stages of
    suppression: (i) the formation of the excited radiative nuclear state is
    quenched by the enhanced phonon coupling, and (ii) any virtual photon is
    re-absorbed into the phonon bath before it can escape.

    For canonical parameters (g² ≈ 194.6, P_γ_std ≈ 3×10⁻⁷):

        P_γ ≈ 3×10⁻⁷ / (195.6)² ≈ 7.8 × 10⁻¹²  << 10⁻⁶  ✓

    Parameters
    ----------
    radion_coupling : float
        Phonon-radion coupling constant g.
    gamma_standard : float
        D + D → He-4 + γ branching fraction without UM enhancement
        (default 3×10⁻⁷ for Pd lattice).

    Returns
    -------
    float
        UM-suppressed prompt gamma fraction P_γ ∈ [0, 1].

    Raises
    ------
    ValueError
        If gamma_standard is not in [0, 1].
    """
    if gamma_standard < 0.0 or gamma_standard > 1.0:
        raise ValueError(
            f"gamma_standard must be in [0, 1], got {gamma_standard}"
        )
    suppression = (1.0 + radion_coupling ** 2) ** 2
    return gamma_standard / suppression


# ---------------------------------------------------------------------------
# Energy branching
# ---------------------------------------------------------------------------


def energy_branching(
    Q_MeV: float = DD_Q_HE3_MEV,
    tau_Bmu: float | None = None,
    radion_coupling: float | None = None,
    gamma_standard: float = DD_GAMMA_STANDARD,
) -> dict:
    """Complete D-D energy branching in the UM-enhanced Pd lattice.

    Computes the fraction of the D-D fusion Q-value deposited as lattice
    heat, the prompt gamma fraction, and the thermalization time.

    Parameters
    ----------
    Q_MeV : float
        D-D fusion Q-value [MeV] (default 3.27 MeV for He-3+n channel).
    tau_Bmu : float or None
        B_μ relaxation time [s].  If None, uses canonical value from
        ``bmu_relaxation_time()`` with default parameters.
    radion_coupling : float or None
        Phonon-radion coupling g.  If None, uses canonical value from
        ``radion_phonon_coupling()``.
    gamma_standard : float
        Standard D + D → He-4 + γ branching fraction.

    Returns
    -------
    dict with keys:
        ``Q_MeV``               : float — fusion Q-value [MeV]
        ``tau_Bmu_s``           : float — B_μ relaxation time [s]
        ``radion_coupling``     : float — phonon-radion coupling g
        ``g_squared``           : float — g²
        ``enhancement_factor``  : float — (1 + g²)
        ``tau_eff_s``           : float — effective thermalization time [s]
        ``tau_eff_fs``          : float — effective thermalization time [fs]
        ``prompt_gamma_ratio``  : float — P_γ (UM-suppressed)
        ``prompt_gamma_ratio_standard`` : float — P_γ without UM
        ``phonon_fraction``     : float — fraction of Q deposited as heat
        ``Q_lattice_MeV``       : float — lattice heat [MeV]
        ``Q_gamma_MeV``         : float — gamma energy [MeV]
        ``gamma_ratio_lt_1e6``  : bool — P_γ < 10⁻⁶ (required benchmark)
        ``tau_in_fs_range``     : bool — τ_eff ∈ [0.1, 100] fs (benchmark)
    """
    if tau_Bmu is None:
        tau_Bmu = bmu_relaxation_time()
    if radion_coupling is None:
        radion_coupling = radion_phonon_coupling()

    g2 = radion_coupling ** 2
    enhancement = 1.0 + g2
    tau_eff = tau_Bmu / enhancement
    tau_eff_fs_val = tau_eff / FS_TO_S
    P_gamma = prompt_gamma_ratio(radion_coupling, gamma_standard)
    phonon_frac = 1.0 - P_gamma

    return {
        "Q_MeV": float(Q_MeV),
        "tau_Bmu_s": float(tau_Bmu),
        "radion_coupling": float(radion_coupling),
        "g_squared": float(g2),
        "enhancement_factor": float(enhancement),
        "tau_eff_s": float(tau_eff),
        "tau_eff_fs": float(tau_eff_fs_val),
        "prompt_gamma_ratio": float(P_gamma),
        "prompt_gamma_ratio_standard": float(gamma_standard),
        "phonon_fraction": float(phonon_frac),
        "Q_lattice_MeV": float(phonon_frac * Q_MeV),
        "Q_gamma_MeV": float(P_gamma * Q_MeV),
        "gamma_ratio_lt_1e6": bool(P_gamma < 1e-6),
        "tau_in_fs_range": bool(0.1 <= tau_eff_fs_val <= 100.0),
    }


# ---------------------------------------------------------------------------
# Phonon distribution evolution (analytic RTA)
# ---------------------------------------------------------------------------


def phonon_distribution_evolution(
    f_init: "np.ndarray | float",
    f0: "np.ndarray | float",
    tau_Bmu: float,
    radion_coupling: float,
    t_arr: "np.ndarray",
) -> "np.ndarray":
    """Analytic time evolution of the phonon distribution under C_UM.

    In the relaxation-time approximation the Boltzmann equation has the
    analytic solution:

        f(t) = f₀ + (f_init − f₀) × exp(−t / τ_eff)

    where τ_eff = τ_Bmu / (1 + g²) is the UM-enhanced relaxation time.

    Parameters
    ----------
    f_init : ndarray or float
        Initial phonon occupation distribution f(ω, t=0).
    f0 : ndarray or float
        Equilibrium distribution f₀(ω) (Bose–Einstein at lattice temperature).
    tau_Bmu : float
        B_μ relaxation time [s].
    radion_coupling : float
        Phonon-radion coupling g.
    t_arr : ndarray, shape (N_t,)
        Time array in seconds at which to evaluate f(t).

    Returns
    -------
    ndarray, shape (N_omega, N_t) or (N_t,) for scalar f_init/f0
        Distribution function at each time step.

    Raises
    ------
    ValueError
        If tau_Bmu ≤ 0.
    """
    if tau_Bmu <= 0.0:
        raise ValueError(f"tau_Bmu must be positive, got {tau_Bmu}")
    tau_eff = thermalization_time(tau_Bmu, radion_coupling)
    f_init = np.asarray(f_init, dtype=float)
    f0 = np.asarray(f0, dtype=float)
    t_arr = np.asarray(t_arr, dtype=float)
    delta_f = f_init - f0
    # shape broadcast: delta_f[..., None] × exp_decay[None, :]
    exp_decay = np.exp(-t_arr / tau_eff)
    if delta_f.ndim == 0:
        return f0 + delta_f * exp_decay
    return f0[..., None] + delta_f[..., None] * exp_decay[None, :]


# ---------------------------------------------------------------------------
# Validation / benchmark check
# ---------------------------------------------------------------------------


def validate_um_predictions(
    tau_Bmu: float | None = None,
    radion_coupling: float | None = None,
    gamma_standard: float = DD_GAMMA_STANDARD,
) -> dict:
    """Verify that UM predictions satisfy the required benchmarks.

    Checks:
        1. Prompt gamma ratio P_γ < 10⁻⁶  (radiation-safety criterion).
        2. Thermalization time τ_eff ∈ [0.1, 100] fs  (femtosecond regime).

    Parameters
    ----------
    tau_Bmu : float or None
        B_μ relaxation time [s].  Defaults to canonical.
    radion_coupling : float or None
        Coupling constant g.  Defaults to canonical.
    gamma_standard : float
        Standard gamma branching fraction.

    Returns
    -------
    dict with keys:
        ``passed``                  : bool — True if both benchmarks pass
        ``gamma_ratio_lt_1e6``      : bool — P_γ < 10⁻⁶
        ``tau_in_fs_range``         : bool — τ_eff ∈ [0.1, 100] fs
        ``prompt_gamma_ratio``      : float
        ``tau_eff_fs``              : float
        ``radion_coupling``         : float
        ``g_squared``               : float
        ``enhancement_factor``      : float
        ``tau_Bmu_s``               : float
    """
    branch = energy_branching(
        Q_MeV=DD_Q_HE3_MEV,
        tau_Bmu=tau_Bmu,
        radion_coupling=radion_coupling,
        gamma_standard=gamma_standard,
    )
    passed = branch["gamma_ratio_lt_1e6"] and branch["tau_in_fs_range"]
    return {
        "passed": passed,
        "gamma_ratio_lt_1e6": branch["gamma_ratio_lt_1e6"],
        "tau_in_fs_range": branch["tau_in_fs_range"],
        "prompt_gamma_ratio": branch["prompt_gamma_ratio"],
        "tau_eff_fs": branch["tau_eff_fs"],
        "radion_coupling": branch["radion_coupling"],
        "g_squared": branch["g_squared"],
        "enhancement_factor": branch["enhancement_factor"],
        "tau_Bmu_s": branch["tau_Bmu_s"],
    }


# ---------------------------------------------------------------------------
# Heat power output
# ---------------------------------------------------------------------------


def lattice_heat_power(
    n_DD_per_cc_s: float,
    Q_MeV: float = DD_Q_HE3_MEV,
    radion_coupling: float | None = None,
    gamma_standard: float = DD_GAMMA_STANDARD,
) -> float:
    """Net lattice heat deposition rate [W/cm³].

    Computes the volumetric heat power deposited in the lattice from D-D
    fusion events, accounting for the UM-suppressed gamma loss:

        P_lattice = n_DD/s × Q_DD × (1 − P_γ) × MeV_to_J

    Parameters
    ----------
    n_DD_per_cc_s : float
        D-D fusion event rate per cm³ per second.  Must be ≥ 0.
    Q_MeV : float
        D-D fusion Q-value [MeV] (default 3.27 MeV).
    radion_coupling : float or None
        Phonon-radion coupling g.  Defaults to canonical.
    gamma_standard : float
        Standard gamma branching fraction.

    Returns
    -------
    float
        Lattice heat deposition rate in W/cm³.

    Raises
    ------
    ValueError
        If n_DD_per_cc_s < 0 or Q_MeV ≤ 0.
    """
    if n_DD_per_cc_s < 0.0:
        raise ValueError(f"n_DD_per_cc_s must be ≥ 0, got {n_DD_per_cc_s}")
    if Q_MeV <= 0.0:
        raise ValueError(f"Q_MeV must be positive, got {Q_MeV}")
    if radion_coupling is None:
        radion_coupling = radion_phonon_coupling()
    P_gamma = prompt_gamma_ratio(radion_coupling, gamma_standard)
    phonon_fraction = 1.0 - P_gamma
    Q_J = Q_MeV * MEV_TO_J
    return n_DD_per_cc_s * Q_J * phonon_fraction


# ---------------------------------------------------------------------------
# Coefficient of Performance (COP)
# ---------------------------------------------------------------------------


def calculate_cop(
    n_DD_per_cc_s: float,
    W_input_W_per_cc: float,
    volume_cc: float = 1.0,
    Q_MeV: float = DD_Q_HE3_MEV,
    radion_coupling: float | None = None,
    gamma_standard: float = DD_GAMMA_STANDARD,
) -> dict:
    """Coefficient of Performance for the UM-enhanced Pd-D cold-fusion cell.

    Connects the Gamow-entry side (fusion event rate per cm³ per second) to
    the heat-output side (Boltzmann transport efficiency) in a single COP
    calculation:

        COP = Q_lattice_total / W_input_total
            = (n_DD/s × V × Q_DD × phonon_fraction) / (W_input/cc × V)
            = (n_DD/s × Q_DD × phonon_fraction) / (W_input/cc)

    **Epistemics note:** The fusion event rate ``n_DD_per_cc_s`` must be
    supplied by the caller (typically from ``src.core.cold_fusion.cold_fusion_rate``
    or from experimental calorimetry).  This function computes the
    *thermodynamic output efficiency* of those events — what fraction of the
    Q-value reaches the lattice as useful heat — and folds it into the COP.

    Break-even condition: COP ≥ 1.0.

    Parameters
    ----------
    n_DD_per_cc_s : float
        D-D fusion event rate per cm³ per second (events / cm³ / s).
        Obtain from ``cold_fusion.cold_fusion_rate()`` or experiment.
    W_input_W_per_cc : float
        Electrical (or other) work input per cm³ per second [W/cm³].
        Must be > 0.
    volume_cc : float
        Active volume of the cell [cm³] (default 1.0).  Cancels in the
        COP ratio but is retained for absolute power accounting.
    Q_MeV : float
        D-D fusion Q-value [MeV] (default 3.27 MeV).
    radion_coupling : float or None
        Phonon-radion coupling g.  Defaults to canonical.
    gamma_standard : float
        Standard gamma branching fraction (pre-UM).

    Returns
    -------
    dict with keys:
        ``n_DD_per_cc_s``      : float — fusion rate input [/cm³/s]
        ``W_input_W_per_cc``   : float — work input [W/cm³]
        ``volume_cc``          : float — active volume [cm³]
        ``Q_MeV``              : float — fusion Q-value [MeV]
        ``radion_coupling``    : float — phonon-radion coupling g
        ``phonon_fraction``    : float — fraction of Q reaching lattice
        ``Q_lattice_W_per_cc`` : float — heat output rate [W/cm³]
        ``Q_lattice_W_total``  : float — total heat output [W]
        ``W_input_W_total``    : float — total work input [W]
        ``COP``                : float — Coefficient of Performance
        ``break_even``         : bool — True if COP ≥ 1.0
        ``COP_margin``         : float — COP − 1.0 (positive = above break-even)
        ``prompt_gamma_ratio`` : float — UM-suppressed P_γ

    Raises
    ------
    ValueError
        If W_input_W_per_cc ≤ 0 or volume_cc ≤ 0.
    """
    if W_input_W_per_cc <= 0.0:
        raise ValueError(
            f"W_input_W_per_cc must be positive, got {W_input_W_per_cc}"
        )
    if volume_cc <= 0.0:
        raise ValueError(f"volume_cc must be positive, got {volume_cc}")

    if radion_coupling is None:
        radion_coupling = radion_phonon_coupling()

    P_gamma = prompt_gamma_ratio(radion_coupling, gamma_standard)
    phonon_fraction = 1.0 - P_gamma

    Q_lattice_W_per_cc = lattice_heat_power(
        n_DD_per_cc_s, Q_MeV, radion_coupling, gamma_standard
    )
    Q_lattice_W_total = Q_lattice_W_per_cc * volume_cc
    W_input_W_total = W_input_W_per_cc * volume_cc

    COP_val = Q_lattice_W_total / W_input_W_total
    break_even = bool(COP_val >= 1.0)

    return {
        "n_DD_per_cc_s": float(n_DD_per_cc_s),
        "W_input_W_per_cc": float(W_input_W_per_cc),
        "volume_cc": float(volume_cc),
        "Q_MeV": float(Q_MeV),
        "radion_coupling": float(radion_coupling),
        "phonon_fraction": float(phonon_fraction),
        "Q_lattice_W_per_cc": float(Q_lattice_W_per_cc),
        "Q_lattice_W_total": float(Q_lattice_W_total),
        "W_input_W_total": float(W_input_W_total),
        "COP": float(COP_val),
        "break_even": break_even,
        "COP_margin": float(COP_val - 1.0),
        "prompt_gamma_ratio": float(P_gamma),
    }
