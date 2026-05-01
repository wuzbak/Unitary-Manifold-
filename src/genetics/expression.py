# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/genetics/expression.py
===========================
Gene Expression as φ-Field Transcription Dynamics — Pillar 25.
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


def transcription_phi_rate(phi_tf: float, promoter_strength: float,
                             B_noise: float) -> float:
    """mRNA production rate driven by transcription factor φ.

    rate = phi_tf × promoter_strength / (B_noise + ε)

    Parameters
    ----------
    phi_tf           : float — transcription factor φ concentration (must be ≥ 0)
    promoter_strength: float — promoter efficiency (must be > 0)
    B_noise          : float — transcriptional noise floor (must be ≥ 0)

    Returns
    -------
    rate : float — mRNA production rate
    """
    if phi_tf < 0.0:
        raise ValueError(f"phi_tf must be ≥ 0, got {phi_tf!r}")
    if promoter_strength <= 0.0:
        raise ValueError(f"promoter_strength must be > 0, got {promoter_strength!r}")
    if B_noise < 0.0:
        raise ValueError(f"B_noise must be ≥ 0, got {B_noise!r}")
    return float(phi_tf * promoter_strength / (B_noise + _EPS))


def translation_phi_efficiency(phi_mrna: float, ribosome_density: float,
                                codon_bias: float = 1.0) -> float:
    """Protein production efficiency from mRNA φ.

    phi_protein = phi_mrna × ribosome_density × codon_bias

    Parameters
    ----------
    phi_mrna        : float — mRNA φ abundance (must be ≥ 0)
    ribosome_density: float — ribosome occupancy on mRNA (must be ≥ 0)
    codon_bias      : float — codon optimality factor ∈ (0, 1] (default 1.0)

    Returns
    -------
    phi_protein : float
    """
    if phi_mrna < 0.0:
        raise ValueError(f"phi_mrna must be ≥ 0, got {phi_mrna!r}")
    if ribosome_density < 0.0:
        raise ValueError(f"ribosome_density must be ≥ 0, got {ribosome_density!r}")
    if not (0.0 < codon_bias <= 1.0):
        raise ValueError(f"codon_bias must be in (0,1], got {codon_bias!r}")
    return float(phi_mrna * ribosome_density * codon_bias)


def protein_phi_folding(phi_unfolded: float, chaperone_phi: float,
                         misfolding_rate: float = 0.05) -> float:
    """Correctly folded protein φ after chaperone-assisted folding.

    phi_folded = (phi_unfolded + chaperone_phi) × (1 − misfolding_rate)

    Parameters
    ----------
    phi_unfolded    : float — unfolded protein φ (must be ≥ 0)
    chaperone_phi   : float — chaperone-assisted folding φ contribution (must be ≥ 0)
    misfolding_rate : float — fraction that misfolds ∈ [0, 1] (default 0.05)

    Returns
    -------
    phi_folded : float
    """
    if phi_unfolded < 0.0:
        raise ValueError(f"phi_unfolded must be ≥ 0, got {phi_unfolded!r}")
    if chaperone_phi < 0.0:
        raise ValueError(f"chaperone_phi must be ≥ 0, got {chaperone_phi!r}")
    if not (0.0 <= misfolding_rate <= 1.0):
        raise ValueError(f"misfolding_rate must be in [0,1], got {misfolding_rate!r}")
    return float((phi_unfolded + chaperone_phi) * (1.0 - misfolding_rate))


def gene_regulatory_phi(n_activators: int, phi_activator: float,
                         n_repressors: int, phi_repressor: float) -> float:
    """Net regulatory φ acting on a gene.

    phi_reg = n_activators × phi_activator − n_repressors × phi_repressor

    Parameters
    ----------
    n_activators  : int   — number of activating TFs (must be ≥ 0)
    phi_activator : float — φ per activator (must be ≥ 0)
    n_repressors  : int   — number of repressing TFs (must be ≥ 0)
    phi_repressor : float — φ per repressor (must be ≥ 0)

    Returns
    -------
    phi_reg : float
    """
    if n_activators < 0:
        raise ValueError(f"n_activators must be ≥ 0, got {n_activators!r}")
    if phi_activator < 0.0:
        raise ValueError(f"phi_activator must be ≥ 0, got {phi_activator!r}")
    if n_repressors < 0:
        raise ValueError(f"n_repressors must be ≥ 0, got {n_repressors!r}")
    if phi_repressor < 0.0:
        raise ValueError(f"phi_repressor must be ≥ 0, got {phi_repressor!r}")
    return float(n_activators * phi_activator - n_repressors * phi_repressor)


def rna_stability_phi(phi_mrna: float, t: float, decay_rate: float = 0.1) -> float:
    """mRNA φ remaining after time t (first-order decay).

    phi_t = phi_mrna × exp(−decay_rate × t)

    Parameters
    ----------
    phi_mrna    : float — initial mRNA φ (must be ≥ 0)
    t           : float — elapsed time in hours (must be ≥ 0)
    decay_rate  : float — mRNA degradation rate hr⁻¹ (default 0.1, must be ≥ 0)

    Returns
    -------
    phi_t : float
    """
    if phi_mrna < 0.0:
        raise ValueError(f"phi_mrna must be ≥ 0, got {phi_mrna!r}")
    if t < 0.0:
        raise ValueError(f"t must be ≥ 0, got {t!r}")
    if decay_rate < 0.0:
        raise ValueError(f"decay_rate must be ≥ 0, got {decay_rate!r}")
    return float(phi_mrna * math.exp(-decay_rate * t))


def splicing_phi_fidelity(n_correct: int, n_total: int) -> float:
    """Splicing accuracy as fraction of correctly spliced transcripts.

    fidelity = n_correct / n_total

    Parameters
    ----------
    n_correct : int — correctly spliced transcripts (must be ≥ 0)
    n_total   : int — total transcripts (must be > 0)

    Returns
    -------
    fidelity : float ∈ [0, 1]
    """
    if n_correct < 0:
        raise ValueError(f"n_correct must be ≥ 0, got {n_correct!r}")
    if n_total <= 0:
        raise ValueError(f"n_total must be > 0, got {n_total!r}")
    return float(np.clip(n_correct / n_total, 0.0, 1.0))


def protein_phi_interaction(phi_A: float, phi_B: float,
                             K_d: float) -> float:
    """Protein-protein interaction φ at equilibrium.

    phi_complex = phi_A × phi_B / (K_d + phi_B + _EPS)

    Parameters
    ----------
    phi_A : float — protein A concentration φ (must be ≥ 0)
    phi_B : float — protein B concentration φ (must be ≥ 0)
    K_d   : float — dissociation constant (must be > 0)

    Returns
    -------
    phi_complex : float
    """
    if phi_A < 0.0:
        raise ValueError(f"phi_A must be ≥ 0, got {phi_A!r}")
    if phi_B < 0.0:
        raise ValueError(f"phi_B must be ≥ 0, got {phi_B!r}")
    if K_d <= 0.0:
        raise ValueError(f"K_d must be > 0, got {K_d!r}")
    return float(phi_A * phi_B / (K_d + phi_B + _EPS))


def expression_phi_noise(phi_mean: float, B_intrinsic: float,
                          n_molecules: int) -> float:
    """Coefficient of variation of gene expression.

    CV = sqrt(B_intrinsic² + phi_mean / n_molecules) / phi_mean

    Parameters
    ----------
    phi_mean    : float — mean expression φ (must be > 0)
    B_intrinsic : float — intrinsic noise floor (must be ≥ 0)
    n_molecules : int   — mean molecule count (must be ≥ 1)

    Returns
    -------
    CV : float ≥ 0
    """
    if phi_mean <= 0.0:
        raise ValueError(f"phi_mean must be > 0, got {phi_mean!r}")
    if B_intrinsic < 0.0:
        raise ValueError(f"B_intrinsic must be ≥ 0, got {B_intrinsic!r}")
    if n_molecules < 1:
        raise ValueError(f"n_molecules must be ≥ 1, got {n_molecules!r}")
    variance = B_intrinsic ** 2 + phi_mean / n_molecules
    return float(math.sqrt(variance) / phi_mean)


def chromatin_phi_state(phi_open: float, phi_closed: float,
                         remodeling_phi: float) -> float:
    """Chromatin accessibility φ after remodelling.

    phi_access = (phi_open + remodeling_phi) / (phi_open + phi_closed + _EPS)

    Parameters
    ----------
    phi_open       : float — open chromatin φ (must be ≥ 0)
    phi_closed     : float — closed chromatin φ (must be ≥ 0)
    remodeling_phi : float — ATP-dependent remodelling φ (must be ≥ 0)

    Returns
    -------
    phi_access : float ∈ [0, 1]
    """
    if phi_open < 0.0:
        raise ValueError(f"phi_open must be ≥ 0, got {phi_open!r}")
    if phi_closed < 0.0:
        raise ValueError(f"phi_closed must be ≥ 0, got {phi_closed!r}")
    if remodeling_phi < 0.0:
        raise ValueError(f"remodeling_phi must be ≥ 0, got {remodeling_phi!r}")
    total = phi_open + phi_closed + _EPS
    return float(np.clip((phi_open + remodeling_phi) / total, 0.0, 1.0))


def gene_phi_dosage(n_copies: int, phi_per_copy: float) -> float:
    """Total gene dosage φ from n copies.

    phi_dosage = n_copies × phi_per_copy

    Parameters
    ----------
    n_copies      : int   — gene copy number (must be ≥ 0)
    phi_per_copy  : float — expression φ per copy (must be ≥ 0)

    Returns
    -------
    phi_dosage : float
    """
    if n_copies < 0:
        raise ValueError(f"n_copies must be ≥ 0, got {n_copies!r}")
    if phi_per_copy < 0.0:
        raise ValueError(f"phi_per_copy must be ≥ 0, got {phi_per_copy!r}")
    return float(n_copies * phi_per_copy)
