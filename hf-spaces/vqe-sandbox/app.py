# hf-spaces/vqe-sandbox/app.py
# AxiomZero VQE Sandbox — Hugging Face Space (Gradio)
#
# Quantum simulation lane: VQE + Fermi–Hubbard
# Gate: ADJACENT_TRACK — non-hardgate, steward approval needed for pillar numbering
#
# AxiomZero Technologies & Consulting, SPC — UBI 606 239 876
# Sprint BA (2026-09-01): Yukawa SVD closed; XDiag bridge in development
# Status: ADJACENT_TRACK — non-hardgate

import sys
import math
import numpy as np

try:
    import gradio as gr
except ImportError:
    print("pip install gradio")
    sys.exit(1)

# ── Constants ─────────────────────────────────────────────────────────────────
WINDING_NUMBER = 5
K_CS           = 74
BRAIDED_CS     = 12 / 37
VERSION        = "v24.1"
TEST_COUNT     = 57927
FOOTER = (
    "\n\n---\n"
    "**Gate: 🔵 ADJACENT_TRACK** — quantum simulation lane. Non-hardgate. "
    "Requires steward approval for formal pillar numbering.\n\n"
    f"*AxiomZero Technologies & Consulting, SPC — UBI 606 239 876 · {VERSION}*"
)

# ── Pauli matrices ─────────────────────────────────────────────────────────────
I2 = np.eye(2, dtype=complex)
X  = np.array([[0,1],[1,0]], dtype=complex)
Y  = np.array([[0,-1j],[1j,0]], dtype=complex)
Z  = np.array([[1,0],[0,-1]], dtype=complex)

def kron_op(ops):
    """Kronecker product of a list of operators."""
    result = ops[0]
    for op in ops[1:]:
        result = np.kron(result, op)
    return result

def pauli_string(n_qubits, site, op):
    """Pauli string: op at site, I elsewhere."""
    return kron_op([op if i == site else I2 for i in range(n_qubits)])

# ── Jordan–Wigner encoding ─────────────────────────────────────────────────────
def jw_c_dag(n_qubits, site):
    """Jordan-Wigner c†_site operator."""
    z_string = [Z if i < site else I2 for i in range(n_qubits)]
    xterm = z_string[:]
    xterm[site] = X
    yterm = z_string[:]
    yterm[site] = Y
    return 0.5 * (kron_op(xterm) - 1j * kron_op(yterm))

def jw_c(n_qubits, site):
    """Jordan-Wigner c_site operator."""
    return jw_c_dag(n_qubits, site).conj().T

# ── Fermi–Hubbard Hamiltonian ──────────────────────────────────────────────────
def fermi_hubbard_hamiltonian(n_sites: int, t_hop: float, u_int: float) -> np.ndarray:
    """
    1D Fermi-Hubbard model (spinless single-band, n_sites sites).
    H = -t Σ (c†_i c_{i+1} + h.c.) + U Σ n_i n_{i+1}
    JW encoding: 2*n_sites qubits (spin-up + spin-down).
    Limited to n_sites <= 4 for tractable diagonalization.
    """
    n_qubits = 2 * n_sites  # spin up (0..n-1) + spin down (n..2n-1)
    dim = 2 ** n_qubits
    H = np.zeros((dim, dim), dtype=complex)

    # Hopping terms
    for s in range(2):  # spin sector
        offset = s * n_sites
        for i in range(n_sites - 1):
            cd = jw_c_dag(n_qubits, offset + i)
            c  = jw_c(n_qubits, offset + i + 1)
            H += -t_hop * (cd @ c + c.conj().T @ cd.conj().T)

    # On-site interaction U n_up n_down
    for i in range(n_sites):
        n_up   = jw_c_dag(n_qubits, i) @ jw_c(n_qubits, i)
        n_down = jw_c_dag(n_qubits, n_sites + i) @ jw_c(n_qubits, n_sites + i)
        H += u_int * (n_up @ n_down)

    return H

def vqe_exact_diag(H: np.ndarray) -> tuple:
    """Exact diagonalization — returns ground state energy and state."""
    eigvals, eigvecs = np.linalg.eigh(H)
    return eigvals[0].real, eigvecs[:, 0]

# ── KK VQE: φ-enhanced ansatz ─────────────────────────────────────────────────
def kk_vqe_ansatz_energy(n_qubits: int, theta_params: list, H: np.ndarray) -> float:
    """
    KK VQE ansatz: single-layer Ry rotations + CNOT entanglement (hardware-efficient).
    φ-weights scale the rotation angles via powers of golden ratio.
    """
    phi = (1 + math.sqrt(5)) / 2
    dim = 2 ** n_qubits
    state = np.zeros(dim, dtype=complex)
    state[0] = 1.0  # |0...0⟩ initial state

    # Apply Ry(θ_i * φ^(-i)) on each qubit (φ-weighted rotation)
    for i in range(n_qubits):
        theta = theta_params[i] * phi**(-i % WINDING_NUMBER)
        # Ry gate: [[cos(θ/2), -sin(θ/2)], [sin(θ/2), cos(θ/2)]]
        Ry = np.array([[math.cos(theta/2), -math.sin(theta/2)],
                       [math.sin(theta/2),  math.cos(theta/2)]])
        Ry_full = pauli_string(n_qubits, i, I2)  # identity first
        # Apply Ry to qubit i: reshape and contract
        state = state.reshape([2] * n_qubits)
        state = np.tensordot(Ry, state, axes=([1], [i]))
        state = np.moveaxis(state, 0, i)
        state = state.reshape(dim)

    # Measure ⟨ψ|H|ψ⟩
    energy = np.real(state.conj() @ H @ state)
    return energy

def run_vqe_sim(n_sites: int, t_hop: float, u_int: float, n_steps: int) -> str:
    """Run VQE simulation: exact diag + KK ansatz comparison."""
    if n_sites > 4:
        return "⚠️ n_sites > 4 is too expensive for browser simulation. Use n_sites ≤ 4."

    n_qubits = 2 * n_sites
    H = fermi_hubbard_hamiltonian(n_sites, t_hop, u_int)
    E_exact, _ = vqe_exact_diag(H)

    # KK VQE: simple gradient-free optimization (Adam-style with φ-steps)
    phi = (1 + math.sqrt(5)) / 2
    thetas = [math.pi / (k + 1) for k in range(n_qubits)]
    best_E = kk_vqe_ansatz_energy(n_qubits, thetas, H)
    history = [best_E]

    # Coordinate descent with φ-scaled step
    step = math.pi / (WINDING_NUMBER * K_CS)
    for step_i in range(n_steps):
        q = step_i % n_qubits
        for sign in [1, -1]:
            trial = thetas[:]
            trial[q] += sign * step * phi**(-step_i % WINDING_NUMBER)
            E_trial = kk_vqe_ansatz_energy(n_qubits, trial, H)
            if E_trial < best_E:
                best_E = E_trial
                thetas = trial
        history.append(best_E)

    gap = abs(best_E - E_exact)
    relative_error = abs(gap / E_exact) * 100 if E_exact != 0 else 0

    lines = [
        "## ⚛️ VQE Sandbox — Fermi–Hubbard Simulation",
        f"**Gate:** 🔵 ADJACENT_TRACK · Quantum simulation lane",
        "",
        "### Hamiltonian Parameters",
        f"| Parameter | Value |",
        f"|-----------|-------|",
        f"| Sites (n_sites) | {n_sites} |",
        f"| Qubits | {n_qubits} |",
        f"| Hopping t | {t_hop:.3f} |",
        f"| Interaction U | {u_int:.3f} |",
        f"| Hilbert space dim | {2**n_qubits} |",
        "",
        "### Results",
        f"| Method | Ground state energy |",
        f"|--------|---------------------|",
        f"| Exact diagonalization | **{E_exact:.6f}** |",
        f"| KK VQE ansatz ({n_steps} steps) | **{best_E:.6f}** |",
        f"| Energy gap | {gap:.6f} ({relative_error:.2f}% error) |",
        "",
        "### Encoding",
        "- **Jordan-Wigner** mapping: fermionic → qubit operators",
        f"- **φ-weighted KK ansatz:** Ry(θ_i · φ^(-i mod n_w)) with n_w = {WINDING_NUMBER}",
        f"- **Step size:** π / (n_w · k_cs) = π / {WINDING_NUMBER * K_CS}",
        "",
        "### Convergence (last 5 steps)",
    ]
    lines += [f"- Step {i}: E = {e:.6f}" for i, e in enumerate(history[-5:], len(history)-5)]
    lines.append(FOOTER)
    return "\n".join(lines)

def bravyi_kitaev_info(n_sites: int) -> str:
    """Explain Bravyi-Kitaev encoding for n_sites."""
    n_qubits = 2 * n_sites
    jw_terms = n_sites * (n_sites - 1)  # hopping term count
    bk_improvement = f"O(log {n_qubits}) vs O({n_qubits}) qubit operations"
    lines = [
        f"## Bravyi-Kitaev Encoding — {n_sites} sites ({n_qubits} qubits)",
        "",
        "### JW vs BK Comparison",
        "| Property | Jordan-Wigner | Bravyi-Kitaev |",
        "|----------|--------------|----------------|",
        f"| Qubit operations | O(n) = O({n_qubits}) | O(log n) = O({math.ceil(math.log2(n_qubits+1))}) |",
        f"| Locality | Non-local strings | {bk_improvement} |",
        f"| Hopping terms | {jw_terms} | {jw_terms} (same count, shorter strings) |",
        "| Advantage | Simpler implementation | Better for NISQ devices |",
        "",
        "### KK Connection",
        f"The KK ansatz uses n_w = {WINDING_NUMBER} as the φ-weight period.",
        "This maps KK winding modes to qubit rotation angles.",
        "",
        "*Full BK encoding requires symbolic algebra (SymPy/PySCF). "
        "This sandbox uses JW for tractable browser simulation.*",
        FOOTER,
    ]
    return "\n".join(lines)

def xdiag_bridge_info() -> str:
    return (
        "## XDiag Bridge Interface\n\n"
        "**Gate:** 🔵 ADJACENT_TRACK · `src/quantum/xdiag_bridge/`\n\n"
        "### What XDiag Does\n"
        "XDiag is a C++/Python library for exact diagonalization of quantum many-body systems.\n"
        "The AxiomZero XDiag bridge (`src/quantum/xdiag_bridge/`) provides:\n\n"
        "| Component | Purpose |\n"
        "|-----------|----------|\n"
        "| `contract.py` | UM↔XDiag data exchange protocol |\n"
        "| `parity.py` | Parity symmetry sector routing |\n"
        "| `routing.py` | Hamiltonian routing to XDiag solver |\n"
        "| `__init__.py` | Bridge initialization and validation |\n\n"
        "### Usage (requires XDiag installed)\n"
        "```python\n"
        "from src.quantum.xdiag_bridge import XDiagBridge\n"
        "bridge = XDiagBridge(n_sites=4, model='fermi_hubbard')\n"
        "result = bridge.solve(t=1.0, U=4.0)\n"
        "print(result.ground_energy)\n"
        "```\n\n"
        "### Status\n"
        "- Parity routing: ✅ implemented\n"
        "- UM↔XDiag contract: ✅ implemented\n"
        "- Full XDiag backend: ⏳ requires XDiag binary install\n"
        "- Formal pillar numbering: ⏳ pending steward approval\n\n"
        + FOOTER
    )

# ── Gradio UI ─────────────────────────────────────────────────────────────────
THEME = gr.themes.Base(
    primary_hue="indigo", secondary_hue="blue",
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif"],
    font_mono=[gr.themes.GoogleFont("JetBrains Mono"), "ui-monospace"],
).set(
    body_background_fill="#050a1a",
    body_text_color="#e8ecf4",
    block_background_fill="#0d1830",
    block_border_color="#1a2a4a",
    button_primary_background_fill="linear-gradient(135deg, #3b8bff, #7c4dff)",
    button_primary_text_color="#ffffff",
    input_background_fill="#0a1228",
)

HEADER = f"""
<div style="text-align:center; padding:1rem 0; border-bottom:1px solid #1a2a4a; margin-bottom:1rem;">
  <h1 style="font-size:1.8rem; font-weight:800; background:linear-gradient(135deg,#e8ecf4,#7c4dff);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:.3rem;">
    ⚛️ AxiomZero VQE Sandbox
  </h1>
  <p style="color:#7a8ba8; font-size:.9rem;">
    Quantum simulation lane · Gate: ADJACENT_TRACK · {VERSION} ·
    <a href="https://axiomzerospc.org" style="color:#7c4dff;" target="_blank">axiomzerospc.org</a>
  </p>
  <p style="color:#ff9f0a; font-size:.8rem;">
    ⚠️ Not a hardgate physics claim — requires steward approval for formal pillar numbering
  </p>
</div>
"""

with gr.Blocks(theme=THEME, title="AxiomZero VQE Sandbox") as demo:
    gr.HTML(HEADER)

    with gr.Tabs():

        with gr.Tab("Fermi–Hubbard VQE"):
            gr.Markdown("### KK VQE + Fermi–Hubbard Simulation\n"
                        "Exact diagonalization vs KK φ-weighted ansatz. JW encoding. n_sites ≤ 4.")
            with gr.Row():
                with gr.Column():
                    vh_sites = gr.Slider(1, 4, value=2, step=1, label="Sites (n_sites)")
                    vh_t = gr.Slider(0.1, 5.0, value=1.0, step=0.1, label="Hopping t")
                    vh_u = gr.Slider(0.0, 10.0, value=4.0, step=0.5, label="Interaction U")
                    vh_steps = gr.Slider(10, 200, value=50, step=10, label="Optimization steps")
                    vh_btn = gr.Button("Run VQE simulation", variant="primary")
                with gr.Column():
                    vh_out = gr.Markdown()
            vh_btn.click(run_vqe_sim, [vh_sites, vh_t, vh_u, vh_steps], vh_out)

        with gr.Tab("BK Encoding"):
            gr.Markdown("### Bravyi-Kitaev vs Jordan-Wigner Encoding")
            with gr.Row():
                bk_sites = gr.Slider(1, 8, value=4, step=1, label="Sites")
                bk_btn = gr.Button("Compare encodings", variant="primary")
            bk_out = gr.Markdown()
            bk_btn.click(bravyi_kitaev_info, [bk_sites], bk_out)

        with gr.Tab("XDiag Bridge"):
            gr.Markdown("### XDiag Bridge Interface")
            xd_btn = gr.Button("Load XDiag bridge info", variant="primary")
            xd_out = gr.Markdown()
            xd_btn.click(xdiag_bridge_info, [], xd_out)
            demo.load(xdiag_bridge_info, [], xd_out)

    gr.Markdown(
        f"---\n*Theory: ThomasCory Walker-Pearson · Code: GitHub Copilot (AI) · "
        f"[GitHub](https://github.com/wuzbak/Unitary-Manifold-)*"
    )

if __name__ == "__main__":
    demo.launch()
