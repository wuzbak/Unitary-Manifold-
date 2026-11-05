# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Validation-only group calibration of the retained failed P43 research model."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from . import research_quantization as quant
from .artifact_io import publish_immutable
from .execution_spine import ExecutionSpineRecord, build_fail_closed_governance
from .model_interchange import _read_model, load_inference_checkpoint

GROUP_SIZES = (128, 256, 512, 1024, 2048, 4096)
NATIVE_SHA256 = "979847638ed7ec97277a0f5023515192779fc369050963048a12e0300fd8ede3"


def _publish(directory, value):
    content = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii") + b"\n"
    return publish_immutable(directory, hashlib.sha256(content).hexdigest(), content)


def _fidelity(candidate, native):
    ce = candidate["cross_entropy_nats"] - native["cross_entropy_nats"]
    accuracy = candidate["greedy_accuracy"] - native["greedy_accuracy"]
    return {
        "cross_entropy_delta_nats": ce, "greedy_accuracy_delta": accuracy,
        "passed": ce <= quant._QUALITY_TOLERANCE["maximum_cross_entropy_increase_nats"]
        and accuracy >= quant._QUALITY_TOLERANCE["minimum_greedy_accuracy_delta"],
    }


def calibrate(checkpoint, output_dir):
    """Freeze choices before validation, then inspect the old exposed test once.

    The historical test is not a new held-out qualification. No native weights
    are trained and no candidate is selected using its historical-test metrics.
    """
    directory = Path(output_dir)
    if not directory.is_dir():
        raise ValueError("output_dir must be an existing directory")
    content = _read_model(Path(checkpoint))
    digest = hashlib.sha256(content).hexdigest()
    if digest != NATIVE_SHA256:
        raise ValueError("calibration is bound to the retained original failed model")
    model = load_inference_checkpoint(content).model
    vocabulary, rows = quant._fixture()
    mapping = {character: index for index, character in enumerate(vocabulary)}
    validation = quant._encode_rows(rows["validation"], mapping)
    protocol = {
        "schema_version": "az_validation_only_group_calibration_v1",
        "native_checkpoint_sha256": digest, "group_sizes": list(GROUP_SIZES), "bits": 3,
        "selection_rule": "Among complete artifacts below 4 bits/parameter passing unchanged validation fidelity, choose minimum bytes; ties smaller group size. No test-based selection or retry.",
        "quality_tolerance": quant._QUALITY_TOLERANCE,
        "validation": quant._split_identity(rows["validation"]),
        "historical_test": "Already exposed, diagnostic only after selection; not an untouched holdout or native-model utility qualification.",
        "source_sha256": {
            "src/infrastructure/quantization_calibration.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "src/infrastructure/model_interchange.py": hashlib.sha256((quant._REPO_ROOT / "src/infrastructure/model_interchange.py").read_bytes()).hexdigest(),
            "src/infrastructure/tokenizer_interchange.py": hashlib.sha256((quant._REPO_ROOT / "src/infrastructure/tokenizer_interchange.py").read_bytes()).hexdigest(),
            **quant._source_identities(),
        },
    }
    protocol_path = _publish(directory, protocol)
    native_validation = quant._metrics(model, *validation)
    candidates = []
    eligible = []
    for group_size in GROUP_SIZES:
        artifact = quant.serialize_model(model, bit_width=3, group_size=group_size)
        candidate = quant.load_model_artifact(artifact)
        metrics = quant._metrics(candidate, *validation)
        size = quant._artifact_accounting(artifact)
        fidelity = _fidelity(metrics, native_validation)
        row = {"group_size": group_size, "validation": metrics, "fidelity": fidelity,
               "accounting": size, "artifact_sha256": hashlib.sha256(artifact).hexdigest()}
        candidates.append(row)
        if size["effective_bits_per_parameter"] < 4 and fidelity["passed"]:
            eligible.append((len(artifact), group_size, artifact, row))
    report = {
        "schema_version": "az_validation_only_group_calibration_result_v1",
        "protocol_sha256": protocol_path.stem, "native_validation": native_validation,
        "candidates": candidates, "selection_used_test": False,
        "scope": "Relative weight-quantization fidelity on a failed synthetic model. Original and subsequent 0/30 utility failures remain; historical test is exposed.",
        "status": "no_validation_candidate" if not eligible else "validation_candidate_selected",
        "promotion_eligible": False,
    }
    if eligible:
        _, group_size, artifact, selected = min(eligible, key=lambda item: (item[0], item[1]))
        artifact_path = publish_immutable(directory, selected["artifact_sha256"], artifact, suffix=".azmq")
        # This is the first access to test evaluation, after the choice is fixed.
        historical_test = quant._encode_rows(rows["test"], mapping)
        native_test = quant._metrics(model, *historical_test)
        selected_test = quant._metrics(quant.load_model_artifact(artifact), *historical_test)
        report["selected"] = {
            "group_size": group_size, "artifact_sha256": artifact_path.stem,
            "accounting": selected["accounting"], "historical_native_test": native_test,
            "historical_quantized_test": selected_test,
            "historical_fidelity": _fidelity(selected_test, native_test),
        }
    report["execution_spine"] = ExecutionSpineRecord(
        surface_id="az-validation-only-group-calibration",
        surface_kind="reference_benchmark_receipt", lane="az_ml_infrastructure",
        status=report["status"], generated_at_utc=None, summary=report["scope"],
        canonical_paths=["src/infrastructure/quantization_calibration.py"],
        governance=build_fail_closed_governance(
            epistemic_label="validation-selected calibration; exposed test diagnostic",
            promotion_rule="No useful native model or fresh quality qualification is established.",
            residual_blockers=["Native arithmetic generalization failed; no GPU or independent quantizer baseline."],
        ),
        promotion={"eligible": False, "physics_claim": False},
    ).to_dict()
    return _publish(directory, report), report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args(argv)
    path, report = calibrate(args.checkpoint, args.output_dir)
    print(json.dumps({"evidence": str(path), "status": report["status"]}))
    # Successful measurement/publication is not a quality pass.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
