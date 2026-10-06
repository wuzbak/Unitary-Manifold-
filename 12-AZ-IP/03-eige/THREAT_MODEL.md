# EIGE v22 Threat Model

**System:** EIGE v22 is an audit-support and transparency tool that sits alongside certified tabulators and paper ballots. A county publishes the following, which anyone can check with `python -m eige.verify`:
- an append-only Merkle log of cast vote records (CVRs) and chain-of-custody events;
- signed tree heads;
- results;
- tally commitments;
- an audit sample and the audit inputs.

**Method:** STRIDE, extended with insider, supply-chain and election-specific threats. Each threat names the control that answers it and the tests that exercise that control. `tests/test_eige_compliance.py` fails if any test referenced here does not exist.

**Status legend:** **Mitigated** means detected or prevented by tested behaviour. **Partial** means it depends on deployment practice outside EIGE. **Accepted** means it is out of scope and stated as such.

## Assets and trust boundaries

| Asset | Where | Who must not be able to change it undetected |
|---|---|---|
| CVR log entries | county log (`log.jsonl`) | county staff, vendors, network attackers |
| Signed tree heads (STHs) | `heads.json`, bulletin board | the county itself (equivocation), attackers |
| Key registry | `registry.json` | anyone except the registry authority |
| Reported results | `results.json` | county staff, reporting systems |
| Tally commitments / openings | `commitments.json` | aggregators (county → state) |
| Audit seed and sample | `sample.json` | the county (seed grinding) |
| Paper custody record | custody ledger entries | individual officials |

Trust assumptions:
- At least one honest witness or observer compares published heads.
- Signing keys are held in HSMs in production.
- The paper ballots are the record of voter intent.

EIGE does **not** assume the county is honest.

## STRIDE threats

| ID | Threat | Category | Control | Status | Tests |
|---|---|---|---|---|---|
| T1 | Ballot stuffing: adding CVRs after publication | Tampering | RFC 6962 log; root covered by signed head; manifest reconciliation | Mitigated | `tests/test_eige_v22_adversarial.py::test_ballot_stuffing_extra_cvr_in_log_fails` |
| T2 | Deleting CVRs | Tampering | Merkle root mismatch; manifest/cast reconciliation | Mitigated | `tests/test_eige_v22_adversarial.py::test_deletion_of_logged_cvr_fails` |
| T3 | Reordering CVRs, so audit draws point at different ballots | Tampering | Leaf position is bound into the root | Mitigated | `tests/test_eige_v22_adversarial.py::test_reordering_logged_cvrs_fails` |
| T4 | Forged county: heads signed by an unregistered key | Spoofing | Key registry checks owner and role | Mitigated | `tests/test_eige_v22_adversarial.py::test_forged_county_key_head_fails`, `tests/test_eige_redteam_findings.py::TestF5SymmetricSignatures` |
| T5 | Replay: an older head presented as current | Spoofing / Tampering | Verifier requires the latest head to cover the whole log | Mitigated | `tests/test_eige_v22_adversarial.py::test_replayed_stale_head_fails` |
| T6 | Equivocation: different histories shown to different people | Repudiation / Tampering | Consistency proofs, bulletin board gossip, witness cosignatures | Mitigated (needs ≥1 honest witness) | `tests/test_eige_v22_adversarial.py::test_equivocation_same_size_different_root_fails`, `tests/test_eige_v22_ledger.py::test_bulletin_board_consistency_witness_threshold_and_gossip` |
| T7 | Altering reported totals | Tampering | Results recomputed from logged CVRs | Mitigated | `tests/test_eige_v22_adversarial.py::test_altered_results_totals_fail` |
| T8 | Falsifying the aggregated state total | Tampering | Homomorphic Pedersen commitments; opening must match | Mitigated | `tests/test_eige_v22_adversarial.py::test_altered_commitment_opening_fails`, `tests/test_eige_v22_commitments.py::test_county_commitments_aggregate_to_state_total` |
| T9 | Seed grinding: picking the audit seed after seeing the CVRs | Tampering | Seed must post-date a signed head committing to the CVRs; public sampling rule | Mitigated | `tests/test_eige_v22_adversarial.py::test_sample_seed_before_committed_root_timestamp_fails`, `tests/test_eige_v22_audit.py::test_seed_validation_deterministic_draws_and_tamper_detection` |
| T10 | Forging telemetry with a shared or derivable key | Spoofing | Ed25519 telemetry; placeholder derivations removed | Mitigated | `tests/test_eige_redteam_findings.py::TestF4PlaceholderKeys`, `tests/test_eige_redteam_findings.py::TestF5SymmetricSignatures` |
| T11 | Development keys or mock attestation used in production | Elevation of privilege | `EIGE_MODE=production` refuses development facilities; unknown modes count as production | Mitigated | `tests/test_eige_v22_signing.py::test_development_signer_refuses_in_production`, `tests/test_eige_hsm_interface.py::TestAttestationReport` |
| T12 | Compromised signing key | Spoofing | Revocation (including compromise revocation) in the key registry | Partial (detection depends on reporting the compromise) | `tests/test_eige_v22_signing.py::test_registry_register_verify_rotate_revoke_and_round_trip` |
| T13 | Malformed input crashing or confusing the verifier | Denial of service / Tampering | Strict parsers; property-based fuzzing | Mitigated | `tests/test_eige_v22_properties.py::test_parse_cvrs_random_input_only_succeeds_or_raises_model_error`, `tests/test_eige_v22_properties.py::test_bundle_reader_errors_are_documented_for_random_non_directories` |
| T14 | Data exposure: publishing voter-identifying data | Information disclosure | CVRs carry no voter identity; small-batch privacy is a deployment policy | Partial | — |
| T15 | Votes moved between precincts while contest totals are unchanged | Tampering | Precinct (reporting-unit) results recomputed from logged CVRs | Mitigated when results are published by reporting unit; otherwise reported as not checked | `tests/test_eige_scale_verify.py::test_votes_moved_between_precincts_are_detected_even_when_totals_match` |
| T16 | The same CVR export ingested twice (double counting) or a CVR id reused | Tampering | Ingest validates the whole file first and refuses ids already in the log; unique-key index in the log database; verifier reports duplicate ids | Mitigated | `tests/test_eige_scale_ingest.py::test_ingest_is_all_or_nothing_and_never_logs_a_cvr_twice`, `tests/test_eige_scale_storage.py::test_unique_key_violation_rolls_back_the_whole_batch` |
| T17 | Edits to the county log database behind the software's back | Tampering | Integrity check recomputes every leaf and stored head from stored bytes and runs before every head signature and every export, which refuse to proceed on any problem; any published bundle is verified independently | Mitigated (detected, not prevented) | `tests/test_eige_scale_storage.py::test_integrity_check_detects_edited_leaf_bytes`, `tests/test_eige_scale_ingest.py::test_edited_database_blocks_status_signing_and_export` |
| T18 | Exhausting verifier memory with a full-population or hostile bundle | Denial of service | Streaming single-pass verifier; per-entry and per-document size limits; disk-spilling duplicate detection; bounded discrepancy output | Mitigated | `tests/test_eige_scale_verify.py::test_verification_memory_is_bounded_at_scale`, `tests/test_eige_scale_verify.py::test_duplicate_detector_is_exact_in_memory_and_when_spilled` |
| T19 | A parallel verification path that disagrees with the serial one | Tampering (of the verdict) | Reports from serial, parallel and in-memory verification must be identical on clean and tampered bundles | Mitigated | `tests/test_eige_scale_verify.py::test_serial_parallel_and_in_memory_reports_are_identical`, `tests/test_eige_scale_verify.py::test_truncated_log_is_reported_identically_serial_and_parallel` |
| T20 | Lost sampled ballots or missing CVRs used to pass an audit | Tampering | Missing ballot or CVR is scored as the worst case for the reported outcome | Mitigated | `tests/test_eige_scale_verify.py::test_lost_ballots_cannot_confirm_an_outcome`, `tests/test_eige_scale_verify.py::test_missing_ballot_or_cvr_counts_as_worst_case_overstatement` |
| T21 | State roll-up that omits, repeats or alters a county | Tampering | Statewide verifier checks each county bundle, distinct counties, each county figure and each state sum | Mitigated | `tests/test_eige_scale_verify.py::test_statewide_detects_altered_county_figure_and_bad_sum`, `tests/test_eige_scale_verify.py::test_statewide_detects_missing_and_repeated_counties`, `tests/test_eige_scale_verify.py::test_statewide_fails_when_any_county_fails` |
| T22 | A partially logged export (crash, unreadable file, or a file replaced between validation and logging) | Tampering / reliability | Whole file logged in one transaction; the file's SHA-256 is re-checked before COMMIT; any failure rolls back to the previous log size | Mitigated | `tests/test_eige_scale_ingest.py::test_interrupted_ingest_leaves_the_log_unchanged_and_can_be_retried`, `tests/test_eige_scale_ingest.py::test_export_changed_during_ingest_is_not_logged` |

## Insider threats

| ID | Threat | Control | Status | Tests |
|---|---|---|---|---|
| I1 | A single official breaks a seal or transfers a container alone | Custody ledger requires two distinct registered officials per event | Mitigated | `tests/test_eige_v22_ledger.py::test_custody_two_person_rule_and_role_enforcement` |
| I2 | Gaps in a container's custody history | `verify_container` reports broken seals and transfer gaps | Mitigated | `tests/test_eige_v22_ledger.py::test_verify_container_reports_broken_seals_and_transfer_gaps` |
| I3 | Batch counts or provisional ballots quietly mis-accounted | Canvass reconciliation with reasoned discrepancy codes | Mitigated | `tests/test_eige_v22_audit.py::test_reconciliation_discrepancy_codes` |
| I4 | Official records a "clean" audit without inspecting paper | RLA math is checkable; physical inspection is not | Partial | `tests/test_eige_v22_audit.py::test_comparison_audit_confirms_clean_mvrs_and_escalates_with_overstatements` |
| I5 | Colluding officials sign false custody events | Signatures attribute events to keys; collusion is not detectable in software | Accepted | — |

## Supply-chain threats

| ID | Threat | Control | Status | Tests |
|---|---|---|---|---|
| S1 | Dependency substitution or drift | Exact pins; hash-locked `requirements.lock`; CI installs with `--require-hashes` | Mitigated | `tests/test_eige_supply_chain.py::test_requirements_txt_matches_lock` |
| S2 | Unknown component inventory | CycloneDX SBOM generated from the lock and checked in CI | Mitigated | `tests/test_eige_supply_chain.py::test_sbom_is_current` |
| S3 | Verifier behaviour drifting from the published format | Deterministic test vectors (RFC 6962, RFC 8032, sampling, bundle) checked in CI | Mitigated | `tests/test_eige_supply_chain.py::test_test_vectors_are_current`, `tests/test_eige_v22_merkle.py::test_certificate_transparency_reference_roots` |
| S4 | Compromised build host or container base image | Pin `PYTHON_IMAGE` by digest in release pipelines; reproducible-build environment variables | Partial | — |
| S5 | Legacy "security" code mistaken for real controls | Red-team regression tests pin each retracted mechanism | Mitigated | `tests/test_eige_redteam_findings.py::TestF7DocumentationClaims` |

## Election-specific threats outside EIGE's reach

| ID | Threat | Why EIGE cannot address it | What does |
|---|---|---|---|
| X1 | Ballot altered, substituted or misread before scanning | EIGE only sees records after they are logged | Paper ballots, chain of custody, risk-limiting audit |
| X2 | Tabulator software or firmware compromise | EIGE does not certify or attest tabulators | VVSG certification, logic-and-accuracy testing, RLA |
| X3 | Voter coercion or vote buying | Not a voting protocol | Law and polling-place procedures |
| X4 | Statistical anomalies treated as proof of fraud | Screens produce leads only, labelled `investigation_lead_not_evidence` | Human investigation |

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
