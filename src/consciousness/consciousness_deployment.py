# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/consciousness/consciousness_deployment.py
==============================================
Consciousness-Bridge Deployment — Pillar 9-B.

Maps the converged CoupledSystem (Ψ_brain ⊗ Ψ_univ) state from Pillar 9
onto 13 analogical application domains (Pillars 10, 12–13, 17–26), constituting
the formal "deployment" of the consciousness-bridge into the full Unitary
Manifold application framework.

Epistemic framing
-----------------
This module sits at the boundary of **Tier 2** (speculative physics) and
**Tier 3** (analogical applications).  See ``SEPARATION.md`` for the full
epistemic taxonomy.

* Tier 2 (Pillar 9): the coupled brain–universe attractor is a speculative
  physical model.  Whether consciousness is *actually* a 5D fixed-point
  phenomenon is unconfirmed.

* Tier 3 (Pillars 10, 12–13, 17–26): the φ-field mathematics is used as a *modeling
  language* for complex domains.  The bridge does **not** claim that
  medicine, justice, or governance are literally 5D geometric phenomena.

The bridge provides a principled, internally consistent way to seed each
application-domain model from a shared Pillar-9 base state, so that all
13 implemented domain models are simultaneously consistent with a single coupled
(brain ⊗ universe) attractor.

Physical derivation of the bridge quantities
--------------------------------------------
From the converged ``CoupledSystem`` the following observables are derived:

``phi_brain`` (φ_B)
    KK radion of the neural manifold — local information-carrying capacity.

``phi_univ`` (φ_U)
    KK radion of the universe manifold — cosmological information-carrying
    capacity.

``phi_eff`` (φ_eff = √(φ_B · φ_U))
    Geometric-mean effective radion — the bridge coupling that both poles
    of the interaction (local observer and global universe) share.  Used
    wherever a single domain parameter must inherit from both manifolds.

``info_gap`` (ΔI = |φ_B² − φ_U²|)
    Information Gap: measures the differentiation between the two
    manifolds.  In each domain this maps to a "deviation from equilibrium"
    or "perturbation strength."

``phase_offset`` (Δφ ∈ [0, π])
    Moiré phase angle between the two UEUM state vectors.

``resonance_quality`` (q ∈ [0, 1])
    How close the precession-rate ratio is to the ideal n1/n2 = 5/7
    lock.  q = 1 − min(|ratio − 5/7|, |ratio − 7/5|) / (7/5 − 5/7).

``beta`` (β)
    Birefringence coupling constant — the information-flux coupling between
    the two manifolds.

``entropy_brain``, ``entropy_univ``
    Entropy of the two manifolds at the coupled fixed point.

``entropy_coherence`` (1 − |S_B − S_U| / (S_B + S_U + ε))
    Normalised entropy coherence between the two manifolds.  1 = perfect
    thermodynamic alignment; 0 = maximally misaligned.

Domain deployment mapping
--------------------------
Each domain method returns a ``dict`` whose keys are the natural φ-field
parameters for that domain model:

| Pillar | Domain     | Method          | Key outputs                        |
|--------|------------|-----------------|------------------------------------|
| 10     | Chemistry  | to_chemistry    | phi_bond, reaction_barrier         |
| 12     | Earth      | to_earth        | tectonic_phi, thermal_gradient     |
| 13     | Biology    | to_biology      | negentropy_rate, homeostasis_margin|
| 17     | Medicine   | to_medicine     | health_phi, systemic_deviation     |
| 18     | Justice    | to_justice      | equity_phi, equity_deviation       |
| 19     | Governance | to_governance   | stability_phi, fragmentation_index |
| 20     | Neuroscience| to_neuroscience| neural_phi, coherence_index        |
| 21     | Ecology    | to_ecology      | biodiversity_phi, perturbation     |
| 22     | Climate    | to_climate      | radiative_phi, forcing             |
| 23     | Marine     | to_marine       | ocean_phi, salinity_gradient       |
| 24     | Psychology | to_psychology   | behavioral_phi, cognitive_gap      |
| 25     | Genetics   | to_genetics     | genomic_phi, mutation_coupling     |
| 26     | Materials  | to_materials    | lattice_phi, disorder_param        |

Public API
----------
BridgeState
    Frozen snapshot of the bridge observables extracted from a CoupledSystem.
    All fields are plain floats; no references to the original system.

ConsciousnessBridgeDeployment
    Main class.  Constructed from a ``CoupledSystem``.  Exposes one method
    per target domain plus ``deploy_all()`` and ``bridge_state()``.

bridge_from_system(system) → ConsciousnessBridgeDeployment
    Convenience constructor.

RESONANCE_TARGET : float = 5/7
    Ideal n1/n2 precession-rate ratio at the coupled fixed point.

RESONANCE_WIDTH : float = 7/5 − 5/7
    Full width of the resonance band used for normalising resonance_quality.
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
from dataclasses import dataclass, field
from typing import Dict

import numpy as np

import sys
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from src.consciousness.coupled_attractor import (
    CoupledSystem,
    information_gap,
    phase_offset,
    resonance_ratio,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Ideal n1/n2 precession-rate ratio (5/7) at the coupled fixed point.
RESONANCE_TARGET: float = 5.0 / 7.0

#: Full resonance band width used for normalising resonance_quality.
RESONANCE_WIDTH: float = 7.0 / 5.0 - 5.0 / 7.0   # ≈ 0.686

#: Guard against division by zero.
_EPS: float = 1e-12


# ---------------------------------------------------------------------------
# BridgeState — snapshot of bridge observables
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BridgeState:
    """Frozen snapshot of the bridge observables extracted from a CoupledSystem.

    All attributes are plain Python floats.  Immutable once created.

    Attributes
    ----------
    phi_brain : float
        Radion of the neural manifold (local information capacity).
    phi_univ : float
        Radion of the universe manifold (cosmological information capacity).
    phi_eff : float
        Geometric-mean effective coupling: √(phi_brain · phi_univ).
    info_gap : float
        Information Gap ΔI = |φ²_brain − φ²_univ|.
    phase_offset_rad : float
        Moiré phase angle Δφ in radians ∈ [0, π].
    resonance_quality : float
        Normalised resonance proximity q ∈ [0, 1]; 1 = perfect 5:7 lock.
    beta : float
        Birefringence coupling constant β.
    entropy_brain : float
        Entropy of the brain manifold at the fixed point.
    entropy_univ : float
        Entropy of the universe manifold at the fixed point.
    entropy_coherence : float
        Normalised entropy coherence ∈ [0, 1]; 1 = perfect alignment.
    """

    phi_brain: float
    phi_univ: float
    phi_eff: float
    info_gap: float
    phase_offset_rad: float
    resonance_quality: float
    beta: float
    entropy_brain: float
    entropy_univ: float
    entropy_coherence: float


# ---------------------------------------------------------------------------
# ConsciousnessBridgeDeployment
# ---------------------------------------------------------------------------

class ConsciousnessBridgeDeployment:
    """Deploys Pillar 9 coupled state onto Pillars 10–26 application domains.

    Constructed from a converged ``CoupledSystem`` (brain ⊗ universe).
    Extracts bridge observables once and provides one deployment method per
    target domain.  Each method returns a ``dict`` of named φ-parameters
    ready to be passed to the corresponding domain module.

    Parameters
    ----------
    system : CoupledSystem
        A converged (or partially converged) CoupledSystem from Pillar 9.

    Examples
    --------
    >>> from src.consciousness.coupled_attractor import (
    ...     ManifoldState, CoupledSystem
    ... )
    >>> brain = ManifoldState.brain()
    >>> univ  = ManifoldState.universe()
    >>> sys_  = CoupledSystem(brain=brain, universe=univ)
    >>> dep   = ConsciousnessBridgeDeployment(sys_)
    >>> med   = dep.to_medicine()
    >>> 0.0 <= med["health_phi"]
    True
    """

    def __init__(self, system: CoupledSystem) -> None:
        self._system = system
        self._state  = _extract_bridge_state(system)

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def bridge_state(self) -> BridgeState:
        """Return the frozen BridgeState snapshot."""
        return self._state

    # ------------------------------------------------------------------
    # Domain deployment methods
    # ------------------------------------------------------------------

    def to_chemistry(self) -> Dict[str, float]:
        """Pillar 10 — Chemistry: bond strength and reaction barrier.

        Returns
        -------
        dict with keys:

        ``phi_bond``
            Effective bond-field strength φ_eff.  Higher values correspond
            to stronger, more stable chemical bonds (deeper φ potential
            wells).

        ``reaction_barrier``
            Activation barrier proportional to the Information Gap ΔI.
            When ΔI → 0 (maximum coherence), the reaction barrier is
            minimal; when ΔI is large the extra disorder raises the
            effective barrier.

        ``braid_coupling``
            β × φ_eff — the birefringence-mediated coupling that drives
            stereochemical selectivity in asymmetric reactions.
        """
        s = self._state
        return {
            "phi_bond":        s.phi_eff,
            "reaction_barrier": s.info_gap,
            "braid_coupling":  s.beta * s.phi_eff,
        }

    def to_earth(self) -> Dict[str, float]:
        """Pillar 12 — Earth Sciences: tectonic and thermal coupling.

        Returns
        -------
        dict with keys:

        ``tectonic_phi``
            φ_univ drives large-scale geological processes; the universe
            manifold represents the planetary bulk.

        ``thermal_gradient``
            ΔI supplies the driving gradient for mantle convection and
            geothermal heat flux.

        ``phase_coupling``
            cos(Δφ) maps the Moiré alignment to the degree of coherence
            between tectonic plates and asthenosphere flow.
        """
        s = self._state
        return {
            "tectonic_phi":    s.phi_univ,
            "thermal_gradient": s.info_gap,
            "phase_coupling":  math.cos(s.phase_offset_rad),
        }

    def to_biology(self) -> Dict[str, float]:
        """Pillar 13 — Biology: life as negentropy attractor.

        Returns
        -------
        dict with keys:

        ``negentropy_rate``
            φ_eff² — rate at which the biological system accumulates
            negative entropy (maintains order against thermodynamic decay).

        ``homeostasis_margin``
            1 − ΔI / (φ_eff² + ε) — how far the system is from losing its
            homeostatic fixed point.  1 = perfect homeostasis; < 0 = failed.

        ``entropy_coherence``
            Shared entropy coherence inherited directly from the bridge.
        """
        s = self._state
        phi2 = s.phi_eff ** 2
        margin = 1.0 - s.info_gap / (phi2 + _EPS)
        return {
            "negentropy_rate":   phi2,
            "homeostasis_margin": margin,
            "entropy_coherence": s.entropy_coherence,
        }

    def to_medicine(self) -> Dict[str, float]:
        """Pillar 17 — Medicine: individual health state and systemic deviation.

        Returns
        -------
        dict with keys:

        ``health_phi``
            φ_brain — the individual's information-carrying capacity; the
            local φ-homeostasis setpoint.

        ``systemic_deviation``
            ΔI — how far the system-level (societal / healthcare network)
            fixed point deviates from the individual fixed point.

        ``clinician_burnout_risk``
            ΔI / (φ_brain² + ε) — high information gap relative to
            personal φ capacity correlates with clinician burnout risk.

        ``resonance_quality``
            How coherently the neural (individual) manifold is coupled
            to the universe manifold; proxy for treatment efficacy.
        """
        s = self._state
        return {
            "health_phi":          s.phi_brain,
            "systemic_deviation":  s.info_gap,
            "clinician_burnout_risk": s.info_gap / (s.phi_brain ** 2 + _EPS),
            "resonance_quality":   s.resonance_quality,
        }

    def to_justice(self) -> Dict[str, float]:
        """Pillar 18 — Justice: φ-equity and sentencing coherence.

        Returns
        -------
        dict with keys:

        ``equity_phi``
            φ_eff — the effective coupling that drives equitable information
            distribution across a legal system's participants.

        ``equity_deviation``
            ΔI — the gap between individual (brain) and systemic (universe)
            information capacity; maps to structural inequity.

        ``bias_index``
            phase_offset / π — Moiré misalignment as a normalised proxy for
            systematic bias (0 = fully aligned; 1 = maximally biased).

        ``correction_strength``
            β × φ_eff — the coupling available to drive corrective flow
            from high-φ to low-φ regions.
        """
        s = self._state
        return {
            "equity_phi":         s.phi_eff,
            "equity_deviation":   s.info_gap,
            "bias_index":         s.phase_offset_rad / math.pi,
            "correction_strength": s.beta * s.phi_eff,
        }

    def to_governance(self) -> Dict[str, float]:
        """Pillar 19 — Governance: democratic stability and fragmentation.

        Returns
        -------
        dict with keys:

        ``stability_phi``
            φ_eff — collective information capacity of the governance system;
            higher φ_eff → more stable distributed democracy.

        ``fragmentation_index``
            ΔI / (φ_eff² + ε) — normalised information gap; proxy for
            political fragmentation (analogous to Gini index for information
            current distribution).

        ``legitimacy``
            entropy_coherence × resonance_quality — joint measure of
            thermodynamic alignment and precession-rate lock; proxies for
            democratic legitimacy.

        ``n_effective_sources``
            φ_eff² / (ΔI + ε) — effective number of independent φ-sources
            (citizen voices) contributing to the collective decision field
            (analogous to N_eff in the Condorcet jury theorem).
        """
        s = self._state
        phi2 = s.phi_eff ** 2
        frag  = s.info_gap / (phi2 + _EPS)
        legit = s.entropy_coherence * s.resonance_quality
        n_eff = phi2 / (s.info_gap + _EPS)
        return {
            "stability_phi":       s.phi_eff,
            "fragmentation_index": frag,
            "legitimacy":          legit,
            "n_effective_sources": n_eff,
        }

    def to_neuroscience(self) -> Dict[str, float]:
        """Pillar 20 — Neuroscience: neural dynamics as φ-field.

        Returns
        -------
        dict with keys:

        ``neural_phi``
            φ_brain — local neural information capacity (theta-band
            amplitude / arousal proxy).

        ``coherence_index``
            resonance_quality — how tightly the neural oscillations are
            locked to the universal 5:7 braid frequency.

        ``synaptic_coupling``
            β × φ_brain — synapse-level birefringence coupling strength.

        ``decoherence_risk``
            ΔI / (φ_brain + ε) — elevated information gap relative to
            local φ is a proxy for cognitive decoherence risk.
        """
        s = self._state
        return {
            "neural_phi":       s.phi_brain,
            "coherence_index":  s.resonance_quality,
            "synaptic_coupling": s.beta * s.phi_brain,
            "decoherence_risk": s.info_gap / (s.phi_brain + _EPS),
        }

    def to_ecology(self) -> Dict[str, float]:
        """Pillar 21 — Ecology: ecosystem diversity and perturbation.

        Returns
        -------
        dict with keys:

        ``biodiversity_phi``
            φ_eff — carrying capacity of the ecosystem's information field;
            proportional to species richness and trophic complexity.

        ``perturbation``
            ΔI — external driving perturbation (analogous to an
            environmental shock that shifts the ecosystem's fixed point).

        ``resilience``
            resonance_quality × entropy_coherence — joint measure of the
            ecosystem's ability to recover from perturbation.

        ``extinction_risk``
            ΔI / (φ_eff + ε) — perturbation relative to carrying capacity;
            high values indicate elevated extinction risk.
        """
        s = self._state
        return {
            "biodiversity_phi": s.phi_eff,
            "perturbation":     s.info_gap,
            "resilience":       s.resonance_quality * s.entropy_coherence,
            "extinction_risk":  s.info_gap / (s.phi_eff + _EPS),
        }

    def to_climate(self) -> Dict[str, float]:
        """Pillar 22 — Climate: radiative forcing and feedback.

        Returns
        -------
        dict with keys:

        ``radiative_phi``
            φ_univ — planetary-scale information capacity; maps to the
            radiative energy budget of the climate system.

        ``forcing``
            ΔI — external radiative forcing (perturbation from the
            pre-industrial fixed point).

        ``feedback_gain``
            1.0 / (1.0 − s.resonance_quality × s.entropy_coherence + ε) —
            climate feedback gain factor; resonance lock amplifies feedback.

        ``albedo_proxy``
            cos(Δφ / 2)² — normalised Moiré alignment maps to surface
            reflectivity coherence.
        """
        s = self._state
        feedback_denom = 1.0 - s.resonance_quality * s.entropy_coherence
        feedback_gain  = 1.0 / (abs(feedback_denom) + _EPS)
        albedo = math.cos(s.phase_offset_rad / 2.0) ** 2
        return {
            "radiative_phi":  s.phi_univ,
            "forcing":        s.info_gap,
            "feedback_gain":  feedback_gain,
            "albedo_proxy":   albedo,
        }

    def to_marine(self) -> Dict[str, float]:
        """Pillar 23 — Marine Sciences: ocean dynamics.

        Returns
        -------
        dict with keys:

        ``ocean_phi``
            φ_eff — deep-ocean information capacity (thermohaline coupling).

        ``salinity_gradient``
            ΔI — drives the density differential that powers thermohaline
            circulation (analogous to the Information Gap driving flow).

        ``stratification``
            phase_offset / π — normalised Moiré misalignment maps to
            vertical stratification strength; 0 = well-mixed; 1 = maximal.

        ``upwelling_rate``
            β × φ_eff — birefringence-mediated upwelling coupling.
        """
        s = self._state
        return {
            "ocean_phi":         s.phi_eff,
            "salinity_gradient": s.info_gap,
            "stratification":    s.phase_offset_rad / math.pi,
            "upwelling_rate":    s.beta * s.phi_eff,
        }

    def to_psychology(self) -> Dict[str, float]:
        """Pillar 24 — Psychology: behaviour as φ-field.

        Returns
        -------
        dict with keys:

        ``behavioral_phi``
            φ_brain — local motivational/attentional capacity.

        ``cognitive_gap``
            ΔI — the gap between the agent's internal model (brain manifold)
            and the true external state (universe manifold); source of
            cognitive dissonance and prediction error.

        ``stress_index``
            ΔI / (φ_brain² + ε) — normalised cognitive mismatch; high
            values correlate with chronic stress and rumination.

        ``self_regulation``
            resonance_quality — degree of neural 5:7 lock; proxy for
            executive-function / impulse-control capacity.
        """
        s = self._state
        return {
            "behavioral_phi":  s.phi_brain,
            "cognitive_gap":   s.info_gap,
            "stress_index":    s.info_gap / (s.phi_brain ** 2 + _EPS),
            "self_regulation": s.resonance_quality,
        }

    def to_genetics(self) -> Dict[str, float]:
        """Pillar 25 — Genetics: genomic information and mutation.

        Returns
        -------
        dict with keys:

        ``genomic_phi``
            φ_eff — information-carrying capacity of the genome (analogous
            to sequence diversity / coding density).

        ``mutation_coupling``
            β × ΔI — birefringence-weighted information gap drives the
            effective mutation rate (larger gap = higher stochastic
            rewriting pressure on the genome).

        ``selection_strength``
            resonance_quality — how strongly natural selection locks the
            population phenotype to the environmental attractor.

        ``drift_amplitude``
            ΔI / (φ_eff² + ε) — genetic drift strength relative to the
            effective population information content.
        """
        s = self._state
        return {
            "genomic_phi":       s.phi_eff,
            "mutation_coupling": s.beta * s.info_gap,
            "selection_strength": s.resonance_quality,
            "drift_amplitude":   s.info_gap / (s.phi_eff ** 2 + _EPS),
        }

    def to_materials(self) -> Dict[str, float]:
        """Pillar 26 — Materials Science: lattice order and disorder.

        Returns
        -------
        dict with keys:

        ``lattice_phi``
            φ_eff — long-range order parameter of the material lattice.

        ``disorder_param``
            ΔI — disorder (phonon scattering / defect density); drives
            deviation from the crystalline fixed point.

        ``conductivity_proxy``
            resonance_quality × φ_eff² — braid-resonance × order²
            proxies for ballistic charge-carrier coherence (electronic
            conductivity in the φ-lattice model).

        ``critical_coupling``
            β × φ_eff — birefringence coupling at which a topological
            phase transition (analogous to a quantum critical point) occurs.
        """
        s = self._state
        return {
            "lattice_phi":       s.phi_eff,
            "disorder_param":    s.info_gap,
            "conductivity_proxy": s.resonance_quality * s.phi_eff ** 2,
            "critical_coupling": s.beta * s.phi_eff,
        }

    # ------------------------------------------------------------------
    # Aggregate deployment
    # ------------------------------------------------------------------

    def deploy_all(self) -> Dict[str, Dict[str, float]]:
        """Deploy to all 13 application domains simultaneously.

        Returns
        -------
        dict mapping domain name → deployment parameter dict.

        Keys: ``chemistry``, ``earth``, ``biology``, ``medicine``,
        ``justice``, ``governance``, ``neuroscience``, ``ecology``,
        ``climate``, ``marine``, ``psychology``, ``genetics``,
        ``materials``.
        """
        return {
            "chemistry":    self.to_chemistry(),
            "earth":        self.to_earth(),
            "biology":      self.to_biology(),
            "medicine":     self.to_medicine(),
            "justice":      self.to_justice(),
            "governance":   self.to_governance(),
            "neuroscience": self.to_neuroscience(),
            "ecology":      self.to_ecology(),
            "climate":      self.to_climate(),
            "marine":       self.to_marine(),
            "psychology":   self.to_psychology(),
            "genetics":     self.to_genetics(),
            "materials":    self.to_materials(),
        }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _extract_bridge_state(system: CoupledSystem) -> BridgeState:
    """Extract all bridge observables from a CoupledSystem.

    Parameters
    ----------
    system : CoupledSystem

    Returns
    -------
    BridgeState
    """
    brain  = system.brain
    univ   = system.universe

    phi_b  = float(brain.phi)
    phi_u  = float(univ.phi)
    phi_eff = float(math.sqrt(abs(phi_b * phi_u)))

    gap    = information_gap(brain, univ)
    delta  = phase_offset(brain, univ)

    ratio  = resonance_ratio(brain, univ)
    # Distance to the nearest resonance target (5/7 or 7/5)
    dist_lo = abs(ratio - RESONANCE_TARGET)
    dist_hi = abs(ratio - 1.0 / RESONANCE_TARGET)
    dist    = min(dist_lo, dist_hi)
    res_q   = float(max(0.0, 1.0 - dist / (RESONANCE_WIDTH + _EPS)))

    S_b = float(brain.node.S)
    S_u = float(univ.node.S)
    total_S = S_b + S_u
    ent_coh = 1.0 - abs(S_b - S_u) / (total_S + _EPS)

    return BridgeState(
        phi_brain=phi_b,
        phi_univ=phi_u,
        phi_eff=phi_eff,
        info_gap=gap,
        phase_offset_rad=delta,
        resonance_quality=res_q,
        beta=float(system.beta),
        entropy_brain=S_b,
        entropy_univ=S_u,
        entropy_coherence=float(ent_coh),
    )


# ---------------------------------------------------------------------------
# Convenience constructor
# ---------------------------------------------------------------------------

def bridge_from_system(system: CoupledSystem) -> ConsciousnessBridgeDeployment:
    """Convenience constructor for ConsciousnessBridgeDeployment.

    Parameters
    ----------
    system : CoupledSystem
        Converged coupled brain–universe system from Pillar 9.

    Returns
    -------
    ConsciousnessBridgeDeployment
    """
    return ConsciousnessBridgeDeployment(system)
