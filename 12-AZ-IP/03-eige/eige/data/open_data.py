# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Ingest public election results from real sources, with provenance.

Supported sources
-----------------
* **OpenElections** — per-state GitHub repositories
  ``openelections/openelections-data-{state}``, CSV files such as
  ``2020/20201103__wa__general__county.csv`` with columns
  ``county, office, district, party, candidate, votes``.
* **MIT Election Data and Science Lab (MEDSL)** — e.g. *County Presidential
  Election Returns 2000–2020* (Harvard Dataverse, doi:10.7910/DVN/VOQCHQ),
  CSV columns ``year, state, state_po, county_name, county_fips, office,
  candidate, party, candidatevotes, totalvotes, ...``.  Dataverse files are
  addressed by numeric file id.

Every fetch returns the raw bytes with a provenance record (URL, retrieval
time, SHA-256, size).  Failures raise :class:`OpenDataError`; there is no
silent fallback to placeholder numbers.  Only HTTPS URLs on an allow-list of
hosts are fetched.
"""

from __future__ import annotations

import csv
import hashlib
import io
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, List, Optional

ALLOWED_HOSTS = frozenset({"raw.githubusercontent.com", "dataverse.harvard.edu"})
MAX_BYTES = 200 * 1024 * 1024
OPENELECTIONS_RAW = "https://raw.githubusercontent.com/openelections/openelections-data-{state}/{ref}/{path}"
DATAVERSE_FILE = "https://dataverse.harvard.edu/api/access/datafile/{file_id}"
_STATE_RE = re.compile(r"^[a-z]{2}$")
_PATH_RE = re.compile(r"^[A-Za-z0-9_./-]+\.csv$")
_REF_RE = re.compile(r"^[A-Za-z0-9_.-]+$")


class OpenDataError(RuntimeError):
    """Raised when data cannot be fetched, verified or parsed."""


@dataclass(frozen=True)
class Provenance:
    source: str
    url: str
    retrieved_at: str
    sha256: str
    size_bytes: int

    def as_dict(self) -> dict:
        return dict(self.__dict__)


@dataclass(frozen=True)
class Fetched:
    data: bytes
    provenance: Provenance


@dataclass(frozen=True)
class ResultRow:
    jurisdiction: str
    office: str
    district: str
    party: str
    candidate: str
    votes: int
    total_votes: Optional[int] = None


def openelections_url(state: str, path: str, ref: str = "master") -> str:
    state = state.strip().lower()
    if not _STATE_RE.match(state):
        raise OpenDataError(f"invalid state code {state!r}")
    if not _PATH_RE.match(path) or ".." in path.split("/"):
        raise OpenDataError(f"invalid OpenElections path {path!r}")
    if not _REF_RE.match(ref):
        raise OpenDataError(f"invalid git ref {ref!r}")
    return OPENELECTIONS_RAW.format(state=state, ref=ref, path=path)


def dataverse_url(file_id: int) -> str:
    if not isinstance(file_id, int) or isinstance(file_id, bool) or file_id <= 0:
        raise OpenDataError("Dataverse file id must be a positive integer")
    return DATAVERSE_FILE.format(file_id=file_id)


def _check_url(url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise OpenDataError(f"refusing to fetch {url!r}: only HTTPS on {sorted(ALLOWED_HOSTS)} is allowed")


def _default_opener(url: str, timeout: float) -> bytes:  # pragma: no cover - network
    req = urllib.request.Request(url, headers={"User-Agent": "EIGE-open-data/22"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - URL allow-listed above
        final = resp.geturl()
        _check_url(final)
        data = resp.read(MAX_BYTES + 1)
    return data


def fetch(
    url: str,
    source: str,
    expected_sha256: Optional[str] = None,
    timeout: float = 30.0,
    opener: Callable[[str, float], bytes] = _default_opener,
) -> Fetched:
    """Fetch ``url`` (allow-listed HTTPS only) and return bytes with provenance."""
    _check_url(url)
    try:
        data = opener(url, timeout)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise OpenDataError(f"could not fetch {url}: {exc}") from exc
    if len(data) > MAX_BYTES:
        raise OpenDataError(f"{url} exceeds {MAX_BYTES} bytes")
    digest = hashlib.sha256(data).hexdigest()
    if expected_sha256 is not None and digest != expected_sha256.lower():
        raise OpenDataError(f"SHA-256 mismatch for {url}: expected {expected_sha256}, got {digest}")
    prov = Provenance(source, url, datetime.now(timezone.utc).isoformat(timespec="seconds"), digest, len(data))
    return Fetched(data, prov)


def load_local(path: str, source: str, original_url: str, expected_sha256: Optional[str] = None) -> Fetched:
    """Load a previously downloaded file, recording where it originally came from."""
    data = Path(path).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if expected_sha256 is not None and digest != expected_sha256.lower():
        raise OpenDataError(f"SHA-256 mismatch for {path}: expected {expected_sha256}, got {digest}")
    mtime = datetime.fromtimestamp(Path(path).stat().st_mtime, timezone.utc).isoformat(timespec="seconds")
    return Fetched(data, Provenance(source, original_url, mtime, digest, len(data)))


def _read_csv(data: bytes, required: List[str]) -> csv.DictReader:
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise OpenDataError(f"CSV is not valid UTF-8: {exc}") from exc
    reader = csv.DictReader(io.StringIO(text))
    header = [h.strip().lower() for h in (reader.fieldnames or [])]
    missing = [c for c in required if c not in header]
    if missing:
        raise OpenDataError(f"CSV missing required column(s): {', '.join(missing)}")
    reader.fieldnames = header
    return reader


def _parse_int(value: Optional[str], row: int, column: str) -> int:
    text = (value or "").strip().replace(",", "")
    if not text.isdigit():
        raise OpenDataError(f"row {row}: column '{column}' is not a non-negative integer ({value!r})")
    return int(text)


def parse_openelections_csv(data: bytes, level: str = "county") -> List[ResultRow]:
    """Parse an OpenElections results CSV (county- or precinct-level)."""
    if level not in ("county", "precinct"):
        raise OpenDataError("level must be 'county' or 'precinct'")
    reader = _read_csv(data, [level, "office", "candidate", "votes"])
    rows = []
    for i, r in enumerate(reader, start=2):
        rows.append(ResultRow(
            jurisdiction=(r.get(level) or "").strip(),
            office=(r.get("office") or "").strip(),
            district=(r.get("district") or "").strip(),
            party=(r.get("party") or "").strip(),
            candidate=(r.get("candidate") or "").strip(),
            votes=_parse_int(r.get("votes"), i, "votes"),
        ))
    return rows


def parse_medsl_county_csv(data: bytes) -> List[ResultRow]:
    """Parse a MEDSL county-returns CSV (e.g. countypres_2000-2020)."""
    reader = _read_csv(data, ["state_po", "county_name", "office", "candidate", "party", "candidatevotes", "totalvotes"])
    rows = []
    for i, r in enumerate(reader, start=2):
        rows.append(ResultRow(
            jurisdiction=f"{(r.get('state_po') or '').strip()}:{(r.get('county_name') or '').strip()}",
            office=(r.get("office") or "").strip(),
            district=(r.get("county_fips") or "").strip(),
            party=(r.get("party") or "").strip(),
            candidate=(r.get("candidate") or "").strip(),
            votes=_parse_int(r.get("candidatevotes"), i, "candidatevotes"),
            total_votes=_parse_int(r.get("totalvotes"), i, "totalvotes"),
        ))
    return rows
