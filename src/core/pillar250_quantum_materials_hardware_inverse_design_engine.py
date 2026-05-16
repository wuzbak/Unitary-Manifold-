# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 250 — Quantum-Materials Hardware Inverse-Design Engine.

Adjacent research track (non-hardgate): maps the Unitary Manifold fingerprint
(5,7,74) into practical device-readiness and architecture search signals for
fabricable quantum hardware.

Boundary statement (strict):
- This module is an engineering planning and comparative simulation surface.
- It is not a hardgate physics claim and does not alter ToE score surfaces.
- It does not guarantee fabrication success or commercial device outcomes.
"""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Any, Mapping

__provenance__ = {
    "pillar": 250,
    "title": "Quantum-Materials Hardware Inverse-Design Engine",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "status": (
        "ADJACENT RESEARCH TRACK — quantum-materials / hardware inverse-design; "
        "non-hardgate, engineering-planning only"
    ),
}

N_W: int = 5
K_CS: int = 74
C_S: float = 12.0 / 37.0
PHI0: float = 0.7390851332151607
BRAID_PAIR: tuple[int, int] = (5, 7)

ADJACENCY_TRACK_LABEL = "ADJACENT RESEARCH TRACK"
QUANTUM_HARDWARE_TRACK_LABEL = "QUANTUM_MATERIALS_HARDWARE_INVERSE_DESIGN_TRACK"

DOMAIN_ORDER: tuple[str, ...] = (
    "coherence_margin",
    "entangling_fidelity",
    "thermal_isolation",
    "fab_repeatability",
    "control_latency",
    "error_correction_overhead",
    "materials_defect_suppression",
    "braid_geometry_alignment",
)

SCORE_WEIGHTS: Mapping[str, float] = {
    "coherence_margin": 0.18,
    "entangling_fidelity": 0.18,
    "thermal_isolation": 0.12,
    "fab_repeatability": 0.14,
    "control_latency": 0.12,
    "error_correction_overhead": 0.10,
    "materials_defect_suppression": 0.10,
    "braid_geometry_alignment": 0.06,
}


@dataclass(frozen=True)
class QuantumHardwareScenario:
    coherence_time_us: float
    two_qubit_gate_time_ns: float
    two_qubit_fidelity: float
    thermal_load_mw: float
    thermal_budget_mw: float
    fabrication_yield_fraction: float
    control_loop_latency_ns: float
    error_correction_overhead: float
    defect_density_ppm: float
    braid_overlap_fraction: float
    sound_material_coupling: float
    nanofabrication_stability: float

    def __post_init__(self) -> None:
        if self.coherence_time_us <= 0:
            raise ValueError("coherence_time_us must be > 0")
        if self.two_qubit_gate_time_ns <= 0:
            raise ValueError("two_qubit_gate_time_ns must be > 0")
        _validate01("two_qubit_fidelity", self.two_qubit_fidelity)
        if self.thermal_load_mw < 0:
            raise ValueError("thermal_load_mw must be >= 0")
        if self.thermal_budget_mw <= 0:
            raise ValueError("thermal_budget_mw must be > 0")
        _validate01("fabrication_yield_fraction", self.fabrication_yield_fraction)
        if self.control_loop_latency_ns <= 0:
            raise ValueError("control_loop_latency_ns must be > 0")
        _validate01("error_correction_overhead", self.error_correction_overhead)
        if self.defect_density_ppm < 0:
            raise ValueError("defect_density_ppm must be >= 0")
        _validate01("braid_overlap_fraction", self.braid_overlap_fraction)
        _validate01("sound_material_coupling", self.sound_material_coupling)
        _validate01("nanofabrication_stability", self.nanofabrication_stability)


def _validate01(name: str, value: float) -> None:
    if not 0.0 <= float(value) <= 1.0:
        raise ValueError(f"{name} must be in [0, 1]")


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def separation_guard() -> dict[str, Any]:
    return {
        "label": ADJACENCY_TRACK_LABEL,
        "track": QUANTUM_HARDWARE_TRACK_LABEL,
        "hardgate_isolation": True,
        "toe_score_delta_allowed": False,
        "physics_claim_promotion_allowed": False,
        "device_performance_guarantee_allowed": False,
        "message": (
            "Pillar 250 is an adjacent engineering design surface. "
            "Outputs are prioritization artifacts, not guaranteed fabrication outcomes."
        ),
    }


def hardware_domain_scores(s: QuantumHardwareScenario) -> dict[str, float]:
    coherence_ratio = s.coherence_time_us / (0.001 * s.two_qubit_gate_time_ns + 1e-12)
    coherence_adequacy = _clamp01((coherence_ratio - 2_000.0) / 8_000.0)

    thermal_margin = 1.0 - s.thermal_load_mw / max(s.thermal_budget_mw, 1e-12)
    thermal_adequacy = _clamp01(thermal_margin)

    control_adequacy = _clamp01(1.0 - s.control_loop_latency_ns / 2_000.0)
    overhead_adequacy = _clamp01(1.0 - s.error_correction_overhead)
    defect_adequacy = _clamp01(1.0 - s.defect_density_ppm / 50.0)

    braid_target = K_CS / float(K_CS + N_W)
    braid_adequacy = _clamp01(
        1.0 - abs(s.braid_overlap_fraction - braid_target) / max(braid_target, 1e-12)
    )
    material_bridge = _clamp01(
        0.55 * s.sound_material_coupling + 0.45 * s.nanofabrication_stability
    )

    return {
        "coherence_margin": coherence_adequacy,
        "entangling_fidelity": _clamp01((s.two_qubit_fidelity - 0.90) / 0.099),
        "thermal_isolation": thermal_adequacy,
        "fab_repeatability": _clamp01(s.fabrication_yield_fraction),
        "control_latency": control_adequacy,
        "error_correction_overhead": overhead_adequacy,
        "materials_defect_suppression": _clamp01(0.60 * defect_adequacy + 0.40 * material_bridge),
        "braid_geometry_alignment": braid_adequacy,
    }


def architecture_alignment_scores(s: QuantumHardwareScenario) -> list[dict[str, float | str]]:
    d = hardware_domain_scores(s)
    superconducting = _clamp01(
        0.32 * d["coherence_margin"]
        + 0.30 * d["entangling_fidelity"]
        + 0.18 * d["thermal_isolation"]
        + 0.20 * d["control_latency"]
    )
    neutral_atom = _clamp01(
        0.30 * d["entangling_fidelity"]
        + 0.20 * d["fab_repeatability"]
        + 0.20 * d["materials_defect_suppression"]
        + 0.30 * d["braid_geometry_alignment"]
    )
    photonic = _clamp01(
        0.35 * d["control_latency"]
        + 0.25 * d["materials_defect_suppression"]
        + 0.20 * d["fab_repeatability"]
        + 0.20 * d["braid_geometry_alignment"]
    )
    topological = _clamp01(
        0.20 * d["coherence_margin"]
        + 0.15 * d["thermal_isolation"]
        + 0.20 * d["error_correction_overhead"]
        + 0.45 * d["braid_geometry_alignment"]
    )

    rows = [
        {"architecture": "topological", "alignment_score": topological},
        {"architecture": "superconducting", "alignment_score": superconducting},
        {"architecture": "neutral_atom", "alignment_score": neutral_atom},
        {"architecture": "photonic", "alignment_score": photonic},
    ]
    return sorted(rows, key=lambda x: float(x["alignment_score"]), reverse=True)


def inverse_design_readiness_surface(s: QuantumHardwareScenario) -> float:
    d = hardware_domain_scores(s)
    weighted = sum(float(SCORE_WEIGHTS[k]) * float(d[k]) for k in DOMAIN_ORDER)
    dispersion = sum((float(d[k]) - weighted) ** 2 for k in DOMAIN_ORDER) / len(DOMAIN_ORDER)
    coherence_penalty = _clamp01(0.15 * dispersion / 0.25)
    return _clamp01(weighted * (1.0 - coherence_penalty))


def intervention_priority(s: QuantumHardwareScenario, budget_usd: float) -> list[dict[str, float | str]]:
    if budget_usd < 0:
        raise ValueError("budget_usd must be >= 0")

    d = hardware_domain_scores(s)
    gaps = {k: 1.0 - float(v) for k, v in d.items()}
    coupling_gain = 1.0 + C_S
    impacts = {k: gaps[k] * (1.0 + float(SCORE_WEIGHTS[k]) * coupling_gain) for k in DOMAIN_ORDER}

    total = sum(impacts.values())
    if total <= 0 or budget_usd == 0:
        return [
            {
                "domain": k,
                "gap": gaps[k],
                "impact_score": impacts[k],
                "allocated_budget_usd": 0.0,
                "allocated_fraction": 0.0,
            }
            for k in sorted(DOMAIN_ORDER, key=lambda name: impacts[name], reverse=True)
        ]

    rows = []
    for k in DOMAIN_ORDER:
        frac = impacts[k] / total
        rows.append(
            {
                "domain": k,
                "gap": gaps[k],
                "impact_score": impacts[k],
                "allocated_budget_usd": budget_usd * frac,
                "allocated_fraction": frac,
            }
        )
    rows.sort(key=lambda x: float(x["impact_score"]), reverse=True)
    return rows


def monte_carlo_readiness(
    s: QuantumHardwareScenario,
    n_trials: int = 250,
    sigma: float = 0.05,
    seed: int = 250,
) -> dict[str, float]:
    if n_trials < 10:
        raise ValueError("n_trials must be >= 10")
    if sigma < 0:
        raise ValueError("sigma must be >= 0")

    rng = random.Random(seed)
    samples: list[float] = []
    for _ in range(n_trials):
        sampled = QuantumHardwareScenario(
            **{
                **s.__dict__,
                "two_qubit_fidelity": _clamp01(s.two_qubit_fidelity + rng.uniform(-sigma, sigma)),
                "fabrication_yield_fraction": _clamp01(s.fabrication_yield_fraction + rng.uniform(-sigma, sigma)),
                "braid_overlap_fraction": _clamp01(s.braid_overlap_fraction + rng.uniform(-sigma, sigma)),
                "sound_material_coupling": _clamp01(s.sound_material_coupling + rng.uniform(-sigma, sigma)),
                "nanofabrication_stability": _clamp01(s.nanofabrication_stability + rng.uniform(-sigma, sigma)),
            }
        )
        samples.append(inverse_design_readiness_surface(sampled))

    samples.sort()
    i10 = int(0.10 * (n_trials - 1))
    i50 = int(0.50 * (n_trials - 1))
    i90 = int(0.90 * (n_trials - 1))
    return {
        "p10": samples[i10],
        "p50": samples[i50],
        "p90": samples[i90],
        "spread": samples[i90] - samples[i10],
        "status": "CALCULATED deterministic Monte Carlo envelope",
    }


def baseline_quantum_hardware_scenario() -> QuantumHardwareScenario:
    return QuantumHardwareScenario(
        coherence_time_us=185.0,
        two_qubit_gate_time_ns=42.0,
        two_qubit_fidelity=0.982,
        thermal_load_mw=1.2,
        thermal_budget_mw=2.0,
        fabrication_yield_fraction=0.71,
        control_loop_latency_ns=520.0,
        error_correction_overhead=0.58,
        defect_density_ppm=8.5,
        braid_overlap_fraction=0.90,
        sound_material_coupling=0.62,
        nanofabrication_stability=0.69,
    )


def pillar250_quantum_hardware_inverse_design_report(
    budget_usd: float = 500_000_000.0,
) -> dict[str, Any]:
    s = baseline_quantum_hardware_scenario()
    domains = hardware_domain_scores(s)
    readiness = inverse_design_readiness_surface(s)
    return {
        "provenance": __provenance__,
        "separation_guard": separation_guard(),
        "baseline": s,
        "domain_scores": domains,
        "readiness_score": readiness,
        "status_band": (
            "HIGH" if readiness >= 0.75 else "INTERMEDIATE" if readiness >= 0.50 else "LOW"
        ),
        "architecture_rank": architecture_alignment_scores(s),
        "intervention_priority": intervention_priority(s, budget_usd=budget_usd),
        "uncertainty": monte_carlo_readiness(s),
        "falsification_condition": (
            "FALSIFIED if independent fabrication campaigns repeatedly show no "
            "correlation between reported readiness ordering and observed "
            "cross-platform device performance under pre-registered benchmarks."
        ),
    }


__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "BRAID_PAIR",
    "C_S",
    "DOMAIN_ORDER",
    "K_CS",
    "N_W",
    "PHI0",
    "QUANTUM_HARDWARE_TRACK_LABEL",
    "SCORE_WEIGHTS",
    "QuantumHardwareScenario",
    "__provenance__",
    "architecture_alignment_scores",
    "baseline_quantum_hardware_scenario",
    "hardware_domain_scores",
    "intervention_priority",
    "inverse_design_readiness_surface",
    "monte_carlo_readiness",
    "pillar250_quantum_hardware_inverse_design_report",
    "separation_guard",
]
