# AxiomZero EIGE — Election Integrity Governance Engine

**Version:** 22.0.0  
**Epistemic label:** 🔵 ADJACENT TRACK — governance application (not a physics claim)  
**Theory & scientific direction:** ThomasCory Walker-Pearson  
**Code architecture & implementation:** GitHub Copilot (AI)

---

EIGE v22 is an audit-support and public-transparency tool for election officials. It helps publish verifiable election records, reconcile canvass data, run risk-limiting audit calculations, document paper custody, and let observers rerun verification from a publication bundle.

EIGE does **not** count votes. It does **not** replace certified tabulators, paper ballots, canvass procedures, or chain-of-custody law. It is not an end-to-end voter-verifiable cryptographic voting system.

## What changed in v22

A red-team review found that several v21 security claims were unsupported. The Chern-Simons rolling hash is retained only as a non-security sequence fingerprint. The metric-closure detector and prior “zero-knowledge proof” claim are retired. See [RED_TEAM_FINDINGS.md](RED_TEAM_FINDINGS.md) and [RETRACTED_CLAIMS.md](RETRACTED_CLAIMS.md).

The v22 package is `eige/`. The older `src/` package remains for compatibility and demonstration paths, with development-only components refusing production mode where applicable.

## What EIGE detects or checks

| Issue | v22 mechanism |
|---|---|
| Stuffing, deletion, or reordering of logged records after publication | RFC 6962/RFC 9162 Merkle log roots, inclusion proofs, and consistency proofs |
| Forged county data by an unregistered key | Ed25519 signatures and public key registry checks |
| Split views of the public log | Bulletin board, witness cosignatures, and equivocation evidence for conflicting signed heads |
| Outcome-changing tabulation error in sampled ballots | Risk-limiting audit support: comparison audits and ballot-polling BRAVO calculations |
| Count, manifest, provisional, or result mismatch | Canvass reconciliation with blocking/review discrepancy codes |
| Custody gaps for paper containers | Chain-of-custody ledger requiring at least two official sign-offs per event |
| Votes moved between precincts while contest totals stay the same | Precinct (reporting-unit) results recomputed from logged CVRs when results are published by reporting unit |
| The same CVR export ingested twice, or a CVR id reused | All-or-nothing ingest with a unique CVR-id index; duplicate ids fail reconciliation |
| A state roll-up that omits, repeats or alters a county | Statewide verifier: every county bundle, distinct counties, and every county figure and state sum |
| Turnout or residual-vote anomalies | Robust statistical screens labelled only as investigation leads, not evidence |

## What EIGE does not detect

- Manipulation before a ballot is scanned or logged. Only paper custody and audits can check paper reality.
- Dishonest officials who sign false records. Signatures identify the key used; they do not prove the keyholder was honest.
- Compromised certified tabulator firmware, unless the compromise produces records or samples that fail reconciliation or audit checks.
- Ballot-secrecy risks from publishing rare CVR patterns; jurisdictions must apply their own CVR redaction rules.
- A failed or incomplete risk-limiting audit as “fraud.” Failure to meet the risk limit means escalation, potentially to a full hand count.

## Quick start

```bash
cd 12-AZ-IP/03-eige
pip install -r requirements.txt
python -m pytest tests/ -q
python run_demo.py
python -m eige.verify bundle path/to/bundle --audience official
```

For machine-readable artifact specifications, see [docs/FORMATS.md](docs/FORMATS.md).

## County and state scale

EIGE is built to handle a full county or state, not a sample of one:

- **County operations** — `python -m eige.county` keeps the log in a durable SQLite file and streams NIST SP 1500-103 (JSON or JSONL) or CSV exports into it. Each export is validated in full before anything is logged, and a CVR id can never be logged twice. Heads are signed through PKCS#11 (or a development key outside production), results can be tallied per precinct, and the bundle is exported from the database.
- **Verification** — `python -m eige.verify bundle` reads the log in a single streaming pass, in bounded memory, and can split the work across processes with `--workers`; the report is identical either way. Merkle proofs read O(log² n) stored nodes rather than rebuilding the tree.
- **Full-population checks** — results by reporting unit, risk-limiting audits of every contest from one sample (`eige.audit_input.v2`), conservative handling of lost ballots, and `python -m eige.verify state` for the statewide roll-up.

Measured throughput and memory, and the method for reproducing them, are in [SCALE.md](SCALE.md).

## Official workflow

1. **Manifest** — load election definitions and ballot manifests.
2. **Ingest** — log CVRs (`python -m eige.county ingest`), publish signed tree heads, and collect witness cosignatures.
3. **Reconcile** — compare manifests, CVRs, cast counts, provisional counts, and reported results.
4. **Audit** — commit results, hold a public seed ceremony, draw samples, hand-interpret sampled ballots, and run RLA calculations.
5. **Certify & publish** — export the bundle (`python -m eige.county export`), run `python -m eige.verify bundle ...`, and for a state canvass `python -m eige.verify state ...`.

The UI flow is specified in [blueprint/OFFICIAL_WORKFLOW.md](blueprint/OFFICIAL_WORKFLOW.md).

## Repository structure

| Path | Purpose |
|---|---|
| `eige/` | v22 implementation: canonical JSON, signing, Merkle log (in-memory and durable), CVR import, county CLI, reconciliation, RLA, custody, streaming/parallel bundle verifier, statewide verifier |
| `tools/scale_benchmark.py` | reproducible scale measurements (see `SCALE.md`) |
| `src/` | legacy v21 compatibility modules; not the basis for v22 security claims |
| `tests/` | regression and behavior tests |
| `docs/FORMATS.md` | artifact and bundle specification |
| `blueprint/` | UI and operator workflow blueprints |
| `outreach/` | engagement material for review and pilots |
| `paper/` | research preprint material with v22 retraction notice |

## Related documents

- [RED_TEAM_FINDINGS.md](RED_TEAM_FINDINGS.md)
- [RETRACTED_CLAIMS.md](RETRACTED_CLAIMS.md)
- [THREAT_MODEL.md](THREAT_MODEL.md)
- [COMPLIANCE.md](COMPLIANCE.md)
- [SECURITY.md](SECURITY.md)
