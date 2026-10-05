# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 538 — Enteric Neural Core: ENS as Second Brain and KK Biophysical Coupling.

🔵 ADJACENT TRACK — not a hardgate physics claim.

Adjacent applied research track (non-hardgate): this module does not claim
consciousness resides in the gut, nor that KK geometry causally governs
enteric signalling.  It provides a quantitative framework for:

1) mapping the Enteric Nervous System (ENS) anatomy to the 5D KK geometry via
   shared structural invariants (N_W = 5, K_CS = 74, PHI0 ≈ 73.9 %);
2) computing the toroidal vector null point that coincides with the body's
   geometric center of mass (~4.4 cm / 1.74 inches below the navel);
3) modelling ENS autonomy — the fraction of enteric function retained after
   vagal disconnection — as a φ-debt entropy metric;
4) connecting embryological neural-crest migration geometry to the 5D
   compactification picture (N_gen = 3 generations, n_before = 6).

All clinical/neuroanatomical parameters are drawn from published literature
(Hopkins Medicine, Cleveland Clinic, Stanford Medicine, PMC/NIH).  They are
used as empirical inputs, not UM-derived predictions.

SCIENTIFIC GROUNDING
--------------------
The Enteric Nervous System (ENS):
  - Contains 100–500 million neurons (more than the spinal cord).
  - Cell architecture mirrors the cranial CNS: afferent, interneuron, efferent.
  - Enteric glial cells (EGCs) are structurally analogous to CNS astrocytes.
  - Manufactures ~90–95 % of the body's serotonin and ~50 % of its dopamine.
  - Operates fully autonomously if the vagus nerve is severed.
  - Embryological origin: vagal + sacral neural crest cells migrating into the
    GI mesoderm during weeks 3–7 of gestation — the same neural crest tissue
    that forms the cranial brain.

Geometric coordinates:
  - Center of mass of the adult human torso ≈ 4.4 cm (1.74 in) below the
    umbilicus — the "hypogastric sub-umbilical coordinate."
  - In a toroidal energy field, the central axis null point coincides with
    this coordinate.

KK coupling analogy:
  - The dense autonomous neural cluster at the body's center of mass acts as
    a high-density biological field node, structurally analogous to a KK
    antenna coupling to the unified EM/gravitational field encoded in the
    compactified 5th dimension.
  - This is a geometric analogy; it does not constitute a claim that KK
    physics directly governs enteric signalling.

TOROIDAL MATHEMATICS
--------------------
A torus in ℝ³ with major radius R and minor radius r is parametrized by:

    x(σ, φ) = (R + r cos σ) cos φ
    y(σ, φ) = (R + r cos σ) sin φ
    z(σ, φ) = r sin σ

The velocity / flux vector field on the surface:

    V = v_φ φ̂ + v_σ σ̂

Vector null condition at the central axis (r → 0):

    ΣF_net = ∫₀²π ∫₀²π V(σ,φ) dσ dφ = 0

This null point is the geometric anchor of the toroidal field.

EMBRYOLOGICAL KK LINK
----------------------
Neural crest migration distance ∝ n_before = 2 × N_gen = 6 (Pillar 537).
Vagal crest cells travel the full craniocaudal axis (distance ≈ crown-rump
length L_CR); sacral crest cells migrate the distal fraction (≈ L_CR / n_w).
The ratio sacral/vagal ≈ 1/n_w = 1/5 is a structural coincidence noted here
as a geometric curiosity, not a causal claim.
"""
from __future__ import annotations

import math
from typing import Any

__provenance__ = {
    "pillar": 538,
    "title": "Enteric Neural Core: ENS as Second Brain and KK Biophysical Coupling",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "status": (
        "ADJACENT RESEARCH TRACK — quantitative ENS/toroidal/KK geometric "
        "framework; no claim of causal KK governance of enteric signalling"
    ),
    "primary_sources": [
        "Hopkins Medicine — second brain / ENS overview",
        "Cleveland Clinic — ENS neuron counts and autonomy",
        "Stanford Medicine — enteric glial cells",
        "PMC/NIH — neural crest migration and ENS development",
    ],
}

__all__ = [
    # KK constants
    "N_W",
    "K_CS",
    "C_S",
    "PHI0",
    "N_BEFORE",
    # ENS anatomy constants
    "ENS_NEURON_COUNT_LOW",
    "ENS_NEURON_COUNT_HIGH",
    "ENS_NEURON_COUNT_MID",
    "SEROTONIN_GUT_FRACTION",
    "DOPAMINE_GUT_FRACTION",
    "NEUROTRANSMITTER_TYPES",
    "SPINAL_CORD_NEURON_COUNT",
    "VAGUS_NERVE_MAX_SPEED_MS",
    # Geometric constants
    "SUB_UMBILICAL_DISTANCE_CM",
    "SUB_UMBILICAL_DISTANCE_IN",
    "TORSO_MAJOR_RADIUS_CM",
    "TORSO_MINOR_RADIUS_CM",
    # Functions
    "torus_surface_point",
    "torus_vector_field_integral",
    "toroidal_null_condition",
    "ens_autonomy_score",
    "gut_brain_reaction_lag",
    "ens_serotonin_production",
    "ens_phi_coherence",
    "kk_bio_coupling_strength",
    "neural_crest_migration_ratio",
    "embryological_kk_link",
    "enteric_vs_cranial_comparison",
    "pillar538_summary",
]

# ---------------------------------------------------------------------------
# KK / UM physics constants
# ---------------------------------------------------------------------------
N_W: int = 5                            # winding number — braid primary
K_CS: int = 74                          # K_CS = 5² + 7² = 74
C_S: float = 12.0 / 37.0               # braided sound speed
PHI0: float = 0.7390851332151607        # radion attractor / φ₀ efficiency ceiling
N_BEFORE: int = 6                       # pre-Z₂ parent integer (Pillar 537)

# ---------------------------------------------------------------------------
# ENS anatomy constants (empirical, from published literature)
# ---------------------------------------------------------------------------
ENS_NEURON_COUNT_LOW: int = 100_000_000   # lower bound — ~100 million neurons
ENS_NEURON_COUNT_HIGH: int = 500_000_000  # upper bound — ~500 million neurons
ENS_NEURON_COUNT_MID: int = (ENS_NEURON_COUNT_LOW + ENS_NEURON_COUNT_HIGH) // 2

SEROTONIN_GUT_FRACTION: float = 0.925    # ~90–95 % of body serotonin produced in gut
DOPAMINE_GUT_FRACTION: float = 0.50      # ~50 % of body dopamine produced in gut
NEUROTRANSMITTER_TYPES: int = 30         # ENS uses ≥30 neurotransmitter types (same as CNS)

SPINAL_CORD_NEURON_COUNT: int = 69_000_000  # ~69 million spinal cord neurons (lit. estimate)
VAGUS_NERVE_MAX_SPEED_MS: float = 120.0   # max classical nerve conduction speed (m/s)

# ---------------------------------------------------------------------------
# Geometric constants — body core coordinates
# ---------------------------------------------------------------------------
SUB_UMBILICAL_DISTANCE_CM: float = 4.4   # ~1.74 in = ~4.4 cm below navel
SUB_UMBILICAL_DISTANCE_IN: float = 1.74  # inches below umbilicus

# Approximate toroidal model of the human torso (cm)
TORSO_MAJOR_RADIUS_CM: float = 15.0     # R — distance from torso axis to tube centre
TORSO_MINOR_RADIUS_CM: float = 10.0     # r — tube cross-section radius


# ---------------------------------------------------------------------------
# Toroidal geometry
# ---------------------------------------------------------------------------

def torus_surface_point(
    sigma: float,
    phi: float,
    R: float = TORSO_MAJOR_RADIUS_CM,
    r: float = TORSO_MINOR_RADIUS_CM,
) -> tuple[float, float, float]:
    """Return Cartesian coordinates (x, y, z) of a point on the torus surface.

    Parameters
    ----------
    sigma : float
        Poloidal angle (minor loop), radians.
    phi : float
        Toroidal angle (major loop), radians.
    R : float
        Major radius (cm).  Defaults to torso model value.
    r : float
        Minor radius (cm).  Defaults to torso model value.

    Returns
    -------
    tuple[float, float, float]
        (x, y, z) in cm.
    """
    if R <= 0 or r <= 0:
        raise ValueError("Torus radii must be positive")
    x = (R + r * math.cos(sigma)) * math.cos(phi)
    y = (R + r * math.cos(sigma)) * math.sin(phi)
    z = r * math.sin(sigma)
    return x, y, z


def torus_vector_field_integral(
    n_sigma: int = 360,
    n_phi: int = 360,
) -> tuple[float, float, float]:
    """Numerically integrate the symmetric toroidal flux vector over the surface.

    In a symmetric torus, the net integral of any antisymmetric component is
    exactly zero by symmetry.  This function verifies the null condition
    numerically by computing the discrete Riemann sum of the surface normal
    vector field and confirming it vanishes to floating-point precision.

    Returns
    -------
    tuple[float, float, float]
        (Fx_sum, Fy_sum, Fz_sum) — should be ≈ (0, 0, 0).
    """
    if n_sigma < 2 or n_phi < 2:
        raise ValueError("Integration resolution must be ≥ 2 in each dimension")

    d_sigma = 2 * math.pi / n_sigma
    d_phi = 2 * math.pi / n_phi

    Fx = Fy = Fz = 0.0
    for i in range(n_sigma):
        sigma = i * d_sigma
        for j in range(n_phi):
            phi = j * d_phi
            x, y, z = torus_surface_point(sigma, phi)
            Fx += x * d_sigma * d_phi
            Fy += y * d_sigma * d_phi
            Fz += z * d_sigma * d_phi

    # Normalise by surface area element scale
    area = (2 * math.pi) ** 2
    return Fx / area, Fy / area, Fz / area


def toroidal_null_condition(tolerance: float = 1e-6) -> dict[str, Any]:
    """Verify that the toroidal vector integral vanishes (null point condition).

    Returns
    -------
    dict with keys:
        Fx, Fy, Fz : float — integrated vector components
        null_satisfied : bool — True if |F| < tolerance
        sub_umbilical_cm : float — physical location of null point
        sub_umbilical_in : float
    """
    Fx, Fy, Fz = torus_vector_field_integral(n_sigma=180, n_phi=180)
    magnitude = math.sqrt(Fx**2 + Fy**2 + Fz**2)
    return {
        "Fx": Fx,
        "Fy": Fy,
        "Fz": Fz,
        "magnitude": magnitude,
        "null_satisfied": magnitude < tolerance,
        "sub_umbilical_cm": SUB_UMBILICAL_DISTANCE_CM,
        "sub_umbilical_in": SUB_UMBILICAL_DISTANCE_IN,
    }


# ---------------------------------------------------------------------------
# ENS functional metrics
# ---------------------------------------------------------------------------

def ens_autonomy_score(vagal_signal_fraction: float = 0.0) -> dict[str, Any]:
    """Quantify ENS autonomy relative to vagal input.

    The ENS can sustain all core digestive, immune, and neuroendocrine
    functions without any vagal input.  This function models autonomy as
    a φ-debt metric: the residual functional capacity after vagal disconnection.

    Parameters
    ----------
    vagal_signal_fraction : float
        Fraction of ENS activity attributed to vagal (cranial) input [0, 1].
        0.0 = fully autonomous; 1.0 = fully cranially driven.

    Returns
    -------
    dict with keys:
        vagal_fraction : float
        autonomous_fraction : float
        phi_autonomy : float — φ₀-normalised autonomy (autonomous_fraction / PHI0)
        status : str
    """
    if not 0.0 <= vagal_signal_fraction <= 1.0:
        raise ValueError("vagal_signal_fraction must be in [0, 1]")

    autonomous = 1.0 - vagal_signal_fraction
    phi_autonomy = autonomous / PHI0  # normalised against radion attractor ceiling

    if phi_autonomy >= 1.0:
        status = "FULLY_AUTONOMOUS — exceeds φ₀ ceiling; fully independent of cranial input"
    elif phi_autonomy >= C_S:
        status = "HIGH_AUTONOMY — enteric network operating above braided sound-speed threshold"
    else:
        status = "PARTIAL_AUTONOMY — vagal modulation dominant"

    return {
        "vagal_fraction": vagal_signal_fraction,
        "autonomous_fraction": autonomous,
        "phi_autonomy": phi_autonomy,
        "status": status,
    }


def gut_brain_reaction_lag(
    stimulus_distance_m: float = 0.5,
    ens_local_reaction_ms: float = 1.0,
    vagal_conduction_speed_ms: float = 80.0,
) -> dict[str, Any]:
    """Compute the temporal lag between gut-first vs cranial-first threat response.

    The ENS responds via local electrochemical shifts at the stimulus site
    before the ascending vagal signal reaches the brainstem.  The local ENS
    reaction is essentially on-site (millisecond-scale), whereas the vagal
    signal must travel the craniocaudal distance.

    Parameters
    ----------
    stimulus_distance_m : float
        Approximate distance from the abdominal core to the brainstem (metres).
    ens_local_reaction_ms : float
        Local ENS electrochemical reaction time at the stimulus site (ms).
        This is an on-site process — no long-range transmission required.
        Literature estimates: ~1 ms for fast ionotropic responses.
    vagal_conduction_speed_ms : float
        Vagus nerve ascending conduction speed (m/s).

    Returns
    -------
    dict with keys:
        cranial_arrival_ms : float — time for signal to reach brainstem (ms)
        ens_local_response_ms : float — time for local ENS response (ms)
        lag_ms : float — cranial arrives this many ms *after* ENS has reacted
        gut_is_faster : bool
    """
    if stimulus_distance_m <= 0:
        raise ValueError("stimulus_distance_m must be positive")
    if ens_local_reaction_ms <= 0:
        raise ValueError("ens_local_reaction_ms must be positive")
    if vagal_conduction_speed_ms <= 0:
        raise ValueError("vagal_conduction_speed_ms must be positive")

    # Time for ascending vagal signal to travel to brainstem (ms)
    cranial_arrival_ms = (stimulus_distance_m / vagal_conduction_speed_ms) * 1000.0

    lag_ms = cranial_arrival_ms - ens_local_reaction_ms
    return {
        "cranial_arrival_ms": cranial_arrival_ms,
        "ens_local_response_ms": ens_local_reaction_ms,
        "lag_ms": lag_ms,
        "gut_is_faster": lag_ms > 0,
    }


def ens_serotonin_production(
    total_body_serotonin_mg: float = 10.0,
) -> dict[str, Any]:
    """Compute ENS serotonin production and residual cranial fraction.

    Parameters
    ----------
    total_body_serotonin_mg : float
        Total daily serotonin synthesis in the body (mg).

    Returns
    -------
    dict with keys:
        gut_serotonin_mg : float
        cranial_serotonin_mg : float
        gut_fraction : float
        neurotransmitter_types : int
    """
    if total_body_serotonin_mg <= 0:
        raise ValueError("total_body_serotonin_mg must be positive")

    gut_mg = total_body_serotonin_mg * SEROTONIN_GUT_FRACTION
    cranial_mg = total_body_serotonin_mg - gut_mg
    return {
        "gut_serotonin_mg": gut_mg,
        "cranial_serotonin_mg": cranial_mg,
        "gut_fraction": SEROTONIN_GUT_FRACTION,
        "neurotransmitter_types": NEUROTRANSMITTER_TYPES,
    }


def ens_phi_coherence(
    neuron_count: float = float(ENS_NEURON_COUNT_MID),
    firing_synchrony: float = 0.5,
) -> dict[str, Any]:
    """Compute a φ-coherence metric for the enteric neural network.

    The φ-coherence is defined analogously to neural_phi_coherence in
    src/neuroscience/cognition.py but calibrated to the ENS scale.
    A synchrony of PHI0 ≈ 73.9 % represents the radion attractor ceiling.

    Parameters
    ----------
    neuron_count : float
        Active ENS neuron count.
    firing_synchrony : float
        Fraction of neurons firing in synchrony [0, 1].

    Returns
    -------
    dict with keys:
        phi_coherence : float
        phi_debt : float — gap between observed synchrony and PHI0 ceiling
        neuron_count : float
        status : str
    """
    if not 0.0 <= firing_synchrony <= 1.0:
        raise ValueError("firing_synchrony must be in [0, 1]")
    if neuron_count <= 0:
        raise ValueError("neuron_count must be positive")

    # Scale factor: log(neuron_count) / log(ENS_NEURON_COUNT_HIGH)
    scale = math.log(neuron_count) / math.log(ENS_NEURON_COUNT_HIGH)
    phi_coherence = firing_synchrony * scale
    phi_debt = max(0.0, PHI0 - phi_coherence)

    if phi_coherence >= PHI0:
        status = "AT_OR_ABOVE_PHI0_CEILING"
    elif phi_coherence >= C_S:
        status = "ABOVE_BRAIDED_SOUND_SPEED_THRESHOLD"
    else:
        status = "BELOW_THRESHOLD"

    return {
        "phi_coherence": phi_coherence,
        "phi_debt": phi_debt,
        "neuron_count": neuron_count,
        "firing_synchrony": firing_synchrony,
        "phi0_ceiling": PHI0,
        "status": status,
    }


# ---------------------------------------------------------------------------
# KK biophysical coupling
# ---------------------------------------------------------------------------

def kk_bio_coupling_strength(
    neural_density_per_cm3: float = 1e6,
    field_frequency_hz: float = 0.1,
) -> dict[str, Any]:
    """Estimate the KK-analogy bio-coupling strength at the abdominal core.

    This is a geometric analogy model, NOT a derived physics prediction.
    The coupling strength is defined as the product of the normalised neural
    density and the φ₀-weighted field frequency, scaled by K_CS.

    Parameters
    ----------
    neural_density_per_cm3 : float
        Neural density at the ENS core (neurons per cm³).
    field_frequency_hz : float
        Dominant low-frequency electromagnetic oscillation at the core (Hz).

    Returns
    -------
    dict with keys:
        coupling_strength : float
        kk_scale_factor : float — 1/K_CS weight
        phi0_weight : float
        status : str — epistemic label
    """
    if neural_density_per_cm3 <= 0:
        raise ValueError("neural_density_per_cm3 must be positive")
    if field_frequency_hz <= 0:
        raise ValueError("field_frequency_hz must be positive")

    # Normalise density to log scale
    log_density = math.log10(neural_density_per_cm3)
    # KK scale factor: each KK mode contributes 1/K_CS
    kk_scale = 1.0 / K_CS
    # φ₀ weight — radion attractor
    phi0_weight = PHI0
    # Coupling: dimensionless analogy index
    coupling = kk_scale * phi0_weight * log_density * math.log(1.0 + field_frequency_hz)

    return {
        "coupling_strength": coupling,
        "kk_scale_factor": kk_scale,
        "phi0_weight": phi0_weight,
        "neural_density_per_cm3": neural_density_per_cm3,
        "field_frequency_hz": field_frequency_hz,
        "status": (
            "ADJACENT TRACK — geometric analogy only; "
            "not a causal KK-physics claim"
        ),
    }


# ---------------------------------------------------------------------------
# Embryological link
# ---------------------------------------------------------------------------

def neural_crest_migration_ratio() -> dict[str, Any]:
    """Compute the vagal/sacral neural crest cell migration ratio.

    Vagal neural crest cells (NCC) travel the full craniocaudal length L_CR.
    Sacral NCC travel approximately L_CR / n_w (the distal fraction).
    The ratio sacral/vagal ≈ 1/n_w = 1/5 is noted as a structural
    geometric curiosity — a coincidence with the KK winding number N_W = 5.

    Returns
    -------
    dict with keys:
        n_w : int
        vagal_fraction : float  (normalised to 1.0)
        sacral_fraction : float (≈ 1/N_W)
        ratio_sacral_vagal : float
        n_gen : int
        n_before : int
        note : str
    """
    vagal_fraction = 1.0
    sacral_fraction = 1.0 / N_W
    return {
        "n_w": N_W,
        "vagal_fraction": vagal_fraction,
        "sacral_fraction": sacral_fraction,
        "ratio_sacral_vagal": sacral_fraction / vagal_fraction,
        "n_gen": 3,
        "n_before": N_BEFORE,
        "note": (
            "sacral/vagal ≈ 1/N_W = 1/5 is a geometric coincidence noted as "
            "a curiosity; it is NOT a causal KK prediction."
        ),
    }


def embryological_kk_link() -> dict[str, Any]:
    """Summarise the embryological–KK geometric link for the ENS.

    Neural crest cell (NCC) migration during weeks 3–7 of gestation populates
    the enteric plexuses.  The pre-Z₂ parent integer n_before = 6 (Pillar 537)
    equals 2 × N_gen = 2 × 3.  This module notes that the ENS arises from
    exactly N_gen = 3 identified neural crest sub-populations (vagal, truncal,
    sacral) — a structural parallel to the 3 SM generations encoded in n_before.

    Returns
    -------
    dict with keys:
        n_generations : int
        n_before : int
        ncc_subpopulations : list[str]
        parallel_note : str
        epistemic_status : str
    """
    ncc_subpops = ["vagal", "truncal", "sacral"]
    return {
        "n_generations": 3,
        "n_before": N_BEFORE,
        "ncc_subpopulations": ncc_subpops,
        "n_ncc_subpopulations": len(ncc_subpops),
        "parallel_note": (
            "N_gen = 3 SM generations (Pillar 205) equals the count of "
            "neural crest sub-populations that form the ENS.  "
            "n_before = 2×N_gen = 6 (Pillar 537) encodes the pre-Z₂ braid "
            "parent.  This structural parallel is noted as a geometric "
            "curiosity; no causal claim is made."
        ),
        "epistemic_status": "GEOMETRIC_CURIOSITY — not a physics prediction",
    }


# ---------------------------------------------------------------------------
# Comparison table
# ---------------------------------------------------------------------------

def enteric_vs_cranial_comparison() -> list[dict[str, Any]]:
    """Return a structured comparison of cranial vs enteric brain attributes.

    Returns
    -------
    list of dicts, each with keys:
        attribute, cranial_brain, enteric_brain, source_note
    """
    return [
        {
            "attribute": "neuron_count",
            "cranial_brain": 86_000_000_000,
            "enteric_brain": ENS_NEURON_COUNT_MID,
            "source_note": "Cleveland Clinic / Stanford Medicine",
        },
        {
            "attribute": "serotonin_production_fraction",
            "cranial_brain": 1.0 - SEROTONIN_GUT_FRACTION,
            "enteric_brain": SEROTONIN_GUT_FRACTION,
            "source_note": "Cleveland Clinic",
        },
        {
            "attribute": "dopamine_production_fraction",
            "cranial_brain": 1.0 - DOPAMINE_GUT_FRACTION,
            "enteric_brain": DOPAMINE_GUT_FRACTION,
            "source_note": "Cleveland Clinic",
        },
        {
            "attribute": "autonomous_without_vagus",
            "cranial_brain": False,
            "enteric_brain": True,
            "source_note": "Hopkins Medicine / PMC",
        },
        {
            "attribute": "glial_support_cells",
            "cranial_brain": "astrocytes",
            "enteric_brain": "enteric glial cells (EGCs)",
            "source_note": "PMC — EGC structural homology to astrocytes",
        },
        {
            "attribute": "embryological_origin",
            "cranial_brain": "neural tube (cranial)",
            "enteric_brain": "vagal + sacral neural crest cells",
            "source_note": "PMC — neural crest migration",
        },
        {
            "attribute": "primary_function",
            "cranial_brain": "cognition / voluntary motor control",
            "enteric_brain": "visceral homeostasis / emotional signalling",
            "source_note": "Hopkins Medicine",
        },
    ]


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def pillar538_summary() -> dict[str, Any]:
    """Return a machine-readable summary of Pillar 538.

    Returns
    -------
    dict with keys:
        pillar, title, status, kk_constants, ens_constants, geometry,
        toroidal_null, ens_autonomy, embryological_link, comparison_table
    """
    toroidal = toroidal_null_condition()
    autonomy = ens_autonomy_score(vagal_signal_fraction=0.0)
    emb = embryological_kk_link()

    return {
        "pillar": 538,
        "title": "Enteric Neural Core: ENS as Second Brain and KK Biophysical Coupling",
        "status": "ADJACENT RESEARCH TRACK (non-hardgate)",
        "kk_constants": {
            "N_W": N_W,
            "K_CS": K_CS,
            "C_S": C_S,
            "PHI0": PHI0,
            "N_BEFORE": N_BEFORE,
        },
        "ens_constants": {
            "neuron_count_low": ENS_NEURON_COUNT_LOW,
            "neuron_count_high": ENS_NEURON_COUNT_HIGH,
            "serotonin_gut_fraction": SEROTONIN_GUT_FRACTION,
            "dopamine_gut_fraction": DOPAMINE_GUT_FRACTION,
            "neurotransmitter_types": NEUROTRANSMITTER_TYPES,
        },
        "geometry": {
            "sub_umbilical_cm": SUB_UMBILICAL_DISTANCE_CM,
            "sub_umbilical_in": SUB_UMBILICAL_DISTANCE_IN,
            "torso_major_radius_cm": TORSO_MAJOR_RADIUS_CM,
            "torso_minor_radius_cm": TORSO_MINOR_RADIUS_CM,
        },
        "toroidal_null": toroidal,
        "ens_autonomy": autonomy,
        "embryological_link": emb,
        "comparison_table": enteric_vs_cranial_comparison(),
    }
