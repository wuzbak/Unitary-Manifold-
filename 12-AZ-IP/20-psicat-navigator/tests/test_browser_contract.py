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

from browser_contract_helpers import launch_browser_or_skip, playwright_sync_api, running_server
from ox_navigator.app.server import serve


@pytest.mark.parametrize("browser_name", ["chromium", "firefox", "webkit"])
def test_psicat_browser_contract(browser_name: str) -> None:
    sync_api = playwright_sync_api()
    with running_server(lambda: serve(port=0)) as base_url:
        with sync_api.sync_playwright() as playwright:
            browser = launch_browser_or_skip(playwright, browser_name)
            page = browser.new_page(viewport={"width": 1440, "height": 1100})
            try:
                base_root = base_url.rstrip("/")
                page.route(
                    f"{base_root}/api/merlin/status",
                    lambda route: route.fulfill(
                        status=200,
                        content_type="application/json",
                        body="""{
                          "live_model_available": false,
                          "live_status": {"meta": {"version": "test"}, "tests": {"passed": 64150}, "lean4": {"theorem_count": 3952}}
                        }""",
                    ),
                )
                page.route(
                    f"{base_root}/api/merlin",
                    lambda route: route.fulfill(
                        status=200,
                        content_type="application/json",
                        body="""{
                          "answer": "HARDGATE body\\n---\\nFOLLOWUPS:\\n1. Inspect the observatory lane.\\n2. Review the memory lane.\\nSources:\\n- Pillar 11 | HARDGATE | Canonical route\\n- STATUS.md | REPOSITORY | Regression marker",
                          "body": "HARDGATE body",
                          "followups": ["Inspect the observatory lane.", "Review the memory lane."],
                          "sources": [
                            {"label": "Pillar 11", "type": "HARDGATE", "description": "Canonical route"},
                            {"label": "STATUS.md", "type": "REPOSITORY", "description": "Regression marker"}
                          ],
                          "gate_badges": ["HARDGATE"],
                          "persona_mode": "storyteller",
                          "context_source": "test_harness",
                          "active_kernel": {"kernel_id": "kernel-test", "role": "navigator", "lane": "offline", "provider_variant": "mock"},
                          "accumulated_learnings": {"count": 2, "blocked_count": 0, "target_namespace": "physics"},
                          "observatory_poll": {"executed": false}
                        }""",
                    ),
                )
                page.goto(f"{base_root}/ox-navigator.html", wait_until="domcontentloaded")
                page.wait_for_function("document.getElementById('ox-status-text').textContent.includes('Merlin available')")
                page.locator("#ox-query-input").fill("Explain the birefringence falsifier.")
                page.get_by_role("button", name="Ask Merlin ↗").click()
                page.wait_for_function("document.querySelectorAll('#ox-followups button').length === 2")
                page.wait_for_function("document.querySelectorAll('#ox-sources .ox-source-card').length === 2")
                assert "offline RAG fallback ready" in (page.locator("#ox-status-text").text_content() or "")
                page.reload(wait_until="domcontentloaded")
                page.wait_for_function("document.querySelectorAll('#ox-history-list .ox-history-item').length >= 1")
                assert "Explain the birefringence falsifier." in (page.locator("#ox-history-list").text_content() or "")
            finally:
                browser.close()
