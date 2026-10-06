# EIGE — Frequently Asked Questions

*Skeptic FAQ — four audiences: election skeptics, cryptography researchers, privacy advocates, federalism advocates*

---

## For Election Skeptics

**Q: Does EIGE make an election trustworthy by itself?**

No. EIGE is an audit-support and transparency tool. It helps officials and observers verify published records, reconciliation, custody events, and risk-limiting audit calculations. Trust still depends on paper ballots, certified systems, observer access, canvass procedures, and accountable people.

**Q: Can EIGE detect manipulation before a ballot is scanned or logged?**

No. EIGE starts from records it receives. Manipulation of paper before scanning can only be addressed by paper chain of custody and paper audits.

**Q: What does a failed EIGE check mean?**

It means a specific check failed or needs explanation: for example, a signature mismatch, a Merkle consistency failure, a reconciliation discrepancy, or an RLA that has not met the risk limit. It is not by itself evidence of fraud.

**Q: What happened to the Chern-Simons hash and zero-knowledge proof?**

They were retracted as security mechanisms after red-team review. The hash is only a non-security sequence fingerprint. The prior proof format proved nothing and was not zero-knowledge. See [RETRACTED_CLAIMS.md](RETRACTED_CLAIMS.md).

---

## For Cryptography Researchers

**Q: What primitives does v22 use?**

Canonical JSON, RFC 6962/RFC 9162-style SHA-256 Merkle trees, Ed25519 signatures through `cryptography`, witness cosignatures, and Pedersen tally commitments in the quadratic-residue subgroup of RFC 3526 group 14.

**Q: Are the tally commitments zero-knowledge proofs?**

No. They are Pedersen commitments with selective opening for auditors and homomorphic aggregation checks. EIGE v22 makes no zero-knowledge claim.

**Q: Does Ed25519 provide public verification?**

Yes, for signed artifacts. Public keys are listed in `registry.json`, and signatures are domain-separated by context. A valid signature says which key signed a payload; it does not prove the signer was honest.

---

## For Privacy Advocates

**Q: Does EIGE publish raw ballots?**

EIGE publishes CVRs and audit artifacts when a jurisdiction chooses to publish a bundle. CVR publication can create ballot-secrecy risks for rare ballot styles or small groups. Jurisdictions should apply their standard CVR redaction and aggregation rules first.

**Q: Does EIGE expose voter identities?**

The v22 data model is not designed to include voter identities. Deployment procedures must still ensure that logs, manifests, and CVRs do not include personally identifying information.

---

## For Federalism and Election-Administration Audiences

**Q: Does EIGE centralize election control?**

No. It is a publication and verification toolkit. Counties or jurisdictions can produce their own bundles; observers can verify them without control over the election system.

**Q: Is EIGE certified under VVSG 2.0?**

No. EIGE is not a voting system and does not claim VVSG certification. [COMPLIANCE.md](COMPLIANCE.md) maps only the limited controls supported by implemented behavior.

**Q: How should an election office evaluate EIGE?**

Run it in shadow mode on public or test data, compare RLA output with SHANGRLA or Arlo, review CVR privacy implications, test HSM integration if used, and invite independent cryptographic review.
