# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Human-in-the-loop review helpers for Axiom Journalist."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass(slots=True)
class HILSReviewRequest:
    claim: str
    evidence: str
    requester: str = 'Axiom Journalist'
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec='seconds'))


def submit_for_review(claim: str, evidence: str) -> dict:
    """Create a review envelope for human approval."""
    request = HILSReviewRequest(claim=claim, evidence=evidence)
    payload = asdict(request)
    payload.update({
        'review_id': f'HILS-{uuid.uuid4().hex[:12].upper()}',
        'status': 'PENDING_HUMAN_REVIEW',
    })
    return payload


def format_review_output(review: dict) -> str:
    """Render a stable text summary for the review queue."""
    return (
        f"[{review.get('status', 'UNKNOWN')}] {review.get('review_id', 'NO-ID')}\n"
        f"Requester: {review.get('requester', 'Axiom Journalist')}\n"
        f"Timestamp: {review.get('timestamp', '')}\n"
        f"Claim: {review.get('claim', '')}\n"
        f"Evidence: {review.get('evidence', '')}"
    )
