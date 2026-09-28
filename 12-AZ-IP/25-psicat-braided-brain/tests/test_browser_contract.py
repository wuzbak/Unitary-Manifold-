# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import sys
from pathlib import Path

import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PRODUCT_ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from browser_contract_helpers import launch_browser_or_skip, playwright_sync_api, running_server


@pytest.mark.parametrize('browser_name', ['chromium', 'firefox', 'webkit'])
def test_braided_brain_browser_contract(browser_name: str) -> None:
    sync_api = playwright_sync_api()
    with running_server(
        lambda: ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(PRODUCT_ROOT)))
    ) as base_url:
        with sync_api.sync_playwright() as playwright:
            browser = launch_browser_or_skip(playwright, browser_name)
            page = browser.new_page(viewport={'width': 1440, 'height': 1200})
            try:
                page.route('**/api/psicat', lambda route: route.fulfill(status=200, content_type='application/json', body='{"answer":"Wrap once, then deliver the grid phase to the entorhinal torus."}'))
                page.goto(f'{base_url}ui/index.html', wait_until='domcontentloaded')
                page.wait_for_function("document.querySelectorAll('#board .cell').length > 40")
                assert 'PsiCat Braided Brain' in page.title()
                assert 'Science atlas' in (page.locator('body').text_content() or '')
                page.locator('#board .cell[data-x=\"1\"][data-y=\"0\"]').click()
                page.wait_for_function("""
                    () => Array.from(document.querySelectorAll('.metric strong'))
                      .some((node) => node.textContent.trim() === '1')
                """)
                page.get_by_role('button', name='Install app').is_visible()
                page.get_by_role('button', name='Ask PsiCat').click()
                page.wait_for_function("document.getElementById('coach-output').textContent.includes('entorhinal torus')")
                page.get_by_role('button', name='Download save bundle').click()
                assert 'Saved locally' in (page.locator('#save-status').text_content() or '')
                assert len(page.screenshot(full_page=True)) > 10_000
            finally:
                browser.close()
