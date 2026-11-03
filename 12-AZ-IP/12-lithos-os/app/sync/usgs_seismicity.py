# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
LithosOS — USGS measured-seismicity adapter
===========================================
Fetches *measured* earthquake events near a field site from the USGS
Earthquake Hazards Program ComCat FDSN Event Web Service (GeoJSON) and
returns them with source, time, and provenance metadata.

Design guarantees:
  - Bounded network use: per-request socket timeout clamped to
    ``[MIN_TIMEOUT_S, MAX_TIMEOUT_S]`` and response size capped at
    ``MAX_RESPONSE_BYTES``.
  - Schema validation: the FeatureCollection envelope is validated strictly;
    individual malformed features are dropped and counted, never guessed.
  - Explicit data status on every result:
        ``live``         fresh fetch succeeded, data within freshness window
        ``cached``       served from local cache, still within freshness window
        ``stale``        data served but older than the freshness window
                         (e.g. network failed, last good copy returned)
        ``unavailable``  no valid measured data could be obtained
  - Injectable transport (``fetch_fn``) and clock (``now_fn``) so tests are
    deterministic and never touch the network.

This adapter reports catalogued seismic events only. It does not model
geothermal resources, predict earthquakes, or assess hazard.
"""
from __future__ import annotations

import hashlib
import json
import math
import sqlite3
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Optional

ADAPTER_VERSION = "1.0.0"
SOURCE_NAME = "USGS Earthquake Hazards Program — ComCat FDSN Event Web Service"
SOURCE_HOST = "earthquake.usgs.gov"
SOURCE_ENDPOINT = f"https://{SOURCE_HOST}/fdsnws/event/1/query"
SOURCE_LICENSE = "U.S. Government work — public domain (USGS)"

DEFAULT_TIMEOUT_S = 8.0
MIN_TIMEOUT_S = 0.5
MAX_TIMEOUT_S = 15.0
MAX_RESPONSE_BYTES = 5_000_000
DEFAULT_STALE_AFTER_S = 3600          # data older than 1 h is reported stale
DEFAULT_CACHE_TTL_S = 900             # reuse a fetch for 15 min unless refresh

# Query bounds (validated before any network call)
LAT_RANGE = (-90.0, 90.0)
LON_RANGE = (-180.0, 180.0)
RADIUS_KM_RANGE = (1.0, 2000.0)
DAYS_RANGE = (1, 90)
MAG_RANGE = (-1.0, 10.0)
LIMIT_RANGE = (1, 500)

STATUS_LIVE = "live"
STATUS_CACHED = "cached"
STATUS_STALE = "stale"
STATUS_UNAVAILABLE = "unavailable"

FetchFn = Callable[[str, float], bytes]
NowFn = Callable[[], datetime]


class SeismicityQueryError(ValueError):
    """Raised when query parameters are outside validated bounds."""


class SeismicitySchemaError(ValueError):
    """Raised when the upstream payload does not match the expected schema."""


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SeismicityQuery:
    latitude: float
    longitude: float
    radius_km: float = 100.0
    days: int = 30
    min_magnitude: float = 1.0
    limit: int = 100

    def validate(self) -> "SeismicityQuery":
        def _chk(name: str, value: float, bounds: tuple) -> None:
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
                raise SeismicityQueryError(f"{name} must be a finite number")
            if not bounds[0] <= value <= bounds[1]:
                raise SeismicityQueryError(f"{name}={value} outside [{bounds[0]}, {bounds[1]}]")

        _chk("latitude", self.latitude, LAT_RANGE)
        _chk("longitude", self.longitude, LON_RANGE)
        _chk("radius_km", self.radius_km, RADIUS_KM_RANGE)
        _chk("days", self.days, DAYS_RANGE)
        _chk("min_magnitude", self.min_magnitude, MAG_RANGE)
        _chk("limit", self.limit, LIMIT_RANGE)
        if int(self.days) != self.days or int(self.limit) != self.limit:
            raise SeismicityQueryError("days and limit must be integers")
        return self

    def cache_key(self) -> str:
        raw = json.dumps(
            [round(self.latitude, 4), round(self.longitude, 4), self.radius_km,
             int(self.days), self.min_magnitude, int(self.limit)]
        )
        return hashlib.sha256(raw.encode()).hexdigest()[:32]

    def to_url(self, now: datetime) -> str:
        # Start time is truncated to the hour so equivalent queries share a URL.
        start = (now - timedelta(days=int(self.days))).replace(minute=0, second=0, microsecond=0)
        params = {
            "format": "geojson",
            "latitude": f"{self.latitude:.4f}",
            "longitude": f"{self.longitude:.4f}",
            "maxradiuskm": f"{self.radius_km:g}",
            "starttime": start.strftime("%Y-%m-%dT%H:%M:%S"),
            "minmagnitude": f"{self.min_magnitude:g}",
            "limit": str(int(self.limit)),
            "orderby": "time",
        }
        return f"{SOURCE_ENDPOINT}?{urllib.parse.urlencode(params)}"


@dataclass
class SeismicEvent:
    event_id: str
    time_utc: str
    magnitude: Optional[float]
    magnitude_type: str
    place: str
    latitude: float
    longitude: float
    depth_km: float
    distance_km: float
    review_status: str
    event_url: str


@dataclass
class SeismicityResult:
    status: str
    query: dict
    events: list[SeismicEvent] = field(default_factory=list)
    summary: dict = field(default_factory=dict)
    provenance: dict = field(default_factory=dict)
    error: str = ""

    def as_dict(self) -> dict:
        d = asdict(self)
        return d


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(min(1.0, math.sqrt(a)))


def _is_num(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def default_fetch(url: str, timeout_s: float) -> bytes:
    """HTTPS GET restricted to the USGS host, with timeout and size cap."""
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != SOURCE_HOST:
        raise ValueError(f"refusing to fetch non-USGS URL: {url}")
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/geo+json, application/json",
                 "User-Agent": f"LithosOS/{ADAPTER_VERSION} (usgs-seismicity-adapter)"},
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:  # noqa: S310 (host checked)
        body = resp.read(MAX_RESPONSE_BYTES + 1)
    if len(body) > MAX_RESPONSE_BYTES:
        raise ValueError("response exceeds size cap")
    return body


def parse_feature_collection(payload: Any, query: SeismicityQuery) -> tuple[list[SeismicEvent], dict]:
    """Validate a USGS GeoJSON FeatureCollection and extract events.

    Returns ``(events, meta)`` where meta holds ``generated_ms``,
    ``features_received`` and ``features_rejected``. Raises
    :class:`SeismicitySchemaError` if the envelope is invalid.
    """
    if not isinstance(payload, dict):
        raise SeismicitySchemaError("payload is not a JSON object")
    if payload.get("type") != "FeatureCollection":
        raise SeismicitySchemaError("payload.type is not 'FeatureCollection'")
    metadata = payload.get("metadata")
    if not isinstance(metadata, dict) or not _is_num(metadata.get("generated")):
        raise SeismicitySchemaError("metadata.generated (epoch ms) missing or invalid")
    features = payload.get("features")
    if not isinstance(features, list):
        raise SeismicitySchemaError("features is not a list")

    events: list[SeismicEvent] = []
    rejected = 0
    for feat in features:
        try:
            if not isinstance(feat, dict) or feat.get("type") != "Feature":
                raise ValueError
            props = feat["properties"]
            coords = feat["geometry"]["coordinates"]
            if feat["geometry"].get("type") != "Point" or not isinstance(coords, list) or len(coords) < 3:
                raise ValueError
            lon, lat, depth = coords[0], coords[1], coords[2]
            if not (_is_num(lon) and _is_num(lat) and _is_num(depth)):
                raise ValueError
            if not (LAT_RANGE[0] <= lat <= LAT_RANGE[1] and LON_RANGE[0] <= lon <= LON_RANGE[1]):
                raise ValueError
            t_ms = props["time"]
            if not _is_num(t_ms):
                raise ValueError
            mag = props.get("mag")
            if mag is not None and not _is_num(mag):
                raise ValueError
            event_id = feat.get("id")
            if not isinstance(event_id, str) or not event_id:
                raise ValueError
            events.append(SeismicEvent(
                event_id=event_id,
                time_utc=_iso(datetime.fromtimestamp(t_ms / 1000.0, tz=timezone.utc)),
                magnitude=float(mag) if mag is not None else None,
                magnitude_type=str(props.get("magType") or ""),
                place=str(props.get("place") or ""),
                latitude=float(lat),
                longitude=float(lon),
                depth_km=float(depth),
                distance_km=round(_haversine_km(query.latitude, query.longitude, lat, lon), 2),
                review_status=str(props.get("status") or "unknown"),
                event_url=str(props.get("url") or ""),
            ))
        except (KeyError, TypeError, ValueError, OverflowError, OSError):
            rejected += 1

    events.sort(key=lambda e: e.time_utc, reverse=True)
    return events, {
        "generated_ms": float(metadata["generated"]),
        "features_received": len(features),
        "features_rejected": rejected,
    }


def summarize(events: list[SeismicEvent]) -> dict:
    mags = [e.magnitude for e in events if e.magnitude is not None]
    return {
        "event_count": len(events),
        "max_magnitude": max(mags) if mags else None,
        "mean_depth_km": round(sum(e.depth_km for e in events) / len(events), 2) if events else None,
        "nearest_event_km": min(e.distance_km for e in events) if events else None,
        "most_recent_utc": events[0].time_utc if events else None,
        "reviewed_fraction": round(sum(e.review_status == "reviewed" for e in events) / len(events), 3) if events else None,
    }


# ---------------------------------------------------------------------------
# Adapter
# ---------------------------------------------------------------------------

class USGSSeismicityAdapter:
    """Fetch, validate, cache, and status-label measured USGS seismicity."""

    CACHE_SQL = """
    CREATE TABLE IF NOT EXISTS seismicity_cache (
        cache_key     TEXT PRIMARY KEY,
        source_url    TEXT NOT NULL,
        payload_json  TEXT NOT NULL,
        retrieved_at  TEXT NOT NULL
    );
    """

    def __init__(
        self,
        db_path: Optional[Path] = None,
        *,
        fetch_fn: Optional[FetchFn] = None,
        now_fn: Optional[NowFn] = None,
        timeout_s: float = DEFAULT_TIMEOUT_S,
        stale_after_s: float = DEFAULT_STALE_AFTER_S,
        cache_ttl_s: float = DEFAULT_CACHE_TTL_S,
        offline: bool = False,
    ):
        self.db_path = Path(db_path) if db_path else None
        self.fetch_fn = fetch_fn or default_fetch
        self.now_fn = now_fn or _utc_now
        self.timeout_s = min(max(float(timeout_s), MIN_TIMEOUT_S), MAX_TIMEOUT_S)
        self.stale_after_s = float(stale_after_s)
        self.cache_ttl_s = float(cache_ttl_s)
        self.offline = offline

    # ── cache ──────────────────────────────────────────────────────────────

    def _conn(self) -> Optional[sqlite3.Connection]:
        if self.db_path is None:
            return None
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        try:
            conn.executescript(self.CACHE_SQL)
        except sqlite3.Error:
            conn.close()
            raise
        return conn

    def _load_cache(self, key: str) -> Optional[tuple[str, Any, datetime]]:
        conn = self._conn()
        if conn is None:
            return None
        try:
            row = conn.execute(
                "SELECT source_url, payload_json, retrieved_at FROM seismicity_cache WHERE cache_key=?",
                (key,),
            ).fetchone()
            if not row:
                return None
            return row[0], json.loads(row[1]), _parse_iso(row[2])
        finally:
            conn.close()

    def _save_cache(self, key: str, url: str, payload: Any, retrieved_at: datetime) -> None:
        conn = self._conn()
        if conn is None:
            return
        try:
            conn.execute(
                "INSERT INTO seismicity_cache (cache_key, source_url, payload_json, retrieved_at) "
                "VALUES (?, ?, ?, ?) ON CONFLICT(cache_key) DO UPDATE SET "
                "source_url=excluded.source_url, payload_json=excluded.payload_json, "
                "retrieved_at=excluded.retrieved_at",
                (key, url, json.dumps(payload), _iso(retrieved_at)),
            )
            conn.commit()
        finally:
            conn.close()

    # ── public ────────────────────────────────────────────────────────────

    def get_seismicity(self, query: SeismicityQuery, refresh: bool = False) -> SeismicityResult:
        query.validate()
        now = self.now_fn()
        key = query.cache_key()
        cached = self._load_cache(key)
        fetch_error = ""

        use_cache_first = (
            cached is not None and not refresh
            and (now - cached[2]).total_seconds() <= self.cache_ttl_s
        )
        if not use_cache_first and not self.offline:
            url = query.to_url(now)
            try:
                raw = self.fetch_fn(url, self.timeout_s)
                payload = json.loads(raw.decode("utf-8") if isinstance(raw, bytes) else raw)
                events, meta = parse_feature_collection(payload, query)
                self._save_cache(key, url, payload, now)
                return self._build(query, events, meta, url, now, now, from_cache=False)
            except SeismicitySchemaError as exc:
                fetch_error = f"schema validation failed: {exc}"
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                fetch_error = f"invalid JSON from source: {exc.__class__.__name__}"
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                if isinstance(exc, TimeoutError) or isinstance(getattr(exc, "reason", None), TimeoutError):
                    fetch_error = f"source timed out after {self.timeout_s:g}s"
                else:
                    fetch_error = f"source unreachable: {exc.__class__.__name__}: {exc}"[:300]
        elif self.offline and not use_cache_first:
            fetch_error = "offline mode: live fetch disabled"

        if cached is not None:
            url, payload, retrieved_at = cached
            try:
                events, meta = parse_feature_collection(payload, query)
                return self._build(query, events, meta, url, now, retrieved_at,
                                   from_cache=True, error=fetch_error)
            except SeismicitySchemaError as exc:
                fetch_error = (fetch_error + "; " if fetch_error else "") + f"cached payload invalid: {exc}"

        return SeismicityResult(
            status=STATUS_UNAVAILABLE,
            query=asdict(query),
            provenance=self._provenance(None, None, None, None, from_cache=False),
            error=fetch_error or "no data",
        )

    # ── internals ─────────────────────────────────────────────────────────

    def _provenance(self, url, retrieved_at, generated, meta, *, from_cache) -> dict:
        return {
            "source": SOURCE_NAME,
            "source_endpoint": SOURCE_ENDPOINT,
            "source_url": url,
            "license": SOURCE_LICENSE,
            "adapter": "lithos-os.usgs_seismicity",
            "adapter_version": ADAPTER_VERSION,
            "retrieved_at_utc": _iso(retrieved_at) if retrieved_at else None,
            "source_generated_utc": _iso(generated) if generated else None,
            "from_cache": from_cache,
            "features_received": meta["features_received"] if meta else 0,
            "features_rejected": meta["features_rejected"] if meta else 0,
            "data_kind": "measured (catalogued seismic events)",
            "data_age_s": None,
            "stale_after_s": self.stale_after_s,
        }

    def _build(self, query, events, meta, url, now, retrieved_at, *, from_cache, error="") -> SeismicityResult:
        generated = datetime.fromtimestamp(meta["generated_ms"] / 1000.0, tz=timezone.utc)
        age_s = max(0.0, (now - min(generated, retrieved_at)).total_seconds())
        if age_s > self.stale_after_s:
            status = STATUS_STALE
        else:
            status = STATUS_CACHED if from_cache else STATUS_LIVE
        prov = self._provenance(url, retrieved_at, generated, meta, from_cache=from_cache)
        prov["data_age_s"] = round(age_s, 1)
        return SeismicityResult(
            status=status,
            query=asdict(query),
            events=events,
            summary=summarize(events),
            provenance=prov,
            error=error,
        )


def format_report_markdown(result: SeismicityResult | dict) -> str:
    """Render a short human-readable report (used by the Gradio UI)."""
    d = result.as_dict() if isinstance(result, SeismicityResult) else result
    badge = {
        STATUS_LIVE: "🟢 LIVE", STATUS_CACHED: "🟢 CACHED (fresh)",
        STATUS_STALE: "🟠 STALE", STATUS_UNAVAILABLE: "🔴 UNAVAILABLE",
    }.get(d["status"], d["status"])
    prov = d.get("provenance", {})
    lines = [f"**Data status:** {badge}"]
    if d.get("error"):
        lines.append(f"**Note:** {d['error']}")
    if d["status"] != STATUS_UNAVAILABLE:
        s = d.get("summary", {})
        lines.append(
            f"**Events:** {s.get('event_count', 0)} · max M {s.get('max_magnitude')} · "
            f"nearest {s.get('nearest_event_km')} km · mean depth {s.get('mean_depth_km')} km"
        )
        lines.append(
            f"**Source:** {prov.get('source')} — generated {prov.get('source_generated_utc')}, "
            f"retrieved {prov.get('retrieved_at_utc')} (age {prov.get('data_age_s')} s)"
        )
    return "\n\n".join(lines)
