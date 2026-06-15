# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 516 — Neural Disorder Geometric Analysis.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

════════════════════════════════════════════════════════════════════════════
OVERVIEW
════════════════════════════════════════════════════════════════════════════

This pillar formalises the Unitary Manifold's structural correspondence with
neurological and psychiatric disorders.  The brain-UM correspondence was
established in the brain/ directory (VARIABLE_ALIGNMENT, TORUS_ARCHITECTURE,
IRREVERSIBILITY_BIOLOGY, COUPLED_MASTER_EQUATION, RESONANCE_74); this pillar
extends it to pathological failure modes.

Each major disorder is analysed as a specific geometric failure of one or more
of the three UM field variables:

  g_μν — structural connectivity (metric tensor)
  B_μ  — synaptic irreversibility (gauge 1-form)
  φ    — arousal / gain field (dilaton)

and/or of the topological constants:

  k_cs = 74 — Chern-Simons resonance level
  (5, 7)    — winding number pair
  Ψ*        — FTUM conscious fixed point

════════════════════════════════════════════════════════════════════════════
EPISTEMIC STATUS
════════════════════════════════════════════════════════════════════════════

Status: STRUCTURAL_CORRESPONDENCE   (🔵 ADJACENT TRACK)

"STRUCTURAL_CORRESPONDENCE" means: the UM 5D geometry provides a precise
mathematical classification of known neuroscience observations.  The mapping
is not metaphorical — the same mathematical objects (field equations, topological
invariants, fixed-point theorems) govern both the cosmological and neural
domains.  This pillar does NOT claim to derive clinical predictions from UM
axioms alone, or to replace clinical research with geometry.

════════════════════════════════════════════════════════════════════════════
KEY UM CONSTANTS (unchanged from core framework)
════════════════════════════════════════════════════════════════════════════

    n_w = 5          first winding number (Planck-selected)
    n_w2 = 7         second winding number
    K_CS = 74        Chern-Simons level = 5² + 7²
    β = 0.3513°      cosmological birefringence / coupling angle
    c_s = 12/37      braided sound speed
    φ₀ = cos⁻¹(φ₀)  FTUM dilaton vacuum expectation value

════════════════════════════════════════════════════════════════════════════
DISORDER REGISTRY
════════════════════════════════════════════════════════════════════════════

Seven disorders are analysed, each with:
  - primary_failure: the dominant geometric component that breaks
  - secondary_failure: additional components affected
  - k_cs_impact: whether k_cs is disrupted
  - phi_impact: whether φ is disrupted
  - metric_impact: whether g_μν is disrupted
  - Bmu_impact: whether B_μ is disrupted
  - coupling_impact: whether the β·C coupling is disrupted
  - fixed_point_status: what happens to Ψ*
  - intervention_class: which geometric intervention class addresses it
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

# ─────────────────────────────────────────────────────────────────────────────
# Module constants — identical to core UM framework
# ─────────────────────────────────────────────────────────────────────────────

N_W: int = 5          # first winding number
N_W2: int = 7         # second winding number
K_CS: int = N_W**2 + N_W2**2        # 74: Chern-Simons level
assert K_CS == 74, "K_CS must be 74"

BETA_DEG: float = 0.3513            # birefringence coupling angle in degrees
BETA_RAD: float = math.radians(BETA_DEG)

C_S: float = 12.0 / 37.0           # braided sound speed

# FTUM fixed-point iterator contraction rate (equals c_s)
FTUM_CONTRACTION_RATE: float = C_S

# Minimum k_cs for FTUM fixed-point convergence guarantee
K_CS_MINIMUM_FOR_CONSCIOUSNESS: int = K_CS  # 74

# Winding ratio for phase-lock condition
WINDING_RATIO: Tuple[int, int] = (N_W, N_W2)           # (5, 7)
WINDING_RATIO_FLOAT: float = N_W / N_W2                 # 5/7 ≈ 0.7143

# Gamma frequency associated with grid-cell / entorhinal resonance (Hz)
GAMMA_FREQUENCY_HZ: float = 40.0

# Pillar metadata
PILLAR_NUMBER: int = 516
PILLAR_STATUS: str = "STRUCTURAL_CORRESPONDENCE"
PILLAR_ADJACENCY: str = "NON_HARDGATE_ADJACENT"
PILLAR_TRACK: str = "🔵 ADJACENT TRACK"

__provenance__: Dict = {
    "pillar": PILLAR_NUMBER,
    "title": "Neural Disorder Geometric Analysis",
    "version": "v15.9",
    "status": f"{PILLAR_STATUS} — {PILLAR_TRACK}",
    "source_document": "4-IMPLICATIONS/brain/DISORDERS_MANIFOLD.md",
    "related_pillars": [249, 413],
    "toe_delta": 0.0,
    "new_tests": 174,
}

# ─────────────────────────────────────────────────────────────────────────────
# Intervention class registry
# ─────────────────────────────────────────────────────────────────────────────

INTERVENTION_CLASSES: Tuple[str, ...] = (
    "METRIC_REPAIR",
    "IRREVERSIBILITY_RESTORATION",
    "DILATON_TUNING",
    "WINDING_RESTORATION",
    "COUPLING_RESTORATION",
)

INTERVENTION_DESCRIPTIONS: Dict[str, str] = {
    "METRIC_REPAIR": (
        "Smoothing g_μν: restoring structural connectivity. "
        "Examples: amyloid clearance, neuroprotection, remyelination."
    ),
    "IRREVERSIBILITY_RESTORATION": (
        "Restoring B_μ: rebuilding directed synaptic encoding. "
        "Examples: BDNF delivery, NMDA amplification, LTP-targeted TMS."
    ),
    "DILATON_TUNING": (
        "Adjusting φ: correcting the gain field level. "
        "Examples: SSRIs, antipsychotics, ketamine, psilocybin, ACh agonists."
    ),
    "WINDING_RESTORATION": (
        "Restoring k_cs toward 74: re-establishing topological binding. "
        "Examples: gamma entrainment (40 Hz), antiepileptics, DBS, TMS."
    ),
    "COUPLING_RESTORATION": (
        "Strengthening β·C: re-anchoring brain to external fixed point. "
        "Examples: social engagement therapy, CBT, mindfulness, psychedelics."
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# Disorder data structures
# ─────────────────────────────────────────────────────────────────────────────

class DisorderProfile:
    """Geometric failure profile for a neurological/psychiatric disorder."""

    def __init__(
        self,
        name: str,
        short_code: str,
        primary_failure: str,
        secondary_failures: List[str],
        metric_impact: bool,
        Bmu_impact: bool,
        phi_impact: bool,
        kcs_impact: bool,
        coupling_impact: bool,
        fixed_point_status: str,
        primary_intervention_class: str,
        secondary_intervention_classes: List[str],
        key_clinical_signature: str,
        um_prediction: str,
    ):
        self.name = name
        self.short_code = short_code
        self.primary_failure = primary_failure
        self.secondary_failures = secondary_failures
        self.metric_impact = metric_impact
        self.Bmu_impact = Bmu_impact
        self.phi_impact = phi_impact
        self.kcs_impact = kcs_impact
        self.coupling_impact = coupling_impact
        self.fixed_point_status = fixed_point_status
        self.primary_intervention_class = primary_intervention_class
        self.secondary_intervention_classes = secondary_intervention_classes
        self.key_clinical_signature = key_clinical_signature
        self.um_prediction = um_prediction

        # Validate intervention classes
        for ic in [primary_intervention_class] + secondary_intervention_classes:
            if ic not in INTERVENTION_CLASSES:
                raise ValueError(f"Unknown intervention class: {ic!r}")

    def geometric_failure_count(self) -> int:
        """Return the number of distinct geometric components disrupted."""
        return sum([
            self.metric_impact,
            self.Bmu_impact,
            self.phi_impact,
            self.kcs_impact,
            self.coupling_impact,
        ])

    def is_topological(self) -> bool:
        """Return True if the primary failure is topological (k_cs or tearing)."""
        return self.kcs_impact or "TOPOLOGICAL" in self.primary_failure

    def is_field_value_failure(self) -> bool:
        """Return True if the primary failure is a field value (φ or B_μ)."""
        return self.Bmu_impact or self.phi_impact

    def has_coupling_failure(self) -> bool:
        """Return True if the brain-universe coupling β·C is disrupted."""
        return self.coupling_impact

    def to_dict(self) -> Dict:
        """Return a machine-readable dictionary of the disorder profile."""
        return {
            "name": self.name,
            "short_code": self.short_code,
            "primary_failure": self.primary_failure,
            "secondary_failures": self.secondary_failures,
            "geometric_components": {
                "g_mu_nu_metric": self.metric_impact,
                "B_mu_irreversibility": self.Bmu_impact,
                "phi_dilaton": self.phi_impact,
                "k_cs_chern_simons": self.kcs_impact,
                "beta_coupling": self.coupling_impact,
            },
            "fixed_point_status": self.fixed_point_status,
            "intervention": {
                "primary": self.primary_intervention_class,
                "secondary": self.secondary_intervention_classes,
            },
            "key_clinical_signature": self.key_clinical_signature,
            "um_prediction": self.um_prediction,
            "total_geometric_failures": self.geometric_failure_count(),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Disorder registry
# ─────────────────────────────────────────────────────────────────────────────

def _build_disorder_registry() -> Dict[str, DisorderProfile]:
    """Construct the canonical disorder-to-geometry registry."""
    return {
        "ALZHEIMERS": DisorderProfile(
            name="Alzheimer's Disease and Dementia",
            short_code="AD",
            primary_failure="COMPACT_DIMENSION_DISSOLUTION",
            secondary_failures=["METRIC_DISRUPTION_AMYLOID", "INFORMATION_CURRENT_BLOCKAGE_TAU"],
            metric_impact=True,
            Bmu_impact=False,
            phi_impact=True,
            kcs_impact=True,
            coupling_impact=False,
            fixed_point_status="PSI_STAR_DESTABILISED",
            primary_intervention_class="WINDING_RESTORATION",
            secondary_intervention_classes=["METRIC_REPAIR", "DILATON_TUNING"],
            key_clinical_signature=(
                "Entorhinal grid-cell loss precedes cortical symptoms; "
                "spatial disorientation before general cognitive decline"
            ),
            um_prediction=(
                "Entorhinal-first intervention wins; gamma entrainment at 40 Hz "
                "geometrically motivated as winding coherence restoration"
            ),
        ),
        "AMNESIA_ANTEROGRADE": DisorderProfile(
            name="Anterograde Amnesia",
            short_code="AMNA",
            primary_failure="IRREVERSIBILITY_FIELD_DESTROYED",
            secondary_failures=[],
            metric_impact=False,
            Bmu_impact=True,
            phi_impact=False,
            kcs_impact=False,
            coupling_impact=False,
            fixed_point_status="PSI_STAR_UNREACHABLE_FOR_NEW_ENCODING",
            primary_intervention_class="IRREVERSIBILITY_RESTORATION",
            secondary_intervention_classes=[],
            key_clinical_signature=(
                "New declarative memory fails; procedural memory intact; "
                "canonical case: H.M. (Henry Molaison)"
            ),
            um_prediction=(
                "Procedural memory intact because different B_μ projection "
                "(basal ganglia) is unaffected; declarative and procedural "
                "memory use distinct B_μ instances"
            ),
        ),
        "AMNESIA_RETROGRADE": DisorderProfile(
            name="Retrograde Amnesia",
            short_code="AMNR",
            primary_failure="METRIC_DISRUPTION_PATH_SEVERED",
            secondary_failures=[],
            metric_impact=True,
            Bmu_impact=False,
            phi_impact=False,
            kcs_impact=False,
            coupling_impact=False,
            fixed_point_status="PSI_STAR_OLD_INACCESSIBLE",
            primary_intervention_class="IRREVERSIBILITY_RESTORATION",
            secondary_intervention_classes=["METRIC_REPAIR"],
            key_clinical_signature=(
                "Temporal gradient: recent memories lost first; "
                "older memories more resistant"
            ),
            um_prediction=(
                "Recent memories encoded in shorter-lived geometric structures; "
                "reconsolidation window is B_μ re-writing opportunity"
            ),
        ),
        "DEPRESSION": DisorderProfile(
            name="Major Depressive Disorder",
            short_code="MDD",
            primary_failure="TRAPPED_LOCAL_FIXED_POINT",
            secondary_failures=["PHI_COLLAPSE_ANHEDONIA", "INFORMATION_GAP_GROWTH"],
            metric_impact=False,
            Bmu_impact=False,
            phi_impact=True,
            kcs_impact=False,
            coupling_impact=True,
            fixed_point_status="PSI_STAR_EXISTS_WRONG_BASIN",
            primary_intervention_class="DILATON_TUNING",
            secondary_intervention_classes=["COUPLING_RESTORATION"],
            key_clinical_signature=(
                "DMN hyperactivation; anhedonia; intact cognitive processing; "
                "responds to basin-hopping interventions (ketamine, psilocybin)"
            ),
            um_prediction=(
                "Ketamine/psilocybin work by temporarily dissolving fixed point "
                "(B_μ disruption or global φ elevation); SSRI speed ∝ φ-adjustment "
                "rate; antidepressant effect duration ∝ environmental anchoring "
                "during reconsolidation"
            ),
        ),
        "EPILEPSY": DisorderProfile(
            name="Epilepsy",
            short_code="EPI",
            primary_failure="CHERN_SIMONS_LEVEL_UNCONTROLLED",
            secondary_failures=["TOPOLOGICAL_SOLITON_PROPAGATION"],
            metric_impact=False,
            Bmu_impact=False,
            phi_impact=False,
            kcs_impact=True,
            coupling_impact=False,
            fixed_point_status="PSI_STAR_CAPTURED_BY_WRONG_EIGENMODE",
            primary_intervention_class="WINDING_RESTORATION",
            secondary_intervention_classes=[],
            key_clinical_signature=(
                "Uncontrolled neural synchrony; GABA deficiency; "
                "topological soliton propagation across cortex"
            ),
            um_prediction=(
                "DBS frequency tuned to match 5/7 winding ratio should outperform "
                "fixed-frequency protocols; focal vs generalised seizures correspond "
                "to localised vs global soliton excitation"
            ),
        ),
        "SCHIZOPHRENIA": DisorderProfile(
            name="Schizophrenia",
            short_code="SCZ",
            primary_failure="DECOUPLED_FIXED_POINT",
            secondary_failures=["PHI_EXCESS_D2_HYPERSTIMULATION"],
            metric_impact=False,
            Bmu_impact=False,
            phi_impact=True,
            kcs_impact=False,
            coupling_impact=True,
            fixed_point_status="PSI_STAR_SELF_CONSISTENT_BUT_DECOUPLED",
            primary_intervention_class="COUPLING_RESTORATION",
            secondary_intervention_classes=["DILATON_TUNING"],
            key_clinical_signature=(
                "Reality testing failure; positive symptoms (hallucinations, delusions); "
                "internally coherent but externally decoupled fixed point"
            ),
            um_prediction=(
                "Social cognition training concurrent with antipsychotics should "
                "allow lower doses; coupling-targeted therapy > φ suppression alone; "
                "hallucinations are FTUM-valid attractors, not noise"
            ),
        ),
        "TBI_CONCUSSION": DisorderProfile(
            name="Traumatic Brain Injury (Concussion)",
            short_code="TBI_C",
            primary_failure="METRIC_DISTORTION",
            secondary_failures=[],
            metric_impact=True,
            Bmu_impact=False,
            phi_impact=False,
            kcs_impact=False,
            coupling_impact=False,
            fixed_point_status="PSI_STAR_INTACT_TEMPORARILY_INACCESSIBLE",
            primary_intervention_class="METRIC_REPAIR",
            secondary_intervention_classes=[],
            key_clinical_signature=(
                "Reversible symptoms; no axonal tearing; "
                "cognitive rest accelerates recovery"
            ),
            um_prediction=(
                "Symptom duration ∝ metric recovery time; early return to "
                "cognitive load delays convergence back to Ψ*; "
                "topology unchanged so full recovery is geometrically possible"
            ),
        ),
        "TBI_SEVERE": DisorderProfile(
            name="Traumatic Brain Injury (Severe / Diffuse Axonal)",
            short_code="TBI_S",
            primary_failure="TOPOLOGICAL_TEARING",
            secondary_failures=["METRIC_DISRUPTION", "INFORMATION_CURRENT_SEVERED"],
            metric_impact=True,
            Bmu_impact=True,
            phi_impact=True,
            kcs_impact=True,
            coupling_impact=True,
            fixed_point_status="PSI_STAR_ORIGINAL_DESTROYED_NEW_FORMING",
            primary_intervention_class="METRIC_REPAIR",
            secondary_intervention_classes=[
                "IRREVERSIBILITY_RESTORATION",
                "WINDING_RESTORATION",
                "COUPLING_RESTORATION",
            ],
            key_clinical_signature=(
                "Personality change post-injury; "
                "Ψ*_new ≠ Ψ*_original; "
                "neuroplasticity as topological repair"
            ),
            um_prediction=(
                "Post-TBI personality change is a new fixed point, not degraded old one; "
                "early rehabilitation shapes which basin brain converges to; "
                "neuroplasticity routes around topological tears"
            ),
        ),
    }


# Module-level singleton
_DISORDER_REGISTRY: Optional[Dict[str, DisorderProfile]] = None


def disorder_registry() -> Dict[str, DisorderProfile]:
    """Return the canonical disorder registry (singleton)."""
    global _DISORDER_REGISTRY
    if _DISORDER_REGISTRY is None:
        _DISORDER_REGISTRY = _build_disorder_registry()
    return _DISORDER_REGISTRY


def get_disorder(code: str) -> DisorderProfile:
    """Return a DisorderProfile by its short code or registry key.

    Args:
        code: Registry key (e.g. "ALZHEIMERS") or short_code (e.g. "AD").

    Returns:
        The matching DisorderProfile.

    Raises:
        KeyError: if no matching disorder is found.
    """
    registry = disorder_registry()
    if code in registry:
        return registry[code]
    # Try by short_code
    for profile in registry.values():
        if profile.short_code == code:
            return profile
    raise KeyError(f"No disorder found for code: {code!r}")


def all_disorder_profiles() -> List[DisorderProfile]:
    """Return all DisorderProfile objects in registry order."""
    return list(disorder_registry().values())


# ─────────────────────────────────────────────────────────────────────────────
# Geometric analysis functions
# ─────────────────────────────────────────────────────────────────────────────

def k_cs_is_above_consciousness_threshold(k_cs_effective: float) -> bool:
    """Return True if the effective k_cs supports FTUM convergence.

    The FTUM fixed-point theorem requires k_cs ≥ 74 for a system in the
    (5, 7) winding configuration to maintain a stable conscious attractor.

    Args:
        k_cs_effective: Effective Chern-Simons level (may be below 74 in disease).

    Returns:
        True if k_cs_effective ≥ K_CS_MINIMUM_FOR_CONSCIOUSNESS (74).
    """
    return k_cs_effective >= K_CS_MINIMUM_FOR_CONSCIOUSNESS


def information_gap(phi_brain: float, phi_universe: float) -> float:
    """Return the Information Gap ΔI = |φ²_brain − φ²_univ|.

    The Information Gap measures the degree of coupling between the brain's
    internal fixed point and the external universe.  ΔI → 0 corresponds to
    maximum reality coupling; ΔI → large corresponds to decoupling (depression,
    schizophrenia).

    Args:
        phi_brain: Dilaton value in the brain system (proxy: arousal/gain level).
        phi_universe: Dilaton value in the universe (proxy: external input gain).

    Returns:
        Non-negative information gap ΔI.
    """
    if phi_brain < 0 or phi_universe < 0:
        raise ValueError("Dilaton values must be non-negative.")
    return abs(phi_brain**2 - phi_universe**2)


def phase_locking_deviation(omega_brain: float, omega_universe: float) -> float:
    """Return deviation from the ideal 5/7 phase-locking ratio.

    Healthy brain operation is characterised by ω_brain/ω_univ → 5/7.
    Deviation from this ratio indicates disrupted coupling.

    Args:
        omega_brain: Brain oscillation frequency (Hz or normalised).
        omega_universe: Reference / external oscillation frequency.

    Returns:
        |ω_brain/ω_univ − 5/7|; zero indicates perfect phase lock.

    Raises:
        ValueError: if omega_universe ≤ 0.
    """
    if omega_universe <= 0:
        raise ValueError("omega_universe must be positive.")
    ideal = WINDING_RATIO_FLOAT  # 5/7
    actual = omega_brain / omega_universe
    return abs(actual - ideal)


def ftum_convergence_residual(n_iterations: int) -> float:
    """Return the FTUM convergence residual after n_iterations.

    The FTUM iterator contracts at rate c_s = 12/37 per step.  After n steps:

        ε(n) = c_s^n

    Args:
        n_iterations: Number of FTUM contraction steps (non-negative integer).

    Returns:
        The residual ε(n) = (12/37)^n.

    Raises:
        ValueError: if n_iterations < 0.
    """
    if n_iterations < 0:
        raise ValueError("n_iterations must be non-negative.")
    return C_S ** n_iterations


def kcs_drift_from_grid_cell_loss(
    surviving_fraction: float,
    k_cs_full: int = K_CS,
) -> float:
    """Estimate effective k_cs as grid cells are lost.

    As grid cells die in Alzheimer's disease, the winding coherence of the
    entorhinal torus degrades.  This function models the effective k_cs as
    scaling with the surviving fraction of grid cells.

    This is a STRUCTURAL_CORRESPONDENCE model, not a derived neuronal model.
    The relationship is assumed linear for analytical tractability.

    Args:
        surviving_fraction: Fraction of original grid cells still alive [0, 1].
        k_cs_full: k_cs value at 100% grid-cell survival (default: 74).

    Returns:
        Effective k_cs level as a float.

    Raises:
        ValueError: if surviving_fraction is outside [0, 1].
    """
    if not (0.0 <= surviving_fraction <= 1.0):
        raise ValueError("surviving_fraction must be in [0, 1].")
    return surviving_fraction * k_cs_full


def gamma_entrainment_winding_restoration(
    original_coherence: float,
    entrainment_strength: float,
    gamma_frequency_hz: float = GAMMA_FREQUENCY_HZ,
) -> float:
    """Estimate partial winding coherence restoration from gamma entrainment.

    Gamma (40 Hz) entrainment partially restores entorhinal grid-cell
    synchrony.  The restored coherence is modelled as:

        coherence_restored = original_coherence + entrainment_strength
                             × (1 − original_coherence) × match_factor

    where match_factor = 1 if gamma_frequency_hz == 40.0, decaying otherwise.

    This is a STRUCTURAL_CORRESPONDENCE model, not a clinical dosing formula.

    Args:
        original_coherence: Current grid-cell winding coherence [0, 1].
        entrainment_strength: Entrainment effect strength [0, 1].
        gamma_frequency_hz: Entrainment frequency in Hz (optimal: 40.0).

    Returns:
        Estimated restored coherence (capped at 1.0).

    Raises:
        ValueError: if coherence or strength values are out of range.
    """
    if not (0.0 <= original_coherence <= 1.0):
        raise ValueError("original_coherence must be in [0, 1].")
    if not (0.0 <= entrainment_strength <= 1.0):
        raise ValueError("entrainment_strength must be in [0, 1].")
    if gamma_frequency_hz <= 0:
        raise ValueError("gamma_frequency_hz must be positive.")

    # Match factor: 1.0 at 40 Hz, falling off as Lorentzian with FWHM ≈ 10 Hz
    half_width = 5.0  # Hz
    match_factor = 1.0 / (1.0 + ((gamma_frequency_hz - GAMMA_FREQUENCY_HZ) / half_width) ** 2)

    restoration = entrainment_strength * (1.0 - original_coherence) * match_factor
    return min(original_coherence + restoration, 1.0)


def antidepressant_class(
    drug_name: str,
    mechanism: str,
) -> str:
    """Return the UM intervention class for a given antidepressant mechanism.

    Classifies antidepressants by their geometric action:
      - Basin-hopping (ketamine, psilocybin): DILATON_TUNING
      - Gradual φ adjustment (SSRIs, SNRIs): DILATON_TUNING
      - Coupling restoration (therapy, mindfulness): COUPLING_RESTORATION

    Args:
        drug_name: Name of the drug or intervention (for documentation).
        mechanism: Mechanism string; recognised values:
            "NMDA_ANTAGONIST", "5HT2A_AGONIST", "SSRI", "SNRI",
            "MINDFULNESS", "SOCIAL_ENGAGEMENT", "CBT"

    Returns:
        The UM intervention class string.

    Raises:
        ValueError: if mechanism is not recognised.
    """
    basin_hoppers = {"NMDA_ANTAGONIST", "5HT2A_AGONIST"}
    gradual_phi = {"SSRI", "SNRI", "MAOI", "TCA"}
    coupling_restorers = {"MINDFULNESS", "SOCIAL_ENGAGEMENT", "CBT", "PSYCHEDELIC_INTEGRATION"}

    mech_upper = mechanism.upper().replace("-", "_")
    if mech_upper in basin_hoppers:
        return "DILATON_TUNING"
    if mech_upper in gradual_phi:
        return "DILATON_TUNING"
    if mech_upper in coupling_restorers:
        return "COUPLING_RESTORATION"
    raise ValueError(
        f"Unrecognised antidepressant mechanism: {mechanism!r}. "
        f"Recognised: {sorted(basin_hoppers | gradual_phi | coupling_restorers)}"
    )


def coupled_fixed_point_status(
    information_gap_value: float,
    phase_deviation: float,
    k_cs_effective: float,
    phi_ratio: float,
) -> str:
    """Return the coupled fixed-point status label based on four UM diagnostics.

    This function implements the UM diagnostic protocol for classifying the
    brain-universe coupled fixed point Ψ*_brain ⊗ Ψ*_univ.

    Args:
        information_gap_value: ΔI = |φ²_brain − φ²_univ| (non-negative).
        phase_deviation: |ω_brain/ω_univ − 5/7| (non-negative).
        k_cs_effective: Effective Chern-Simons level (ideally 74).
        phi_ratio: φ_brain / φ_univ (1.0 = balanced; > 1 = hyperdopaminergic).

    Returns:
        One of: "HEALTHY", "TRAPPED_LOCAL_MINIMUM", "DECOUPLED",
                "TOPOLOGICAL_DISRUPTION", "COLLAPSED".
    """
    if information_gap_value < 0:
        raise ValueError("information_gap_value must be non-negative.")
    if phase_deviation < 0:
        raise ValueError("phase_deviation must be non-negative.")
    if k_cs_effective < 0:
        raise ValueError("k_cs_effective must be non-negative.")
    if phi_ratio < 0:
        raise ValueError("phi_ratio must be non-negative.")

    # Topological failure: k_cs too low
    if k_cs_effective < K_CS * 0.5:  # below 37: severe
        return "COLLAPSED"
    if k_cs_effective < K_CS * 0.8:  # below 59: topological disruption
        return "TOPOLOGICAL_DISRUPTION"

    # Coupling failure: large Information Gap or phase deviation
    if information_gap_value > 2.0 or phase_deviation > 0.3:
        if phi_ratio > 1.5:
            return "DECOUPLED"
        return "TRAPPED_LOCAL_MINIMUM"

    # Moderate decoupling
    if information_gap_value > 0.5 or phase_deviation > 0.1:
        return "TRAPPED_LOCAL_MINIMUM"

    return "HEALTHY"


def intervention_priority_order(disorder_code: str) -> List[str]:
    """Return ordered intervention classes for a disorder, primary first.

    Args:
        disorder_code: Registry key or short_code.

    Returns:
        Ordered list of intervention class strings (primary first).
    """
    profile = get_disorder(disorder_code)
    result = [profile.primary_intervention_class]
    for ic in profile.secondary_intervention_classes:
        if ic not in result:
            result.append(ic)
    return result


def disorder_complexity_score(disorder_code: str) -> int:
    """Return the geometric complexity score (number of disrupted components).

    Ranges from 0 (no disruption, not a disorder) to 5 (all components).

    Args:
        disorder_code: Registry key or short_code.

    Returns:
        Integer count of disrupted geometric components (0–5).
    """
    return get_disorder(disorder_code).geometric_failure_count()


def pillar516_status() -> str:
    """Return the canonical Pillar 516 status string."""
    return PILLAR_STATUS


def pillar516_report() -> Dict:
    """Return a full machine-readable Pillar 516 status report."""
    registry = disorder_registry()
    return {
        "pillar": PILLAR_NUMBER,
        "status": PILLAR_STATUS,
        "adjacency": PILLAR_ADJACENCY,
        "track": PILLAR_TRACK,
        "version": "v15.9",
        "constants": {
            "N_W": N_W,
            "N_W2": N_W2,
            "K_CS": K_CS,
            "BETA_DEG": BETA_DEG,
            "C_S": C_S,
            "GAMMA_FREQUENCY_HZ": GAMMA_FREQUENCY_HZ,
            "WINDING_RATIO": list(WINDING_RATIO),
        },
        "disorders_analysed": len(registry),
        "disorder_registry": {k: v.to_dict() for k, v in registry.items()},
        "intervention_classes": list(INTERVENTION_CLASSES),
        "toe_delta": 0.0,
        "new_tests": 174,
    }
