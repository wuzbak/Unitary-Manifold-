# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Reproducible, bounded CPU evidence for the original ML reference libraries."""

from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import struct
import time

from .artifact_io import publish_immutable
from .drift_monitor import evaluate_drift
from .data_lineage import LineageGraph, LineageNode
from .execution_spine import ExecutionSpineRecord, build_fail_closed_governance
from .lowbit_quantization import QuantizedTensor, quantize
from .performance_profile import profile_callable
from .repository_vectors import build_repository_vectors
from .vector_index import (
    EmbeddingManifest, ExactVectorIndex, RetrievalQuery, VectorDocument,
    corpus_content_identity, evaluate_retrieval,
)

ROOT = Path(__file__).resolve().parents[2]
SOURCE_FILES = (
    "src/infrastructure/artifact_io.py",
    "src/infrastructure/lowbit_quantization.py",
    "src/infrastructure/vector_index.py",
    "src/infrastructure/repository_vectors.py",
    "src/infrastructure/drift_monitor.py",
    "src/infrastructure/data_lineage.py",
    "src/infrastructure/performance_profile.py",
    "src/infrastructure/temporal_data.py",
    "src/infrastructure/ml_reference_benchmarks.py",
    "src/infrastructure/execution_spine.py",
    "bot/rag_index.py",
)


def run_reference_benchmarks() -> dict[str, object]:
    """Measure declared fixtures; exceptions fail the run rather than produce a pass."""
    measurements: dict[str, object] = {}
    values = tuple(((index % 1025) - 512) / 512 for index in range(32768))
    started = time.perf_counter()
    tensor = quantize(values, bit_width=3, group_size=1024, mode="symmetric")
    encoded = tensor.to_bytes()
    restored = QuantizedTensor.from_bytes(encoded)
    if restored.dequantize() != tensor.dequantize():
        raise ValueError("Packed artifact decoding did not round-trip exactly")
    elapsed = time.perf_counter() - started
    metrics = tensor.metrics(values)
    quantization_gates = {
        "complete_serialized_representation_below_4_bits_per_weight":
            metrics.effective_bits_per_weight < 4,
        "max_error_at_most_one_sixth": metrics.max_absolute_error <= 1 / 6 + 1e-12,
        "packed_serialization_roundtrip_exact": True,
    }
    if not all(quantization_gates.values()):
        raise ValueError("Declared low-bit reference thresholds were not met")
    measurements["quantization"] = {
        **asdict(metrics),
        "value_count": len(values), "nominal_bits": 3, "group_size": 1024,
        "mode": "symmetric", "elapsed_seconds": elapsed,
        "float32_raw_bytes": len(struct.pack(f"<{len(values)}f", *values)),
        "fixture": "constructed periodic bounded numerical weights; not a trained model",
        "gates": quantization_gates,
    }
    profile = profile_callable(
        lambda: quantize(values, bit_width=3, group_size=1024, mode="symmetric"),
        subject="3-bit symmetric quantization of 32768 constructed scalar weights",
        owner_scope="reference", warmups=1, repetitions=5,
    )
    measurements["cpu_quantization_profile"] = {
        **profile.to_dict(), "values_per_call": len(values),
        "execution_spine": profile.receipt().to_dict(),
    }

    documents = tuple(
        VectorDocument(
            name, "reference", vector, f"constructed/{name}.txt",
            hashlib.sha256(name.encode()).hexdigest(), {"origin": "synthetic"},
        )
        for name, vector in (("x", (1.0, 0.0, 0.0)), ("y", (0.0, 1.0, 0.0)), ("z", (0.0, 0.0, 1.0)))
    )
    manifest = EmbeddingManifest(
        "constructed-axis-encoder-v1", 3, True, "cosine",
        corpus_content_identity(documents), "constructed-unit-axes-v1", "reference",
    )
    index = ExactVectorIndex(manifest, documents)
    queries = tuple(
        RetrievalQuery(doc.document_id, doc.vector, manifest, {doc.document_id: 1.0})
        for doc in documents
    )
    started = time.perf_counter()
    retrieval = evaluate_retrieval(index, queries, owner_scope="reference", k=1)
    retrieval_seconds = time.perf_counter() - started
    if retrieval.recall_at_k != 1.0 or retrieval.ndcg_at_k != 1.0:
        raise ValueError("Independent axis-reference retrieval thresholds were not met")
    measurements["exact_retrieval"] = {
        **asdict(retrieval), "elapsed_seconds": retrieval_seconds,
        "generation_ref": index.generation_ref,
        "fixture": "three orthogonal axes with one exact relevant document each",
    }

    from bot.rag_index import RAGIndex

    started = time.perf_counter()
    rag = RAGIndex.build(repo_root=ROOT, include_psicat_literature=False)
    allowed = (
        "12-AZ-IP/40-az-live-data-harness/README.md",
        "12-AZ-IP/43-az-geometric-tori-transformer/README.md",
        "12-AZ-IP/44-axiomzero-weave/README.md",
    )
    lexical = build_repository_vectors(
        rag, repo_root=ROOT, owner_scope="public-reference", allowed_sources=allowed,
    )
    results = []
    for query, expected in (
        ("availability observation earthquake", allowed[0]),
        ("NumPy autograd transformer", allowed[1]),
    ):
        hits = lexical.search(query, owner_scope="public-reference", top_k=1)
        actual = hits[0].document.evidence_path if hits else None
        if actual != expected:
            raise ValueError(f"Declared source-retrieval fixture failed: {query}")
        results.append({
            "query": query, "expected_source": expected, "actual_source": actual,
            "document_id": hits[0].document.document_id, "score": hits[0].score,
        })
    if lexical.search("azunknowntermwithoutoverlap", owner_scope="public-reference"):
        raise ValueError("No-overlap query unexpectedly returned evidence")
    measurements["rag_integration"] = {
        "rag_chunk_count": len(rag.chunks), "vector_chunk_count": len(lexical.index.documents),
        "generation_ref": lexical.index.generation_ref,
        "source_sha256": dict(lexical.source_identities),
        "elapsed_seconds": time.perf_counter() - started,
        "queries": results, "no_overlap_returned_no_hits": True,
        "scope": "Two declared lexical fixtures over real repository documents; not a semantic-quality benchmark.",
    }

    started = time.perf_counter()
    drift = evaluate_drift(seed=1729, trials=20, sample_size=256, shift=3.0, alpha=0.05)
    if drift["false_alert_fraction"] > 0.05 or drift["detection_rate"] < 0.9:
        raise ValueError("Declared constructed distribution-replay thresholds were not met")
    measurements["distribution_drift"] = {
        **drift, "elapsed_seconds": time.perf_counter() - started,
        "gates": {"false_alert_fraction_max": 0.05, "detection_rate_min": 0.9},
    }
    started = time.perf_counter()
    common = {
        "owner_scope": "constructed-lineage", "origins": ("synthetic",),
        "rights_assertion": "Constructed numerical fixture, not a third-party rights assessment",
        "purpose_assertion": "Reference lineage integrity checks",
    }
    source = LineageNode.from_payload(b"source fixture", kind="source", source="constructed://source", **common)
    fixture_code = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    fixture_config = hashlib.sha256(b"declared-lineage-reference-v1").hexdigest()
    snapshot_node = LineageNode.from_payload(
        b"snapshot fixture", kind="temporal_snapshot", parent_ids=(source.node_id,),
        transform="constructed-snapshot", code_sha256=fixture_code,
        config_sha256=fixture_config, **common,
    )
    feature_node = LineageNode.from_payload(
        b"features fixture", kind="features", parent_ids=(snapshot_node.node_id,),
        transform="constructed-features", code_sha256=fixture_code,
        config_sha256=fixture_config, **common,
    )
    graph = LineageGraph("constructed-lineage", (feature_node, source, snapshot_node))
    restored_graph = LineageGraph.from_json(graph.to_json())
    removal = graph.affected_by_deletion((source.node_id,))
    if restored_graph != graph or set(removal.remove_ids) != {node.node_id for node in graph.nodes}:
        raise ValueError("Declared lineage round-trip/deletion-closure thresholds were not met")
    measurements["lineage_integrity"] = {
        "graph_id": graph.content_hash, "node_count": len(graph.nodes),
        "roundtrip_exact": True, "deletion_plan_count": len(removal.remove_ids),
        "deletes_artifacts": removal.deletes_artifacts, "claims_unlearning": removal.claims_unlearning,
        "elapsed_seconds": time.perf_counter() - started,
        "scope": "Constructed manifest integrity only; the manifest does not prove execution or rights.",
    }
    source_hashes = {source: hashlib.sha256((ROOT / source).read_bytes()).hexdigest() for source in SOURCE_FILES}
    report = {
        "schema_version": "az_ml_reference_benchmarks_v1",
        "measured_at_utc": datetime.now(timezone.utc).isoformat(),
        "environment": {
            "python": platform.python_version(), "system": platform.system(),
            "machine": platform.machine(), "logical_cpus": os.cpu_count(),
            "gpu": "not_measured",
            "measurement_context": "Reference fixtures; no isolated-host or comparative performance guarantee",
        },
        "source_sha256": source_hashes,
        "measurements": measurements,
        "scope": "Scoped CPU reference milestones only; no capability or deployment promotion.",
        "gates_passed": True,
    }
    report["execution_spine"] = ExecutionSpineRecord(
        surface_id="az-ml-original-reference-baselines",
        surface_kind="reference_benchmark_receipt",
        lane="az_ml_infrastructure",
        status="scoped_reference_gates_passed",
        summary="Measured low-bit, CPU profiling, retrieval, RAG adapter, drift and lineage reference fixtures.",
        canonical_paths=["src/infrastructure/ml_reference_benchmarks.py"],
        sources=list(source_hashes),
        governance=build_fail_closed_governance(
            epistemic_label="constructed reference and bounded repository integration",
            promotion_rule="Reference gates do not establish trained-model or production readiness.",
            residual_blockers=[
                "No pretrained model, ANN backend, GPU or real prediction-performance monitoring measured.",
                "Real USGS access is independently assessed; constructed responses are not live measurements.",
            ],
        ),
        compatibility={"source_sha256": source_hashes, "measurement_keys": list(measurements)},
        promotion={"eligible": False, "physics_claim": False, "model_quality_claim": False},
    ).to_dict()
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, help="existing durable directory for immutable JSON receipt")
    args = parser.parse_args(argv)
    try:
        report = run_reference_benchmarks()
        content = (json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
        if args.output_dir is None:
            print(content.decode(), end="")
        else:
            identity = hashlib.sha256(content).hexdigest()
            print(publish_immutable(args.output_dir, identity, content))
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Reference benchmark failed: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
