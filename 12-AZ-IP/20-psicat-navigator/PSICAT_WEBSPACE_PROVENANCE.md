# PsiCat Webspace Provenance Audit

**Status:** 🔵 ADJACENT TRACK. Software audit inside Product 20; not a physics claim.
**Module:** `ox_navigator/engine/merlin_webspace_provenance.py` · **Data:** `ox_navigator/engine/data/webspace_provenance_snapshot.json`
**Tests:** `tests/test_merlin_webspace_provenance.py` · **Tool:** `getMerlinWebspaceProvenance` · **Endpoint:** `GET /api/psicat/webspace-provenance`

The AxiomZero webspace publishes two descriptions of itself. One is a machine index, written for agents and auditors. The other is a Data Provenance page, written for people. The machine index states its own rule of authority: the repository decides questions of science and framework status, and the index decides questions about the webspace's code and configuration. Merlin now holds both descriptions to that rule. It also holds each of them to the evidence the other provides.

The audit does three things. Where the inputs to a hash are published, it recomputes the hash and states the convention it used. It checks the arithmetic in the published counts. And it compares versions and licences against the repository and against the dependency list (SBOM) that the webspace itself publishes. It does not go online, and it does not claim that the live site matches the snapshot.

## What checks out

The machine index is careful work, and most of its counts reconcile:
- Routed, embedded and orphaned page files sum to the stated 119.
- The declared runtime and dev dependency lists contain exactly 79 and 17 entries, as the coverage block says.
- The licence histogram accounts for 886 packages, and the six packages without licence metadata bring the total to 892.
- The per-file mailbox redactions (12, 8 and 3) sum to the stated 23.
- The tree hash is defined precisely enough to recompute, and `tree_hash` implements that definition.

## What does not

**High severity:**
- **The licences contradict each other.** The Data Provenance page labels all five internal components MIT. The page's own licence summary, the machine index and the repository's `LICENSE` and `LICENSE-AGPL` all say DPC v1.0 for theory and AGPL-3.0 for code. MIT would grant rights the project does not grant.
- **The chain hash cannot be checked.** The page publishes the digest but not the per-component digests it is computed from. It also leaves the concatenation order, separator and encoding undefined. `verify_chain_hash` tries the four plausible conventions once full digests are supplied.
- **The per-component timeline hashes look synthetic.** In the five per-component prefixes, 27 of 32 successive nibble steps go down by exactly one. Real SHA-256 output does that about once in sixteen steps. They may be placeholders, and they should either be replaced with real digests or labelled as illustrative.

**Medium severity:**
- **Versions have drifted.** The components show v33.1. The webspace declares v37.7. The repository's live registry reports the current version (v38.2 at the time of writing). The last version bump in the timeline is v24.1.
- **The timeline is stale.** Its latest event is dated 2026-08-20, but the machine index was generated on 2026-10-07.
- **Timeline hashes are truncated.** Each is 8 characters, or 32 bits, which is too short to tie an event to a file.
- **External dependencies are undercounted.** The page lists 3 external packages as "audited and hash-verified". The SBOM lists 892.
- **Two dependencies carry a use-restricted licence.** They are licensed Hippocratic-2.1, which is not an open-source licence and attaches field-of-use terms. Their compatibility with AGPL distribution should be confirmed.

**Low severity:**
- **Tailwind version mismatch.** The page shows Tailwind v3.4.0, but `package.json` declares ^3.4.17.
- **Timeline order.** The events are not in date order.
- **Unexplained direct count.** The SBOM's `direct_count` is 111, but `package.json` declares 79 + 17 = 96 direct dependencies.
- **Orphaned pages.** Nine page files are neither routed nor embedded.
- **Missing licence metadata.** Six packages have none.

**Informational:**
- **dompurify classification.** dompurify is counted as copyleft, but its licence is "MPL-2.0 OR Apache-2.0", so the permissive option can be chosen.
- **Partial transcription.** The machine index arrived truncated, so its agents, workflows and contracts were not audited.

## How a finding clears

Each finding names its fix. The test suite applies these fixes to a copy of the snapshot:
- full per-component digests;
- internal licences changed to AGPL-3.0-or-later;
- versions read from the live registry;
- Tailwind brought in line with `package.json`.

It then confirms that the corresponding findings disappear. The audit is therefore a working checklist for the webspace, not a fixed verdict.

## Why this belongs in Merlin

A provenance page makes a promise: every component can be traced from source to deployment. Merlin should be able to check that promise, not repeat it. The same discipline already applies to the physics, where a claim is only as strong as the gate it has passed. That discipline now covers the webspace as well.

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
