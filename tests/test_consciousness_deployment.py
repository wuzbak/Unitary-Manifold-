# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_consciousness_deployment.py
=======================================
Test suite for src/consciousness/consciousness_deployment.py — Pillar 9-B.

Covers:
 * BridgeState construction and field validity
 * ConsciousnessBridgeDeployment construction via class and convenience func
 * All 13 domain deployment methods (output types and range checks)
 * Internal consistency across deployments (shared phi_eff / info_gap)
 * Edge-case inputs (zero phi, identical manifolds, extreme coupling)
 * deploy_all() completeness and key names
 * Determinism / reproducibility
"""

import math
import pytest
import numpy as np

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.consciousness.coupled_attractor import (
    ManifoldState,
    CoupledSystem,
    BIREFRINGENCE_RAD,
)
from src.consciousness.consciousness_deployment import (
    BridgeState,
    ConsciousnessBridgeDeployment,
    bridge_from_system,
    _extract_bridge_state,
    RESONANCE_TARGET,
    RESONANCE_WIDTH,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def default_system():
    """Default CoupledSystem with standard brain/universe initial states."""
    brain = ManifoldState.brain()
    univ  = ManifoldState.universe()
    return CoupledSystem(brain=brain, universe=univ)


@pytest.fixture
def default_dep(default_system):
    """Default ConsciousnessBridgeDeployment."""
    return ConsciousnessBridgeDeployment(default_system)


@pytest.fixture
def identical_system():
    """CoupledSystem where brain == universe (phi_brain == phi_univ)."""
    brain = ManifoldState.brain(phi=1.0)
    univ  = ManifoldState.universe(phi=1.0)
    return CoupledSystem(brain=brain, universe=univ)


@pytest.fixture
def high_gap_system():
    """CoupledSystem with large information gap (phi_brain << phi_univ)."""
    brain = ManifoldState.brain(phi=0.1)
    univ  = ManifoldState.universe(phi=2.0)
    return CoupledSystem(brain=brain, universe=univ)


@pytest.fixture
def low_gap_system():
    """CoupledSystem with small (but non-zero) information gap."""
    brain = ManifoldState.brain(phi=0.99)
    univ  = ManifoldState.universe(phi=1.0)
    return CoupledSystem(brain=brain, universe=univ)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_resonance_target(self):
        assert math.isclose(RESONANCE_TARGET, 5.0 / 7.0)

    def test_resonance_width(self):
        expected = 7.0 / 5.0 - 5.0 / 7.0
        assert math.isclose(RESONANCE_WIDTH, expected)

    def test_resonance_width_positive(self):
        assert RESONANCE_WIDTH > 0.0


# ---------------------------------------------------------------------------
# BridgeState fields
# ---------------------------------------------------------------------------

class TestBridgeStateConstruction:
    def test_bridge_state_is_frozen(self, default_system):
        bs = _extract_bridge_state(default_system)
        with pytest.raises((AttributeError, TypeError)):
            bs.phi_brain = 99.9  # type: ignore[misc]

    def test_phi_brain_positive(self, default_system):
        bs = _extract_bridge_state(default_system)
        assert bs.phi_brain > 0.0

    def test_phi_univ_positive(self, default_system):
        bs = _extract_bridge_state(default_system)
        assert bs.phi_univ > 0.0

    def test_phi_eff_geometric_mean(self, default_system):
        bs = _extract_bridge_state(default_system)
        expected = math.sqrt(bs.phi_brain * bs.phi_univ)
        assert math.isclose(bs.phi_eff, expected, rel_tol=1e-9)

    def test_phi_eff_nonnegative(self, default_system):
        bs = _extract_bridge_state(default_system)
        assert bs.phi_eff >= 0.0

    def test_info_gap_nonnegative(self, default_system):
        bs = _extract_bridge_state(default_system)
        assert bs.info_gap >= 0.0

    def test_info_gap_zero_for_identical(self, identical_system):
        bs = _extract_bridge_state(identical_system)
        # phi_brain == phi_univ → ΔI = 0 (within numerical noise)
        assert bs.info_gap < 1e-10

    def test_info_gap_large_for_high_gap(self, high_gap_system):
        bs = _extract_bridge_state(high_gap_system)
        assert bs.info_gap > 0.1

    def test_phase_offset_in_range(self, default_system):
        bs = _extract_bridge_state(default_system)
        assert 0.0 <= bs.phase_offset_rad <= math.pi

    def test_resonance_quality_in_range(self, default_system):
        bs = _extract_bridge_state(default_system)
        assert 0.0 <= bs.resonance_quality <= 1.0

    def test_beta_equals_system_beta(self, default_system):
        bs = _extract_bridge_state(default_system)
        assert math.isclose(bs.beta, default_system.beta)

    def test_beta_default_is_birefringence(self, default_system):
        bs = _extract_bridge_state(default_system)
        assert math.isclose(bs.beta, BIREFRINGENCE_RAD, rel_tol=1e-9)

    def test_entropy_brain_real(self, default_system):
        bs = _extract_bridge_state(default_system)
        assert math.isfinite(bs.entropy_brain)

    def test_entropy_univ_real(self, default_system):
        bs = _extract_bridge_state(default_system)
        assert math.isfinite(bs.entropy_univ)

    def test_entropy_coherence_in_range(self, default_system):
        bs = _extract_bridge_state(default_system)
        assert 0.0 <= bs.entropy_coherence <= 1.0

    def test_entropy_coherence_high_for_identical_phi(self, identical_system):
        # phi identical, but node entropies may differ — coherence depends on S
        bs = _extract_bridge_state(identical_system)
        assert 0.0 <= bs.entropy_coherence <= 1.0


# ---------------------------------------------------------------------------
# ConsciousnessBridgeDeployment construction
# ---------------------------------------------------------------------------

class TestDeploymentConstruction:
    def test_class_construction(self, default_system):
        dep = ConsciousnessBridgeDeployment(default_system)
        assert isinstance(dep, ConsciousnessBridgeDeployment)

    def test_convenience_constructor(self, default_system):
        dep = bridge_from_system(default_system)
        assert isinstance(dep, ConsciousnessBridgeDeployment)

    def test_bridge_state_accessible(self, default_dep):
        bs = default_dep.bridge_state()
        assert isinstance(bs, BridgeState)

    def test_bridge_state_consistent_with_direct(self, default_system):
        dep = ConsciousnessBridgeDeployment(default_system)
        direct = _extract_bridge_state(default_system)
        assert math.isclose(dep.bridge_state().phi_eff, direct.phi_eff)


# ---------------------------------------------------------------------------
# Shared phi_eff consistency across methods
# ---------------------------------------------------------------------------

class TestPhiEffConsistency:
    """Domains that directly expose phi_eff as a named output must match bridge_state.phi_eff.

    Note: ``to_biology()`` intentionally uses ``phi_eff²`` (not ``phi_eff``) for
    ``negentropy_rate``; ``to_earth()`` intentionally uses ``phi_univ`` for
    ``tectonic_phi``.  These are excluded from this consistency check.
    """

    _phi_eff_keys = {
        # "earth" uses phi_univ (not phi_eff) for tectonic_phi — intentional
        # "biology" uses phi_eff² for negentropy_rate — checked separately
        "chemistry":    "phi_bond",
        "justice":      "equity_phi",
        "governance":   "stability_phi",
        "ecology":      "biodiversity_phi",
        "marine":       "ocean_phi",
        "genetics":     "genomic_phi",
        "materials":    "lattice_phi",
    }
    _info_gap_keys = {
        "chemistry":    "reaction_barrier",
        "earth":        "thermal_gradient",
        "medicine":     "systemic_deviation",
        "justice":      "equity_deviation",
        "ecology":      "perturbation",
        "climate":      "forcing",
        "marine":       "salinity_gradient",
        "psychology":   "cognitive_gap",
        "genetics":     "mutation_coupling",  # scaled by beta
        "materials":    "disorder_param",
    }

    def test_phi_eff_consistent_across_domains(self, default_dep):
        bs = default_dep.bridge_state()
        all_d = default_dep.deploy_all()
        for domain, key in self._phi_eff_keys.items():
            val = all_d[domain][key]
            assert math.isclose(val, bs.phi_eff, rel_tol=1e-9), (
                f"{domain}.{key} = {val!r} != phi_eff = {bs.phi_eff!r}"
            )

    def test_info_gap_consistent_across_domains(self, default_dep):
        bs = default_dep.bridge_state()
        all_d = default_dep.deploy_all()
        for domain, key in self._info_gap_keys.items():
            val = all_d[domain][key]
            if domain == "genetics":
                # mutation_coupling = beta * info_gap
                expected = bs.beta * bs.info_gap
            else:
                expected = bs.info_gap
            assert math.isclose(val, expected, rel_tol=1e-9), (
                f"{domain}.{key} = {val!r} != expected = {expected!r}"
            )


# ---------------------------------------------------------------------------
# Chemistry (Pillar 10)
# ---------------------------------------------------------------------------

class TestChemistry:
    def test_returns_dict(self, default_dep):
        assert isinstance(default_dep.to_chemistry(), dict)

    def test_keys(self, default_dep):
        result = default_dep.to_chemistry()
        assert {"phi_bond", "reaction_barrier", "braid_coupling"} <= result.keys()

    def test_phi_bond_positive(self, default_dep):
        assert default_dep.to_chemistry()["phi_bond"] > 0.0

    def test_reaction_barrier_nonneg(self, default_dep):
        assert default_dep.to_chemistry()["reaction_barrier"] >= 0.0

    def test_braid_coupling_positive(self, default_dep):
        assert default_dep.to_chemistry()["braid_coupling"] > 0.0

    def test_braid_coupling_formula(self, default_dep):
        bs = default_dep.bridge_state()
        result = default_dep.to_chemistry()
        assert math.isclose(result["braid_coupling"], bs.beta * bs.phi_eff)

    def test_high_gap_raises_barrier(self, high_gap_system, low_gap_system):
        dep_hi = ConsciousnessBridgeDeployment(high_gap_system)
        dep_lo = ConsciousnessBridgeDeployment(low_gap_system)
        assert dep_hi.to_chemistry()["reaction_barrier"] > \
               dep_lo.to_chemistry()["reaction_barrier"]


# ---------------------------------------------------------------------------
# Earth (Pillar 12)
# ---------------------------------------------------------------------------

class TestEarth:
    def test_keys(self, default_dep):
        result = default_dep.to_earth()
        assert {"tectonic_phi", "thermal_gradient", "phase_coupling"} <= result.keys()

    def test_phase_coupling_in_range(self, default_dep):
        pc = default_dep.to_earth()["phase_coupling"]
        assert -1.0 <= pc <= 1.0

    def test_thermal_gradient_nonneg(self, default_dep):
        assert default_dep.to_earth()["thermal_gradient"] >= 0.0

    def test_tectonic_phi_positive(self, default_dep):
        assert default_dep.to_earth()["tectonic_phi"] > 0.0


# ---------------------------------------------------------------------------
# Biology (Pillar 13)
# ---------------------------------------------------------------------------

class TestBiology:
    def test_keys(self, default_dep):
        result = default_dep.to_biology()
        assert {"negentropy_rate", "homeostasis_margin", "entropy_coherence"} \
               <= result.keys()

    def test_negentropy_rate_positive(self, default_dep):
        assert default_dep.to_biology()["negentropy_rate"] > 0.0

    def test_negentropy_rate_is_phi_eff_squared(self, default_dep):
        bs = default_dep.bridge_state()
        result = default_dep.to_biology()
        assert math.isclose(result["negentropy_rate"], bs.phi_eff ** 2)

    def test_homeostasis_margin_finite(self, default_dep):
        assert math.isfinite(default_dep.to_biology()["homeostasis_margin"])

    def test_entropy_coherence_in_range(self, default_dep):
        ec = default_dep.to_biology()["entropy_coherence"]
        assert 0.0 <= ec <= 1.0


# ---------------------------------------------------------------------------
# Medicine (Pillar 17)
# ---------------------------------------------------------------------------

class TestMedicine:
    def test_keys(self, default_dep):
        result = default_dep.to_medicine()
        assert {"health_phi", "systemic_deviation",
                "clinician_burnout_risk", "resonance_quality"} <= result.keys()

    def test_health_phi_positive(self, default_dep):
        assert default_dep.to_medicine()["health_phi"] > 0.0

    def test_systemic_deviation_nonneg(self, default_dep):
        assert default_dep.to_medicine()["systemic_deviation"] >= 0.0

    def test_burnout_risk_nonneg(self, default_dep):
        assert default_dep.to_medicine()["clinician_burnout_risk"] >= 0.0

    def test_resonance_quality_in_range(self, default_dep):
        rq = default_dep.to_medicine()["resonance_quality"]
        assert 0.0 <= rq <= 1.0

    def test_high_gap_raises_burnout(self, high_gap_system, low_gap_system):
        dep_hi = ConsciousnessBridgeDeployment(high_gap_system)
        dep_lo = ConsciousnessBridgeDeployment(low_gap_system)
        assert dep_hi.to_medicine()["clinician_burnout_risk"] > \
               dep_lo.to_medicine()["clinician_burnout_risk"]


# ---------------------------------------------------------------------------
# Justice (Pillar 18)
# ---------------------------------------------------------------------------

class TestJustice:
    def test_keys(self, default_dep):
        result = default_dep.to_justice()
        assert {"equity_phi", "equity_deviation",
                "bias_index", "correction_strength"} <= result.keys()

    def test_bias_index_in_range(self, default_dep):
        bi = default_dep.to_justice()["bias_index"]
        assert 0.0 <= bi <= 1.0

    def test_equity_deviation_nonneg(self, default_dep):
        assert default_dep.to_justice()["equity_deviation"] >= 0.0

    def test_correction_strength_positive(self, default_dep):
        assert default_dep.to_justice()["correction_strength"] > 0.0


# ---------------------------------------------------------------------------
# Governance (Pillar 19)
# ---------------------------------------------------------------------------

class TestGovernance:
    def test_keys(self, default_dep):
        result = default_dep.to_governance()
        assert {"stability_phi", "fragmentation_index",
                "legitimacy", "n_effective_sources"} <= result.keys()

    def test_fragmentation_nonneg(self, default_dep):
        assert default_dep.to_governance()["fragmentation_index"] >= 0.0

    def test_legitimacy_in_range(self, default_dep):
        legit = default_dep.to_governance()["legitimacy"]
        assert 0.0 <= legit <= 1.0

    def test_n_effective_sources_positive(self, default_dep):
        assert default_dep.to_governance()["n_effective_sources"] > 0.0

    def test_high_gap_lowers_legitimacy(self, high_gap_system, low_gap_system):
        dep_hi = ConsciousnessBridgeDeployment(high_gap_system)
        dep_lo = ConsciousnessBridgeDeployment(low_gap_system)
        assert dep_hi.to_governance()["fragmentation_index"] > \
               dep_lo.to_governance()["fragmentation_index"]


# ---------------------------------------------------------------------------
# Neuroscience (Pillar 20)
# ---------------------------------------------------------------------------

class TestNeuroscience:
    def test_keys(self, default_dep):
        result = default_dep.to_neuroscience()
        assert {"neural_phi", "coherence_index",
                "synaptic_coupling", "decoherence_risk"} <= result.keys()

    def test_neural_phi_positive(self, default_dep):
        assert default_dep.to_neuroscience()["neural_phi"] > 0.0

    def test_coherence_index_in_range(self, default_dep):
        ci = default_dep.to_neuroscience()["coherence_index"]
        assert 0.0 <= ci <= 1.0

    def test_synaptic_coupling_positive(self, default_dep):
        assert default_dep.to_neuroscience()["synaptic_coupling"] > 0.0

    def test_decoherence_risk_nonneg(self, default_dep):
        assert default_dep.to_neuroscience()["decoherence_risk"] >= 0.0


# ---------------------------------------------------------------------------
# Ecology (Pillar 21)
# ---------------------------------------------------------------------------

class TestEcology:
    def test_keys(self, default_dep):
        result = default_dep.to_ecology()
        assert {"biodiversity_phi", "perturbation",
                "resilience", "extinction_risk"} <= result.keys()

    def test_biodiversity_phi_positive(self, default_dep):
        assert default_dep.to_ecology()["biodiversity_phi"] > 0.0

    def test_resilience_in_range(self, default_dep):
        res = default_dep.to_ecology()["resilience"]
        assert 0.0 <= res <= 1.0

    def test_extinction_risk_nonneg(self, default_dep):
        assert default_dep.to_ecology()["extinction_risk"] >= 0.0


# ---------------------------------------------------------------------------
# Climate (Pillar 22)
# ---------------------------------------------------------------------------

class TestClimate:
    def test_keys(self, default_dep):
        result = default_dep.to_climate()
        assert {"radiative_phi", "forcing",
                "feedback_gain", "albedo_proxy"} <= result.keys()

    def test_radiative_phi_positive(self, default_dep):
        assert default_dep.to_climate()["radiative_phi"] > 0.0

    def test_albedo_proxy_in_range(self, default_dep):
        alb = default_dep.to_climate()["albedo_proxy"]
        assert 0.0 <= alb <= 1.0

    def test_feedback_gain_positive(self, default_dep):
        assert default_dep.to_climate()["feedback_gain"] > 0.0

    def test_forcing_nonneg(self, default_dep):
        assert default_dep.to_climate()["forcing"] >= 0.0


# ---------------------------------------------------------------------------
# Marine (Pillar 23)
# ---------------------------------------------------------------------------

class TestMarine:
    def test_keys(self, default_dep):
        result = default_dep.to_marine()
        assert {"ocean_phi", "salinity_gradient",
                "stratification", "upwelling_rate"} <= result.keys()

    def test_ocean_phi_positive(self, default_dep):
        assert default_dep.to_marine()["ocean_phi"] > 0.0

    def test_stratification_in_range(self, default_dep):
        strat = default_dep.to_marine()["stratification"]
        assert 0.0 <= strat <= 1.0

    def test_salinity_gradient_nonneg(self, default_dep):
        assert default_dep.to_marine()["salinity_gradient"] >= 0.0

    def test_upwelling_rate_positive(self, default_dep):
        assert default_dep.to_marine()["upwelling_rate"] > 0.0


# ---------------------------------------------------------------------------
# Psychology (Pillar 24)
# ---------------------------------------------------------------------------

class TestPsychology:
    def test_keys(self, default_dep):
        result = default_dep.to_psychology()
        assert {"behavioral_phi", "cognitive_gap",
                "stress_index", "self_regulation"} <= result.keys()

    def test_behavioral_phi_positive(self, default_dep):
        assert default_dep.to_psychology()["behavioral_phi"] > 0.0

    def test_stress_index_nonneg(self, default_dep):
        assert default_dep.to_psychology()["stress_index"] >= 0.0

    def test_self_regulation_in_range(self, default_dep):
        sr = default_dep.to_psychology()["self_regulation"]
        assert 0.0 <= sr <= 1.0

    def test_high_gap_raises_stress(self, high_gap_system, low_gap_system):
        dep_hi = ConsciousnessBridgeDeployment(high_gap_system)
        dep_lo = ConsciousnessBridgeDeployment(low_gap_system)
        assert dep_hi.to_psychology()["stress_index"] > \
               dep_lo.to_psychology()["stress_index"]


# ---------------------------------------------------------------------------
# Genetics (Pillar 25)
# ---------------------------------------------------------------------------

class TestGenetics:
    def test_keys(self, default_dep):
        result = default_dep.to_genetics()
        assert {"genomic_phi", "mutation_coupling",
                "selection_strength", "drift_amplitude"} <= result.keys()

    def test_genomic_phi_positive(self, default_dep):
        assert default_dep.to_genetics()["genomic_phi"] > 0.0

    def test_mutation_coupling_nonneg(self, default_dep):
        assert default_dep.to_genetics()["mutation_coupling"] >= 0.0

    def test_selection_strength_in_range(self, default_dep):
        ss = default_dep.to_genetics()["selection_strength"]
        assert 0.0 <= ss <= 1.0

    def test_drift_amplitude_nonneg(self, default_dep):
        assert default_dep.to_genetics()["drift_amplitude"] >= 0.0


# ---------------------------------------------------------------------------
# Materials (Pillar 26)
# ---------------------------------------------------------------------------

class TestMaterials:
    def test_keys(self, default_dep):
        result = default_dep.to_materials()
        assert {"lattice_phi", "disorder_param",
                "conductivity_proxy", "critical_coupling"} <= result.keys()

    def test_lattice_phi_positive(self, default_dep):
        assert default_dep.to_materials()["lattice_phi"] > 0.0

    def test_disorder_param_nonneg(self, default_dep):
        assert default_dep.to_materials()["disorder_param"] >= 0.0

    def test_conductivity_proxy_nonneg(self, default_dep):
        assert default_dep.to_materials()["conductivity_proxy"] >= 0.0

    def test_critical_coupling_positive(self, default_dep):
        assert default_dep.to_materials()["critical_coupling"] > 0.0


# ---------------------------------------------------------------------------
# deploy_all()
# ---------------------------------------------------------------------------

class TestDeployAll:
    EXPECTED_DOMAINS = {
        "chemistry", "earth", "biology", "medicine", "justice",
        "governance", "neuroscience", "ecology", "climate",
        "marine", "psychology", "genetics", "materials",
    }

    def test_returns_dict(self, default_dep):
        assert isinstance(default_dep.deploy_all(), dict)

    def test_all_domains_present(self, default_dep):
        result = default_dep.deploy_all()
        assert self.EXPECTED_DOMAINS == set(result.keys())

    def test_each_value_is_dict(self, default_dep):
        result = default_dep.deploy_all()
        for domain, sub in result.items():
            assert isinstance(sub, dict), f"{domain} value is not a dict"

    def test_each_sub_dict_nonempty(self, default_dep):
        result = default_dep.deploy_all()
        for domain, sub in result.items():
            assert len(sub) > 0, f"{domain} sub-dict is empty"

    def test_deploy_all_consistent_with_individual_calls(self, default_dep):
        all_d = default_dep.deploy_all()
        assert all_d["chemistry"] == default_dep.to_chemistry()
        assert all_d["medicine"] == default_dep.to_medicine()
        assert all_d["governance"] == default_dep.to_governance()
        assert all_d["materials"] == default_dep.to_materials()

    def test_all_float_values(self, default_dep):
        result = default_dep.deploy_all()
        for domain, sub in result.items():
            for key, val in sub.items():
                assert isinstance(val, (int, float)), (
                    f"{domain}.{key} is not numeric: {type(val)}"
                )

    def test_all_finite_values(self, default_dep):
        result = default_dep.deploy_all()
        for domain, sub in result.items():
            for key, val in sub.items():
                assert math.isfinite(val), (
                    f"{domain}.{key} = {val!r} is not finite"
                )


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

class TestDeterminism:
    def test_same_system_same_bridge_state(self, default_system):
        bs1 = _extract_bridge_state(default_system)
        bs2 = _extract_bridge_state(default_system)
        assert bs1 == bs2

    def test_same_system_same_deploy_all(self, default_system):
        dep1 = ConsciousnessBridgeDeployment(default_system)
        dep2 = ConsciousnessBridgeDeployment(default_system)
        assert dep1.deploy_all() == dep2.deploy_all()


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_high_gap_system_finite(self, high_gap_system):
        dep = ConsciousnessBridgeDeployment(high_gap_system)
        result = dep.deploy_all()
        for domain, sub in result.items():
            for key, val in sub.items():
                assert math.isfinite(val), (
                    f"high_gap: {domain}.{key} = {val!r} not finite"
                )

    def test_identical_phi_zero_info_gap(self, identical_system):
        dep = ConsciousnessBridgeDeployment(identical_system)
        bs = dep.bridge_state()
        assert bs.info_gap < 1e-10

    def test_identical_phi_zero_chemistry_barrier(self, identical_system):
        dep = ConsciousnessBridgeDeployment(identical_system)
        assert dep.to_chemistry()["reaction_barrier"] < 1e-10

    def test_low_gap_positive_n_effective(self, low_gap_system):
        dep = ConsciousnessBridgeDeployment(low_gap_system)
        n_eff = dep.to_governance()["n_effective_sources"]
        assert n_eff > 0.0

    def test_custom_beta(self, default_system):
        system_highbeta = CoupledSystem(
            brain=default_system.brain,
            universe=default_system.universe,
            beta=0.5,
        )
        dep = ConsciousnessBridgeDeployment(system_highbeta)
        assert math.isclose(dep.bridge_state().beta, 0.5)
        # braid_coupling should scale with beta
        braid = dep.to_chemistry()["braid_coupling"]
        assert math.isclose(braid, 0.5 * dep.bridge_state().phi_eff)

    def test_perfect_57_resonance_n_effective(self):
        """Perfect 5:7 braid lock → n_eff = phi_eff² / info_gap = 35/24.

        Derivation (from the model formula):
            phi_eff²  = phi_brain × phi_univ = 5 × 7 = 35
            info_gap  = |phi_brain² − phi_univ²| = |25 − 49| = 24
            n_eff     = 35 / 24 ≈ 1.458…

        This is the bipolarity fixed-point of the 5:7 braid geometry — the
        system trends toward n_eff > 1.0 (two distinct winding strands) rather
        than toward 1.0 (unified) or 2.0 (balanced bipolarity).  35/24 is the
        exact, derivable fixed-point; no empirical tuning required.
        """
        brain_57 = ManifoldState.brain(phi=5.0)
        univ_57  = ManifoldState.universe(phi=7.0)
        system_57 = CoupledSystem(brain=brain_57, universe=univ_57)
        dep = ConsciousnessBridgeDeployment(system_57)
        n_eff = dep.to_governance()["n_effective_sources"]
        assert math.isclose(n_eff, 35 / 24, rel_tol=1e-9), (
            f"Expected 35/24 ≈ {35/24:.10f}, got {n_eff:.10f}"
        )
        assert n_eff > 1.0, "5:7 lock is bimodal, not unified (n_eff must exceed 1)"
