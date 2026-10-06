# EIGE Retracted Claims

The statements below appeared in EIGE v21 documentation, code docstrings, outreach drafts or the public-site page. They are withdrawn. Each one is tied to a finding in [RED_TEAM_FINDINGS.md](RED_TEAM_FINDINGS.md). Where a v22 mechanism now provides part of what was claimed, the replacement statement says exactly what it does and nothing more.

| # | Finding | Retracted claim (v21 wording, paraphrased where long) | Why it is withdrawn | Accurate v22 statement |
|---|---------|------------------------------------------------------|---------------------|------------------------|
| R1 | F1 | The Chern-Simons rolling hash "prevents ballot forgery" and makes any insertion, deletion or reordering "immediately detectable". | The function is unkeyed and invertible, so a forged sequence can reach any target state. | Ballot records are leaves of a SHA-256 Merkle log (RFC 6962 / RFC 9162) with Ed25519-signed tree heads. Changing a logged record changes the root, and published heads plus consistency proofs show whether history was rewritten. |
| R2 | F1 | Machine-verifiable deviation "from the expected geometric state" proves tampering. | There is no expected geometric state. The constants are configuration. | `K_CS` and `PHI_0` are named configuration constants with no security role. |
| R3 | F2 | 5D metric closure (φ₀ = π/4, k_CS = 74) detects tampering and makes unauthorised administrative changes "mathematically impossible". | The computed value is always within tolerance, so the check cannot fail. | Metric closure is retired. It is not a detection signal. |
| R4 | F3 | EIGE issues "zero-knowledge proofs" of election integrity. | The "proof" was a commitment plus self-asserted flags, and verification trusted the flags. | EIGE publishes Pedersen commitments to per-contest totals. They can be opened selectively for auditors, and county commitments combine into the state total. None of this is zero-knowledge. |
| R5 | F3 | Federal auditors can verify integrity "without seeing any data". | Without the opening, nothing was verified. | Verifying a commitment requires its opening. What an auditor learns is stated in the verification report. |
| R6 | F4 | Telemetry is protected by HSM-backed keys. | The default key was derived from the public county id. | Development keys are random and refused in production mode. Production requires an HSM-backed signer (PKCS#11), which has not been exercised on hardware in this repository. |
| R7 | F4 | Nodes are hardware-attested by Intel TDX or AMD SEV-SNP. | The code fell back silently to a mock with a published key, and never verified a quote. | The mock requires explicit opt-in and is labelled `MOCK_NOT_EVIDENCE`. Hardware quotes are passed through as `RAW_QUOTE_UNVERIFIED` for external verification. |
| R8 | F5 | HMAC-SHA512 signatures prove which county produced a payload. | HMAC is symmetric, so every verifier can forge. | Telemetry, tree heads, custody signoffs and witness cosignatures use Ed25519 public-key signatures checked against a key registry. |
| R9 | F6 | EIGE ingests live results from OpenElections and Harvard Dataverse. | The URLs did not exist, and failures silently returned fixed values scored as "nominal". | EIGE ingests named OpenElections GitHub CSVs and MEDSL Dataverse files, records their provenance (URL, SHA-256, time) and fails loudly on any error. |
| R10 | F6 | Anomaly scores indicate election integrity or fraud. | Statistical outliers are not evidence. | Screens produce investigation leads labelled `investigation_lead_not_evidence`. |
| R11 | F7 | EIGE satisfies NIST SP 800-53 SI-7, SI-7(1), SI-7(6), AC-1, AU-12, AU-12(1), PS-6 and CA-2. | The mappings described mechanisms that do not provide those controls. | Each control is mapped with an honest status (`implemented` / `partial` / `planned` / `not-applicable`) and linked to tests. See `eige/compliance.py` and `COMPLIANCE.md`. |
| R12 | F7 | Published test counts (for example "449 passing tests") and "all tests pass". | The counts were stale, and 14 tests errored because Flask was not a declared dependency. | Dependencies are pinned. Documents do not state test counts; CI runs the EIGE suite on its own. |
| R13 | F7 | EIGE can replace or certify voting systems, or is "federally compliant". | EIGE is not a certified voting system and has not been assessed. | EIGE is an audit-support and transparency tool used alongside certified systems and paper ballots. |

## Out of scope (unchanged by v22)

- EIGE does not replace certified tabulators or paper ballots.
- EIGE is not end-to-end voter-verifiable cryptographic voting.
- EIGE cannot detect manipulation that happens before a ballot is scanned. The paper record, chain of custody and a risk-limiting audit address that.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
