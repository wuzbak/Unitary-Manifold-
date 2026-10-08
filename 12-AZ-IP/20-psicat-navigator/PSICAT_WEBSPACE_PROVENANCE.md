# PsiCat Webspace Provenance Audit

**Status:** 🔵 ADJACENT TRACK. Software audit inside Product 20; not a physics claim.
**Module:** `ox_navigator/engine/merlin_webspace_provenance.py` · **Data:** `ox_navigator/engine/data/webspace_provenance_snapshot.json`
**Tests:** `tests/test_merlin_webspace_provenance.py` · **Tool:** `getMerlinWebspaceProvenance` · **Endpoint:** `GET /api/psicat/webspace-provenance`
**Full index:** `ox_navigator/engine/merlin_webspace_index.py` · `data/raw/machine_index_2026-10-07.json.gz` · `tests/test_merlin_webspace_index.py` · tool `getMerlinWebspaceIndex` · `GET /api/psicat/webspace-index`

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
- **Partial transcription (superseded).** The first copy of the machine index was truncated. The complete index has since arrived; see below.

## The complete index

The steward later supplied the whole index as a 2,190-page PDF export. Rebuilding JSON from a PDF invites the obvious question of whether the copy is faithful, and the index answers it for us: it publishes a tree hash with an exact definition. Recomputed from the rebuilt copy over all 1,454 file digests, it matches the published value to the last nibble. Paths, digests, counts and flags are therefore exact; only whitespace inside long prose fields is best-effort. The rebuilt copy and a sidecar describing how it was made are stored under `ox_navigator/engine/data/raw/`.

With the full SBOM in hand, the earlier leads became findings. The 892 entries are 870 distinct packages; the rest are repeated install locations without a recorded path. The `direct` flag follows the package name rather than the install location, so seven nested entries at incompatible versions are counted as direct, along with eight nested in-range copies of `@radix-ui/react-slot`; together they account exactly for 111 against 96. Five declared dev dependencies are flagged as runtime. Both Hippocratic-licensed packages are now named, `@react-leaflet/core` and `react-leaflet`, and the second is a direct dependency, so its terms reach the shipped app. Five declared packages sit at two major versions, TensorFlow.js among them.

The backend sections, which never arrived in the pasted parts, carry the three high-severity findings of this round:
- **Write-capable GitHub scope.** The GitHub connector holds `public_repo`, a scope that can write to public repositories. The webspace's stated policy, enforced in code by two stub refusal functions, is read-only. The policy is right and the credential should match it. A GitHub token secret is configured and used by nothing.
- **Service-role functions without a detected auth check.** Forty-one of 190 functions use the service role, are not admin-only, and show no auth check in the index's static analysis. Static analysis can miss a check, so this is a reading list rather than a verdict.
- **A credential-type file in the stale public bundle.** The source bundle that the webspace's own finding VF-6 calls stale includes `.npmrc`, which the index's exclusion rules withhold because such files can hold registry tokens. Someone should look inside it.

Lower down: two workflows run the same five-minute job twice, and the schedules add up to roughly 2,777 runs a day. On the clock, the index shows a wall-time instrument — a fifteen-minute durable tick cross-checked hourly against external time servers — and mentions 12/37 only as the sound speed in a maintenance replay. Whether the clock's constants use 12/37 is not visible without the clock's source.

Each finding names its fix. The test suite applies these fixes to a copy of the snapshot:
- full per-component digests;
- internal licences changed to AGPL-3.0-or-later;
- versions read from the live registry;
- Tailwind brought in line with `package.json`.

It then confirms that the corresponding findings disappear. The audit is therefore a working checklist for the webspace, not a fixed verdict.

## After the steward's confirmation

The steward confirmed all three high findings on 2026-10-08, reported that PsiCat's GitHub write access has been removed, and announced wider admin, backend and frontend access for PsiCat on the webspace. Two consequences follow, and both are now in code.

A reported fix is recorded, not assumed. The remediation register holds each report with its date, and Merlin checks it against the index. The only index in hand was generated the evening before the report, so it can neither confirm the change nor contradict it; the GitHub entry therefore reads *awaiting a newer index*. When a later index arrives, the entry becomes verified if the connector has lost `public_repo`, and is marked contradicted if it has not. The unused `PSICAT_GITHUB_TOKEN` should go at the same time.

Widening access calls for reading the locks first. Merlin ranks the forty-one functions with no detected login check by what the index says each can reach: a secret it can spend, outside hosts it can call, records it can touch with service privileges, functions it can trigger, and whether a schedule runs it. Six come out on top, including the ElevenLabs proxy (a paid API key behind an open door, if the scan is right), the sanctions watchlist scan (a paid key and four outside hosts) and the steward digest (which can queue email). This is a reading order, not a verdict. The review also lists what an admin grant would reach, the nine entities that declare no row-level rules, and the LinkedIn connector's ability to post as the organisation. It reports expansion as not yet ready until each precondition is settled.

## PsiCat's own exports

The steward added three PDFs that the webspace compiled from PsiCat's own work. Merlin stores their text with each file's hash and audits them.

The inventory is sound. All thirty-six articles match the index's published list by title and category, and the Knowledge Library's tier and domain counts add up exactly. The numbers PsiCat writes about the physics are right as well: n_s, its distance from Planck, k_CS, c_s, the birefringence branches and window, and the DESI and JUNO significances all agree with the repository's live registry.

The statuses are where the articles fall behind. Two articles say the tensor-to-scalar prediction holds, citing BICEP/Keck alone, while the registry has it under high tension from ACT DR6. One repeats a CMB "irreducible mismatch" that the registry has since withdrawn as an invalid inference. The DESI tension carries a label the registry does not use and is described as coming from one experiment. Several pieces describe hardgates as proven and machine-verified, or k_CS as free of any fit to data, where the repository's truth layer treats n_w and k_CS as postulates with n_w selected by Planck data. These are the corrections an author working from an older map would need, and the repository is the newer map.

The PDF compiler has two faults of its own. Every Contents entry in all three files points to the first page of the following work, and the final entry points past the end. And Greek letters and math symbols come out garbled, because the built-in PDF fonts cannot draw them.

## Why this belongs in Merlin

A provenance page makes a promise: every component can be traced from source to deployment. Merlin should be able to check that promise, not repeat it. The same discipline already applies to the physics, where a claim is only as strong as the gate it has passed. That discipline now covers the webspace as well.

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
