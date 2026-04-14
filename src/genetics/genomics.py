# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/genetics/genomics.py
=========================
Genome as φ-Field Information Archive — Pillar 25: Genetics.

Theory
------
The genome is the highest-fidelity φ-storage device in biology.
DNA encodes φ in a 4-symbol alphabet; the information content per base
pair is 2 bits = log₂(4).  Mutation events are B_μ-noise insertions
that perturb the φ sequence.  The DNA repair machinery is the biological
analogue of the FTUM irreversibility operator — it restores the φ
fixed-point after B_μ perturbation.
"""

from __future__ import annotations
import math
import numpy as np

_EPS = 1e-30


def mutation_rate_phi(n_mutations: int, n_bases: int,
                       n_generations: int) -> float:
    """Per-base per-generation mutation rate.

    μ = n_mutations / (n_bases × n_generations)

    Parameters
    ----------
    n_mutations  : int — observed mutations (must be ≥ 0)
    n_bases      : int — genome length in base pairs (must be > 0)
    n_generations: int — number of generations (must be > 0)

    Returns
    -------
    mu : float — mutation rate per base per generation
    """
    if n_mutations < 0:
        raise ValueError(f"n_mutations must be ≥ 0, got {n_mutations!r}")
    if n_bases <= 0:
        raise ValueError(f"n_bases must be > 0, got {n_bases!r}")
    if n_generations <= 0:
        raise ValueError(f"n_generations must be > 0, got {n_generations!r}")
    return float(n_mutations / (n_bases * n_generations))


def genetic_phi_diversity(allele_frequencies: np.ndarray) -> float:
    """Expected heterozygosity as a measure of genetic φ diversity.

    H_e = 1 − Σ p_i²

    Parameters
    ----------
    allele_frequencies : ndarray — allele frequencies (must sum ≈ 1, each ≥ 0)

    Returns
    -------
    H_e : float ∈ [0, 1)
    """
    p = np.asarray(allele_frequencies, dtype=float)
    if np.any(p < 0.0):
        raise ValueError("allele_frequencies must be ≥ 0")
    p = p / (p.sum() + _EPS)
    return float(np.clip(1.0 - np.sum(p ** 2), 0.0, 1.0))


def allele_phi_frequency(n_allele: int, n_total: int) -> float:
    """Allele frequency in a diploid population.

    p = n_allele / n_total

    Parameters
    ----------
    n_allele : int — count of allele copies (must be ≥ 0)
    n_total  : int — total allele count (must be > 0)

    Returns
    -------
    p : float ∈ [0, 1]
    """
    if n_allele < 0:
        raise ValueError(f"n_allele must be ≥ 0, got {n_allele!r}")
    if n_total <= 0:
        raise ValueError(f"n_total must be > 0, got {n_total!r}")
    return float(np.clip(n_allele / n_total, 0.0, 1.0))


def genome_phi_complexity(n_genes: int, mean_intron_fraction: float = 0.25) -> float:
    """Effective coding φ-information in a genome.

    phi_complex = n_genes × (1 − mean_intron_fraction) × 2 bits per bp

    Parameters
    ----------
    n_genes              : int   — number of protein-coding genes (must be ≥ 0)
    mean_intron_fraction : float — fraction of gene that is intronic ∈ [0, 1]

    Returns
    -------
    phi_complex : float — effective coding information units
    """
    if n_genes < 0:
        raise ValueError(f"n_genes must be ≥ 0, got {n_genes!r}")
    if not (0.0 <= mean_intron_fraction <= 1.0):
        raise ValueError(f"mean_intron_fraction must be in [0,1], got {mean_intron_fraction!r}")
    return float(n_genes * (1.0 - mean_intron_fraction) * 2.0)


def dna_repair_phi(phi_damage: float, repair_efficiency: float) -> float:
    """Residual DNA damage after repair mechanism acts.

    phi_residual = phi_damage × (1 − repair_efficiency)

    Parameters
    ----------
    phi_damage        : float — initial DNA damage φ (must be ≥ 0)
    repair_efficiency : float — repair fraction ∈ [0, 1]

    Returns
    -------
    phi_residual : float ≥ 0
    """
    if phi_damage < 0.0:
        raise ValueError(f"phi_damage must be ≥ 0, got {phi_damage!r}")
    if not (0.0 <= repair_efficiency <= 1.0):
        raise ValueError(f"repair_efficiency must be in [0,1], got {repair_efficiency!r}")
    return float(phi_damage * (1.0 - repair_efficiency))


def recombination_phi(n_crossovers: float, genome_length_morgan: float) -> float:
    """Recombination fraction given crossover density.

    r = 1 − exp(−2 × n_crossovers × genome_length_morgan)  (Haldane)
    clipped to [0, 0.5]

    Parameters
    ----------
    n_crossovers          : float — mean crossover events per meiosis (must be ≥ 0)
    genome_length_morgan  : float — genome length in Morgans (must be > 0)

    Returns
    -------
    r : float ∈ [0, 0.5]
    """
    if n_crossovers < 0.0:
        raise ValueError(f"n_crossovers must be ≥ 0, got {n_crossovers!r}")
    if genome_length_morgan <= 0.0:
        raise ValueError(f"genome_length_morgan must be > 0, got {genome_length_morgan!r}")
    r = 0.5 * (1.0 - math.exp(-2.0 * n_crossovers / genome_length_morgan))
    return float(np.clip(r, 0.0, 0.5))


def copy_number_phi(n_copies: int, ref_copies: int = 2) -> float:
    """Copy number variation φ relative to diploid reference.

    CNV = n_copies / ref_copies

    Parameters
    ----------
    n_copies  : int — observed copy number (must be ≥ 0)
    ref_copies: int — reference diploid copy count (default 2, must be > 0)

    Returns
    -------
    CNV : float
    """
    if n_copies < 0:
        raise ValueError(f"n_copies must be ≥ 0, got {n_copies!r}")
    if ref_copies <= 0:
        raise ValueError(f"ref_copies must be > 0, got {ref_copies!r}")
    return float(n_copies / ref_copies)


def epigenetic_phi(phi_methylation: float, phi_acetylation: float) -> float:
    """Epigenetic φ modification net effect on gene expression.

    phi_epi = phi_acetylation − phi_methylation

    Acetylation opens chromatin (+φ); methylation closes it (−φ).

    Parameters
    ----------
    phi_methylation  : float — methylation silencing φ (must be ≥ 0)
    phi_acetylation  : float — acetylation activation φ (must be ≥ 0)

    Returns
    -------
    phi_epi : float
    """
    if phi_methylation < 0.0:
        raise ValueError(f"phi_methylation must be ≥ 0, got {phi_methylation!r}")
    if phi_acetylation < 0.0:
        raise ValueError(f"phi_acetylation must be ≥ 0, got {phi_acetylation!r}")
    return float(phi_acetylation - phi_methylation)


def transposon_phi_activity(phi_transposon: float,
                             silencing_fraction: float = 0.9) -> float:
    """Active transposon φ after piRNA/siRNA silencing.

    phi_active = phi_transposon × (1 − silencing_fraction)

    Parameters
    ----------
    phi_transposon     : float — total transposon φ (must be ≥ 0)
    silencing_fraction : float — epigenetic silencing ∈ [0, 1] (default 0.9)

    Returns
    -------
    phi_active : float ≥ 0
    """
    if phi_transposon < 0.0:
        raise ValueError(f"phi_transposon must be ≥ 0, got {phi_transposon!r}")
    if not (0.0 <= silencing_fraction <= 1.0):
        raise ValueError(f"silencing_fraction must be in [0,1], got {silencing_fraction!r}")
    return float(phi_transposon * (1.0 - silencing_fraction))


def gene_phi_density(n_genes: int, genome_size_mbp: float) -> float:
    """Gene density: genes per megabase pair.

    density = n_genes / genome_size_mbp

    Parameters
    ----------
    n_genes         : int   — number of genes (must be ≥ 0)
    genome_size_mbp : float — genome size in Mbp (must be > 0)

    Returns
    -------
    density : float
    """
    if n_genes < 0:
        raise ValueError(f"n_genes must be ≥ 0, got {n_genes!r}")
    if genome_size_mbp <= 0.0:
        raise ValueError(f"genome_size_mbp must be > 0, got {genome_size_mbp!r}")
    return float(n_genes / genome_size_mbp)
