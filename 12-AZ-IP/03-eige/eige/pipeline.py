# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""End-to-end workflow helpers: manifest → ingest → reconcile → audit → certify → publish.

:class:`CountyPublisher` is what a county runs.  :func:`build_synthetic_bundle`
produces a complete, deterministic synthetic election bundle used by the demo,
the test-vector generator and the adversarial test-suite.  Synthetic bundles
are signed with development-only keys and say so.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

from .audit import rla
from .audit.sampling import draw_sample, sample_record
from .bundle import write_bundle
from .canonical import canonical_bytes
from .crypto import commitments as cm
from .crypto.signing import DevelopmentSigner, KeyRegistry, Signer
from .ledger.bulletin import Witness
from .ledger.log import MerkleLog, SignedTreeHead
from .model.election import CVR, Election, parse_election, parse_manifest, results_report, tally


@dataclass
class CountyPublisher:
    """A county's append-only log of CVRs and administrative events plus its signed heads."""

    log_id: str
    signer: Signer
    log: MerkleLog = field(init=False)
    heads: List[SignedTreeHead] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.log = MerkleLog(self.log_id)

    def log_cvr(self, cvr: dict) -> int:
        return self.log.append({"type": "cvr", "cvr": cvr})

    def log_event(self, event_type: str, details: dict) -> int:
        return self.log.append({"type": event_type, "details": details})

    def publish_head(self, timestamp: int) -> SignedTreeHead:
        head = self.log.sign_head(self.signer, timestamp)
        self.heads.append(head)
        return head


def _seed32(label: str) -> bytes:
    return hashlib.sha256(b"EIGE synthetic development key / " + label.encode()).digest()


SYNTHETIC_ELECTION = {
    "id": "synthetic-2026-general",
    "name": "Synthetic County General Election (test data)",
    "date": "2026-11-03",
    "jurisdiction": "SYNTH-COUNTY",
    "contests": [
        {"id": "mayor", "name": "Mayor", "vote_for": 1, "candidates": [
            {"id": "alvarez", "name": "R. Alvarez"}, {"id": "brooks", "name": "T. Brooks"}, {"id": "chen", "name": "M. Chen"}]},
        {"id": "measure-1", "name": "Measure 1", "vote_for": 1, "candidates": [
            {"id": "yes", "name": "Yes"}, {"id": "no", "name": "No"}]},
    ],
}


def synthetic_cvrs(n_batches: int, per_batch: int, rng: random.Random) -> List[dict]:
    cvrs = []
    for b in range(n_batches):
        for i in range(per_batch):
            r = rng.random()
            mayor = ["alvarez"] if r < 0.52 else ["brooks"] if r < 0.85 else ["chen"] if r < 0.97 else []
            if rng.random() < 0.005:
                mayor = ["alvarez", "brooks"]  # overvote
            measure = ["yes"] if rng.random() < 0.58 else ["no"]
            cvrs.append({"id": f"B{b:02d}-{i + 1:04d}", "batch_id": f"B{b:02d}", "ballot_style": "1",
                         "selections": {"mayor": mayor, "measure-1": measure}})
    return cvrs


def build_synthetic_bundle(
    directory: str | Path,
    n_batches: int = 4,
    per_batch: int = 250,
    rng_seed: int = 2026,
    public_seed: str = "31415926535897932384",
    tamper: Optional[Callable[[Dict], None]] = None,
) -> Dict:
    """Build a full bundle; ``tamper`` may mutate the in-memory state before writing (for tests)."""
    rng = random.Random(rng_seed)
    election: Election = parse_election(SYNTHETIC_ELECTION)
    county_signer = DevelopmentSigner(_seed32("county"))
    witness_signer = DevelopmentSigner(_seed32("witness"))
    registry = KeyRegistry()
    registry.register_signer(county_signer, owner="SYNTH-COUNTY", role="county-log", valid_from=0)
    registry.register_signer(witness_signer, owner="observer-university", role="witness", valid_from=0)

    manifest_doc = {"jurisdiction": "SYNTH-COUNTY", "batches": [
        {"batch_id": f"B{b:02d}", "ballot_count": per_batch, "container_id": f"BOX-{b:02d}", "tabulator_id": "TAB-1"}
        for b in range(n_batches)]}
    manifest = parse_manifest(manifest_doc)
    cvr_docs = synthetic_cvrs(n_batches, per_batch, rng)

    pub = CountyPublisher("SYNTH-COUNTY", county_signer)
    pub.log_event("manifest_committed", {"sha256": hashlib.sha256(canonical_bytes(manifest_doc)).hexdigest()})
    half = len(cvr_docs) // 2
    for c in cvr_docs[:half]:
        pub.log_cvr(c)
    pub.publish_head(1_793_700_000)
    for c in cvr_docs[half:]:
        pub.log_cvr(c)
    head = pub.publish_head(1_793_710_000)

    from .model.election import parse_cvrs
    cvrs: List[CVR] = parse_cvrs(cvr_docs, election)
    results = results_report(election, cvrs)
    totals = tally(election, cvrs)
    mayor = election.contest("mayor")
    reported = dict(totals["mayor"].candidate_votes)

    n = rla.comparison_sample_size(mayor, reported, manifest.total_ballots, 0.05)
    draws = draw_sample(public_seed, manifest, n)
    sample = sample_record(public_seed, manifest, draws)
    sample["committed_root"] = head.root_hash
    sample["seed_generated_at"] = 1_793_720_000
    by_pos = {}
    for c in cvr_docs:
        by_pos.setdefault(c["batch_id"], []).append(c)
    mvrs = [{"draw": d.draw_number, "selections": list(by_pos[d.batch_id][d.index_in_batch - 1]["selections"]["mayor"])}
            for d in draws]
    audit = {"format": "eige.audit_input.v1", "contest_id": "mayor", "method": "comparison", "risk_limit": 0.05, "mvrs": mvrs}

    # Two half-county commitments combine homomorphically into the county total.
    parts, openings = [], []
    for label, chunk in (("SYNTH-COUNTY/precincts-A", cvrs[:half]), ("SYNTH-COUNTY/precincts-B", cvrs[half:])):
        t = tally(election, chunk)["mayor"].candidate_votes
        rnd = {k: int.from_bytes(hashlib.sha256(f"{label}/{k}".encode()).digest(), "big") for k in t}
        pc, po = cm.commit_tallies(label, "mayor", t, randomness=rnd)
        parts.append(pc)
        openings.append(po)
    state = cm.aggregate(parts, "SYNTH-COUNTY")
    state_open = cm.aggregate_openings(openings)
    commitments = {
        "format": "eige.commitment_bundle.v1",
        "parts": [p.as_dict() for p in parts],
        "state": state.as_dict(),
        "state_opening": {k: {"value": o.value, "randomness": format(o.randomness, "x")} for k, o in state_open.items()},
    }

    witness = Witness("observer-university", witness_signer, registry)
    witness.cosign(pub.heads[0])
    cosig = witness.cosign(head, pub.log.consistency_proof(pub.heads[0].tree_size))

    state_doc = {
        "files": {
            "registry.json": registry.as_dict(),
            "heads.json": [h.as_dict() for h in pub.heads],
            "election.json": SYNTHETIC_ELECTION,
            "manifest.json": manifest_doc,
            "results.json": results,
            "sample.json": sample,
            "audit.json": audit,
            "commitments.json": commitments,
            "cosignatures.json": [cosig.as_dict()],
            "provisional.json": {"issued": 12, "accepted": 9, "rejected": 3, "pending": 0, "accepted_counted": 9},
            "cast.json": {b.batch_id: b.ballot_count for b in manifest.batches},
        },
        "entries": pub.log.entries(),
        "signers": {"county": county_signer, "witness": witness_signer},
        "publisher": pub,
    }
    if tamper is not None:
        tamper(state_doc)
    write_bundle(directory, state_doc["files"], state_doc["entries"])
    return state_doc
