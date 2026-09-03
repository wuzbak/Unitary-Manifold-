#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Resilient Copilot review orchestration with model fallback.

This tool owns repository-side retry behavior for Copilot PR reviews.
It does not change the Copilot backend; it reacts to unsupported-model
failures by selecting the next allowed model and posting a fresh request.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlencode
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = REPO_ROOT / ".github" / "copilot-review-fallback.json"
ORCHESTRATOR_MARKER = "<!-- copilot-review-orchestrator -->"
REQUEST_META_RE = re.compile(
    r"copilot-review-orchestrator:\s*head-sha=(?P<head>[0-9a-f]+);\s*model=(?P<model>[A-Za-z0-9._-]+)",
    re.IGNORECASE,
)
COPILOT_MENTION_RE = re.compile(r"@copilot\+(?P<model>[A-Za-z0-9._-]+)", re.IGNORECASE)
MODEL_UNAVAILABLE_RE = re.compile(r'Model\s+"(?P<model>[^"]+)"\s+is\s+not\s+available', re.IGNORECASE)
UNSUPPORTED_MODEL_MARKERS = (
    "requested model is not supported",
    "model \"",
    "is not available",
)
SUCCESSFUL_REVIEW_STATES = {"APPROVED", "COMMENTED", "CHANGES_REQUESTED"}
COPILOT_LOGINS = {"copilot"}
NO_ACTION_EXIT_CODE = 1
EXHAUSTED_EXIT_CODE = 2
HEALTH_FAILURE_EXIT_CODE = 3


@dataclass(frozen=True)
class OrchestratorConfig:
    preferred_model: str
    fallback_models: tuple[str, ...]
    cooldown_hours: int = 72
    max_issue_comments: int = 100
    max_pull_reviews: int = 100

    @property
    def allowed_models(self) -> list[str]:
        ordered = [self.preferred_model, *self.fallback_models]
        unique: list[str] = []
        for model in ordered:
            if model and model not in unique:
                unique.append(model)
        return unique


@dataclass(frozen=True)
class ReviewRequest:
    comment_id: int
    model: str
    head_sha: str
    created_at: datetime


@dataclass(frozen=True)
class ReviewOutcome:
    state: str
    selected_model: str | None
    detail: str


class GitHubAPI:
    def __init__(self, repo: str, token: str) -> None:
        self.repo = repo
        self.token = token
        self.base_url = f"https://api.github.com/repos/{repo}"

    def _request_json(self, method: str, url: str, data: dict[str, Any] | None = None) -> Any:
        payload = None if data is None else json.dumps(data).encode("utf-8")
        request = Request(url, data=payload, method=method)
        request.add_header("Accept", "application/vnd.github+json")
        request.add_header("Authorization", f"******")
        request.add_header("X-GitHub-Api-Version", "2022-11-28")
        if payload is not None:
            request.add_header("Content-Type", "application/json")
        with urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))

    def get_pull(self, pr_number: int) -> dict[str, Any]:
        return self._request_json("GET", f"{self.base_url}/pulls/{pr_number}")

    def list_issue_comments(self, pr_number: int, per_page: int) -> list[dict[str, Any]]:
        params = urlencode({"per_page": per_page, "page": 1})
        return self._request_json("GET", f"{self.base_url}/issues/{pr_number}/comments?{params}")

    def list_pull_reviews(self, pr_number: int, per_page: int) -> list[dict[str, Any]]:
        params = urlencode({"per_page": per_page, "page": 1})
        return self._request_json("GET", f"{self.base_url}/pulls/{pr_number}/reviews?{params}")

    def list_recent_repo_issue_comments(self, since: datetime, per_page: int) -> list[dict[str, Any]]:
        params = urlencode({"since": since.isoformat().replace("+00:00", "Z"), "per_page": per_page, "page": 1})
        return self._request_json("GET", f"{self.base_url}/issues/comments?{params}")

    def post_issue_comment(self, pr_number: int, body: str) -> dict[str, Any]:
        return self._request_json("POST", f"{self.base_url}/issues/{pr_number}/comments", {"body": body})


def load_config(path: Path) -> OrchestratorConfig:
    data = json.loads(path.read_text(encoding="utf-8"))
    preferred = str(data["preferred_model"]).strip()
    fallbacks = tuple(str(model).strip() for model in data.get("fallback_models", []))
    if not preferred:
        raise ValueError("preferred_model must be non-empty")
    allowed = [preferred, *fallbacks]
    if len({m for m in allowed if m}) != len([m for m in allowed if m]):
        raise ValueError("allowed models must be unique")
    return OrchestratorConfig(
        preferred_model=preferred,
        fallback_models=fallbacks,
        cooldown_hours=int(data.get("cooldown_hours", 72)),
        max_issue_comments=int(data.get("max_issue_comments", 100)),
        max_pull_reviews=int(data.get("max_pull_reviews", 100)),
    )


def parse_github_timestamp(raw: str) -> datetime:
    return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(timezone.utc)


def is_copilot_actor(item: dict[str, Any]) -> bool:
    return str(item.get("user", {}).get("login", "")).lower() in COPILOT_LOGINS


def comment_mentions_model(body: str) -> str | None:
    match = COPILOT_MENTION_RE.search(body)
    return match.group("model") if match else None


def extract_unavailable_model(body: str) -> str | None:
    match = MODEL_UNAVAILABLE_RE.search(body)
    if match:
        return match.group("model")
    return comment_mentions_model(body)


def is_unsupported_model_error(body: str) -> bool:
    normalized = body.lower()
    return (
        "copilot" in normalized
        and any(marker in normalized for marker in UNSUPPORTED_MODEL_MARKERS)
        and (
            "requested model is not supported" in normalized
            or "is not available" in normalized
        )
    )


def parse_review_requests(issue_comments: Iterable[dict[str, Any]], head_sha: str) -> list[ReviewRequest]:
    requests: list[ReviewRequest] = []
    for comment in issue_comments:
        body = str(comment.get("body", ""))
        if ORCHESTRATOR_MARKER not in body:
            continue
        meta = REQUEST_META_RE.search(body)
        if not meta:
            continue
        if meta.group("head") != head_sha:
            continue
        requests.append(
            ReviewRequest(
                comment_id=int(comment["id"]),
                model=meta.group("model"),
                head_sha=meta.group("head"),
                created_at=parse_github_timestamp(comment["created_at"]),
            )
        )
    requests.sort(key=lambda item: item.created_at)
    return requests


def has_successful_review(reviews: Iterable[dict[str, Any]], head_sha: str) -> bool:
    for review in reviews:
        if not is_copilot_actor(review):
            continue
        if review.get("commit_id") != head_sha:
            continue
        if str(review.get("state", "")).upper() not in SUCCESSFUL_REVIEW_STATES:
            continue
        if is_unsupported_model_error(str(review.get("body", ""))):
            continue
        return True
    return False


def has_failure_after_request(request: ReviewRequest, issue_comments: Iterable[dict[str, Any]]) -> bool:
    for comment in issue_comments:
        if not is_copilot_actor(comment):
            continue
        created_at = parse_github_timestamp(comment["created_at"])
        if created_at <= request.created_at:
            continue
        body = str(comment.get("body", ""))
        if not is_unsupported_model_error(body):
            continue
        model = extract_unavailable_model(body) or request.model
        if model == request.model:
            return True
    return False


def recent_model_failures(
    repo_issue_comments: Iterable[dict[str, Any]],
    config: OrchestratorConfig,
    now: datetime,
) -> dict[str, int]:
    floor = now - timedelta(hours=config.cooldown_hours)
    failures = {model: 0 for model in config.allowed_models}
    for comment in repo_issue_comments:
        if not is_copilot_actor(comment):
            continue
        created_at = parse_github_timestamp(comment["created_at"])
        if created_at < floor:
            continue
        body = str(comment.get("body", ""))
        if not is_unsupported_model_error(body):
            continue
        model = extract_unavailable_model(body)
        if model in failures:
            failures[model] += 1
    return failures


def rank_models(config: OrchestratorConfig, model_failures: dict[str, int]) -> list[str]:
    allowed = config.allowed_models
    healthy = [model for model in allowed if model_failures.get(model, 0) == 0]
    unhealthy = [model for model in allowed if model_failures.get(model, 0) > 0]
    return healthy + unhealthy if healthy else allowed[:]


def choose_next_model(
    config: OrchestratorConfig,
    head_sha: str,
    issue_comments: list[dict[str, Any]],
    repo_model_failures: dict[str, int],
) -> tuple[str | None, str]:
    requests = parse_review_requests(issue_comments, head_sha)
    ranked_models = rank_models(config, repo_model_failures)
    if not requests:
        return ranked_models[0], "initial-request"

    latest_request = requests[-1]
    if not has_failure_after_request(latest_request, issue_comments):
        return None, f"awaiting-review-after-{latest_request.model}"

    attempted = {request.model for request in requests}
    for model in ranked_models:
        if model not in attempted:
            return model, f"fallback-after-{latest_request.model}"
    return None, f"fallbacks-exhausted-after-{latest_request.model}"


def build_review_request_comment(model: str, head_sha: str) -> str:
    return (
        f"{ORCHESTRATOR_MARKER}\n"
        f"copilot-review-orchestrator: head-sha={head_sha}; model={model}\n\n"
        f"@copilot+{model} Please review this pull request for high-confidence bugs, "
        "security vulnerabilities, and logic errors. "
        "If this model is unavailable, return the platform error and the fallback workflow will retry automatically."
    )


def append_summary(lines: list[str]) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    with open(summary_path, "a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def resolve_pr_number(event: dict[str, Any]) -> int | None:
    if "pull_request" in event:
        return int(event["pull_request"]["number"])
    issue = event.get("issue")
    if issue and issue.get("pull_request"):
        return int(issue["number"])
    review = event.get("review")
    if review and "pull_request_url" in review and "pull_request" in event:
        return int(event["pull_request"]["number"])
    return None


def load_event() -> dict[str, Any]:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        raise RuntimeError("GITHUB_EVENT_PATH is required")
    return json.loads(Path(event_path).read_text(encoding="utf-8"))


def orchestrate(config: OrchestratorConfig, api: GitHubAPI, event: dict[str, Any], now: datetime) -> ReviewOutcome:
    pr_number = resolve_pr_number(event)
    if pr_number is None:
        return ReviewOutcome("skipped", None, "event is not associated with a pull request")

    pull = api.get_pull(pr_number)
    if pull.get("draft"):
        return ReviewOutcome("skipped", None, "pull request is draft; review orchestration deferred")

    head_sha = str(pull["head"]["sha"])
    reviews = api.list_pull_reviews(pr_number, config.max_pull_reviews)
    issue_comments = api.list_issue_comments(pr_number, config.max_issue_comments)

    if has_successful_review(reviews, head_sha):
        return ReviewOutcome("success", None, f"successful Copilot review detected for head {head_sha}")

    repo_comments = api.list_recent_repo_issue_comments(
        now - timedelta(hours=config.cooldown_hours),
        config.max_issue_comments,
    )
    repo_failures = recent_model_failures(repo_comments, config, now)
    model, reason = choose_next_model(config, head_sha, issue_comments, repo_failures)
    ranked_models = rank_models(config, repo_failures)

    summary = [
        "## Copilot review orchestrator",
        f"- PR: #{pr_number}",
        f"- Head SHA: `{head_sha}`",
        f"- Ranked models: {', '.join(ranked_models)}",
        f"- Recent model failures: `{json.dumps(repo_failures, sort_keys=True)}`",
        f"- Decision: {reason}",
    ]

    if model is None:
        append_summary(summary)
        if reason.startswith("fallbacks-exhausted"):
            return ReviewOutcome("failed", None, reason)
        return ReviewOutcome("pending", None, reason)

    api.post_issue_comment(pr_number, build_review_request_comment(model, head_sha))
    summary.append(f"- Requested model: `{model}`")
    append_summary(summary)
    return ReviewOutcome("pending", model, reason)


def health_report(config: OrchestratorConfig, api: GitHubAPI, now: datetime) -> dict[str, Any]:
    repo_comments = api.list_recent_repo_issue_comments(
        now - timedelta(hours=config.cooldown_hours),
        config.max_issue_comments,
    )
    failures = recent_model_failures(repo_comments, config, now)
    ranked = rank_models(config, failures)
    return {
        "preferred_model": config.preferred_model,
        "preferred_model_healthy": failures.get(config.preferred_model, 0) == 0,
        "all_models_unhealthy": all(failures.get(model, 0) > 0 for model in config.allowed_models),
        "model_failures": failures,
        "ranked_models": ranked,
        "cooldown_hours": config.cooldown_hours,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("orchestrate", "health"))
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"))
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"))
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if not args.repo:
        raise RuntimeError("GitHub repository is required")
    if not args.token:
        raise RuntimeError("GITHUB_TOKEN is required")

    config = load_config(Path(args.config))
    api = GitHubAPI(args.repo, args.token)
    now = datetime.now(timezone.utc)

    if args.command == "health":
        report = health_report(config, api, now)
        append_summary([
            "## Copilot review health",
            f"- Preferred model: `{report['preferred_model']}`",
            f"- Preferred healthy: `{report['preferred_model_healthy']}`",
            f"- Ranked models: {', '.join(report['ranked_models'])}",
            f"- Failure counts: `{json.dumps(report['model_failures'], sort_keys=True)}`",
        ])
        print(json.dumps(report, indent=2, sort_keys=True))
        if report["all_models_unhealthy"] or not report["preferred_model_healthy"]:
            return HEALTH_FAILURE_EXIT_CODE
        return 0

    event = load_event()
    outcome = orchestrate(config, api, event, now)
    print(f"[{outcome.state}] {outcome.detail}")
    if outcome.state == "success" or outcome.state == "skipped":
        return 0
    if outcome.state == "failed":
        return EXHAUSTED_EXIT_CODE
    return NO_ACTION_EXIT_CODE


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
