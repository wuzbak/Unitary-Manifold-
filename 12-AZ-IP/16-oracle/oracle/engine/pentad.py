# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
oracle/engine/pentad.py
=======================
The System Pentad Modeler.

Any real-world system — a democracy, a company, a community, a project, a
family — can be represented as a five-body Pentad.  The five bodies are
whatever the analyst decides they are.  The mathematics governing their
coupling and stability is drawn from the Unitary Manifold HILS framework.

Theory: ThomasCory Walker-Pearson.
Code:   GitHub Copilot (AI).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import math

from oracle.engine.constants import (
    N_W, N_2, C_S_F, XI_C_F,
    STATUS_WEIGHTS, DEFAULT_PENTAD_BODIES,
    stability_floor, phi_trust_status, omega_grade,
)


# ── Data models ───────────────────────────────────────────────────────────────

@dataclass
class PentadBody:
    """One body within a five-body Pentad."""
    name: str
    label: str                          # e.g., "Ψ₁ — Foundation"
    epistemic_status: str               # SOLID | CONSTRAINED | ESTIMATED | OPEN
    phi_trust: float                    # 0.0–1.0  authenticity / integrity
    description: str = ""
    foundations: str = ""              # what is working
    constraints: str = ""              # real limits being worked within
    open_gaps: str = ""                # what is unresolved
    falsifiable_commitment: str = ""   # what would prove strategy wrong

    def __post_init__(self) -> None:
        self.epistemic_status = self.epistemic_status.upper()
        if self.epistemic_status not in STATUS_WEIGHTS:
            raise ValueError(
                f"Invalid epistemic_status '{self.epistemic_status}'. "
                f"Must be one of: {list(STATUS_WEIGHTS)}"
            )
        if not (0.0 <= self.phi_trust <= 1.0):
            raise ValueError(f"phi_trust must be in [0, 1]; got {self.phi_trust}")

    @property
    def status_weight(self) -> float:
        return STATUS_WEIGHTS[self.epistemic_status]

    @property
    def is_aligned(self) -> bool:
        """SOLID or CONSTRAINED bodies count as aligned for stability."""
        return self.epistemic_status in ("SOLID", "CONSTRAINED")

    @property
    def resonance(self) -> float:
        """Body resonance: status_weight × phi_trust."""
        return self.status_weight * self.phi_trust

    @property
    def status_symbol(self) -> str:
        return {"SOLID": "✅", "CONSTRAINED": "⚙️", "ESTIMATED": "〰️", "OPEN": "🔓"}[
            self.epistemic_status
        ]


@dataclass
class PentadModel:
    """
    A five-body Pentad representing any system.

    All stability and coherence mathematics follows the HILS framework
    documented in the Unitary Pentad and omega_synthesis.py.
    """
    system_name: str
    system_type: str                    # e.g., "Democracy", "Project", "Community"
    bodies: list[PentadBody]
    context: str = ""

    def __post_init__(self) -> None:
        if len(self.bodies) != N_W:
            raise ValueError(
                f"A Pentad requires exactly {N_W} bodies; got {len(self.bodies)}"
            )

    # ── Core metrics ─────────────────────────────────────────────────────────

    @property
    def n_aligned(self) -> int:
        return sum(1 for b in self.bodies if b.is_aligned)

    @property
    def stability(self) -> float:
        return stability_floor(self.n_aligned)

    @property
    def avg_phi_trust(self) -> float:
        return sum(b.phi_trust for b in self.bodies) / N_W

    @property
    def avg_resonance(self) -> float:
        return sum(b.resonance for b in self.bodies) / N_W

    @property
    def omega_score(self) -> float:
        return self.stability * self.avg_resonance

    @property
    def grade(self) -> tuple[str, str, str]:
        return omega_grade(self.omega_score)

    @property
    def phi_trust_label(self) -> str:
        return phi_trust_status(self.avg_phi_trust)

    @property
    def in_authenticity_crisis(self) -> bool:
        return self.avg_phi_trust < C_S_F

    # ── Coupling analysis ─────────────────────────────────────────────────────

    def weakest_body(self) -> PentadBody:
        return min(self.bodies, key=lambda b: b.resonance)

    def strongest_body(self) -> PentadBody:
        return max(self.bodies, key=lambda b: b.resonance)

    def open_bodies(self) -> list[PentadBody]:
        return [b for b in self.bodies if b.epistemic_status == "OPEN"]

    def coupling_matrix(self) -> list[list[float]]:
        """
        Symmetric 5×5 coupling matrix.
        Entry (i, j) = Ξ_c × resonance_i × resonance_j  (i ≠ j)
        Diagonal = resonance_i (self-coupling).
        """
        n = len(self.bodies)
        m = [[0.0] * n for _ in range(n)]
        for i, bi in enumerate(self.bodies):
            for j, bj in enumerate(self.bodies):
                if i == j:
                    m[i][j] = bi.resonance
                else:
                    m[i][j] = XI_C_F * bi.resonance * bj.resonance
        return m

    def braid_coherence(self) -> float:
        """
        Braid coherence of the Pentad — derived from the (5,7) braid resonance.
        coherence = sum of off-diagonal couplings / (N_W*(N_W-1)/2)
        Normalized to [0, 1] by the maximum possible coupling (Ξ_c × 1.0 × 1.0).
        """
        pairs = [(i, j) for i in range(N_W) for j in range(i + 1, N_W)]
        if not pairs:
            return 0.0
        total = sum(XI_C_F * self.bodies[i].resonance * self.bodies[j].resonance
                    for i, j in pairs)
        max_possible = XI_C_F * len(pairs)
        return total / max_possible if max_possible > 0 else 0.0

    # ── Narrative ─────────────────────────────────────────────────────────────

    def summary(self) -> str:
        letter, label, desc = self.grade
        lines = [
            f"╔══════════════════════════════════════════════════════════════╗",
            f"║  PENTAD ANALYSIS — {self.system_name[:42]:<42}  ║",
            f"╚══════════════════════════════════════════════════════════════╝",
            f"",
            f"  System type    : {self.system_type}",
            f"  Omega Score    : {self.omega_score:.4f}  [{letter} — {label}]",
            f"  Stability floor: {self.stability:.4f}  (n_aligned={self.n_aligned}/{N_W})",
            f"  phi_trust      : {self.avg_phi_trust:.4f}  [{self.phi_trust_label}]",
            f"  Braid coherence: {self.braid_coherence():.4f}",
            f"",
            f"  {desc}",
            f"",
        ]
        if self.in_authenticity_crisis:
            lines.append(
                f"  ⚠  AUTHENTICITY CRISIS — avg phi_trust ({self.avg_phi_trust:.3f})"
                f" < C_S ({C_S_F:.3f})"
            )
            lines.append("")

        lines.append("  BODY BREAKDOWN:")
        for b in self.bodies:
            bar_len = int(b.resonance * 20)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            lines.append(
                f"    {b.status_symbol} {b.label:<32}  [{bar}]  {b.resonance:.3f}"
            )

        open_b = self.open_bodies()
        if open_b:
            lines.append("")
            lines.append("  🔓 OPEN BODIES (require attention):")
            for b in open_b:
                lines.append(f"    • {b.label}: {b.open_gaps or '(no detail provided)'}")

        lines.append("")
        lines.append(
            f"  Mathematics: stability_floor({self.n_aligned}) = "
            f"min(1, C_S + {self.n_aligned}×C_S/N_2) = "
            f"min(1, {C_S_F:.4f} + {self.n_aligned}×{C_S_F:.4f}/{N_2}) "
            f"= {self.stability:.4f}"
        )
        return "\n".join(lines)
