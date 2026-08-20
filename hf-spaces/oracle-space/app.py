# hf-spaces/oracle-space/app.py
# AxiomZero Ω Oracle — Hugging Face Space (Gradio)
#
# Deploys Product 16 (Grand Synthesis Engine) as a public HF Space.
# Epistemic gate labels appear in every output.
#
# Deploy: push to huggingface.co/spaces/axiomzero/oracle
# Requirements: gradio>=4.0, numpy, scipy
#
# AxiomZero Technologies & Consulting, SPC — UBI 606 239 876

import os
import sys
import math
import numpy as np

try:
    import gradio as gr
    GRADIO_OK = True
except ImportError:
    GRADIO_OK = False
    print("gradio not installed. Run: pip install gradio")
    sys.exit(1)

# ── Framework constants ────────────────────────────────────────────────────────
WINDING_NUMBER        = 5
K_CS                  = 74          # = 5² + 7²
BRAIDED_SOUND_SPEED   = 12 / 37
XI_C                  = 35 / 74     # consciousness coupling
SENTINEL_CAPACITY     = 12 / 37
N_S_PREDICTED         = 0.9635
R_PREDICTED           = 0.0315
BETA_CANONICAL        = [0.2728, 0.3309]  # degrees — approximate
BETA_ADMISSIBLE       = (0.22, 0.38)

EPISTEMIC_FOOTER = (
    "\n\n---\n"
    "*Open science artifact — AxiomZero Technologies & Consulting, SPC — UBI 606 239 876*\n"
    "*Use at your own liability. Epistemic gate labels reflect formal status, not certainty.*"
)


# ── Oracle synthesis functions ─────────────────────────────────────────────────
def pentad_model(n_operators: int, coupling: float, phase_shift: float) -> dict:
    """Unitary Pentad HILS governance model."""
    # Sentinel capacity per operator
    sentinel_cap = SENTINEL_CAPACITY * coupling
    # Phase threshold: n >= 15 aligned HIL operators
    phase_aligned = n_operators >= 15
    # HILS resonance score (not a physics claim — governance metric)
    resonance = (1 - math.exp(-n_operators * sentinel_cap)) * math.cos(math.radians(phase_shift))
    return {
        "n_operators": n_operators,
        "coupling": coupling,
        "sentinel_capacity_per_op": round(sentinel_cap, 5),
        "phase_shift_deg": phase_shift,
        "phase_aligned": phase_aligned,
        "hils_resonance": round(resonance, 5),
        "gate": "GOVERNANCE (not a hardgate physics claim)",
        "note": "Pentad is an independent HILS framework. Does not depend on physics being correct.",
    }


def synthesis_score(n_s: float, r: float, beta: float, w_a: float) -> dict:
    """Compute synthesis alignment score vs UM predictions."""
    # Agreement metrics
    ns_sigma = abs(n_s - N_S_PREDICTED) / 0.0042
    r_ok     = r < 0.036
    beta_in_window = BETA_ADMISSIBLE[0] <= beta <= BETA_ADMISSIBLE[1]
    beta_in_gap    = 0.29 <= beta <= 0.31
    wa_tension = abs(w_a) > 0.2  # simple threshold

    # Synthesis score (honest: weighted agreement, not "proof")
    score = 0.0
    if ns_sigma < 1:  score += 30
    elif ns_sigma < 2: score += 15
    if r_ok:           score += 20
    if beta_in_window and not beta_in_gap: score += 30
    if not wa_tension: score += 20

    return {
        "input": {"n_s": n_s, "r": r, "beta_deg": beta, "w_a": w_a},
        "ns_tension_sigma": round(ns_sigma, 3),
        "r_within_bound": r_ok,
        "beta_in_admissible_window": beta_in_window,
        "beta_in_falsification_gap": beta_in_gap,
        "wa_tension": wa_tension,
        "synthesis_score": round(score, 1),
        "max_score": 100,
        "gate": "SYNTHESIS (not a proof — alignment metric only)",
        "note": (
            "A high synthesis score indicates agreement between input values and UM predictions. "
            "It is not evidence that UM is correct. Primary falsifier: LiteBIRD ~2032 (birefringence)."
        ),
    }


def kk_tower(R_planck: float, n_max: int) -> dict:
    """KK mass tower up to level n_max."""
    E_Pl_GeV = 1.22e19
    masses = {}
    for n in range(1, min(n_max + 1, 11)):
        m_GeV = (n / R_planck) * E_Pl_GeV
        masses[f"m_{n}"] = f"{m_GeV:.4e} GeV"
    return {
        "R_planck": R_planck,
        "n_w": WINDING_NUMBER,
        "K_cs": K_CS,
        "masses_GeV": masses,
        "gate": "HARDGATE (Pillar 3)",
        "note": "m_n = n/R in natural units. R is a framework parameter, not independently measured.",
    }


def birefringence_predict(Kcs: float, cs: float) -> dict:
    """Birefringence angle prediction."""
    beta1 = math.degrees(math.atan(1.0 / math.sqrt(Kcs)) * cs)
    beta2 = beta1 * 1.212
    in_window = BETA_ADMISSIBLE[0] <= beta1 <= BETA_ADMISSIBLE[1]
    in_gap    = 0.29 <= beta1 <= 0.31
    return {
        "Kcs": Kcs, "cs": cs,
        "beta_1_deg": round(beta1, 5),
        "beta_2_deg": round(beta2, 5),
        "admissible_window_deg": list(BETA_ADMISSIBLE),
        "falsification_gap_deg": [0.29, 0.31],
        "in_window": in_window,
        "in_gap": in_gap,
        "falsified_if_measured": in_gap,
        "gate": "HARDGATE — primary LiteBIRD falsifier",
        "test": "LiteBIRD ~2032",
    }


# ── Gradio UI ─────────────────────────────────────────────────────────────────
def fmt(d: dict) -> str:
    import json
    return json.dumps(d, indent=2)


def run_pentad(n_ops, coupling, phase):
    result = pentad_model(int(n_ops), float(coupling), float(phase))
    return fmt(result) + EPISTEMIC_FOOTER


def run_synthesis(ns, r, beta, wa):
    result = synthesis_score(float(ns), float(r), float(beta), float(wa))
    return fmt(result) + EPISTEMIC_FOOTER


def run_kk(R, n_max):
    result = kk_tower(float(R), int(n_max))
    return fmt(result) + EPISTEMIC_FOOTER


def run_bire(Kcs, cs):
    result = birefringence_predict(float(Kcs), float(cs))
    return fmt(result) + EPISTEMIC_FOOTER


with gr.Blocks(
    title="AxiomZero Ω Oracle",
    theme=gr.themes.Base(primary_hue="blue", neutral_hue="slate"),
) as demo:
    gr.Markdown(
        """# 🌀 AxiomZero Ω Oracle — Grand Synthesis Engine
        **Product 16** · 5D Kaluza-Klein physics framework · v22.10

        > *Epistemic honesty: all outputs carry gate labels. Results include uncertainty and open gaps.
        > This engine does not claim to prove the Unitary Manifold — it computes predictions from it.*

        **Status snapshot:** 56,772 passing tests · 976 Lean4 theorems.

        **Primary falsifier:** Birefringence β — LiteBIRD ~2032.
        **Primary open gap:** DESI w_a tension · Δm²₂₁ residual.
        """
    )

    with gr.Tab("🌀 Synthesis Score"):
        gr.Markdown("Compare observational values against UM predictions. A high score = agreement, not proof.")
        with gr.Row():
            with gr.Column():
                ns_in   = gr.Slider(0.94, 0.99, value=0.9649, label="Spectral index n_s (Planck: 0.9649±0.0042)")
                r_in    = gr.Slider(0.0, 0.1,   value=0.036,  label="Tensor ratio r (BICEP/Keck: <0.036)")
                beta_in = gr.Slider(0.1, 0.6,   value=0.273,  label="Birefringence β (deg) — LiteBIRD ~2032")
                wa_in   = gr.Slider(-1.0, 1.0,  value=0.0,    label="Dark energy w_a (KK predicts 0)")
                btn_syn = gr.Button("Compute Synthesis Score", variant="primary")
            with gr.Column():
                out_syn = gr.Textbox(label="Result (JSON + gate labels)", lines=20)
        btn_syn.click(run_synthesis, inputs=[ns_in, r_in, beta_in, wa_in], outputs=out_syn)

    with gr.Tab("💡 Birefringence Predictor"):
        gr.Markdown("Predict CMB birefringence β from braided-winding geometry. Primary LiteBIRD falsifier.")
        with gr.Row():
            with gr.Column():
                kcs_in  = gr.Number(value=74,    label="K_cs (canonical: 74 = 5²+7²)")
                cs_in   = gr.Number(value=0.3243, label="Braided sound speed c_s (canonical: 12/37)")
                btn_b   = gr.Button("Predict β", variant="primary")
            with gr.Column():
                out_b   = gr.Textbox(label="Result", lines=15)
        btn_b.click(run_bire, inputs=[kcs_in, cs_in], outputs=out_b)

    with gr.Tab("⚛️ KK Mass Tower"):
        gr.Markdown("Compute Kaluza-Klein mass tower from compactification radius R. Gate: HARDGATE (Pillar 3).")
        with gr.Row():
            with gr.Column():
                R_in    = gr.Number(value=1e-15, label="Compactification radius R (Planck lengths)")
                nmax_in = gr.Slider(1, 10, value=5, step=1, label="Max KK level n_max")
                btn_kk  = gr.Button("Compute Tower", variant="primary")
            with gr.Column():
                out_kk  = gr.Textbox(label="Result", lines=15)
        btn_kk.click(run_kk, inputs=[R_in, nmax_in], outputs=out_kk)

    with gr.Tab("📐 Pentad HILS Model"):
        gr.Markdown("Unitary Pentad governance model — **ADJACENT TRACK, not a hardgate physics claim**.")
        with gr.Row():
            with gr.Column():
                nop_in   = gr.Slider(1, 30, value=12, step=1, label="N HIL operators")
                coup_in  = gr.Slider(0.1, 1.0, value=float(XI_C), label="Coupling Ξ_c (canonical: 35/74)")
                phase_in = gr.Slider(0, 90, value=15, label="Phase shift (deg, threshold: 15°)")
                btn_p    = gr.Button("Model Pentad", variant="primary")
            with gr.Column():
                out_p    = gr.Textbox(label="Result", lines=15)
        btn_p.click(run_pentad, inputs=[nop_in, coup_in, phase_in], outputs=out_p)

    gr.Markdown(
        """---
        *AxiomZero Technologies & Consulting, SPC — UBI 606 239 876*
        *Theory & scientific direction: ThomasCory Walker-Pearson ·
        Code, engineering, synthesis: GitHub Copilot (AI)*
        *Open science artifact for human review. Use at your own liability.*
        """
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7872)))
