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
