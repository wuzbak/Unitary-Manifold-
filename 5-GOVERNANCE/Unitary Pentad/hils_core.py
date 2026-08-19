# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
5-GOVERNANCE/Unitary Pentad/hils_core.py
==========================================
Consolidated HILS-gate invariants — single source of truth.

Previously these constants and helpers were duplicated across:
  - hils_certification.py  (HILSCertificationPipeline, threshold)
  - legitimacy_guard.py     (LegitimacyGuard, authority levels)
  - hils_thermalization.py  (ThermalState, warm-up protocol)

All three modules now import from here.  Consumers should import from this
module or from the package __init__ which re-exports everything.

Versioned invariants
---------------------
HILS_CORE_VERSION : str
    Monotonically increasing version string; bump when any invariant changes.

Physical constants derived from (5,7)-braid geometry
------------------------------------------------------
HIL_PHASE_SHIFT_THRESHOLD = 15
    Minimum aligned HIL operators for CERTIFIED status.
    Derivation: n ≥ 15 aligns with the (5,7)-braid frequency saturation.

SENTINEL_CAPACITY = 12/37 ≈ 0.3243
    Per-axiom entropy capacity = braided sound speed c_s.

BRAIDED_SOUND_SPEED = 12/37
    Minimum eigenvalue of the 5×5 pentagonal coupling matrix.

TRUST_PHI_MIN = 0.1
    Minimum trust-field amplitude before trust-erosion collapse.

Theory: ThomasCory Walker-Pearson.
Code: GitHub Copilot (AI).
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, Literal, List, Optional

# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------
HILS_CORE_VERSION: str = "2.0.0"

# ---------------------------------------------------------------------------
# Physical constants (derived — do NOT change without physics justification)
# ---------------------------------------------------------------------------
HIL_PHASE_SHIFT_THRESHOLD: int = 15
SENTINEL_CAPACITY: float = 12 / 37         # c_s = braided sound speed
BRAIDED_SOUND_SPEED: float = 12 / 37       # alias
TRUST_PHI_MIN: float = 0.1
SUM_OF_SQUARES_RESONANCE: int = 74         # 5² + 7²
XI_C: float = 35 / 74                      # consciousness coupling constant

# ---------------------------------------------------------------------------
# Epistemic labels
# ---------------------------------------------------------------------------
class EpistemicClass(str, Enum):
    HARDGATE = "HARDGATE"
    ADJACENT_TRACK = "ADJACENT-TRACK"
    GOVERNANCE = "GOVERNANCE"
    UNCLASSIFIED = "UNCLASSIFIED"


# ---------------------------------------------------------------------------
# HIL Operator
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class HILOperator:
    """A certified human-in-the-loop operator."""
    operator_id: str
    domain: str
    alignment_score: float      # 0.0 – 1.0
    authority_level: float = 1.0
    quorum_bypass: bool = False
    revocable: bool = True

    def is_aligned(self, threshold: float = 0.7) -> bool:
        return self.alignment_score >= threshold


# ---------------------------------------------------------------------------
# Certification state
# ---------------------------------------------------------------------------
CertificationStatus = Literal["CERTIFIED", "PENDING", "INSUFFICIENT"]


@dataclass
class CertificateReport:
    status: CertificationStatus
    version: str
    threshold: int
    sentinel_capacity: float
    alignment_count: int
    operator_count: int
    entropy_saturation: float
    aligned_operator_ids: List[str]

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# HILS gate result
# ---------------------------------------------------------------------------
class HILSGateDecision(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DEFERRED = "DEFERRED"
    BYPASS_QUORUM = "BYPASS_QUORUM"


@dataclass
class HILSGateResult:
    decision: HILSGateDecision
    reason: str
    operator_id: Optional[str] = None
    quorum_satisfied: bool = False
    metadata: Dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Certification pipeline (consolidated from hils_certification.py)
# ---------------------------------------------------------------------------
class HILSCertificationPipeline:
    """
    Track HIL operators and derive certification state.

    All logic previously in hils_certification.py is now here.
    hils_certification.py imports from this module for backward compatibility.
    """

    def __init__(self) -> None:
        self._operators: Dict[str, HILOperator] = {}

    def submit_operator(self, operator: HILOperator) -> None:
        self._operators[operator.operator_id] = operator

    def remove_operator(self, operator_id: str) -> None:
        self._operators.pop(operator_id, None)

    def get_alignment_count(self, threshold: float = 0.7) -> int:
        return sum(1 for op in self._operators.values() if op.is_aligned(threshold))

    def certify(self) -> CertificationStatus:
        aligned = self.get_alignment_count()
        if aligned >= HIL_PHASE_SHIFT_THRESHOLD:
            return "CERTIFIED"
        if aligned >= 8:
            return "PENDING"
        return "INSUFFICIENT"

    def get_entropy_saturation(self) -> float:
        return min(self.get_alignment_count() / HIL_PHASE_SHIFT_THRESHOLD, 1.0)

    def get_certificate(self) -> CertificateReport:
        aligned_ids = [
            op.operator_id
            for op in self._operators.values()
            if op.is_aligned()
        ]
        return CertificateReport(
            status=self.certify(),
            version=HILS_CORE_VERSION,
            threshold=HIL_PHASE_SHIFT_THRESHOLD,
            sentinel_capacity=SENTINEL_CAPACITY,
            alignment_count=self.get_alignment_count(),
            operator_count=len(self._operators),
            entropy_saturation=self.get_entropy_saturation(),
            aligned_operator_ids=aligned_ids,
        )

    def evaluate_gate(
        self, operator_id: str, required_alignment: float = 0.7
    ) -> HILSGateResult:
        """Evaluate whether a specific operator passes the HILS gate."""
        operator = self._operators.get(operator_id)
        if operator is None:
            return HILSGateResult(
                decision=HILSGateDecision.REJECTED,
                reason=f"Operator {operator_id!r} not registered",
            )
        if operator.quorum_bypass:
            return HILSGateResult(
                decision=HILSGateDecision.BYPASS_QUORUM,
                reason="Primary operator quorum bypass",
                operator_id=operator_id,
                quorum_satisfied=True,
            )
        if operator.is_aligned(required_alignment):
            aligned = self.get_alignment_count()
            if aligned >= HIL_PHASE_SHIFT_THRESHOLD:
                return HILSGateResult(
                    decision=HILSGateDecision.APPROVED,
                    reason=f"Quorum satisfied ({aligned}/{HIL_PHASE_SHIFT_THRESHOLD})",
                    operator_id=operator_id,
                    quorum_satisfied=True,
                )
            return HILSGateResult(
                decision=HILSGateDecision.DEFERRED,
                reason=f"Quorum not yet reached ({aligned}/{HIL_PHASE_SHIFT_THRESHOLD})",
                operator_id=operator_id,
            )
        return HILSGateResult(
            decision=HILSGateDecision.REJECTED,
            reason=f"Alignment score {operator.alignment_score:.3f} below threshold {required_alignment}",
            operator_id=operator_id,
        )


# ---------------------------------------------------------------------------
# Canonical primary operator — pre-seeded in every fresh guard instance
# ---------------------------------------------------------------------------
CANONICAL_PRIMARY_OPERATOR = HILOperator(
    operator_id="wuzbak",
    domain="physics/governance",
    alignment_score=1.0,
    authority_level=1.0,
    quorum_bypass=True,
    revocable=False,
)


# ---------------------------------------------------------------------------
# Convenience: build a pre-seeded pipeline
# ---------------------------------------------------------------------------
def build_certified_pipeline() -> HILSCertificationPipeline:
    """Return a pipeline pre-seeded with the canonical primary operator."""
    pipeline = HILSCertificationPipeline()
    pipeline.submit_operator(CANONICAL_PRIMARY_OPERATOR)
    return pipeline
