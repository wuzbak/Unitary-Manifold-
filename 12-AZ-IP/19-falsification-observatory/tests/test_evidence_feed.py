# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Deterministic tests for the arXiv public evidence feed (no live network)."""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest

from falsification_observatory.app.server import make_server
from falsification_observatory.engine import evidence_feed as ef
from falsification_observatory.engine.evidence_feed import (
    ARXIV_ENDPOINT,
    TRACKED_FEEDS,
    EvidenceFeedTracker,
    FeedInvalid,
    FeedUnavailable,
    FetchResponse,
    build_request_url,
    dispatch_evidence_request,
    parse_arxiv_atom,
)

FIXTURES = Path(__file__).resolve().parent / 'fixtures'
PAGE1 = (FIXTURES / 'arxiv_birefringence_page1.xml').read_bytes()
PAGE2 = (FIXTURES / 'arxiv_birefringence_page2.xml').read_bytes()
API_ERROR = (FIXTURES / 'arxiv_api_error.xml').read_bytes()
ROOT = Path(__file__).resolve().parents[1]
T0 = 1_793_640_000.0  # 2026-11-02T...Z, fixed clock origin


class FakeClock:
    def __init__(self, start: float = T0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class ScriptedFetcher:
    """Return/raise scripted results in order and record every requested URL."""

    def __init__(self, *results) -> None:
        self.results = list(results)
        self.calls: list[tuple[str, float]] = []

    def __call__(self, url: str, timeout: float) -> FetchResponse:
        self.calls.append((url, timeout))
        result = self.results.pop(0)
        if isinstance(result, BaseException):
            raise result
        return result


def ok(body: bytes, **kw) -> FetchResponse:
    kw.setdefault('content_type', 'application/atom+xml; charset=UTF-8')
    kw.setdefault('final_url', 'https://export.arxiv.org/api/query?x=1')
    return FetchResponse(status=200, body=body, **kw)


def make_tracker(*results, clock=None, **kw):
    fetcher = ScriptedFetcher(*results)
    clock = clock or FakeClock()
    kw.setdefault('cooldown_seconds', 0)
    tracker = EvidenceFeedTracker(fetcher=fetcher, clock=clock, **kw)
    return tracker, fetcher, clock


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError('tests must not open network connections')

    monkeypatch.setattr(socket, 'create_connection', refuse)
    monkeypatch.setattr(urllib.request, 'urlopen', refuse)


# ── parsing / validation ────────────────────────────────────────────────────

class TestParse:
    def test_valid_entries_extracted(self):
        parsed = parse_arxiv_atom(PAGE1)
        ids = [e['arxiv_id'] for e in parsed['entries']]
        assert ids == ['2610.01234', '2609.05678']
        assert parsed['total_results'] == 412

    def test_entry_fields(self):
        entry = parse_arxiv_atom(PAGE1)['entries'][0]
        assert entry['version'] == 2
        assert entry['title'] == 'Fixture: Isotropic cosmic birefringence from Planck PR4 polarization'
        assert entry['summary'].startswith('FIXTURE RECORD')
        assert entry['author_count'] == 4
        assert entry['doi'] == '10.1103/FixtureRev.1.000001'
        assert entry['journal_ref'] == 'Fixture Rev. 1, 000001 (2026)'
        assert entry['primary_category'] == 'astro-ph.CO'
        assert entry['abs_url'] == 'https://arxiv.org/abs/2610.01234'
        assert entry['pdf_url'] == 'https://arxiv.org/pdf/2610.01234'

    def test_invalid_entries_rejected_with_reasons(self):
        rejected = parse_arxiv_atom(PAGE1)['rejected']
        assert len(rejected) == 2
        assert any('invalid arXiv id' in r for r in rejected)
        assert any('invalid published timestamp' in r for r in rejected)

    def test_markup_in_title_kept_as_text(self):
        entry = parse_arxiv_atom(PAGE1)['entries'][1]
        assert '<script>' in entry['title']  # escaped in XML, rendered via textContent in the UI

    def test_old_style_id(self):
        body = PAGE2.replace(b'2611.00042v1', b'hep-ph/0101001v3')
        ids = [e['arxiv_id'] for e in parse_arxiv_atom(body)['entries']]
        assert 'hep-ph/0101001' in ids

    def test_duplicates_rejected(self):
        body = PAGE2.replace(b'2611.00042v1', b'2610.01234v1')
        parsed = parse_arxiv_atom(body)
        assert len(parsed['entries']) == 1
        assert any('duplicate' in r for r in parsed['rejected'])

    def test_api_error_feed(self):
        with pytest.raises(FeedInvalid, match='arXiv API error'):
            parse_arxiv_atom(API_ERROR)

    @pytest.mark.parametrize('body,match', [
        (b'', 'empty'),
        (b'<feed', 'malformed'),
        (b'<html><body>maintenance</body></html>', 'unexpected root'),
        (b'<?xml version="1.0"?><!DOCTYPE feed [<!ENTITY a "x">]><feed xmlns="http://www.w3.org/2005/Atom"/>', 'DOCTYPE'),
    ])
    def test_rejects_bad_documents(self, body, match):
        with pytest.raises(FeedInvalid, match=match):
            parse_arxiv_atom(body)

    def test_rejects_oversize(self):
        with pytest.raises(FeedInvalid, match='exceeds'):
            parse_arxiv_atom(b' ' * (ef.MAX_RESPONSE_BYTES + 1))

    def test_all_entries_invalid_is_error(self):
        body = PAGE2.replace(b'http://arxiv.org/abs/', b'http://evil.example/abs/')
        with pytest.raises(FeedInvalid, match='all 2 entries'):
            parse_arxiv_atom(body)

    def test_empty_result_set_is_valid(self):
        body = (b'<feed xmlns="http://www.w3.org/2005/Atom"><opensearch:totalResults '
                b'xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">0</opensearch:totalResults></feed>')
        parsed = parse_arxiv_atom(body)
        assert parsed['entries'] == [] and parsed['total_results'] == 0


# ── request construction ────────────────────────────────────────────────────

class TestRequest:
    def test_all_seven_experiments_tracked(self):
        assert sorted(TRACKED_FEEDS) == [f'EXP-{i}' for i in range(1, 8)]

    def test_request_url_is_fixed_endpoint(self):
        url = build_request_url('EXP-1', 5)
        parts = urlsplit(url)
        assert f'{parts.scheme}://{parts.netloc}{parts.path}' == ARXIV_ENDPOINT
        q = parse_qs(parts.query)
        assert q['search_query'] == ['abs:"cosmic birefringence"']
        assert q['sortBy'] == ['submittedDate'] and q['max_results'] == ['5']

    def test_default_fetcher_refuses_other_hosts(self):
        with pytest.raises(FeedInvalid, match='non-arXiv HTTPS URL'):
            ef.urllib_fetch('https://example.com/feed', 1.0)
        with pytest.raises(FeedInvalid, match='HTTPS'):
            ef.urllib_fetch('http://export.arxiv.org/api/query', 1.0)

    def test_default_fetcher_maps_network_failure(self, monkeypatch):
        def boom(request, timeout):
            assert timeout == 2.5
            raise urllib.error.URLError('dns failure')
        monkeypatch.setattr(urllib.request, 'urlopen', boom)
        with pytest.raises(FeedUnavailable, match='dns failure'):
            ef.urllib_fetch(build_request_url('EXP-2'), 2.5)

    @pytest.mark.parametrize('code,exc', [(503, FeedUnavailable), (429, FeedUnavailable), (400, FeedInvalid)])
    def test_default_fetcher_maps_http_errors(self, monkeypatch, code, exc):
        def boom(request, timeout):
            raise urllib.error.HTTPError(request.full_url, code, 'x', {}, None)
        monkeypatch.setattr(urllib.request, 'urlopen', boom)
        with pytest.raises(exc):
            ef.urllib_fetch(build_request_url('EXP-2'), 1.0)

    def test_default_fetcher_bounds_read_and_sends_user_agent(self, monkeypatch):
        seen = {}

        class Resp:
            status = 200
            headers = {'Content-Type': 'application/atom+xml'}
            def read(self, n):
                seen['n'] = n
                return PAGE2
            def geturl(self):
                return 'https://export.arxiv.org/api/query'
            def __enter__(self):
                return self
            def __exit__(self, *a):
                return False

        def fake(request, timeout):
            seen['ua'] = request.get_header('User-agent')
            seen['timeout'] = timeout
            return Resp()
        monkeypatch.setattr(urllib.request, 'urlopen', fake)
        response = ef.urllib_fetch(build_request_url('EXP-1'), 4.0)
        assert response.body == PAGE2
        assert seen['n'] == ef.MAX_RESPONSE_BYTES + 1
        assert seen['timeout'] == 4.0
        assert 'Falsification-Observatory' in seen['ua']

    @pytest.mark.parametrize('kw', [
        {'timeout_seconds': 0}, {'timeout_seconds': 120}, {'max_results': 0},
        {'max_results': 1.5}, {'max_age_seconds': 0}, {'max_age_seconds': float('nan')},
        {'cooldown_seconds': -1}, {'cooldown_seconds': float('nan')},
    ])
    def test_tracker_rejects_unbounded_config(self, kw):
        with pytest.raises(ValueError):
            EvidenceFeedTracker(fetcher=ScriptedFetcher(), **kw)

    def test_tracker_rejects_redirect_to_insecure_or_untrusted_url(self):
        tracker, _, _ = make_tracker(ok(PAGE1, final_url='http://export.arxiv.org/api/query'))
        result = tracker.refresh('EXP-1')
        assert result['refresh']['outcome'] == 'error'
        assert 'insecure URL' in result['refresh']['error']


# ── tracker states ──────────────────────────────────────────────────────────

class TestTracker:
    def test_never_fetched_initially(self):
        tracker, fetcher, _ = make_tracker()
        snap = tracker.snapshot()
        assert snap['status_counts']['never_fetched'] == 7
        assert all(f['status'] == 'never_fetched' for f in snap['feeds'])
        assert fetcher.calls == []

    def test_successful_refresh_is_fresh_with_provenance(self):
        tracker, fetcher, _ = make_tracker(ok(PAGE1), timeout_seconds=7.5)
        result = tracker.refresh('EXP-1')
        assert result['refresh'] == {'performed': True, 'outcome': 'ok', 'error': None}
        feed = result['feed']
        assert feed['status'] == 'fresh'
        assert feed['entry_count'] == 2
        assert feed['baseline'] is True and feed['new_count'] == 0
        prov = feed['provenance']
        assert prov['endpoint'] == ARXIV_ENDPOINT
        assert prov['request_url'] == fetcher.calls[0][0]
        assert fetcher.calls[0][1] == 7.5
        assert prov['http_status'] == 200
        assert prov['byte_length'] == len(PAGE1)
        assert len(prov['content_sha256']) == 64
        assert prov['total_results'] == 412
        assert prov['rejected_entries'] == 2
        assert prov['fetched_at'].endswith('Z')
        assert prov['parser'] == ef.PARSER_VERSION

    def test_becomes_stale_after_max_age(self):
        tracker, _, clock = make_tracker(ok(PAGE1), max_age_seconds=3600)
        tracker.refresh('EXP-1')
        clock.advance(3601)
        feed = tracker.snapshot('EXP-1')['feeds'][0]
        assert feed['status'] == 'stale'
        assert feed['served_from_cache'] is True
        assert feed['entry_count'] == 2

    def test_unavailable_keeps_last_good_snapshot(self):
        tracker, _, clock = make_tracker(ok(PAGE1), FeedUnavailable('network error: timed out'))
        tracker.refresh('EXP-1')
        clock.advance(10)
        result = tracker.refresh('EXP-1')
        feed = result['feed']
        assert result['refresh']['outcome'] == 'unavailable'
        assert feed['status'] == 'unavailable'
        assert feed['served_from_cache'] is True
        assert feed['entry_count'] == 2
        assert 'timed out' in feed['last_error']
        assert feed['last_success_at'] != feed['last_attempt_at']

    @pytest.mark.parametrize('exc', [TimeoutError('read timed out'), ConnectionResetError('reset'), OSError('down')])
    def test_os_level_failures_are_unavailable(self, exc):
        tracker, _, _ = make_tracker(exc)
        feed = tracker.refresh('EXP-3')['feed']
        assert feed['status'] == 'unavailable'
        assert feed['served_from_cache'] is False and feed['entries'] == []

    @pytest.mark.parametrize('response,match', [
        (FetchResponse(503, b'', 'text/html'), 'HTTP 503'),
    ])
    def test_http_5xx_unavailable(self, response, match):
        tracker, _, _ = make_tracker(response)
        feed = tracker.refresh('EXP-2')['feed']
        assert feed['status'] == 'unavailable' and match in feed['last_error']

    @pytest.mark.parametrize('response,match', [
        (FetchResponse(404, b'', 'text/html'), 'HTTP 404'),
        (FetchResponse(200, PAGE1, 'text/html'), 'content type'),
        (FetchResponse(200, PAGE1, 'application/atom+xml', 'https://evil.example/x'), 'unexpected host'),
        (FetchResponse(200, API_ERROR, 'application/atom+xml'), 'arXiv API error'),
        (FetchResponse(200, b'<not-xml', 'application/atom+xml'), 'malformed'),
    ])
    def test_validation_failures_are_error(self, response, match):
        tracker, _, _ = make_tracker(response)
        feed = tracker.refresh('EXP-2')['feed']
        assert feed['status'] == 'error'
        assert match in feed['last_error']

    def test_unexpected_fetcher_exception_is_error_not_crash(self):
        tracker, _, _ = make_tracker(RuntimeError('bug'))
        assert tracker.refresh('EXP-4')['feed']['status'] == 'error'

    def test_error_then_recovery(self):
        tracker, _, clock = make_tracker(FetchResponse(200, b'<x', 'application/atom+xml'), ok(PAGE1))
        assert tracker.refresh('EXP-1')['feed']['status'] == 'error'
        clock.advance(5)
        feed = tracker.refresh('EXP-1')['feed']
        assert feed['status'] == 'fresh' and feed['last_error'] is None

    def test_tracks_new_entries_between_refreshes(self):
        tracker, _, clock = make_tracker(ok(PAGE1), ok(PAGE2))
        tracker.refresh('EXP-1')
        clock.advance(10)
        feed = tracker.refresh('EXP-1')['feed']
        assert feed['baseline'] is False
        assert feed['new_count'] == 1
        flags = {e['arxiv_id']: e['is_new'] for e in feed['entries']}
        assert flags == {'2611.00042': True, '2610.01234': False}

    def test_cooldown_prevents_hammering(self):
        tracker, fetcher, clock = make_tracker(ok(PAGE1), ok(PAGE2), cooldown_seconds=60)
        tracker.refresh('EXP-1')
        clock.advance(30)
        result = tracker.refresh('EXP-1')
        assert result['refresh']['performed'] is False
        assert result['refresh']['reason'] == 'cooldown'
        assert result['refresh']['retry_after_seconds'] == pytest.approx(30)
        assert len(fetcher.calls) == 1
        clock.advance(31)
        assert tracker.refresh('EXP-1')['refresh']['performed'] is True

    def test_global_outbound_spacing(self):
        tracker, fetcher, clock = make_tracker(ok(PAGE1), ok(PAGE2))
        tracker.refresh('EXP-1')
        result = tracker.refresh('EXP-2')
        assert result['refresh']['reason'] == 'rate_limit'
        clock.advance(ef.MIN_OUTBOUND_SPACING_SECONDS)
        assert tracker.refresh('EXP-2')['refresh']['performed'] is True
        assert len(fetcher.calls) == 2

    def test_concurrent_refresh_reports_in_progress(self):
        gate = threading.Event()
        release = threading.Event()

        def slow(url, timeout):
            gate.set()
            release.wait(5)
            return ok(PAGE1)

        tracker = EvidenceFeedTracker(fetcher=slow, clock=FakeClock(), cooldown_seconds=0)
        worker = threading.Thread(target=tracker.refresh, args=('EXP-1',))
        worker.start()
        assert gate.wait(5)
        assert tracker.refresh('EXP-1')['refresh']['reason'] == 'in_progress'
        release.set()
        worker.join(5)
        assert tracker.snapshot('EXP-1')['feeds'][0]['status'] == 'fresh'

    def test_unknown_experiment(self):
        tracker, _, _ = make_tracker()
        with pytest.raises(KeyError):
            tracker.refresh('EXP-99')

    def test_snapshot_never_fetches(self):
        tracker, fetcher, _ = make_tracker()
        tracker.snapshot()
        tracker.snapshot('EXP-5')
        assert fetcher.calls == []

    def test_persistence_round_trip(self, tmp_path):
        state = tmp_path / 'evidence.json'
        tracker, _, clock = make_tracker(ok(PAGE1), state_path=state)
        tracker.refresh('EXP-1')
        assert json.loads(state.read_text())['parser'] == ef.PARSER_VERSION
        clock.advance(10)
        reloaded = EvidenceFeedTracker(fetcher=ScriptedFetcher(ok(PAGE2)), clock=clock, cooldown_seconds=0,
                                       state_path=state)
        assert reloaded.snapshot('EXP-1')['feeds'][0]['entry_count'] == 2
        feed = reloaded.refresh('EXP-1')['feed']
        assert feed['new_count'] == 1 and feed['baseline'] is False

    def test_corrupt_state_file_is_reported_not_fatal(self, tmp_path):
        state = tmp_path / 'evidence.json'
        state.write_text('{not json')
        tracker = EvidenceFeedTracker(fetcher=ScriptedFetcher(), clock=FakeClock(), state_path=state)
        snap = tracker.snapshot()
        assert 'could not load' in snap['persistence_error']
        assert snap['status_counts']['never_fetched'] == 7

    def test_no_files_written_without_state_path(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        tracker, _, _ = make_tracker(ok(PAGE1))
        tracker.refresh('EXP-1')
        assert list(tmp_path.iterdir()) == []


# ── API dispatch & HTTP integration ─────────────────────────────────────────

class TestApi:
    def test_dispatch_get_all(self):
        tracker, _, _ = make_tracker()
        status, payload = dispatch_evidence_request(tracker, 'GET', '/api/evidence', {})
        assert status == 200 and len(payload['feeds']) == 7
        assert 'never change a verdict' in payload['epistemic_note']

    def test_dispatch_validation(self):
        tracker, fetcher, _ = make_tracker()
        assert dispatch_evidence_request(tracker, 'GET', '/api/evidence', {'exp': ['EXP-42']})[0] == 400
        assert dispatch_evidence_request(tracker, 'POST', '/api/evidence/refresh', {})[0] == 400
        assert dispatch_evidence_request(tracker, 'GET', '/api/evidence/refresh', {'exp': ['EXP-1']})[0] == 405
        assert dispatch_evidence_request(tracker, 'POST', '/api/evidence', {})[0] == 405
        assert dispatch_evidence_request(tracker, 'GET', '/api/evidence/other', {})[0] == 404
        assert fetcher.calls == []

    def test_dispatch_refresh_lowercase_exp(self):
        tracker, _, _ = make_tracker(ok(PAGE1))
        status, payload = dispatch_evidence_request(tracker, 'POST', '/api/evidence/refresh', {'exp': ['exp-1']})
        assert status == 200 and payload['feed']['exp_id'] == 'EXP-1'

    def test_dispatch_refresh_throttled_is_429(self):
        tracker, _, _ = make_tracker(ok(PAGE1), cooldown_seconds=60)
        dispatch_evidence_request(tracker, 'POST', '/api/evidence/refresh', {'exp': ['EXP-1']})
        status, payload = dispatch_evidence_request(tracker, 'POST', '/api/evidence/refresh', {'exp': ['EXP-1']})
        assert status == 429 and payload['refresh']['reason'] == 'cooldown'

    def test_http_server_end_to_end(self, monkeypatch):
        tracker, fetcher, _ = make_tracker(ok(PAGE1))
        monkeypatch.undo()  # allow loopback HTTP for the local test server only
        server = make_server('127.0.0.1', 0, tracker)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f'http://127.0.0.1:{server.server_address[1]}'
        try:
            with urllib.request.urlopen(f'{base}/api/evidence?exp=EXP-1', timeout=5) as r:
                assert r.headers['Cache-Control'] == 'no-store'
                assert json.loads(r.read())['feeds'][0]['status'] == 'never_fetched'
            req = urllib.request.Request(f'{base}/api/evidence/refresh?exp=EXP-1', method='POST')
            with urllib.request.urlopen(req, timeout=5) as r:
                payload = json.loads(r.read())
            assert payload['feed']['status'] == 'fresh'
            assert payload['feed']['entry_count'] == 2
            with pytest.raises(urllib.error.HTTPError) as err:
                urllib.request.urlopen(urllib.request.Request(f'{base}/api/litebird', method='POST'), timeout=5)
            assert err.value.code == 405
            with urllib.request.urlopen(f'{base}/api/litebird', timeout=5) as r:
                assert json.loads(r.read())['endpoint'] == '/api/litebird'
        finally:
            server.shutdown()
            server.server_close()
        assert len(fetcher.calls) == 1


# ── UI contract (static) ────────────────────────────────────────────────────

class TestUiContract:
    html = (ROOT / 'ui' / 'index.html').read_text()
    js = (ROOT / 'ui' / 'falsification-observatory.js').read_text()

    @pytest.mark.parametrize('element_id', ['evidence-panel', 'ev-exp', 'ev-refresh', 'ev-status', 'ev-message',
                                            'ev-provenance', 'ev-list'])
    def test_panel_elements_present(self, element_id):
        assert f'id="{element_id}"' in self.html

    def test_all_experiments_selectable(self):
        for exp_id in TRACKED_FEEDS:
            assert f'value="{exp_id}"' in self.html

    def test_js_uses_api_and_safe_rendering(self):
        assert "/api/evidence?exp=" in self.js
        assert "/api/evidence/refresh?exp=" in self.js
        assert "method: 'POST'" in self.js
        evidence_js = self.js[self.js.index('Public evidence feed'):self.js.index('Test harness')]
        assert 'innerHTML' not in evidence_js
        for status in ('fresh', 'stale', 'unavailable', 'error', 'never_fetched'):
            assert f'{status}:' in evidence_js

    def test_page_loads_evidence_on_start(self):
        assert 'FO.loadEvidence()' in self.html
