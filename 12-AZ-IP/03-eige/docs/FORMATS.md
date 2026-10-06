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

EIGE v22 parses strict election definitions, CVRs, ballot manifests, and result reports. These files may use EIGE native JSON or the supported NIST shapes:

- NIST SP 1500-103 CVR subset through `cvr_to_nist` / `cvr_from_nist`; CVR JSON root shape: `CVR.CVR`.
- NIST SP 1500-100 ERR subset through `results_report`.

The manifest identifies batches and ballot positions. The convention for CVR-to-paper mapping is: the i-th CVR of a batch in Merkle-log order is the i-th ballot of that batch in the manifest.

Overvotes, undervotes, and votes are reconciled using vote-opportunity identity:

```text
votes + overvotes * vote_for + undervotes = ballots * vote_for
```

## Sample record (`sample.json`)

Format name: `eige.sample.v1`.

```json
{
  "format": "eige.sample.v1",
  "committed_root": "hex sha256 results/log root",
  "seed": "12345678901234567890",
  "seed_generated_at": 1791310000,
  "population_size": 100000,
  "draws": [
    {"draw": 1, "number": 48123, "batch_id": "batch-17", "position": 93}
  ]
}
```

The public seed must contain at least 20 decimal digits and must be generated after the committed results root. Draw `i` is `1 + SHA256(f"{seed},{i}") mod N`, mapped to manifest batch and position. Escalation continues the same sequence rather than starting over.

## Audit input (`audit.json`)

Format name: `eige.audit_input.v1`.

```json
{
  "format": "eige.audit_input.v1",
  "contest_id": "mayor",
  "method": "comparison",
  "risk_limit": "0.05",
  "mvrs": [
    {"draw": 1, "selections": ["candidate-a"]},
    {"draw": 2, "selections": null}
  ]
}
```

`method` is `"comparison"` or `"polling"`. `selections: null` means the sampled ballot could not be interpreted from the manual voter record and must be handled under jurisdiction procedures. Failing to meet the risk limit means escalation, ultimately to a full hand count.

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

`cast.json`:

```json
{
  "jurisdiction": "Example County",
  "ballots_cast": 10000,
  "batches": [{"batch_id": "batch-1", "ballots_cast": 200}]
}
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

`log.jsonl` contains one canonical JSON object per line before hashing. Verifiers recompute roots, signatures, results from logged CVRs, reconciliation, sampling, RLA calculations, commitments, and witness cosignatures.

## Verifier commands and exit codes

```bash
python -m eige.verify bundle DIR --audience official|court|voter|json
python -m eige.verify inclusion ...
python -m eige.verify consistency ...
```

Exit codes:

- `0`: verification completed with no failed checks.
- `1`: one or more checks failed.
- `2`: usage, input/output, or bundle parsing error.

A `not_checked` item is never a pass. It means the artifact needed for that check was absent or out of scope.
