# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PRODUCT_ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.browser_contract_helpers import launch_browser_or_skip, playwright_sync_api, reserve_port, running_server


@pytest.mark.parametrize("browser_name", ["chromium", "firefox", "webkit"])
def test_falsification_observatory_browser_contract(browser_name: str) -> None:
    sync_api = playwright_sync_api()
    port = reserve_port()
    base_url = f"http://127.0.0.1:{port}/"
    with running_server(PRODUCT_ROOT, ["run.py", "--port", str(port), "--no-open"], base_url=base_url):
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
