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

from browser_contract_helpers import launch_browser_or_skip, playwright_sync_api, reserve_port, running_server


@pytest.mark.parametrize("browser_name", ["chromium", "firefox", "webkit"])
def test_um_image_generator_browser_contract(browser_name: str) -> None:
    sync_api = playwright_sync_api()
    port = reserve_port()
    base_url = f"http://127.0.0.1:{port}/"
    with running_server(PRODUCT_ROOT, ["run.py", "--port", str(port), "--no-open"], base_url=base_url):
        with sync_api.sync_playwright() as playwright:
            browser = launch_browser_or_skip(playwright, browser_name)
            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            try:
                page.goto(base_url, wait_until="domcontentloaded")
                page.wait_for_function("document.querySelectorAll('#vizSelector .umig-viz-btn').length >= 8")
                assert "UM Physics Image Generator" in page.title()
                initial_title = page.locator("#vizTitle").text_content() or ""
                assert initial_title != "Loading…"
                page.locator("#vizSelector .umig-viz-btn").nth(1).click()
                page.wait_for_function(
                    """previous => {
                        const current = document.getElementById('vizTitle').textContent;
                        return current && current !== previous;
                    }""",
                    initial_title,
                )
                canvas_size = page.evaluate(
                    """() => {
                        const canvas = document.getElementById('umigCanvas');
                        return { width: canvas.width, height: canvas.height };
                    }"""
                )
                assert canvas_size == {"width": 1400, "height": 900}
                assert len(page.screenshot()) > 5_000
            finally:
                browser.close()
