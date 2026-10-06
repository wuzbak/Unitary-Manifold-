# EIGE v22 File Formats

**Version:** 22.0.0  
**Epistemic label:** 🔵 ADJACENT TRACK — governance application (not a physics claim)

This document specifies the public artifacts used by EIGE v22. Test vectors live in `test_vectors/` and are maintained with the implementation.

## Scope and privacy

EIGE publishes election audit-support artifacts so officials, observers, courts, and voters can independently recompute log roots, signatures, reconciliation checks, audit samples, and commitments. EIGE does not count votes and does not replace certified tabulators, paper ballots, canvass procedures, or risk-limiting audit law.

Publishing CVRs can risk ballot secrecy for rare ballot styles, small precincts, or unusual write-ins. Jurisdictions should apply their standard CVR redaction and aggregation rules before publication.

## Canonical JSON

All signed, hashed, or committed JSON uses `eige.canonical`:

- UTF-8 bytes.
- Objects sorted by key.
- Compact separators: `,` and `:` with no insignificant whitespace.
- Strings encoded as JSON strings.
- Integers allowed.
- Floats rejected. Use integer counts, decimal strings, or explicit numerator/denominator fields.
- Arrays remain in given order.
- No duplicate object keys.

The canonical bytes are the only bytes used for hashes and signatures.

## Signing

Ed25519 signatures use domain-separated messages:

```text
b"EIGE-v22/" + context + b"\x00" + canonical_json(payload)
```

`context` is an ASCII byte string such as `b"sth"` or `b"cosignature"`. `key_id` is:

```text
ed25519:<first 16 bytes of SHA-256(public_key), hex>
```

Development keys are for demos and tests only. Production verification should reject development keys unless explicitly configured otherwise.

## Merkle log hashing

EIGE uses the RFC 6962/RFC 9162 Merkle tree convention with SHA-256:

- Leaf hash: `SHA256(0x00 || canonical_json(record))`
- Node hash: `SHA256(0x01 || left_hash || right_hash)`
- The empty tree root is `SHA256(b"")`.

Records are dictionaries with a required `type` field. A logged CVR record is:

```json
{"type":"cvr","cvr":{...}}
```

Inclusion and consistency proofs follow the RFC 6962 audit-path model. Proof fields are hex-encoded SHA-256 hashes.

## Signed tree head (`heads.json`)

Format name: `eige.sth.v1`.

A signed tree head has:

```json
{
  "format": "eige.sth.v1",
  "log_id": "example-county-2026-general",
  "tree_size": 12345,
  "root_hash": "hex sha256 root",
  "timestamp": 1791300000,
  "key_id": "ed25519:...",
  "alg": "Ed25519",
  "signature": "hex ed25519 signature"
}
```

The signed payload is the same object without `signature`. The signature is over `signing_message("sth", payload_without_signature)`. The `alg` field is included in the signed payload.

## Key registry (`registry.json`)

Format name: `eige.key_registry.v1`.

```json
{
  "format": "eige.key_registry.v1",
  "keys": [
    {
      "key_id": "ed25519:...",
      "alg": "Ed25519",
      "public_key": "hex raw public key",
      "owner": "Example County",
      "role": "official|county|state|witness|auditor",
      "created_at": 1791200000,
      "valid_from": 1791200000,
      "valid_until": null,
      "revoked_at": null,
      "compromised": false,
      "development": false
    }
  ]
}
```

Rotation sets `valid_until` on the replaced key and registers a new key. Revocation sets `revoked_at`; if `compromised` is true, signatures by that key are rejected regardless of signing time.

## Witness cosignatures (`cosignatures.json`)

Format name: `eige.cosignature.v1`.

```json
{
  "format": "eige.cosignature.v1",
  "log_id": "example-county-2026-general",
  "tree_size": 12345,
  "root_hash": "hex sha256 root",
  "sth_signature": "hex original sth signature",
  "witness_id": "observer-1",
  "key_id": "ed25519:...",
  "alg": "Ed25519",
  "timestamp": 1791300010,
  "signature": "hex ed25519 signature"
}
```

The signature is over `signing_message("cosignature", payload_without_signature)`. A witness signs only if the head is consistent with its previous view. Two valid signed heads for the same `log_id` and `tree_size` with different roots are equivocation evidence.

## Election, contest, candidate, CVR, manifest, and results files

EIGE parses strict election definitions, CVRs, ballot manifests, and result reports. These files may use EIGE native JSON or the supported NIST shapes:

- NIST SP 1500-103 CVR subset through `cvr_to_nist` / `cvr_from_nist`; CVR JSON root shape: `CVR.CVR`.
- NIST SP 1500-100 ERR subset through `results_report` / `results_from_totals`.

An EIGE CVR is:

```json
{"id": "B000017-00042", "batch_id": "B000017", "ballot_style": "odd",
 "reporting_unit": "P0017", "selections": {"c00": ["a"], "c01": [], "c03": ["a", "b"]}}
```

A contest key that is present with an empty list is an undervote; more marks than `vote_for` is an overvote; a contest that is absent was not on that ballot style. `reporting_unit` (precinct or other GpUnit) is optional, but it is required for precinct-level results to be checked.

The manifest identifies batches and ballot positions. The convention for CVR-to-paper mapping is: the i-th CVR of a batch in Merkle-log order is the i-th ballot of that batch in the manifest. Batches with `ballot_count: 0` are allowed and are never sampled.

Overvotes, undervotes, and votes are reconciled using vote-opportunity identity:

```text
votes + overvotes * vote_for + undervotes = ballots * vote_for
```

### Results and reporting-unit (precinct) results

`results.json` follows the ERR subset produced by `results_report`. Each candidate's `VoteCounts` entries are disjoint parts of its total. When every entry's `GpUnitId` is the jurisdiction, the verifier checks contest totals only and reports **Reporting-unit (precinct) results: not checked**. When entries name reporting units, the verifier recomputes every (contest, unit, candidate) figure from the logged CVRs and reports each difference as `REPORTED_UNIT_TOTAL_MISMATCH`; a CVR without `reporting_unit` in that case is `CVR_REPORTING_UNIT_MISSING`. Votes moved from one precinct to another therefore fail verification even when the contest total is unchanged.

### CVR import formats (`python -m eige.county ingest --format ...`)

| Format | Input | Notes |
|---|---|---|
| `nist-json` | one NIST SP 1500-103 `CVR.CastVoteRecordReport` document | The `CVR` array is parsed incrementally (constant memory). If `Election` appears before `CVR` and maps `ContestSelection` ids to a single `CandidateIds` entry, selection ids are translated; otherwise the selection id must equal the EIGE candidate id. The `CurrentSnapshotId` snapshot is used. Positions with `IsAllocable: "no"` are dropped unless the contest reports `Overvotes > 0`, in which case all indicated marks are kept so the ballot remains an overvote. `BallotStyleUnitId` becomes `reporting_unit`. |
| `nist-jsonl` | one `CVR.CVR` object per line | Same conversion, no `Election` mapping. |
| `csv` | header `cvr_id,batch_id,ballot_style[,reporting_unit],<contest_id>...` | Contest cells hold `|`-separated candidate ids; an empty cell is an undervote; `~` means the contest is not on that ballot. |

Vendor-proprietary exports must be converted to one of these formats first. That conversion is jurisdiction-specific and outside EIGE.

## Sample record (`sample.json`)

Format name: `eige.sample.v1`.

```json
{
  "format": "eige.sample.v1",
  "seed": "12345678901234567890",
  "population": 100000,
  "committed_root": "hex SHA-256 root of a signed tree head",
  "seed_generated_at": 1791310000,
  "draws": [
    {"draw": 1, "position": 48123, "batch_id": "batch-17", "index_in_batch": 93}
  ]
}
```

The public seed must contain at least 20 decimal digits and must be generated after the committed root was signed (`seed_generated_at` ≥ the head's timestamp). `population` must equal the manifest total. Draw `i` maps to position `1 + SHA256(f"{seed},{i}") mod N` and then to a manifest batch and 1-based index. Escalation continues the same sequence rather than starting over.

## Audit input (`audit.json`)

Two formats are accepted.

`eige.audit_input.v1` audits one contest:

```json
{
  "format": "eige.audit_input.v1",
  "contest_id": "mayor",
  "method": "comparison",
  "risk_limit": 0.05,
  "mvrs": [
    {"draw": 1, "selections": ["candidate-a"]},
    {"draw": 2, "selections": null}
  ]
}
```

`eige.audit_input.v2` audits several contests from the same sample (one hand interpretation per ballot):

```json
{
  "format": "eige.audit_input.v2",
  "contests": [
    {"contest_id": "governor", "method": "comparison", "risk_limit": 0.05},
    {"contest_id": "measure-1", "method": "polling", "risk_limit": 0.10}
  ],
  "mvrs": [
    {"draw": 1, "selections": {"governor": ["a"], "measure-1": []}},
    {"draw": 2, "selections": null}
  ]
}
```

In v2, a contest absent from a ballot's `selections` was not on that ballot. Every audited `draw` must appear in `sample.json`.

`method` is `"comparison"` (Kaplan–Markov with per-assertion overstatements) or `"polling"` (BRAVO). `selections: null` means the sampled ballot could not be found. EIGE treats a missing ballot conservatively: in a comparison audit it is a two-vote overstatement for every assertion, and in a polling audit it counts as a vote for the reported loser. A sampled position with no logged CVR is treated the same way. Neither can help confirm an outcome. Failing to meet the risk limit means escalation, ultimately to a full hand count.

## Commitment bundle (`commitments.json`)

Format name: `eige.commitment_bundle.v1`.

Pedersen commitments are in the quadratic-residue subgroup of RFC 3526 group 14. `g=4`; `h` is derived from the public seed using SHAKE-256 and squared into the subgroup. Commitments are perfectly hiding and computationally binding under the stated group assumptions. EIGE makes no zero-knowledge proof claim.

```json
{
  "format": "eige.commitment_bundle.v1",
  "group": "RFC3526-group14-QR",
  "seed": "public generator seed",
  "parts": [
    {
      "jurisdiction": "Example County",
      "contest_id": "mayor",
      "commitments": {"candidate-a": "hex", "candidate-b": "hex"}
    }
  ],
  "state": {
    "contest_id": "mayor",
    "commitments": {"candidate-a": "hex", "candidate-b": "hex"}
  },
  "state_opening": {
    "candidate-a": {"value": 1200, "randomness": "hex"},
    "candidate-b": {"value": 1000, "randomness": "hex"}
  }
}
```

County commitments multiply into the state commitment. The state opening is checked against the published state commitment.

## Provisional and cast records

`provisional.json`:

```json
{
  "issued": 42,
  "accepted": 30,
  "rejected": 10,
  "pending": 2,
  "accepted_counted": 30
}
```

`cast.json` maps each manifest batch to the number of ballots cast according to pollbooks or check-in records:

```json
{"batch-1": 200, "batch-2": 187}
```

Pending provisionals and mismatches between accepted and accepted-counted provisionals are reconciliation issues, not fraud findings.

## Chain-of-custody records

Custody event types are `seal_applied`, `seal_verified`, `seal_broken`, `transfer`, `container_opened`, and `storage_check`. Each event requires at least two Ed25519 sign-offs from distinct registered officials with role `official`. Custody events are appended to the Merkle log. Verification flags seal mismatches, openings without a prior seal break, transfers from the wrong custodian or without a seal, and backwards timestamps.

## Bundle layout

A publication bundle is a directory. Required files:

```text
registry.json
log.jsonl
heads.json
election.json
manifest.json
results.json
```

Optional files:

```text
sample.json
audit.json
commitments.json
cosignatures.json
provisional.json
cast.json
```

`log.jsonl` contains one canonical JSON object per line, each terminated by `\n`. It is streamed, so it has no total size limit; a single entry may not exceed 4 MiB, and a final line without `\n` is reported as **Log file readable: failed** (a truncated download or file). Each JSON document other than the log may not exceed 512 MiB. Verifiers recompute roots, signatures, results from logged CVRs, reconciliation, sampling, RLA calculations, commitments, and witness cosignatures.

Log entries written by `eige.county` are:

| `type` | Content |
|---|---|
| `manifest_committed` | `details.sha256` = SHA-256 of the canonical manifest |
| `cvr_import` | `details` = source file name, SHA-256, format and record count; precedes that file's CVRs |
| `cvr` | `cvr` = the normalized EIGE CVR |
| other | administrative events, e.g. chain-of-custody records, logged with `eige.county event` |

### County log database

`eige.county` keeps the log in a SQLite file (WAL mode, `synchronous=FULL`) holding the leaf bytes, the stored Merkle nodes of every complete subtree, signed heads, and a unique-key index of logged CVR ids. Each batch of appends is one transaction, so a crash leaves every committed batch and nothing of a partial one. `status --check-integrity` recomputes every leaf hash and the root from the stored bytes and rechecks every stored head. The database is an operational store, not a publication artifact: only the exported bundle is public.

### State results (`python -m eige.statewide`)

A state roll-up uses the results format with `Jurisdiction` set to the state and one `VoteCounts` entry per county whose `GpUnitId` is that county's jurisdiction id. The statewide verifier verifies every county bundle; checks that all bundles describe the same election and are distinct counties (no repeated jurisdiction, log id, or root); and, if state results are supplied, checks that each county figure equals that county's published total and each state total equals the sum of the county figures.

## Verifier commands and exit codes

```bash
python -m eige.verify bundle DIR --audience official|court|voter|json [--workers N]
python -m eige.verify state DIR [DIR ...] [--state-results FILE] [--workers N]
python -m eige.verify inclusion ...
python -m eige.verify consistency ...
```

`--workers` splits the log scan across processes; the report is identical to a single-process run (`--workers 0` uses every CPU).

Exit codes:

- `0`: verification completed with no failed checks.
- `1`: one or more checks failed.
- `2`: usage, input/output, or bundle parsing error.

A `not_checked` item is never a pass. It means the artifact needed for that check was absent or out of scope.
