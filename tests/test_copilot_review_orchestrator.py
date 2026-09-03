# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "TOOLS" / "checks" / "copilot_review_orchestrator.py"
SPEC = importlib.util.spec_from_file_location("copilot_review_orchestrator", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def make_comment(comment_id: int, created_at: str, body: str, login: str = "Copilot") -> dict:
    return {
        "id": comment_id,
        "created_at": created_at,
        "body": body,
        "user": {"login": login},
    }


def make_review(review_id: int, commit_id: str, state: str, body: str = "", login: str = "Copilot") -> dict:
    return {
        "id": review_id,
        "commit_id": commit_id,
        "state": state,
        "body": body,
        "user": {"login": login},
    }


def test_load_config_orders_unique_models(tmp_path: Path):
    config_path = tmp_path / "copilot-review-fallback.json"
    config_path.write_text(
        """
        {
          "preferred_model": "claude-sonnet-5",
          "fallback_models": ["claude-fable-5", "gpt-5.5"]
        }
        """,
        encoding="utf-8",
    )
    config = MODULE.load_config(config_path)
    assert config.allowed_models == ["claude-sonnet-5", "claude-fable-5", "gpt-5.5"]


def test_parse_review_requests_filters_by_head_sha():
    head_sha = "abc1234"
    body = MODULE.build_review_request_comment("claude-sonnet-5", head_sha)
    comments = [
        make_comment(1, "2026-09-03T12:00:00Z", body),
        make_comment(2, "2026-09-03T12:05:00Z", MODULE.build_review_request_comment("gpt-5.5", "other")),
    ]
    requests = MODULE.parse_review_requests(comments, head_sha)
    assert len(requests) == 1
    assert requests[0].model == "claude-sonnet-5"


def test_has_successful_review_on_current_head():
    reviews = [
        make_review(1, "old", "COMMENTED"),
        make_review(2, "head", "COMMENTED"),
    ]
    assert MODULE.has_successful_review(reviews, "head") is True
    assert MODULE.has_successful_review(reviews, "missing") is False


def test_choose_next_model_initial_request_prefers_healthy_model():
    config = MODULE.OrchestratorConfig("claude-sonnet-5", ("claude-fable-5", "gpt-5.5"))
    model, reason = MODULE.choose_next_model(
        config,
        "deadbeef",
        [],
        {"claude-sonnet-5": 1, "claude-fable-5": 0, "gpt-5.5": 0},
    )
    assert model == "claude-fable-5"
    assert reason == "initial-request"


def test_choose_next_model_waits_without_failure():
    config = MODULE.OrchestratorConfig("claude-sonnet-5", ("claude-fable-5",))
    comments = [make_comment(1, "2026-09-03T12:00:00Z", MODULE.build_review_request_comment("claude-sonnet-5", "deadbeef"))]
    model, reason = MODULE.choose_next_model(config, "deadbeef", comments, {"claude-sonnet-5": 0, "claude-fable-5": 0})
    assert model is None
    assert reason == "awaiting-review-after-claude-sonnet-5"


def test_choose_next_model_falls_back_after_unsupported_model_error():
    config = MODULE.OrchestratorConfig("claude-sonnet-5", ("claude-fable-5", "gpt-5.5"))
    request = make_comment(1, "2026-09-03T12:00:00Z", MODULE.build_review_request_comment("claude-sonnet-5", "deadbeef"))
    failure = make_comment(
        2,
        "2026-09-03T12:01:00Z",
        'Copilot has encountered an unexpected error: [runtime:unclassified] Execution failed: Error: Model "claude-sonnet-5" is not available.',
    )
    model, reason = MODULE.choose_next_model(
        config,
        "deadbeef",
        [request, failure],
        {"claude-sonnet-5": 1, "claude-fable-5": 0, "gpt-5.5": 0},
    )
    assert model == "claude-fable-5"
    assert reason == "fallback-after-claude-sonnet-5"


def test_choose_next_model_exhausts_allowlist():
    config = MODULE.OrchestratorConfig("claude-sonnet-5", ("claude-fable-5",))
    comments = [
        make_comment(1, "2026-09-03T12:00:00Z", MODULE.build_review_request_comment("claude-sonnet-5", "deadbeef")),
        make_comment(2, "2026-09-03T12:01:00Z", 'Copilot has encountered an unexpected error: Error: Model "claude-sonnet-5" is not available.'),
        make_comment(3, "2026-09-03T12:02:00Z", MODULE.build_review_request_comment("claude-fable-5", "deadbeef")),
        make_comment(4, "2026-09-03T12:03:00Z", 'Copilot has encountered an unexpected error: Error: Model "claude-fable-5" is not available.'),
    ]
    model, reason = MODULE.choose_next_model(
        config,
        "deadbeef",
        comments,
        {"claude-sonnet-5": 1, "claude-fable-5": 1},
    )
    assert model is None
    assert reason == "fallbacks-exhausted-after-claude-fable-5"


def test_recent_model_failures_counts_only_supported_copilot_errors():
    config = MODULE.OrchestratorConfig("claude-sonnet-5", ("claude-fable-5",))
    now = datetime(2026, 9, 3, 12, 0, tzinfo=timezone.utc)
    comments = [
        make_comment(1, "2026-09-03T11:00:00Z", 'Copilot error: Error: Model "claude-sonnet-5" is not available.'),
        make_comment(2, "2026-09-03T11:05:00Z", 'Copilot has encountered an unexpected error: requested model is not supported (@copilot+claude-fable-5).'),
        make_comment(3, "2026-08-30T01:00:00Z", 'Copilot error: Error: Model "claude-sonnet-5" is not available.'),
        make_comment(4, "2026-09-03T11:10:00Z", 'User pasted an error string', login="wuzbak"),
    ]
    failures = MODULE.recent_model_failures(comments, config, now)
    assert failures == {"claude-sonnet-5": 1, "claude-fable-5": 1}


def test_health_report_flags_unhealthy_preferred_model():
    config = MODULE.OrchestratorConfig("claude-sonnet-5", ("claude-fable-5",))

    class FakeAPI:
        def list_recent_repo_issue_comments(self, since, per_page):
            return [
                make_comment(1, "2026-09-03T11:00:00Z", 'Copilot error: Error: Model "claude-sonnet-5" is not available.'),
            ]

    report = MODULE.health_report(config, FakeAPI(), datetime(2026, 9, 3, 12, 0, tzinfo=timezone.utc))
    assert report["preferred_model_healthy"] is False
    assert report["ranked_models"][0] == "claude-fable-5"
