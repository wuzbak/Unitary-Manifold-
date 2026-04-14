# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""src/genetics — Pillar 25: Genetics & Genomics."""
from .genomics import (
    mutation_rate_phi, genetic_phi_diversity, allele_phi_frequency,
    genome_phi_complexity, dna_repair_phi, recombination_phi,
    copy_number_phi, epigenetic_phi, transposon_phi_activity, gene_phi_density,
)
from .evolution import (
    natural_selection_phi, genetic_drift_phi, fitness_phi,
    speciation_phi_barrier, phylogenetic_phi_distance,
    adaptive_radiation_phi, bottleneck_phi_loss, founder_phi_effect,
    horizontal_gene_phi, evolutionary_phi_rate,
)
from .expression import (
    transcription_phi_rate, translation_phi_efficiency, protein_phi_folding,
    gene_regulatory_phi, rna_stability_phi, splicing_phi_fidelity,
    protein_phi_interaction, expression_phi_noise, chromatin_phi_state,
    gene_phi_dosage,
)

__all__ = [
    "mutation_rate_phi", "genetic_phi_diversity", "allele_phi_frequency",
    "genome_phi_complexity", "dna_repair_phi", "recombination_phi",
    "copy_number_phi", "epigenetic_phi", "transposon_phi_activity",
    "gene_phi_density",
    "natural_selection_phi", "genetic_drift_phi", "fitness_phi",
    "speciation_phi_barrier", "phylogenetic_phi_distance",
    "adaptive_radiation_phi", "bottleneck_phi_loss", "founder_phi_effect",
    "horizontal_gene_phi", "evolutionary_phi_rate",
    "transcription_phi_rate", "translation_phi_efficiency",
    "protein_phi_folding", "gene_regulatory_phi", "rna_stability_phi",
    "splicing_phi_fidelity", "protein_phi_interaction", "expression_phi_noise",
    "chromatin_phi_state", "gene_phi_dosage",
]
