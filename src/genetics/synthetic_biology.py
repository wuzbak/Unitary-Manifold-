# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/genetics/synthetic_biology.py
===================================
Synthetic Biology as Attractor Engineering — Pillar 25 Extension.

Theory
------
Natural biology *discovers* FTUM fixed points through evolution; synthetic
biology *designs* them.  In UM language every synthetic gene circuit is a
deliberate sculpting of the φ-field landscape inside a living cell:

    CRISPR edit   → targeted B_μ perturbation that moves the φ fixed-point
    Gene circuit  → designed FTUM attractor (toggle switch, oscillator, logic gate)
    Metabolic eng.→ rewired B_μ gauge network (new catalytic pathway topology)
    AI-driven SynBio → gradient descent on the effective φ-potential surface

The key insight from Groff-Vindman (2026) is that the convergence of AI and
synthetic biology represents a φ-field criticality: AI learns the effective
φ-potential landscape while SynBio engineers new attractors within it.  The
"looming deluge" is a phase transition in the density of navigable design space.

Connection to National Security / HILS
---------------------------------------
Dual-use risk in synthetic biology is a HILS governance problem (Pillar 19 /
Unitary Pentad).  AI-accelerated bio-design compresses the time constant of
the B_μ perturbation cycle: both healing and harm can be designed at speed.
The biosafety kill-switch (containment_phi) is the FTUM attractor-stability
radius in biology — the engineering analogue of the vacuum stability bound in
Pillar 96.

Epistemic status: TIER 3 — Mathematical framework applied to SynBio domain.
Tests confirm code correctness ONLY.  See src/genetics/README.md.
"""



from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",  # The braid triad; unique to this framework
}
import math
import numpy as np

_EPS = 1e-30


# ---------------------------------------------------------------------------
# 1. Gene circuit — bistable toggle switch as designed FTUM attractor
# ---------------------------------------------------------------------------

def gene_circuit_phi_attractor(phi_activator: float, phi_repressor: float,
                                hill_n: float = 2.0,
                                K: float = 1.0) -> float:
    """Steady-state φ of a bistable toggle-switch gene circuit.

    Models the Gardner–Collins–Cantor (2000) toggle switch as a FTUM
    fixed-point.  Each promoter represses the other; the Hill function
    captures cooperative repression.

        phi_ss = phi_activator / (1 + (phi_repressor / K)^n)

    In UM language: the bistable switch is a designed φ attractor with
    two stable fixed points separated by a B_μ-noise threshold.

    Parameters
    ----------
    phi_activator : float — activator input φ (must be ≥ 0)
    phi_repressor : float — repressor concentration φ (must be ≥ 0)
    hill_n        : float — Hill cooperativity exponent (must be > 0)
    K             : float — repression threshold φ (must be > 0)

    Returns
    -------
    phi_ss : float — steady-state expression φ of the driven gene
    """
    if phi_activator < 0.0:
        raise ValueError(f"phi_activator must be ≥ 0, got {phi_activator!r}")
    if phi_repressor < 0.0:
        raise ValueError(f"phi_repressor must be ≥ 0, got {phi_repressor!r}")
    if hill_n <= 0.0:
        raise ValueError(f"hill_n must be > 0, got {hill_n!r}")
    if K <= 0.0:
        raise ValueError(f"K must be > 0, got {K!r}")
    return float(phi_activator / (1.0 + (phi_repressor / K) ** hill_n))


# ---------------------------------------------------------------------------
# 2. CRISPR edit — targeted B_μ perturbation
# ---------------------------------------------------------------------------

def crispr_phi_edit_precision(guide_phi: float, off_target_fraction: float,
                               repair_template_phi: float = 0.0) -> float:
    """Net on-target φ edit after CRISPR-Cas9 cuts and repair.

    In UM: the guide RNA is a B_μ perturbation targeted to a specific
    position in the φ-archive (genome).  Off-target cuts are stochastic
    B_μ noise.  HDR template shifts the FTUM attractor; NHEJ leaves a
    perturbation scar.

        phi_edit = guide_phi × (1 − off_target_fraction) + repair_template_phi

    Parameters
    ----------
    guide_phi            : float — guide RNA targeting φ efficiency ∈ [0, 1]
    off_target_fraction  : float — fraction of cuts at off-target sites ∈ [0, 1]
    repair_template_phi  : float — HDR template fidelity φ (≥ 0; 0 = NHEJ)

    Returns
    -------
    phi_edit : float — effective on-target edit φ
    """
    if not (0.0 <= guide_phi <= 1.0):
        raise ValueError(f"guide_phi must be in [0,1], got {guide_phi!r}")
    if not (0.0 <= off_target_fraction <= 1.0):
        raise ValueError(f"off_target_fraction must be in [0,1], got {off_target_fraction!r}")
    if repair_template_phi < 0.0:
        raise ValueError(f"repair_template_phi must be ≥ 0, got {repair_template_phi!r}")
    return float(guide_phi * (1.0 - off_target_fraction) + repair_template_phi)


# ---------------------------------------------------------------------------
# 3. Metabolic pathway engineering — B_μ gauge network rewiring
# ---------------------------------------------------------------------------

def metabolic_pathway_phi_flux(n_enzymes: int, phi_per_enzyme: float,
                                bottleneck_fraction: float = 0.0) -> float:
    """Net metabolic flux φ through an engineered pathway.

    In UM: each enzymatic step is a B_μ gauge transformation.  The
    engineered pathway is a deliberately connected sequence of such
    transformations.  The bottleneck enzyme limits the total flux.

        phi_flux = n_enzymes × phi_per_enzyme × (1 − bottleneck_fraction)

    Parameters
    ----------
    n_enzymes           : int   — number of pathway enzymes (must be ≥ 1)
    phi_per_enzyme      : float — φ flux capacity per enzyme (must be ≥ 0)
    bottleneck_fraction : float — fraction of flux lost at the rate-limiting
                                  step ∈ [0, 1] (default 0)

    Returns
    -------
    phi_flux : float — net engineered pathway flux φ
    """
    if n_enzymes < 1:
        raise ValueError(f"n_enzymes must be ≥ 1, got {n_enzymes!r}")
    if phi_per_enzyme < 0.0:
        raise ValueError(f"phi_per_enzyme must be ≥ 0, got {phi_per_enzyme!r}")
    if not (0.0 <= bottleneck_fraction <= 1.0):
        raise ValueError(f"bottleneck_fraction must be in [0,1], got {bottleneck_fraction!r}")
    return float(n_enzymes * phi_per_enzyme * (1.0 - bottleneck_fraction))


# ---------------------------------------------------------------------------
# 4. AI × SynBio — convergence rate on the φ-potential landscape
# ---------------------------------------------------------------------------

def ai_synbio_phi_convergence(phi_design_space: float, ai_accuracy: float,
                               n_design_cycles: int) -> float:
    """φ convergence of AI-guided synthetic biology after n design-build-test cycles.

    In UM: AI learns the effective φ-potential surface; each design cycle is
    a gradient step.  The convergence rate is ai_accuracy per step.

        phi_converged = phi_design_space × (1 − (1 − ai_accuracy)^n)

    This saturates at phi_design_space (full landscape coverage) as n → ∞.

    Parameters
    ----------
    phi_design_space : float — total navigable φ design space (must be ≥ 0)
    ai_accuracy      : float — fraction of design space sampled per cycle ∈ (0, 1]
    n_design_cycles  : int   — number of DBTL cycles (must be ≥ 0)

    Returns
    -------
    phi_converged : float — fraction of design space explored
    """
    if phi_design_space < 0.0:
        raise ValueError(f"phi_design_space must be ≥ 0, got {phi_design_space!r}")
    if not (0.0 < ai_accuracy <= 1.0):
        raise ValueError(f"ai_accuracy must be in (0,1], got {ai_accuracy!r}")
    if n_design_cycles < 0:
        raise ValueError(f"n_design_cycles must be ≥ 0, got {n_design_cycles!r}")
    return float(phi_design_space * (1.0 - (1.0 - ai_accuracy) ** n_design_cycles))


# ---------------------------------------------------------------------------
# 5. Chassis minimality — minimal genome as minimal φ-attractor
# ---------------------------------------------------------------------------

def chassis_phi_minimality(n_essential_genes: int, n_total_genes: int,
                            phi_per_gene: float = 1.0) -> float:
    """φ-minimality of a chassis organism (minimal cell concept).

    In UM: a chassis is the smallest stable FTUM attractor that can support
    a programmed φ payload.  The minimality index measures how close the
    organism is to the Venter-JCVI minimum genome.

        phi_min = phi_per_gene × n_essential_genes / n_total_genes

    Parameters
    ----------
    n_essential_genes : int   — minimal essential gene count (must be ≥ 1)
    n_total_genes     : int   — actual genome gene count (must be ≥ n_essential_genes)
    phi_per_gene      : float — φ per gene (must be > 0)

    Returns
    -------
    phi_min : float ∈ (0, 1] — minimality ratio (1 = perfectly minimal)
    """
    if n_essential_genes < 1:
        raise ValueError(f"n_essential_genes must be ≥ 1, got {n_essential_genes!r}")
    if n_total_genes < n_essential_genes:
        raise ValueError(
            f"n_total_genes ({n_total_genes}) must be ≥ n_essential_genes ({n_essential_genes})"
        )
    if phi_per_gene <= 0.0:
        raise ValueError(f"phi_per_gene must be > 0, got {phi_per_gene!r}")
    return float(phi_per_gene * n_essential_genes / n_total_genes)


# ---------------------------------------------------------------------------
# 6. Biosafety containment — kill-switch as FTUM attractor stability radius
# ---------------------------------------------------------------------------

def biosafety_containment_phi(phi_escape_rate: float,
                               kill_switch_strength: float,
                               auxotrophy_layers: int = 1) -> float:
    """Residual φ-escape probability after multi-layer biocontainment.

    In UM: the kill-switch is the biological analogue of the vacuum stability
    bound (Pillar 96).  Each containment layer is an independent attractor
    barrier.  The residual escape rate follows multiplicative containment.

        phi_escape = phi_escape_rate × (1 − kill_switch_strength)^auxotrophy_layers

    Parameters
    ----------
    phi_escape_rate     : float — baseline escape probability φ ∈ [0, 1]
    kill_switch_strength: float — single-layer containment efficiency ∈ [0, 1]
    auxotrophy_layers   : int   — number of independent containment layers (≥ 1)

    Returns
    -------
    phi_escape : float ∈ [0, 1] — residual escape φ after all layers
    """
    if not (0.0 <= phi_escape_rate <= 1.0):
        raise ValueError(f"phi_escape_rate must be in [0,1], got {phi_escape_rate!r}")
    if not (0.0 <= kill_switch_strength <= 1.0):
        raise ValueError(f"kill_switch_strength must be in [0,1], got {kill_switch_strength!r}")
    if auxotrophy_layers < 1:
        raise ValueError(f"auxotrophy_layers must be ≥ 1, got {auxotrophy_layers!r}")
    return float(phi_escape_rate * (1.0 - kill_switch_strength) ** auxotrophy_layers)


# ---------------------------------------------------------------------------
# 7. DNA data storage — genome as digital φ-archive
# ---------------------------------------------------------------------------

def dna_data_storage_phi_density(n_bits: float, error_correction_overhead: float,
                                  synthesis_fidelity: float = 0.999) -> float:
    """Net information φ stored per unit synthesis cost in a DNA archive.

    In UM: DNA is the highest-fidelity φ-storage device.  Synthetic DNA
    data storage deliberately exploits this.  Error-correcting codes add
    overhead; synthesis errors reduce fidelity.

        phi_density = n_bits × synthesis_fidelity / (1 + error_correction_overhead)

    Parameters
    ----------
    n_bits                    : float — raw bits to encode (must be ≥ 0)
    error_correction_overhead : float — fractional overhead from ECC ∈ [0, ∞)
    synthesis_fidelity        : float — per-base synthesis accuracy ∈ (0, 1]

    Returns
    -------
    phi_density : float — net effective bits stored
    """
    if n_bits < 0.0:
        raise ValueError(f"n_bits must be ≥ 0, got {n_bits!r}")
    if error_correction_overhead < 0.0:
        raise ValueError(f"error_correction_overhead must be ≥ 0, got {error_correction_overhead!r}")
    if not (0.0 < synthesis_fidelity <= 1.0):
        raise ValueError(f"synthesis_fidelity must be in (0,1], got {synthesis_fidelity!r}")
    return float(n_bits * synthesis_fidelity / (1.0 + error_correction_overhead))


# ---------------------------------------------------------------------------
# 8. Directed evolution — gradient ascent on φ-fitness landscape
# ---------------------------------------------------------------------------

def directed_evolution_phi_gradient(phi_initial: float, selection_pressure: float,
                                     n_rounds: int,
                                     mutation_rate: float = 0.01) -> float:
    """Improved protein φ-fitness after n rounds of directed evolution.

    In UM: directed evolution is iterative gradient ascent on the φ-fitness
    landscape.  Each round of mutation + selection moves the population
    toward a higher φ attractor.

        phi_evolved = phi_initial × exp(selection_pressure × mutation_rate × n_rounds)

    Parameters
    ----------
    phi_initial        : float — initial protein φ-fitness (must be ≥ 0)
    selection_pressure : float — differential selection coefficient ≥ 0
    n_rounds           : int   — rounds of mutation + selection (must be ≥ 0)
    mutation_rate      : float — mutations per residue per round ∈ (0, 1]

    Returns
    -------
    phi_evolved : float — evolved protein φ-fitness
    """
    if phi_initial < 0.0:
        raise ValueError(f"phi_initial must be ≥ 0, got {phi_initial!r}")
    if selection_pressure < 0.0:
        raise ValueError(f"selection_pressure must be ≥ 0, got {selection_pressure!r}")
    if n_rounds < 0:
        raise ValueError(f"n_rounds must be ≥ 0, got {n_rounds!r}")
    if not (0.0 < mutation_rate <= 1.0):
        raise ValueError(f"mutation_rate must be in (0,1], got {mutation_rate!r}")
    return float(phi_initial * math.exp(selection_pressure * mutation_rate * n_rounds))


# ---------------------------------------------------------------------------
# 9. Synthetic gene circuit noise — B_μ stochastic resilience
# ---------------------------------------------------------------------------

def synthetic_gene_circuit_noise(phi_signal: float, B_intrinsic: float,
                                  n_redundant_copies: int = 1) -> float:
    """Signal-to-noise ratio of a synthetic gene circuit.

    In UM: B_μ is the stochastic noise field.  Redundant gene copies (gene
    dosage) average out B_μ fluctuations, increasing the SNR as √n.

        SNR = phi_signal × sqrt(n_redundant_copies) / (B_intrinsic + ε)

    Parameters
    ----------
    phi_signal          : float — designed signal φ (must be ≥ 0)
    B_intrinsic         : float — intrinsic B_μ noise floor (must be ≥ 0)
    n_redundant_copies  : int   — gene copy number for noise averaging (must be ≥ 1)

    Returns
    -------
    SNR : float — signal-to-noise ratio
    """
    if phi_signal < 0.0:
        raise ValueError(f"phi_signal must be ≥ 0, got {phi_signal!r}")
    if B_intrinsic < 0.0:
        raise ValueError(f"B_intrinsic must be ≥ 0, got {B_intrinsic!r}")
    if n_redundant_copies < 1:
        raise ValueError(f"n_redundant_copies must be ≥ 1, got {n_redundant_copies!r}")
    return float(phi_signal * math.sqrt(n_redundant_copies) / (B_intrinsic + _EPS))


# ---------------------------------------------------------------------------
# 10. Bioeconomy output — biomanufacturing productivity as φ flux
# ---------------------------------------------------------------------------

def bioeconomy_phi_output(phi_titer: float, phi_rate: float,
                           phi_yield: float,
                           scale_factor: float = 1.0) -> float:
    """Bioeconomy productivity φ (titer × rate × yield × scale).

    In UM: industrial biomanufacturing is the B_μ gauge network operating
    at scale.  The three engineering metrics (titer, rate, yield — the TRY
    framework) are the three independent B_μ flux components.  Their product
    gives the total φ output of the bioprocess.

        phi_out = phi_titer × phi_rate × phi_yield × scale_factor

    Parameters
    ----------
    phi_titer    : float — product titer φ (g/L; must be ≥ 0)
    phi_rate     : float — volumetric productivity φ (g/L/h; must be ≥ 0)
    phi_yield    : float — substrate-to-product yield φ ∈ [0, 1]
    scale_factor : float — scale-up multiplier (must be > 0)

    Returns
    -------
    phi_out : float — total bioeconomy output φ
    """
    if phi_titer < 0.0:
        raise ValueError(f"phi_titer must be ≥ 0, got {phi_titer!r}")
    if phi_rate < 0.0:
        raise ValueError(f"phi_rate must be ≥ 0, got {phi_rate!r}")
    if not (0.0 <= phi_yield <= 1.0):
        raise ValueError(f"phi_yield must be in [0,1], got {phi_yield!r}")
    if scale_factor <= 0.0:
        raise ValueError(f"scale_factor must be > 0, got {scale_factor!r}")
    return float(phi_titer * phi_rate * phi_yield * scale_factor)
