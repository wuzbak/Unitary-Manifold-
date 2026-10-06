# King County Elections — Shadow-Mode Pilot Proposal

**AxiomZero EIGE v22.0**  
**Proposal type:** Observational shadow-mode audit-support trial  
**Jurisdiction:** King County Elections, Washington State  
**Proposing organization:** AxiomZero Technologies & Consulting, SPC  
**Contact:** ThomasCory Walker-Pearson, Scientific Director

---

## Executive summary

AxiomZero proposes a shadow-mode trial of EIGE v22 as an open-source audit-support and public-transparency tool. EIGE would not replace any certified voting system, tabulator, paper ballot, canvass process, risk-limiting audit requirement, or chain-of-custody procedure.

The goal is to evaluate whether EIGE can help publish verifiable records for observers: Merkle logs, signed tree heads, witness cosignatures, reconciliation outputs, RLA support artifacts, custody records, and a public verifier.

## What EIGE would do in a pilot

- Ingest copies of records already produced or exported by existing election systems.
- Build a publication bundle: registry, log, heads, election definition, manifest, results, and optional audit/custody/commitment files.
- Run reconciliation checks for manifest, cast-count, provisional, CVR, and reported-result consistency.
- Support public-seed sampling and RLA calculations for comparison with existing tools.
- Produce observer-facing verification reports.

## What EIGE would not do

- Count votes.
- Change, delay, or control tabulation.
- Replace certified systems or legal procedures.
- Detect manipulation before a ballot is scanned or logged.
- Treat statistical outliers as evidence of fraud.
- Claim physics-based tamper detection or zero-knowledge proofs.

## Proposed evaluation questions

1. Can the publication bundle be produced from existing exports without disrupting operations?
2. Can independent observers run `python -m eige.verify bundle ...` and reproduce the same results?
3. Do reconciliation outputs match existing canvass explanations?
4. Do RLA calculations cross-check with SHANGRLA or Arlo?
5. What CVR redaction rules are needed before public release?
6. What key-management and witness procedures would be acceptable to the jurisdiction?

## Data and privacy

No voter identity data is requested. CVRs can still create ballot-secrecy risks for rare ballot styles or small reporting groups. The pilot should follow King County and Washington State rules for CVR publication, redaction, and aggregation.

## Review request

We invite King County, independent election-security researchers, public observers, and civil-society groups to review the code, documentation, and threat model before any pilot. A useful pilot outcome may be a decision not to deploy; the purpose is sober evaluation, not promotion.
