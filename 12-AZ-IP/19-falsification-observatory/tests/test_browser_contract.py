# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

from functools import partial
from http.server import ThreadingHTTPServer
import sys
from pathlib import Path

import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PRODUCT_ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from browser_contract_helpers import launch_browser_or_skip, playwright_sync_api, running_server
from falsification_observatory.app.server import ObservatoryRequestHandler, UI_DIR


@pytest.mark.parametrize("browser_name", ["chromium", "firefox", "webkit"])
def test_falsification_observatory_browser_contract(browser_name: str) -> None:
    sync_api = playwright_sync_api()
    with running_server(
        lambda: ThreadingHTTPServer(("127.0.0.1", 0), partial(ObservatoryRequestHandler, directory=str(UI_DIR)))
    ) as base_url:
        with sync_api.sync_playwright() as playwright:
            browser = launch_browser_or_skip(playwright, browser_name)
            page = browser.new_page(viewport={"width": 1440, "height": 1200})
            try:
                page.goto(base_url, wait_until="domcontentloaded")
                page.wait_for_function("document.querySelectorAll('#exp-grid .exp-card').length === 7")
                assert "Falsification Observatory" in page.title()
                page.locator("#in-beta").fill("0.30")
                page.locator("#in-beta-sigma").fill("0.001")
                page.get_by_role("button", name="▶ Update Observatory").click()
                page.wait_for_function("document.getElementById('tally-falsified').textContent.trim() === '1'")
                assert "FALSIFIED" in (page.locator("#framework-status-text").text_content() or "")
                assert len(page.screenshot(full_page=True)) > 10_000
            finally:
                browser.close()


@pytest.mark.parametrize("browser_name", ["chromium"])
def test_evidence_feed_panel_browser_contract(browser_name: str) -> None:
    from falsification_observatory.app.server import make_server
    from falsification_observatory.engine.evidence_feed import EvidenceFeedTracker, FetchResponse

    sync_api = playwright_sync_api()
    body = (PRODUCT_ROOT / "tests" / "fixtures" / "arxiv_birefringence_page1.xml").read_bytes()
    tracker = EvidenceFeedTracker(
        fetcher=lambda url, timeout: FetchResponse(200, body, "application/atom+xml", "https://export.arxiv.org/api/query"),
        cooldown_seconds=0,
    )
    with running_server(lambda: make_server("127.0.0.1", 0, tracker)) as base_url:
        with sync_api.sync_playwright() as playwright:
            browser = launch_browser_or_skip(playwright, browser_name)
            page = browser.new_page()
            try:
                page.goto(base_url, wait_until="domcontentloaded")
                page.wait_for_function("document.getElementById('ev-status').dataset.status === 'never_fetched'")
                page.locator("#ev-refresh").click()
                page.wait_for_function("document.getElementById('ev-status').dataset.status === 'fresh'")
                assert page.locator("#ev-list .ev-entry").count() == 2
                assert "<script>" in (page.locator("#ev-list .ev-entry").nth(1).text_content() or "")
                assert "sha256" in (page.locator("#ev-provenance").text_content() or "")
            finally:
                browser.close()
