# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/genetics/evolution.py
==========================
Evolution as φ-Field Selection Dynamics — Pillar 25.
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


def natural_selection_phi(phi_fit: float, phi_unfit: float,
                           selection_coeff: float) -> float:
    """φ change due to natural selection per generation.

    Δφ = selection_coeff × (phi_fit − phi_unfit) × phi_fit / (phi_fit + phi_unfit + ε)

    Parameters
    ----------
    phi_fit        : float — φ of fit allele carriers (must be ≥ 0)
    phi_unfit      : float — φ of unfit allele carriers (must be ≥ 0)
    selection_coeff: float — selection coefficient ∈ [0, 1]

    Returns
    -------
    delta_phi : float
    """
    if phi_fit < 0.0:
        raise ValueError(f"phi_fit must be ≥ 0, got {phi_fit!r}")
    if phi_unfit < 0.0:
        raise ValueError(f"phi_unfit must be ≥ 0, got {phi_unfit!r}")
    if not (0.0 <= selection_coeff <= 1.0):
        raise ValueError(f"selection_coeff must be in [0,1], got {selection_coeff!r}")
    total = phi_fit + phi_unfit + _EPS
    return float(selection_coeff * (phi_fit - phi_unfit) * phi_fit / total)


def genetic_drift_phi(p: float, N_e: float) -> float:
    """Standard deviation of allele frequency change due to drift.

    σ_drift = sqrt(p × (1 − p) / N_e)

    Parameters
    ----------
    p   : float — allele frequency ∈ [0, 1]
    N_e : float — effective population size (must be > 0)

    Returns
    -------
    sigma : float ≥ 0
    """
    if not (0.0 <= p <= 1.0):
        raise ValueError(f"p must be in [0,1], got {p!r}")
    if N_e <= 0.0:
        raise ValueError(f"N_e must be > 0, got {N_e!r}")
    return float(math.sqrt(p * (1.0 - p) / N_e))


def fitness_phi(phi_reproductive: float, phi_survival: float,
                 phi_offspring: float) -> float:
    """Composite Darwinian fitness φ.

    W = phi_survival × phi_reproductive × phi_offspring

    Parameters
    ----------
    phi_reproductive : float — φ of reproductive success (must be ≥ 0)
    phi_survival     : float — φ of viability/survival (must be ≥ 0)
    phi_offspring    : float — mean offspring φ quality (must be ≥ 0)

    Returns
    -------
    W : float — composite fitness φ
    """
    for name, v in [("phi_reproductive", phi_reproductive),
                    ("phi_survival", phi_survival),
                    ("phi_offspring", phi_offspring)]:
        if v < 0.0:
            raise ValueError(f"{name} must be ≥ 0, got {v!r}")
    return float(phi_survival * phi_reproductive * phi_offspring)


def speciation_phi_barrier(phi_gene_flow: float, phi_isolation: float) -> float:
    """Speciation barrier as isolation φ minus gene flow φ.

    barrier = phi_isolation − phi_gene_flow

    Positive barrier → speciation is occurring; negative → gene flow prevents it.

    Parameters
    ----------
    phi_gene_flow  : float — gene flow φ between populations (must be ≥ 0)
    phi_isolation  : float — reproductive isolation φ (must be ≥ 0)

    Returns
    -------
    barrier : float
    """
    if phi_gene_flow < 0.0:
        raise ValueError(f"phi_gene_flow must be ≥ 0, got {phi_gene_flow!r}")
    if phi_isolation < 0.0:
        raise ValueError(f"phi_isolation must be ≥ 0, got {phi_isolation!r}")
    return float(phi_isolation - phi_gene_flow)


def phylogenetic_phi_distance(n_substitutions: int, n_sites: int) -> float:
    """Jukes-Cantor corrected phylogenetic φ distance.

    d = −(3/4) × ln(1 − (4/3) × p)   where p = n_substitutions / n_sites

    Parameters
    ----------
    n_substitutions : int — observed substitutions (must be ≥ 0)
    n_sites         : int — total aligned sites (must be > 0)

    Returns
    -------
    d : float — corrected genetic distance
    """
    if n_substitutions < 0:
        raise ValueError(f"n_substitutions must be ≥ 0, got {n_substitutions!r}")
    if n_sites <= 0:
        raise ValueError(f"n_sites must be > 0, got {n_sites!r}")
    p = min(n_substitutions / n_sites, 0.74)  # cap below JC singularity
    return float(-(3.0 / 4.0) * math.log(1.0 - (4.0 / 3.0) * p))


def adaptive_radiation_phi(phi_ancestor: float, n_niches: int,
                            radiation_rate: float = 0.1) -> float:
    """Total φ-diversification during an adaptive radiation.

    phi_total = phi_ancestor × n_niches × radiation_rate

    Parameters
    ----------
    phi_ancestor   : float — ancestral lineage φ (must be ≥ 0)
    n_niches       : int   — available ecological niches (must be ≥ 1)
    radiation_rate : float — fraction of niches colonised per event (must be ∈ (0,1])

    Returns
    -------
    phi_total : float
    """
    if phi_ancestor < 0.0:
        raise ValueError(f"phi_ancestor must be ≥ 0, got {phi_ancestor!r}")
    if n_niches < 1:
        raise ValueError(f"n_niches must be ≥ 1, got {n_niches!r}")
    if not (0.0 < radiation_rate <= 1.0):
        raise ValueError(f"radiation_rate must be in (0,1], got {radiation_rate!r}")
    return float(phi_ancestor * n_niches * radiation_rate)


def bottleneck_phi_loss(phi_pre: float, N_bottleneck: int,
                         N_pre: int) -> float:
    """φ-diversity lost in a population bottleneck.

    phi_post = phi_pre × N_bottleneck / N_pre

    Parameters
    ----------
    phi_pre       : float — pre-bottleneck diversity φ (must be ≥ 0)
    N_bottleneck  : int   — bottleneck population size (must be ≥ 1)
    N_pre         : int   — pre-bottleneck population size (must be > 0)

    Returns
    -------
    phi_post : float
    """
    if phi_pre < 0.0:
        raise ValueError(f"phi_pre must be ≥ 0, got {phi_pre!r}")
    if N_bottleneck < 1:
        raise ValueError(f"N_bottleneck must be ≥ 1, got {N_bottleneck!r}")
    if N_pre <= 0:
        raise ValueError(f"N_pre must be > 0, got {N_pre!r}")
    return float(phi_pre * min(N_bottleneck, N_pre) / N_pre)


def founder_phi_effect(phi_source: float, n_founders: int,
                        N_source: int) -> float:
    """φ-diversity retained by a founder population.

    phi_founder = phi_source × sqrt(n_founders / N_source)

    Parameters
    ----------
    phi_source : float — source population φ diversity (must be ≥ 0)
    n_founders : int   — number of founding individuals (must be ≥ 1)
    N_source   : int   — source population size (must be > 0)

    Returns
    -------
    phi_founder : float
    """
    if phi_source < 0.0:
        raise ValueError(f"phi_source must be ≥ 0, got {phi_source!r}")
    if n_founders < 1:
        raise ValueError(f"n_founders must be ≥ 1, got {n_founders!r}")
    if N_source <= 0:
        raise ValueError(f"N_source must be > 0, got {N_source!r}")
    return float(phi_source * math.sqrt(min(n_founders, N_source) / N_source))


def horizontal_gene_phi(phi_donor: float, transfer_probability: float,
                         n_recipients: int) -> float:
    """Total φ transferred horizontally across n recipients.

    phi_hgt = phi_donor × transfer_probability × n_recipients

    Parameters
    ----------
    phi_donor            : float — donor gene φ (must be ≥ 0)
    transfer_probability : float — probability per contact ∈ [0, 1]
    n_recipients         : int   — number of potential recipients (must be ≥ 0)

    Returns
    -------
    phi_hgt : float
    """
    if phi_donor < 0.0:
        raise ValueError(f"phi_donor must be ≥ 0, got {phi_donor!r}")
    if not (0.0 <= transfer_probability <= 1.0):
        raise ValueError(f"transfer_probability must be in [0,1], got {transfer_probability!r}")
    if n_recipients < 0:
        raise ValueError(f"n_recipients must be ≥ 0, got {n_recipients!r}")
    return float(phi_donor * transfer_probability * n_recipients)


def evolutionary_phi_rate(phi_divergence: float, t_mya: float) -> float:
    """Evolutionary φ rate (substitutions per million years).

    rate = phi_divergence / t_mya

    Parameters
    ----------
    phi_divergence : float — total φ divergence between lineages (must be ≥ 0)
    t_mya          : float — divergence time in Ma (must be > 0)

    Returns
    -------
    rate : float
    """
    if phi_divergence < 0.0:
        raise ValueError(f"phi_divergence must be ≥ 0, got {phi_divergence!r}")
    if t_mya <= 0.0:
        raise ValueError(f"t_mya must be > 0, got {t_mya!r}")
    return float(phi_divergence / t_mya)
