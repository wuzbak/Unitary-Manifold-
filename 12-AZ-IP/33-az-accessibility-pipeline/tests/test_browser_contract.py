# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
from __future__ import annotations

import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PRODUCT_ROOT.parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pytest

from browser_contract_helpers import launch_browser_or_skip, playwright_sync_api, running_server
from az_accessibility_pipeline.app.server import build_server


def test_report_browser_contract_supports_continuous_speech_playback() -> None:
    sync_api = playwright_sync_api()
    with running_server(lambda: build_server("127.0.0.1", 0)) as base_url:
        with sync_api.sync_playwright() as playwright:
            browser = launch_browser_or_skip(playwright, "chromium")
            page = browser.new_page()
            page.add_init_script(
                """
                window.__spoken = [];
                window.SpeechSynthesisUtterance = class {
                  constructor(text) { this.text = text; }
                };
                const mockSpeech = {
                  getVoices: () => [],
                  speak(utterance) {
                    window.__spoken.push(utterance.text);
                    setTimeout(() => utterance.onend && utterance.onend(), 0);
                  },
                  cancel() {},
                  addEventListener() {}
                };
                Object.defineProperty(window, "speechSynthesis", { value: mockSpeech });
                """
            )
            try:
                page.goto(base_url, wait_until="domcontentloaded")
                page.get_by_label("Passage to make easier to read and explore").fill(
                    "First accessible sentence. Second accessible sentence."
                )
                page.get_by_role("button", name="Build accessibility report").click()
                page.wait_for_function("document.querySelectorAll('.segment').length === 2")
                page.get_by_role("button", name="Read all segments").click()
                page.wait_for_function(
                    "document.getElementById('status').textContent.includes('Finished reading all segments.')"
                )
                assert page.locator(".segment-play").count() == 2
                assert page.evaluate("window.__spoken") == [
                    "First accessible sentence.",
                    "Second accessible sentence.",
                ]
                assert page.get_by_role("status").get_attribute("aria-live") == "polite"
            finally:
                browser.close()
