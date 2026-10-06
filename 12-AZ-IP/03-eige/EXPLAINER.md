# EIGE — What It Is and Why It Matters

## A 5-Minute Explainer

*For election officials, journalists, policy makers, and voters*

---

## The problem

Election records are hard for the public to verify. A final result may depend on CVRs, ballot manifests, custody records, provisional-ballot accounting, sampled paper ballots, and canvass reconciliation. Those records often exist, but they are not always published in a form that independent observers can recompute.

## The v22 approach

EIGE v22 packages standard audit-support tools into one publication workflow:

- append-only Merkle logs for published election records;
- Ed25519 signatures tied to a public key registry;
- witness cosignatures to detect split views;
- canvass reconciliation checks;
- public-seed sampling for audits;
- RLA calculations for comparison and polling audits;
- custody records with two-person sign-offs;
- a standalone verifier for officials, courts, voters, and JSON output.

## What EIGE does

| What EIGE does | How it works |
|---|---|
| Publishes records that can be recomputed | Canonical JSON, Merkle roots, inclusion proofs, and consistency proofs |
| Checks signer authority | Ed25519 signatures and a public key registry with owner/role/time checks |
| Detects split views after publication | Witness cosignatures and bulletin-board consistency checks |
| Supports paper audits | Public-seed sampling and RLA calculations |
| Flags accounting mismatches | Reconciliation codes with plain reasons |
| Documents paper custody | Custody ledger with two distinct official sign-offs |

## What EIGE does not do

| EIGE cannot | Why |
|---|---|
| Count votes | Certified tabulators and canvass procedures remain the source of official counts |
| Replace paper ballots | Only paper can check whether electronic records reflect voter-marked ballots |
| Detect manipulation before scanning/logging | EIGE verifies records after they exist |
| Prove a signer was honest | A signature identifies a key, not the signer’s intent |
| Turn statistical leads into fraud findings | Outlier screens are investigation leads only |

## How to verify a bundle

```bash
cd 12-AZ-IP/03-eige
pip install -r requirements.txt
python -m pytest tests/ -q
python run_demo.py
python -m eige.verify bundle path/to/bundle --audience voter
```

The verifier reports each check as `verified`, `failed`, `warning`, or `not_checked`. `not_checked` is never a pass.

## What changed from v21

The previous Chern-Simons rolling hash, metric-closure detector, and claimed zero-knowledge proof are no longer security claims. They were retracted after review. See [RETRACTED_CLAIMS.md](RETRACTED_CLAIMS.md).
