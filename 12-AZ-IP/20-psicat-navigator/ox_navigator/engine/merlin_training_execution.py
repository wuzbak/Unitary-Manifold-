# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Active three-lane training execution queues and retained progress ledgers for Merlin."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .merlin_counterexample import build_counterexample_digest
from .merlin_memory import MerlinSession
from .merlin_meta_learning import analyze_depth, consolidate_memory, generate_falsification_oracle, run_self_audit
from .merlin_program import build_merlin_continuous_learning_queue
from src.core.navier_stokes_method_transfer import CURRICULUM_PACKET_PATH, INTAKE_PACKET_PATH

REPO_ROOT = Path(__file__).resolve().parents[4]
PRODUCT_ROOT = Path(__file__).resolve().parents[2]
EXECUTION_ARTIFACT_PATH = PRODUCT_ROOT / "training" / "training_execution" / "three_lane_execution_bundle.json"
GATE_LABELS = ("HARDGATE", "ADJACENT_TRACK", "OPEN_GAP", "ARCHITECTURE_LIMIT", "GOVERNANCE")
LANE_ORDER = (
    "lane_a_applications_tools_mastery",
    "lane_b_books_articles_mastery",
    "lane_c_adversarial_self_correction",
    "lane_d_formal_proof_foundry",
)
LANE_NAMES = {
    "lane_a_applications_tools_mastery": "Lane A — Applications and Tools Mastery",
    "lane_b_books_articles_mastery": "Lane B — Books and Articles Mastery",
    "lane_c_adversarial_self_correction": "Lane C — Adversarial Self-Correction",
    "lane_d_formal_proof_foundry": "Lane D — Formal Proof Foundry",
}
LANE_MASTERY_THRESHOLDS = {
    "lane_a_applications_tools_mastery": 0.25,
    "lane_b_books_articles_mastery": 0.22,
    "lane_c_adversarial_self_correction": 0.5,
    "lane_d_formal_proof_foundry": 0.35,
}


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_limit(limit: int | None) -> int | None:
    if limit is None:
        return None
    return max(0, int(limit))


def _repo_rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def _markdown_title(text: str, *, fallback: str) -> str:
    for pattern in (r"^#\s+(.+)$", r"^##\s+(.+)$"):
        match = re.search(pattern, text, flags=re.MULTILINE)
        if match:
            return str(match.group(1)).strip()
    return fallback


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _parse_iso_timestamp(value: Any) -> datetime | None:
    stamp = str(value or "").strip()
    if not stamp:
        return None
    try:
        parsed = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except ValueError:
        return None


def _relative_target(reference_path: str) -> Path:
    return REPO_ROOT / str(reference_path or "").strip()


def _navier_stokes_packet_kind(reference_path: str) -> str | None:
    target = str(reference_path or "").strip()
    if target == INTAKE_PACKET_PATH:
        return "intake_packet"
    if target == CURRICULUM_PACKET_PATH:
        return "curriculum_packet"
    return None


def _latest_receipts_by_queue(session: MerlinSession) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for item in list(session.training_execution_receipts):
        queue_id = str(item.get("queue_id") or "").strip()
        if not queue_id:
            continue
        latest[queue_id] = dict(item)
    return latest


def _queue_blueprint() -> list[dict[str, Any]]:
    payload = build_merlin_continuous_learning_queue(limit=None)
    return list(payload.get("items") or [])


def _round_robin_queue_items(items: list[dict[str, Any]], *, limit: int | None) -> list[dict[str, Any]]:
    cap = _coerce_limit(limit)
    per_lane: dict[str, list[dict[str, Any]]] = {lane_id: [] for lane_id in LANE_ORDER}
    spillover: list[dict[str, Any]] = []
    for item in items:
        lane_id = str(item.get("lane_id") or "")
        if lane_id in per_lane:
            per_lane[lane_id].append(item)
        else:
            spillover.append(item)
    selected: list[dict[str, Any]] = []
    while True:
        advanced = False
        for lane_id in LANE_ORDER:
            bucket = per_lane[lane_id]
            if not bucket:
                continue
            selected.append(bucket.pop(0))
            advanced = True
            if cap is not None and len(selected) >= cap:
                return selected
        if not advanced:
            break
    selected.extend(spillover)
    return selected if cap is None else selected[:cap]


def _walk_stats(path: Path) -> dict[str, Any]:
    root = path.parent if path.is_file() else path
    if not root.exists():
        return {
            "root": _repo_rel(root),
            "exists": False,
            "file_count": 0,
            "python_files": 0,
            "markdown_files": 0,
            "test_files": 0,
            "sample_files": [],
        }
    files = [candidate for candidate in root.rglob("*") if candidate.is_file()]
    python_files = [candidate for candidate in files if candidate.suffix == ".py"]
    markdown_files = [candidate for candidate in files if candidate.suffix == ".md"]
    test_files = [candidate for candidate in files if candidate.name.startswith("test_") or "/tests/" in candidate.as_posix()]
    return {
        "root": _repo_rel(root),
        "exists": True,
        "file_count": len(files),
        "python_files": len(python_files),
        "markdown_files": len(markdown_files),
        "test_files": len(test_files),
        "sample_files": [_repo_rel(candidate) for candidate in files[:8]],
    }


def _path_file_inventory(path: Path) -> list[Path]:
    if not path.exists():
        return []
    if path.is_file():
        return [path]
    return [candidate for candidate in path.rglob("*") if candidate.is_file()]


def _build_source_snapshot(item: dict[str, Any], *, session: MerlinSession | None = None) -> dict[str, Any]:
    lane_id = str(item.get("lane_id") or "")
    reference_path = str(item.get("reference_path") or "")
    if lane_id in {
        "lane_a_applications_tools_mastery",
        "lane_b_books_articles_mastery",
        "lane_d_formal_proof_foundry",
    }:
        target = _relative_target(reference_path)
        files = _path_file_inventory(target if target.exists() else target.parent)
        entries: list[str] = []
        last_modified = 0.0
        for candidate in files:
            try:
                stat = candidate.stat()
            except OSError:
                continue
            rel = _repo_rel(candidate)
            entries.append(f"{rel}|{int(stat.st_mtime_ns)}|{int(stat.st_size)}")
            last_modified = max(last_modified, float(stat.st_mtime))
        digest = hashlib.sha256("\n".join(sorted(entries)).encode("utf-8")).hexdigest()
        return {
            "snapshot_type": "filesystem",
            "reference_path": reference_path,
            "tracked_root": _repo_rel(target if target.exists() else target.parent),
            "file_count": len(entries),
            "content_digest": digest,
            "last_modified_at": (
                datetime.fromtimestamp(last_modified, tz=timezone.utc).isoformat()
                if last_modified > 0
                else ""
            ),
        }
    files = [
        Path(__file__).resolve(),
        Path(__file__).with_name("merlin_counterexample.py"),
        Path(__file__).with_name("merlin_meta_learning.py"),
        Path(__file__).with_name("merlin_memory.py"),
    ]
    entries: list[str] = []
    last_modified = 0.0
    for candidate in files:
        if not candidate.exists():
            continue
        try:
            stat = candidate.stat()
        except OSError:
            continue
        entries.append(f"{_repo_rel(candidate)}|{int(stat.st_mtime_ns)}|{int(stat.st_size)}")
        last_modified = max(last_modified, float(stat.st_mtime))
    return {
        "snapshot_type": "engine_sources",
        "reference_path": reference_path,
        "tracked_files": [_repo_rel(candidate) for candidate in files if candidate.exists()],
        "content_digest": hashlib.sha256("\n".join(sorted(entries)).encode("utf-8")).hexdigest(),
        "last_modified_at": (
            datetime.fromtimestamp(last_modified, tz=timezone.utc).isoformat()
            if last_modified > 0
            else ""
        ),
    }


def _extract_internal_links(text: str) -> list[str]:
    return sorted({match.strip() for match in re.findall(r"\]\((?!https?://)([^)#]+)", text) if match.strip()})


def _hash_receipt(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _score_lane_receipt(lane_id: str, metrics: dict[str, Any]) -> tuple[float, str, list[str]]:
    blockers: list[str] = []
    if lane_id == "lane_a_applications_tools_mastery":
        score = min(
            1.0,
            (
                min(float(metrics.get("inventory_files", 0) or 0) / 20.0, 1.0) * 0.3
                + min(float(metrics.get("python_files", 0) or 0) / 20.0, 1.0) * 0.25
                + min(float(metrics.get("test_files", 0) or 0) / 6.0, 1.0) * 0.2
                + min(float(metrics.get("documented_endpoint_count", 0) or 0) / 4.0, 1.0) * 0.15
                + min(float(metrics.get("gate_marker_count", 0) or 0) / 2.0, 1.0) * 0.1
            ),
        )
        if float(metrics.get("inventory_files", 0) or 0) == 0:
            blockers.append("no_repository_surface_detected")
    elif lane_id == "lane_b_books_articles_mastery":
        score = min(
            1.0,
            (
                min(float(metrics.get("word_count", 0) or 0) / 900.0, 1.0) * 0.4
                + min(float(metrics.get("heading_count", 0) or 0) / 6.0, 1.0) * 0.2
                + min(float(metrics.get("internal_link_count", 0) or 0) / 4.0, 1.0) * 0.2
                + min(float(metrics.get("limits_marker_count", 0) or 0) / 3.0, 1.0) * 0.2
            ),
        )
        if float(metrics.get("word_count", 0) or 0) == 0:
            blockers.append("empty_editorial_surface")
    elif lane_id == "lane_c_adversarial_self_correction":
        contract_pass_rate = float(metrics.get("contract_pass_rate", 0.0) or 0.0)
        audit_sample_count = float(metrics.get("audit_sample_count", 0) or 0)
        effective_contract_pass_rate = contract_pass_rate if audit_sample_count > 0 else 0.9
        score = min(
            1.0,
            (
                effective_contract_pass_rate * 0.45
                + min(float(metrics.get("recommended_depth", 0) or 0) / 5.0, 1.0) * 0.2
                + min(float(metrics.get("compiled_insights", 0) or 0) / 8.0, 1.0) * 0.2
                + (1.0 if float(metrics.get("digest_items", 1) or 1) > 0 else 0.0) * 0.15
            ),
        )
        if audit_sample_count > 0 and contract_pass_rate < 0.9:
            blockers.append("contract_pass_rate_below_target")
    else:
        score = min(
            1.0,
            (
                min(float(metrics.get("word_count", 0) or 0) / 500.0, 1.0) * 0.3
                + min(float(metrics.get("heading_count", 0) or 0) / 5.0, 1.0) * 0.2
                + min(float(metrics.get("review_packet_mentions", 0) or 0) / 1.0, 1.0) * 0.25
                + min(float(metrics.get("open_gap_mentions", 0) or 0) / 2.0, 1.0) * 0.15
                + min(float(metrics.get("internal_link_count", 0) or 0) / 3.0, 1.0) * 0.1
            ),
        )
        if float(metrics.get("review_packet_mentions", 0) or 0) == 0 and float(metrics.get("open_gap_mentions", 0) or 0) == 0:
            blockers.append("missing_review_packet_reference")
    threshold = float(LANE_MASTERY_THRESHOLDS.get(lane_id, 0.6))
    verdict = "pass" if score >= threshold and not blockers else "needs_review"
    return round(score, 4), verdict, blockers


def _upsert_insight(session: MerlinSession, *, source_query: str, fact: str, tags: list[str], namespace: str = "general") -> None:
    for entry in reversed(session.compiled_insights):
        if str(entry.get("source_query") or "") != source_query:
            continue
        entry.update(
            {
                "fact": fact,
                "source_query": source_query,
                "tags": list(tags),
                "namespace": namespace,
                "status": "[TRUSTED_COMPILED]",
                "proof_verdict": "not_applicable",
                "contradictions": [],
                "ingested_at": _utcnow(),
            }
        )
        return
    session.ingest_compiled_insight(
        {
            "insight_id": source_query,
            "fact": fact,
            "source_query": source_query,
            "tags": list(tags),
            "namespace": namespace,
            "proof_verdict": "not_applicable",
            "contradictions": [],
        }
    )


def _build_lane_a_receipt(item: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], str]:
    target = _relative_target(str(item.get("reference_path") or ""))
    readme_path = target if target.is_file() else target / "README.md"
    text = _read_text(readme_path)
    stats = _walk_stats(target)
    endpoints = sorted({match for match in re.findall(r"/api/[A-Za-z0-9_./-]+", text)})[:12]
    artifact = {
        "artifact_type": str(item.get("expected_artifact") or "product_capability_map"),
        "training_mode": "structural_repository_ingestion",
        "honesty_note": "This receipt captures deterministic repository ingestion and retained structure, not hidden model-weight updates.",
        "reference_path": _repo_rel(readme_path if readme_path.exists() else target),
        "document_title": _markdown_title(text, fallback=str(item.get("task") or "product_training_receipt")),
        "documented_endpoints": endpoints,
        "structure_metrics": stats,
        "gate_markers": [label for label in GATE_LABELS if label in text],
        "internal_links": _extract_internal_links(text)[:12],
    }
    metrics = {
        "inventory_files": stats["file_count"],
        "python_files": stats["python_files"],
        "test_files": stats["test_files"],
        "documented_endpoint_count": len(endpoints),
        "gate_marker_count": len(artifact["gate_markers"]),
    }
    fact = (
        f"{item.get('task')} retained {_repo_rel(readme_path if readme_path.exists() else target)} with "
        f"{stats['python_files']} Python files, {stats['test_files']} tests, and {len(endpoints)} documented endpoints."
    )
    return artifact, metrics, fact


def _build_lane_b_receipt(item: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], str]:
    target = _relative_target(str(item.get("reference_path") or ""))
    text = _read_text(target)
    headings = [match.strip() for match in re.findall(r"^#{1,6}\s+(.+)$", text, flags=re.MULTILINE)]
    internal_links = _extract_internal_links(text)
    words = re.findall(r"\b[\w'’-]+\b", text)
    artifact = {
        "artifact_type": str(item.get("expected_artifact") or "editorial_study_ledger"),
        "training_mode": "structural_editorial_ingestion",
        "honesty_note": "This receipt retains visible title, section, link, and epistemic-marker structure and does not claim latent semantic mastery beyond audited repository evidence.",
        "reference_path": _repo_rel(target),
        "title": _markdown_title(text, fallback=target.stem.replace("-", " ")),
        "heading_count": len(headings),
        "heading_preview": headings[:10],
        "internal_link_count": len(internal_links),
        "internal_link_preview": internal_links[:12],
        "word_count": len(words),
        "gate_markers": [label for label in GATE_LABELS if label in text],
        "limits_markers": sorted(
            {
                marker
                for marker in ("open gap", "architecture limit", "falsif", "honest", "limit", "boundary")
                if marker in text.lower()
            }
        ),
    }
    metrics = {
        "heading_count": artifact["heading_count"],
        "internal_link_count": artifact["internal_link_count"],
        "word_count": artifact["word_count"],
        "gate_marker_count": len(artifact["gate_markers"]),
        "limits_marker_count": len(artifact["limits_markers"]),
    }
    fact = (
        f"{artifact['title']} retained {_repo_rel(target)} with {artifact['word_count']} words, "
        f"{artifact['heading_count']} headings, and {artifact['internal_link_count']} internal links."
    )
    return artifact, metrics, fact


def _build_lane_c_receipt(item: dict[str, Any], *, session: MerlinSession) -> tuple[dict[str, Any], dict[str, Any], str]:
    queue_id = str(item.get("queue_id") or "")
    if queue_id == "lane_c_contradiction_digest":
        digest = build_counterexample_digest(session=session, limit=25)
        artifact = {
            "artifact_type": "contradiction_remediation_ledger",
            "training_mode": "adversarial_counterexample_refresh",
            "reference_path": str(item.get("reference_path") or ""),
            "digest": digest,
        }
        metrics = {
            "contradiction_events": int(digest.get("total_events", 0) or 0),
            "quarantined_insights": int(digest.get("quarantined_insight_count", 0) or 0),
            "digest_items": len(list(digest.get("items") or [])),
        }
        fact = (
            f"Contradiction digest retained {metrics['digest_items']} counterexample signals with "
            f"{metrics['contradiction_events']} contradiction events."
        )
        return artifact, metrics, fact
    if queue_id == "lane_c_falsification_oracle":
        domains = ["general_reasoning", "journalism", "earth_science", "film_production"]
        oracles = [generate_falsification_oracle(domain=domain, session=session) for domain in domains]
        artifact = {
            "artifact_type": "domain_kill_condition_registry",
            "training_mode": "falsification_oracle_refresh",
            "reference_path": str(item.get("reference_path") or ""),
            "oracles": oracles,
        }
        metrics = {
            "domain_count": len(oracles),
            "kill_condition_count": sum(len(list(oracle.get("kill_conditions") or [])) for oracle in oracles),
        }
        fact = f"Falsification oracles refreshed across {metrics['domain_count']} domains with {metrics['kill_condition_count']} total kill conditions."
        return artifact, metrics, fact
    memory = consolidate_memory(session=session, limit=10)
    audit = run_self_audit(session=session)
    depth = analyze_depth(session=session, limit=25)
    artifact = {
        "artifact_type": "telemetry_calibration_receipt",
        "training_mode": "memory_and_depth_self_audit",
        "reference_path": str(item.get("reference_path") or ""),
        "memory_consolidation": memory,
        "self_audit": audit,
        "depth_recommendation": depth,
    }
    calibration = dict(audit.get("calibration") or {})
    metrics = {
        "durable_memory": int((memory.get("counts") or {}).get("durable_memory", 0) or 0),
        "compiled_insights": int((memory.get("counts") or {}).get("trusted_compiled_insights", 0) or 0),
        "recommended_depth": int(depth.get("recommended_depth", 0) or 0),
        "contract_pass_rate": float(calibration.get("contract_pass_rate", 0.0) or 0.0),
        "audit_sample_count": int(calibration.get("sample_count", 0) or 0),
    }
    fact = (
        f"Self-audit retained {metrics['durable_memory']} durable memories, {metrics['compiled_insights']} trusted compiled insights, "
        f"and deterministic depth {metrics['recommended_depth']}."
    )
    return artifact, metrics, fact


def _build_lane_d_receipt(item: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], str]:
    target = _relative_target(str(item.get("reference_path") or ""))
    text = _read_text(target)
    navier_kind = _navier_stokes_packet_kind(str(item.get("reference_path") or ""))
    headings = [match.strip() for match in re.findall(r"^#{1,6}\s+(.+)$", text, flags=re.MULTILINE)]
    internal_links = _extract_internal_links(text)
    words = re.findall(r"\b[\w'’/-]+\b", text)
    review_packet_mentions = len(re.findall(r"REVIEW_PACKET|review packet", text))
    open_gap_mentions = len(re.findall(r"OPEN_GAP|open gap|boundary", text, flags=re.IGNORECASE))
    crosswalk_question_count = len(
        re.findall(r"what is structurally analogous|what is only metaphorically similar|what is mathematically reusable|what is completely non-transferable", text, flags=re.IGNORECASE)
    )
    adversarial_review_question_count = len(
        re.findall(r"precise blowup quantity|finite kinetic energy|smooth forcing|axisymmetry|perturbation|proved versus arranged", text, flags=re.IGNORECASE)
    )
    non_transfer_clause_present = bool(re.search(r"non-transfer clause|by analogy alone", text, flags=re.IGNORECASE))
    artifact = {
        "artifact_type": str(item.get("expected_artifact") or "proof_foundry_review_brief"),
        "training_mode": "formal_proof_foundry_ingestion",
        "honesty_note": "This receipt captures auditable proof-foundry intake surfaces and reviewer packets, not direct proof execution.",
        "reference_path": _repo_rel(target),
        "title": _markdown_title(text, fallback=target.stem.replace("_", " ")),
        "heading_count": len(headings),
        "heading_preview": headings[:10],
        "internal_link_count": len(internal_links),
        "internal_link_preview": internal_links[:12],
        "word_count": len(words),
        "review_packet_mentions": review_packet_mentions,
        "open_gap_markers": open_gap_mentions,
        "gate_markers": [label for label in GATE_LABELS if label in text],
        "packet_kind": navier_kind or "standard_proof_foundry_surface",
        "non_transfer_clause_present": non_transfer_clause_present,
        "crosswalk_question_count": crosswalk_question_count,
        "adversarial_review_question_count": adversarial_review_question_count,
    }
    metrics = {
        "heading_count": artifact["heading_count"],
        "internal_link_count": artifact["internal_link_count"],
        "word_count": artifact["word_count"],
        "review_packet_mentions": review_packet_mentions,
        "open_gap_mentions": open_gap_mentions,
        "non_transfer_clause_present": 1 if non_transfer_clause_present else 0,
        "crosswalk_question_count": crosswalk_question_count,
        "adversarial_review_question_count": adversarial_review_question_count,
    }
    if navier_kind:
        fact = (
            f"{artifact['title']} retained {_repo_rel(target)} as Navier-Stokes {navier_kind} with "
            f"{crosswalk_question_count} crosswalk questions and {adversarial_review_question_count} adversarial review prompts."
        )
    else:
        fact = (
            f"{artifact['title']} retained {_repo_rel(target)} with {artifact['word_count']} words, "
            f"{review_packet_mentions} review-packet markers, and {open_gap_mentions} boundary markers."
        )
    return artifact, metrics, fact


def _execute_queue_item(item: dict[str, Any], *, session: MerlinSession) -> dict[str, Any]:
    lane_id = str(item.get("lane_id") or "")
    started_at = _utcnow()
    source_snapshot = _build_source_snapshot(item, session=session)
    if lane_id == "lane_a_applications_tools_mastery":
        artifact, metrics, fact = _build_lane_a_receipt(item)
    elif lane_id == "lane_b_books_articles_mastery":
        artifact, metrics, fact = _build_lane_b_receipt(item)
    elif lane_id == "lane_c_adversarial_self_correction":
        artifact, metrics, fact = _build_lane_c_receipt(item, session=session)
    else:
        artifact, metrics, fact = _build_lane_d_receipt(item)
    mastery_score, gate_verdict, blockers = _score_lane_receipt(lane_id, metrics)
    base_receipt = {
        "queue_id": str(item.get("queue_id") or ""),
        "lane_id": lane_id,
        "lane_name": LANE_NAMES.get(lane_id, lane_id),
        "status": "completed",
        "task": str(item.get("task") or ""),
        "reference_path": str(item.get("reference_path") or ""),
        "expected_artifact": str(item.get("expected_artifact") or ""),
        "artifact": artifact,
        "metrics": metrics,
        "source_snapshot": source_snapshot,
        "mastery_score": mastery_score,
        "gate_verdict": gate_verdict,
        "gate_blockers": blockers,
        "summary_fact": fact,
        "started_at": started_at,
        "completed_at": _utcnow(),
        "retained_training": True,
    }
    base_receipt["receipt_id"] = _hash_receipt(base_receipt)
    session.record_training_execution_receipt(base_receipt)
    _upsert_insight(
        session,
        source_query=f"training_cycle:{base_receipt['queue_id']}",
        fact=fact,
        tags=["training_execution", lane_id, str(item.get("expected_artifact") or "")],
        namespace=(
            "governance"
            if lane_id == "lane_c_adversarial_self_correction"
            else "formal"
            if lane_id == "lane_d_formal_proof_foundry"
            else "general"
        ),
    )
    return base_receipt


def _resolve_queue_status(item: dict[str, Any], receipt: dict[str, Any] | None, *, session: MerlinSession) -> str:
    if not isinstance(receipt, dict):
        return "queued"
    if str(receipt.get("status") or "") == "failed":
        return "failed"
    current_snapshot = _build_source_snapshot(item, session=session)
    receipt_snapshot = dict(receipt.get("source_snapshot") or {})
    if receipt_snapshot.get("content_digest") and receipt_snapshot.get("content_digest") != current_snapshot.get("content_digest"):
        return "stale_retrain_required"
    completed_at = _parse_iso_timestamp(receipt.get("completed_at"))
    source_last_modified = _parse_iso_timestamp(current_snapshot.get("last_modified_at"))
    if completed_at and source_last_modified and source_last_modified > completed_at:
        return "stale_retrain_required"
    if str(receipt.get("gate_verdict") or "pass") != "pass":
        return "needs_review"
    return "completed"


def _lane_gate_summary(receipts: list[dict[str, Any]], *, total: int) -> dict[str, Any]:
    if not receipts:
        return {
            "mastery_score_mean": 0.0,
            "freshness_ratio": 0.0,
            "gate_pass_ratio": 0.0,
            "readiness": "not_started",
        }
    mastery_scores = [float(item.get("mastery_score", 0.0) or 0.0) for item in receipts]
    gate_passes = [item for item in receipts if str(item.get("gate_verdict") or "") == "pass"]
    fresh = [
        item for item in receipts
        if str(item.get("queue_status") or "completed") == "completed"
    ]
    gate_pass_ratio = len(gate_passes) / total if total else 0.0
    freshness_ratio = len(fresh) / total if total else 0.0
    mastery_mean = sum(mastery_scores) / len(mastery_scores)
    readiness = "ready" if gate_pass_ratio >= 0.9 and freshness_ratio >= 0.9 else "needs_work"
    return {
        "mastery_score_mean": round(mastery_mean, 4),
        "freshness_ratio": round(freshness_ratio, 4),
        "gate_pass_ratio": round(gate_pass_ratio, 4),
        "readiness": readiness,
    }


def get_merlin_training_challenge_pack(*, session: MerlinSession, limit: int = 12) -> dict[str, Any]:
    cap = max(1, min(int(limit or 12), 48))
    queue = build_merlin_training_execution_queue(session=session, limit=None)
    challenge_items: list[dict[str, Any]] = []
    for item in list(queue.get("items") or []):
        lane_id = str(item.get("lane_id") or "")
        prompt = ""
        answer_key = str(item.get("summary_fact") or item.get("task") or "")
        if lane_id == "lane_a_applications_tools_mastery":
            prompt = (
                f"Identify the Merlin product for {item.get('reference_path')} and state when it should be routed or recommended."
            )
        elif lane_id == "lane_b_books_articles_mastery":
            prompt = (
                f"Summarize the thesis, limits, and cross-reference obligations of {item.get('reference_path')}."
            )
        elif lane_id == "lane_d_formal_proof_foundry":
            if _navier_stokes_packet_kind(str(item.get("reference_path") or "")):
                prompt = (
                    f"Summarize the Navier-Stokes method-transfer packet for {item.get('reference_path')}, "
                    "including the non-transfer clause and the four crosswalk questions."
                )
            else:
                prompt = (
                    f"Summarize the proof-foundry obligation, reviewer packet, and non-claim boundary for {item.get('reference_path')}."
                )
        else:
            prompt = (
                f"State the contradiction, falsification, or calibration discipline required for {item.get('queue_id')}."
            )
        challenge_items.append(
            {
                "challenge_id": f"challenge_{item.get('queue_id')}",
                "lane_id": lane_id,
                "queue_id": item.get("queue_id"),
                "status": item.get("status"),
                "prompt": prompt,
                "required_output": item.get("expected_artifact"),
                "answer_key": answer_key,
                "reference_path": item.get("reference_path"),
            }
        )
    prioritized = sorted(
        challenge_items,
        key=lambda challenge: (
            {"stale_retrain_required": 0, "needs_review": 1, "queued": 2, "completed": 3}.get(str(challenge.get("status") or ""), 4),
            0 if _navier_stokes_packet_kind(str(challenge.get("reference_path") or "")) else 1,
            str(challenge.get("challenge_id") or ""),
        ),
    )
    selected = prioritized[:cap]
    return {
        "generated_at": _utcnow(),
        "challenge_count": len(selected),
        "selection_policy": "Prioritize stale and review-required work before merely completed work.",
        "challenges": selected,
    }


def build_merlin_training_execution_queue(*, session: MerlinSession, limit: int | None = None) -> dict[str, Any]:
    latest = _latest_receipts_by_queue(session)
    items: list[dict[str, Any]] = []
    for item in _queue_blueprint():
        queue_id = str(item.get("queue_id") or "")
        receipt = latest.get(queue_id)
        status = _resolve_queue_status(item, receipt, session=session)
        items.append(
            {
                **item,
                "status": status,
                "completed_at": receipt.get("completed_at") if isinstance(receipt, dict) else None,
                "latest_receipt_id": receipt.get("receipt_id") if isinstance(receipt, dict) else None,
                "summary_fact": receipt.get("summary_fact") if isinstance(receipt, dict) else None,
            }
        )
    completed = sum(1 for item in items if item["status"] == "completed")
    queued = sum(1 for item in items if item["status"] in {"queued", "stale_retrain_required", "needs_review"})
    stale = sum(1 for item in items if item["status"] == "stale_retrain_required")
    review = sum(1 for item in items if item["status"] == "needs_review")
    selected = items if limit is None else items[: _coerce_limit(limit)]
    return {
        "mode": "active_execution_queue",
        "objective": "Execute and retain four-lane Merlin training work with auditable per-item receipts.",
        "artifact_export_path": _repo_rel(EXECUTION_ARTIFACT_PATH),
        "total_queue_items": len(items),
        "completed_count": completed,
        "queued_count": queued,
        "stale_retrain_count": stale,
        "needs_review_count": review,
        "completion_ratio": round(completed / len(items), 4) if items else 1.0,
        "items": selected,
    }


def get_merlin_lane_progress_ledgers(*, session: MerlinSession, limit: int = 5) -> dict[str, Any]:
    cap = max(1, min(int(limit or 5), 25))
    blueprint = _queue_blueprint()
    queue_totals: dict[str, int] = {lane_id: 0 for lane_id in LANE_ORDER}
    for item in blueprint:
        lane_id = str(item.get("lane_id") or "")
        queue_totals[lane_id] = queue_totals.get(lane_id, 0) + 1
    latest = _latest_receipts_by_queue(session)
    receipts_by_lane: dict[str, list[dict[str, Any]]] = {lane_id: [] for lane_id in LANE_ORDER}
    for receipt in latest.values():
        lane_id = str(receipt.get("lane_id") or "")
        receipts_by_lane.setdefault(lane_id, []).append(dict(receipt))
    ledgers: list[dict[str, Any]] = []
    for lane_id in LANE_ORDER:
        queue_items_for_lane = [item for item in blueprint if str(item.get("lane_id") or "") == lane_id]
        receipts = sorted(
            receipts_by_lane.get(lane_id, []),
            key=lambda item: str(item.get("completed_at") or item.get("recorded_at") or ""),
        )
        receipt_index = {str(item.get("queue_id") or ""): dict(item) for item in receipts}
        queue_status_index = {
            str(item.get("queue_id") or ""): _resolve_queue_status(item, receipt_index.get(str(item.get("queue_id") or "")), session=session)
            for item in queue_items_for_lane
        }
        for item in receipts:
            item["queue_status"] = queue_status_index.get(str(item.get("queue_id") or ""), "completed")
        completed_count = len([item for item in receipts if str(item.get("status") or "") == "completed"])
        failed_count = len([item for item in receipts if str(item.get("status") or "") == "failed"])
        total = int(queue_totals.get(lane_id, 0) or 0)
        recent = receipts[-cap:]
        gate_summary = _lane_gate_summary(receipts, total=total)
        ledgers.append(
            {
                "lane_id": lane_id,
                "lane_name": LANE_NAMES.get(lane_id, lane_id),
                "total_queue_items": total,
                "completed_count": completed_count,
                "failed_count": failed_count,
                "queued_count": max(0, len([status for status in queue_status_index.values() if status in {"queued", "stale_retrain_required", "needs_review"}])),
                "stale_retrain_count": len([status for status in queue_status_index.values() if status == "stale_retrain_required"]),
                "needs_review_count": len([status for status in queue_status_index.values() if status == "needs_review"]),
                "completion_ratio": round(completed_count / total, 4) if total else 1.0,
                "latest_completed_at": receipts[-1].get("completed_at") if receipts else None,
                "gate_summary": gate_summary,
                "recent_receipts": [
                    {
                        "queue_id": item.get("queue_id"),
                        "receipt_id": item.get("receipt_id"),
                        "artifact_type": ((item.get("artifact") or {}).get("artifact_type")),
                        "completed_at": item.get("completed_at"),
                        "mastery_score": item.get("mastery_score"),
                        "gate_verdict": item.get("gate_verdict"),
                        "queue_status": item.get("queue_status"),
                        "summary_fact": item.get("summary_fact"),
                    }
                    for item in recent
                ],
                "metric_totals": {
                    key: round(
                        sum(float((item.get("metrics") or {}).get(key) or 0.0) for item in receipts),
                        4,
                    )
                    for key in sorted(
                        {
                            metric_key
                            for item in receipts
                            for metric_key in dict(item.get("metrics") or {}).keys()
                        }
                    )
                },
            }
        )
    overall_completed = sum(int(item["completed_count"]) for item in ledgers)
    overall_total = sum(int(item["total_queue_items"]) for item in ledgers)
    overall_stale = sum(int(item["stale_retrain_count"]) for item in ledgers)
    overall_review = sum(int(item["needs_review_count"]) for item in ledgers)
    return {
        "generated_at": _utcnow(),
        "artifact_export_path": _repo_rel(EXECUTION_ARTIFACT_PATH),
        "lane_ledgers": ledgers,
        "overall": {
            "lane_count": len(ledgers),
            "total_queue_items": overall_total,
            "completed_count": overall_completed,
            "queued_count": max(0, sum(int(item["queued_count"]) for item in ledgers)),
            "stale_retrain_count": overall_stale,
            "needs_review_count": overall_review,
            "completion_ratio": round(overall_completed / overall_total, 4) if overall_total else 1.0,
            "retained_training_receipts": len(list(session.training_execution_receipts)),
        },
    }


def run_merlin_training_cycle(*, session: MerlinSession, limit: int | None = None) -> dict[str, Any]:
    latest = _latest_receipts_by_queue(session)
    pending = []
    for item in _queue_blueprint():
        queue_id = str(item.get("queue_id") or "")
        status = _resolve_queue_status(item, latest.get(queue_id), session=session)
        if status in {"queued", "stale_retrain_required", "needs_review"}:
            pending.append(item)
    queue_before = build_merlin_training_execution_queue(session=session, limit=limit)
    selected = _round_robin_queue_items(pending, limit=limit)
    receipts = [_execute_queue_item(item, session=session) for item in selected]
    return {
        "ok": True,
        "generated_at": _utcnow(),
        "mode": "synchronous_retained_training_execution",
        "processed_count": len(receipts),
        "queue_before": queue_before,
        "receipts": receipts,
        "queue_after": build_merlin_training_execution_queue(session=session, limit=limit),
        "lane_progress": get_merlin_lane_progress_ledgers(session=session, limit=5),
        "challenge_pack": get_merlin_training_challenge_pack(session=session, limit=12),
        "retained_memory_state": session.get_public_memory_state(),
        "honesty_note": "This cycle executes deterministic repository-backed training receipts and retains them in Merlin session memory; it does not claim autonomous hidden-weight learning outside those auditable artifacts.",
    }


def build_merlin_training_execution_bundle(*, session: MerlinSession, limit: int | None = None) -> dict[str, Any]:
    queue_state = build_merlin_training_execution_queue(session=session, limit=None)
    if (
        any(str(item.get("status") or "") == "completed" for item in session.training_execution_receipts)
        and int(queue_state.get("queued_count", 0) or 0) == 0
        and int(queue_state.get("stale_retrain_count", 0) or 0) == 0
        and int(queue_state.get("needs_review_count", 0) or 0) == 0
    ):
        cycle = {
            "ok": True,
            "generated_at": _utcnow(),
            "mode": "reuse_retained_training_state",
            "processed_count": 0,
            "receipts": [],
            "queue_after": build_merlin_training_execution_queue(session=session, limit=limit),
            "lane_progress": get_merlin_lane_progress_ledgers(session=session, limit=5),
            "retained_memory_state": session.get_public_memory_state(),
            "honesty_note": "Previously retained training receipts were reused for this export bundle.",
        }
    else:
        cycle = run_merlin_training_cycle(session=session, limit=limit)
    return {
        "ok": True,
        "generated_at": _utcnow(),
        "artifact_path": _repo_rel(EXECUTION_ARTIFACT_PATH),
        "training_execution_queue": build_merlin_training_execution_queue(session=session, limit=24),
        "lane_progress_ledgers": get_merlin_lane_progress_ledgers(session=session, limit=5),
        "training_challenge_pack": get_merlin_training_challenge_pack(session=session, limit=12),
        "execution_cycle": cycle,
    }
