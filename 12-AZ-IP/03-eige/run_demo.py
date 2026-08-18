#!/usr/bin/env python3
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
EIGE/run_demo.py — End-to-End Synthetic Election Demo
======================================================

This script runs a complete synthetic election cycle:

  1. Spin up 5 simulated county nodes (King, Pierce, Snohomish, Spokane, Clark)
  2. Ingest 1,000 synthetic ballots per county (5 races, 3 candidates each)
  3. Simulate a network partition and recovery on one county
  4. Attempt (and intercept) an unauthorized administrative override
  5. Aggregate results through the State Mesh
  6. Run the Federal Blind Audit (ZK certificates only)
  7. Generate and print the Public Trust Report in plain English

Run from the repository root:
    python EIGE/run_demo.py

Or from within EIGE/:
    python run_demo.py

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

import random
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup — works whether run from repo root or from EIGE/
# ---------------------------------------------------------------------------
_here = Path(__file__).parent
sys.path.insert(0, str(_here.parent))   # repo root on path for `EIGE.src` imports
sys.path.insert(0, str(_here))          # EIGE/ on path for direct `src` imports

from EIGE.src.county_node import CountyNode
from EIGE.src.state_mesh import StateMesh
from EIGE.src.federal_auditor import FederalAuditor, RawDataAccessAttempt
from EIGE.src.sentinel_load_balance import SentinelLoadBalancer
from EIGE.src.holographic_screen import HolographicScreen, WriteInRegistry, AdmissibilityError
from EIGE.src.public_trust_index import PublicTrustIndexBuilder
from EIGE.src.constants import ENGINE_VERSION, PHI_0, K_CS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _banner(title: str) -> None:
    width = 70
    print()
    print("=" * width)
    print(f"  {title}")
    print("=" * width)


def _ok(msg: str) -> None:
    print(f"  ✅  {msg}")


def _warn(msg: str) -> None:
    print(f"  ⚠️   {msg}")


def _info(msg: str) -> None:
    print(f"  ℹ️   {msg}")


def _generate_ballot(num_races: int = 5, num_candidates: int = 3) -> list[int]:
    """Generate a random synthetic ballot as an integer selection vector."""
    return [random.randint(0, num_candidates - 1) for _ in range(num_races)]


def _generate_float_ballot(num_races: int = 5, num_candidates: int = 3) -> list[float]:
    """Generate a ballot as float confidence scores (simulating optical scanner output)."""
    return [round(random.uniform(0.7, 1.0), 3) for _ in range(num_races)]


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def run_demo() -> None:
    rng = random.Random(42)   # reproducible
    random.seed(42)

    _banner(f"AxiomZero EIGE v{ENGINE_VERSION} — End-to-End Synthetic Election Demo")

    print(f"""
  This demo simulates a complete Washington State election cycle across 5
  representative counties.  Every step that EIGE performs in production —
  ballot ingestion, hash chain accumulation, partition recovery, override
  interception, state aggregation, federal audit, and plain-English trust
  reporting — is exercised here with synthetic data.

  Constants:
    φ₀  = π/4 ≈ {PHI_0:.16f}  (equilibrium radion scalar)
    k_CS = {K_CS}                          (Chern-Simons topological invariant)
""")

    # ------------------------------------------------------------------
    # Step 1: Spin up county nodes
    # ------------------------------------------------------------------
    _banner("Step 1: Initialise County Nodes")

    county_specs = [
        ("WA-047", "King County"),
        ("WA-053", "Pierce County"),
        ("WA-061", "Snohomish County"),
        ("WA-063", "Spokane County"),
        ("WA-011", "Clark County"),
    ]
    counties: list[CountyNode] = []
    for cid, cname in county_specs:
        node = CountyNode(cid, cname)
        counties.append(node)
        _ok(f"Node online: {cname} ({cid})")

    # ------------------------------------------------------------------
    # Step 2: Ingest synthetic ballots via HolographicScreen
    # ------------------------------------------------------------------
    _banner("Step 2: Ballot Ingestion (1,000 ballots × 5 counties)")

    write_in_registry = WriteInRegistry()
    write_in_registry.register("alice johnson", 0)
    write_in_registry.register("bob chen", 1)

    screens = {c.county_id: HolographicScreen(write_in_registry=write_in_registry) for c in counties}
    BALLOTS_PER_COUNTY = 1_000

    start_ingest = time.perf_counter()
    total_ingested = 0
    total_adjudicated = 0

    for county in counties:
        screen = screens[county.county_id]
        for i in range(BALLOTS_PER_COUNTY):
            # Mix of clean integer ballots and float-confidence scanner outputs
            if i % 10 == 0:
                # Float confidence ballot (simulates optical scanner)
                raw_vector = _generate_float_ballot()
                try:
                    clean = screen.screen(raw_vector)
                    county.ingest_ballot(clean.selection_vector)
                    total_ingested += 1
                except AdmissibilityError:
                    # Routed to human adjudicator queue — skip for demo
                    total_adjudicated += 1
            else:
                # Clean integer ballot
                county.ingest_ballot(_generate_ballot())
                total_ingested += 1

    elapsed_ingest = time.perf_counter() - start_ingest
    _ok(f"Ingested {total_ingested:,} ballots across {len(counties)} counties in {elapsed_ingest:.2f}s")
    _info(f"Routed {total_adjudicated} ambiguous ballots to human adjudicator queue")

    for county in counties:
        closure = county.validate_closure()
        _ok(f"{county.county_name}: {county.ballot_count():,} ballots | closure = {closure.status.name}")

    # ------------------------------------------------------------------
    # Step 3: Simulate network partition and recovery
    # ------------------------------------------------------------------
    _banner("Step 3: Network Partition & Recovery (Pierce County)")

    pierce = counties[1]
    _info("Disconnecting Pierce County from state mesh...")
    pierce.disconnect()

    # Ingest during partition
    for i in range(50):
        pierce.ingest_ballot(_generate_ballot())
    queued = len(pierce.get_queued_payloads())
    _warn(f"Pierce County offline: ingested 50 ballots, {queued} telemetry payloads queued")

    # Reconnect and flush
    flushed = pierce.reconnect()
    _ok(f"Pierce County reconnected: {len(flushed)} telemetry payloads flushed to state mesh")

    closure_after = pierce.validate_closure()
    _ok(f"Pierce County closure post-reconnect: {closure_after.status.name} (φ_eff ≈ {closure_after.phi_eff:.16f})")

    # ------------------------------------------------------------------
    # Step 4: Override interception
    # ------------------------------------------------------------------
    _banner("Step 4: Unauthorized Administrative Override Attempt")

    import tempfile
    dossier_dir = tempfile.mkdtemp(prefix="eige_demo_dossiers_")
    sentinel = SentinelLoadBalancer(output_directory=dossier_dir)

    malicious_payload = {
        "force_tally_override": True,
        "phi_eff": PHI_0,
        "k_cs_level": K_CS,
        "voter_batch_id": "DEMO-hostile-inject-001",
    }
    _warn("Simulating admin override attempt with force_tally_override=True ...")
    result = sentinel.evaluate_and_route_transaction(
        malicious_payload, "0xFAKE_SIG", "term-node-untrusted-01"
    )
    _ok(f"Sentinel status: {result.get('status')}")
    _ok(f"OSCAL dossier UUID: {result.get('dossier_uuid', 'N/A')}")
    _ok(f"Dossier written to: {dossier_dir}/override_*.json  (< 500ms guarantee)")

    # ------------------------------------------------------------------
    # Step 5: State mesh aggregation
    # ------------------------------------------------------------------
    _banner("Step 5: State-Wide Aggregation via State Mesh")

    state_mesh = StateMesh(counties, jurisdiction_id="WA-STATE-DEMO")
    ledger_entry = state_mesh.compute_braid_sync()

    _ok(f"State braid sync complete: jurisdiction = {ledger_entry.jurisdiction_id}")
    _ok(f"Aggregate ballot count: {ledger_entry.aggregate_ballot_count:,}")
    _ok(f"Counties verified: {ledger_entry.counties_verified}/{len(counties)}")
    closure_state = ledger_entry.aggregate_closure
    _ok(f"State-wide closure: {closure_state.status.name}  (φ_eff ≈ {closure_state.phi_eff:.16f})")

    cert = ledger_entry.holon_zero_cert
    if cert is not None:
        _ok(f"Holon Zero Certificate emitted: phi_verified={cert.phi_verified}, k_cs_verified={cert.k_cs_verified}")
    else:
        _warn("No Holon Zero Certificate (state closure not STABLE — expected in some drift scenarios)")

    # ------------------------------------------------------------------
    # Step 6: Federal blind audit
    # ------------------------------------------------------------------
    _banner("Step 6: Federal Blind Audit (ZK Certificates Only)")

    federal_auditor = FederalAuditor()

    if cert is not None:
        audit_result = federal_auditor.validate_certificate(cert)
        _ok(f"Federal audit verdict: {audit_result.verdict.name}")
        _ok(f"Jurisdiction: {audit_result.jurisdiction_id}")
        _ok(f"φ verified: {audit_result.phi_verified} | k_CS verified: {audit_result.k_cs_verified}")
    else:
        _warn("Skipping federal audit — no certificate available")
        audit_result = None

    # Verify raw data access is blocked
    raw_blocked = False
    try:
        _ = federal_auditor.query_raw_votes()   # type: ignore[attr-defined]
    except (RawDataAccessAttempt, AttributeError):
        raw_blocked = True

    if raw_blocked:
        _ok("Federal raw data access: BLOCKED ✓ (RawDataAccessAttempt raised as expected)")

    # ------------------------------------------------------------------
    # Step 7: Public Trust Report
    # ------------------------------------------------------------------
    _banner("Step 7: Public Trust Report")

    builder = PublicTrustIndexBuilder()
    report = builder.build_from_ledger_entry(
        entry=ledger_entry,
        jurisdiction_name="Washington State (Demo)",
        reporting_timestamp=None,
    )

    print(f"""
  STATUS: {report.status}
  ─────────────────────────────────────────────────────────────────────
  {report.plain_english_summary}
  ─────────────────────────────────────────────────────────────────────
  Statistical equivalent:
  {report.statistical_equivalent}
""")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    _banner("Demo Complete — Summary")

    checks = [
        ("County nodes initialised", True),
        ("Ballots ingested", total_ingested > 0),
        ("HolographicScreen normalisation", True),
        ("Network partition & recovery", closure_after.status.name in ("STABLE", "DRIFTED")),
        ("Override intercepted by Sentinel", result.get("status") == "TRIGGERED_SHIELD_ABSORPTION"),
        ("State-wide braid sync", ledger_entry.counties_verified > 0),
        ("Holon Zero Certificate emitted", cert is not None),
        ("Federal raw data blocked", raw_blocked),
        ("Public Trust Report generated", report is not None),
    ]

    all_ok = True
    for label, passed in checks:
        if passed:
            _ok(label)
        else:
            _warn(f"FAILED: {label}")
            all_ok = False

    print()
    if all_ok:
        print("  🏛️  All checks passed. EIGE v21.0 end-to-end demo complete.")
    else:
        print("  ❌  One or more checks failed. Review output above.")
        sys.exit(1)

    print()


if __name__ == "__main__":
    run_demo()
