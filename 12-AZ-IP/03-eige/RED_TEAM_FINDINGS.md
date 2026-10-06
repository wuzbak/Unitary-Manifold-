# EIGE Red-Team Findings (v21 → v22)

**Scope:** an internal adversarial review of EIGE v21 (`src/`, `eige/engine/`, the documentation and the public-site page), carried out in October 2026 before any pilot engagement.
**Status:** all seven findings are fixed or retired in v22. Each one is pinned by a regression test in `tests/test_eige_redteam_findings.py`, and every test in that file fails against the v21 code.

This document records what was wrong, why it mattered and what replaced it. The withdrawn public statements are listed separately in [RETRACTED_CLAIMS.md](RETRACTED_CLAIMS.md).

---

## F1 — The Chern-Simons rolling hash could be forged

**Where:** `src/chern_simon_hash.py` (`ChernSimonChain.update`).

**What was wrong:** each update computes `s' = ((s·74 + b) XOR (s >> 7)) mod (2⁶³−1)`. The function has no key, and for a fixed state `s` the step is affine in the ballot value `b`. That means:

- from any state, an attacker can solve for a ballot value that reaches any chosen next state;
- anyone can recompute a "valid" chain for a fabricated ballot sequence.

During the review a forged two-ballot sequence reached the same final state as an honest three-ballot sequence.

**Why it mattered:** the documentation said the hash made insertion, deletion and reordering "immediately detectable". It did not. Anyone who could recompute the chain could also rewrite it.

**v22 fix:**
- The function is kept only as a *non-security sequence fingerprint*, stated in `SECURITY_ROLE` and in the module docstring. `forge_next_ballot()` stays in the code as a permanent demonstration.
- Tamper evidence now comes from an RFC 6962 / RFC 9162 Merkle log (`eige/crypto/merkle.py`, `eige/ledger/log.py`) built on SHA-256, with domain-separated leaf and node hashes, Ed25519 signed tree heads, and inclusion and consistency proofs.
- The implementation reproduces the Certificate Transparency reference roots.

**Tests:** `TestF1RollingHashForgeable`, `tests/test_eige_v22_merkle.py`.

## F2 — "Metric closure" could never fail

**Where:**
- `src/county_node.py` (`_compute_phi_eff`)
- `src/metric_closure.py`

**What was wrong:**
- φ_eff was computed as π/4 plus a residual of at most about 10⁻¹⁵ divided by the ballot count. That is always inside `PHI_TOLERANCE`, so every county reported `STABLE` regardless of its ballots.
- k_CS was a constant (74), so its check could not fail either.

**Why it mattered:** a green "closure" indicator was presented as an integrity signal and mapped to NIST AC-1. It carried no information.

**v22 fix:**
- Closure is retired as a detection signal (`SECURITY_ROLE = "retired: …"`).
- The constants remain only as named configuration with a stated non-security role.
- The OSCAL mapping for AC-1 is now `not-applicable`.

**Tests:** `TestF2MetricClosureCannotFail`.

## F3 — The "zero-knowledge proof" verified self-asserted flags

**Where:**
- `src/zk_proof.py` (`verify_metric_proof`)
- `src/holon_zero_cert.py`
- `src/federal_auditor.py`

**What was wrong:**
- The "proof" was a Pedersen commitment followed by two flag bytes written by the prover.
- Verification read the flag bytes back and never checked them against the committed value, so `commitment=12345` with flags `01 01` "verified".
- The legacy boolean certificate format was accepted on the flags alone.
- Nothing in the scheme was zero-knowledge.

**v22 fix:**
- `verify_metric_proof` now requires the opening (value and blinding factor). It recomputes the commitment, checks that the proof bytes encode it, and recomputes both flags from the opened value. Without an opening it returns `False`.
- Certificates disclose the opening, because the value is not secret.
- The certificate key is renamed from `zero_knowledge_proof` to `metric_commitment`, and the status from `INVARIANTS_VERIFIED` to `INVARIANTS_CLAIMED`.
- The legacy flag-only format is rejected.
- Tally commitments for auditors live in `eige/crypto/commitments.py`: Pedersen commitments in the RFC 3526 group-14 prime-order subgroup, which are additively homomorphic and can be opened selectively. No zero-knowledge claim is made anywhere.

**Tests:** `TestF3FakeZeroKnowledgeProof`, `tests/test_eige_zk_proof.py`, `tests/test_eige_v22_commitments.py`.

## F4 — Placeholder keys, published seeds and silent mock attestation

**Where:**
- `src/county_node.py` (`_derive_key`)
- `src/hsm_interface.py` (`SoftwareKeyProvider`)
- `src/sentinel_load_balance.py` (`PentadHILS`)
- `src/tee_attestation.py`

**What was wrong:**
- County HMAC keys were `SHA-512("EIGE-v21-{county_id}-hmac-key-placeholder")`. County ids are public, so every key was public.
- Pentad acknowledgement keys were derived from a seed published in the source.
- `get_attestation_report()` silently fell back to a software mock "signed" with a fixed key published in the source.
- The TDX and SEV-SNP paths returned SHA-512 of the quote as the "signature" and never validated a certificate chain.

**v22 fix:**
- **County and Pentad keys:** placeholder derivations are removed. Development keys are random per instance, and every development facility (`DevelopmentSigner`, `SoftwareKeyProvider`, `MockHSMKeyProvider`, the Pentad default keys, the TEE mock) refuses to run when `EIGE_MODE=production`. Any unknown mode value is treated as production.
- **Attestation mock:** the mock is never chosen implicitly. It requires `allow_mock=True` or `EIGE_ALLOW_TEE_MOCK=1`, carries no signature, and is labelled `MOCK_NOT_EVIDENCE`.
- **TDX and SEV-SNP:** reports carry the raw quote with the status `RAW_QUOTE_UNVERIFIED`. `verify_attestation_report` never returns `verified=True`, because quote verification (Intel DCAP for TDX; the VCEK→ASK→ARK chain for SEV-SNP) is not implemented here and must be done with external tooling.

**Tests:** `TestF4PlaceholderKeys`, `tests/test_eige_hsm_interface.py`.

## F5 — Symmetric MACs let every verifier forge

**Where:** telemetry signing in `src/county_node.py` and `src/hsm_interface.py`.

**What was wrong:** HMAC-SHA512 is symmetric. Anyone able to check a county's telemetry could also produce it, so the "signature" could not show which party created a payload.

**v22 fix:**
- Telemetry is signed with Ed25519 (`eige/crypto/signing.py`).
- Each signature uses a domain-separated context, and keys are identified by a key ID.
- A `KeyRegistry` records owner, role, validity window, rotation and revocation (including compromise revocation).
- `verify_telemetry()` checks against the registry, and so do the signed tree heads, custody signoffs and witness cosignatures.
- HMAC is produced only when a legacy key provider is passed explicitly, and it is documented as a non-attributable channel MAC.
- HSM-backed signing is available via PKCS#11 (`PKCS11Ed25519Signer`) but has not been exercised on hardware in this repository.

**Tests:** `TestF5SymmetricSignatures`, `tests/test_eige_v22_signing.py`.

## F6 — The tool did not model how elections are run

**Where:** product-wide; `eige/engine/open_election_data.py`.

**What was wrong:**
- **Missing election records:** there were no cast vote records, ballot manifests, contest or candidate definitions, risk-limiting audits, canvass reconciliation or paper chain-of-custody.
- **Fabricated data sources:** the "open data" fetcher used URLs that do not exist (`openelections.net/results/{year}/{state}/`). On any failure it returned fixed placeholder metrics, which then scored as "Integrity checks nominal".

**v22 fix:**
- **Data model:** a model based on NIST SP 1500-103 (CVR) and SP 1500-100 (ERR) is in `eige/model/election.py`.
- **Audits:** seeded, publicly reproducible sampling is in `eige/audit/sampling.py`. Ballot-polling (BRAVO) and comparison (Kaplan–Markov) risk-limiting audits are in `eige/audit/rla.py`.
- **Canvass:** reconciliation of manifest, cast, counted, reported and provisional ballots, with reasoned discrepancies, is in `eige/audit/reconciliation.py`.
- **Chain of custody:** a two-person-signoff paper custody ledger linked to the Merkle log is in `eige/ledger/custody.py`.
- **Open data:** ingestion from OpenElections GitHub CSVs and MIT Election Data and Science Lab files on Harvard Dataverse uses an HTTPS host allow-list, SHA-256 provenance and loud failure (`eige/data/open_data.py`). The legacy fetcher delegates to it and no longer falls back.
- **Screens:** statistical screens are labelled `investigation_lead_not_evidence`.

**Tests:** `TestF6ElectionWorkflow`, `tests/test_eige_upgrade.py`, `tests/test_eige_v22_model.py`, `tests/test_eige_v22_audit.py`, `tests/test_eige_v22_open_data.py`.

## F7 — Overstated documentation and compliance claims

**Where:**
- `README.md`, `BOOK.md`, `COMPLIANCE.md`, `FAQ.md`
- the public-site page
- `src/oscal_schema.py`, `src/holon_zero_cert.py`

**What was wrong:**
- **Overstated claims:** the documents claimed EIGE "prevents forgery", provides "zero-knowledge" proofs and makes manipulation "mathematically impossible".
- **Stale test counts:** published test counts were out of date.
- **Broken test suite:** Flask was not a declared dependency, so 14 tests errored.
- **Compliance overclaims:** NIST SP 800-53 controls (SI-7, SI-7(6), AC-1, CA-2) were described as satisfied by mechanisms that do not provide them.

**v22 fix:**
- **Documentation:** the documents were rewritten and the withdrawn claims are listed in `RETRACTED_CLAIMS.md`.
- **Dependencies:** they are pinned in `requirements.txt`, including Flask, and the suite reports zero errors.
- **Compliance mapping:** every legacy OSCAL mapping states an honest implementation status (`implemented` / `partial` / `planned` / `not-applicable`). Generated certificates emit the same status as an OSCAL property.
- **v22 control mapping:** the authoritative mapping (`eige/compliance.py`) links each claimed control to the tests that exercise it, and a test fails if a referenced test does not exist.
- **Test counts:** documents no longer state test counts.

**Tests:** `TestF7DocumentationClaims`, `tests/test_eige_compliance.py`.

---

## What remains out of scope

EIGE v22 is an audit-support and transparency tool.
- It does not replace certified tabulators or paper ballots.
- It is not end-to-end voter-verifiable cryptographic voting.
- It cannot detect manipulation that happens before a ballot is scanned (for example, a marked ballot altered before tabulation). Detecting that depends on the paper record, chain of custody and a risk-limiting audit.

See [THREAT_MODEL.md](THREAT_MODEL.md) for the threats considered and the control that answers each one.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
