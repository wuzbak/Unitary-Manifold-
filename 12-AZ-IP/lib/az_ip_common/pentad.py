# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""az_ip_common/pentad.py — Pentad governance lane classification hook."""
from __future__ import annotations

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


async def pentad_classify(
    task_summary: str,
    axiomzero_url: str = "http://localhost:8000",
    jwt_token: str = "",
    timeout: float = 10.0,
) -> Dict[str, Any]:
    """Classify a task via the Pentad governance endpoint."""
    try:
        import httpx  # type: ignore
        headers: Dict[str, str] = {}
        if jwt_token:
            headers["Authorization"] = "Bearer " + jwt_token
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(
                f"{axiomzero_url}/api/v1/governance/classify",
                json={"task_summary": task_summary},
                headers=headers,
            )
            resp.raise_for_status()
            return resp.json()
    except Exception as exc:
        logger.warning("Pentad classify failed (%s) — defaulting to UNCLASSIFIED", exc)
        return {"epistemic_label": "UNCLASSIFIED", "reason": str(exc)}
