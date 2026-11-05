# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Exact finite-population checks for the exposed arithmetic audit."""

import hashlib
import json
from pathlib import Path
import shutil
import sys
from uuid import uuid4

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from src.infrastructure import research_quality_audit as audit  # noqa: E402


@pytest.fixture
def output_directory():
    path = ROOT / (".quality-audit-test-" + uuid4().hex)
    path.mkdir()
    try:
        yield path
    finally:
        shutil.rmtree(path)


def test_exact_counts_baselines_and_shift():
    report = audit.audit_arithmetic_protocol()
    assert report["enumerated_ordered_pairs"] == 100
    splits = report["splits"]
    assert [splits[s]["identity"]["examples"] for s in audit._SPLITS] == [60, 10, 30]
    for label in range(10):
        assert splits["train"]["answer_histogram"][str(label)] == 6
        assert splits["validation"]["answer_histogram"][str(label)] == (0 if label % 2 else 2)
        assert splits["test"]["answer_histogram"][str(label)] == (4 if label % 2 else 2)
    assert splits["validation"]["unseen_answer_labels_in_split"] == [1, 3, 5, 7, 9]
    assert splits["test"]["underrepresented_vs_uniform_answer_labels"] == [0, 2, 4, 6, 8]
    assert all(not splits[s]["answer_labels_unseen_in_training"] for s in audit._SPLITS)
    for split, operand_count in zip(audit._SPLITS, (6, 1, 3)):
        assert set(splits[split]["left_operand_histogram"].values()) == {operand_count}
        assert set(splits[split]["right_operand_histogram"].values()) == {operand_count}
        baseline = splits[split]["baselines"]
        assert baseline["uniform_random_digit_expected_accuracy"] == 0.1
        assert baseline["train_majority_selected_label"] == 0
        assert baseline["train_majority_accuracy"] == pytest.approx(
            {"train": 0.1, "validation": 0.2, "test": 1 / 15}[split]
        )
        assert baseline["train_histogram_random_guess_expected_accuracy"] == pytest.approx(0.1)
    shift = report["distribution_shift"]
    assert shift["answer_total_variation"] == pytest.approx({
        "train_vs_validation": 0.5, "train_vs_test": 1 / 6, "validation_vs_test": 2 / 3,
    })
    assert shift["train_test_split_answer_mutual_information_nats"] == pytest.approx(0.012692066792422244)


def test_overlap_identities_and_enumerated_mechanism():
    report = audit.audit_arithmetic_protocol()
    for comparison, reverse_count in (
        ("train_vs_validation", 10), ("train_vs_test", 30), ("validation_vs_test", 0),
    ):
        overlap = report["overlaps"][comparison]
        assert overlap["ordered_pair_overlap_count"] == 0
        assert len(overlap["reverse_pair_overlap_pairs_in_first_split"]) == reverse_count
        assert overlap["reverse_pair_overlap_count"] == reverse_count
        assert overlap["left_operand_overlap"] == list(range(10))
        assert overlap["right_operand_overlap"] == list(range(10))
    for split, left_minus_right in (("train", [0, 2, 3, 5, 6, 9]), ("validation", [8]), ("test", [1, 4, 7])):
        assert report["construction_diagnosis"]["modular_left_minus_right_by_split"][split] == left_minus_right
        for left, right in report["splits"][split]["ordered_pairs"]:
            residue = (7 * left + 3 * right) % 10
            assert residue == 7 * (left - right) % 10
            assert residue % 2 == (left + right) % 2
    assert report["construction_diagnosis"]["answer_parity_equals_residue_parity_for_all_100_pairs"]


def test_existing_scores_no_training_and_fail_closed(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("audit must not load, run, or train a model")
    for name in ("_p43_api", "train_reference_model", "_metrics", "load_model_artifact"):
        monkeypatch.setattr(audit.protocol, name, forbidden)
    report = audit.audit_arithmetic_protocol()
    evidence = report["existing_evidence"]
    assert evidence["report_whole_bytes_verified"]
    assert evidence["checkpoint_whole_bytes_verified"]
    scores = evidence["answer_scores"]["float64_native"]
    assert [scores[s]["answer_correct"] for s in audit._SPLITS] == [43, 0, 0]
    assert [scores[s]["examples"] for s in audit._SPLITS] == [60, 10, 30]
    assert report["execution_spine"]["promotion"]["eligible"] is False
    assert report["interpretation"]["causal_explanation_established"] is False
    assert report["interpretation"]["useful_model_evidence"] is False
    future = report["future_experiment_recommendation"]
    assert future["executed"] is False
    assert future["selection_budget"]["maximum_training_runs"] == 1
    assert future["predeclared_gate"]["minimum_correct_of_30"] == 30
    json.dumps(report, allow_nan=False)


def test_fixture_drift_rejected(monkeypatch):
    monkeypatch.setattr(audit.protocol, "_fixture", lambda: ([], {}))
    with pytest.raises(ValueError, match="fixture differs"):
        audit.audit_arithmetic_protocol()


def test_evidence_tampering_source_drift_and_size_bounds(monkeypatch):
    original = audit._read_bounded
    monkeypatch.setattr(
        audit, "_read_bounded",
        lambda path, limit: b"{}" if path.name == audit._EVIDENCE_SHA256 + ".json" else original(path, limit),
    )
    with pytest.raises(ValueError, match="whole-byte SHA-256"):
        audit.audit_arithmetic_protocol()
    monkeypatch.setattr(
        audit, "_read_bounded",
        lambda path, limit: b"changed" if path.name == "model.py" else original(path, limit),
    )
    with pytest.raises(ValueError, match="source identity"):
        audit.audit_arithmetic_protocol()
    monkeypatch.setattr(audit, "_read_bounded", original)
    monkeypatch.setattr(audit, "_MAX_REPORT_BYTES", 1)
    with pytest.raises(ValueError, match="size limit"):
        audit.audit_arithmetic_protocol()


def test_publication_is_whole_byte_hash_and_cli(output_directory, capsys):
    report = audit.audit_arithmetic_protocol(output_directory)
    again = audit.audit_arithmetic_protocol(output_directory)
    assert report == again
    assert len(list(output_directory.iterdir())) == 1
    path = next(output_directory.iterdir())
    assert hashlib.sha256(path.read_bytes()).hexdigest() == path.stem
    assert json.loads(path.read_bytes()) == report
    assert audit.main(["--output-dir", str(output_directory)]) == 0
    assert json.loads(capsys.readouterr().out)["sha256"] == path.stem
    with pytest.raises(ValueError, match="existing directory"):
        audit.audit_arithmetic_protocol(output_directory / "missing")
    with pytest.raises(ValueError, match="existing directory"):
        audit.audit_arithmetic_protocol(path)
