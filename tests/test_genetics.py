# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_genetics.py
=======================
Unit tests for the src/genetics package — Pillar 25: Genetics, Genomics &
Synthetic Biology.
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
from src.genetics.synthetic_biology import (
    gene_circuit_phi_attractor, crispr_phi_edit_precision,
    metabolic_pathway_phi_flux, ai_synbio_phi_convergence,
    chassis_phi_minimality, biosafety_containment_phi,
    dna_data_storage_phi_density, directed_evolution_phi_gradient,
    synthetic_gene_circuit_noise, bioeconomy_phi_output,
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


# ===========================================================================
# synthetic_biology.py — Pillar 25 Extension: Synthetic Biology
# ===========================================================================

class TestGeneCircuitPhiAttractor:
    def test_no_repressor(self):
        # phi_repressor=0 → full activator output
        v = gene_circuit_phi_attractor(2.0, 0.0)
        assert v == pytest.approx(2.0)

    def test_full_repression(self):
        # Very high repressor relative to K → output → 0
        v = gene_circuit_phi_attractor(1.0, 1e6, K=1.0)
        assert v < 1e-5

    def test_half_max(self):
        # phi_repressor == K, n=1 → phi_ss = phi_activator / 2
        v = gene_circuit_phi_attractor(4.0, 1.0, hill_n=1.0, K=1.0)
        assert v == pytest.approx(2.0)

    def test_hill_cooperativity_sharpens(self):
        # Higher hill_n → stronger repression when repressor > K
        # phi_repressor=2.0 > K=1.0:
        #   n=1: 1/(1+2) = 0.333; n=4: 1/(1+16) = 0.059 → v2 < v1
        v1 = gene_circuit_phi_attractor(1.0, 2.0, hill_n=1.0, K=1.0)
        v2 = gene_circuit_phi_attractor(1.0, 2.0, hill_n=4.0, K=1.0)
        assert v2 < v1

    def test_raises_negative_activator(self):
        with pytest.raises(ValueError):
            gene_circuit_phi_attractor(-1.0, 0.5)

    def test_raises_negative_repressor(self):
        with pytest.raises(ValueError):
            gene_circuit_phi_attractor(1.0, -0.5)

    def test_raises_zero_K(self):
        with pytest.raises(ValueError):
            gene_circuit_phi_attractor(1.0, 0.5, K=0.0)

    def test_raises_zero_hill(self):
        with pytest.raises(ValueError):
            gene_circuit_phi_attractor(1.0, 0.5, hill_n=0.0)


class TestCrisprPhiEditPrecision:
    def test_perfect_guide_no_off_target(self):
        v = crispr_phi_edit_precision(1.0, 0.0)
        assert v == pytest.approx(1.0)

    def test_hdr_template_adds_phi(self):
        v = crispr_phi_edit_precision(1.0, 0.0, repair_template_phi=0.5)
        assert v == pytest.approx(1.5)

    def test_off_target_reduces_edit(self):
        v = crispr_phi_edit_precision(1.0, 0.2)
        assert v == pytest.approx(0.8)

    def test_full_off_target_with_template(self):
        # guide=1.0, off-target=1.0, template=0.3 → 0 + 0.3 = 0.3
        v = crispr_phi_edit_precision(1.0, 1.0, repair_template_phi=0.3)
        assert v == pytest.approx(0.3)

    def test_raises_guide_out_of_range(self):
        with pytest.raises(ValueError):
            crispr_phi_edit_precision(1.5, 0.0)

    def test_raises_negative_off_target(self):
        with pytest.raises(ValueError):
            crispr_phi_edit_precision(0.9, -0.1)

    def test_raises_negative_template(self):
        with pytest.raises(ValueError):
            crispr_phi_edit_precision(0.9, 0.1, repair_template_phi=-1.0)


class TestMetabolicPathwayPhiFlux:
    def test_single_enzyme_no_bottleneck(self):
        v = metabolic_pathway_phi_flux(1, 2.0, 0.0)
        assert v == pytest.approx(2.0)

    def test_multiple_enzymes(self):
        v = metabolic_pathway_phi_flux(5, 1.0, 0.0)
        assert v == pytest.approx(5.0)

    def test_bottleneck_reduces_flux(self):
        v = metabolic_pathway_phi_flux(5, 1.0, 0.5)
        assert v == pytest.approx(2.5)

    def test_complete_bottleneck(self):
        v = metabolic_pathway_phi_flux(5, 1.0, 1.0)
        assert v == pytest.approx(0.0)

    def test_raises_zero_enzymes(self):
        with pytest.raises(ValueError):
            metabolic_pathway_phi_flux(0, 1.0)

    def test_raises_bad_bottleneck(self):
        with pytest.raises(ValueError):
            metabolic_pathway_phi_flux(3, 1.0, 1.5)


class TestAiSynbioPhiConvergence:
    def test_zero_cycles(self):
        v = ai_synbio_phi_convergence(100.0, 0.1, 0)
        assert v == pytest.approx(0.0)

    def test_one_cycle(self):
        v = ai_synbio_phi_convergence(100.0, 0.1, 1)
        assert v == pytest.approx(10.0)

    def test_saturates(self):
        # Many cycles → approaches phi_design_space
        v = ai_synbio_phi_convergence(100.0, 0.5, 100)
        assert v == pytest.approx(100.0, rel=1e-5)

    def test_monotone_increasing(self):
        vals = [ai_synbio_phi_convergence(1.0, 0.3, n) for n in range(5)]
        for i in range(len(vals) - 1):
            assert vals[i] <= vals[i + 1]

    def test_raises_zero_accuracy(self):
        with pytest.raises(ValueError):
            ai_synbio_phi_convergence(100.0, 0.0, 5)

    def test_raises_negative_space(self):
        with pytest.raises(ValueError):
            ai_synbio_phi_convergence(-1.0, 0.1, 5)


class TestChassisPhiMinimality:
    def test_minimal_genome(self):
        # n_essential == n_total → minimality = phi_per_gene × 1.0
        v = chassis_phi_minimality(473, 473, phi_per_gene=1.0)
        assert v == pytest.approx(1.0)

    def test_bloated_genome(self):
        v = chassis_phi_minimality(473, 4000, phi_per_gene=1.0)
        assert v == pytest.approx(473 / 4000)

    def test_phi_per_gene_scales(self):
        v = chassis_phi_minimality(100, 200, phi_per_gene=2.0)
        assert v == pytest.approx(1.0)  # 2.0 × 100/200 = 1.0

    def test_raises_zero_essential(self):
        with pytest.raises(ValueError):
            chassis_phi_minimality(0, 100)

    def test_raises_total_less_than_essential(self):
        with pytest.raises(ValueError):
            chassis_phi_minimality(100, 50)

    def test_raises_zero_phi_per_gene(self):
        with pytest.raises(ValueError):
            chassis_phi_minimality(100, 200, phi_per_gene=0.0)


class TestBiosafetyContainmentPhi:
    def test_perfect_containment(self):
        v = biosafety_containment_phi(1.0, 1.0, auxotrophy_layers=1)
        assert v == pytest.approx(0.0)

    def test_no_containment(self):
        v = biosafety_containment_phi(0.5, 0.0, auxotrophy_layers=3)
        assert v == pytest.approx(0.5)

    def test_multiple_layers_compound(self):
        # 2 layers of 50% containment → residual = 0.5 × 0.5^2 = 0.125
        v = biosafety_containment_phi(0.5, 0.5, auxotrophy_layers=2)
        assert v == pytest.approx(0.5 * 0.5 ** 2)

    def test_monotone_decreasing_with_layers(self):
        vs = [biosafety_containment_phi(1.0, 0.8, n) for n in range(1, 6)]
        for i in range(len(vs) - 1):
            assert vs[i] >= vs[i + 1]

    def test_raises_negative_escape(self):
        with pytest.raises(ValueError):
            biosafety_containment_phi(-0.1, 0.9)

    def test_raises_zero_layers(self):
        with pytest.raises(ValueError):
            biosafety_containment_phi(0.5, 0.9, auxotrophy_layers=0)


class TestDnaDataStoragePhiDensity:
    def test_no_overhead_perfect_fidelity(self):
        v = dna_data_storage_phi_density(1000.0, 0.0, synthesis_fidelity=1.0)
        assert v == pytest.approx(1000.0)

    def test_overhead_reduces_density(self):
        v = dna_data_storage_phi_density(1000.0, 1.0, synthesis_fidelity=1.0)
        assert v == pytest.approx(500.0)

    def test_fidelity_reduces_density(self):
        v = dna_data_storage_phi_density(1000.0, 0.0, synthesis_fidelity=0.9)
        assert v == pytest.approx(900.0)

    def test_raises_zero_bits(self):
        v = dna_data_storage_phi_density(0.0, 0.1)
        assert v == pytest.approx(0.0)

    def test_raises_negative_bits(self):
        with pytest.raises(ValueError):
            dna_data_storage_phi_density(-1.0, 0.1)

    def test_raises_zero_fidelity(self):
        with pytest.raises(ValueError):
            dna_data_storage_phi_density(100.0, 0.0, synthesis_fidelity=0.0)


class TestDirectedEvolutionPhiGradient:
    def test_zero_rounds(self):
        v = directed_evolution_phi_gradient(1.0, 1.0, 0)
        assert v == pytest.approx(1.0)

    def test_increases_with_rounds(self):
        v = directed_evolution_phi_gradient(1.0, 1.0, 10)
        assert v > 1.0

    def test_selection_pressure_scales(self):
        v1 = directed_evolution_phi_gradient(1.0, 1.0, 5)
        v2 = directed_evolution_phi_gradient(1.0, 2.0, 5)
        assert v2 > v1

    def test_zero_initial_stays_zero(self):
        v = directed_evolution_phi_gradient(0.0, 1.0, 10)
        assert v == pytest.approx(0.0)

    def test_raises_negative_selection(self):
        with pytest.raises(ValueError):
            directed_evolution_phi_gradient(1.0, -0.1, 5)

    def test_raises_zero_mutation_rate(self):
        with pytest.raises(ValueError):
            directed_evolution_phi_gradient(1.0, 1.0, 5, mutation_rate=0.0)


class TestSyntheticGeneCircuitNoise:
    def test_zero_noise(self):
        # B_intrinsic ≈ 0 → very high SNR
        v = synthetic_gene_circuit_noise(10.0, 1e-30, n_redundant_copies=1)
        assert v > 1e10

    def test_redundancy_increases_snr(self):
        v1 = synthetic_gene_circuit_noise(1.0, 0.5, n_redundant_copies=1)
        v4 = synthetic_gene_circuit_noise(1.0, 0.5, n_redundant_copies=4)
        assert v4 == pytest.approx(v1 * 2.0, rel=1e-6)  # sqrt(4)/sqrt(1) = 2

    def test_raises_negative_signal(self):
        with pytest.raises(ValueError):
            synthetic_gene_circuit_noise(-1.0, 0.1)

    def test_raises_zero_copies(self):
        with pytest.raises(ValueError):
            synthetic_gene_circuit_noise(1.0, 0.1, n_redundant_copies=0)

    def test_raises_negative_noise(self):
        with pytest.raises(ValueError):
            synthetic_gene_circuit_noise(1.0, -0.1)


class TestBioeconomyPhiOutput:
    def test_unit_values(self):
        v = bioeconomy_phi_output(1.0, 1.0, 1.0)
        assert v == pytest.approx(1.0)

    def test_scale_factor(self):
        v = bioeconomy_phi_output(1.0, 1.0, 1.0, scale_factor=1000.0)
        assert v == pytest.approx(1000.0)

    def test_zero_yield(self):
        v = bioeconomy_phi_output(10.0, 5.0, 0.0)
        assert v == pytest.approx(0.0)

    def test_try_product(self):
        # titer=10, rate=2, yield=0.5, scale=1 → 10
        v = bioeconomy_phi_output(10.0, 2.0, 0.5)
        assert v == pytest.approx(10.0)

    def test_raises_negative_titer(self):
        with pytest.raises(ValueError):
            bioeconomy_phi_output(-1.0, 1.0, 0.5)

    def test_raises_yield_out_of_range(self):
        with pytest.raises(ValueError):
            bioeconomy_phi_output(1.0, 1.0, 1.5)

    def test_raises_zero_scale(self):
        with pytest.raises(ValueError):
            bioeconomy_phi_output(1.0, 1.0, 0.5, scale_factor=0.0)
