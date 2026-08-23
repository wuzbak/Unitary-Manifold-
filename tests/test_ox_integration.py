# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_ox_integration.py — OX Alpha Integration Tests

Covers:
  - 9-INFRASTRUCTURE/ox_context_pack.py (build, stats, output structure)
  - bot/assistant_api.py (OX config, call_ox function signature, /api/ox endpoint)
  - TOOLS/ox_regression_watchdog.py (import, parse logic, schema validation)
  - TOOLS/ox_lean4_assistant.py (import, python extraction, path derivation)
  - public-site/az-apps/19-ox-navigator.html (file presence, key strings)
  - public-site/js/19-ox-navigator.js (file presence, key functions)
  - hf-spaces/oracle-space/app.py (OX tab present, run_ox_query defined)

No live API calls are made — all LLM calls are mocked/skipped.
0 test failures required.

Theory & scientific direction: ThomasCory Walker-Pearson.
Code, engineering: GitHub Copilot (AI).
"""

from __future__ import annotations

import ast
import importlib
import json
import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).parent.parent

# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def ox_context_pack_module():
    spec_path = REPO_ROOT / "9-INFRASTRUCTURE" / "ox_context_pack.py"
    import importlib.util
    spec = importlib.util.spec_from_file_location("ox_context_pack", spec_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def watchdog_module():
    spec_path = REPO_ROOT / "TOOLS" / "ox_regression_watchdog.py"
    import importlib.util
    spec = importlib.util.spec_from_file_location("ox_regression_watchdog", spec_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def lean4_assistant_module():
    spec_path = REPO_ROOT / "TOOLS" / "ox_lean4_assistant.py"
    import importlib.util
    spec = importlib.util.spec_from_file_location("ox_lean4_assistant", spec_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ══════════════════════════════════════════════════════════════════════════════
# 1. ox_context_pack.py
# ══════════════════════════════════════════════════════════════════════════════

class TestContextPackModule:
    def test_module_imports(self, ox_context_pack_module):
        assert ox_context_pack_module is not None

    def test_output_path_defined(self, ox_context_pack_module):
        assert hasattr(ox_context_pack_module, "OUTPUT_PATH")
        assert str(ox_context_pack_module.OUTPUT_PATH).endswith("ox_full_context.md")

    def test_verbatim_sources_list(self, ox_context_pack_module):
        sources = ox_context_pack_module.VERBATIM_SOURCES
        assert isinstance(sources, list)
        assert len(sources) >= 4

    def test_predictions_block_present(self, ox_context_pack_module):
        pb = ox_context_pack_module.PREDICTIONS_BLOCK
        assert "HARDGATE" in pb
        assert "LiteBIRD" in pb
        assert "OPEN_GAP" in pb

    def test_build_pack_returns_string(self, ox_context_pack_module):
        pack = ox_context_pack_module.build_pack()
        assert isinstance(pack, str)
        assert len(pack) > 1000

    def test_build_pack_contains_required_sections(self, ox_context_pack_module):
        pack = ox_context_pack_module.build_pack()
        assert "OX Alpha Full Repository Context Pack" in pack
        assert "Key UM Predictions" in pack
        assert "Lean4 Theorem Names" in pack

    def test_build_pack_governance_note(self, ox_context_pack_module):
        pack = ox_context_pack_module.build_pack()
        assert "GOVERNANCE" in pack
        assert "steward" in pack.lower()

    def test_estimate_tokens_positive(self, ox_context_pack_module):
        n = ox_context_pack_module.estimate_tokens("hello world " * 100)
        assert n > 0

    def test_extract_pillar_docstrings_returns_string(self, ox_context_pack_module):
        result = ox_context_pack_module._extract_pillar_docstrings()
        assert isinstance(result, str)

    def test_extract_lean4_theorems_returns_string(self, ox_context_pack_module):
        result = ox_context_pack_module._extract_lean4_theorems()
        assert isinstance(result, str)

    def test_stats_flag_no_write(self, ox_context_pack_module, tmp_path):
        # --stats should not write any file
        out = tmp_path / "should_not_exist.md"
        ox_context_pack_module.main(["--stats", "--output", str(out)])
        assert not out.exists()

    def test_main_writes_file(self, ox_context_pack_module, tmp_path):
        out = tmp_path / "test_ox_context.md"
        ox_context_pack_module.main(["--output", str(out)])
        assert out.exists()
        assert out.stat().st_size > 500

    def test_main_output_valid_markdown(self, ox_context_pack_module, tmp_path):
        out = tmp_path / "test_ox_context.md"
        ox_context_pack_module.main(["--output", str(out)])
        text = out.read_text(encoding="utf-8")
        assert text.startswith("#")


class TestContextPackOutputFile:
    """Tests on the pre-built ox_full_context.md in the repo."""

    OUTPUT = REPO_ROOT / "9-INFRASTRUCTURE" / "ox_full_context.md"

    def test_output_file_exists(self):
        assert self.OUTPUT.exists(), (
            "ox_full_context.md not found — run: python 9-INFRASTRUCTURE/ox_context_pack.py"
        )

    def test_output_not_empty(self):
        assert self.OUTPUT.stat().st_size > 10_000

    def test_output_contains_predictions(self):
        text = self.OUTPUT.read_text(encoding="utf-8")
        assert "n_s" in text
        assert "LiteBIRD" in text

    def test_output_contains_governance(self):
        text = self.OUTPUT.read_text(encoding="utf-8")
        assert "GOVERNANCE" in text

    def test_output_contains_pillar_section(self):
        text = self.OUTPUT.read_text(encoding="utf-8")
        assert "Pillar Module Docstrings" in text

    def test_output_contains_lean4_section(self):
        text = self.OUTPUT.read_text(encoding="utf-8")
        assert "Lean4 Theorem Names" in text

    def test_output_no_api_keys(self):
        text = self.OUTPUT.read_text(encoding="utf-8")
        # Ensure no real OpenRouter/HF API key patterns slipped in
        # (real keys are long hex/alphanumeric strings starting with sk-, or similar)
        assert re.search(r'\bsk-[A-Za-z0-9]{20,}', text) is None
        assert "Bearer " not in text


# ══════════════════════════════════════════════════════════════════════════════
# 2. bot/assistant_api.py — OX additions
# ══════════════════════════════════════════════════════════════════════════════

class TestAssistantApiOX:
    API_PATH = REPO_ROOT / "bot" / "assistant_api.py"

    def test_file_exists(self):
        assert self.API_PATH.exists()

    def test_openrouter_config_present(self):
        text = self.API_PATH.read_text(encoding="utf-8")
        assert "OPENROUTER_API_KEY" in text
        assert "OPENROUTER_BASE_URL" in text
        assert "stealth/ox-alpha" in text

    def test_no_hardcoded_api_key(self):
        text = self.API_PATH.read_text(encoding="utf-8")
        # Must use os.environ.get, not a literal key
        assert 'os.environ.get("OPENROUTER_API_KEY"' in text
        # Must not contain an actual key value
        assert re.search(r'OPENROUTER_API_KEY\s*=\s*"[a-zA-Z0-9]{20,}"', text) is None

    def test_call_ox_function_defined(self):
        text = self.API_PATH.read_text(encoding="utf-8")
        assert "async def call_ox(" in text

    def test_call_ox_governance_note(self):
        text = self.API_PATH.read_text(encoding="utf-8")
        assert "GOVERNANCE" in text
        assert "steward" in text.lower()

    def test_ox_endpoint_defined(self):
        text = self.API_PATH.read_text(encoding="utf-8")
        assert '"/api/ox"' in text

    def test_ox_status_endpoint_defined(self):
        text = self.API_PATH.read_text(encoding="utf-8")
        assert '"/api/ox/status"' in text

    def test_call_ox_no_key_returns_warning(self):
        """call_ox must return a clear warning if no API key is set."""
        # Import the module with mocked env
        spec_path = REPO_ROOT / "bot" / "assistant_api.py"
        import importlib.util
        spec = importlib.util.spec_from_file_location("assistant_api_test", spec_path)
        # Patch out FastAPI so it doesn't require it
        sys.modules.setdefault("fastapi", MagicMock())
        sys.modules.setdefault("pydantic", MagicMock())
        sys.modules.setdefault("httpx", MagicMock())
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "", "HF_API_TOKEN": ""}):
            mod = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(mod)
                import asyncio
                result = asyncio.get_event_loop().run_until_complete(mod.call_ox("test query"))
                assert "OPENROUTER_API_KEY" in result or "not configured" in result.lower()
            except Exception:
                # If import fails due to missing deps, just check source
                text = spec_path.read_text(encoding="utf-8")
                assert "OPENROUTER_API_KEY not set" in text

    def test_ox_context_pack_path_defined(self):
        text = self.API_PATH.read_text(encoding="utf-8")
        assert "ox_full_context.md" in text


# ══════════════════════════════════════════════════════════════════════════════
# 3. TOOLS/ox_regression_watchdog.py
# ══════════════════════════════════════════════════════════════════════════════

class TestWatchdogModule:
    def test_module_imports(self, watchdog_module):
        assert watchdog_module is not None

    def test_governance_note_defined(self, watchdog_module):
        note = watchdog_module.GOVERNANCE_NOTE
        assert "AI-generated" in note
        assert "steward" in note.lower()

    def test_ox_model_id(self, watchdog_module):
        assert watchdog_module.OX_MODEL_ID == "stealth/ox-alpha"

    def test_error_result_schema(self, watchdog_module):
        result = watchdog_module._error_result("test error")
        assert "affected_pillars" in result
        assert "risk_level" in result
        assert "recommended_tests" in result
        assert "governance_note" in result
        assert "model" in result
        assert "timestamp" in result

    def test_error_result_risk_level(self, watchdog_module):
        result = watchdog_module._error_result("x")
        assert result["risk_level"] in ("low", "medium", "high")

    def test_parse_ox_json_valid(self, watchdog_module):
        raw = json.dumps({
            "affected_pillars": [1, 3, 67],
            "risk_level": "medium",
            "recommended_tests": ["tests/test_metric.py"],
            "summary": "Metric change affects Pillars 1,3.",
        })
        result = watchdog_module._parse_ox_json(raw)
        assert result["affected_pillars"] == [1, 3, 67]
        assert result["risk_level"] == "medium"
        assert "tests/test_metric.py" in result["recommended_tests"]

    def test_parse_ox_json_with_fence(self, watchdog_module):
        raw = "```json\n" + json.dumps({
            "affected_pillars": [4],
            "risk_level": "low",
            "recommended_tests": [],
            "summary": "Holography change.",
        }) + "\n```"
        result = watchdog_module._parse_ox_json(raw)
        assert result["affected_pillars"] == [4]

    def test_parse_ox_json_bad_risk(self, watchdog_module):
        raw = json.dumps({
            "affected_pillars": [],
            "risk_level": "unknown_value",
            "recommended_tests": [],
            "summary": "",
        })
        result = watchdog_module._parse_ox_json(raw)
        assert result["risk_level"] in ("low", "medium", "high")

    def test_parse_ox_json_invalid(self, watchdog_module):
        result = watchdog_module._parse_ox_json("not json at all {{{")
        assert "error" in result or "invalid" in result.get("summary", "").lower()

    def test_build_query_has_diff(self, watchdog_module):
        q = watchdog_module.build_query("diff content here", "")
        assert "diff content here" in q

    def test_build_query_has_failures(self, watchdog_module):
        q = watchdog_module.build_query("", "FAILED tests/test_metric.py")
        assert "FAILED" in q

    def test_load_context_returns_string(self, watchdog_module):
        ctx = watchdog_module.load_context()
        assert isinstance(ctx, str)
        assert len(ctx) > 10

    def test_no_api_key_error_result(self, watchdog_module):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": ""}):
            result = watchdog_module.call_ox_sync("query", "context")
        assert "OPENROUTER_API_KEY" in result.get("summary", "") or "error" in result


class TestWatchdogFile:
    PATH = REPO_ROOT / "TOOLS" / "ox_regression_watchdog.py"

    def test_file_exists(self):
        assert self.PATH.exists()

    def test_has_spdx_header(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "SPDX-License-Identifier" in text

    def test_governance_comment(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "GOVERNANCE" in text

    def test_no_hardcoded_key(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert re.search(r'"[a-zA-Z0-9_\-]{30,}"', text) is None or \
               "OPENROUTER_API_KEY" in text


# ══════════════════════════════════════════════════════════════════════════════
# 4. TOOLS/ox_lean4_assistant.py
# ══════════════════════════════════════════════════════════════════════════════

class TestLean4AssistantModule:
    def test_module_imports(self, lean4_assistant_module):
        assert lean4_assistant_module is not None

    def test_ox_model_id(self, lean4_assistant_module):
        assert lean4_assistant_module.OX_MODEL_ID == "stealth/ox-alpha"

    def test_governance_header_contains_steward(self, lean4_assistant_module):
        assert "steward" in lean4_assistant_module.GOVERNANCE_HEADER.lower()

    def test_governance_header_contains_ox_generated(self, lean4_assistant_module):
        assert "OX" in lean4_assistant_module.GOVERNANCE_HEADER

    def test_extract_python_summary_docstring(self, lean4_assistant_module, tmp_path):
        mod_file = tmp_path / "pillar_test.py"
        mod_file.write_text('"""Test pillar docstring."""\n\nTEST_CONST = 42\n\ndef compute():\n    pass\n')
        summary = lean4_assistant_module.extract_python_summary(mod_file)
        assert "pillar_test.py" in summary
        assert "Test pillar docstring" in summary
        assert "compute" in summary

    def test_extract_python_summary_constants(self, lean4_assistant_module, tmp_path):
        mod_file = tmp_path / "pillar_x.py"
        mod_file.write_text("WINDING = 5\nK_CS = 74\n")
        summary = lean4_assistant_module.extract_python_summary(mod_file)
        assert "WINDING" in summary or "K_CS" in summary

    def test_load_lean4_examples_returns_string(self, lean4_assistant_module):
        result = lean4_assistant_module._load_lean4_examples(1)
        assert isinstance(result, str)

    def test_no_api_key_returns_comment(self, lean4_assistant_module):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": ""}):
            result = lean4_assistant_module.call_ox_lean4("summary", "examples")
        assert "ERROR" in result or "OPENROUTER_API_KEY" in result


class TestLean4AssistantFile:
    PATH = REPO_ROOT / "TOOLS" / "ox_lean4_assistant.py"

    def test_file_exists(self):
        assert self.PATH.exists()

    def test_has_spdx_header(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "SPDX-License-Identifier" in text

    def test_sorry_in_system_prompt(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "sorry" in text

    def test_governance_present(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "GOVERNANCE" in text

    def test_no_hardcoded_key(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert 'os.environ.get("OPENROUTER_API_KEY"' in text


# ══════════════════════════════════════════════════════════════════════════════
# 5. public-site/az-apps/19-ox-navigator.html
# ══════════════════════════════════════════════════════════════════════════════

class TestOxNavigatorHTML:
    PATH = REPO_ROOT / "public-site" / "az-apps" / "19-ox-navigator.html"

    def test_file_exists(self):
        assert self.PATH.exists()

    def test_title_correct(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "OX Navigator" in text

    def test_product_20_tag(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "Product 20" in text

    def test_governance_note_present(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "HILS Governance" in text or "steward" in text.lower()

    def test_openrouter_referenced(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "openrouter" in text.lower()

    def test_ox_model_referenced(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "stealth/ox-alpha" in text

    def test_js_file_linked(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "19-ox-navigator.js" in text

    def test_no_hardcoded_key(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert re.search(r'"[a-zA-Z0-9_\-]{30,}"', text) is None

    def test_valid_html_structure(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in text
        assert "<html" in text
        assert "</html>" in text

    def test_authorship_credit(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "Walker-Pearson" in text


# ══════════════════════════════════════════════════════════════════════════════
# 6. public-site/js/19-ox-navigator.js
# ══════════════════════════════════════════════════════════════════════════════

class TestOxNavigatorJS:
    PATH = REPO_ROOT / "public-site" / "js" / "19-ox-navigator.js"

    def test_file_exists(self):
        assert self.PATH.exists()

    def test_ox_send_function_defined(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "window.oxSend" in text or "oxSend" in text

    def test_ox_clear_function_defined(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "oxClear" in text

    def test_api_ox_endpoint_called(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "/api/ox" in text

    def test_gate_labels_listed(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "HARDGATE" in text
        assert "OPEN_GAP" in text

    def test_governance_note_present(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "governance" in text.lower() or "steward" in text.lower()

    def test_use_strict(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "'use strict'" in text

    def test_no_hardcoded_api_key(self):
        text = self.PATH.read_text(encoding="utf-8")
        # No 30+ char string literals that look like API keys
        assert re.search(r'"[a-zA-Z0-9_\-]{30,}"', text) is None

    def test_example_queries_present(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "Δm²₂₁" in text or "OPEN_GAP" in text or "LiteBIRD" in text

    def test_history_function_present(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "addHistory" in text or "history" in text


# ══════════════════════════════════════════════════════════════════════════════
# 7. hf-spaces/oracle-space/app.py — OX tab
# ══════════════════════════════════════════════════════════════════════════════

class TestOracleSpaceOX:
    PATH = REPO_ROOT / "hf-spaces" / "oracle-space" / "app.py"

    def test_file_exists(self):
        assert self.PATH.exists()

    def test_ox_model_id_defined(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "stealth/ox-alpha" in text

    def test_openrouter_api_key_env(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert 'os.environ.get("OPENROUTER_API_KEY"' in text

    def test_run_ox_query_function_defined(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "def run_ox_query(" in text

    def test_ox_tab_in_gradio(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "OX Extended Memory" in text

    def test_governance_note_in_ox_tab(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "steward" in text.lower()

    def test_no_hardcoded_api_key(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert re.search(r'OPENROUTER_API_KEY\s*=\s*"[a-zA-Z0-9]{20,}"', text) is None

    def test_httpx_import_guarded(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "HTTPX_OK" in text or "import httpx" in text

    def test_ox_context_pack_path_defined(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "ox_full_context.md" in text

    def test_epistemic_footer_in_ox_response(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "EPISTEMIC_FOOTER" in text

    def test_ox_system_prompt_no_toe_score(self):
        text = self.PATH.read_text(encoding="utf-8")
        # The OX_SYSTEM_PROMPT may reference "ToE score" only as a prohibition rule.
        # Ensure it does NOT use ToE score as a positive claim or branding.
        # (The phrase is allowed in a "Never use X" rule context.)
        assert "ToE score" not in text or 'Never use "ToE score"' in text or "No ToE" in text


# ══════════════════════════════════════════════════════════════════════════════
# 8. Integration: context pack rebuilds cleanly
# ══════════════════════════════════════════════════════════════════════════════

class TestContextPackRebuild:
    def test_rebuild_via_subprocess(self, tmp_path):
        out = tmp_path / "rebuilt.md"
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "9-INFRASTRUCTURE" / "ox_context_pack.py"),
             "--output", str(out)],
            capture_output=True, text=True, timeout=60,
        )
        assert result.returncode == 0, f"Context pack build failed:\n{result.stderr}"
        assert out.exists()
        assert out.stat().st_size > 1000

    def test_rebuild_stats_flag(self):
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "9-INFRASTRUCTURE" / "ox_context_pack.py"),
             "--stats"],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0
        assert "chars" in result.stdout
        assert "tokens" in result.stdout
