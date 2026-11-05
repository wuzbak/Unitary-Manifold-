# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Enumerate the exposed arithmetic protocol, without fitting or running a model.

This audit explains properties of the fixture, not the cause of model failure.
It preserves the published negative result and recommends a separate, future
experiment; neither the old test set nor this audit is independent validation.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from .artifact_io import publish_immutable
from .execution_spine import ExecutionSpineRecord, build_fail_closed_governance
from . import research_quantization as protocol

SCHEMA_VERSION = "az_arithmetic_protocol_audit_v1"
_ROOT = Path(__file__).resolve().parents[2]
_EVIDENCE_SHA256 = "abff87f2999f404fbdf2c40aa8dea8cc52bbd972e489dcabb0d360660918f3c4"
_EVIDENCE = (
    "9-INFRASTRUCTURE/az-ml-program/evidence/" + _EVIDENCE_SHA256 + ".json"
)
_SPLITS = ("train", "validation", "test")
_MAX_REPORT_BYTES = 1024 * 1024
_MAX_CHECKPOINT_BYTES = 64 * 1024 * 1024
_ARCHIVED_SOURCE_PATH = "src/infrastructure/artifact_io.py"
_ARCHIVED_SOURCE_SHA256 = "3dcf14855fd2a44ea3666f3a1a84036a9ad150a85f184cbe0403ca3c94284f2b"
_ARCHIVED_SOURCE = (
    "9-INFRASTRUCTURE/az-ml-program/evidence/" + _ARCHIVED_SOURCE_SHA256 + ".bin"
)


def _json_bytes(value: dict[str, Any]) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False,
    ).encode("ascii")


def _read_bounded(path: Path, limit: int) -> bytes:
    with path.open("rb") as stream:
        content = stream.read(limit + 1)
    if len(content) > limit:
        raise ValueError(f"{path.name} exceeds audit size limit")
    return content


def _identity(rows: list[str]) -> dict[str, Any]:
    content = "".join(rows).encode("ascii")
    return {
        "sha256": hashlib.sha256(content).hexdigest(),
        "examples": len(rows),
        "utf8_bytes": len(content),
    }


def _enumeration() -> tuple[list[str], dict[str, list[str]], dict[str, list[tuple[int, int, int, int]]]]:
    # Independently reconstruct every row, then require byte-for-byte agreement.
    rows: dict[str, list[str]] = {split: [] for split in _SPLITS}
    records: dict[str, list[tuple[int, int, int, int]]] = {split: [] for split in _SPLITS}
    for left in range(10):
        for right in range(10):
            residue = (7 * left + 3 * right) % 10
            split = "train" if residue <= 5 else "validation" if residue == 6 else "test"
            answer = (left + right) % 10
            rows[split].append(f"{left}+{right}={answer}\n")
            records[split].append((left, right, answer, residue))
    vocabulary = sorted("\n+=0123456789")
    actual_vocabulary, actual_rows = protocol._fixture()
    if actual_vocabulary != vocabulary or actual_rows != rows:
        raise ValueError("current fixture differs from the fixed enumerated protocol")
    return vocabulary, rows, records


def _verified_evidence(identities: dict[str, Any], vocabulary: list[str]) -> dict[str, Any]:
    content = _read_bounded(_ROOT / _EVIDENCE, _MAX_REPORT_BYTES)
    if hashlib.sha256(content).hexdigest() != _EVIDENCE_SHA256:
        raise ValueError("published evidence whole-byte SHA-256 mismatch")
    report = json.loads(content)
    fixture_digest = hashlib.sha256(_json_bytes(identities)).hexdigest()
    if (
        report["schema_version"] != protocol.SCHEMA_VERSION
        or report["data"]["splits"] != identities
        or report["data"]["fixture_sha256"] != fixture_digest
        or report["data"]["vocabulary"] != vocabulary
    ):
        raise ValueError("published evidence fixture identity mismatch")
    expected_paths = {*protocol._IMPLEMENTATION_SOURCE_PATHS, *protocol._P43_SOURCE_PATHS}
    source_hashes = report["model"]["source_sha256"]
    if set(source_hashes) != expected_paths:
        raise ValueError("published source manifest mismatch")
    verified_sources = {}
    source_bindings = {}
    for relative in sorted(expected_paths):
        digest = hashlib.sha256(_read_bounded(_ROOT / relative, _MAX_REPORT_BYTES)).hexdigest()
        if relative == _ARCHIVED_SOURCE_PATH:
            if source_hashes[relative] != _ARCHIVED_SOURCE_SHA256:
                raise ValueError("published archived source manifest identity mismatch")
            try:
                archived = _read_bounded(_ROOT / _ARCHIVED_SOURCE, _MAX_REPORT_BYTES)
            except FileNotFoundError as exc:
                raise ValueError("required historical source archive is missing") from exc
            if hashlib.sha256(archived).hexdigest() != _ARCHIVED_SOURCE_SHA256:
                raise ValueError("historical source archive SHA-256 mismatch")
            source_bindings[relative] = {
                "binding": "hash_verified_historical_archive_not_current_source",
                "published_source_sha256": _ARCHIVED_SOURCE_SHA256,
                "archive_path": _ARCHIVED_SOURCE,
                "archive_sha256_verified": _ARCHIVED_SOURCE_SHA256,
                "current_source_sha256": digest,
                "current_matches_published_source": digest == _ARCHIVED_SOURCE_SHA256,
                "current_source_safety_assessed": False,
            }
            continue
        if digest != source_hashes[relative]:
            raise ValueError(f"published source identity mismatch: {relative}")
        verified_sources[relative] = digest
        source_bindings[relative] = {
            "binding": "hash_verified_current_source",
            "published_source_sha256": digest,
            "current_source_sha256": digest,
            "current_matches_published_source": True,
        }
    checkpoint = report["trained_checkpoint"]
    checkpoint_digest = checkpoint["sha256"]
    if (
        not checkpoint["published"]
        or checkpoint["filename"] != checkpoint_digest + ".npz"
        or len(checkpoint_digest) != 64
        or any(character not in "0123456789abcdef" for character in checkpoint_digest)
    ):
        raise ValueError("invalid published checkpoint identity")
    checkpoint_bytes = _read_bounded(
        (_ROOT / _EVIDENCE).parent / checkpoint["filename"], _MAX_CHECKPOINT_BYTES,
    )
    if (
        len(checkpoint_bytes) != checkpoint["bytes"]
        or hashlib.sha256(checkpoint_bytes).hexdigest() != checkpoint_digest
    ):
        raise ValueError("published checkpoint whole-byte identity mismatch")
    scores = {}
    for variant, evaluation in report["evaluations"].items():
        scores[variant] = {}
        for split in _SPLITS:
            metrics = evaluation["metrics"][split]
            accuracy = metrics["answer_digit_accuracy"]
            cross_entropy = metrics["answer_digit_cross_entropy_nats"]
            n = identities[split]["examples"]
            if (
                type(accuracy) not in (int, float) or not math.isfinite(accuracy)
                or not 0 <= accuracy <= 1
                or not math.isclose(accuracy * n, round(accuracy * n), abs_tol=1e-10)
                or type(cross_entropy) not in (int, float)
                or not math.isfinite(cross_entropy) or cross_entropy < 0
                or metrics["tokens"] != 5 * n
            ):
                raise ValueError("published answer metric out of bounds")
            scores[variant][split] = {
                "examples": n,
                "answer_correct": round(accuracy * n),
                "answer_digit_accuracy": accuracy,
                "answer_digit_cross_entropy_nats": cross_entropy,
                "teacher_forced_token_accuracy": metrics["greedy_accuracy"],
            }
    return {
        "report_path": _EVIDENCE,
        "report_sha256": _EVIDENCE_SHA256,
        "report_whole_bytes_verified": True,
        "fixture_identity_verified": True,
        "current_source_sha256_verified": verified_sources,
        "source_bindings": source_bindings,
        "checkpoint_sha256": checkpoint_digest,
        "checkpoint_whole_bytes_verified": True,
        "checkpoint_loaded_or_executed": False,
        "scores_origin": "Copied from hash-verified existing report; inference was not rerun.",
        "answer_scores": scores,
    }


def _histogram(values: list[int]) -> dict[str, int]:
    counts = Counter(values)
    return {str(label): counts[label] for label in range(10)}


def _future_protocol() -> dict[str, Any]:
    return {
        "status": "predeclared_recommendation_not_executed_by_this_audit",
        "implementation": "src.infrastructure.arithmetic_generalization",
        "problem_family": "Two-digit operands with one-digit sum modulo10.",
        "scope": "Fresh complete-string and newly trained model residue-pair generalization, not historically unseen arithmetic computations or useful application LLM evidence.",
        "separation": "Old single-digit test rows are diagnostic only and never select the new checkpoint.",
        "predeclared_partition": {
            "unit": "operand units-digit pair grouped with its reversal",
            "allocation": "Hash-select15 unordered distinct unit pairs and their reversals as30 fresh holdout pairs; remaining70 are development pairs.",
            "train": "Development unit pairs crossed with both tens digits1..8:4480 strings.",
            "validation": "Development unit pairs with tens9,8:70 new strings.",
            "fresh_holdout": "Excluded unit pairs with tens9,9:30 new strings.",
            "custody": "Publish immutable source/config/development-bound preregistration before training or generating heldout results.",
        },
        "selection_budget": {
            "architecture": "Existing P43 dim48,4 heads,2 layers; no answer lookup or symbolic inference features.",
            "training_seeds": [43117],
            "learning_rates": [0.003],
            "checkpoint_steps": [1000, 3000, 6000, 10000],
            "maximum_training_runs": 1,
            "runtime_seconds_maximum": 300,
            "loss": "Answer-only cross-entropy at target index5.",
            "selection": "Minimum validation answer cross-entropy only, ties earlier checkpoint.",
        },
        "freeze_and_evaluate": "After validation selection, evaluate the30 fresh strings once; retain old30 only as separately labeled exposed diagnostic.",
        "predeclared_gate": {
            "metric": "answer-label accuracy, not formatting-token accuracy",
            "uniform_digit_chance_accuracy": 0.1,
            "minimum_correct_of_30": 30,
            "threshold_may_change": False,
            "report": "Publish all validation checkpoints, selected checkpoint, fresh predictions and exact counts, regardless of failure.",
            "interpretation": "Passing supports only this task-specific gate, not a useful general LLM or production promotion.",
        },
        "failure_policy": "Publish negatives; no test-selected retries or threshold weakening. Further development needs a new preregistration and genuinely fresh heldout evidence.",
        "executed": False,
    }


def audit_arithmetic_protocol(output_dir: str | Path | None = None) -> dict[str, Any]:
    """Audit the fixed exposed protocol; optionally publish whole-byte hashed JSON.

    The sole optional argument must name an existing directory. No model is
    trained, loaded, calibrated, selected, or executed. Identity drift is fatal.
    """
    if output_dir is not None and not Path(output_dir).is_dir():
        raise ValueError("--output-dir must be an existing directory")
    vocabulary, rows, records = _enumeration()
    identities = {split: _identity(rows[split]) for split in _SPLITS}
    evidence = _verified_evidence(identities, vocabulary)
    histograms = {
        split: _histogram([answer for _, _, answer, _ in records[split]])
        for split in _SPLITS
    }
    sizes = {split: len(records[split]) for split in _SPLITS}
    majority_labels = [
        int(label) for label, count in histograms["train"].items()
        if count == max(histograms["train"].values())
    ]
    majority = min(majority_labels)
    split_results = {}
    pairs = {split: {(left, right) for left, right, _, _ in records[split]} for split in _SPLITS}
    for split in _SPLITS:
        n = sizes[split]
        histogram = histograms[split]
        split_results[split] = {
            "identity": identities[split],
            "answer_histogram": histogram,
            "left_operand_histogram": _histogram([left for left, _, _, _ in records[split]]),
            "right_operand_histogram": _histogram([right for _, right, _, _ in records[split]]),
            "residue_histogram": _histogram([residue for _, _, _, residue in records[split]]),
            "ordered_pairs": [list(pair) for pair in sorted(pairs[split])],
            "answer_labels": [int(label) for label, count in histogram.items() if count],
            "unseen_answer_labels_in_split": [int(label) for label, count in histogram.items() if not count],
            "underrepresented_vs_uniform_answer_labels": [
                int(label) for label, count in histogram.items() if count / n < 0.1
            ],
            "answer_labels_unseen_in_training": [
                int(label) for label, count in histogram.items()
                if count and not histograms["train"][label]
            ],
            "baselines": {
                "uniform_random_digit_expected_accuracy": 0.1,
                "uniform_random_digit_expected_correct": n / 10,
                "uniform_random_digit_cross_entropy_nats": math.log(10),
                "uniform_random_vocabulary_expected_accuracy": 1 / len(vocabulary),
                "uniform_random_vocabulary_cross_entropy_nats": math.log(len(vocabulary)),
                "train_majority_tied_labels": majority_labels,
                "train_majority_tie_rule": "smallest digit; no evaluation-label selection",
                "train_majority_selected_label": majority,
                "train_majority_accuracy": histogram[str(majority)] / n,
                "train_histogram_random_guess_expected_accuracy": sum(
                    histograms["train"][str(label)] / sizes["train"] * histogram[str(label)] / n
                    for label in range(10)
                ),
                "split_oracle_constant_accuracy_descriptive_not_fitted_baseline": max(histogram.values()) / n,
            },
        }
    overlaps = {}
    for i, first in enumerate(_SPLITS):
        for second in _SPLITS[i + 1:]:
            direct = pairs[first] & pairs[second]
            reverse = pairs[first] & {(right, left) for left, right in pairs[second]}
            overlaps[f"{first}_vs_{second}"] = {
                "ordered_pair_overlap_count": len(direct),
                "ordered_pair_overlap": [list(pair) for pair in sorted(direct)],
                "reverse_pair_overlap_count": len(reverse),
                "reverse_pair_overlap_pairs_in_first_split": [list(pair) for pair in sorted(reverse)],
                "answer_label_overlap": sorted(
                    {answer for _, _, answer, _ in records[first]}
                    & {answer for _, _, answer, _ in records[second]}
                ),
                "left_operand_overlap": sorted({x[0] for x in records[first]} & {x[0] for x in records[second]}),
                "right_operand_overlap": sorted({x[1] for x in records[first]} & {x[1] for x in records[second]}),
            }
    tv = {}
    for i, first in enumerate(_SPLITS):
        for second in _SPLITS[i + 1:]:
            tv[f"{first}_vs_{second}"] = 0.5 * sum(
                abs(histograms[first][str(label)] / sizes[first] - histograms[second][str(label)] / sizes[second])
                for label in range(10)
            )
    train_test_total = sizes["train"] + sizes["test"]
    mi = 0.0
    for split in ("train", "test"):
        for label in range(10):
            count = histograms[split][str(label)]
            marginal = (histograms["train"][str(label)] + histograms["test"][str(label)]) / train_test_total
            if count:
                mi += count / train_test_total * math.log((count / sizes[split]) / marginal)
    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "measured_exposed_protocol_audit_not_new_validation",
        "fixture_sha256": hashlib.sha256(_json_bytes(identities)).hexdigest(),
        "enumerated_ordered_pairs": 100,
        "splits": split_results,
        "overlaps": overlaps,
        "distribution_shift": {
            "answer_total_variation": tv,
            "train_test_split_answer_mutual_information_nats": mi,
            "measure": "Exact finite-population enumeration, not sampled estimates or significance tests; MI weights train/test by their actual 60/30 sizes.",
        },
        "construction_diagnosis": {
            "split_residue": "(7*left + 3*right) mod 10 = 7*(left-right) mod 10",
            "answer_parity_equals_residue_parity_for_all_100_pairs": all(
                answer % 2 == residue % 2 for split in _SPLITS for _, _, answer, residue in records[split]
            ),
            "mechanism": "For fixed answer a, right=a-left mod 10, so residue=4*left+3*a mod 10. Exactly five residues of parity a occur, each twice. Train residues 0-5 give six examples per answer; validation residue 6 allows only even answers; test residues 7-9 give two per even and four per odd answer.",
            "reversal": "Swapping operands maps residue r to (-r) mod 10. All 10 validation and all 30 test pairs have a reversed training pair, despite zero ordered-pair overlap.",
            "modular_left_minus_right_by_split": {
                split: sorted({(left - right) % 10 for left, right, _, _ in records[split]})
                for split in _SPLITS
            },
            "established": "Deterministic split/answer-parity confounding and commutative reverse-pair overlap are established by complete enumeration.",
            "not_established": "These properties do not establish the causal source of the checkpoint's zero heldout answer accuracy. All answer labels and all operand digits occur in training. Optimization failure, shortcut learning, and inadequate generalization remain unseparated hypotheses; no prediction-level or intervention evidence is available here.",
        },
        "existing_evidence": evidence,
        "interpretation": {
            "useful_model_evidence": False,
            "old_holdout_exposed": True,
            "new_training_or_inference_performed": False,
            "finding": "Native checkpoint solves 43/60 training answers but 0/10 validation and 0/30 test answers. Four-bit preservation of this failed reference is not useful-model quality; token accuracy includes punctuation and operand prediction.",
            "causal_explanation_established": False,
            "next_action": "Retire the exposed arithmetic fixture as a capability gate; preserve all negative reports and perform only a separately preregistered untouched-family experiment.",
        },
        "future_experiment_recommendation": _future_protocol(),
    }
    paths = [
        "src/infrastructure/research_quality_audit.py", _EVIDENCE,
        *evidence["source_bindings"], _ARCHIVED_SOURCE,
    ]
    report["execution_spine"] = ExecutionSpineRecord(
        surface_id=f"arithmetic-protocol-audit:{report['fixture_sha256'][:16]}",
        surface_kind="exposed_research_protocol_audit",
        lane="non-hardgate-ml-infrastructure",
        status="research_measured",
        generated_at_utc=None,
        summary="Enumerated split confounding and verified existing negative arithmetic evidence; no causal or useful-model claim.",
        canonical_paths=paths,
        sources=paths,
        governance=build_fail_closed_governance(
            epistemic_label="exposed finite-fixture audit, not independent validation",
            promotion_rule="No promotion from an audit or preservation of a failed model.",
            residual_blockers=["No causal intervention evidence.", "No untouched independent useful-model evaluation."],
        ),
        compatibility={"fixture_sha256": report["fixture_sha256"], "report_sha256": _EVIDENCE_SHA256},
        promotion={
            "eligible": False, "model_claim": False, "backend_claim": False,
            "physics_claim": False, "independent_validation": False,
            "reason": "An exposed protocol audit establishes no useful-model capability.",
        },
    ).to_dict()
    report["audit_source_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if output_dir is not None:
        report["published_evidence"] = {"filename_is_sha256_of_complete_json_bytes": True}
        content = _json_bytes(report) + b"\n"
        publish_immutable(Path(output_dir), hashlib.sha256(content).hexdigest(), content)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True, help="existing directory for immutable audit JSON")
    args = parser.parse_args(argv)
    report = audit_arithmetic_protocol(args.output_dir)
    content = _json_bytes(report) + b"\n"
    print(json.dumps({"sha256": hashlib.sha256(content).hexdigest(), "promotion_eligible": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
