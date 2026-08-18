# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
gym/pillar_registry.py — Canonical Pillar Registry for the AxiomZero Gymnasium

Maps pillar IDs to their backing ``src/core/`` modules, expected ground-truth
outputs, difficulty tiers, and challenge prompts.  Every entry is verifiable:
the ``executor`` callable is the actual module function that produces the
canonical answer.

Difficulty tiers
----------------
easy   — single-module lookup; answer is a direct constant or function return
medium — requires combining two or more constants or calling multiple functions
hard   — requires reasoning from first principles; the module is hidden

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Ensure the repo root is importable wherever the gym is launched from
_REPO_ROOT = Path(__file__).parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

__all__ = ["PillarEntry", "PillarRegistry", "REGISTRY"]


@dataclass
class PillarEntry:
    """One challenge in the Pillar Arcade."""

    pillar_id: int
    name: str
    zone: str                   # "arcade" for all entries here
    difficulty: str             # "easy" | "medium" | "hard"
    domain: str                 # "geometry" | "inflation" | "sm" | "holography" | "multiverse"
    prompt: str                 # Challenge text shown to the agent/human
    hint: str                   # Shown only on easy/medium; hidden on hard
    module_path: str            # Dotted import path, e.g. "src.core.braided_winding"
    executor: Callable[[], Any] # No-arg callable that returns the ground-truth value
    expected_type: str          # "float" | "dict" | "bool" | "tuple"
    ground_truth: Any = field(default=None, init=False)

    def load_ground_truth(self) -> Any:
        """Execute the backing module function and cache the result."""
        if self.ground_truth is None:
            self.ground_truth = self.executor()
        return self.ground_truth


class PillarRegistry:
    """Ordered, searchable registry of pillar challenges."""

    def __init__(self) -> None:
        self._entries: Dict[int, PillarEntry] = {}

    def register(self, entry: PillarEntry) -> None:
        self._entries[entry.pillar_id] = entry

    def get(self, pillar_id: int) -> Optional[PillarEntry]:
        return self._entries.get(pillar_id)

    def all(self) -> List[PillarEntry]:
        return list(self._entries.values())

    def by_difficulty(self, difficulty: str) -> List[PillarEntry]:
        return [e for e in self._entries.values() if e.difficulty == difficulty]

    def by_domain(self, domain: str) -> List[PillarEntry]:
        return [e for e in self._entries.values() if e.domain == domain]

    def ids(self) -> List[int]:
        return sorted(self._entries.keys())

    def __len__(self) -> int:
        return len(self._entries)

    def summary(self) -> Dict[str, Any]:
        counts: Dict[str, int] = {}
        for e in self._entries.values():
            counts[e.difficulty] = counts.get(e.difficulty, 0) + 1
        return {
            "total": len(self._entries),
            "by_difficulty": counts,
            "domains": list({e.domain for e in self._entries.values()}),
        }


# ---------------------------------------------------------------------------
# Helper — lazy module import so registry builds even without numpy installed
# ---------------------------------------------------------------------------

def _lazy(module_path: str, fn_name: str, *args: Any, **kwargs: Any) -> Callable[[], Any]:
    """Return a zero-argument callable that imports *module_path* at call time."""
    def _call() -> Any:
        mod = importlib.import_module(module_path)
        fn = getattr(mod, fn_name)
        return fn(*args, **kwargs)
    return _call


# ---------------------------------------------------------------------------
# Build the canonical registry
# ---------------------------------------------------------------------------

def _build_registry() -> PillarRegistry:
    reg = PillarRegistry()

    # ── Pillar 1 · 5D Metric Assembly ──────────────────────────────────────
    reg.register(PillarEntry(
        pillar_id=1,
        name="5D KK Metric Ansatz",
        zone="arcade",
        difficulty="easy",
        domain="geometry",
        prompt=(
            "The Unitary Manifold uses a 5D Kaluza-Klein metric G_AB assembled "
            "from a 4D metric g_μν, a gauge field B_μ, and a radion scalar φ. "
            "Given a flat 4D Minkowski metric, B_μ = 0, φ = 1, and λ = 1, "
            "what is the (5,5) component G_55 of the assembled 5D metric?"
        ),
        hint="G_55 = φ² in the KK ansatz. See src/core/metric.py.",
        module_path="src.core.metric",
        executor=_lazy(
            "src.core.metric", "assemble_5d_metric",
            # g: Minkowski flat; B=0; phi=1; lam=1
            # returns (N,5,5) array — we compute at a single point
            *[],
            **{},
        ),
        expected_type="float",
    ))
    # Override executor to return a scalar G_55 value
    import numpy as np
    def _pillar1() -> float:
        from src.core.metric import assemble_5d_metric
        g = np.diag([-1.0, 1.0, 1.0, 1.0]).reshape(1, 4, 4)
        B = np.zeros((1, 4))
        phi = np.ones(1)
        G = assemble_5d_metric(g, B, phi, lam=1.0)
        return float(G[0, 4, 4])   # G_55
    reg.get(1).executor = _pillar1

    # ── Pillar 2 · Braided Sound Speed ──────────────────────────────────────
    reg.register(PillarEntry(
        pillar_id=2,
        name="Braided Sound Speed c_s",
        zone="arcade",
        difficulty="easy",
        domain="inflation",
        prompt=(
            "In the Unitary Manifold, the n_w = 5 and n_w = 7 winding modes are "
            "braided around each other in the compact S¹/Z₂ dimension. Under the "
            "sum-of-squares resonance condition k_CS = n₁² + n₂², compute the "
            "canonically-normalised braided sound speed c_s for (n₁, n₂) = (5, 7)."
        ),
        hint="c_s = |n₂² − n₁²| / k_CS = 24/74. See src/core/braided_winding.py.",
        module_path="src.core.braided_winding",
        executor=_lazy("src.core.braided_winding", "braided_sound_speed", 5, 7, 74),
        expected_type="float",
    ))

    # ── Pillar 3 · Resonant k_CS ────────────────────────────────────────────
    reg.register(PillarEntry(
        pillar_id=3,
        name="Sum-of-Squares Resonance k_CS",
        zone="arcade",
        difficulty="easy",
        domain="inflation",
        prompt=(
            "The Chern-Simons level k_CS is selected by the sum-of-squares "
            "resonance condition k_CS = n₁² + n₂². For (n₁, n₂) = (5, 7), "
            "what is the canonical value of k_CS?"
        ),
        hint="k_CS = 5² + 7² = 25 + 49 = 74.",
        module_path="src.core.braided_winding",
        executor=_lazy("src.core.braided_winding", "resonant_kcs", 5, 7),
        expected_type="float",
    ))

    # ── Pillar 4 · CMB Spectral Index & Tensor Ratio ────────────────────────
    reg.register(PillarEntry(
        pillar_id=4,
        name="CMB Observables (n_s, r)",
        zone="arcade",
        difficulty="medium",
        domain="inflation",
        prompt=(
            "Using the braided Kaluza-Klein inflation model with n₁ = 5, n₂ = 7, "
            "compute the predicted CMB scalar spectral index n_s and the "
            "tensor-to-scalar ratio r. "
            "Return both values. The Planck 2018 constraint is n_s = 0.9649 ± 0.0042; "
            "the BICEP/Keck 95% CL bound is r < 0.036."
        ),
        hint="Use braided_ns_r(5, 7) from src.core.braided_winding. "
             "n_s ≈ 0.9635, r ≈ 0.0315.",
        module_path="src.core.braided_winding",
        executor=_lazy("src.core.braided_winding", "braided_ns_r", 5, 7),
        expected_type="dict",
    ))
    # Normalise executor output to a plain dict of key values
    def _pillar4() -> dict:
        from src.core.braided_winding import braided_ns_r
        pred = braided_ns_r(5, 7)
        return {
            "ns": float(pred.ns),
            "r_eff": float(pred.r_eff),
            "c_s": float(pred.c_s),
            "r_satisfies_bicep": bool(pred.r_satisfies_bicep),
        }
    reg.get(4).executor = _pillar4

    # ── Pillar 5 · Fine-Structure Constant α_em ─────────────────────────────
    reg.register(PillarEntry(
        pillar_id=5,
        name="Fine-Structure Constant α_em (Geometric Derivation)",
        zone="arcade",
        difficulty="medium",
        domain="sm",
        prompt=(
            "The Unitary Manifold derives the GUT coupling constant from the "
            "5D Chern-Simons action: α_GUT = N_c / k_CS where N_c = 3 (colour "
            "charge) and k_CS = 74. Running this from the GUT scale to Q = 0 via "
            "the standard SU(5) → SM one-loop RGE yields the fine-structure "
            "constant α_em. What is the predicted inverse fine-structure constant "
            "α_em⁻¹ and the PDG value? What is the residual percentage?"
        ),
        hint="α_GUT = 3/74 ≈ 0.04054. After RGE: α_em⁻¹ ≈ 137.0 (PDG: 137.036). "
             "See src/core/alpha_em_geometric.py.",
        module_path="src.core.alpha_em_geometric",
        executor=_lazy("src.core.alpha_em_geometric", "alpha_em_summary"),
        expected_type="dict",
    ))
    def _pillar5() -> dict:
        from src.core.alpha_em_geometric import alpha_em_summary
        r = alpha_em_summary()
        return {
            "alpha_inv_geo": float(r["result"]["alpha_inv_geo"]),
            "alpha_inv_pdg": float(r["result"]["alpha_inv_pdg"]),
            "residual_pct": float(r["result"]["residual_pct"]),
            "status": r["status"],
        }
    reg.get(5).executor = _pillar5

    # ── Pillar 6 · COBE Normalisation ──────────────────────────────────────
    reg.register(PillarEntry(
        pillar_id=6,
        name="COBE / Planck Amplitude Normalisation",
        zone="arcade",
        difficulty="medium",
        domain="inflation",
        prompt=(
            "The primordial power spectrum amplitude A_s must match the Planck "
            "2018 measurement A_s = 2.101 × 10⁻⁹. Using the Goldberger-Wise "
            "double-well inflaton potential V(φ) = λ(φ² − φ₀²)² with the "
            "effective KK radion φ₀_eff (n_w = 5), what is the required coupling "
            "λ_COBE and the predicted scalar spectral index n_s?"
        ),
        hint="φ₀_eff = π·n_w = 5π ≈ 31.42 (from effective_phi0_kk). "
             "See src/core/inflation.py → cobe_normalization().",
        module_path="src.core.inflation",
        executor=_lazy("src.core.inflation", "cobe_normalization", 1.0, 5),
        expected_type="dict",
    ))
    def _pillar6() -> dict:
        from src.core.inflation import cobe_normalization
        r = cobe_normalization(1.0, 5)
        return {
            "ns": float(r["ns"]),
            "r": float(r["r"]),
            "lam_cobe": float(r["lam_cobe"]),
            "As_predicted": float(r["As_predicted"]),
        }
    reg.get(6).executor = _pillar6

    # ── Pillar 7 · Birefringence Angle β ───────────────────────────────────
    reg.register(PillarEntry(
        pillar_id=7,
        name="CMB Birefringence Angle β",
        zone="arcade",
        difficulty="hard",
        domain="inflation",
        prompt=(
            "The braided-winding mechanism predicts a CMB polarisation rotation "
            "angle β that will be measured by LiteBIRD (~2032). The admissible "
            "window is [0.22°, 0.38°] with a falsification gap at [0.29°, 0.31°]. "
            "Given the AxiomZero aggregated gauge coupling g_agg = 0.3 and "
            "field displacement δφ = 0.1 (Planck units), compute the predicted β "
            "in degrees. State whether this falls inside the admissible window."
        ),
        hint="Use birefringence_angle(g_agg, delta_phi) from src/core/braided_winding.py. "
             "β ≈ 0.273° – 0.331° (canonical range).",
        module_path="src.core.braided_winding",
        executor=_lazy("src.core.braided_winding", "birefringence_angle", 0.3, 0.1),
        expected_type="float",
    ))
    def _pillar7() -> dict:
        from src.core.braided_winding import birefringence_angle
        beta = birefringence_angle(0.3, 0.1)
        return {
            "beta_deg": float(beta),
            "in_admissible_window": bool(0.22 <= float(beta) <= 0.38),
            "in_falsification_gap": bool(0.29 <= float(beta) <= 0.31),
        }
    reg.get(7).executor = _pillar7

    # ── Pillar 8 · Holographic Entropy-Area Law ─────────────────────────────
    reg.register(PillarEntry(
        pillar_id=8,
        name="Holographic Entropy-Area Law (Pillar 4)",
        zone="arcade",
        difficulty="medium",
        domain="holography",
        prompt=(
            "The Bekenstein-Hawking entropy-area law S = A / (4G) is an exact "
            "geometric consequence of the 5D metric reduction in the UM. "
            "For a 2D holographic screen with induced metric determinant √h = 1.0 "
            "and area A = 1.0 (Planck units, G_N = 1), what is the holographic "
            "entropy S?"
        ),
        hint="S = A / 4 in Planck units with G_N = 1. S = 0.25.",
        module_path="src.holography.boundary",
        executor=_lazy("src.holography.boundary", "entropy_area", 1.0),
        expected_type="float",
    ))
    def _pillar8() -> float:
        # entropy_area(h) where h is the induced-metric determinant value
        from src.holography.boundary import entropy_area
        return float(entropy_area(1.0))
    reg.get(8).executor = _pillar8

    # ── Pillar 9 · FTUM Fixed-Point Convergence ─────────────────────────────
    reg.register(PillarEntry(
        pillar_id=9,
        name="FTUM Fixed-Point α Derivation (Pillar 5/29/38)",
        zone="arcade",
        difficulty="hard",
        domain="multiverse",
        prompt=(
            "The Fractal Time Unitary Manifold (FTUM) operator is a contraction "
            "on the space of Multiverse states. Starting from a stabilised radion "
            "φ_0 = 1.0, derive the nonminimal coupling α using the KK fixed-point "
            "iteration. What is the value of α? "
            "Bonus: state the geometric interpretation of α in the 5D theory."
        ),
        hint="Use derive_alpha_from_fixed_point(phi_stabilized=1.0) from "
             "src.multiverse.fixed_point. α ≈ 1/φ₀² (KK coupling).",
        module_path="src.multiverse.fixed_point",
        executor=_lazy("src.multiverse.fixed_point", "derive_alpha_from_fixed_point", 1.0),
        expected_type="tuple",
    ))
    def _pillar9() -> dict:
        from src.multiverse.fixed_point import derive_alpha_from_fixed_point
        alpha, _network, converged = derive_alpha_from_fixed_point(1.0)
        return {"alpha": float(alpha), "converged": bool(converged)}
    reg.get(9).executor = _pillar9

    # ── Pillar 10 · φ₀ Closure Self-Consistency ────────────────────────────
    reg.register(PillarEntry(
        pillar_id=10,
        name="φ₀ Radion Self-Consistency Closure (Pillar 56)",
        zone="arcade",
        difficulty="medium",
        domain="geometry",
        prompt=(
            "The bare FTUM fixed point gives φ₀_bare = 1, but the KK compactification "
            "requires an effective φ₀_eff that is self-consistent with the CMB "
            "spectral index n_s ≈ 0.9635. The closure condition is: "
            "n_s(φ₀_eff) = n_s_target. What is the effective φ₀_eff for n_w = 5? "
            "Does iterating from φ₀_bare = 1 converge?"
        ),
        hint="φ₀_eff = π · n_w = 5π ≈ 31.42. See src/core/phi0_closure.py → "
             "ftum_phi0_iteration() or src/core/inflation.py → effective_phi0_kk().",
        module_path="src.core.phi0_closure",
        executor=_lazy("src.core.phi0_closure", "ftum_phi0_iteration"),
        expected_type="dict",
    ))
    def _pillar10() -> dict:
        from src.core.phi0_closure import ftum_phi0_iteration
        r = ftum_phi0_iteration()
        # normalise to a consistent schema
        if isinstance(r, dict):
            return r
        return {"phi0_eff": float(r)}
    reg.get(10).executor = _pillar10

    # ── Pillar 11 · Acoustic Peak Positions ────────────────────────────────
    reg.register(PillarEntry(
        pillar_id=11,
        name="CMB Acoustic Peak Positions",
        zone="arcade",
        difficulty="medium",
        domain="cmb",
        prompt=(
            "The CMB power spectrum has acoustic peaks at multipole ℓ_n. Using "
            "the UM transfer function with braided sound speed c_s = 12/37, "
            "what are the positions (in ℓ) of the first three acoustic peaks? "
            "Compare to the Planck 2018 values: ℓ₁ ≈ 220, ℓ₂ ≈ 540, ℓ₃ ≈ 810."
        ),
        hint="Use acoustic_peak_positions() from src/core/cmb_transfer.py.",
        module_path="src.core.cmb_transfer",
        executor=_lazy("src.core.cmb_transfer", "acoustic_peak_positions"),
        expected_type="dict",
    ))
    def _pillar11() -> dict:
        from src.core.cmb_transfer import acoustic_peak_positions
        r = acoustic_peak_positions()
        return r if isinstance(r, dict) else {"peaks": list(r)}
    reg.get(11).executor = _pillar11

    return reg


# Module-level singleton — import this anywhere
REGISTRY: PillarRegistry = _build_registry()
