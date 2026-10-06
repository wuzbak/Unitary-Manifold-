# EIGE at County and State Scale

This note records how EIGE behaves on full-population data, how that was measured, and what has not been measured. The numbers are measurements on one machine, not guarantees.

## Design

Nothing in the county or verifier path needs the population in memory.

| Concern | Approach | Cost |
|---|---|---|
| County log | `DurableMerkleLog`: SQLite (WAL, `synchronous=FULL`), leaf bytes plus the stored hash of every complete subtree | Disk ≈ 170 bytes per CVR plus the CVR itself; one transaction per batch of appends |
| Roots and proofs | `LevelledTree` reads stored subtree nodes; `CompactRange` streams a root | Root and proofs: O(log² n) node reads; streaming root: O(log n) memory |
| CVR exports | Incremental NIST SP 1500-103 JSON parser, JSONL, CSV | Constant memory per record (one record ≤ 64 MiB) |
| Ingest validation | Two passes over the export: validate everything, then log the whole file in one transaction, re-checking the file's SHA-256 before COMMIT | Disk-spilling duplicate detection; per-record lookup in the unique-id index. An interrupted ingest logs nothing; the SQLite WAL grows to about the size of the file's records until COMMIT |
| Verification | One streaming pass over `log.jsonl`: canonical check, leaf hashes, head roots, CVR parsing, tallies, precinct tallies, sampled-ballot capture | Memory grows with batches, contests, reporting units and the in-memory part of duplicate detection, not with ballots |
| Duplicate CVR ids | In-memory set up to `dedup_memory_limit` ids (default 2,000,000), then hashed into 256 files on disk | Exact counts either way |
| Parallel verification | The log is split on line boundaries into jobs of at most 16 MiB; at most two jobs per worker are in flight and results are merged in order | Parent memory holds the leaf hashes of the in-flight jobs only (about 32 bytes per entry in them). The report is required (and tested) to be identical to the serial report |
| State | Each county bundle verified in its own process, then the roll-up arithmetic | One county's memory per worker |

## Measurements

Synthetic counties from `eige.synthetic_scale`: five contests (two of them only on half the ballot styles), 200 reporting units, uneven batches of about 500 ballots, rare overvotes, results published by reporting unit, and a comparison audit of all five contests from one sample. Each phase ran in its own process. Peak RSS for parallel verification is the largest single process, so total memory is roughly the worker count times that figure.

Environment: GitHub-hosted Linux runner, 4 vCPUs, Python 3.12. Other test jobs were running on the same machine during the 5,000,000-ballot run, so those times are pessimistic. They are recorded as observed.

| Ballots | `log.jsonl` | Build: generate CSV, ingest, sign, tally, sample, export | Verify, 1 process | Verify, 4 processes |
|---:|---:|---:|---:|---:|
| 100,000 | 16.6 MiB | 7.5 s · 72 MiB | 2.3 s · 41 MiB | 1.6 s · 34 MiB per process |
| 1,000,000 | 166 MiB | 76 s · 181 MiB | 24 s · 126 MiB | 14 s · 47 MiB per process |
| 5,000,000 | 830 MiB | 426 s · 282 MiB | 172 s · 248 MiB | 69 s · 95 MiB per process |

Every bundle verified with no failed checks: 12 verified, 1 warning (development signing key), 3 not checked (no provisional, commitment or witness files in the synthetic bundle).

Peak memory is below the log size at one million ballots and grows far more slowly than the population after that. Most of the serial verifier's memory at these sizes is the in-memory part of duplicate detection. A smaller `dedup_memory_limit` (for example `verify_bundle(dir, dedup_memory_limit=100_000)`) spills sooner and trades memory for disk reads. The slow test `tests/test_eige_scale_verify.py::test_verification_memory_is_bounded_at_scale` verifies 200,000 ballots with a 20,000-id limit and requires traced Python memory to stay under 32 MiB.

## Reproducing

```bash
cd 12-AZ-IP/03-eige
python tools/scale_benchmark.py --ballots 100000 1000000 --contests 5 --workers 4
```

Each line of output is JSON with the time and peak RSS for each phase. CI runs a 250,000-ballot build and verification on every change (`.github/workflows/eige.yml`).

## What has not been measured

- Real vendor exports. The importers follow NIST SP 1500-103 and have been tested on constructed documents, not on exports from certified systems. Vendor-specific layouts need a conversion step outside EIGE.
- Populations above 5,000,000 ballots in one county log. Nothing in the design is expected to change behaviour at larger sizes, but that expectation has not been tested.
- Ingest throughput on a county's actual hardware and storage, including network or encrypted disks.
- A statewide run with dozens of large counties. The statewide verifier has been exercised with small synthetic counties only.
- HSM signing throughput. Heads are signed a handful of times per election, so this is not expected to matter, but it has not been exercised on hardware.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
