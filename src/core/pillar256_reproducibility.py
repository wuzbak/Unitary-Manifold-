# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 256 reproducibility surfaces: thresholds, signed manifests, replay, trends."""

from __future__ import annotations

import hashlib
import hmac
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.core.pillar256_empirical_hardening_falsification import (
    pillar256_empirical_hardening_report,
)

ROOT = Path(__file__).resolve().parents[2]
THRESHOLD_METADATA_PATH = ROOT / "docs" / "falsification" / "pillar256_thresholds.yml"
THRESHOLD_GOVERNANCE_PATH = (
    ROOT / "docs" / "falsification" / "pillar256_threshold_governance.yml"
)
DEFAULT_SNAPSHOT_DIR = ROOT / "2-REPRODUCIBILITY" / "pillar256" / "snapshots"
DEFAULT_HISTORY_PATH = ROOT / "2-REPRODUCIBILITY" / "pillar256" / "run_history.jsonl"
DEFAULT_TREND_PANELS_PATH = ROOT / "2-REPRODUCIBILITY" / "pillar256" / "trend_panels.json"

VALID_GATE_STATUSES = {
    "PENDING_EXTERNAL_DATA",
    "CONSISTENT",
    "HIGH_TENSION",
    "FALSIFIED",
}

__all__ = [
    "THRESHOLD_METADATA_PATH",
    "THRESHOLD_GOVERNANCE_PATH",
    "DEFAULT_SNAPSHOT_DIR",
    "DEFAULT_HISTORY_PATH",
    "DEFAULT_TREND_PANELS_PATH",
    "load_threshold_metadata",
    "validate_threshold_metadata_integrity",
    "evaluate_falsification_gates",
    "create_execution_snapshot",
    "create_signed_run_manifest",
    "verify_signed_run_manifest",
    "write_snapshot_bundle",
    "append_run_history",
    "read_run_history",
    "build_trend_panels",
    "write_trend_panels",
]


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise ImportError("PyYAML required: pip install pyyaml") from exc
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Invalid YAML object in {path}")
    return loaded


def _canonical_json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256_hexdigest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _to_utc_z(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_threshold_metadata(path: Path = THRESHOLD_METADATA_PATH) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Threshold metadata not found: {path}")
    return _load_yaml(path)


def validate_threshold_metadata_integrity(
    metadata: dict[str, Any] | None = None,
) -> list[str]:
    if metadata is None:
        metadata = load_threshold_metadata()

    violations: list[str] = []

    for field in ("version", "effective_date", "gates", "governance"):
        if field not in metadata:
            violations.append(f"Missing top-level field: {field}")

    gates = metadata.get("gates", [])
    if not isinstance(gates, list) or not gates:
        violations.append("gates must be a non-empty list")
        return violations

    seen: set[str] = set()
    for gate in gates:
        gid = gate.get("id", "<missing-id>")
        if gid in seen:
            violations.append(f"Duplicate gate ID: {gid}")
        seen.add(gid)

        for field in (
            "id",
            "name",
            "observable",
            "thresholds",
            "ci_probe_fields",
            "default_status",
        ):
            if field not in gate:
                violations.append(f"[{gid}] Missing field: {field}")

        status = gate.get("default_status", "")
        if status not in VALID_GATE_STATUSES:
            violations.append(
                f"[{gid}] Invalid default_status '{status}' (valid: {sorted(VALID_GATE_STATUSES)})"
            )

        probe_fields = gate.get("ci_probe_fields", [])
        if not isinstance(probe_fields, list) or not probe_fields:
            violations.append(f"[{gid}] ci_probe_fields must be a non-empty list")

    governance = metadata.get("governance", {})
    if not isinstance(governance, dict):
        violations.append("governance must be a mapping")
    else:
        for field in (
            "revision_policy",
            "revision_log_file",
            "ci_ingest_contract",
        ):
            if field not in governance:
                violations.append(f"governance missing field: {field}")

    return violations


def _distance_to_interval(value: float, low: float, high: float) -> float:
    if value < low:
        return value - low
    if value > high:
        return high - value
    return min(value - low, high - value)


def _evaluate_fst1(gate: dict[str, Any], obs: dict[str, Any]) -> dict[str, Any]:
    thresholds = gate["thresholds"]
    window = thresholds["forbidden_mass_window_eV"]
    min_mix = float(thresholds["min_forbidden_mixing_sin2_2theta"])

    mass = obs.get("mass_eV")
    mixing = obs.get("mixing_sin2_2theta")
    confirmed = bool(obs.get("confirmed", False))

    if mass is None or mixing is None:
        return {
            "status": gate["default_status"],
            "distance_to_forbidden_window_eV": None,
            "triggered": False,
            "reason": "Missing mass/mixing observation.",
        }

    mass_f = float(mass)
    mixing_f = float(mixing)
    in_window = float(window["min"]) <= mass_f <= float(window["max"])
    triggered = bool(in_window and mixing_f > min_mix and confirmed)
    status = "FALSIFIED" if triggered else "CONSISTENT"

    return {
        "status": status,
        "distance_to_forbidden_window_eV": (
            0.0
            if in_window
            else min(
                abs(mass_f - float(window["min"])),
                abs(mass_f - float(window["max"])),
            )
        ),
        "triggered": triggered,
        "reason": (
            "Confirmed sterile branch entered forbidden mass-mixing region."
            if triggered
            else "No forbidden sterile branch crossing reported."
        ),
    }


def _evaluate_fst2(gate: dict[str, Any], obs: dict[str, Any]) -> dict[str, Any]:
    allowed = gate["thresholds"]["allowed_alpha_s_1tev"]
    alpha_s = obs.get("alpha_s_1tev")
    confirmed = bool(obs.get("confirmed", False))

    if alpha_s is None:
        return {
            "status": gate["default_status"],
            "distance_to_allowed_interval": None,
            "triggered": False,
            "reason": "Missing alpha_s(1 TeV) observation.",
        }

    alpha_f = float(alpha_s)
    low = float(allowed["min"])
    high = float(allowed["max"])
    distance = _distance_to_interval(alpha_f, low, high)
    out_of_bounds = alpha_f < low or alpha_f > high
    triggered = bool(out_of_bounds and confirmed)
    status = "FALSIFIED" if triggered else "CONSISTENT"

    return {
        "status": status,
        "distance_to_allowed_interval": distance,
        "triggered": triggered,
        "reason": (
            "Confirmed alpha_s(1 TeV) outside allowed chain window."
            if triggered
            else "No confirmed QCD chain break crossing reported."
        ),
    }


def _evaluate_fst3(gate: dict[str, Any], obs: dict[str, Any]) -> dict[str, Any]:
    thr = gate["thresholds"]
    soft = thr["soft_allowed_mbb_meV"]
    hard = thr["hard_fail_outside_mbb_meV"]

    mbb = obs.get("mbb_meV")
    sigma = obs.get("confidence_sigma", 0.0)
    confirmed = bool(obs.get("confirmed", False))

    if mbb is None:
        return {
            "status": gate["default_status"],
            "distance_to_hard_fail_interval_meV": None,
            "triggered": False,
            "reason": "Missing m_bb observation.",
        }

    mbb_f = float(mbb)
    sigma_f = float(sigma)

    hard_low = float(hard["min"])
    hard_high = float(hard["max"])
    soft_low = float(soft["min"])
    soft_high = float(soft["max"])

    distance_hard = _distance_to_interval(mbb_f, hard_low, hard_high)
    hard_fail = bool((mbb_f < hard_low or mbb_f > hard_high) and sigma_f >= 3.0 and confirmed)

    if hard_fail:
        status = "FALSIFIED"
        reason = "m_bb crossed hard fail interval at >=3σ."
    elif mbb_f < soft_low or mbb_f > soft_high:
        status = "HIGH_TENSION"
        reason = "m_bb outside soft allowed window; monitor external consensus."
    else:
        status = "CONSISTENT"
        reason = "m_bb within allowed window."

    return {
        "status": status,
        "distance_to_hard_fail_interval_meV": distance_hard,
        "triggered": hard_fail,
        "reason": reason,
    }


def evaluate_falsification_gates(
    metadata: dict[str, Any], observations: dict[str, Any] | None = None
) -> dict[str, dict[str, Any]]:
    observations = observations or {}
    results: dict[str, dict[str, Any]] = {}

    for gate in metadata.get("gates", []):
        gid = gate["id"]
        obs = observations.get(gid, {})
        if gid == "FST-1":
            results[gid] = _evaluate_fst1(gate, obs)
        elif gid == "FST-2":
            results[gid] = _evaluate_fst2(gate, obs)
        elif gid == "FST-3":
            results[gid] = _evaluate_fst3(gate, obs)
        else:
            results[gid] = {
                "status": gate.get("default_status", "PENDING_EXTERNAL_DATA"),
                "triggered": False,
                "reason": "No evaluator registered for gate ID.",
            }

    return results


def create_execution_snapshot(
    observations: dict[str, Any] | None = None,
    *,
    timestamp: datetime | None = None,
) -> dict[str, Any]:
    ts = timestamp or _utc_now()
    ts_z = _to_utc_z(ts)
    metadata = load_threshold_metadata()
    gate_evals = evaluate_falsification_gates(metadata, observations)

    return {
        "snapshot_id": f"pillar256-{ts.strftime('%Y%m%dT%H%M%SZ')}",
        "created_at_utc": ts_z,
        "python_version": sys.version.split()[0],
        "pillar256_report": pillar256_empirical_hardening_report(),
        "threshold_registry": {
            "file": str(THRESHOLD_METADATA_PATH.relative_to(ROOT)),
            "version": metadata.get("version"),
            "effective_date": metadata.get("effective_date"),
        },
        "falsification_gate_evaluations": gate_evals,
        "observations": observations or {},
    }


def create_signed_run_manifest(
    snapshot: dict[str, Any],
    *,
    signer: str = "PILLAR256_SELF_ATTESTED",
    signing_key: str | None = None,
) -> dict[str, Any]:
    snapshot_sha = _sha256_hexdigest(_canonical_json_bytes(snapshot))
    scheme = "HMAC_SHA256_V1" if signing_key else "SELF_HASH_ATTESTATION_V1"

    if signing_key:
        signature = hmac.new(
            signing_key.encode("utf-8"), snapshot_sha.encode("utf-8"), hashlib.sha256
        ).hexdigest()
    else:
        signature = _sha256_hexdigest(
            f"{snapshot_sha}|{signer}|{scheme}".encode("utf-8")
        )

    manifest = {
        "manifest_version": "v1",
        "snapshot_id": snapshot.get("snapshot_id"),
        "signed_at_utc": _to_utc_z(_utc_now()),
        "signer": signer,
        "signature_scheme": scheme,
        "snapshot_sha256": snapshot_sha,
        "signature": signature,
    }
    manifest["manifest_sha256"] = _sha256_hexdigest(_canonical_json_bytes(manifest))
    return manifest


def verify_signed_run_manifest(
    snapshot: dict[str, Any],
    manifest: dict[str, Any],
    *,
    signing_key: str | None = None,
) -> dict[str, Any]:
    errors: list[str] = []

    snapshot_sha = _sha256_hexdigest(_canonical_json_bytes(snapshot))
    if manifest.get("snapshot_sha256") != snapshot_sha:
        errors.append("snapshot_sha256 mismatch")

    scheme = manifest.get("signature_scheme")
    signer = manifest.get("signer", "")

    if scheme == "HMAC_SHA256_V1":
        if not signing_key:
            errors.append("signing_key required for HMAC_SHA256_V1 verification")
            expected_sig = None
        else:
            expected_sig = hmac.new(
                signing_key.encode("utf-8"), snapshot_sha.encode("utf-8"), hashlib.sha256
            ).hexdigest()
    elif scheme == "SELF_HASH_ATTESTATION_V1":
        expected_sig = _sha256_hexdigest(
            f"{snapshot_sha}|{signer}|{scheme}".encode("utf-8")
        )
    else:
        expected_sig = None
        errors.append(f"unsupported signature scheme: {scheme}")

    if expected_sig is not None and manifest.get("signature") != expected_sig:
        errors.append("signature mismatch")

    manifest_without_hash = dict(manifest)
    actual_manifest_hash = manifest_without_hash.pop("manifest_sha256", None)
    expected_manifest_hash = _sha256_hexdigest(_canonical_json_bytes(manifest_without_hash))
    if actual_manifest_hash != expected_manifest_hash:
        errors.append("manifest_sha256 mismatch")

    return {"valid": not errors, "errors": errors}


def write_snapshot_bundle(
    snapshot: dict[str, Any],
    manifest: dict[str, Any],
    *,
    snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR,
) -> dict[str, Path]:
    bundle_dir = snapshot_dir / str(snapshot["snapshot_id"])
    bundle_dir.mkdir(parents=True, exist_ok=True)

    snapshot_path = bundle_dir / "snapshot.json"
    manifest_path = bundle_dir / "manifest.json"
    snapshot_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True), encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    return {"bundle_dir": bundle_dir, "snapshot_path": snapshot_path, "manifest_path": manifest_path}


def append_run_history(
    snapshot: dict[str, Any],
    manifest: dict[str, Any],
    *,
    history_path: Path = DEFAULT_HISTORY_PATH,
) -> dict[str, Any]:
    history_path.parent.mkdir(parents=True, exist_ok=True)

    gate_evals = snapshot.get("falsification_gate_evaluations", {})
    row = {
        "snapshot_id": snapshot.get("snapshot_id"),
        "created_at_utc": snapshot.get("created_at_utc"),
        "manifest_signature": manifest.get("signature"),
        "manifest_scheme": manifest.get("signature_scheme"),
        "snapshot_sha256": manifest.get("snapshot_sha256"),
        "gate_status": {
            gid: payload.get("status") for gid, payload in gate_evals.items()
        },
        "gate_distance": {
            gid: next(
                (
                    value
                    for key, value in payload.items()
                    if key.startswith("distance_to_")
                ),
                None,
            )
            for gid, payload in gate_evals.items()
        },
    }

    with history_path.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(row, sort_keys=True) + "\n")

    return row


def read_run_history(history_path: Path = DEFAULT_HISTORY_PATH) -> list[dict[str, Any]]:
    if not history_path.exists():
        return []

    rows: list[dict[str, Any]] = []
    for line in history_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def build_trend_panels(
    history: list[dict[str, Any]],
    threshold_metadata: dict[str, Any],
) -> dict[str, Any]:
    panels: dict[str, Any] = {
        "panel_version": "v1",
        "generated_at_utc": _to_utc_z(_utc_now()),
        "history_points": len(history),
        "gates": [],
    }

    for gate in threshold_metadata.get("gates", []):
        gid = gate["id"]
        points: list[dict[str, Any]] = []
        counts = {status: 0 for status in sorted(VALID_GATE_STATUSES)}

        for row in history:
            status = row.get("gate_status", {}).get(gid, "PENDING_EXTERNAL_DATA")
            counts[status] = counts.get(status, 0) + 1
            points.append(
                {
                    "snapshot_id": row.get("snapshot_id"),
                    "created_at_utc": row.get("created_at_utc"),
                    "status": status,
                    "distance_to_threshold": row.get("gate_distance", {}).get(gid),
                }
            )

        panels["gates"].append(
            {
                "id": gid,
                "name": gate.get("name"),
                "observable": gate.get("observable"),
                "points": points,
                "summary_counts": counts,
                "latest_status": points[-1]["status"] if points else gate.get("default_status"),
            }
        )

    return panels


def write_trend_panels(
    trend_panels: dict[str, Any],
    *,
    output_path: Path = DEFAULT_TREND_PANELS_PATH,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(trend_panels, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return output_path
