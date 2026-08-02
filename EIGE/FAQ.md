# EIGE — Frequently Asked Questions

*Skeptic FAQ — four audiences: election skeptics, cryptography researchers, privacy advocates, federalism advocates*

---

## For Election Skeptics

**Q: I don't trust the current election system. Does EIGE make it trustworthy?**

EIGE is specifically designed for this concern. It does not ask you to trust election administrators. It asks you to verify mathematics.

The core property is: if the ballot sequence was manipulated after ingestion into EIGE, the mathematical fingerprint will be different from what it should be. That difference is machine-readable, deterministic, and requires no expert interpretation. You can verify it yourself by running the open-source test suite.

What EIGE cannot do: it starts at the moment a ballot enters the scanner. It does not cover what happens to paper ballots before scanning. For full election integrity, EIGE must be combined with robust paper chain-of-custody — which it is designed to complement, not replace.

---

**Q: Can EIGE be configured to produce a "VERIFIED" result even when something went wrong?**

No. The VERIFIED/WATCH/ALERT status is a deterministic output of the mathematical invariant. There is no configuration parameter that makes a manipulated sequence produce a VERIFIED result.

The one partial exception: if EIGE itself is not running during the counting process, it cannot detect manipulation that occurred before it was activated. This is why we recommend that EIGE be activated at the beginning of the counting process, not installed retroactively after certification.

---

**Q: Who controls EIGE? Can the company running it tamper with results?**

EIGE is fully open-source and released to the public domain under the Defensive Public Commons License. There is no proprietary component, no closed-source library, no "phone home" call. Any election jurisdiction can:

1. Download the source code
2. Verify every line independently
3. Run it on their own infrastructure
4. Never contact AxiomZero again

The AxiomZero organisation cannot modify results that have already been recorded in the hash chain.

---

**Q: What if the people running EIGE conspire to change the results?**

This is exactly what the Override Interception architecture is designed to detect. Any administrative override attempt generates an OSCAL dossier record within 500 milliseconds — an atomic write to disk that goes to both the local audit log and the public transparency dashboard.

The dossier includes: timestamp, operator identity, hardware cryptographic signature, and the specific action attempted. An administrator who attempts a conspiracy has a public paper trail before they can complete the action.

Additionally, the three-tier architecture requires that the state and county tiers are operated by independent jurisdictions. A conspiracy would require simultaneous compromise of all tiers, each of which generates independent audit records.

---

**Q: Is this the same as blockchain voting?**

No. Key differences:

- EIGE does not store ballot data on a public ledger
- Raw ballot data never leaves the county node
- There is no central blockchain database
- Federal oversight is achieved through zero-knowledge certificates — the federal government receives a proof that the sequence was valid, not the sequence itself

See [EXPLAINER.md](EXPLAINER.md) for a comparison table.

---

## For Cryptography Researchers

**Q: Is the Chern-Simons rolling hash a cryptographic hash?**

**No. Explicitly not.** The CS rolling hash is a tamper-detection invariant, not a cryptographic hash function. Specifically:

- It does not have the preimage resistance of SHA-256 or SHA-3
- It should not be used as a standalone secret-preserving commitment scheme
- Its security property is **non-commutativity and sequence-position encoding**, not collision resistance in the cryptographic sense

The full audit trail relies on:
- SHA-512 block hashes (cryptographic-standard shard fingerprints)
- HMAC-SHA-512 signatures over shard telemetry packets
- TLS 1.3 mTLS transport between tiers

The CS hash provides the **sequence integrity layer**. SHA-512 / HMAC provide the **cryptographic authentication layer**. These are complementary.

---

**Q: What is the security proof for the CS hash?**

We provide informal security arguments in the arXiv preprint (Section 3). Specifically:

- **Non-commutativity:** the XOR term `(s_n >> 7)` introduces state-dependent non-linearity that makes `hash([a,b,c]) ≠ hash([b,a,c])` for virtually all permutations. The Mersenne prime modulus eliminates small-order subgroup exploits.

- **Insertion detection:** inserting ballot `b'` at position k propagates a perturbation through all subsequent hash states via the multiplicative `K_CS` term, with residual probability `1/M ≈ 10^{-19}`.

These are not formal proofs. A formal security proof — and an independent cryptographic review — is a Phase 2 deliverable. We are actively seeking cryptography researchers willing to provide an independent assessment. See [SECURITY.md](SECURITY.md).

---

**Q: Why use a Mersenne prime (M63 = 2^63 − 1) as the hash modulus?**

- Mersenne primes admit efficient modular reduction without full division
- `M63 = 2^63 − 1` has no small-factor subgroup structure that could be exploited to construct commuting ballot pairs
- The state space {0, ..., M-1} has approximately 9.2 × 10^18 elements — large enough that birthday attacks are infeasible for realistic ballot counts

---

**Q: What is the Holon Zero Certificate? Is it a real ZK proof?**

In v21.0, the Holon Zero Certificate is a **commitment-scheme architecture**, not a formal zero-knowledge proof in the cryptographic sense (e.g., zk-SNARK, Pedersen commitment). It proves that the state mesh validated `φ_verified = True` and `k_cs_verified = True` without transmitting raw ballot data.

We are explicit about this limitation in [BOOK.md §17](BOOK.md#17-known-limitations-and-open-problems) and in the arXiv preprint. A formal ZK proof construction is a Phase 2 deliverable.

---

**Q: How can I test the hash security myself?**

Run the EIGE test suite and look at:
- `tests/test_eige_chern_simon_hash.py` — non-commutativity and avalanche tests
- `tests/test_eige_chaos_injection.py` — adversarial noise and replay attack tests
- `tests/test_eige_chaos_integration.py` — full-pipeline adversarial scenarios

Or see [SECURITY.md](SECURITY.md) for the open cryptanalysis challenge.

---

## For Privacy Advocates

**Q: Does EIGE create a federal database of ballots or voter choices?**

**No.** This is the primary design motivation of the three-tier sovereignty architecture.

- Raw ballot data (which candidate a voter chose) **never leaves the county node**
- The state tier receives only: ballot counts, hash states, and HMAC-signed summaries — no selections
- The federal tier receives only: a zero-knowledge certificate with two boolean fields (`phi_verified`, `k_cs_verified`) — no counts, no selections, no county data

A federal administrator attempting to query raw ballot data will receive a `RawDataAccessAttempt` exception. This is enforced at the Python `__getattr__` level — it is structural, not a policy that can be reconfigured.

---

**Q: Can the government use EIGE to track how individuals voted?**

No. EIGE receives ballots as integer vectors encoding selection choices — it never receives voter identity information. The ballot ingestion pipeline (`CountyNode.ingest_ballot()`) accepts an integer selection vector with no associated voter ID, name, or registration record. EIGE is privacy-blind by design.

---

**Q: What data is retained after the election?**

- **County tier:** hash chain state, shard digests, ballot count — no raw ballot contents
- **State tier:** aggregate hash states, Holon Zero Certificates — no raw ballot data
- **Federal tier:** OSCAL certificates — two boolean fields per election

OSCAL dossiers (override attempt records) are retained per WAC 434 requirements (22 months minimum) because they are the machine-readable equivalent of the paper chain-of-custody audit trail required by Washington State law.

---

**Q: Is EIGE compliant with voter privacy laws?**

EIGE's data architecture is designed for compatibility with:
- **HAVA** — no federally accessible voter-level data
- **State ballot secrecy statutes** — individual ballot content is never transmitted between tiers
- **GDPR and equivalent privacy frameworks** — no personal data is processed by EIGE

Formal legal review for specific jurisdiction deployment is a Phase 2 deliverable.

---

## For Federalism Advocates

**Q: Does EIGE give the federal government more control over elections?**

**No. The opposite.** EIGE's federal tier is deliberately read-only and data-blind.

The federal tier receives only a zero-knowledge certificate: a proof that the state-level audit passed, with no data about which counties, which candidates, or which vote counts produced that result. Federal oversight is mathematically possible; federal access to election data is structurally prevented.

This is a novel property. Existing federal audit frameworks require the federal government to receive raw data. EIGE provides compliance verification without data transfer.

---

**Q: Who has jurisdiction over EIGE once it's deployed in a county?**

The county. EIGE runs on county infrastructure, under county administration, with county-pinned cryptographic keys. The state tier receives only the telemetry that the county chooses to emit. The federal tier receives only what the state chooses to certify.

AxiomZero does not operate any infrastructure in a deployment scenario. We provide software and documentation; jurisdiction, operation, and control remain entirely with the electoral authority.

---

**Q: Could the federal government mandate EIGE to expand their data access?**

No — and this is by design. The federal blind audit gate (`FederalAuditor`) cannot be configured to expose raw ballot data. The restriction is in source code, not in a policy document. A federal mandate to "add ballot data access" would require modifying the open-source code — a modification that would be publicly visible, requiring a new source build, and auditable by any state or county administrator.

---

**Q: What happens if AxiomZero goes away?**

Nothing. EIGE is fully open-source, irrevocably public domain, and dependency-minimal (Python standard library + numpy + mpmath). Any jurisdiction running EIGE can continue running it indefinitely with no relationship with AxiomZero. The source code is immutable once published.

---

*Theory, framework, and scientific direction: ThomasCory Walker-Pearson.*  
*Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).*
