# Intake: AxiomZero webspace seed

**Status:** pending review; no source integrated or executed.

## Provenance

- Received in commit [`c717d235`](https://github.com/wuzbak/Unitary-Manifold-/commit/c717d23555309c5fca38de926fd63241166d00d5), authored by the repository owner on 2026-10-05 at 23:03:12 UTC.
- Commit message labels the upload “Base44, psicat, webspace”; the archive README identifies it as an AxiomZero Webspace seed and reports generation on 2026-10-04 at 19:20:26 UTC.
- The upload and its contents do not independently authenticate Base44 as the sender or establish that any related pull request originated there.
- Original filename: `ed3726e8f_axiomzero-webspace-seed.zip`.
- Original SHA-256: `d98d3ca2f91be977d945e4173db3ad6850c79259970f6abfbd219080f4de46f5`.

## Inventory and review

The original archive contained 1,171 entries (51,912,090 uncompressed bytes; 8,205,707 compressed bytes). Its README describes 71 entities, 11,835 data records, 1,017 source files, 98 backend functions, 10 workflows, and 15 third-party API integrations; those counts are source-provided and have not been functionally verified. The source/schema snapshot includes `MerlinNote` and `MerlinSession` schemas, PsiCat council/proposal functions, and a webspace seed-export function.

An offline pattern scan found 11 JWT-like strings in `data/entities/SdrStation.json`; ten carried expiration claims dated no later than 2026-09-16, and one had no expiration claim. The scan did not validate tokens with their issuer. No matching GitHub/OpenAI/AWS key or private-key marker was found by the patterns used. The archive also contains a large, unreviewed application data export, so the original dataset was excluded rather than committed here.

The retained `webspace-source-only.zip` is a sanitized derivative: it omits all `data/entities/` records, the root `.env.example`, and `migrate.sh`. It contains 1,099 entries (15,703,697 uncompressed bytes; 4,455,849 compressed bytes), SHA-256 `f4687e022210986b7d584d0ffa320a575d6cc0d2d275638b2eefd63c782ad696`. The same credential-pattern scan found no matches in this derivative. This is a pattern scan, not a full security, privacy, or code review. The source remains untrusted and must not be executed or deployed.

The original archive was committed and stored through Git LFS before this intake review. Removing it from the current tree does not purge the historical commit or LFS object. Treat any credential-like values that might still be accepted by a provider as exposed and revoke or rotate them.

## CI context

- Tests run #4474 on the upload commit failed in repository CI; they are not external-submission test results.
- PR #1005's two Product 20 PR-smoke jobs separately failed during collection because `src.infrastructure` was not importable from the product working directory. The smoke workflows now add the repository root to `PYTHONPATH`; their targeted commands pass locally from that directory.
- Tests run #4476 on main commit `2c96bda` completed successfully. This is CI evidence for that repository revision, not proof of physics claims or of the external source bundle.

## Triage decision

Keep only the code/schema review derivative and this provenance record in the intake area. Do not merge it into Product 20 or treat its proposals, notes, tests, or scientific statements as canonical. Any useful implementation must be independently reviewed, relocated to its proper product or module, and tested through the repository pipeline.
