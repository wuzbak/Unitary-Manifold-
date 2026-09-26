import gradio as gr
import requests
import os
import random

HF_API_KEY = os.environ.get("HUGGINGFACE_API_KEY", "")
GITHUB_REPO = "wuzbak/Unitary-Manifold-"

custom_css = """
:root { --az-bg: #0B0F13; --az-panel: #111820; --az-amber: #FF9F00; --az-teal: #4DD0E1; --az-text: #E0E0E0; --az-muted: #8B949E; --az-border: #1F2933; }
.gradio-container { background: var(--az-bg) !important; color: var(--az-text) !important; font-family: 'Inter', system-ui, sans-serif !important; }
.gradio-container h1, .gradio-container h2 { font-family: 'JetBrains Mono', monospace !important; color: var(--az-amber) !important; }
.gradio-container .gr-block { background: var(--az-panel) !important; border: 1px solid var(--az-border) !important; border-radius: 0 !important; }
.gradio-container .gr-button-primary { background: var(--az-amber) !important; color: var(--az-bg) !important; border: none !important; border-radius: 0 !important; font-family: 'JetBrains Mono', monospace !important; text-transform: uppercase !important; }
"""

PILLARS = [
    {"id": "301", "name": "Cosmological Constant", "prompt": "What is the value of w_a (cosmological constant) in the Unitary Manifold Framework?", "answer": "0", "tier": "easy", "domain": "cosmology"},
    {"id": "396", "name": "Tensor-to-Scalar Ratio", "prompt": "What is the predicted tensor-to-scalar ratio r in the UM Framework?", "answer": "0.0315", "tier": "easy", "domain": "cosmology"},
    {"id": "789", "name": "Winding Resonance", "prompt": "What is the unique integer n_w satisfying all three CMB constraints?", "answer": "5", "tier": "medium", "domain": "geometry"},
    {"id": "CS", "name": "Chern-Simons Level", "prompt": "What is the Chern-Simons level k_CS, and how is it derived from the (5,7) sector?", "answer": "74", "tier": "easy", "domain": "geometry"},
    {"id": "ns", "name": "Scalar Spectral Index", "prompt": "What is the scalar spectral index n_s predicted by the framework?", "answer": "0.9635", "tier": "medium", "domain": "cosmology"},
    {"id": "793", "name": "KK Graviton Mass", "prompt": "What is the predicted mass of the KK graviton (n=1 mode)?", "answer": "1.0", "tier": "hard", "domain": "particle physics"},
    {"id": "DIM", "name": "Dimensionality", "prompt": "How many dimensions does the Kaluza-Klein metric use?", "answer": "5", "tier": "easy", "domain": "geometry"},
    {"id": "787", "name": "Falsification Oracle", "prompt": "How many live experiments are in the falsification routing oracle (Pillar 787)?", "answer": "7", "tier": "medium", "domain": "epistemology"},
]

session = {"current": None, "score": 0, "total": 0, "streak": 0}

def get_challenge(tier):
    pool = [p for p in PILLARS if tier == "all" or p["tier"] == tier]
    if not pool: pool = PILLARS
    challenge = random.choice(pool)
    session["current"] = challenge
    return f"Pillar {challenge['id']} \u2014 {challenge['name']}\nDomain: {challenge['domain']}\nTier: {challenge['tier']}\n\n{challenge['prompt']}"

def submit_answer(answer):
    if not session["current"]: return "No active challenge. Click GET CHALLENGE first."
    correct = session["current"]["answer"]
    session["total"] += 1
    # Fuzzy match
    is_correct = answer.strip().lower() == correct.lower() or correct.lower() in answer.strip().lower()
    if is_correct:
        session["score"] += 1
        session["streak"] += 1
        result = f"\u2705 CORRECT! Answer: {correct}\nStreak: {session['streak']}\nScore: {session['score']}/{session['total']}"
    else:
        session["streak"] = 0
        result = f"\u274c Incorrect. Expected: {correct}\nStreak reset.\nScore: {session['score']}/{session['total']}"
    return result

def get_status():
    try:
        s = requests.get(f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/9-INFRASTRUCTURE/um_live_status.json", headers={"User-Agent":"AZ"}, timeout=10).json()
        l = s.get("lean4",{}).get("theorem_count",0)
        p = s.get("pillars",{}).get("total_slots",0)
        t = s.get("tests",{}).get("passed",0)
        return f"<div style='font-family:monospace;color:#4DD0E1;'>LEAN4: {l:,} | PILLARS: {p} | TESTS: {t:,}</div>"
    except: return "<div style='color:#8B949E;'>Status unavailable</div>"

with gr.Blocks(css=custom_css, title="Training Gym — AxiomZero") as app:
    gr.HTML('<div style="text-align:center;padding:2rem 0;border-bottom:2px solid #FF9F00;margin-bottom:1rem;"><h1 style="font-size:2.5rem;color:#FF9F00 !important;font-family:JetBrains Mono,monospace !important;margin:0;">TRAINING GYM</h1><div style="color:#4DD0E1;font-family:monospace;font-size:0.85rem;letter-spacing:0.1em;margin-top:0.5rem;">PILLAR CHALLENGE CONSOLE · AXIOMZERO</div></div>')
    status = gr.HTML()
    app.load(get_status, [], [status])
    with gr.Tabs():
        with gr.Tab("CHALLENGES"):
            tier = gr.Dropdown(["all","easy","medium","hard"], value="easy", label="Difficulty Tier")
            ch_btn = gr.Button("GET CHALLENGE", variant="primary")
            challenge_out = gr.Textbox(label="Challenge", lines=6, interactive=False)
            answer_in = gr.Textbox(label="Your Answer", placeholder="Type your answer...")
            submit_btn = gr.Button("SUBMIT ANSWER", variant="primary")
            result_out = gr.Textbox(label="Result", lines=4, interactive=False)
            ch_btn.click(get_challenge, [tier], [challenge_out])
            submit_btn.click(submit_answer, [answer_in], [result_out])
        with gr.Tab("PILLARS"):
            html = '<div style="color:#E0E0E0;"><h2 style="color:#FF9F00;">Pillar Registry</h2><table style="width:100%;border-collapse:collapse;font-size:0.85rem;"><tr style="border-bottom:1px solid #1F2933;"><th style="text-align:left;padding:0.5rem;color:#FF9F00;">ID</th><th style="text-align:left;padding:0.5rem;color:#FF9F00;">Name</th><th style="text-align:left;padding:0.5rem;color:#FF9F00;">Tier</th><th style="text-align:left;padding:0.5rem;color:#FF9F00;">Domain</th></tr>'
            for p in PILLARS:
                html += f'<tr style="border-bottom:1px solid #1F2933;"><td style="padding:0.5rem;">{p["id"]}</td><td style="padding:0.5rem;">{p["name"]}</td><td style="padding:0.5rem;">{p["tier"]}</td><td style="padding:0.5rem;">{p["domain"]}</td></tr>'
            html += '</table></div>'
            gr.HTML(html)
        with gr.Tab("ABOUT"):
            gr.HTML('<div style="color:#E0E0E0;line-height:1.8;max-width:800px;margin:0 auto;"><h2 style="color:#FF9F00;">Training Gym</h2><p>PsiCat\'s autonomous training system. Challenges against the 208+ hardgate pillars. Difficulty scales: easy \u2192 medium \u2192 hard.</p><p style="color:#8B949E;font-size:0.85rem;">The Training Gym in the Base44 webspace has full scoring, ledger entries, and difficulty progression. This Space provides a public training interface.</p></div>')

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860, share=False, show_error=True)
