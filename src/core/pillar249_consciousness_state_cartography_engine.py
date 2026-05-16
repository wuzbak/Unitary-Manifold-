# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 249 — Consciousness State Cartography Engine.

Adjacent research track (non-hardgate): this module synthesizes existing
consciousness and neuroscience surfaces into a deterministic research atlas for
human consciousness-state questions.

Boundary statement (strict):
- This module is for research framing, simulation, and comparative state
  cartography only.
- It is not a diagnostic device, not a prognostic instrument, and not a
  declaration about metaphysical survival after death.
- "Near-death" here means a low-support physiological transition regime with
  residual transient activity, not evidence for consciousness after irreversible
  brain death.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import random
from typing import Any, Mapping

from src.consciousness.consciousness_deployment import ConsciousnessBridgeDeployment
from src.consciousness.coupled_attractor import CoupledSystem, ManifoldState
from src.neuroscience.synaptic import (
    dopamine_phi_modulation,
    gaba_inhibition_phi,
    glutamate_snr,
    serotonin_phi,
)

__provenance__ = {
    "pillar": 249,
    "title": "Consciousness State Cartography Engine",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "version": "v11.1",
    "status": (
        "ADJACENT RESEARCH TRACK — consciousness-state cartography; "
        "non-hardgate, non-clinical, non-metaphysical"
    ),
}

N_W: int = 5
K_CS: int = 74
C_S: float = 12.0 / 37.0
PHI0: float = 0.7390851332151607

ADJACENCY_TRACK_LABEL = "ADJACENT RESEARCH TRACK"
CONSCIOUSNESS_TRACK_LABEL = "CONSCIOUSNESS_STATE_CARTOGRAPHY_TRACK"
STATE_ORDER: tuple[str, ...] = (
    "wake",
    "rem",
    "nrem",
    "anesthesia",
    "coma",
    "near_death_transition",
)

SCORE_WEIGHTS: Mapping[str, float] = {
    "neuromodulator_balance": 0.25,
    "network_integration": 0.30,
    "state_support": 0.15,
    "metabolic_reversibility": 0.20,
    "geometry_alignment": 0.10,
}


@dataclass(frozen=True)
class ConsciousnessStateScenario:
    name: str
    acetylcholine: float
    norepinephrine: float
    dopamine: float
    serotonin: float
    histamine: float
    orexin: float
    gaba: float
    glutamate: float
    eeg_complexity: float
    thalamocortical_coupling: float
    cortical_integration: float
    sensory_responsiveness: float
    metabolic_support: float
    perfusion_fraction: float
    burst_suppression_fraction: float
    slow_wave_fraction: float
    rem_pressure: float
    transient_gamma_surge: float

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("name must be non-empty")
        for field_name in (
            "acetylcholine",
            "norepinephrine",
            "dopamine",
            "serotonin",
            "histamine",
            "orexin",
            "gaba",
            "glutamate",
            "eeg_complexity",
            "thalamocortical_coupling",
            "cortical_integration",
            "sensory_responsiveness",
            "metabolic_support",
            "perfusion_fraction",
            "burst_suppression_fraction",
            "slow_wave_fraction",
            "rem_pressure",
            "transient_gamma_surge",
        ):
            _validate01(field_name, float(getattr(self, field_name)))


def _validate01(name: str, value: float) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be in [0, 1]")



def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@lru_cache(maxsize=1)
def _bridge_state() -> Any:
    system = CoupledSystem(
        brain=ManifoldState.brain(),
        universe=ManifoldState.universe(),
    )
    return ConsciousnessBridgeDeployment(system).bridge_state()



def separation_guard() -> dict[str, Any]:
    """Return explicit non-hardgate/no-clinical/no-metaphysical boundaries."""
    return {
        "label": ADJACENCY_TRACK_LABEL,
        "track": CONSCIOUSNESS_TRACK_LABEL,
        "hardgate_isolation": True,
        "toe_score_delta_allowed": False,
        "physics_claim_promotion_allowed": False,
        "clinical_claims_allowed": False,
        "metaphysical_claims_allowed": False,
        "postmortem_survival_claims_allowed": False,
        "message": (
            "Pillar 249 is an adjacent consciousness-state research atlas. "
            "Outputs are comparative simulation artifacts only and cannot be "
            "read as diagnosis, prognosis, or evidence for awareness after "
            "irreversible brain death."
        ),
    }



def neuromodulator_stack(s: ConsciousnessStateScenario) -> dict[str, Any]:
    wake_drive = (
        s.acetylcholine + s.norepinephrine + s.histamine + s.orexin
    ) / 4.0
    monoamine_withdrawal = (
        (1.0 - s.norepinephrine)
        + (1.0 - s.serotonin)
        + (1.0 - s.histamine)
    ) / 3.0
    dopaminergic_gain = dopamine_phi_modulation(1.0, s.dopamine, d1_gain=0.8)
    serotonergic_tone = serotonin_phi(1.0, s.serotonin, mood_coupling=0.4)
    residual_excitation = gaba_inhibition_phi(
        phi_pre=0.5 * s.glutamate + 0.5 * wake_drive,
        gaba_fraction=min(1.0, 0.85 * s.gaba),
    )
    excitation_snr = glutamate_snr(
        J_glu=max(0.0, s.glutamate - 0.35 * s.gaba),
        B_noise=max(0.05, 1.0 - s.cortical_integration),
    )
    excitation_snr_norm = excitation_snr / (1.0 + excitation_snr)

    balance_score = _clamp01(
        0.34 * wake_drive
        + 0.16 * excitation_snr_norm
        + 0.14 * (dopaminergic_gain / 1.8)
        + 0.10 * (serotonergic_tone / 1.2)
        + 0.11 * residual_excitation
        + 0.15 * s.acetylcholine
        - 0.28 * s.gaba
    )
    rem_bias = _clamp01(
        0.35 * s.acetylcholine
        + 0.20 * s.dopamine
        + 0.20 * monoamine_withdrawal
        + 0.15 * s.rem_pressure
        + 0.10 * s.transient_gamma_surge
        - 0.10 * s.orexin
    )

    return {
        "wake_drive": wake_drive,
        "monoamine_withdrawal": monoamine_withdrawal,
        "dopaminergic_gain": dopaminergic_gain,
        "serotonergic_tone": serotonergic_tone,
        "residual_excitation": residual_excitation,
        "excitation_snr": excitation_snr,
        "excitation_snr_norm": excitation_snr_norm,
        "neuromodulator_balance_score": balance_score,
        "rem_bias": rem_bias,
        "status": "CALCULATED literature-anchored neuromodulator stack",
    }



def network_integration_stack(s: ConsciousnessStateScenario) -> dict[str, Any]:
    integration_score = _clamp01(
        0.32 * s.eeg_complexity
        + 0.24 * s.thalamocortical_coupling
        + 0.24 * s.cortical_integration
        + 0.10 * s.sensory_responsiveness
        + 0.10 * (1.0 - s.burst_suppression_fraction)
    )
    perturbational_capacity = _clamp01(
        0.55 * s.eeg_complexity + 0.45 * s.cortical_integration
    )
    collapse_risk = _clamp01(
        0.45 * (1.0 - integration_score)
        + 0.25 * s.burst_suppression_fraction
        + 0.15 * (1.0 - s.perfusion_fraction)
        + 0.15 * (1.0 - s.metabolic_support)
    )
    return {
        "integration_score": integration_score,
        "perturbational_capacity": perturbational_capacity,
        "collapse_risk": collapse_risk,
        "status": "CALCULATED complexity + thalamocortical integration stack",
    }



def sleep_architecture_stack(s: ConsciousnessStateScenario) -> dict[str, Any]:
    slow_wave_drive = _clamp01(
        0.45 * s.gaba + 0.35 * s.slow_wave_fraction + 0.20 * (1.0 - s.eeg_complexity)
    )
    rem_drive = _clamp01(
        0.35 * s.acetylcholine
        + 0.25 * s.rem_pressure
        + 0.15 * s.dopamine
        + 0.15 * (1.0 - s.norepinephrine)
        + 0.10 * (1.0 - s.serotonin)
    )
    wake_pressure = _clamp01(
        0.35 * s.orexin
        + 0.25 * s.histamine
        + 0.20 * s.norepinephrine
        + 0.10 * s.acetylcholine
        + 0.10 * s.sensory_responsiveness
    )

    drivers = {
        "wake": wake_pressure,
        "rem": rem_drive,
        "slow_wave": slow_wave_drive,
    }
    dominant_rhythm = max(drivers, key=drivers.get)
    return {
        "wake_pressure": wake_pressure,
        "rem_drive": rem_drive,
        "slow_wave_drive": slow_wave_drive,
        "dominant_rhythm": dominant_rhythm,
        "status": "CALCULATED sleep-wake architecture stack",
    }



def transition_stack(s: ConsciousnessStateScenario) -> dict[str, Any]:
    reversibility_score = _clamp01(
        0.40 * s.metabolic_support
        + 0.30 * s.perfusion_fraction
        + 0.15 * (1.0 - s.burst_suppression_fraction)
        + 0.15 * s.cortical_integration
    )
    near_death_signal = _clamp01(
        0.35 * (1.0 - s.perfusion_fraction)
        + 0.25 * (1.0 - s.metabolic_support)
        + 0.25 * s.transient_gamma_surge
        + 0.15 * (1.0 - s.sensory_responsiveness)
    )
    boundary_zone = (
        s.perfusion_fraction < 0.20 and s.metabolic_support < 0.25
    )
    return {
        "reversibility_score": reversibility_score,
        "near_death_signal": near_death_signal,
        "boundary_zone": boundary_zone,
        "status": "CALCULATED physiological transition-risk stack",
    }



def geometry_alignment_stack(s: ConsciousnessStateScenario) -> dict[str, Any]:
    bridge = _bridge_state()
    info_gap_scale = float(bridge.info_gap) / (1.0 + float(bridge.info_gap))
    alignment_score = _clamp01(
        0.40 * float(bridge.resonance_quality)
        + 0.25 * float(bridge.entropy_coherence)
        + 0.20 * s.cortical_integration
        + 0.15 * s.eeg_complexity
        - 0.10 * info_gap_scale
    )
    return {
        "phi_eff": float(bridge.phi_eff),
        "beta": float(bridge.beta),
        "resonance_quality": float(bridge.resonance_quality),
        "entropy_coherence": float(bridge.entropy_coherence),
        "geometry_alignment_score": alignment_score,
        "status": "CALCULATED bridge-consistent geometry-alignment stack",
    }



def classify_state(s: ConsciousnessStateScenario) -> dict[str, Any]:
    neuro = neuromodulator_stack(s)
    net = network_integration_stack(s)
    sleep = sleep_architecture_stack(s)
    transition = transition_stack(s)

    if transition["boundary_zone"] and transition["near_death_signal"] >= 0.60:
        label = "near_death_transition"
        confidence = _clamp01(0.55 + 0.35 * transition["near_death_signal"])
    elif (
        s.burst_suppression_fraction >= 0.45
        and s.gaba >= 0.75
        and net["integration_score"] <= 0.35
    ):
        label = "anesthesia"
        confidence = _clamp01(0.55 + 0.35 * s.burst_suppression_fraction)
    elif net["integration_score"] <= 0.25 and transition["reversibility_score"] <= 0.45:
        label = "coma"
        confidence = _clamp01(0.55 + 0.30 * (1.0 - net["integration_score"]))
    elif (
        sleep["dominant_rhythm"] == "slow_wave"
        and s.gaba >= 0.60
        and s.sensory_responsiveness <= 0.25
    ):
        label = "nrem"
        confidence = _clamp01(0.55 + 0.25 * sleep["slow_wave_drive"])
    elif (
        sleep["dominant_rhythm"] == "rem"
        and s.acetylcholine >= 0.60
        and s.norepinephrine <= 0.30
        and s.serotonin <= 0.30
    ):
        label = "rem"
        confidence = _clamp01(0.55 + 0.25 * neuro["rem_bias"])
    else:
        label = "wake"
        confidence = _clamp01(0.55 + 0.25 * net["integration_score"] + 0.10 * neuro["wake_drive"])

    return {
        "predicted_state": label,
        "classification_confidence": confidence,
        "status": "CALCULATED rule-based consciousness-state classification",
    }



def consciousness_access_score(s: ConsciousnessStateScenario) -> dict[str, Any]:
    neuro = neuromodulator_stack(s)
    net = network_integration_stack(s)
    sleep = sleep_architecture_stack(s)
    transition = transition_stack(s)
    geometry = geometry_alignment_stack(s)
    classification = classify_state(s)

    state_support = _clamp01(
        max(
            float(sleep["wake_pressure"]),
            float(sleep["rem_drive"]),
            1.0 - 0.70 * float(sleep["slow_wave_drive"]),
        )
    )
    score = _clamp01(
        float(SCORE_WEIGHTS["neuromodulator_balance"]) * float(neuro["neuromodulator_balance_score"])
        + float(SCORE_WEIGHTS["network_integration"]) * float(net["integration_score"])
        + float(SCORE_WEIGHTS["state_support"]) * state_support
        + float(SCORE_WEIGHTS["metabolic_reversibility"]) * float(transition["reversibility_score"])
        + float(SCORE_WEIGHTS["geometry_alignment"]) * float(geometry["geometry_alignment_score"])
    )

    if score >= 0.70:
        band = "high-conscious-access"
    elif score >= 0.45:
        band = "intermediate-conscious-access"
    else:
        band = "low-conscious-access"

    return {
        "neuromodulators": neuro,
        "network": net,
        "sleep": sleep,
        "transition": transition,
        "geometry": geometry,
        "classification": classification,
        "score_weights": dict(SCORE_WEIGHTS),
        "state_support_score": state_support,
        "consciousness_access_score": score,
        "access_band": band,
        "status": "CALCULATED adjacent consciousness-state score",
    }



def uncertainty_bands(
    s: ConsciousnessStateScenario,
    n_trials: int = 249,
    seed: int = 249,
) -> dict[str, Any]:
    if n_trials < 1:
        raise ValueError("n_trials must be >= 1")

    rng = random.Random(seed)
    vals: list[float] = []
    state_counts = {name: 0 for name in STATE_ORDER}

    for _ in range(n_trials):
        perturbed = ConsciousnessStateScenario(
            name=s.name,
            acetylcholine=_clamp01(s.acetylcholine + rng.uniform(-0.05, 0.05)),
            norepinephrine=_clamp01(s.norepinephrine + rng.uniform(-0.05, 0.05)),
            dopamine=_clamp01(s.dopamine + rng.uniform(-0.05, 0.05)),
            serotonin=_clamp01(s.serotonin + rng.uniform(-0.05, 0.05)),
            histamine=_clamp01(s.histamine + rng.uniform(-0.05, 0.05)),
            orexin=_clamp01(s.orexin + rng.uniform(-0.05, 0.05)),
            gaba=_clamp01(s.gaba + rng.uniform(-0.05, 0.05)),
            glutamate=_clamp01(s.glutamate + rng.uniform(-0.05, 0.05)),
            eeg_complexity=_clamp01(s.eeg_complexity + rng.uniform(-0.05, 0.05)),
            thalamocortical_coupling=_clamp01(s.thalamocortical_coupling + rng.uniform(-0.05, 0.05)),
            cortical_integration=_clamp01(s.cortical_integration + rng.uniform(-0.05, 0.05)),
            sensory_responsiveness=_clamp01(s.sensory_responsiveness + rng.uniform(-0.05, 0.05)),
            metabolic_support=_clamp01(s.metabolic_support + rng.uniform(-0.06, 0.06)),
            perfusion_fraction=_clamp01(s.perfusion_fraction + rng.uniform(-0.06, 0.06)),
            burst_suppression_fraction=_clamp01(s.burst_suppression_fraction + rng.uniform(-0.05, 0.05)),
            slow_wave_fraction=_clamp01(s.slow_wave_fraction + rng.uniform(-0.05, 0.05)),
            rem_pressure=_clamp01(s.rem_pressure + rng.uniform(-0.05, 0.05)),
            transient_gamma_surge=_clamp01(s.transient_gamma_surge + rng.uniform(-0.08, 0.08)),
        )
        report = consciousness_access_score(perturbed)
        vals.append(float(report["consciousness_access_score"]))
        state_counts[report["classification"]["predicted_state"]] += 1

    vals.sort()
    p10 = vals[max(0, int(0.10 * len(vals)) - 1)]
    p50 = vals[len(vals) // 2]
    p90 = vals[min(len(vals) - 1, int(0.90 * len(vals)))]
    spread = p90 - p10

    if spread <= 0.10:
        confidence = "tight"
    elif spread <= 0.20:
        confidence = "moderate"
    else:
        confidence = "wide"

    dominant_state = max(state_counts, key=state_counts.get)
    return {
        "mean_score": sum(vals) / len(vals),
        "p10_score": p10,
        "p50_score": p50,
        "p90_score": p90,
        "uncertainty_spread": spread,
        "uncertainty_band": confidence,
        "dominant_state": dominant_state,
        "state_counts": state_counts,
        "n_trials": n_trials,
        "seed": seed,
    }



def baseline_consciousness_state_catalogue() -> dict[str, ConsciousnessStateScenario]:
    return {
        "wake": ConsciousnessStateScenario(
            name="wake",
            acetylcholine=0.75,
            norepinephrine=0.80,
            dopamine=0.60,
            serotonin=0.65,
            histamine=0.80,
            orexin=0.85,
            gaba=0.25,
            glutamate=0.75,
            eeg_complexity=0.85,
            thalamocortical_coupling=0.82,
            cortical_integration=0.88,
            sensory_responsiveness=0.90,
            metabolic_support=0.95,
            perfusion_fraction=0.95,
            burst_suppression_fraction=0.05,
            slow_wave_fraction=0.10,
            rem_pressure=0.15,
            transient_gamma_surge=0.10,
        ),
        "rem": ConsciousnessStateScenario(
            name="rem",
            acetylcholine=0.80,
            norepinephrine=0.15,
            dopamine=0.60,
            serotonin=0.15,
            histamine=0.10,
            orexin=0.05,
            gaba=0.35,
            glutamate=0.70,
            eeg_complexity=0.78,
            thalamocortical_coupling=0.74,
            cortical_integration=0.70,
            sensory_responsiveness=0.20,
            metabolic_support=0.82,
            perfusion_fraction=0.90,
            burst_suppression_fraction=0.02,
            slow_wave_fraction=0.10,
            rem_pressure=0.88,
            transient_gamma_surge=0.25,
        ),
        "nrem": ConsciousnessStateScenario(
            name="nrem",
            acetylcholine=0.20,
            norepinephrine=0.25,
            dopamine=0.20,
            serotonin=0.25,
            histamine=0.15,
            orexin=0.10,
            gaba=0.75,
            glutamate=0.30,
            eeg_complexity=0.30,
            thalamocortical_coupling=0.35,
            cortical_integration=0.32,
            sensory_responsiveness=0.15,
            metabolic_support=0.70,
            perfusion_fraction=0.88,
            burst_suppression_fraction=0.05,
            slow_wave_fraction=0.82,
            rem_pressure=0.15,
            transient_gamma_surge=0.05,
        ),
        "anesthesia": ConsciousnessStateScenario(
            name="anesthesia",
            acetylcholine=0.10,
            norepinephrine=0.15,
            dopamine=0.20,
            serotonin=0.15,
            histamine=0.10,
            orexin=0.05,
            gaba=0.88,
            glutamate=0.22,
            eeg_complexity=0.18,
            thalamocortical_coupling=0.20,
            cortical_integration=0.18,
            sensory_responsiveness=0.05,
            metabolic_support=0.62,
            perfusion_fraction=0.84,
            burst_suppression_fraction=0.55,
            slow_wave_fraction=0.65,
            rem_pressure=0.05,
            transient_gamma_surge=0.05,
        ),
        "coma": ConsciousnessStateScenario(
            name="coma",
            acetylcholine=0.12,
            norepinephrine=0.10,
            dopamine=0.18,
            serotonin=0.12,
            histamine=0.08,
            orexin=0.05,
            gaba=0.55,
            glutamate=0.20,
            eeg_complexity=0.12,
            thalamocortical_coupling=0.10,
            cortical_integration=0.12,
            sensory_responsiveness=0.04,
            metabolic_support=0.30,
            perfusion_fraction=0.45,
            burst_suppression_fraction=0.35,
            slow_wave_fraction=0.40,
            rem_pressure=0.03,
            transient_gamma_surge=0.03,
        ),
        "near_death_transition": ConsciousnessStateScenario(
            name="near_death_transition",
            acetylcholine=0.18,
            norepinephrine=0.08,
            dopamine=0.22,
            serotonin=0.08,
            histamine=0.05,
            orexin=0.02,
            gaba=0.45,
            glutamate=0.28,
            eeg_complexity=0.16,
            thalamocortical_coupling=0.10,
            cortical_integration=0.12,
            sensory_responsiveness=0.02,
            metabolic_support=0.12,
            perfusion_fraction=0.08,
            burst_suppression_fraction=0.18,
            slow_wave_fraction=0.20,
            rem_pressure=0.04,
            transient_gamma_surge=0.72,
        ),
    }



def state_landscape_report(
    catalogue: Mapping[str, ConsciousnessStateScenario] | None = None,
    n_trials: int = 80,
    seed: int = 249,
) -> dict[str, Any]:
    scenarios = dict(baseline_consciousness_state_catalogue() if catalogue is None else catalogue)
    reports: dict[str, Any] = {}

    for idx, name in enumerate(STATE_ORDER):
        s = scenarios[name]
        reports[name] = {
            "scenario": s,
            "analysis": consciousness_access_score(s),
            "uncertainty": uncertainty_bands(s, n_trials=n_trials, seed=seed + idx),
        }

    ranking = sorted(
        (
            {
                "name": name,
                "score": float(payload["analysis"]["consciousness_access_score"]),
                "predicted_state": payload["analysis"]["classification"]["predicted_state"],
            }
            for name, payload in reports.items()
        ),
        key=lambda row: row["score"],
        reverse=True,
    )

    return {
        "reports": reports,
        "ranking": ranking,
        "highest_access_state": ranking[0]["name"],
        "lowest_access_state": ranking[-1]["name"],
        "status": "CALCULATED adjacent consciousness-state landscape",
    }



def pillar249_consciousness_state_report(
    catalogue: Mapping[str, ConsciousnessStateScenario] | None = None,
    n_trials: int = 80,
    seed: int = 249,
) -> dict[str, Any]:
    """Integrated Pillar 249 adjacent-track report."""
    landscape = state_landscape_report(catalogue=catalogue, n_trials=n_trials, seed=seed)
    return {
        "pillar": 249,
        "status": __provenance__["status"],
        "separation_guard": separation_guard(),
        "landscape": landscape,
        "falsification_condition": (
            "FALSIFIED as an adjacent cartography layer if its comparative state "
            "rankings systematically fail against independent, pre-registered "
            "EEG-complexity / arousal benchmarks for the same state families."
        ),
        "epistemic_boundary": (
            "No diagnostic or metaphysical claim is made. Near-death modeling here "
            "tracks low-support transition dynamics only and does not imply "
            "awareness after irreversible brain death."
        ),
    }


__all__ = [
    "N_W",
    "K_CS",
    "C_S",
    "PHI0",
    "ADJACENCY_TRACK_LABEL",
    "CONSCIOUSNESS_TRACK_LABEL",
    "STATE_ORDER",
    "SCORE_WEIGHTS",
    "ConsciousnessStateScenario",
    "__provenance__",
    "separation_guard",
    "neuromodulator_stack",
    "network_integration_stack",
    "sleep_architecture_stack",
    "transition_stack",
    "geometry_alignment_stack",
    "classify_state",
    "consciousness_access_score",
    "uncertainty_bands",
    "baseline_consciousness_state_catalogue",
    "state_landscape_report",
    "pillar249_consciousness_state_report",
]
