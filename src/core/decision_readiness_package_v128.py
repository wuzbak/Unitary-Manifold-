# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Pillar 392 — Decision Readiness Package v12.8
🔵 ADJACENT TRACK (non-hardgate; governance engineering)

Consolidates all 2027–2032 decision-window readiness protocols into a single
machine-readable package. Every active falsifier lane must have:

  1. A preregistered prediction (numerical, with uncertainty).
  2. A same-day routing protocol (callable Python function).
  3. A rehearsal drill output (mock verdict for plausible future scenarios).
  4. An explicit PASS / FALSIFIED verdict path.

Decision windows covered:
  • DESI DR3       (~2027)  wₐ = 0 vs wₐ ≠ 0 at ≥3σ
  • Simons Obs DR1 (~2027)  r = 0.0315 confirmation / falsification
  • JUNO           (~2027)  Δm²₃₁ = 2.452×10⁻³ eV²
  • SPHEREx        (~2026–2030)  f_NL ∈ [−3, 0]
  • CMB-S4         (~2030)  joint r, β
  • LiteBIRD       (~2032)  β ∈ {0.273°, 0.331°} ± 0.007°

Epistemic status: GOVERNANCE_ENGINEERING — routes observational verdicts;
does not produce new physics derivations.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ──────────────────────────────────────────────────────────────────────────────
# Verdict taxonomy
# ──────────────────────────────────────────────────────────────────────────────

class ObservationalVerdict(str, Enum):
    CONFIRMED        = "CONFIRMED"        # ≥3σ detection consistent with UM
    CONSISTENT       = "CONSISTENT"       # Consistent; not yet discriminating
    TENSION          = "TENSION"          # 2–3σ tension with UM
    HIGH_TENSION     = "HIGH_TENSION"     # 2.5–3σ, approaching falsification
    FALSIFIED        = "FALSIFIED"        # ≥3σ inconsistent with UM
    PENDING          = "PENDING"          # Data not yet published
    REHEARSAL        = "REHEARSAL"        # Mock verdict from drill


# ──────────────────────────────────────────────────────────────────────────────
# Decision window data model
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class DecisionWindow:
    """A single falsifier decision window."""

    name: str
    experiment: str
    expected_year: int
    um_prediction: str          # Human-readable prediction
    falsifier_condition: str    # Exact falsification condition
    routing_function: str       # Python callable name for same-day routing
    preregistered: bool
    routing_source_module: str  # src/core/pillarXXX_...py

    # Runtime state
    current_verdict: ObservationalVerdict = ObservationalVerdict.PENDING
    routing_protocol_tested: bool = False
    rehearsal_complete: bool = False
    notes: str = ""

    @property
    def is_ready(self) -> bool:
        """Return True when the window has a preregistered, tested routing protocol."""
        return self.preregistered and self.routing_protocol_tested

    @property
    def needs_immediate_attention(self) -> bool:
        """Return True for windows expected ≤ 2028 that are not yet fully ready."""
        return self.expected_year <= 2028 and not self.is_ready


# ──────────────────────────────────────────────────────────────────────────────
# Canonical window registry
# ──────────────────────────────────────────────────────────────────────────────

DECISION_WINDOWS: List[DecisionWindow] = [
    DecisionWindow(
        name="DESI_DR3",
        experiment="DESI Year-5 / DR3",
        expected_year=2027,
        um_prediction="wₐ = 0 (frozen radion); w₀ = −1",
        falsifier_condition="σ ≥ 3.0 and |wₐ| > 0 at ≥3σ measured → FALSIFIED",
        routing_function="desi_dr3_canonical_routing",
        preregistered=True,
        routing_source_module="src/core/pillar367_desi_dr3_canonical_routing.py",
        routing_protocol_tested=True,
        rehearsal_complete=True,
        current_verdict=ObservationalVerdict.HIGH_TENSION,
        notes="DR2 combined: 2.75σ tension. DR3 near-falsification scenario: wₐ≈−0.62, σ=0.18 → 3.44σ FALSIFIED",
    ),
    DecisionWindow(
        name="SO_DR1",
        experiment="Simons Observatory DR1",
        expected_year=2027,
        um_prediction="r = 0.0315; nₛ = 0.9635",
        falsifier_condition="r < 0.010 measured at ≥3σ → FALSIFIED; r ≥ 0.020 at ≥5σ → CONFIRMED",
        routing_function="so_dr1_joint_routing",
        preregistered=True,
        routing_source_module="src/core/pillar368_so_dr1_joint_verdict.py",
        routing_protocol_tested=True,
        rehearsal_complete=True,
        current_verdict=ObservationalVerdict.HIGH_TENSION,
        notes=(
            "ACT DR6 HIGH_TENSION (r<0.016, 95%CL; IRREDUCIBLE_IN_BRAIDED_5D_EFT). "
            "SO DR1 σ_r~0.006 would give ~5.25σ detection if UM correct."
        ),
    ),
    DecisionWindow(
        name="JUNO",
        experiment="JUNO neutrino experiment",
        expected_year=2027,
        um_prediction="Δm²₃₁ = 2.452×10⁻³ eV² (NLO, P274); 0.004% residual from PDG",
        falsifier_condition="|residual| ≥ 3σ_JUNO (σ ≈ 0.5%) → FALSIFIED",
        routing_function="juno_2027_verdict",
        preregistered=True,
        routing_source_module="src/core/pillar369_juno_2027_preregistration.py",
        routing_protocol_tested=True,
        rehearsal_complete=True,
        current_verdict=ObservationalVerdict.CONSISTENT,
        notes="SHA-256 preregistration hash committed (v12.5). Hyper-K 2028 cross-check active.",
    ),
    DecisionWindow(
        name="SPHEREX",
        experiment="SPHEREx (NASA)",
        expected_year=2028,
        um_prediction="f_NL^equil ∈ [−3, 0] (DBI c_s=12/37 + KK braid correction)",
        falsifier_condition="f_NL > +10 at ≥3σ → FALSIFIED (rules out sub-luminal c_s)",
        routing_function="fnl_prediction",
        preregistered=True,
        routing_source_module="src/core/pillar375_fnl_non_gaussianity.py",
        routing_protocol_tested=True,
        rehearsal_complete=False,
        current_verdict=ObservationalVerdict.CONSISTENT,
        notes="Planck 2018 f_NL=−26±47 consistent. SPHEREx borderline discriminator from ΛCDM.",
    ),
    DecisionWindow(
        name="CMB_S4",
        experiment="CMB-S4",
        expected_year=2030,
        um_prediction="r = 0.0315; β ∈ {0.273°, 0.331°} ± 0.007°; nₛ = 0.9635",
        falsifier_condition=(
            "r < 0.010 at 3σ OR nₛ ∉ [0.955, 0.972] at <0.001 → FALSIFIED"
        ),
        routing_function="joint_ns_r_verdict",
        preregistered=True,
        routing_source_module="src/core/cmbs4_ns_r_joint_falsifier.py",
        routing_protocol_tested=True,
        rehearsal_complete=False,
        current_verdict=ObservationalVerdict.PENDING,
        notes="Joint r + β discrimination test. σ_r ~ 0.001.",
    ),
    DecisionWindow(
        name="LITEBIRD",
        experiment="LiteBIRD satellite",
        expected_year=2032,
        um_prediction=(
            "β ∈ {0.273° ± 0.007° [(5,6) shadow], 0.331° ± 0.007° [(5,7) primary]}; "
            "inter-sector gap (0.29°, 0.31°) is itself a falsifier"
        ),
        falsifier_condition=(
            "β < 0.22° at ≥3σ OR β > 0.38° at ≥3σ OR β ∈ (0.29°, 0.31°) at ≥3σ → FALSIFIED"
        ),
        routing_function="classify_beta",
        preregistered=True,
        routing_source_module="src/core/litebird_gap_hardening.py",
        routing_protocol_tested=True,
        rehearsal_complete=True,
        current_verdict=ObservationalVerdict.CONSISTENT,
        notes=(
            "PRIMARY FALSIFIER. β hint 0.35°±0.14° (2020/2022) consistent with (5,7) sector. "
            "Inter-sector gap [0.29°, 0.31°] is a discrete falsifier."
        ),
    ),
]

_WINDOW_MAP: Dict[str, DecisionWindow] = {w.name: w for w in DECISION_WINDOWS}


def get_window(name: str) -> Optional[DecisionWindow]:
    """Look up a decision window by name."""
    return _WINDOW_MAP.get(name)


# ──────────────────────────────────────────────────────────────────────────────
# Rehearsal drills
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class DrillScenario:
    """A mock observational input for a rehearsal drill."""
    window_name: str
    scenario_label: str
    mock_value: float
    mock_sigma: float
    expected_verdict: ObservationalVerdict


def run_desi_dr3_drill(wa: float, sigma: float) -> ObservationalVerdict:
    """Route a mock DESI DR3 wₐ measurement to a verdict."""
    significance = abs(wa) / sigma if sigma > 0 else 0.0
    if significance >= 3.0:
        return ObservationalVerdict.FALSIFIED
    if significance >= 2.5:
        return ObservationalVerdict.HIGH_TENSION
    if significance >= 2.0:
        return ObservationalVerdict.TENSION
    return ObservationalVerdict.CONSISTENT


def run_so_dr1_drill(r_measured: float, sigma_r: float) -> ObservationalVerdict:
    """Route a mock SO DR1 r measurement to a verdict."""
    um_r = 0.0315
    # Falsification: r < 0.010 measured at ≥3σ
    if r_measured < 0.010 and (um_r - r_measured) / sigma_r >= 3.0:
        return ObservationalVerdict.FALSIFIED
    # Confirmation: r ≥ 0.020 at ≥5σ detection
    if r_measured >= 0.020 and r_measured / sigma_r >= 5.0:
        return ObservationalVerdict.CONFIRMED
    # ACT-style HIGH_TENSION: r < 0.016 at 95%CL
    if r_measured < 0.016:
        return ObservationalVerdict.HIGH_TENSION
    return ObservationalVerdict.CONSISTENT


def run_juno_drill(dm31_measured: float, sigma: float) -> ObservationalVerdict:
    """Route a mock JUNO Δm²₃₁ measurement to a verdict."""
    um_dm31 = 2.452e-3
    residual_sigma = abs(dm31_measured - um_dm31) / sigma if sigma > 0 else 0.0
    if residual_sigma >= 3.0:
        return ObservationalVerdict.FALSIFIED
    if residual_sigma >= 2.0:
        return ObservationalVerdict.TENSION
    return ObservationalVerdict.CONSISTENT


def run_litebird_drill(beta_deg: float, sigma_deg: float) -> ObservationalVerdict:
    """Route a mock LiteBIRD β measurement to a verdict.

    Falsification conditions:
      β < 0.22° at ≥3σ (below admissible window)
      β > 0.38° at ≥3σ (above admissible window)
      β ∈ (0.29°, 0.31°) at ≥3σ (inter-sector gap)
    """
    # Check admissible window
    z_low  = (0.22 - beta_deg) / sigma_deg if sigma_deg > 0 else 0.0
    z_high = (beta_deg - 0.38) / sigma_deg if sigma_deg > 0 else 0.0

    if z_low >= 3.0 or z_high >= 3.0:
        return ObservationalVerdict.FALSIFIED

    # Check inter-sector gap: β ∈ (0.29°, 0.31°) and neither sector is within 3σ
    if 0.29 < beta_deg < 0.31:
        z_primary = abs(beta_deg - 0.331) / sigma_deg if sigma_deg > 0 else float("inf")
        z_shadow  = abs(beta_deg - 0.273) / sigma_deg if sigma_deg > 0 else float("inf")
        if min(z_primary, z_shadow) >= 3.0:
            return ObservationalVerdict.FALSIFIED

    # Check sector support
    z_primary = abs(beta_deg - 0.331) / sigma_deg if sigma_deg > 0 else float("inf")
    z_shadow  = abs(beta_deg - 0.273) / sigma_deg if sigma_deg > 0 else float("inf")

    if min(z_primary, z_shadow) <= 1.0:
        return ObservationalVerdict.CONFIRMED
    if min(z_primary, z_shadow) <= 2.0:
        return ObservationalVerdict.CONSISTENT

    return ObservationalVerdict.CONSISTENT


CANONICAL_DRILL_SCENARIOS: List[DrillScenario] = [
    # DESI DR3 near-falsification
    DrillScenario("DESI_DR3", "DR3-S6 near-falsification",
                  mock_value=-0.62, mock_sigma=0.18,
                  expected_verdict=ObservationalVerdict.FALSIFIED),
    # DESI DR3 tension maintained
    DrillScenario("DESI_DR3", "DR3-S3 tension-maintained",
                  mock_value=-0.55, mock_sigma=0.20,
                  expected_verdict=ObservationalVerdict.HIGH_TENSION),
    # DESI DR3 resolved
    DrillScenario("DESI_DR3", "DR3-S1 resolved",
                  mock_value=-0.05, mock_sigma=0.25,
                  expected_verdict=ObservationalVerdict.CONSISTENT),
    # SO DR1 UM confirmed
    DrillScenario("SO_DR1", "SO-CONFIRMED",
                  mock_value=0.0315, mock_sigma=0.006,
                  expected_verdict=ObservationalVerdict.CONFIRMED),
    # SO DR1 falsified
    DrillScenario("SO_DR1", "SO-FALSIFIED",
                  mock_value=0.008, mock_sigma=0.003,
                  expected_verdict=ObservationalVerdict.FALSIFIED),
    # JUNO consistent
    DrillScenario("JUNO", "JUNO-CONSISTENT",
                  mock_value=2.452e-3, mock_sigma=0.012e-3,
                  expected_verdict=ObservationalVerdict.CONSISTENT),
    # JUNO falsified
    DrillScenario("JUNO", "JUNO-FALSIFIED",
                  mock_value=2.600e-3, mock_sigma=0.012e-3,
                  expected_verdict=ObservationalVerdict.FALSIFIED),
    # LiteBIRD primary sector confirmed
    DrillScenario("LITEBIRD", "LB-PRIMARY-CONFIRMED",
                  mock_value=0.331, mock_sigma=0.020,
                  expected_verdict=ObservationalVerdict.CONFIRMED),
    # LiteBIRD below admissible window
    DrillScenario("LITEBIRD", "LB-FALSIFIED-LOW",
                  mock_value=0.14, mock_sigma=0.015,
                  expected_verdict=ObservationalVerdict.FALSIFIED),
    # LiteBIRD inter-sector gap (discrete falsifier)
    DrillScenario("LITEBIRD", "LB-FALSIFIED-GAP",
                  mock_value=0.300, mock_sigma=0.005,
                  expected_verdict=ObservationalVerdict.FALSIFIED),
]


def run_all_drills() -> List[dict]:
    """Execute all canonical rehearsal drills and return results."""
    results: List[dict] = []
    for scenario in CANONICAL_DRILL_SCENARIOS:
        if scenario.window_name == "DESI_DR3":
            verdict = run_desi_dr3_drill(scenario.mock_value, scenario.mock_sigma)
        elif scenario.window_name == "SO_DR1":
            verdict = run_so_dr1_drill(scenario.mock_value, scenario.mock_sigma)
        elif scenario.window_name == "JUNO":
            verdict = run_juno_drill(scenario.mock_value, scenario.mock_sigma)
        elif scenario.window_name == "LITEBIRD":
            verdict = run_litebird_drill(scenario.mock_value, scenario.mock_sigma)
        else:
            verdict = ObservationalVerdict.PENDING

        passed = verdict == scenario.expected_verdict
        results.append({
            "window": scenario.window_name,
            "scenario": scenario.scenario_label,
            "mock_value": scenario.mock_value,
            "mock_sigma": scenario.mock_sigma,
            "expected": scenario.expected_verdict.value,
            "actual": verdict.value,
            "passed": passed,
        })
    return results


# ──────────────────────────────────────────────────────────────────────────────
# Readiness audit
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class ReadinessReport:
    """Full decision-readiness audit for the current sprint."""

    windows: List[DecisionWindow]
    drill_results: List[dict]

    @property
    def all_near_term_ready(self) -> bool:
        return all(not w.needs_immediate_attention for w in self.windows)

    @property
    def drill_pass_rate(self) -> float:
        if not self.drill_results:
            return 1.0
        passed = sum(1 for r in self.drill_results if r["passed"])
        return passed / len(self.drill_results)

    @property
    def all_drills_pass(self) -> bool:
        return self.drill_pass_rate == 1.0

    def summary(self) -> dict:
        near_term = [w for w in self.windows if w.expected_year <= 2028]
        return {
            "total_windows": len(self.windows),
            "near_term_windows": len(near_term),
            "near_term_ready": sum(1 for w in near_term if w.is_ready),
            "rehearsals_complete": sum(1 for w in self.windows if w.rehearsal_complete),
            "drill_scenarios": len(self.drill_results),
            "drills_passed": sum(1 for r in self.drill_results if r["passed"]),
            "drill_pass_rate": round(self.drill_pass_rate, 4),
            "all_drills_pass": self.all_drills_pass,
            "all_near_term_ready": self.all_near_term_ready,
        }

    def unready_windows(self) -> List[str]:
        return [w.name for w in self.windows if not w.is_ready]

    def failed_drills(self) -> List[dict]:
        return [r for r in self.drill_results if not r["passed"]]


def decision_readiness_audit() -> ReadinessReport:
    """Run the full decision-readiness audit."""
    drill_results = run_all_drills()
    return ReadinessReport(
        windows=DECISION_WINDOWS,
        drill_results=drill_results,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Pillar 392 status
# ──────────────────────────────────────────────────────────────────────────────

PILLAR_392_STATUS = "GOVERNANCE_ENGINEERING"
PILLAR_392_LABEL  = "ADJACENT_TRACK"


def pillar_392_status() -> dict:
    """Machine-readable status for Pillar 392."""
    report = decision_readiness_audit()
    return {
        "pillar": 392,
        "name": "Decision Readiness Package v12.8",
        "status": PILLAR_392_STATUS,
        "label": PILLAR_392_LABEL,
        "windows_covered": [w.name for w in DECISION_WINDOWS],
        "readiness_summary": report.summary(),
        "high_tension_windows": [
            w.name for w in DECISION_WINDOWS
            if w.current_verdict in (
                ObservationalVerdict.HIGH_TENSION,
                ObservationalVerdict.TENSION,
            )
        ],
        "hils_status": "ACTIVE",
    }
