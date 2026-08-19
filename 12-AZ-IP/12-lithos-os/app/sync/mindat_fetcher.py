"""
LithosOS — Mindat / USGS Online Fetcher
=========================================
Fetches mineral and gemstone data from publicly available data sources and
caches them in the local SQLite database for offline use.

Supported sources:
  - Mindat Open API (free tier, no key required for basic queries)
    https://api.mindat.org/
  - USGS Mineral Resources Data System (MRDS) — open GeoJSON
    https://mrdata.usgs.gov/services/
  - GIA Gem Encyclopedia (scrape-free: citation-only mode)

Offline-first design:
  - Returns cached (DB) data immediately if no internet
  - Updates cache in background / on explicit refresh call
  - Never blocks the app on network failure

Usage::
    from lithic.app.sync.mindat_fetcher import MindatFetcher
    fetcher = MindatFetcher(db_path=cfg.db_path)
    result = fetcher.fetch_mineral("quartz")
    print(result)          # dict with name, summary, source
    fetcher.refresh_all()  # bulk refresh known minerals
"""
from __future__ import annotations

import json
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional


# ---------------------------------------------------------------------------
# Known Mindat mineral slugs — from the Mindat open mineral list
# These map common names to Mindat API query terms.
# ---------------------------------------------------------------------------

MINDAT_MINERAL_NAMES: dict[str, str] = {
    "quartz": "quartz",
    "pyrite": "pyrite",
    "calcite": "calcite",
    "feldspar": "feldspar",
    "mica": "mica",
    "magnetite": "magnetite",
    "hematite": "hematite",
    "galena": "galena",
    "chalcopyrite": "chalcopyrite",
    "sphalerite": "sphalerite",
    "fluorite": "fluorite",
    "barite": "barite",
    "tourmaline": "tourmaline",
    "garnet": "garnet",
    "olivine": "olivine",
    "apatite": "apatite",
    "malachite": "malachite",
    "azurite": "azurite",
    "turquoise": "turquoise",
    "zircon": "zircon",
    "topaz": "topaz",
    "beryl": "beryl",
    "spinel": "spinel",
    "corundum": "corundum",
    "diamond": "diamond",
    "amber": "amber",
    "opal": "opal",
    "platinum": "platinum",
    "gold": "gold",
    "silver": "silver",
    "copper": "copper",
    "cinnabar": "cinnabar",
    "vanadinite": "vanadinite",
    "wulfenite": "wulfenite",
    "rhodochrosite": "rhodochrosite",
    "smithsonite": "smithsonite",
    "halite": "halite",
    "selenite": "selenite",
    "cassiterite": "cassiterite",
    "kyanite": "kyanite",
}

MINDAT_API_BASE = "https://api.mindat.org"
USGS_MRDS_BASE = "https://mrdata.usgs.gov"


# ---------------------------------------------------------------------------
# Fetch result dataclass
# ---------------------------------------------------------------------------

@dataclass
class MineralFetchResult:
    name: str
    mindat_id: Optional[int] = None
    formula: str = ""
    summary: str = ""
    safety_notes: str = ""
    source: str = ""
    source_url: str = ""
    hardness: str = ""
    crystal_system: str = ""
    fetched_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    from_cache: bool = False
    error: str = ""

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "mindat_id": self.mindat_id,
            "formula": self.formula,
            "summary": self.summary,
            "safety_notes": self.safety_notes,
            "source": self.source,
            "source_url": self.source_url,
            "hardness": self.hardness,
            "crystal_system": self.crystal_system,
            "fetched_at": self.fetched_at,
            "from_cache": self.from_cache,
            "error": self.error,
        }


# ---------------------------------------------------------------------------
# Fetcher
# ---------------------------------------------------------------------------

class MindatFetcher:
    """Fetches and caches Mindat / USGS mineral data in the local DB.

    The fetcher uses a ``mineral_fetch_cache`` table (created lazily) to store
    raw summaries.  All operations degrade gracefully to offline mode when
    the network is unavailable.
    """

    CACHE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS mineral_fetch_cache (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        mineral_key TEXT    NOT NULL UNIQUE,
        data_json   TEXT    NOT NULL DEFAULT '{}',
        source      TEXT    NOT NULL DEFAULT '',
        fetched_at  TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    """

    def __init__(
        self,
        db_path: Path,
        mindat_api_key: str = "",
        timeout_s: int = 8,
        progress_cb: Optional[Callable[[str], None]] = None,
    ):
        self.db_path = db_path
        self.mindat_api_key = mindat_api_key
        self.timeout_s = timeout_s
        self.progress_cb = progress_cb or (lambda msg: None)
        self._ensure_cache_table()

    # ── internal helpers ───────────────────────────────────────────────────

    def _ensure_cache_table(self) -> None:
        if not self.db_path.exists():
            return
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.executescript(self.CACHE_TABLE_SQL)
            conn.commit()
            conn.close()
        except Exception:
            pass

    def _get_cached(self, mineral_key: str) -> Optional[dict]:
        if not self.db_path.exists():
            return None
        try:
            conn = sqlite3.connect(str(self.db_path))
            row = conn.execute(
                "SELECT data_json, source, fetched_at FROM mineral_fetch_cache WHERE mineral_key=?",
                (mineral_key.lower().strip(),)
            ).fetchone()
            conn.close()
            if row:
                data = json.loads(row[0] or "{}")
                data["source"] = row[1]
                data["fetched_at"] = row[2]
                data["from_cache"] = True
                return data
        except Exception:
            pass
        return None

    def _save_cache(self, mineral_key: str, data: dict, source: str) -> None:
        if not self.db_path.exists():
            return
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.execute(
                """
                INSERT INTO mineral_fetch_cache (mineral_key, data_json, source, fetched_at)
                VALUES (?, ?, ?, datetime('now'))
                ON CONFLICT(mineral_key) DO UPDATE SET
                    data_json=excluded.data_json,
                    source=excluded.source,
                    fetched_at=datetime('now')
                """,
                (mineral_key.lower().strip(), json.dumps(data, ensure_ascii=False), source)
            )
            conn.commit()
            conn.close()
        except Exception:
            pass

    # ── Mindat open API ────────────────────────────────────────────────────

    def _fetch_mindat_api(self, mineral_name: str) -> Optional[dict]:
        """Query Mindat open API for mineral data.

        Uses the /minerals endpoint with a name filter (free tier).
        Returns dict with name, formula, description, hardness, crystal_system.
        """
        try:
            params = urllib.parse.urlencode({
                "name": mineral_name,
                "format": "json",
            })
            url = f"{MINDAT_API_BASE}/minerals/?{params}"
            headers = {
                "Accept": "application/json",
                "User-Agent": "LithosOS/1.0 (offline-first mineralogy tool)",
            }
            if self.mindat_api_key:
                headers["Authorization"] = f"Token {self.mindat_api_key}"

            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="replace"))

            results = data.get("results", [])
            if not results:
                return None

            m = results[0]
            summary_parts = []
            if m.get("longid"):
                summary_parts.append(f"Mindat ID: {m['longid']}")
            desc = m.get("description_short") or m.get("description") or ""
            if desc:
                summary_parts.append(desc[:1000])

            return {
                "name": m.get("name", mineral_name),
                "mindat_id": m.get("id"),
                "formula": m.get("formula") or m.get("ima_formula") or "",
                "summary": " ".join(summary_parts)[:2000],
                "hardness": str(m.get("hardness") or m.get("hardness_max") or ""),
                "crystal_system": m.get("crystal_system") or "",
                "source_url": f"https://www.mindat.org/min-{m.get('id', '')}.html",
                "source": "Mindat",
            }

        except (urllib.error.URLError, json.JSONDecodeError, Exception):
            return None

    def _fetch_usgs_mrds(self, mineral_name: str) -> Optional[dict]:
        """Query USGS Mineral Resources Data System for locality data.

        Returns dict with summary and source_url or None on failure.
        """
        try:
            params = urllib.parse.urlencode({
                "commodity": mineral_name,
                "f": "json",
            })
            url = f"{USGS_MRDS_BASE}/services/mrds?{params}"
            req = urllib.request.Request(
                url,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "LithosOS/1.0",
                }
            )
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="replace"))

            features = data.get("features", [])
            if not features:
                return None

            count = len(features)
            countries = set()
            for f in features[:20]:
                props = f.get("properties", {})
                cty = props.get("country") or props.get("cty") or ""
                if cty:
                    countries.add(cty)

            summary = (
                f"USGS MRDS: {count} recorded deposits for '{mineral_name}'. "
                f"Countries: {', '.join(sorted(countries)[:10]) if countries else 'various'}."
            )
            return {
                "summary": summary,
                "source_url": f"{USGS_MRDS_BASE}/mrds/",
                "source": "USGS",
            }

        except (urllib.error.URLError, json.JSONDecodeError, Exception):
            return None

    # ── Public API ────────────────────────────────────────────────────────

    def fetch_mineral(
        self,
        mineral_name: str,
        force_refresh: bool = False,
    ) -> MineralFetchResult:
        """Fetch information for a single mineral.

        Try order:
          1. Return from SQLite cache (unless force_refresh)
          2. Try Mindat open API
          3. Try USGS MRDS
          4. Return empty result (offline mode)

        The result is cached to SQLite for future offline use.
        """
        key = mineral_name.lower().strip()

        if not force_refresh:
            cached = self._get_cached(key)
            if cached:
                return MineralFetchResult(
                    name=mineral_name,
                    mindat_id=cached.get("mindat_id"),
                    formula=cached.get("formula", ""),
                    summary=cached.get("summary", ""),
                    safety_notes=cached.get("safety_notes", ""),
                    source=cached.get("source", "cache"),
                    source_url=cached.get("source_url", ""),
                    hardness=cached.get("hardness", ""),
                    crystal_system=cached.get("crystal_system", ""),
                    fetched_at=cached.get("fetched_at", ""),
                    from_cache=True,
                )

        self.progress_cb(f"[mindat_fetcher] Fetching: {mineral_name}")

        # Try Mindat first
        data = self._fetch_mindat_api(mineral_name)

        # Fallback to USGS
        if not data:
            data = self._fetch_usgs_mrds(mineral_name)

        if data:
            self._save_cache(key, data, data.get("source", ""))
            return MineralFetchResult(
                name=mineral_name,
                mindat_id=data.get("mindat_id"),
                formula=data.get("formula", ""),
                summary=data.get("summary", ""),
                safety_notes=data.get("safety_notes", ""),
                source=data.get("source", ""),
                source_url=data.get("source_url", ""),
                hardness=data.get("hardness", ""),
                crystal_system=data.get("crystal_system", ""),
                from_cache=False,
            )

        # Offline — return empty result
        return MineralFetchResult(
            name=mineral_name,
            from_cache=False,
            error="offline or mineral not found",
        )

    def refresh_all(self, delay_s: float = 0.5) -> dict[str, bool]:
        """Refresh all known minerals.

        Returns a dict mapping mineral_name → success.
        Uses a delay between requests to be a polite client.
        """
        results: dict[str, bool] = {}
        for mineral_name in MINDAT_MINERAL_NAMES:
            result = self.fetch_mineral(mineral_name, force_refresh=True)
            results[mineral_name] = bool(result.summary)
            self.progress_cb(
                f"[mindat_fetcher] {mineral_name}: {'ok' if results[mineral_name] else 'failed'}"
            )
            if delay_s > 0:
                time.sleep(delay_s)
        return results

    def get_all_cached(self) -> list[dict]:
        """Return all cached mineral entries from the local DB."""
        if not self.db_path.exists():
            return []
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT mineral_key, source, fetched_at FROM mineral_fetch_cache ORDER BY mineral_key"
            ).fetchall()
            conn.close()
            return [dict(r) for r in rows]
        except Exception:
            return []

    def cache_stats(self) -> dict:
        """Return statistics about the local mineral cache."""
        cached = self.get_all_cached()
        return {
            "total_cached": len(cached),
            "sources": list({r["source"] for r in cached}),
            "known_minerals": len(MINDAT_MINERAL_NAMES),
            "coverage_pct": round(len(cached) / max(len(MINDAT_MINERAL_NAMES), 1) * 100, 1),
        }
