# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
oracle/engine/synthesis.py
==========================
The Grand Synthesis Orchestrator — AxiomZero Ω Oracle core.

This is the crown engine.  It accepts a free-form description of any
real-world system and produces a complete SynthesisReport combining:

  1.  Pentad model          (any system as five coupled bodies)
  2.  Epistemic audit       (SOLID / CONSTRAINED / ESTIMATED / OPEN)
  3.  Omega score           (stability × resonance)
  4.  Governance audit      (EIGE-aligned seven-dimension integrity)
  5.  Decision analysis     (resonance-ranked option comparison)
  6.  Action priorities     (physics-grounded intervention ranking)
  7.  Falsifiable commitments (what would prove the analysis wrong)

All mathematics derives from the five seed constants.  No external API
calls, no LLM inference, no black-box models.  Every number is traceable
to an equation.

Theory: ThomasCory Walker-Pearson.
Code:   GitHub Copilot (AI).
"""

from __future__ import annotations
import datetime
from dataclasses import dataclass, field
from typing import Optional

from oracle.engine.constants import (
    N_W, N_2, K_CS, C_S_F, XI_C_F,
    STATUS_WEIGHTS, DEFAULT_PENTAD_BODIES,
    stability_floor, phi_trust_status, omega_grade,
    GOV_INTEGRITY_THRESHOLD, GOV_FREEDOM_FLOOR,
    HIL_PHASE_SHIFT_THRESHOLD,
)
from oracle.engine.pentad import PentadModel, PentadBody
from oracle.engine.integrity import (
    IntegrityAudit, AuditDimension, AUDIT_DIMENSIONS,
)
from oracle.engine.resonance import (
    DecisionAnalysis, DecisionOption, BodyImpact,
    compute_option_resonance,
)


# ── Action Priority ───────────────────────────────────────────────────────────

@dataclass
class ActionPriority:
    """
    A ranked action for improving a system.

    priority_score = (1 − status_weight) × impact_factor × Ξ_c

    High score = fixing a broken body with high leverage.
    """
    body_label: str
    action: str
    epistemic_status: str
    priority_score: float
    rationale: str = ""


@dataclass
class FalsifiableCommitment:
    """A falsifiable prediction / commitment about a system."""
    domain: str
    commitment: str
    falsification_condition: str
    test_horizon: str           # e.g., "90 days", "Q4 2026"


# ── Synthesis Report ──────────────────────────────────────────────────────────

@dataclass
class SynthesisReport:
    """
    The complete output of the Grand Synthesis Orchestrator.
    One of these corresponds to one full analysis session.
    """
    session_id: str
    created_at: str
    system_name: str
    system_type: str
    context: str

    pentad: PentadModel
    audit: IntegrityAudit
    action_priorities: list[ActionPriority]
    commitments: list[FalsifiableCommitment]

    decision_analysis: Optional[DecisionAnalysis] = None

    # ── Derived ──────────────────────────────────────────────────────────────

    @property
    def omega_score(self) -> float:
        return self.pentad.omega_score

    @property
    def integrity_score(self) -> float:
        return self.audit.integrity_score

    @property
    def synthesis_score(self) -> float:
        """
        Grand unified score:
            synthesis = Ξ_c × omega + (1 − Ξ_c) × integrity

        A single number 0–1 summarising both coherence and accountability.
        """
        return XI_C_F * self.omega_score + (1.0 - XI_C_F) * self.integrity_score

    @property
    def synthesis_grade(self) -> tuple[str, str]:
        s = self.synthesis_score
        if s >= 0.85: return ("Ω", "Grand Unified — All systems resonant")
        if s >= 0.75: return ("A", "Strong — Minor gaps; solid foundation")
        if s >= 0.60: return ("B", "Functional — Working; some open work")
        if s >= 0.45: return ("C", "Fragmented — Several bodies need work")
        if s >= 0.30: return ("D", "Unstable — Significant dysfunction")
        return ("F", "Crisis — Immediate intervention required")

    @property
    def is_phase_shifted(self) -> bool:
        """True if n_aligned ≥ HIL_PHASE_SHIFT_THRESHOLD (15 pillar analogue)."""
        return self.pentad.n_aligned >= HIL_PHASE_SHIFT_THRESHOLD

    def full_report(self) -> str:
        letter, label = self.synthesis_grade
        lines = [
            "═" * 66,
            f"  AXIOMZERO Ω ORACLE — GRAND SYNTHESIS REPORT",
            "═" * 66,
            f"",
            f"  System      : {self.system_name}",
            f"  Type        : {self.system_type}",
            f"  Session     : {self.session_id}",
            f"  Generated   : {self.created_at}",
            f"",
            f"  ┌─────────────────────────────────────────────────────────┐",
            f"  │  SYNTHESIS SCORE  :  {self.synthesis_score:.4f}  [{letter} — {label}]",
            f"  │  Omega Score      :  {self.omega_score:.4f}",
            f"  │  Integrity Score  :  {self.integrity_score:.4f}",
            f"  │  Stability Floor  :  {self.pentad.stability:.4f}  "
            f"(n_aligned={self.pentad.n_aligned}/{N_W})",
            f"  │  phi_trust        :  {self.pentad.avg_phi_trust:.4f}  "
            f"[{self.pentad.phi_trust_label}]",
            f"  │  Braid coherence  :  {self.pentad.braid_coherence():.4f}",
            f"  └─────────────────────────────────────────────────────────┘",
            f"",
            f"  EQUATION:",
            f"    synthesis = Ξ_c × Ω + (1−Ξ_c) × integrity",
            f"              = {XI_C_F:.5f} × {self.omega_score:.4f} "
            f"+ {1.0-XI_C_F:.5f} × {self.integrity_score:.4f}",
            f"              = {self.synthesis_score:.4f}",
            f"",
            "─" * 66,
            "",
            self.pentad.summary(),
            "",
            "─" * 66,
            "",
            self.audit.summary(),
        ]

        if self.decision_analysis:
            lines += ["", "─" * 66, "", self.decision_analysis.summary()]

        if self.action_priorities:
            lines += [
                "", "─" * 66, "",
                "  ACTION PRIORITIES (physics-ranked):",
                "",
            ]
            for i, ap in enumerate(self.action_priorities, 1):
                bar_len = int(ap.priority_score * 20)
                bar = "█" * bar_len + "░" * (20 - bar_len)
                lines.append(
                    f"    #{i}  [{bar}]  {ap.priority_score:.3f}  "
                    f"{ap.body_label} — {ap.action}"
                )
                if ap.rationale:
                    lines.append(f"         {ap.rationale}")

        if self.commitments:
            lines += [
                "", "─" * 66, "",
                "  FALSIFIABLE COMMITMENTS:",
                "",
            ]
            for c in self.commitments:
                lines.append(f"  [{c.domain}]  {c.commitment}")
                lines.append(f"    Falsification: {c.falsification_condition}")
                lines.append(f"    Test horizon : {c.test_horizon}")
                lines.append("")

        lines += [
            "─" * 66,
            "",
            f"  Mathematics anchored to five seed constants:",
            f"    N_W={N_W}, N_2={N_2}, K_CS={K_CS}, C_S={C_S_F:.5f}, Ξ_c={XI_C_F:.5f}",
            "",
            "  AxiomZero Technologies & Consulting, SPC — Public Commons",
            "  Theory: ThomasCory Walker-Pearson | Code: GitHub Copilot (AI)",
            "═" * 66,
        ]
        return "\n".join(lines)


# ── Orchestrator ──────────────────────────────────────────────────────────────

class SynthesisOrchestrator:
    """
    Build a SynthesisReport from structured input data.

    Usage::

        orch = SynthesisOrchestrator()
        report = orch.synthesize(
            system_name="City of Springfield",
            system_type="Municipal Government",
            body_specs=[
                {"label": "Ψ₁ — Infrastructure", "status": "SOLID", "phi_trust": 0.8, ...},
                ...
            ],
            dim_scores={"Transparency": 0.7, "Participation": 0.5, ...},
            context="...",
        )
        print(report.full_report())
    """

    def synthesize(
        self,
        system_name: str,
        system_type: str,
        body_specs: list[dict],
        dim_scores: dict[str, float],
        context: str = "",
        decision_question: str = "",
        decision_options: list[dict] | None = None,
        commitments: list[dict] | None = None,
        session_id: str | None = None,
    ) -> SynthesisReport:
        import uuid

        sid = session_id or str(uuid.uuid4())[:8]
        created = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # 1. Build Pentad
        if len(body_specs) != N_W:
            raise ValueError(f"Exactly {N_W} body_specs required; got {len(body_specs)}")
        bodies = [
            PentadBody(
                name=s.get("name", s.get("label", f"Body {i+1}")),
                label=s.get("label", f"Ψ{i+1}"),
                epistemic_status=s.get("status", "ESTIMATED"),
                phi_trust=float(s.get("phi_trust", 0.5)),
                description=s.get("description", ""),
                foundations=s.get("foundations", ""),
                constraints=s.get("constraints", ""),
                open_gaps=s.get("open_gaps", ""),
                falsifiable_commitment=s.get("falsifiable_commitment", ""),
            )
            for i, s in enumerate(body_specs)
        ]
        pentad = PentadModel(
            system_name=system_name,
            system_type=system_type,
            bodies=bodies,
            context=context,
        )

        # 2. Build Integrity Audit
        dims = []
        for key, description in AUDIT_DIMENSIONS:
            score = float(dim_scores.get(key, 0.5))
            dims.append(AuditDimension(
                key=key,
                description=description,
                score=max(0.0, min(1.0, score)),
                evidence=str(dim_scores.get(f"{key}_evidence", "")),
                concern=str(dim_scores.get(f"{key}_concern", "")),
            ))
        audit = IntegrityAudit(
            system_name=system_name,
            system_type=system_type,
            dimensions=dims,
            context=context,
        )

        # 3. Compute action priorities
        actions = self._build_action_priorities(pentad, audit)

        # 4. Decision analysis (optional)
        decision = None
        if decision_question and decision_options and len(decision_options) >= 2:
            opts = []
            for od in decision_options:
                impacts = []
                for imp in od.get("impacts", []):
                    impacts.append(BodyImpact(
                        body_label=imp["body_label"],
                        direction=imp.get("direction", "neutral"),
                        magnitude=float(imp.get("magnitude", 1.0)),
                    ))
                opts.append(DecisionOption(
                    name=od["name"],
                    description=od.get("description", ""),
                    body_impacts=impacts,
                    phi_trust_impact=float(od.get("phi_trust_impact", 0.0)),
                ))
            decision = DecisionAnalysis(
                question=decision_question,
                pentad=pentad,
                options=opts,
            )

        # 5. Falsifiable commitments
        fc_list: list[FalsifiableCommitment] = []
        for c in (commitments or []):
            fc_list.append(FalsifiableCommitment(
                domain=c.get("domain", ""),
                commitment=c.get("commitment", ""),
                falsification_condition=c.get("falsification_condition", ""),
                test_horizon=c.get("test_horizon", ""),
            ))

        return SynthesisReport(
            session_id=sid,
            created_at=created,
            system_name=system_name,
            system_type=system_type,
            context=context,
            pentad=pentad,
            audit=audit,
            action_priorities=actions,
            commitments=fc_list,
            decision_analysis=decision,
        )

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _build_action_priorities(
        self,
        pentad: PentadModel,
        audit: IntegrityAudit,
    ) -> list[ActionPriority]:
        """
        Generate ranked actions for the system.

        priority_score = (1 − status_weight) × impact_factor × Ξ_c

        OPEN bodies always rank highest.  Failing governance dimensions
        inject additional action items.
        """
        priorities: list[ActionPriority] = []

        for body in pentad.bodies:
            sw = body.status_weight
            if sw >= 1.0:
                continue   # SOLID — no action needed
            impact_factor = 1.0 + (1.0 - body.phi_trust)
            score = (1.0 - sw) * impact_factor * XI_C_F

            if body.epistemic_status == "OPEN":
                action = "Resolve open gaps — convert to CONSTRAINED or ESTIMATED."
            elif body.epistemic_status == "ESTIMATED":
                action = "Gather evidence — upgrade to CONSTRAINED with real limits."
            else:
                action = "Clarify constraints — document limits and workarounds."

            priorities.append(ActionPriority(
                body_label=body.label,
                action=action,
                epistemic_status=body.epistemic_status,
                priority_score=min(1.0, score),
                rationale=(
                    f"status_weight={sw:.2f}, phi_trust={body.phi_trust:.2f}, "
                    f"score=(1−{sw:.2f})×{impact_factor:.2f}×{XI_C_F:.4f}={score:.4f}"
                ),
            ))

        for dim in audit.failing_dimensions:
            score = (1.0 - dim.score) * XI_C_F
            priorities.append(ActionPriority(
                body_label=f"Governance: {dim.key}",
                action=f"Improve {dim.key} — currently at {dim.score:.2f} (threshold {GOV_INTEGRITY_THRESHOLD:.2f}).",
                epistemic_status="GOVERNANCE",
                priority_score=min(1.0, score),
                rationale=dim.concern or dim.description,
            ))

        return sorted(priorities, key=lambda a: a.priority_score, reverse=True)
