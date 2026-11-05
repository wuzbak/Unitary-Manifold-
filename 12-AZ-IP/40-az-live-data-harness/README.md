# AZ Live-Data Harness — Product 40

**Folder:** `12-AZ-IP/40-az-live-data-harness/`
**Version:** 1.2.0
**Status:** Active — read-only integration with a public USGS live feed

## Live integration

The product fetches and validates the USGS GeoJSON feed for earthquakes
reported in the past day:

`https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson`

The normalized result includes the source URL and title, the timestamp
published by USGS, the local fetch timestamp, calculated feed age, event
count, and most recent event. The feed is marked `stale` when its published
timestamp is more than two hours old. A future publication timestamp,
malformed payload, or fetch failure is reported as an error. This integration
does **not** substitute a cached, fixture, Planck, or hard-coded value when
the live source is unavailable. Generic fallback/verdict helpers remain
available to Python callers but are not used by this adapter.

The adapter uses the Python standard library and makes an HTTPS GET with a
10-second timeout. Tests inject a fake response; they do not depend on network
access. No claim is made here about the feed being reachable in every
deployment environment.

## CLI

Fetch and print one normalized live result:

```bash
python 12-AZ-IP/40-az-live-data-harness/run.py
```

Exit status is `0` for a fresh result, `2` for a valid but stale result, and
`1` when the request or payload validation fails. Start the dashboard and API:

```bash
python 12-AZ-IP/40-az-live-data-harness/run.py --serve --port 8140
```

## HTTP API and UI

The server binds to `127.0.0.1` by default. It serves the static dashboard at
`/` and these read-only JSON endpoints:

- `GET /api/status` — adapter, source URL, endpoints, and explicit
  `fallback: false`.
- `GET /api/fetch-result` — fetches the feed and returns normalized data,
  including provenance and freshness fields. Fetch/validation failures return
  HTTP `502` with an error and source URL; stale valid data remains HTTP `200`
  with `"stale": true`.

The UI shows the live/stale/error state and displays the full JSON response.
Fetching is on demand; opening the dashboard alone does not assert that a
successful request occurred.

## Temporal capture and historical replay

The existing USGS transport now also supports availability-aware magnitude
snapshots through the shared AZ ML temporal foundation:

```bash
python 12-AZ-IP/40-az-live-data-harness/run.py --temporal --owner-scope my-project
```

`GET /api/temporal-result?owner_scope=my-project` exposes the same read-only
capture. Missing or repeated scope parameters return HTTP 400; feed failures
remain HTTP 502. A caller-supplied scope is not authenticated multi-user access
control. The existing summary endpoint and default CLI remain compatible.

The capture carries the exact response SHA-256, feed publication and observation
times, snapshot identity, explicit missing-magnitude IDs, origin and a
promotion-ineligible execution-spine receipt. Magnitudes are USGS-reported
values; magnitude types may differ, so this is not a homogeneous calibrated
prediction dataset. Duplicate event IDs, future events, non-finite numbers and
malformed records fail explicitly. Unknown magnitudes are reported, not filled
with zero.
Missing-value corrections are retained as null records, not dropped. New
snapshots use schema v2 with local revision times; earlier v1 snapshots remain
readable. Later source revisions supersede earlier values only once observed,
even when a corrected event timestamp moves backward.

Availability is **local observation time**, never the earthquake's historical
event time. A later observed correction cannot leak into an earlier replay.
The API always fetches; it does not silently substitute cached or generated
data. Python callers injecting constructed responses must pass
`origin="synthetic"`; such records are excluded by default temporal queries.

Optionally add `--snapshot-dir /existing/durable/directory` to persist both the
content-addressed temporal snapshot and its parent-linked lineage manifest.
The source-payload node links to the temporal transform node with explicit
origin, observation time, code/config identities and caller-asserted use policy.
Deletion impact is an advisory descendant plan, not automatic deletion or model
unlearning. The directory must already exist and have
durably established ancestors. File/directory fsync and hard links require a
supporting POSIX filesystem. Preserve the printed receipt alongside it to retain
source provenance; the snapshot hash alone does not preserve the raw response
or prove source authenticity. No raw feed archive is written without an explicit
archive option.
Each file is published atomically, but the pair is not one transaction. If the
second publication fails, the CLI reports failure and a verified snapshot may
remain; retrying identical artifacts is safe.

### Exact raw-response archives

Use `--archive-dir /existing/durable/directory` alongside `--temporal` and
`--owner-scope` to preserve the exact response bytes in a single immutable,
content-addressed archive. The archive includes scope, origin, original
observation time, raw-response and snapshot hashes, and transform-source hashes.
Transport reads are bounded to 8 MiB; oversized feeds fail rather than truncate.
The base64-framed JSON archive has a separate bounded read limit.

Replay is an explicit, network-free operation, never a fallback for a failed
live request:

```bash
python 12-AZ-IP/40-az-live-data-harness/run.py --temporal \
  --owner-scope my-project --archive-dir /existing/durable/directory \
  --replay-archive ARCHIVE_SHA256
```

Replace `ARCHIVE_SHA256` with the printed archive filename's SHA-256 stem.
The result reports `mode="archive_replay"`. Replay verifies the archive, exact
raw bytes, snapshot and current transform-source bindings. It preserves the
original observation time, origin, missingness and historical stale flag; it
does not attest present-day freshness or fetch today's feed. A changed transform
requires the archived source version, not a silently substituted implementation.
Synthetic archives remain synthetic. Wrong scope, missing/corrupt archives,
unsupported schemas and unsafe files fail explicitly. Archive publication is
atomic; an optional snapshot/lineage export is still a separate operation.
An archive hash proves local byte identity, not upstream authenticity, training
rights, authenticated ownership, power-loss recovery or live-feed qualification.

This completes a scoped transport-to-temporal adapter, **not** a serverless
feature store, statistical prediction-drift detector or deployment qualification.
The broader program and remaining gates are tracked in
[`../../9-INFRASTRUCTURE/az-ml-program/README.md`](../../9-INFRASTRUCTURE/az-ml-program/README.md).

## Tests

```bash
python -m pytest 12-AZ-IP/40-az-live-data-harness/tests -q
```

Tests use injected responses and a fixed clock; running them does not require
the public service or other network access.

## Source

- USGS Earthquake Hazards Program, GeoJSON Summary Feed:
  <https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/>

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
