# EIGE v22 Official Workflow Blueprint

**Version:** 22.0.0  
**Related UI:** `blueprint/OfficialWorkflowCockpit.tsx`

This document describes the operator flow that the official cockpit should implement. EIGE is an audit-support and transparency tool; it does not count votes or replace certified election systems.

## 1. Manifest screen

**Purpose:** Load the election definition, contests, candidates, ballot manifest, and optional cast/provisional counts.

**Shows:**

- Election identifier, jurisdiction, contest list, candidate IDs, `vote_for` values.
- Manifest batches, ballot counts, and expected batch ordering.
- CVR privacy warning for rare ballot styles and small reporting groups.
- Validation status for `election.json`, `manifest.json`, `cast.json`, and `provisional.json`.

**Calls:**

- `eige.model.election` strict parsers.
- `eige.bundle` bundle loading helpers.
- `eige.audit.reconciliation` preflight checks where cast/provisional files are present.

**Sign-offs:**

- Two distinct registered officials acknowledge that the manifest corresponds to the paper inventory before ingest starts.

**Blocking conditions:**

- Invalid election definition.
- Missing required manifest fields.
- Batch totals that cannot be reconciled to the expected ballot inventory.
- Pending CVR redaction decision where the jurisdiction requires redaction before publication.

## 2. Ingest screen

**Purpose:** Log CVRs and custody events, publish signed tree heads, and collect witness cosignatures.

**Shows:**

- Current log size, Merkle root, latest signed tree head, signer key ID, and signing time.
- Batch-level CVR counts in log order. The i-th CVR of a batch in log order is treated as the i-th ballot of that batch in the manifest.
- Witness status and configured witness threshold.
- Development-key warnings, if any.

**Calls:**

- `eige.county` (`python -m eige.county init | commit-manifest | ingest | event | sign-head | status`) for county-scale operation: the log lives in a durable SQLite file (`eige.ledger.store.DurableMerkleLog`), and each CVR export (NIST SP 1500-103 JSON/JSONL or EIGE CSV, via `eige.cvr_import`) is validated in full before anything is logged.
- `eige.canonical` for canonical JSON.
- `eige.ledger.log.MerkleLog` for in-memory append and root calculation (tests and small demonstrations).
- `eige.crypto.signing` for signed tree heads and registry checks.
- `eige.ledger.bulletin` for publishing heads and witness cosignatures.
- `eige.ledger.custody` for seal, transfer, opening, and storage events.

**Sign-offs:**

- Each custody event requires at least two Ed25519 sign-offs from distinct registered officials with role `official`.
- Publishing a signed tree head requires an authorized county or state signing key, depending on the bundle.

**Blocking conditions:**

- Invalid signature or signer role.
- Development key used while production mode is active.
- Same-size different-root head for the same log.
- Missing witness cosignature when a witness threshold is configured.
- Custody event with fewer than two distinct official sign-offs.
- A CVR export with any invalid record, a batch not in the manifest, a repeated CVR id, or a CVR id already in the log (the whole export is refused; nothing is logged).
- An export file that changed while it was being ingested.
- A failed `status --check-integrity` on the county log database.

## 3. Reconcile screen

**Purpose:** Compare CVRs, manifests, cast counts, provisional counts, and reported results before audit or publication.

**Shows:**

- Discrepancy table with code, severity, affected contest/batch, and plain-language reason.
- Vote-opportunity checks: votes + overvotes·vote_for + undervotes = ballots·vote_for.
- Provisional accounting: issued, accepted, rejected, pending, accepted_counted.
- Review notes and operator explanations.

**Calls:**

- `eige.audit.reconciliation`.
- `eige.model.election` result and CVR interpretation helpers.
- `eige.report` for official/court/voter wording.

**Sign-offs:**

- Two distinct officials sign the reconciliation review when all blocking discrepancies are resolved or formally escalated under jurisdiction procedures.

**Blocking conditions:**

- Any blocking reconciliation discrepancy, including duplicate CVR IDs, batches not in manifest, counted-manifest mismatch, cast-count mismatch, vote-opportunity imbalance, missing reported contest, reported-total mismatch, unknown candidate totals, or unresolved provisional imbalance.
- Pending provisionals where jurisdiction rules require resolution before certification.

## 4. Audit screen

**Purpose:** Commit results, run the public seed ceremony, draw samples, enter hand interpretations, and compute RLA status.

**Shows:**

- Committed root and timestamp.
- Public seed, seed generation time, and proof that the seed came after the committed results.
- Sample draw list mapped to manifest batch and position.
- Manual voter records (MVRs) entered for sampled ballots.
- RLA method, risk limit, current risk measure, and escalation status.

**Calls:**

- `eige.audit.sampling` for seed validation and draw mapping.
- `eige.audit.rla` for comparison or polling audit calculations.
- `eige.crypto.merkle` and `eige.ledger.log` for committed roots.
- `eige.report` for audit status language.

**Sign-offs:**

- Two officials record the seed ceremony.
- Two officials confirm each batch retrieval or custody transfer used during hand interpretation, when represented in the custody ledger.

**Blocking conditions:**

- Seed generated before the committed root.
- Sample cannot be mapped to the manifest.
- Missing or uninterpretable MVR without required escalation handling.
- RLA risk limit not met. The workflow must continue sampling or escalate, ultimately to a full hand count.

## 5. Certify & Publish screen

**Purpose:** Assemble the publication bundle, run the verifier, and publish artifacts for observers.

**Shows:**

- Required files: `registry.json`, `log.jsonl`, `heads.json`, `election.json`, `manifest.json`, `results.json`.
- Optional files: `sample.json`, `audit.json`, `commitments.json`, `cosignatures.json`, `provisional.json`, `cast.json`.
- Verification summary by audience: official, court, voter, JSON.
- Out-of-scope list printed by `eige.report`.

**Calls:**

- `python -m eige.county export` to write the bundle from the durable log (refused if records were logged after the last signed head).
- `eige.bundle` to assemble and load the directory.
- `eige.verify` equivalent of `python -m eige.verify bundle DIR --audience official|court|voter|json [--workers N]`.
- For a state canvass, `python -m eige.verify state COUNTY_DIR... --state-results state.json`.
- `eige.crypto.commitments` if `commitments.json` is present.
- `eige.ledger.bulletin` for witness threshold checks.

**Sign-offs:**

- Two officials sign publication approval.
- If a witness threshold is configured, required witness cosignatures must be present before publication is marked ready.

**Blocking conditions:**

- Missing required bundle file.
- Verifier exit code `1` or `2`.
- Any `failed` report item.
- Blocking reconciliation discrepancy unresolved.
- RLA risk not met or escalation incomplete.
- Pending provisionals where jurisdiction rules require resolution.
- Missing witness cosignature when threshold is configured.

## Status semantics

- `verified`: the check passed for the artifact provided.
- `failed`: the check did not pass and must be resolved or escalated.
- `warning`: the check found a condition requiring review but not necessarily blocking.
- `not_checked`: the necessary artifact was absent or the check was out of scope. It is never a pass.
