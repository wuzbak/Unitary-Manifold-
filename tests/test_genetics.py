# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_genetics.py
=======================
Unit tests for the src/genetics package — Pillar 25: Genetics & Genomics.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import math
import numpy as np
import pytest

from src.genetics.genomics import (
    mutation_rate_phi, genetic_phi_diversity, allele_phi_frequency,
    genome_phi_complexity, dna_repair_phi, recombination_phi,
    copy_number_phi, epigenetic_phi, transposon_phi_activity, gene_phi_density,
)
from src.genetics.evolution import (
    natural_selection_phi, genetic_drift_phi, fitness_phi, speciation_phi_barrier,
    phylogenetic_phi_distance, adaptive_radiation_phi, bottleneck_phi_loss,
    founder_phi_effect, horizontal_gene_phi, evolutionary_phi_rate,
)
from src.genetics.expression import (
    transcription_phi_rate, translation_phi_efficiency, protein_phi_folding,
    gene_regulatory_phi, rna_stability_phi, splicing_phi_fidelity,
    protein_phi_interaction, expression_phi_noise, chromatin_phi_state,
    gene_phi_dosage,
)


# ---------------------------------------------------------------------------
# genomics.py
# ---------------------------------------------------------------------------

class TestMutationRatePhi:
    def test_basic(self):
        assert mutation_rate_phi(10, 1000, 10) == pytest.approx(1e-3)

    def test_zero_mutations(self):
        assert mutation_rate_phi(0, 1000, 10) == pytest.approx(0.0)

    def test_raises_zero_bases(self):
        with pytest.raises(ValueError):
            mutation_rate_phi(10, 0, 10)


class TestGeneticPhiDiversity:
    def test_max_two_equal(self):
        v = genetic_phi_diversity([0.5, 0.5])
        assert v == pytest.approx(0.5)

    def test_monomorphic_zero(self):
        v = genetic_phi_diversity([1.0, 0.0])
        assert v == pytest.approx(0.0, abs=1e-6)

    def test_raises_negative(self):
        with pytest.raises(ValueError):
            genetic_phi_diversity([-0.1, 1.1])


class TestAllelePhiFrequency:
    def test_half(self):
        assert allele_phi_frequency(50, 100) == pytest.approx(0.5)

    def test_fixed(self):
        assert allele_phi_frequency(100, 100) == pytest.approx(1.0)

    def test_raises_zero_total(self):
        with pytest.raises(ValueError):
            allele_phi_frequency(50, 0)


class TestGenomePhiComplexity:
    def test_no_introns(self):
        v = genome_phi_complexity(20000, 0.0)
        assert v == pytest.approx(40000.0)

    def test_with_introns(self):
        v = genome_phi_complexity(20000, 0.5)
        assert v == pytest.approx(20000.0)

    def test_raises_bad_fraction(self):
        with pytest.raises(ValueError):
            genome_phi_complexity(20000, 1.5)


class TestDnaRepairPhi:
    def test_perfect_repair(self):
        assert dna_repair_phi(10.0, 1.0) == pytest.approx(0.0)

    def test_no_repair(self):
        assert dna_repair_phi(10.0, 0.0) == pytest.approx(10.0)

    def test_raises_bad_efficiency(self):
        with pytest.raises(ValueError):
            dna_repair_phi(10.0, 1.5)


class TestRecombinationPhi:
    def test_zero_crossovers(self):
        assert recombination_phi(0.0, 1.0) == pytest.approx(0.0, abs=1e-6)

    def test_max_half(self):
        v = recombination_phi(100.0, 1.0)
        assert v <= 0.5 + 1e-10

    def test_raises_zero_length(self):
        with pytest.raises(ValueError):
            recombination_phi(1.0, 0.0)


class TestCopyNumberPhi:
    def test_diploid(self):
        assert copy_number_phi(2, 2) == pytest.approx(1.0)

    def test_amplification(self):
        assert copy_number_phi(6, 2) == pytest.approx(3.0)

    def test_raises_zero_ref(self):
        with pytest.raises(ValueError):
            copy_number_phi(2, 0)


class TestEpigeneticPhi:
    def test_equal_zero(self):
        assert epigenetic_phi(1.0, 1.0) == pytest.approx(0.0)

    def test_acetylation_dominant(self):
        assert epigenetic_phi(0.5, 2.0) > 0.0

    def test_methylation_dominant(self):
        assert epigenetic_phi(2.0, 0.5) < 0.0


class TestTransposonPhiActivity:
    def test_fully_silenced(self):
        assert transposon_phi_activity(1.0, 1.0) == pytest.approx(0.0)

    def test_mostly_silenced(self):
        assert transposon_phi_activity(1.0, 0.9) == pytest.approx(0.1)

    def test_raises_bad_silencing(self):
        with pytest.raises(ValueError):
            transposon_phi_activity(1.0, 1.5)


class TestGenePhiDensity:
    def test_basic(self):
        assert gene_phi_density(20000, 3000.0) == pytest.approx(20000 / 3000.0)

    def test_raises_zero_genome(self):
        with pytest.raises(ValueError):
            gene_phi_density(20000, 0.0)


# ---------------------------------------------------------------------------
# evolution.py
# ---------------------------------------------------------------------------

class TestNaturalSelectionPhi:
    def test_equal_zero(self):
        assert natural_selection_phi(5.0, 5.0, 0.5) == pytest.approx(0.0)

    def test_positive_for_fitter(self):
        v = natural_selection_phi(8.0, 2.0, 0.5)
        assert v > 0.0

    def test_raises_bad_coeff(self):
        with pytest.raises(ValueError):
            natural_selection_phi(8.0, 2.0, 1.5)


class TestGeneticDriftPhi:
    def test_large_population_small_drift(self):
        v_large = genetic_drift_phi(0.5, 1e6)
        v_small = genetic_drift_phi(0.5, 100)
        assert v_large < v_small

    def test_raises_zero_Ne(self):
        with pytest.raises(ValueError):
            genetic_drift_phi(0.5, 0.0)


class TestFitnessPhi:
    def test_zero_component_zero_fitness(self):
        assert fitness_phi(0.0, 1.0, 1.0) == pytest.approx(0.0)

    def test_positive(self):
        assert fitness_phi(2.0, 3.0, 4.0) == pytest.approx(24.0)


class TestSpeciationPhiBarrier:
    def test_speciation_occurring(self):
        assert speciation_phi_barrier(1.0, 5.0) > 0.0

    def test_gene_flow_prevents(self):
        assert speciation_phi_barrier(10.0, 2.0) < 0.0


class TestPhylogeneticPhiDistance:
    def test_zero_substitutions(self):
        assert phylogenetic_phi_distance(0, 1000) == pytest.approx(0.0, abs=1e-6)

    def test_positive(self):
        v = phylogenetic_phi_distance(100, 1000)
        assert v > 0.0

    def test_raises_zero_sites(self):
        with pytest.raises(ValueError):
            phylogenetic_phi_distance(10, 0)


class TestAdaptiveRadiationPhi:
    def test_basic(self):
        assert adaptive_radiation_phi(1.0, 10, 0.1) == pytest.approx(1.0)

    def test_raises_zero_niches(self):
        with pytest.raises(ValueError):
            adaptive_radiation_phi(1.0, 0)


class TestBottleneckPhiLoss:
    def test_extreme_bottleneck(self):
        v = bottleneck_phi_loss(1.0, 1, 1000)
        assert v < 0.01

    def test_no_bottleneck(self):
        v = bottleneck_phi_loss(1.0, 1000, 1000)
        assert v == pytest.approx(1.0)

    def test_raises_zero_pre(self):
        with pytest.raises(ValueError):
            bottleneck_phi_loss(1.0, 10, 0)


class TestFounderPhiEffect:
    def test_few_founders_low(self):
        v = founder_phi_effect(1.0, 5, 1000)
        assert v < 0.1

    def test_all_founders_full(self):
        v = founder_phi_effect(1.0, 1000, 1000)
        assert v == pytest.approx(1.0)


class TestHorizontalGenePhi:
    def test_zero_probability(self):
        assert horizontal_gene_phi(1.0, 0.0, 100) == pytest.approx(0.0)

    def test_scales_with_recipients(self):
        v1 = horizontal_gene_phi(1.0, 0.1, 10)
        v2 = horizontal_gene_phi(1.0, 0.1, 20)
        assert v2 == pytest.approx(2 * v1)

    def test_raises_bad_probability(self):
        with pytest.raises(ValueError):
            horizontal_gene_phi(1.0, 1.5, 10)


class TestEvolutionaryPhiRate:
    def test_basic(self):
        assert evolutionary_phi_rate(10.0, 5.0) == pytest.approx(2.0)

    def test_raises_zero_time(self):
        with pytest.raises(ValueError):
            evolutionary_phi_rate(10.0, 0.0)


# ---------------------------------------------------------------------------
# expression.py
# ---------------------------------------------------------------------------

class TestTranscriptionPhiRate:
    def test_basic(self):
        v = transcription_phi_rate(1.0, 2.0, 0.0)
        assert v > 0.0

    def test_raises_zero_promoter(self):
        with pytest.raises(ValueError):
            transcription_phi_rate(1.0, 0.0, 0.0)


class TestTranslationPhiEfficiency:
    def test_basic(self):
        assert translation_phi_efficiency(1.0, 1.0, 1.0) == pytest.approx(1.0)

    def test_raises_zero_codon_bias(self):
        with pytest.raises(ValueError):
            translation_phi_efficiency(1.0, 1.0, 0.0)


class TestProteinPhiFolding:
    def test_no_misfolding(self):
        assert protein_phi_folding(1.0, 0.0, 0.0) == pytest.approx(1.0)

    def test_chaperone_helps(self):
        v = protein_phi_folding(1.0, 1.0, 0.1)
        assert v > protein_phi_folding(1.0, 0.0, 0.1)


class TestGeneRegulatoryPhi:
    def test_activators_only(self):
        assert gene_regulatory_phi(3, 1.0, 0, 0.0) == pytest.approx(3.0)

    def test_repressors_only(self):
        assert gene_regulatory_phi(0, 0.0, 2, 1.0) == pytest.approx(-2.0)

    def test_raises_negative_activator_phi(self):
        with pytest.raises(ValueError):
            gene_regulatory_phi(1, -1.0, 0, 0.0)


class TestRnaStabilityPhi:
    def test_t_zero(self):
        assert rna_stability_phi(1.0, 0.0) == pytest.approx(1.0)

    def test_decay(self):
        v = rna_stability_phi(1.0, 10.0, 0.1)
        assert v == pytest.approx(math.exp(-1.0), rel=1e-4)

    def test_raises_negative_decay(self):
        with pytest.raises(ValueError):
            rna_stability_phi(1.0, 1.0, -0.1)


class TestSplicingPhiFidelity:
    def test_perfect(self):
        assert splicing_phi_fidelity(100, 100) == pytest.approx(1.0)

    def test_half(self):
        assert splicing_phi_fidelity(50, 100) == pytest.approx(0.5)

    def test_raises_zero_total(self):
        with pytest.raises(ValueError):
            splicing_phi_fidelity(50, 0)


class TestProteinPhiInteraction:
    def test_zero_phi_A(self):
        assert protein_phi_interaction(0.0, 1.0, 1.0) == pytest.approx(0.0)

    def test_positive(self):
        v = protein_phi_interaction(1.0, 1.0, 1.0)
        assert v > 0.0

    def test_raises_zero_Kd(self):
        with pytest.raises(ValueError):
            protein_phi_interaction(1.0, 1.0, 0.0)


class TestExpressionPhiNoise:
    def test_positive(self):
        v = expression_phi_noise(100.0, 0.1, 1000)
        assert v > 0.0

    def test_raises_zero_mean(self):
        with pytest.raises(ValueError):
            expression_phi_noise(0.0, 0.1, 100)


class TestChromatinPhiState:
    def test_fully_open(self):
        v = chromatin_phi_state(1.0, 0.0, 0.0)
        assert v == pytest.approx(1.0)

    def test_fully_closed(self):
        v = chromatin_phi_state(0.0, 1.0, 0.0)
        assert v == pytest.approx(0.0)

    def test_remodeling_opens(self):
        v1 = chromatin_phi_state(0.5, 0.5, 0.0)
        v2 = chromatin_phi_state(0.5, 0.5, 0.3)
        assert v2 >= v1


class TestGenePhiDosage:
    def test_zero_copies(self):
        assert gene_phi_dosage(0, 1.0) == pytest.approx(0.0)

    def test_diploid(self):
        assert gene_phi_dosage(2, 3.0) == pytest.approx(6.0)
