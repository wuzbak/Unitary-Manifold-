# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/symbolic_metric.py
============================
SymPy symbolic Kaluza–Klein metric for the Unitary Manifold.

This module re-expresses the numerical ``assemble_5d_metric()`` in
``src/core/metric.py`` using SymPy symbolic objects so that

    from src.core.symbolic_metric import symbolic_5d_metric
    G, syms = symbolic_5d_metric()
    print(sympy.latex(G))

produces publication-ready LaTeX for the 5×5 KK block matrix — the
same object that appears as Equation (KK-metric) in
``6-MONOGRAPH/arxiv/main.tex``.

The symbolic layer is the bridge between the "living code" and the
formal manuscript: any change to the ansatz in ``metric.py`` should
be mirrored here so that the LaTeX output stays consistent.

Coordinate conventions
----------------------
- Capital Latin indices A, B ∈ {0,1,2,3,5}.
- Greek indices μ, ν ∈ {0,1,2,3}.
- Signature (−,+,+,+,+).
- ``g[μ,ν]`` denotes the symbolic 4×4 Lorentzian metric.
- ``B[μ]`` is the irreversibility 1-form.
- ``φ`` (phi) is the entropic dilaton / KK radion.
- ``λ`` (lam) is the KK coupling constant.

5D metric ansatz (KK block form)
---------------------------------
    ┌──────────────────────────────────────┬────────────┐
    │  g[μ,ν] + λ²φ² B[μ] B[ν]           │  λφ B[μ]  │
    ├──────────────────────────────────────┼────────────┤
    │  λφ B[ν]                             │  φ²        │
    └──────────────────────────────────────┴────────────┘

This is the standard Kaluza–Klein ansatz (Kaluza 1921, Klein 1926)
specialised to the UM irreversibility field.

Line element
------------
    ds² = φ² gμν dxμ dxν
          + φ² (dy + λ Bμ dxμ)²      [conformal frame]

or equivalently in the Einstein frame after Weyl rescaling.

Dimensional reduction
---------------------
Integrating √(−G) R₅ over the compact y ∈ [0, 2πR] using the
cylinder condition ∂₅ G_{AB} = 0 yields the 4D effective action

    S_eff = ∫ d⁴x √(−g) [R/(16πG) − ¼ Hμν H^μν + β(∇φ)² + ...]

documented in Eq. (Seff) of the manuscript.

Public API
----------
symbolic_5d_metric(n=4)
    Return (G, symbols_dict) where G is a (n+1)×(n+1) SymPy Matrix
    representing the KK metric and symbols_dict contains all declared
    SymPy symbols.

symbolic_line_element(n=4)
    Return the symbolic line element ds² as a SymPy expression.

symbolic_field_strength(n=4)
    Return the antisymmetric field-strength tensor H_{μν} = ∂_μ B_ν − ∂_ν B_μ
    as a symbolic Matrix.

symbolic_5d_ricci_scalar_decomposition()
    Return the symbolic decomposition R₅ = R₄ − 2∇²φ − 2(∂φ)²
    + ¼ λ² φ⁻¹ H_{μν} H^{μν} from Appendix A of the manuscript.

symbolic_effective_action()
    Return the integrand of S_eff (without √(−g) d⁴x) as a SymPy
    expression using abstract symbols for each coupling.

latex_5d_metric(n=4)
    Convenience: return ``sympy.latex(G)`` for immediate use in LaTeX.

latex_line_element(n=4)
    Convenience: return ``sympy.latex(ds2)`` for the line element.

latex_field_strength(n=4)
    Convenience: return ``sympy.latex(H)`` for H_{μν}.

latex_effective_action()
    Convenience: return ``sympy.latex(L_eff)`` for the Lagrangian density.

derivation_chain()
    Return an ordered list of (label, latex_string) pairs that reproduce
    the full code→manuscript derivation chain.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import sympy as sp

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
}

# ---------------------------------------------------------------------------
# Internal symbol helpers
# ---------------------------------------------------------------------------

def _make_symbols(n: int = 4) -> Dict[str, sp.Basic]:
    """Create all SymPy symbols needed for the n-dimensional 4D block."""
    syms: Dict[str, sp.Basic] = {}

    # Scalar fields
    syms["phi"] = sp.Symbol(r"\phi", positive=True)
    syms["lam"] = sp.Symbol(r"\lambda", positive=True)

    # Differential coordinate symbols (formal, not functions)
    syms["dx"] = [sp.Symbol(rf"dx^{mu}") for mu in range(n)]
    syms["dy"] = sp.Symbol(r"dy")

    # 4D metric g_{μν} — symmetric matrix of symbols
    g_entries: Dict[Tuple[int, int], sp.Symbol] = {}
    for mu in range(n):
        for nu in range(mu, n):
            sym = sp.Symbol(rf"g_{{{mu}{nu}}}", real=True)
            g_entries[(mu, nu)] = sym
            g_entries[(nu, mu)] = sym
    syms["g_entries"] = g_entries
    syms["g"] = sp.Matrix(n, n, lambda mu, nu: g_entries[(mu, nu)])

    # Gauge field B_μ — column vector of symbols
    B = [sp.Symbol(rf"B_{mu}", real=True) for mu in range(n)]
    syms["B"] = B
    syms["B_vec"] = sp.Matrix(B)

    return syms


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def symbolic_5d_metric(n: int = 4) -> Tuple[sp.Matrix, Dict[str, sp.Basic]]:
    """Return the symbolic 5D KK metric G_{AB} as a SymPy Matrix.

    The matrix is (n+1)×(n+1) and has the block structure::

        ┌──────────────────────────────────┬──────────────┐
        │  g_{μν} + λ²φ² B_μ B_ν         │  λφ B_μ      │
        ├──────────────────────────────────┼──────────────┤
        │  λφ B_ν                          │  φ²          │
        └──────────────────────────────────┴──────────────┘

    Parameters
    ----------
    n : int
        Dimension of the 4D block (default 4).

    Returns
    -------
    G : sp.Matrix, shape (n+1, n+1)
        Symbolic 5D metric.
    syms : dict
        All declared SymPy symbols (phi, lam, g, B, …).
    """
    syms = _make_symbols(n)
    phi: sp.Expr = syms["phi"]
    lam: sp.Expr = syms["lam"]
    g: sp.Matrix = syms["g"]
    B: List[sp.Basic] = syms["B"]

    size = n + 1
    G = sp.zeros(size, size)

    # 4×4 upper-left block: g_{μν} + λ²φ² B_μ B_ν
    for mu in range(n):
        for nu in range(n):
            G[mu, nu] = g[mu, nu] + lam**2 * phi**2 * B[mu] * B[nu]

    # Off-diagonal: G_{μ5} = G_{5μ} = λφ B_μ
    for mu in range(n):
        G[mu, n] = lam * phi * B[mu]
        G[n, mu] = lam * phi * B[mu]

    # G_{55} = φ²
    G[n, n] = phi**2

    return G, syms


def symbolic_line_element(n: int = 4) -> Tuple[sp.Expr, Dict[str, sp.Basic]]:
    """Return the symbolic 5D line element ds².

    ds² = g_{μν} dx^μ dx^ν + φ²(dy + λ B_μ dx^μ)²

    This is the standard Kaluza–Klein line element in the string frame.

    Returns
    -------
    ds2 : sp.Expr
        Symbolic line element.
    syms : dict
        All SymPy symbols used.
    """
    syms = _make_symbols(n)
    phi: sp.Expr = syms["phi"]
    lam: sp.Expr = syms["lam"]
    g: sp.Matrix = syms["g"]
    B: List[sp.Basic] = syms["B"]
    dx: List[sp.Basic] = syms["dx"]
    dy: sp.Basic = syms["dy"]

    # 4D part: g_{μν} dx^μ dx^ν
    ds2_4d = sum(
        g[mu, nu] * dx[mu] * dx[nu]
        for mu in range(n)
        for nu in range(n)
    )

    # Fifth-dimension part: φ²(dy + λ B_μ dx^μ)²
    fifth_form = dy + lam * sum(B[mu] * dx[mu] for mu in range(n))
    ds2_5 = phi**2 * fifth_form**2

    ds2 = ds2_4d + ds2_5
    return ds2, syms


def symbolic_field_strength(n: int = 4) -> Tuple[sp.Matrix, Dict[str, sp.Basic]]:
    """Return the symbolic antisymmetric field-strength tensor H_{μν}.

    H_{μν} = ∂_μ B_ν − ∂_ν B_μ

    Since B_μ are abstract symbols (not functions of coordinates), the
    derivatives are represented as new abstract symbols
    ``partial_mu_B_nu``.

    Returns
    -------
    H : sp.Matrix, shape (n, n)
        Antisymmetric field-strength tensor.
    syms : dict
        All SymPy symbols, extended with partial-derivative symbols.
    """
    syms = _make_symbols(n)

    # ∂_μ B_ν  — abstract symbols for partial derivatives
    dB: Dict[Tuple[int, int], sp.Symbol] = {}
    for mu in range(n):
        for nu in range(n):
            dB[(mu, nu)] = sp.Symbol(rf"\partial_{{{mu}}} B_{{{nu}}}", real=True)

    H = sp.zeros(n, n)
    for mu in range(n):
        for nu in range(n):
            H[mu, nu] = dB[(mu, nu)] - dB[(nu, mu)]

    syms["dB"] = dB
    return H, syms


def symbolic_5d_ricci_scalar_decomposition() -> Tuple[sp.Expr, Dict[str, sp.Basic]]:
    """Return the symbolic KK decomposition of the 5D Ricci scalar.

    R₅ = R₄ − 2∇²φ − 2(∂φ)² + ¼ λ² φ⁻¹ H_{μν} H^{μν}

    This is Eq. (R5-decomp) / Appendix A of the manuscript
    and is implemented numerically in ``src/core/metric.compute_curvature()``.

    All quantities are abstract symbols; the equation encodes the
    correct algebraic structure for use in a LaTeX manuscript.

    Returns
    -------
    R5 : sp.Expr
        Symbolic 5D Ricci scalar.
    syms : dict
        All SymPy symbols.
    """
    phi = sp.Symbol(r"\phi", positive=True)
    lam = sp.Symbol(r"\lambda", positive=True)

    # Abstract curvature and kinetic scalars
    R4 = sp.Symbol(r"R_4", real=True)
    box_phi = sp.Symbol(r"\nabla^2\phi", real=True)
    dphi_sq = sp.Symbol(r"(\partial\phi)^2", nonnegative=True)
    H_sq = sp.Symbol(r"H_{\mu\nu}H^{\mu\nu}", real=True)

    R5 = R4 - 2 * box_phi - 2 * dphi_sq + sp.Rational(1, 4) * lam**2 / phi * H_sq

    syms = {
        "phi": phi, "lam": lam, "R4": R4,
        "box_phi": box_phi, "dphi_sq": dphi_sq, "H_sq": H_sq,
    }
    return R5, syms


def symbolic_effective_action() -> Tuple[sp.Expr, Dict[str, sp.Basic]]:
    """Return the Lagrangian density of the 4D effective action S_eff.

    L_eff = R/(16πG) − ¼ H_{μν} H^{μν} + α ℓ_P² R H_{μν}H^{μν}
            + β (∇φ)² + Γ B_μ J^μ_inf

    This is Eq. (Seff) of the manuscript; the full action is
        S_eff = ∫ d⁴x √(−g) L_eff.

    Returns
    -------
    L_eff : sp.Expr
        Lagrangian density (without √(−g) d⁴x factor).
    syms : dict
        All SymPy symbols.
    """
    G_N   = sp.Symbol(r"G", positive=True)                     # Newton's constant
    R4    = sp.Symbol(r"R", real=True)                          # 4D Ricci scalar
    H_sq  = sp.Symbol(r"H_{\mu\nu}H^{\mu\nu}", real=True)
    alpha = sp.Symbol(r"\alpha", real=True)
    ell_P = sp.Symbol(r"\ell_P", positive=True)
    beta  = sp.Symbol(r"\beta", real=True)
    dphi2 = sp.Symbol(r"(\nabla\phi)^2", real=True)
    Gamma = sp.Symbol(r"\Gamma", real=True)
    BJ    = sp.Symbol(r"B_\mu J^\mu_\mathrm{inf}", real=True)

    L_eff = (
        R4 / (16 * sp.pi * G_N)
        - sp.Rational(1, 4) * H_sq
        + alpha * ell_P**2 * R4 * H_sq
        + beta * dphi2
        + Gamma * BJ
    )

    syms = {
        "G_N": G_N, "R4": R4, "H_sq": H_sq,
        "alpha": alpha, "ell_P": ell_P, "beta": beta,
        "dphi2": dphi2, "Gamma": Gamma, "BJ": BJ,
    }
    return L_eff, syms


# ---------------------------------------------------------------------------
# LaTeX convenience wrappers
# ---------------------------------------------------------------------------

def latex_5d_metric(n: int = 4) -> str:
    """Return ``sympy.latex(G)`` for the 5D KK metric block matrix."""
    G, _ = symbolic_5d_metric(n)
    return sp.latex(G)


def latex_line_element(n: int = 4) -> str:
    """Return ``sympy.latex(ds²)`` for the KK line element."""
    ds2, _ = symbolic_line_element(n)
    return sp.latex(ds2)


def latex_field_strength(n: int = 4) -> str:
    """Return ``sympy.latex(H)`` for H_{μν}."""
    H, _ = symbolic_field_strength(n)
    return sp.latex(H)


def latex_effective_action() -> str:
    """Return ``sympy.latex(L_eff)`` for the 4D Lagrangian density."""
    L_eff, _ = symbolic_effective_action()
    return sp.latex(L_eff)


# ---------------------------------------------------------------------------
# Derivation chain
# ---------------------------------------------------------------------------

def derivation_chain() -> List[Tuple[str, str]]:
    """Return the ordered code→manuscript derivation chain as LaTeX pairs.

    Each entry is ``(label, latex_string)`` suitable for printing or
    embedding in a Jupyter notebook or LaTeX document.  The chain
    follows the narrative structure of ``6-MONOGRAPH/arxiv/main.tex``.

    Returns
    -------
    chain : list of (label, latex) tuples
    """
    G, syms_G = symbolic_5d_metric()
    ds2, syms_ds = symbolic_line_element()
    H, syms_H = symbolic_field_strength()
    R5, syms_R5 = symbolic_5d_ricci_scalar_decomposition()
    L_eff, syms_L = symbolic_effective_action()

    chain = [
        (
            "Step 1 — 5D KK metric G_{AB}",
            r"G_{AB} = " + sp.latex(G),
        ),
        (
            "Step 2 — KK line element ds²",
            r"ds^2 = g_{\mu\nu}\,dx^\mu dx^\nu "
            r"+ \phi^2\!\left(dy + \lambda B_\mu\,dx^\mu\right)^2",
        ),
        (
            "Step 3 — Field strength H_{μν}",
            r"H_{\mu\nu} = \partial_\mu B_\nu - \partial_\nu B_\mu",
        ),
        (
            "Step 4 — 5D → 4D Ricci scalar decomposition",
            r"R_5 = " + sp.latex(R5),
        ),
        (
            "Step 5 — 5D Einstein–Hilbert action",
            r"S_5 = \frac{1}{16\pi G_5}\int d^5x\,\sqrt{-G}\;R_5",
        ),
        (
            "Step 6 — 4D effective action (dimensional reduction)",
            r"S_\mathrm{eff} = \int d^4x\,\sqrt{-g}\;\Bigl["
            + sp.latex(L_eff)
            + r"\Bigr]",
        ),
        (
            "Step 7 — Walker–Pearson field equation (δS/δB_μ = 0)",
            r"\nabla_\nu H^{\mu\nu} = \Gamma J^\mu_\mathrm{inf}"
            r"+ 2\alpha\ell_P^2\,\nabla_\nu\!\left(R\,H^{\mu\nu}\right)",
        ),
        (
            "Step 8 — Modified Einstein equation (δS/δg_{μν} = 0)",
            r"G_{\mu\nu} + \Lambda_\mathrm{eff} g_{\mu\nu}"
            r"= 8\pi G\,T^{(\mathrm{matter})}_{\mu\nu}"
            r"+ 8\pi G\,T_{\mu\nu}(B)",
        ),
    ]
    return chain
