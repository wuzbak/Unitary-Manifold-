# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/pillar219_interstellar_travel.py
==========================================
Pillar 219 — Interstellar Travel: Physics of Limitations and Pathways.

Provides honest quantitative analysis of interstellar travel: energy costs,
time dilation, radiation hazards, propulsion options, warp geometry bounds
from the KK compactification, and an overview of realistic near-term probes.

Status: ADJACENT RESEARCH TRACK (non-hardgate, speculative engineering).
"""
from __future__ import annotations
import math

__provenance__ = {
    "pillar": 219,
    "title": "Interstellar Travel: Physics of Limitations and Pathways",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "status": "ADJACENT RESEARCH TRACK — speculative engineering",
}

__all__ = [
    # Manifold constants
    "N_W",
    "K_CS",
    "PHI0",
    "BRAIDED_SOUND_SPEED",
    # Physical constants (SI)
    "C_LIGHT",
    "AU_METERS",
    "PARSEC_METERS",
    "LY_METERS",
    "ALPHA_CENTAURI_LY",
    "SOLAR_MASS_KG",
    "KJ_PER_KG_TNT",
    "G_NEWTON",
    "HBAR_SI",
    "PLANCK_MASS_KG",
    # World-energy reference
    "WORLD_ENERGY_ANNUAL_J",
    # Functions
    "kinetic_energy_fraction_c",
    "time_dilation",
    "radiation_dose_interstellar",
    "alcubierre_energy_estimate",
    "generation_ship_analysis",
    "kk_warp_geometry_bound",
    "propulsion_comparison",
    "pillar219_summary",
]

# ---------------------------------------------------------------------------
# Manifold constants
# ---------------------------------------------------------------------------
N_W: int = 5
K_CS: int = 74
PHI0: float = 0.739085
BRAIDED_SOUND_SPEED: float = 12 / 37

# ---------------------------------------------------------------------------
# Physical constants (SI)
# ---------------------------------------------------------------------------
C_LIGHT: float = 2.998e8          # m/s
AU_METERS: float = 1.496e11        # 1 AU in metres
PARSEC_METERS: float = 3.086e16    # 1 pc in metres
LY_METERS: float = 9.461e15        # 1 ly in metres
ALPHA_CENTAURI_LY: float = 4.37    # ly to Alpha Centauri
SOLAR_MASS_KG: float = 1.989e30    # kg
KJ_PER_KG_TNT: float = 4.184e6    # J / kg-TNT  (1 t TNT = 4.184 GJ)
G_NEWTON: float = 6.674e-11        # m³ kg⁻¹ s⁻²
HBAR_SI: float = 1.0546e-34        # J·s
PLANCK_MASS_KG: float = math.sqrt(HBAR_SI * C_LIGHT / G_NEWTON)  # ≈ 2.176e-8 kg

# ---------------------------------------------------------------------------
# Derived reference scales
# ---------------------------------------------------------------------------
# World primary energy consumption 2023 ≈ 6.0 × 10²⁰ J/yr
WORLD_ENERGY_ANNUAL_J: float = 6.0e20

# Seconds per year (Julian)
_SECONDS_PER_YEAR: float = 365.25 * 24 * 3600


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def kinetic_energy_fraction_c(mass_kg: float, v_fraction_c: float) -> dict:
    """Relativistic kinetic energy for a spacecraft of given mass.

    Parameters
    ----------
    mass_kg : float
        Rest mass of the spacecraft [kg].
    v_fraction_c : float
        Speed as a fraction of c, in (0, 1).

    Returns
    -------
    dict with keys:
        KE_joules              – relativistic kinetic energy [J]
        KE_megatons_tnt        – same, in megatons of TNT
        KE_annual_world_energy_ratio – ratio to annual world energy use
        lorentz_factor         – γ
        rest_energy_joules     – mc²
        notes                  – brief text
    """
    if v_fraction_c < 0 or v_fraction_c >= 1.0:
        raise ValueError("v_fraction_c must be in [0, 1).")
    v = v_fraction_c * C_LIGHT
    gamma = 1.0 / math.sqrt(1.0 - v_fraction_c ** 2)
    rest_energy = mass_kg * C_LIGHT ** 2
    KE = (gamma - 1.0) * rest_energy

    # 1 megaton TNT = 1e6 t × 4.184e9 J/t = 4.184e15 J
    megatons_tnt = KE / 4.184e15
    world_ratio = KE / WORLD_ENERGY_ANNUAL_J

    return {
        "KE_joules": KE,
        "KE_megatons_tnt": megatons_tnt,
        "KE_annual_world_energy_ratio": world_ratio,
        "lorentz_factor": gamma,
        "rest_energy_joules": rest_energy,
        "notes": (
            f"Relativistic KE for {mass_kg:.2e} kg at {v_fraction_c}c. "
            f"γ = {gamma:.4f}. Energy ≈ {megatons_tnt:.3e} Mt TNT."
        ),
    }


def time_dilation(v_fraction_c: float, distance_ly: float) -> dict:
    """Special-relativistic time dilation on an interstellar voyage.

    Assumes constant velocity (no acceleration phase).

    Parameters
    ----------
    v_fraction_c : float
        Speed as fraction of c, in (0, 1).
    distance_ly : float
        One-way distance [light-years].

    Returns
    -------
    dict with keys:
        lorentz_factor         – γ
        coordinate_time_years  – Earth-frame travel time [yr]
        proper_time_years      – shipboard time [yr]
        fraction_of_light_speed – v / c
        time_savings_years     – coordinate − proper [yr]
        notes                  – brief text
    """
    if v_fraction_c <= 0 or v_fraction_c >= 1.0:
        raise ValueError("v_fraction_c must be in (0, 1).")
    gamma = 1.0 / math.sqrt(1.0 - v_fraction_c ** 2)
    coord_time = distance_ly / v_fraction_c          # years (Earth frame)
    proper_time = coord_time / gamma                 # years (ship frame)

    return {
        "lorentz_factor": gamma,
        "coordinate_time_years": coord_time,
        "proper_time_years": proper_time,
        "fraction_of_light_speed": v_fraction_c,
        "time_savings_years": coord_time - proper_time,
        "notes": (
            f"At {v_fraction_c}c over {distance_ly} ly: "
            f"Earth time {coord_time:.1f} yr, ship time {proper_time:.2f} yr."
        ),
    }


def radiation_dose_interstellar(v_fraction_c: float) -> dict:
    """Estimated cosmic-ray dose rate during interstellar cruise.

    At rest in interstellar space the dose ≈ 100 mSv/year from galactic
    cosmic rays (GCR).  At relativistic speed the flux of GCR in the
    forward hemisphere blue-shifts, roughly scaling as γ² (conservative
    upper bound).  Shielding needed above 1000 mSv/yr threshold (chronic
    lethal risk within years).

    Parameters
    ----------
    v_fraction_c : float
        Speed as fraction of c, in [0, 1).

    Returns
    -------
    dict with keys:
        v_fraction_c            – input speed
        lorentz_factor          – γ
        dose_mSv_per_year       – estimated dose rate [mSv/yr]
        baseline_dose_mSv_yr    – ISS-like baseline [mSv/yr]
        lethal_threshold_mSv    – chronic lethal threshold [mSv/yr]
        shielding_required_bool – True if dose exceeds threshold
        notes                   – brief text
    """
    if v_fraction_c < 0 or v_fraction_c >= 1.0:
        raise ValueError("v_fraction_c must be in [0, 1).")
    BASELINE_MSV_YR = 100.0      # GCR dose in deep space at rest [mSv/yr]
    LETHAL_THRESHOLD = 1000.0    # chronic lethal threshold [mSv/yr]

    gamma = 1.0 / math.sqrt(max(1.0 - v_fraction_c ** 2, 1e-30))
    # Conservative: dose ~ baseline × γ²  (flux blue-shift + energy increase)
    dose = BASELINE_MSV_YR * gamma ** 2

    return {
        "v_fraction_c": v_fraction_c,
        "lorentz_factor": gamma,
        "dose_mSv_per_year": dose,
        "baseline_dose_mSv_yr": BASELINE_MSV_YR,
        "lethal_threshold_mSv": LETHAL_THRESHOLD,
        "shielding_required_bool": dose > LETHAL_THRESHOLD,
        "notes": (
            f"GCR dose at {v_fraction_c}c ≈ {dose:.1f} mSv/yr "
            f"(γ²-scaled). Shielding needed: {dose > LETHAL_THRESHOLD}."
        ),
    }


def alcubierre_energy_estimate(
    R_bubble_m: float = 100.0,
    v_fraction_c: float = 1.0,
) -> dict:
    """Alcubierre warp-bubble exotic-energy requirement.

    The standard order-of-magnitude estimate (Alcubierre 1994, refined by
    White 2011, Lentz 2021) for the magnitude of exotic (negative) energy:

        |E_warp| ≈ (c⁴ / G) × R² × v / c
                 = M_Pl² R² v c  (in SI)

    where M_Pl is the Planck mass.

    The result is negative (exotic matter has negative energy density).
    Modern refined estimates range from tens to thousands of solar masses
    depending on bubble thickness assumptions.

    Parameters
    ----------
    R_bubble_m : float
        Radius of the warp bubble [m]. Default 100 m.
    v_fraction_c : float
        Desired warp speed as fraction of c. Default 1.0 (luminal).

    Returns
    -------
    dict with keys:
        energy_joules       – signed exotic energy [J] (negative)
        energy_solar_masses – magnitude in solar-mass equivalents
        R_bubble_m          – input bubble radius
        v_fraction_c        – input warp speed
        feasibility_note    – honest summary string
        notes               – additional text
    """
    v = v_fraction_c * C_LIGHT
    # |E| ≈ c⁴ R² v / G  (dimensional estimate from the metric shaping function)
    energy_magnitude = (C_LIGHT ** 4 * R_bubble_m ** 2 * v) / G_NEWTON
    energy_joules = -energy_magnitude  # exotic = negative energy density

    energy_solar_masses = energy_magnitude / (SOLAR_MASS_KG * C_LIGHT ** 2)

    feasibility_note = (
        "Requires negative-energy-density (exotic) matter at scale "
        f"~{energy_solar_masses:.2e} solar masses. "
        "No known mechanism produces macroscopic exotic matter. "
        "Casimir effect yields negative energy density only at sub-micron scales. "
        "Alcubierre warp drives remain firmly speculative."
    )

    return {
        "energy_joules": energy_joules,
        "energy_solar_masses": energy_solar_masses,
        "R_bubble_m": R_bubble_m,
        "v_fraction_c": v_fraction_c,
        "feasibility_note": feasibility_note,
        "notes": (
            f"Warp bubble R={R_bubble_m} m at v={v_fraction_c}c: "
            f"|E| ≈ {energy_magnitude:.3e} J ≈ {energy_solar_masses:.2e} M_☉."
        ),
    }


def generation_ship_analysis(
    distance_ly: float,
    accel_g: float = 0.01,
) -> dict:
    """Constant-boost interstellar voyage analysis.

    Models a ship that accelerates at `accel_g` × g (9.81 m/s²) for the
    entire trip (no deceleration phase — arrival speed reported separately).
    Uses relativistic rocket equations.

    Parameters
    ----------
    distance_ly : float
        One-way distance [light-years].
    accel_g : float
        Acceleration as multiple of Earth surface gravity (9.81 m/s²).
        Default 0.01 g (a gentle 0.098 m/s²).

    Returns
    -------
    dict with keys:
        travel_time_years_ship   – proper (shipboard) time [yr]
        travel_time_years_earth  – coordinate (Earth) time [yr]
        peak_v_fraction_c        – velocity at destination / c  (< 1)
        accel_m_s2               – actual acceleration [m/s²]
        distance_ly              – input distance
        energy_joules_per_kg     – kinetic energy imparted per kg of payload
        notes                    – brief text
    """
    g_SI = 9.81  # m/s²
    a = accel_g * g_SI  # m/s²
    d = distance_ly * LY_METERS  # m

    # Relativistic constant-acceleration: Earth-frame travel time t satisfies
    #   d = (c²/a)(cosh(a t / c) - 1)  →  t = (c/a) acosh(1 + a d / c²)
    # Proper time τ = (c/a) sinh(a t / c)
    arg = 1.0 + a * d / C_LIGHT ** 2
    t_earth_s = (C_LIGHT / a) * math.acosh(arg)
    tau_s = (C_LIGHT / a) * math.asinh(math.sqrt(arg ** 2 - 1.0))

    t_earth_yr = t_earth_s / _SECONDS_PER_YEAR
    tau_yr = tau_s / _SECONDS_PER_YEAR

    # Peak velocity (at destination)
    # v/c = tanh(a τ / c)
    peak_v = math.tanh(a * tau_s / C_LIGHT)

    # Kinetic energy per kg of payload
    gamma_peak = 1.0 / math.sqrt(1.0 - peak_v ** 2)
    KE_per_kg = (gamma_peak - 1.0) * C_LIGHT ** 2

    return {
        "travel_time_years_ship": tau_yr,
        "travel_time_years_earth": t_earth_yr,
        "peak_v_fraction_c": peak_v,
        "accel_m_s2": a,
        "distance_ly": distance_ly,
        "energy_joules_per_kg": KE_per_kg,
        "notes": (
            f"Constant {accel_g}g boost to {distance_ly} ly: "
            f"ship time {tau_yr:.1f} yr, Earth time {t_earth_yr:.1f} yr, "
            f"peak v = {peak_v:.4f}c."
        ),
    }


def kk_warp_geometry_bound(
    K_cs: int = K_CS,
    phi0: float = PHI0,
) -> dict:
    """Kaluza-Klein geometry bound on stable warp factors.

    The φ₀ attractor and K_CS = 5² + 7² together set a dimensionless scale
    for the compactified extra dimension.  Within the KK framework the
    ratio:

        Ξ_warp = φ₀ × K_cs / (4π)

    acts as a bound on the dimensionless warp factor of a KK-compactified
    spacetime: warp factors exceeding Ξ_warp would require the compactified
    radius to shrink below the Planck length, signalling breakdown of the
    effective field theory.

    Honest caveat: This is speculative geometry.  The bound connects the
    manifold's attractor structure to warp physics but does NOT constitute
    a proof that warp drives are achievable.

    Parameters
    ----------
    K_cs : int
        Chern-Simons level (default 74).
    phi0 : float
        φ₀ fixed-point attractor (default 0.739085).

    Returns
    -------
    dict with keys:
        kk_warp_bound     – Ξ_warp = φ₀ K_cs / (4π)
        K_cs              – input K_cs
        phi0              – input phi0
        interpretation    – text
        is_speculative    – always True
    """
    bound = phi0 * K_cs / (4.0 * math.pi)
    return {
        "kk_warp_bound": bound,
        "K_cs": K_cs,
        "phi0": phi0,
        "interpretation": (
            f"Ξ_warp = φ₀ × K_CS / (4π) ≈ {bound:.4f}. "
            "This dimensionless number bounds the warp factor in a KK-compactified "
            "spacetime before the compactification radius drops below Planck scale. "
            "A warp factor W < Ξ_warp remains within the EFT validity window. "
            "This is a speculative geometric bound, not a warp-drive recipe."
        ),
        "is_speculative": True,
    }


def propulsion_comparison() -> list[dict]:
    """Comparison of interstellar propulsion concepts.

    Returns
    -------
    list of dicts, each with:
        name                – propulsion system name
        max_v_fraction_c    – peak reachable v / c (rough estimate)
        TRL                 – Technology Readiness Level (1–9, NASA scale)
        energy_per_kg_J     – approximate kinetic energy per kg payload [J]
        notes               – one-sentence summary
    """
    return [
        {
            "name": "Chemical rocket (H₂/O₂)",
            "max_v_fraction_c": 1e-4,
            "TRL": 9,
            "energy_per_kg_J": 1.3e7,
            "notes": (
                "Highest TRL; Isp ≈ 450 s; hopelessly inadequate for interstellar "
                "distances — would take >40,000 years to Alpha Centauri."
            ),
        },
        {
            "name": "Ion / Hall-effect thruster",
            "max_v_fraction_c": 3e-4,
            "TRL": 9,
            "energy_per_kg_J": 4e7,
            "notes": (
                "Isp up to ~10,000 s; excellent for solar-system missions; "
                "transit time to Alpha Centauri ~15,000 years."
            ),
        },
        {
            "name": "Nuclear pulse (Project Orion)",
            "max_v_fraction_c": 3e-3,
            "TRL": 3,
            "energy_per_kg_J": 4e8,
            "notes": (
                "Sequential nuclear detonations; design studies show 3–3.3 % c "
                "achievable; transit ~1,400 years; politically/legally blocked by PTBT."
            ),
        },
        {
            "name": "Laser sail (Breakthrough Starshot)",
            "max_v_fraction_c": 0.20,
            "TRL": 3,
            "energy_per_kg_J": 1.8e15,
            "notes": (
                "1-gram sail accelerated to 0.2c by 100 GW laser array; "
                "transit ~20 years; only gram-scale payloads feasible."
            ),
        },
        {
            "name": "Antimatter annihilation",
            "max_v_fraction_c": 0.50,
            "TRL": 1,
            "energy_per_kg_J": 9e16,
            "notes": (
                "Mass-energy conversion ≈ 100%; current antiproton production "
                "rate ~10 ng/yr at CERN — production shortfall is ~20 orders of magnitude."
            ),
        },
        {
            "name": "Alcubierre warp drive",
            "max_v_fraction_c": 10.0,
            "TRL": 1,
            "energy_per_kg_J": float("inf"),
            "notes": (
                "Theoretically superluminal; requires macroscopic exotic (negative) "
                "energy ~10–1000 M_☉; causality violations suspected; "
                "no known mechanism for exotic matter production."
            ),
        },
    ]


def pillar219_summary() -> dict:
    """Honest epistemic summary of Pillar 219.

    Returns
    -------
    dict with keys:
        pillar, title, honest_assessment, kk_warp_bound,
        alpha_centauri_energy_0p1c_ratio, status, references
    """
    # Representative energy calculation: 1e6 kg ship at 0.1c
    ke = kinetic_energy_fraction_c(1e6, 0.1)
    warp = kk_warp_geometry_bound()

    return {
        "pillar": 219,
        "title": "Interstellar Travel: Physics of Limitations and Pathways",
        "honest_assessment": (
            "Interstellar travel is extraordinarily hard. "
            "A 1,000-tonne ship at 0.1c requires ~{:.1e} times annual world energy. "
            "The only near-term realistic option is gram-scale laser-sail probes "
            "(Breakthrough Starshot). Crewed missions remain centuries away at minimum. "
            "Warp drives require exotic matter that does not observationally exist. "
            "The Unitary Manifold KK geometry provides a dimensionless warp-factor bound "
            "(Ξ_warp ≈ {:.3f}) but does not resolve the exotic-matter problem."
        ).format(
            ke["KE_annual_world_energy_ratio"],
            warp["kk_warp_bound"],
        ),
        "kk_warp_bound": warp["kk_warp_bound"],
        "alpha_centauri_energy_0p1c_ratio": ke["KE_annual_world_energy_ratio"],
        "status": "ADJACENT RESEARCH TRACK — speculative engineering",
        "references": [
            "Alcubierre, M. (1994). Class. Quant. Grav. 11, L73.",
            "Lentz, E.W. (2021). Class. Quant. Grav. 38, 075015.",
            "Breakthrough Starshot Initiative (2016). breakthroughinitiatives.org.",
            "Dyson, F.J. (1968). Physics Today 21(10), 41–45. (Project Orion)",
            "Walker-Pearson, T. (2026). Unitary Manifold v10.4. Zenodo.",
        ],
    }
