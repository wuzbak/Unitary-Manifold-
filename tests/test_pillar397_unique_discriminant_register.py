# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Tests for Pillar 397 — Unique Discriminant Completeness Register.

Verifies the 28-parameter discriminant register, discriminant power metric,
unique discriminant signature, and the machine-readable pillar status interface.
"""

import pytest

from src.core.pillar397_unique_discriminant_register import (
    DiscriminantClass,
    PredictionRecord,
    DISCRIMINANT_REGISTER,
    discriminant_power,
    unique_discriminant_signature,
    discriminant_register_report,
    pillar_397_status,
)


# ──────────────────────────────────────────────────────────────────────────────
# Register structure
# ──────────────────────────────────────────────────────────────────────────────

class TestRegisterStructure:

    def test_total_prediction_count(self):
        assert len(DISCRIMINANT_REGISTER) == 28, "Register must have exactly 28 predictions"

    def test_all_records_have_label(self):
        for r in DISCRIMINANT_REGISTER:
            assert r.label, f"Record missing label: {r.name}"

    def test_all_records_have_name(self):
        for r in DISCRIMINANT_REGISTER:
            assert r.name, f"Record has empty name"

    def test_all_records_have_um_prediction(self):
        for r in DISCRIMINANT_REGISTER:
            assert r.um_prediction, f"Record '{r.label}' missing UM prediction"

    def test_all_records_have_pdg_reference(self):
        for r in DISCRIMINANT_REGISTER:
            assert r.pdg_or_observed, f"Record '{r.label}' missing PDG/observed reference"

    def test_all_records_have_discriminant_class(self):
        valid_classes = set(DiscriminantClass)
        for r in DISCRIMINANT_REGISTER:
            assert r.discriminant_class in valid_classes

    def test_all_records_have_uniqueness_argument(self):
        for r in DISCRIMINANT_REGISTER:
            assert len(r.uniqueness_argument) >= 20, (
                f"Record '{r.label}' has too short a uniqueness argument"
            )

    def test_all_records_have_citation(self):
        for r in DISCRIMINANT_REGISTER:
            assert r.citation, f"Record '{r.label}' missing citation"

    def test_labels_are_unique(self):
        labels = [r.label for r in DISCRIMINANT_REGISTER]
        assert len(labels) == len(set(labels)), "Duplicate labels in register"

    def test_labels_p1_to_p28(self):
        expected = {f"P{i}" for i in range(1, 29)}
        actual = {r.label for r in DISCRIMINANT_REGISTER}
        assert actual == expected, f"Missing or extra labels: {expected.symmetric_difference(actual)}"

    def test_free_parameters_nonnegative(self):
        for r in DISCRIMINANT_REGISTER:
            assert r.free_parameters_used >= 0

    def test_alternatives_is_list(self):
        for r in DISCRIMINANT_REGISTER:
            assert isinstance(r.alternatives, list)


# ──────────────────────────────────────────────────────────────────────────────
# Specific prediction checks
# ──────────────────────────────────────────────────────────────────────────────

class TestSpecificPredictions:

    def _get(self, label: str) -> PredictionRecord:
        match = [r for r in DISCRIMINANT_REGISTER if r.label == label]
        assert match, f"Record '{label}' not found in register"
        return match[0]

    def test_p1_ns_uniquely_discriminating(self):
        r = self._get("P1")
        assert r.discriminant_class == DiscriminantClass.UNIQUELY_DISCRIMINATING
        assert r.free_parameters_used == 0

    def test_p2_r_uniquely_discriminating(self):
        r = self._get("P2")
        assert r.discriminant_class == DiscriminantClass.UNIQUELY_DISCRIMINATING
        assert r.free_parameters_used == 0

    def test_p2_mentions_act_tension(self):
        r = self._get("P2")
        assert "ACT" in r.pdg_or_observed or "TENSION" in r.pdg_or_observed.upper()

    def test_p11_lambda_qcd_uniquely_discriminating(self):
        r = self._get("P11")
        assert r.discriminant_class == DiscriminantClass.UNIQUELY_DISCRIMINATING
        assert r.free_parameters_used == 0

    def test_p12_proton_electron_mass_ratio_unique(self):
        r = self._get("P12")
        assert r.discriminant_class == DiscriminantClass.UNIQUELY_DISCRIMINATING
        assert r.free_parameters_used == 0

    def test_p21_birefringence_uniquely_discriminating(self):
        r = self._get("P21")
        assert r.discriminant_class == DiscriminantClass.UNIQUELY_DISCRIMINATING
        assert r.free_parameters_used == 0

    def test_p21_mentions_litebird(self):
        r = self._get("P21")
        assert "LiteBIRD" in r.uniqueness_argument or "LiteBIRD" in r.pdg_or_observed

    def test_p5_higgs_mass_consistency_only(self):
        r = self._get("P5")
        # m_H requires λ_GW (free parameter) → should not be UNIQUELY_DISCRIMINATING.
        assert r.discriminant_class != DiscriminantClass.UNIQUELY_DISCRIMINATING
        assert r.free_parameters_used >= 1

    def test_p23_w0_shared(self):
        r = self._get("P23")
        # w₀ = −1 is shared with ΛCDM.
        assert r.discriminant_class == DiscriminantClass.SHARED_WITH_ALTERNATIVES

    def test_p24_wa_uniquely_discriminating(self):
        r = self._get("P24")
        # wₐ = 0 is the firm prediction that differs from dynamical DE models.
        assert r.discriminant_class == DiscriminantClass.UNIQUELY_DISCRIMINATING

    def test_p24_mentions_desi_tension(self):
        r = self._get("P24")
        assert "DESI" in r.pdg_or_observed or "TENSION" in r.pdg_or_observed.upper()

    def test_p28_holographic_shared(self):
        r = self._get("P28")
        assert r.discriminant_class == DiscriminantClass.SHARED_WITH_ALTERNATIVES

    def test_p14_ckm_lambda_zero_free_params(self):
        r = self._get("P14")
        assert r.free_parameters_used == 0
        assert r.discriminant_class == DiscriminantClass.UNIQUELY_DISCRIMINATING

    def test_p27_neutrino_mass_uniquely_discriminating(self):
        r = self._get("P27")
        assert r.discriminant_class == DiscriminantClass.UNIQUELY_DISCRIMINATING


# ──────────────────────────────────────────────────────────────────────────────
# Discriminant power metric
# ──────────────────────────────────────────────────────────────────────────────

class TestDiscriminantPower:

    def test_power_returns_dict(self):
        power = discriminant_power()
        assert isinstance(power, dict)

    def test_power_total_is_28(self):
        power = discriminant_power()
        assert power["total_predictions"] == 28

    def test_power_counts_sum_to_total(self):
        power = discriminant_power()
        total = (
            power["uniquely_discriminating_count"]
            + power["shared_with_alternatives_count"]
            + power["consistency_only_count"]
        )
        assert total == 28

    def test_power_fraction_in_range(self):
        power = discriminant_power()
        frac = power["discriminant_power_fraction"]
        assert 0.0 <= frac <= 1.0

    def test_power_fraction_above_0_4(self):
        # At least 40% of predictions should be uniquely discriminating.
        power = discriminant_power()
        assert power["discriminant_power_fraction"] >= 0.40, (
            "UM should have ≥40% uniquely discriminating predictions"
        )

    def test_zero_fp_unique_count_nonzero(self):
        power = discriminant_power()
        assert power["zero_free_param_unique_count"] >= 5, (
            "Must have at least 5 zero-free-parameter uniquely discriminating predictions"
        )

    def test_zero_fp_unique_labels_all_labeled(self):
        power = discriminant_power()
        for label in power["zero_free_param_unique_labels"]:
            assert label.startswith("P"), f"Label '{label}' should start with P"

    def test_power_pct_string_format(self):
        power = discriminant_power()
        assert "%" in power["discriminant_power_pct"]

    def test_uniquely_discriminating_count_at_least_10(self):
        power = discriminant_power()
        assert power["uniquely_discriminating_count"] >= 10


# ──────────────────────────────────────────────────────────────────────────────
# Unique discriminant signature
# ──────────────────────────────────────────────────────────────────────────────

class TestUniqueDiscriminantSignature:

    def test_signature_returns_dict(self):
        sig = unique_discriminant_signature()
        assert isinstance(sig, dict)

    def test_signature_count_positive(self):
        sig = unique_discriminant_signature()
        assert sig["signature_prediction_count"] >= 5

    def test_signature_labels_all_in_register(self):
        sig = unique_discriminant_signature()
        register_labels = {r.label for r in DISCRIMINANT_REGISTER}
        for label in sig["signature_labels"]:
            assert label in register_labels

    def test_signature_predictions_have_required_fields(self):
        sig = unique_discriminant_signature()
        for pred in sig["signature_predictions"]:
            assert "label" in pred
            assert "name" in pred
            assert "value" in pred

    def test_signature_statement_nonempty(self):
        sig = unique_discriminant_signature()
        assert len(sig["signature_statement"]) >= 100

    def test_signature_statement_mentions_litebird(self):
        sig = unique_discriminant_signature()
        assert "LiteBIRD" in sig["signature_statement"]

    def test_signature_mentions_primary_falsifier(self):
        sig = unique_discriminant_signature()
        pf = sig["primary_falsifier"]
        assert "LiteBIRD" in pf or "birefringence" in pf.lower() or "β" in pf

    def test_signature_active_tensions(self):
        sig = unique_discriminant_signature()
        tensions = sig["active_tension_predictions"]
        assert isinstance(tensions, list)
        assert len(tensions) >= 2

    def test_birefringence_in_signature(self):
        sig = unique_discriminant_signature()
        labels = set(sig["signature_labels"])
        # P21 or P22 (birefringence) must be in the unique signature.
        assert "P21" in labels or "P22" in labels, (
            "Birefringence prediction must be in the unique discriminant signature"
        )

    def test_lambda_qcd_in_signature(self):
        sig = unique_discriminant_signature()
        labels = set(sig["signature_labels"])
        assert "P11" in labels, "Λ_QCD (P11) must be in unique signature (zero free parameters)"

    def test_ns_in_signature(self):
        sig = unique_discriminant_signature()
        labels = set(sig["signature_labels"])
        assert "P1" in labels, "nₛ (P1) must be in unique signature (zero free parameters)"


# ──────────────────────────────────────────────────────────────────────────────
# Full register report
# ──────────────────────────────────────────────────────────────────────────────

class TestFullReport:

    def test_report_structure(self):
        report = discriminant_register_report()
        required_keys = [
            "pillar", "title", "version", "total_predictions",
            "discriminant_power", "unique_signature", "by_class", "register",
        ]
        for key in required_keys:
            assert key in report, f"Missing '{key}' in report"

    def test_report_pillar_number(self):
        report = discriminant_register_report()
        assert report["pillar"] == 397

    def test_report_version(self):
        report = discriminant_register_report()
        assert "12.9" in report["version"]

    def test_report_total_predictions_28(self):
        report = discriminant_register_report()
        assert report["total_predictions"] == 28

    def test_report_by_class_has_three_entries(self):
        report = discriminant_register_report()
        assert "UNIQUELY_DISCRIMINATING" in report["by_class"]
        assert "SHARED_WITH_ALTERNATIVES" in report["by_class"]
        assert "CONSISTENCY_ONLY" in report["by_class"]

    def test_report_by_class_counts_sum_to_28(self):
        report = discriminant_register_report()
        total = sum(len(v) for v in report["by_class"].values())
        assert total == 28

    def test_report_register_length(self):
        report = discriminant_register_report()
        assert len(report["register"]) == 28

    def test_report_register_records_have_fields(self):
        report = discriminant_register_report()
        for entry in report["register"]:
            assert "label" in entry
            assert "name" in entry
            assert "class" in entry
            assert "free_parameters" in entry


# ──────────────────────────────────────────────────────────────────────────────
# Pillar status interface
# ──────────────────────────────────────────────────────────────────────────────

class TestPillarStatus:

    def test_status_returns_dict(self):
        assert isinstance(pillar_397_status(), dict)

    def test_status_pillar_field(self):
        assert pillar_397_status()["pillar"] == "397"

    def test_status_name_field(self):
        status = pillar_397_status()
        assert "Discriminant" in status["name"]

    def test_status_total_28(self):
        status = pillar_397_status()
        assert int(status["total_predictions"]) == 28

    def test_status_discriminant_power_pct_has_percent(self):
        status = pillar_397_status()
        assert "%" in status["discriminant_power_pct"]

    def test_status_zero_fp_unique_positive(self):
        status = pillar_397_status()
        assert int(status["zero_fp_unique"]) >= 5

    def test_status_signature_count_positive(self):
        status = pillar_397_status()
        assert int(status["signature_count"]) >= 5

    def test_status_uniquely_discriminating_ge_10(self):
        status = pillar_397_status()
        assert int(status["uniquely_discriminating"]) >= 10

    def test_status_counts_sum_to_28(self):
        status = pillar_397_status()
        total = (
            int(status["uniquely_discriminating"])
            + int(status["shared"])
            + int(status["consistency_only"])
        )
        assert total == 28
