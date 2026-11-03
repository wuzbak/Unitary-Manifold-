# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Public evidence feed for the Falsification Observatory.

Ingests the public arXiv API (Atom 1.0) for a fixed, pre-registered search query
per experiment front, validates every record, attaches provenance, and tracks
which preprints are new since the previous successful refresh.

Evidence entries are literature pointers only. They are never parsed into
measured values and never change a routing verdict; a human must read the
paper and enter numbers in the observatory explicitly.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import threading
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable
from urllib.parse import urlencode, urlsplit

ARXIV_ENDPOINT = 'https://export.arxiv.org/api/query'
ARXIV_HOST = 'export.arxiv.org'
SOURCE_NAME = 'arXiv API (Atom 1.0)'
SOURCE_ACKNOWLEDGEMENT = 'Thank you to arXiv for use of its open access interoperability.'
PARSER_VERSION = 'fo-arxiv-atom/1'
USER_AGENT = 'AxiomZero-Falsification-Observatory/1.0 (Product 19; local evidence tracker)'

DEFAULT_TIMEOUT_SECONDS = 10.0
DEFAULT_MAX_AGE_SECONDS = 24 * 3600
DEFAULT_COOLDOWN_SECONDS = 60.0
MIN_OUTBOUND_SPACING_SECONDS = 3.0  # arXiv API etiquette: at most one request every 3 s
DEFAULT_MAX_RESULTS = 10
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
MAX_TITLE_CHARS = 400
MAX_SUMMARY_CHARS = 600
MAX_AUTHORS = 8
MAX_REJECTION_REASONS = 10
MAX_SEEN_IDS = 2000

STATUS_NEVER_FETCHED = 'never_fetched'
STATUS_FRESH = 'fresh'
STATUS_STALE = 'stale'
STATUS_UNAVAILABLE = 'unavailable'
STATUS_ERROR = 'error'
STATUSES = (STATUS_NEVER_FETCHED, STATUS_FRESH, STATUS_STALE, STATUS_UNAVAILABLE, STATUS_ERROR)

EPISTEMIC_NOTE = (
    'Evidence entries are recent arXiv preprints matching a fixed query. They are literature '
    'pointers, not extracted measurements, and they never change a verdict automatically.'
)

TRACKED_FEEDS: dict[str, dict[str, str]] = {
    'EXP-1': {'name': 'LiteBIRD Cosmic Birefringence', 'query': 'abs:"cosmic birefringence"'},
    'EXP-2': {'name': 'DESI Dark Energy', 'query': 'abs:DESI AND abs:"dark energy"'},
    'EXP-3': {'name': 'JUNO Neutrino Mass', 'query': 'abs:JUNO AND abs:neutrino'},
    'EXP-4': {'name': 'ACT CMB Spectral Index', 'query': 'abs:"Atacama Cosmology Telescope" AND abs:"spectral index"'},
    'EXP-5': {'name': 'HL-LHC KK Gluon', 'query': 'abs:"Kaluza-Klein gluon"'},
    'EXP-6': {'name': 'nEDM Electric Dipole Moment', 'query': 'abs:"neutron electric dipole moment"'},
    'EXP-7': {'name': 'XENON-nT Dark Matter', 'query': 'abs:XENONnT'},
}

_NS = {
    'atom': 'http://www.w3.org/2005/Atom',
    'opensearch': 'http://a9.com/-/spec/opensearch/1.1/',
    'arxiv': 'http://arxiv.org/schemas/atom',
}
_ARXIV_ID_RE = re.compile(
    r'^https?://arxiv\.org/abs/'
    r'(?P<id>\d{4}\.\d{4,5}|[a-z][a-z.\-]*(?:\.[A-Z]{2})?/\d{7})'
    r'(?:v(?P<version>\d+))?$'
)
_TIMESTAMP_RE = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')
_DOI_RE = re.compile(r'^10\.\d{4,9}/\S+$')
_FORBIDDEN_MARKUP = re.compile(rb'<!\s*(DOCTYPE|ENTITY)', re.IGNORECASE)


class FeedUnavailable(Exception):
    """The upstream source could not be reached or is temporarily refusing service."""


class FeedInvalid(Exception):
    """The upstream response was received but failed validation."""


@dataclass(frozen=True)
class FetchResponse:
    status: int
    body: bytes
    content_type: str = ''
    final_url: str = ''


Fetcher = Callable[[str, float], FetchResponse]
Clock = Callable[[], float]


def build_request_url(exp_id: str, max_results: int = DEFAULT_MAX_RESULTS) -> str:
    """Return the fixed arXiv request URL for a tracked experiment."""
    feed = TRACKED_FEEDS[exp_id]
    params = {
        'search_query': feed['query'],
        'sortBy': 'submittedDate',
        'sortOrder': 'descending',
        'start': 0,
        'max_results': int(max_results),
    }
    return f'{ARXIV_ENDPOINT}?{urlencode(params)}'


def urllib_fetch(url: str, timeout: float) -> FetchResponse:
    """Default network fetcher: bounded timeout, bounded size, fixed host only."""
    parsed_url = urlsplit(url)
    if parsed_url.scheme != 'https' or parsed_url.hostname != ARXIV_HOST:
        raise FeedInvalid(f'refusing to fetch non-arXiv HTTPS URL: {urlsplit(url).hostname}')
    request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT, 'Accept': 'application/atom+xml'})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - fixed https host
            body = response.read(MAX_RESPONSE_BYTES + 1)
            return FetchResponse(
                status=getattr(response, 'status', 200),
                body=body,
                content_type=response.headers.get('Content-Type', ''),
                final_url=response.geturl(),
            )
    except urllib.error.HTTPError as exc:
        if exc.code == 429 or exc.code >= 500:
            raise FeedUnavailable(f'HTTP {exc.code} from arXiv') from exc
        raise FeedInvalid(f'HTTP {exc.code} from arXiv') from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        reason = getattr(exc, 'reason', exc)
        raise FeedUnavailable(f'network error: {reason}') from exc


def _iso(ts: float | None) -> str | None:
    if ts is None:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def _clean(text: str | None, limit: int) -> str:
    collapsed = ' '.join((text or '').split())
    return collapsed if len(collapsed) <= limit else collapsed[: limit - 1].rstrip() + '…'


def _text(element: ET.Element, path: str) -> str | None:
    found = element.find(path, _NS)
    return found.text if found is not None and found.text is not None else None


def _parse_entry(entry: ET.Element) -> dict:
    raw_id = (_text(entry, 'atom:id') or '').strip()
    match = _ARXIV_ID_RE.match(raw_id)
    if not match:
        raise ValueError(f'invalid arXiv id: {raw_id[:80]!r}')
    title = _clean(_text(entry, 'atom:title'), MAX_TITLE_CHARS)
    if not title:
        raise ValueError(f'{match.group("id")}: missing title')
    published = (_text(entry, 'atom:published') or '').strip()
    if not _TIMESTAMP_RE.match(published):
        raise ValueError(f'{match.group("id")}: invalid published timestamp {published[:40]!r}')
    updated = (_text(entry, 'atom:updated') or '').strip()
    if updated and not _TIMESTAMP_RE.match(updated):
        raise ValueError(f'{match.group("id")}: invalid updated timestamp {updated[:40]!r}')
    authors = [_clean(a.text, 120) for a in entry.findall('atom:author/atom:name', _NS) if a.text and a.text.strip()]
    arxiv_id = match.group('id')
    abs_url = f'https://arxiv.org/abs/{arxiv_id}'
    pdf_url = f'https://arxiv.org/pdf/{arxiv_id}'
    doi = (_text(entry, 'arxiv:doi') or '').strip() or None
    if doi and not _DOI_RE.match(doi):
        doi = None
    primary = entry.find('arxiv:primary_category', _NS)
    return {
        'arxiv_id': arxiv_id,
        'version': int(match.group('version')) if match.group('version') else None,
        'title': title,
        'summary': _clean(_text(entry, 'atom:summary'), MAX_SUMMARY_CHARS),
        'authors': authors[:MAX_AUTHORS],
        'author_count': len(authors),
        'published': published,
        'updated': updated or None,
        'primary_category': primary.get('term') if primary is not None else None,
        'doi': doi,
        'journal_ref': _clean(_text(entry, 'arxiv:journal_ref'), 200) or None,
        'abs_url': abs_url,
        'pdf_url': pdf_url,
    }


def parse_arxiv_atom(body: bytes) -> dict:
    """Validate and parse an arXiv Atom response into entries plus rejection reasons."""
    if not body:
        raise FeedInvalid('empty response body')
    if len(body) > MAX_RESPONSE_BYTES:
        raise FeedInvalid(f'response exceeds {MAX_RESPONSE_BYTES} bytes')
    if _FORBIDDEN_MARKUP.search(body):
        raise FeedInvalid('response contains DOCTYPE/ENTITY declarations')
    try:
        root = ET.fromstring(body)
    except ET.ParseError as exc:
        raise FeedInvalid(f'malformed XML: {exc}') from exc
    if root.tag != f'{{{_NS["atom"]}}}feed':
        raise FeedInvalid(f'unexpected root element {root.tag!r}')

    raw_entries = root.findall('atom:entry', _NS)
    for entry in raw_entries:
        entry_id = _text(entry, 'atom:id') or ''
        if 'arxiv.org/api/errors' in entry_id:
            raise FeedInvalid(f'arXiv API error: {_clean(_text(entry, "atom:summary"), 200)}')

    total_text = _text(root, 'opensearch:totalResults')
    try:
        total_results = int(total_text) if total_text is not None else None
    except ValueError as exc:
        raise FeedInvalid(f'invalid totalResults {total_text!r}') from exc

    entries: list[dict] = []
    rejected: list[str] = []
    seen: set[str] = set()
    for entry in raw_entries:
        try:
            parsed = _parse_entry(entry)
        except ValueError as exc:
            rejected.append(str(exc))
            continue
        if parsed['arxiv_id'] in seen:
            rejected.append(f'{parsed["arxiv_id"]}: duplicate entry')
            continue
        seen.add(parsed['arxiv_id'])
        entries.append(parsed)
    if raw_entries and not entries:
        raise FeedInvalid(f'all {len(raw_entries)} entries failed validation: {rejected[:3]}')
    return {
        'feed_updated': _text(root, 'atom:updated'),
        'total_results': total_results,
        'entries': entries,
        'rejected': rejected,
    }


class EvidenceFeedTracker:
    """Thread-safe tracker for the arXiv evidence feed of each experiment front."""

    def __init__(
        self,
        fetcher: Fetcher | None = None,
        clock: Clock | None = None,
        *,
        max_age_seconds: float = DEFAULT_MAX_AGE_SECONDS,
        cooldown_seconds: float = DEFAULT_COOLDOWN_SECONDS,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        max_results: int = DEFAULT_MAX_RESULTS,
        state_path: str | os.PathLike | None = None,
    ) -> None:
        if not math.isfinite(timeout_seconds) or not 0 < timeout_seconds <= 60:
            raise ValueError('timeout_seconds must be in (0, 60]')
        if (
            not math.isfinite(max_age_seconds)
            or not math.isfinite(cooldown_seconds)
            or max_age_seconds <= 0
            or cooldown_seconds < 0
        ):
            raise ValueError('max_age_seconds must be > 0 and cooldown_seconds >= 0')
        if type(max_results) is not int or not 1 <= max_results <= 50:
            raise ValueError('max_results must be in [1, 50]')
        self._fetcher = fetcher or urllib_fetch
        self._clock = clock or time.time
        self.max_age_seconds = float(max_age_seconds)
        self.cooldown_seconds = float(cooldown_seconds)
        self.timeout_seconds = float(timeout_seconds)
        self.max_results = int(max_results)
        self.state_path = Path(state_path) if state_path else None
        self._lock = threading.Lock()
        self._in_flight: set[str] = set()
        self._last_outbound: float | None = None
        self._records: dict[str, dict] = {exp_id: self._empty_record() for exp_id in TRACKED_FEEDS}
        self.persistence_error: str | None = None
        self._load_state()

    @staticmethod
    def _empty_record() -> dict:
        return {
            'last_attempt_at': None,
            'last_success_at': None,
            'last_outcome': None,
            'last_error': None,
            'snapshot': None,
            'seen_ids': [],
            'new_ids': [],
            'baseline': True,
        }

    # ── persistence ──────────────────────────────────────────────────────────
    def _load_state(self) -> None:
        if not self.state_path or not self.state_path.exists():
            return
        try:
            data = json.loads(self.state_path.read_text(encoding='utf-8'))
            if data.get('parser') != PARSER_VERSION or not isinstance(data.get('records'), dict):
                raise ValueError('state file has unexpected format')
            for exp_id, record in data['records'].items():
                if exp_id in self._records and isinstance(record, dict):
                    merged = self._empty_record()
                    merged.update({k: record[k] for k in merged if k in record})
                    self._records[exp_id] = merged
        except (OSError, ValueError, TypeError, AttributeError) as exc:
            self.persistence_error = f'could not load {self.state_path.name}: {exc}'

    def _save_state(self) -> None:
        if not self.state_path:
            return
        payload = {'parser': PARSER_VERSION, 'records': self._records}
        tmp = self.state_path.with_suffix(self.state_path.suffix + '.tmp')
        try:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            tmp.write_text(json.dumps(payload, sort_keys=True), encoding='utf-8')
            os.replace(tmp, self.state_path)
            self.persistence_error = None
        except OSError as exc:
            self.persistence_error = f'could not save {self.state_path.name}: {exc}'

    # ── status ───────────────────────────────────────────────────────────────
    def _status(self, record: dict, now: float) -> str:
        outcome = record['last_outcome']
        if outcome is None:
            return STATUS_NEVER_FETCHED
        if outcome == 'unavailable':
            return STATUS_UNAVAILABLE
        if outcome == 'error':
            return STATUS_ERROR
        age = now - record['last_success_at']
        return STATUS_FRESH if age <= self.max_age_seconds else STATUS_STALE

    def _view(self, exp_id: str, record: dict, now: float, include_entries: bool = True) -> dict:
        status = self._status(record, now)
        snapshot = record['snapshot']
        new_ids = set(record['new_ids'])
        entries = []
        if snapshot and include_entries:
            entries = [dict(entry, is_new=entry['arxiv_id'] in new_ids) for entry in snapshot['entries']]
        data_age = now - record['last_success_at'] if record['last_success_at'] is not None else None
        return {
            'exp_id': exp_id,
            'name': TRACKED_FEEDS[exp_id]['name'],
            'query': TRACKED_FEEDS[exp_id]['query'],
            'status': status,
            'served_from_cache': bool(snapshot) and status in (STATUS_UNAVAILABLE, STATUS_ERROR, STATUS_STALE),
            'last_attempt_at': _iso(record['last_attempt_at']),
            'last_success_at': _iso(record['last_success_at']),
            'data_age_seconds': round(data_age, 3) if data_age is not None else None,
            'max_age_seconds': self.max_age_seconds,
            'last_error': record['last_error'],
            'entry_count': len(snapshot['entries']) if snapshot else 0,
            'new_count': len(new_ids),
            'baseline': record['baseline'],
            'entries': entries,
            'provenance': snapshot['provenance'] if snapshot else None,
        }

    def snapshot(self, exp_id: str | None = None) -> dict:
        """Return tracked state without touching the network."""
        now = self._clock()
        with self._lock:
            if exp_id is not None:
                self._require(exp_id)
                feeds = [self._view(exp_id, self._records[exp_id], now)]
            else:
                feeds = [self._view(e, r, now, include_entries=False) for e, r in self._records.items()]
        counts = {status: 0 for status in STATUSES}
        for feed in feeds:
            counts[feed['status']] += 1
        return {
            'source': SOURCE_NAME,
            'endpoint': ARXIV_ENDPOINT,
            'acknowledgement': SOURCE_ACKNOWLEDGEMENT,
            'epistemic_note': EPISTEMIC_NOTE,
            'generated_at': _iso(now),
            'status_counts': counts,
            'persistence_error': self.persistence_error,
            'feeds': feeds,
        }

    @staticmethod
    def _require(exp_id: str) -> None:
        if exp_id not in TRACKED_FEEDS:
            raise KeyError(exp_id)

    # ── refresh ──────────────────────────────────────────────────────────────
    def refresh(self, exp_id: str) -> dict:
        """Fetch, validate and record the arXiv feed for one experiment.

        Returns ``{'refresh': {...}, 'feed': {...}}``. ``refresh.performed`` is
        False when throttled or already in flight; the cached feed is returned.
        """
        self._require(exp_id)
        now = self._clock()
        with self._lock:
            record = self._records[exp_id]
            if exp_id in self._in_flight:
                return self._refusal(exp_id, now, 'in_progress', 1.0)
            if record['last_attempt_at'] is not None:
                wait = self.cooldown_seconds - (now - record['last_attempt_at'])
                if wait > 0:
                    return self._refusal(exp_id, now, 'cooldown', wait)
            if self._last_outbound is not None:
                wait = MIN_OUTBOUND_SPACING_SECONDS - (now - self._last_outbound)
                if wait > 0:
                    return self._refusal(exp_id, now, 'rate_limit', wait)
            self._in_flight.add(exp_id)
            self._last_outbound = now

        url = build_request_url(exp_id, self.max_results)
        outcome, error, parsed, response = 'ok', None, None, None
        try:
            response = self._fetcher(url, self.timeout_seconds)
            if not isinstance(response, FetchResponse):
                raise FeedInvalid('fetcher returned an unexpected object')
            final_url = urlsplit(response.final_url) if response.final_url else None
            if final_url and (final_url.scheme != 'https' or final_url.hostname != ARXIV_HOST):
                raise FeedInvalid(f'redirected to unexpected host or insecure URL {response.final_url}')
            if response.status == 429 or response.status >= 500:
                raise FeedUnavailable(f'HTTP {response.status} from arXiv')
            if response.status != 200:
                raise FeedInvalid(f'HTTP {response.status} from arXiv')
            if response.content_type and 'xml' not in response.content_type.lower():
                raise FeedInvalid(f'unexpected content type {response.content_type!r}')
            parsed = parse_arxiv_atom(response.body)
        except (FeedUnavailable, OSError) as exc:
            outcome, error = 'unavailable', str(exc) or exc.__class__.__name__
        except FeedInvalid as exc:
            outcome, error = 'error', str(exc)
        except Exception as exc:  # noqa: BLE001 - classify unknown failures as errors, never crash the server
            outcome, error = 'error', f'{exc.__class__.__name__}: {exc}'

        finished = self._clock()
        with self._lock:
            self._in_flight.discard(exp_id)
            record = self._records[exp_id]
            record['last_attempt_at'] = finished
            record['last_outcome'] = outcome
            record['last_error'] = error
            if outcome == 'ok':
                ids = [entry['arxiv_id'] for entry in parsed['entries']]
                previously_seen = set(record['seen_ids'])
                record['baseline'] = record['last_success_at'] is None
                record['new_ids'] = [] if record['baseline'] else [i for i in ids if i not in previously_seen]
                record['seen_ids'] = sorted(previously_seen.union(ids))[-MAX_SEEN_IDS:]
                record['last_success_at'] = finished
                record['snapshot'] = {
                    'entries': parsed['entries'],
                    'provenance': {
                        'source': SOURCE_NAME,
                        'endpoint': ARXIV_ENDPOINT,
                        'request_url': url,
                        'query': TRACKED_FEEDS[exp_id]['query'],
                        'fetched_at': _iso(finished),
                        'http_status': response.status,
                        'content_type': response.content_type or None,
                        'byte_length': len(response.body),
                        'content_sha256': hashlib.sha256(response.body).hexdigest(),
                        'feed_updated': parsed['feed_updated'],
                        'total_results': parsed['total_results'],
                        'returned_entries': len(parsed['entries']),
                        'rejected_entries': len(parsed['rejected']),
                        'rejection_reasons': parsed['rejected'][:MAX_REJECTION_REASONS],
                        'parser': PARSER_VERSION,
                        'acknowledgement': SOURCE_ACKNOWLEDGEMENT,
                    },
                }
            self._save_state()
            view = self._view(exp_id, record, finished)
        return {'refresh': {'performed': True, 'outcome': outcome, 'error': error}, 'feed': view}

    def _refusal(self, exp_id: str, now: float, reason: str, retry_after: float) -> dict:
        return {
            'refresh': {'performed': False, 'reason': reason, 'retry_after_seconds': round(max(retry_after, 0.0), 3)},
            'feed': self._view(exp_id, self._records[exp_id], now),
        }


_default_tracker: EvidenceFeedTracker | None = None
_default_lock = threading.Lock()


def get_default_tracker() -> EvidenceFeedTracker:
    global _default_tracker
    with _default_lock:
        if _default_tracker is None:
            _default_tracker = EvidenceFeedTracker()
        return _default_tracker


def _exp_param(query: dict[str, list[str]]) -> str | None:
    values = query.get('exp') or []
    return values[0].strip().upper() if values and values[0].strip() else None


def dispatch_evidence_request(
    tracker: EvidenceFeedTracker, method: str, path: str, query: dict[str, list[str]] | None = None
) -> tuple[int, dict]:
    """Route ``/api/evidence`` (GET) and ``/api/evidence/refresh`` (POST) to the tracker."""
    query = query or {}
    exp_id = _exp_param(query)
    if exp_id is not None and exp_id not in TRACKED_FEEDS:
        return 400, {'error': f'unknown experiment {exp_id!r}', 'tracked': sorted(TRACKED_FEEDS)}
    if path == '/api/evidence':
        if method != 'GET':
            return 405, {'error': 'use GET for /api/evidence'}
        return 200, dict(tracker.snapshot(exp_id), endpoint_path='/api/evidence')
    if path == '/api/evidence/refresh':
        if method != 'POST':
            return 405, {'error': 'use POST for /api/evidence/refresh'}
        if exp_id is None:
            return 400, {'error': 'exp query parameter is required', 'tracked': sorted(TRACKED_FEEDS)}
        result = tracker.refresh(exp_id)
        payload = dict(result, endpoint_path='/api/evidence/refresh', source=SOURCE_NAME,
                       epistemic_note=EPISTEMIC_NOTE)
        status = 200 if result['refresh']['performed'] else 429
        return status, payload
    return 404, {'error': f'unknown evidence endpoint {path!r}'}
