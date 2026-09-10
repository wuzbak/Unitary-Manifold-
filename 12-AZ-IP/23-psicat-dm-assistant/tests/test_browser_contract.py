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
def test_psicat_dm_assistant_browser_contract(browser_name: str) -> None:
    sync_api = playwright_sync_api()
    port = reserve_port()
    base_url = f"http://127.0.0.1:{port}/"
    with running_server(PRODUCT_ROOT, ["run.py", "serve", "--port", str(port)], base_url=base_url):
        with sync_api.sync_playwright() as playwright:
            browser = launch_browser_or_skip(playwright, browser_name)
            page = browser.new_page(viewport={"width": 1360, "height": 1024})
            try:
                page.goto(base_url, wait_until="domcontentloaded")
                assert "PsiCat DM Guide & Player Assistant" in page.title()
                page.get_by_role("button", name="API Health").click()
                page.wait_for_function("document.getElementById('output').textContent.includes('ok')")
                page.get_by_role("button", name="Create Campaign").click()
                page.wait_for_function("document.getElementById('dm-state').textContent.includes('created')")
                page.get_by_role("button", name="Generate Invite").click()
                page.wait_for_function("document.getElementById('player-invite-code').value.length > 0")
                page.get_by_role("button", name="Player Dashboard").click()
                page.get_by_role("button", name="Join Campaign").click()
                page.wait_for_function("document.getElementById('player-state').textContent.includes('Joined')")
                page.get_by_role("button", name="Load Player Dashboard").click()
                page.wait_for_function("document.getElementById('output').textContent.includes('player')")
                page.get_by_role("button", name="Solo Standalone").click()
                page.get_by_role("button", name="Build Solo Dashboard").click()
                page.wait_for_function("document.getElementById('output').textContent.includes('solo_ready')")
            finally:
                browser.close()
