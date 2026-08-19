#!/usr/bin/env python3
# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
run.py — AxiomZero Ω Oracle launcher.

Usage:
    python run.py           # launch Gradio UI at http://localhost:7872
    python run.py --demo    # print a demo synthesis report to stdout
"""
import sys
import os

# Ensure the package root is on the path
sys.path.insert(0, os.path.dirname(__file__))


def demo():
    """Print a complete demo synthesis report to stdout."""
    from oracle.engine.synthesis import SynthesisOrchestrator
    from oracle.engine.constants import DEFAULT_PENTAD_BODIES
    from oracle.engine.integrity import AUDIT_DIMENSIONS

    orch = SynthesisOrchestrator()

    body_specs = [
        {
            "label": DEFAULT_PENTAD_BODIES[0],
            "status": "SOLID",
            "phi_trust": 0.85,
            "description": "Core infrastructure is robust and documented.",
            "foundations": "Reliable CI/CD, 51K+ passing tests, clear architecture.",
            "constraints": "Limited hardware budget; cloud costs rising.",
            "open_gaps": "",
            "falsifiable_commitment": (
                "If infrastructure downtime exceeds 2h/month, consider rearchitecting."
            ),
        },
        {
            "label": DEFAULT_PENTAD_BODIES[1],
            "status": "CONSTRAINED",
            "phi_trust": 0.72,
            "description": "Small but dedicated team; human bandwidth is the real limit.",
            "foundations": "Strong individual expertise; shared values; clear mission.",
            "constraints": "Two people — can not parallelize more than 2 work streams.",
            "open_gaps": "No dedicated DevOps engineer yet.",
            "falsifiable_commitment": (
                "If 3+ urgent issues pile up simultaneously, the bottleneck is staffing."
            ),
        },
        {
            "label": DEFAULT_PENTAD_BODIES[2],
            "status": "SOLID",
            "phi_trust": 0.90,
            "description": "AI-augmented workflows; rigorous test suite; formal proofs.",
            "foundations": "HILS framework, Copilot integration, 208-pillar physics engine.",
            "constraints": "Lean4 bridge still in progress.",
            "open_gaps": "",
            "falsifiable_commitment": (
                "If test count drops below 50K, a regression has occurred."
            ),
        },
        {
            "label": DEFAULT_PENTAD_BODIES[3],
            "status": "SOLID",
            "phi_trust": 0.88,
            "description": "Open-source, public domain, HILS governance, falsifiable.",
            "foundations": "DPCL license, HILS sessions logged, full provenance.",
            "constraints": "Peer review still pending at arXiv.",
            "open_gaps": "",
            "falsifiable_commitment": (
                "If LiteBIRD (2032) measures β outside [0.22°, 0.38°], framework is falsified."
            ),
        },
        {
            "label": DEFAULT_PENTAD_BODIES[4],
            "status": "ESTIMATED",
            "phi_trust": 0.65,
            "description": "Clear physics vision; product roadmap in progress.",
            "foundations": "20-year mission clarity; SPC incorporation; product suite launched.",
            "constraints": "Commercial sustainability model still being developed.",
            "open_gaps": "Revenue model for sustaining long-term development.",
            "falsifiable_commitment": (
                "If no sustainable funding exists by end of 2026, strategy needs revision."
            ),
        },
    ]

    dim_scores = {
        "Transparency":       0.92,
        "Sequence Integrity": 0.88,
        "Participation":      0.75,
        "Accountability":     0.85,
        "Resilience":         0.70,
        "Epistemic Honesty":  0.95,
        "Freedom Floor":      0.80,
    }

    commitments = [
        {
            "domain": "Trust & Accountability",
            "commitment": "Publish a peer-reviewed arXiv submission by Q1 2027.",
            "falsification_condition": "If not submitted by March 31 2027, timeline is not feasible.",
            "test_horizon": "Q1 2027",
        },
        {
            "domain": "Purpose & Horizon",
            "commitment": "Achieve product TRL-7 for at least 3 products by end of 2026.",
            "falsification_condition": "If fewer than 3 products reach TRL-7, roadmap needs revision.",
            "test_horizon": "December 2026",
        },
    ]

    report = orch.synthesize(
        system_name="AxiomZero Technologies & Consulting, SPC",
        system_type="Organisation / Company",
        body_specs=body_specs,
        dim_scores=dim_scores,
        context=(
            "The AxiomZero SPC is a Washington State Social Purpose Corporation "
            "building the Unitary Manifold physics framework and a suite of 15+ software "
            "products under the Defensive Public Commons License.  All work is human-AI "
            "collaborative (HILS framework).  Primary falsifier: LiteBIRD ~2032."
        ),
        commitments=commitments,
        session_id="DEMO0001",
    )

    print(report.full_report())


def main():
    if "--demo" in sys.argv:
        demo()
        return
    from oracle.app.main import main as gradio_main
    gradio_main()


if __name__ == "__main__":
    main()
