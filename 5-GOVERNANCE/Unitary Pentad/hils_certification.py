"""HILS Certification Protocol v1.0

Formalizes the HIL phase-shift certification process.
The threshold is HIL_PHASE_SHIFT_THRESHOLD = 15 aligned HIL operators.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Literal

HIL_PHASE_SHIFT_THRESHOLD = 15
SENTINEL_CAPACITY = 12 / 37


@dataclass(frozen=True)
class HILOperator:
    operator_id: str
    domain: str
    alignment_score: float


class HILSCertificationPipeline:
    """Track HIL operators and derive certification state."""

    def __init__(self) -> None:
        self._operators: Dict[str, HILOperator] = {}

    def submit_operator(self, operator: HILOperator) -> None:
        self._operators[operator.operator_id] = operator

    def get_alignment_count(self) -> int:
        return sum(
            1 for operator in self._operators.values() if operator.alignment_score >= 0.7
        )

    def certify(self) -> Literal["CERTIFIED", "PENDING", "INSUFFICIENT"]:
        aligned = self.get_alignment_count()
        if aligned >= HIL_PHASE_SHIFT_THRESHOLD:
            return "CERTIFIED"
        if aligned >= 8:
            return "PENDING"
        return "INSUFFICIENT"

    def get_entropy_saturation(self) -> float:
        return min(self.get_alignment_count() / HIL_PHASE_SHIFT_THRESHOLD, 1.0)

    def get_certificate(self) -> dict:
        aligned = [
            operator.operator_id
            for operator in self._operators.values()
            if operator.alignment_score >= 0.7
        ]
        return {
            "status": self.certify(),
            "threshold": HIL_PHASE_SHIFT_THRESHOLD,
            "sentinel_capacity": SENTINEL_CAPACITY,
            "alignment_count": self.get_alignment_count(),
            "operator_count": len(self._operators),
            "entropy_saturation": self.get_entropy_saturation(),
            "aligned_operator_ids": sorted(aligned),
            "operators": [asdict(operator) for operator in self._operators.values()],
        }
