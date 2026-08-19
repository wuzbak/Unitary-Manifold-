# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
oracle/app/main.py
==================
AxiomZero Ω Oracle — Gradio user interface.

Seven tabs:
  1. 🌐 System Modeler     — Define any system as a five-body Pentad
  2. ⚖️  Governance Audit   — Seven-dimension integrity scoring
  3. 💡 Decision Oracle    — Resonance-ranked multi-option decisions
  4. 📊 Synthesis Report   — Full grand unified analysis
  5. 📈 History            — Longitudinal tracking across sessions
  6. 🔭 Observatory        — Browse anonymised public analyses
  7. ℹ️  About              — The mathematics, ethics, and vision

Theory: ThomasCory Walker-Pearson.
Code:   GitHub Copilot (AI).
"""

from __future__ import annotations
import json
from typing import Optional

import gradio as gr

from oracle.engine.constants import (
    N_W, N_2, K_CS, C_S_F, XI_C_F,
    DEFAULT_PENTAD_BODIES, AUDIT_DIMENSIONS,
    stability_floor, omega_grade,
)
from oracle.engine.synthesis import SynthesisOrchestrator
from oracle.db import store

_orch = SynthesisOrchestrator()

STATUS_CHOICES = ["SOLID", "CONSTRAINED", "ESTIMATED", "OPEN"]
SYSTEM_TYPE_CHOICES = [
    "Democracy / Government",
    "Community / Neighbourhood",
    "Organisation / Company",
    "Project / Initiative",
    "Policy / Law",
    "Team / Group",
    "Personal Life",
    "Research Program",
    "Economic System",
    "Other",
]

# ── Helper: build body_specs from tab-1 inputs ───────────────────────────────

def _build_body_specs(names, statuses, phi_trusts, descriptions, foundations,
                      constraints, open_gaps, commitments_):
    specs = []
    default_labels = DEFAULT_PENTAD_BODIES
    for i in range(N_W):
        specs.append({
            "name":  names[i] or default_labels[i],
            "label": names[i] or default_labels[i],
            "status": statuses[i],
            "phi_trust": float(phi_trusts[i]),
            "description": descriptions[i],
            "foundations": foundations[i],
            "constraints": constraints[i],
            "open_gaps": open_gaps[i],
            "falsifiable_commitment": commitments_[i],
        })
    return specs


def _build_dim_scores(scores):
    result = {}
    for (key, _), score in zip(AUDIT_DIMENSIONS, scores):
        result[key] = score
    return result


# ── Tab 1+2+4 combined: Run Full Synthesis ────────────────────────────────────

def run_synthesis(
    system_name, system_type, context,
    # 5 bodies (each: name, status, phi_trust, description, foundations, constraints, open_gaps, commitment)
    b1n, b1s, b1p, b1d, b1f, b1c, b1g, b1cm,
    b2n, b2s, b2p, b2d, b2f, b2c, b2g, b2cm,
    b3n, b3s, b3p, b3d, b3f, b3c, b3g, b3cm,
    b4n, b4s, b4p, b4d, b4f, b4c, b4g, b4cm,
    b5n, b5s, b5p, b5d, b5f, b5c, b5g, b5cm,
    # 7 governance dimensions
    d1, d2, d3, d4, d5, d6, d7,
    # optional commitment
    cm_domain, cm_text, cm_falsify, cm_horizon,
):
    if not system_name.strip():
        return "⚠️  Please enter a system name.", ""

    body_specs = _build_body_specs(
        [b1n, b2n, b3n, b4n, b5n],
        [b1s, b2s, b3s, b4s, b5s],
        [b1p, b2p, b3p, b4p, b5p],
        [b1d, b2d, b3d, b4d, b5d],
        [b1f, b2f, b3f, b4f, b5f],
        [b1c, b2c, b3c, b4c, b5c],
        [b1g, b2g, b3g, b4g, b5g],
        [b1cm, b2cm, b3cm, b4cm, b5cm],
    )

    dim_scores = _build_dim_scores([d1, d2, d3, d4, d5, d6, d7])

    commitments = []
    if cm_text.strip():
        commitments = [{
            "domain": cm_domain,
            "commitment": cm_text,
            "falsification_condition": cm_falsify,
            "test_horizon": cm_horizon,
        }]

    try:
        report = _orch.synthesize(
            system_name=system_name.strip(),
            system_type=system_type,
            body_specs=body_specs,
            dim_scores=dim_scores,
            context=context,
            commitments=commitments,
        )
        store.save_session(report)
        full = report.full_report()
        summary = (
            f"**{system_name}** — "
            f"Synthesis: **{report.synthesis_score:.4f}** "
            f"[{report.synthesis_grade[0]} — {report.synthesis_grade[1]}]  \n"
            f"Omega: {report.omega_score:.4f} · Integrity: {report.integrity_score:.4f} · "
            f"Session: `{report.session_id}`"
        )
        return summary, full
    except Exception as exc:
        return f"❌ Error: {exc}", ""


# ── Tab 3: Decision Oracle ────────────────────────────────────────────────────

def run_decision(
    question,
    system_name, system_type,
    b1n, b1s, b1p,
    b2n, b2s, b2p,
    b3n, b3s, b3p,
    b4n, b4s, b4p,
    b5n, b5s, b5p,
    # Option A
    a_name, a_desc,
    a_i1d, a_i1m, a_i2d, a_i2m, a_i3d, a_i3m, a_i4d, a_i4m, a_i5d, a_i5m,
    a_pt,
    # Option B
    b_name, b_desc,
    b_i1d, b_i1m, b_i2d, b_i2m, b_i3d, b_i3m, b_i4d, b_i4m, b_i5d, b_i5m,
    b_pt,
    # Option C (optional)
    c_name, c_desc,
    c_i1d, c_i1m, c_i2d, c_i2m, c_i3d, c_i3m, c_i4d, c_i4m, c_i5d, c_i5m,
    c_pt,
):
    if not question.strip():
        return "⚠️  Please enter a decision question.", ""
    if not system_name.strip():
        return "⚠️  Please enter a system name.", ""

    labels = [b1n or DEFAULT_PENTAD_BODIES[0],
              b2n or DEFAULT_PENTAD_BODIES[1],
              b3n or DEFAULT_PENTAD_BODIES[2],
              b4n or DEFAULT_PENTAD_BODIES[3],
              b5n or DEFAULT_PENTAD_BODIES[4]]

    body_specs = [
        {"label": labels[0], "status": b1s, "phi_trust": float(b1p)},
        {"label": labels[1], "status": b2s, "phi_trust": float(b2p)},
        {"label": labels[2], "status": b3s, "phi_trust": float(b3p)},
        {"label": labels[3], "status": b4s, "phi_trust": float(b4p)},
        {"label": labels[4], "status": b5s, "phi_trust": float(b5p)},
    ]

    def build_impacts(dirs_, mags_):
        impacts = []
        for lbl, d_, m_ in zip(labels, dirs_, mags_):
            if d_ != "neutral":
                impacts.append({"body_label": lbl, "direction": d_, "magnitude": float(m_)})
        return impacts

    options = [
        {
            "name": a_name or "Option A",
            "description": a_desc,
            "impacts": build_impacts(
                [a_i1d, a_i2d, a_i3d, a_i4d, a_i5d],
                [a_i1m, a_i2m, a_i3m, a_i4m, a_i5m],
            ),
            "phi_trust_impact": float(a_pt),
        },
        {
            "name": b_name or "Option B",
            "description": b_desc,
            "impacts": build_impacts(
                [b_i1d, b_i2d, b_i3d, b_i4d, b_i5d],
                [b_i1m, b_i2m, b_i3m, b_i4m, b_i5m],
            ),
            "phi_trust_impact": float(b_pt),
        },
    ]
    if c_name.strip():
        options.append({
            "name": c_name,
            "description": c_desc,
            "impacts": build_impacts(
                [c_i1d, c_i2d, c_i3d, c_i4d, c_i5d],
                [c_i1m, c_i2m, c_i3m, c_i4m, c_i5m],
            ),
            "phi_trust_impact": float(c_pt),
        })

    try:
        report = _orch.synthesize(
            system_name=system_name.strip(),
            system_type=system_type,
            body_specs=body_specs,
            dim_scores={k: 0.7 for k, _ in AUDIT_DIMENSIONS},
            decision_question=question.strip(),
            decision_options=options,
        )
        da = report.decision_analysis
        best = da.best_option()
        summary = (
            f"**Question:** {question}  \n"
            f"✅ **Highest resonance:** {best.name}  \n"
            f"Score: {da.ranked_options[0][0]:+.3f}"
        )
        return summary, da.summary()
    except Exception as exc:
        return f"❌ Error: {exc}", ""


# ── Tab 5: History ────────────────────────────────────────────────────────────

def load_history():
    rows = store.load_sessions(50)
    if not rows:
        return "No sessions recorded yet.  Run a synthesis first."
    lines = ["| Session | System | Type | Synthesis | Omega | Integrity | Grade | Date |",
             "|---------|--------|------|-----------|-------|-----------|-------|------|"]
    for r in rows:
        lines.append(
            f"| `{r['id']}` | {r['system_name'][:30]} | {r['system_type'][:20]} "
            f"| {r['synthesis_score']:.4f} | {r['omega_score']:.4f} "
            f"| {r['integrity_score']:.4f} | {r['grade']} | {r['created_at'][:10]} |"
        )
    return "\n".join(lines)


def load_session_detail(session_id: str):
    if not session_id.strip():
        return "Enter a session ID to retrieve its full report."
    text = store.load_session_report(session_id.strip())
    return text or f"No session found with id '{session_id.strip()}'."


# ── Build the Gradio app ──────────────────────────────────────────────────────

def build_app() -> gr.Blocks:

    def _body_block(idx: int, label: str):
        """Returns input components for one Pentad body."""
        with gr.Group():
            gr.Markdown(f"### {label}")
            with gr.Row():
                name = gr.Textbox(
                    label="Body name / label (optional override)",
                    placeholder=label, scale=3,
                )
                status = gr.Dropdown(STATUS_CHOICES, value="ESTIMATED", label="Epistemic status")
                phi   = gr.Slider(0.0, 1.0, value=0.5, step=0.05, label="φ_trust (authenticity)")
            with gr.Accordion("Detail (optional but improves the report)", open=False):
                desc  = gr.Textbox(label="Current state", lines=2)
                found = gr.Textbox(label="Foundations — what is working", lines=2)
                con   = gr.Textbox(label="Constraints — real limits", lines=2)
                gaps  = gr.Textbox(label="Open gaps — what is unresolved", lines=2)
                cmts  = gr.Textbox(label="Falsifiable commitment (what would prove you wrong)", lines=2)
        return name, status, phi, desc, found, con, gaps, cmts

    with gr.Blocks(
        title="AxiomZero Ω Oracle",
        theme=gr.themes.Soft(primary_hue="indigo", neutral_hue="slate"),
        css="""
            .output-report { font-family: 'Courier New', monospace; font-size: 0.82em; }
            .synthesis-summary { font-size: 1.1em; }
        """,
    ) as app:

        gr.HTML("""
        <div style="text-align:center; padding:24px 0 8px">
          <h1 style="font-size:2.4em; margin-bottom:4px">AxiomZero <span style="color:#6366f1">Ω</span> Oracle</h1>
          <p style="color:#64748b; max-width:680px; margin:0 auto">
            Apply the full AxiomZero epistemic framework to any real-world system.<br>
            Five seed constants · Physics-grounded mathematics · No black boxes.
          </p>
        </div>
        """)

        with gr.Tabs():

            # ── TAB 1+2+4: Full Synthesis ────────────────────────────────────
            with gr.TabItem("📊 Synthesis"):
                gr.Markdown("""
                **Map any system to a five-body Pentad, score its governance integrity,
                and receive a complete Synthesis Report.**

                All mathematics is traceable to five seed constants:
                `N_W=5, N_2=7, K_CS=74, C_S=12/37, Ξ_c=35/74`.
                """)

                with gr.Row():
                    sn = gr.Textbox(
                        label="System name",
                        placeholder="e.g. City of Seattle, My Research Project, …",
                        scale=3,
                    )
                    st = gr.Dropdown(SYSTEM_TYPE_CHOICES, label="System type", value="Organisation / Company")
                ctx = gr.Textbox(label="Context (optional background)", lines=2)

                gr.Markdown("## 🔵 Five-Body Pentad")
                gr.Markdown(
                    "Define the five fundamental bodies of your system.  "
                    "Use the default labels or rename them to fit your system."
                )

                body_inputs: list = []
                for i, lbl in enumerate(DEFAULT_PENTAD_BODIES):
                    body_inputs.extend(_body_block(i, lbl))

                gr.Markdown("## ⚖️ Governance Audit (Seven Dimensions)")
                gr.Markdown("Score each governance dimension 0.0 (failing) → 1.0 (exemplary).")

                dim_sliders = []
                with gr.Row():
                    for key, desc in AUDIT_DIMENSIONS:
                        dim_sliders.append(
                            gr.Slider(0.0, 1.0, value=0.6, step=0.05, label=key)
                        )

                gr.Markdown("## 📌 Falsifiable Commitment (optional)")
                with gr.Row():
                    cm_domain  = gr.Textbox(label="Domain", placeholder="e.g. Governance")
                    cm_text    = gr.Textbox(label="Commitment", placeholder="What are you betting on?")
                with gr.Row():
                    cm_falsify = gr.Textbox(label="Falsification condition", placeholder="What would prove you wrong?")
                    cm_horizon = gr.Textbox(label="Test horizon", placeholder="e.g. 90 days")

                run_btn = gr.Button("🔮  Run Grand Synthesis", variant="primary", size="lg")
                sum_out = gr.Markdown(elem_classes=["synthesis-summary"])
                rep_out = gr.Textbox(
                    label="Full Synthesis Report",
                    lines=60,
                    elem_classes=["output-report"],
                    interactive=False,
                )

                run_btn.click(
                    run_synthesis,
                    inputs=[sn, st, ctx, *body_inputs, *dim_sliders,
                            cm_domain, cm_text, cm_falsify, cm_horizon],
                    outputs=[sum_out, rep_out],
                )

            # ── TAB 2: Decision Oracle ────────────────────────────────────────
            with gr.TabItem("💡 Decision Oracle"):
                gr.Markdown("""
                **Evaluate any multi-option decision against your current system state.**

                The resonance score ranks options by how well each repairs open bodies
                and avoids harming solid ones — using the OmegaHolon decision algorithm
                extended with the five-body coupling tensor.
                """)

                dq = gr.Textbox(label="Decision question", placeholder="Should we expand to a second location?")
                with gr.Row():
                    dsn = gr.Textbox(label="System name", placeholder="My Organisation")
                    dst = gr.Dropdown(SYSTEM_TYPE_CHOICES, label="System type", value="Organisation / Company")

                gr.Markdown("### Current System State (five bodies)")
                dbl = []
                for i, lbl in enumerate(DEFAULT_PENTAD_BODIES):
                    with gr.Row():
                        n = gr.Textbox(label=f"Ψ{i+1} name", value=lbl, scale=3)
                        s = gr.Dropdown(STATUS_CHOICES, value="ESTIMATED", label="Status")
                        p = gr.Slider(0.0, 1.0, value=0.5, step=0.05, label="φ_trust")
                    dbl.extend([n, s, p])

                DIR_CHOICES = ["neutral", "improve", "harm"]

                def _option_block(letter: str):
                    gr.Markdown(f"### Option {letter}")
                    on   = gr.Textbox(label="Name", placeholder=f"Option {letter}")
                    odsc = gr.Textbox(label="Description", lines=1)
                    impacts = []
                    for i, lbl in enumerate(DEFAULT_PENTAD_BODIES):
                        with gr.Row():
                            gr.Markdown(f"**{lbl}**", scale=2)
                            d_ = gr.Dropdown(DIR_CHOICES, value="neutral", label="Direction", scale=1)
                            m_ = gr.Slider(0.0, 2.0, value=1.0, step=0.25, label="Magnitude", scale=1)
                        impacts.extend([d_, m_])
                    pt = gr.Slider(-1.0, 1.0, value=0.0, step=0.1, label="φ_trust impact")
                    return [on, odsc] + impacts + [pt]

                with gr.Row():
                    with gr.Column():
                        a_inputs = _option_block("A")
                    with gr.Column():
                        b_inputs = _option_block("B")
                with gr.Accordion("Option C (optional)", open=False):
                    c_inputs = _option_block("C")

                dec_btn = gr.Button("🔮  Compute Decision Resonance", variant="primary")
                dec_sum = gr.Markdown()
                dec_rep = gr.Textbox(
                    label="Decision Analysis",
                    lines=30,
                    elem_classes=["output-report"],
                    interactive=False,
                )

                dec_btn.click(
                    run_decision,
                    inputs=[dq, dsn, dst, *dbl, *a_inputs, *b_inputs, *c_inputs],
                    outputs=[dec_sum, dec_rep],
                )

            # ── TAB 3: History ────────────────────────────────────────────────
            with gr.TabItem("📈 History"):
                gr.Markdown("""
                **Longitudinal tracking across all synthesis sessions.**

                Each time you run a synthesis, the session is saved locally in SQLite.
                Retrieve any past report by entering its session ID.
                """)
                hist_btn = gr.Button("🔄  Load session history", variant="secondary")
                hist_out = gr.Markdown()
                hist_btn.click(load_history, inputs=[], outputs=[hist_out])

                gr.Markdown("---")
                sid_in  = gr.Textbox(label="Session ID", placeholder="Enter an 8-char session ID")
                sid_btn = gr.Button("📄  Load session report")
                sid_out = gr.Textbox(
                    label="Session report",
                    lines=40,
                    elem_classes=["output-report"],
                    interactive=False,
                )
                sid_btn.click(load_session_detail, inputs=[sid_in], outputs=[sid_out])

            # ── TAB 4: Mathematics ────────────────────────────────────────────
            with gr.TabItem("𝕄 Mathematics"):
                gr.Markdown(f"""
# The Mathematics of the Ω Oracle

## Five Seed Constants

Every number in this system flows from exactly five inputs:

| Constant | Value | Source |
|----------|-------|--------|
| N_W = 5 | Primary winding number | Planck CMB nₛ |
| N_2 = 7 | Braid partner | BICEP/Keck r < 0.036 |
| K_CS = 74 | Chern-Simons level = 5² + 7² | Resonance identity |
| C_S = 12/37 ≈ {C_S_F:.5f} | Braided sound speed | Braid kinematics |
| Ξ_c = 35/74 ≈ {XI_C_F:.5f} | Consciousness coupling | Brain-universe fixed point |

---

## Stability Floor

```
stability_floor(n) = min(1.0,  C_S  +  n × C_S / N_2)
```

| n (aligned bodies) | Stability |
|-------------------|-----------|
{chr(10).join(f"| {n} | {stability_floor(n):.4f} |" for n in range(0, 8))}

---

## Omega Score

```
omega_score = stability_floor(n_aligned) × avg_resonance
avg_resonance = (1/5) × Σ(status_weight_i × phi_trust_i)
```

Status weights: SOLID=1.00, CONSTRAINED=0.75, ESTIMATED=0.40, OPEN=0.00

---

## Synthesis Score (Grand Unified)

```
synthesis = Ξ_c × omega_score + (1 − Ξ_c) × integrity_score
          = {XI_C_F:.5f} × Ω + {1.0-XI_C_F:.5f} × I
```

---

## Decision Resonance

```
resonance(option) = Σ(impact_multiplier × magnitude) + Ξ_c × Δφ_trust
```

| Situation | Multiplier |
|-----------|-----------|
| Improving an OPEN body | +2.0 |
| Improving an ESTIMATED body | +1.5 |
| Harming a SOLID body | −2.0 |
| Harming a CONSTRAINED body | −1.5 |

---

## Authenticity Crisis

```
avg_phi_trust < C_S ≈ {C_S_F:.4f}  →  AUTHENTICITY CRISIS
```

The same threshold that governs the HILS Pentad decoupling condition governs
the authenticity crisis in a human system.

---

*Physics: [Unitary Manifold v20.1](https://github.com/wuzbak/Unitary-Manifold-)*  
*Theory: ThomasCory Walker-Pearson · Code: GitHub Copilot (AI)*  
*License: Defensive Public Commons v1.0*
                """)

            # ── TAB 5: About ─────────────────────────────────────────────────
            with gr.TabItem("ℹ️ About"):
                gr.Markdown("""
# AxiomZero Ω Oracle — About

## What This Is

The AxiomZero Ω Oracle is **Product 16** of the AxiomZero Technologies product suite.
It is the Grand Synthesis: the capstone engine that unifies all prior AxiomZero products
into a single, universally applicable intelligence layer.

Where each prior product goes deep on one domain —
EIGE governs elections, OmegaHolon governs personal life, the Omega Synthesis governs physics —
the Oracle applies the *same mathematics* to **any** real-world system.

A democracy, a nonprofit, a team, a policy, a community, a person's career — all can be
modelled as a Pentad, all can receive a Synthesis Report, all can have falsifiable commitments.

## The Philosophy

Every system has bodies.  Every body has epistemic status.  Every system has a phi_trust
threshold below which it loses coherence.  The Oracle makes this rigorous.

> *"The same five seed constants that generate the observable universe also generate a
> coherent framework for any human system."*

## What It Draws From

| Product | Contribution |
|---------|-------------|
| 06 — Omega Synthesis | Universal mechanics; stability floor formula |
| 07 — Holon Zero | Epistemic status classification |
| 09 — OmegaHolon | Personal coherence → generalised to any system |
| 03 — EIGE | Governance audit framework |
| 05 — UOS Kernel | Five-body geometric coupling |
| Unitary Pentad | HILS stability mathematics |

## Ethics

This tool is released under the **Defensive Public Commons License v1.0**.
All source code is public.  No data leaves your machine (SQLite, local only).
The mathematics is fully auditable — every number has a traceable equation.

The Oracle does not provide legal, medical, or financial advice.
It provides a structured epistemic framework for clearer thinking.

## Authorship

*Theory, framework, product vision, and philosophical direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*

AxiomZero Technologies & Consulting, SPC — Washington State  
Defensive Public Commons License v1.0 — 2026
                """)

    return app


def main():
    store.init_db()
    app = build_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7872,
        show_error=True,
    )


if __name__ == "__main__":
    main()
